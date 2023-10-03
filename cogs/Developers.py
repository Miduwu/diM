from aiohttp import ContentTypeError, ClientSession
from discord.utils import escape_mentions
from discord.ext import commands, tasks
from dataclasses import dataclass
from main import util, mongodb, db, timeouts
from traceback import format_exception
from html import unescape
from util.views import Paginator
from typing import Literal
from urllib.parse import quote_plus

import pydash as _
import re, sys, discord, contextlib, io, os

def add_boilerplate(language, source):
    if language == "java":
        return for_java(source)
    if language == "scala":
        return for_scala(source)
    if language == "rust":
        return for_rust(source)
    if language == "c" or language == "c++":
        return for_c_cpp(source)
    if language == "go":
        return for_go(source)
    if language in ["csharp", "dotnet", "c#.net"]:
        return for_csharp(source)
    return source

def for_go(source):
    if 'main' in source:
        return source

    package = ['package main']
    imports = []
    code = ['func main() {']

    lines = source.split('\n')
    for line in lines:
        if line.lstrip().startswith('import'):
            imports.append(line)
        else:
            code.append(line)

    code.append('}')
    return '\n'.join(package + imports + code)

def for_c_cpp(source):
    if 'main' in source:
        return source

    imports = []
    code = ['int main() {']

    lines = source.replace(';', ';\n').split('\n')
    for line in lines:
        if line.lstrip().startswith('#include'):
            imports.append(line)
        else:
            code.append(line)

    code.append('}')
    return '\n'.join(imports + code)

def for_csharp(source):
    if 'class' in source:
        return source

    imports=[]
    code = ['class Program{']
    if not 'static void Main' in source:
        code.append('static void Main(string[] args){')

    lines = source.replace(';', ';\n').split('\n')
    for line in lines:
        if line.lstrip().startswith('using'):
            imports.append(line)
        else:
            code.append(line)

    if not 'static void Main' in source:
        code.append('}')
    code.append('}')

    return '\n'.join(imports + code).replace(';\n', ';')

def for_java(source):
    if 'class' in source:
        return source

    imports = []
    code = [
        'public class temp extends Object {public static void main(String[] args) {']

    lines = source.replace(';', ';\n').split('\n')
    for line in lines:
        if line.lstrip().startswith('import'):
            imports.append(line)
        else:
            code.append(line)

    code.append('}}')
    return '\n'.join(imports + code).replace(';\n',';')

def for_scala(source):
    if any(s in source for s in ('extends App', 'def main', '@main def', '@main() def')):
        return source

    # Scala will complain about indentation so just indent source
    indented_source = '  ' + source.replace('\n', '\n  ').rstrip() + '\n'

    return f'@main def run(): Unit = {{\n{indented_source}}}\n'

def for_rust(source):
    if 'fn main' in source:
        return source
    imports = []
    code = ['fn main() {']

    lines = source.replace(';', ';\n').split('\n')
    for line in lines:
        if line.lstrip().startswith('use'):
            imports.append(line)
        else:
            code.append(line)

    code.append('}')
    return '\n'.join(imports + code)

@dataclass
class RunIO:
    input: discord.Message
    output: discord.Message

def get_size(obj, seen=None):
    """Recursively finds size of objects"""
    size = sys.getsizeof(obj)
    if seen is None:
        seen = set()
    obj_id = id(obj)
    if obj_id in seen:
        return 0
    # Important mark as seen *before* entering recursion to gracefully handle
    # self-referential objects
    seen.add(obj_id)
    if isinstance(obj, dict):
        size += sum([get_size(v, seen) for v in obj.values()])
        size += sum([get_size(k, seen) for k in obj.keys()])
    elif hasattr(obj, "__dict__"):
        size += get_size(obj.__dict__, seen)
    elif hasattr(obj, "__iter__") and not isinstance(obj, (str, bytes, bytearray)):
        size += sum([get_size(i, seen) for i in obj])
    return size

def esc(pattern):
    special_chars = r"^$.|?*+()[]{}\\"
    escaped_pattern = ""
    for char in pattern:
        if char in special_chars:
            escaped_pattern += "\\" + char
        else:
            escaped_pattern += char
    return escaped_pattern

class Developers(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.languages = dict()
        self.versions = dict()
        async def _(x):
            p = await mongodb.get(table="guilds", id=x, path="prefix")
            return esc(p or "t!")
        async def run_regex_code(x):
            return re.compile(r"(?s)PREFIX(?:edit_last_)?run".replace("PREFIX", await _(x)) + r"(?: +(?P<language>\S*?)\s*|\s*)" r"(?:-> *(?P<output_syntax>\S*)\s*|\s*)" r"(?:\n(?P<args>(?:[^\n\r\f\v]*\n)*?)\s*|\s*)" r"```(?:(?P<syntax>\S+)\n\s*|\s*)(?P<source>.*)```" r"(?:\n?(?P<stdin>(?:[^\n\r\f\v]\n?)+)+|)")
        async def run_regex_file(x):
            return re.compile(r"PREFIXrun(?: *(?P<language>\S*)\s*?|\s*?)?".replace("PREFIX", await _(x)) + r"(?: *-> *(?P<output>\S*)\s*?|\s*?)?" r"(?:\n(?P<args>(?:[^\n\r\f\v]+\n?)*)\s*|\s*)?" r"(?:\n*(?P<stdin>(?:[^\n\r\f\v]\n*)+)+|)?")
        self.run_regex_file = run_regex_file
        self.run_regex_code = run_regex_code
        self.get_available_languages.start()

    @tasks.loop(count=1)
    async def get_available_languages(self):
        async with ClientSession() as session:
            async with session.get(
                "https://emkc.org/api/v2/piston/runtimes"
            ) as response:
                runtimes = await response.json()
            for runtime in runtimes:
                language = runtime["language"]
                self.languages[language] = language
                self.versions[language] = runtime["version"]
                for alias in runtime["aliases"]:
                    self.languages[alias] = language
                    self.versions[alias] = runtime["version"]
    
    async def get_api_parameters_with_codeblock(self, ctx):
        if ctx.message.content.count("```") != 2:
            raise commands.BadArgument("Invalid command format (missing codeblock)?")

        match = await self.run_regex_code(ctx.guild.id)
        match = match.search(ctx.message.content)

        if not match:
            raise commands.BadArgument("Invalid code format")
        
        language, output_syntax, args, syntax, source, stdin = match.groups()

        if not language:
            language = syntax

        if language:
            language = language.lower()

        if language not in self.languages:
            raise commands.BadArgument(f"Ops! You provided an unsupported language: `{str(language)[:100]}`")

        return language, output_syntax, source, args, stdin
    
    async def get_api_parameters_with_file(self, ctx):
        if len(ctx.message.attachments) != 1:
            raise commands.BadArgument("Invalid attachments")

        file = ctx.message.attachments[0]

        MAX_BYTES = 65535
        if file.size > MAX_BYTES:
            raise commands.BadArgument(f"Source file is too big ({file.size}>{MAX_BYTES})")
    
        filename_split = file.filename.split(".")

        if len(filename_split) < 2:
            raise commands.BadArgument("You have to provide the extension too")

        match = await self.run_regex_file(ctx.guild.id)
        match = match.search(ctx.message.content)

        if not match:
            raise commands.BadArgument("Invalid code format")

        language, output_syntax, args, stdin = match.groups()

        if not language:
            language = filename_split[-1]

        if language:
            language = language.lower()

        if language not in self.languages:
            raise commands.BadArgument(f"Ops! You provided an unsupported language: `{str(language)[:100]}`")

        source = await file.read()
        try:
            source = source.decode("utf-8")
        except UnicodeDecodeError as e:
            raise commands.BadArgument(str(e))

        return language, output_syntax, source, args, stdin
    
    async def get_run_output(self, ctx):
        # Get parameters to call api depending on how the command was called (file <> codeblock)
        if ctx.message.attachments:
            (
                alias,
                output_syntax,
                source,
                args,
                stdin,
            ) = await self.get_api_parameters_with_file(ctx)
        else:
            (
                alias,
                output_syntax,
                source,
                args,
                stdin,
            ) = await self.get_api_parameters_with_codeblock(ctx)

        # Resolve aliases for language
        language = self.languages[alias]

        version = self.versions[alias]

        # Add boilerplate code to supported languages
        source = add_boilerplate(language, source)

        # Split args at newlines
        if args:
            args = [arg for arg in args.strip().split("\n") if arg]

        if not source:
            raise commands.BadArgument("No code source found")

        # Call piston API
        data = {
            "language": alias,
            "version": version,
            "files": [{"content": source}],
            "args": args,
            "stdin": stdin or "",
            "log": 0,
        }
        async with ClientSession() as session:
            async with session.post(
                "https://emkc.org/api/v2/piston/execute", json=data
            ) as response:
                try:
                    r = await response.json()
                except ContentTypeError:
                    raise commands.BadArgument("invalid content type")
                if not response.status == 200:
                    raise commands.BadArgument(f'status {response.status}: {r.get("message", "")}')

        comp_stderr = r["compile"]["stderr"] if "compile" in r else ""
        run = r["run"]

        if run["output"] is None:
            raise commands.BadArgument("Your code ran without output")

        language_info = f"{alias}({version})"

        # Return early if no output was received
        if len(run["output"] + comp_stderr) == 0:
            raise commands.BadArgument(f"Your {language_info} code ran without output {ctx.author.mention}")

        # Limit output to 30 lines maximum
        output = "\n".join((comp_stderr + run["output"]).split("\n")[:30])

        # Prevent mentions in the code output
        output = escape_mentions(output)

        # Prevent code block escaping by adding zero width spaces to backticks
        output = output.replace("`", "`\u200b")

        # Truncate output to be below 2000 char discord limit.
        if len(comp_stderr) > 0:
            introduction = (
                f"{ctx.author.mention} I received {language_info} compile errors\n"
            )
        elif len(run["stdout"]) == 0 and len(run["stderr"]) > 0:
            introduction = (
                f"{ctx.author.mention} I only received {language_info} error output\n"
            )
        else:
            introduction = f"Here is your {language_info} output {ctx.author.mention}\n"
        truncate_indicator = "[...]"
        len_codeblock = 7  # 3 Backticks + newline + 3 Backticks
        available_chars = 2000 - len(introduction) - len_codeblock
        if len(output) > available_chars:
            output = (
                output[: available_chars - len(truncate_indicator)] + truncate_indicator
            )

        # Use an empty string if no output language is selected
        return (
            introduction
            + f'```{output_syntax or ""}\n'
            + output.replace("\0", "")
            + "```"
        )
    
    @commands.cooldown(1, 10, commands.BucketType.member)
    @commands.hybrid_command(name="run", aliases=["code"])
    @discord.app_commands.describe(source="The source code")
    async def run(self, ctx, *, source=None):
        """Run some code"""
        try:
            await ctx.typing()
        except discord.errors.Forbidden:
            pass
        if not source and not ctx.message.attachments:
            await self.send_howto(ctx)
            return
        run_output = await self.get_run_output(ctx)
        await ctx.send(run_output)
    
    @commands.hybrid_group(name="mid", hidden=True)
    async def mid(self, ctx):
        """Developer commands (You can't use these)"""
        ...
    
    @mid.command(name="eval", aliases=["ev", "e"], hidden=True)
    @discord.app_commands.describe(text="The code to evaluate")
    @commands.is_owner()
    async def _eval(self, ctx: commands.Context, *, text: str):
        """Eval a Python code"""
        def clean_code(code: str):
            if code.startswith("```") and code.endswith("```"):
                return "\n".join(code.split("\n")[1:])[:-3]
            return code
        code = clean_code(text)
        if "--p" in code or "--print" in code:
            code = f"print({re.sub('--p(rint)?', '', code, flags=re.IGNORECASE)})"
        local_variables = { "discord": discord, "commands": commands, "bot": ctx.bot, "ctx": ctx, "db": db, "timeouts": timeouts, "util": util }
        stdout = io.StringIO()
        try:
            with contextlib.redirect_stdout(stdout):
                exec(code, local_variables)
        except Exception as err:
            return await ctx.send(f"```py\n{''.join(format_exception(err, err, err.__traceback__))}```")

        await ctx.send(content=f"```py\n{'>>> ' + stdout.getvalue() if stdout.getvalue() else '[ No output ]' }```")
    
    @mid.command(name="reload", aliases=["update"], hidden=True)
    @discord.app_commands.describe(extension="The cog to reload")
    @commands.is_owner()
    async def _reload(self, ctx: commands.Context, extension: str):
        """Reload a cog"""
        if not os.path.exists(f"./cogs/{extension}.py"):
            return await util.throw_error(ctx, text="That cog doesn't exist!")
        old = ctx.bot.commands
        await ctx.bot.reload_extension(f"cogs.{extension}")
        view = discord.ui.View().add_item(discord.ui.Button(style=discord.ButtonStyle.blurple, label=f"Commands", custom_id="general", disabled=True)).add_item(discord.ui.Button(style=discord.ButtonStyle.red, label=f"Before: {len(old)}", custom_id="before", disabled=True)).add_item(discord.ui.Button(style=discord.ButtonStyle.green, label=f"After: {len(ctx.bot.commands)}", custom_id="after", disabled=True))
        await util.throw_fine(ctx, text=f"**cogs.{extension}** successfully reloaded!", view=view, bold=False, defer=False)
    
    @mid.command(name="load", hidden=True)
    @discord.app_commands.describe(extension="The cog to load")
    @commands.is_owner()
    async def _load(self, ctx: commands.Context, extension: str):
        """Load a new cog"""
        if not os.path.exists(f"./cogs/{extension}.py"):
            return await util.throw_error(ctx, text="That cog doesn't exist!")
        await ctx.bot.load_extension(f"cogs.{extension}")
        await util.throw_fine(ctx, text=f"**cogs.{extension}** successfully loaded!", bold=False)
    
    @mid.command(name="sync", hidden=True)
    @commands.is_owner()
    async def _sync(self, ctx: commands.Context):
        """Sync the slash commands"""
        await ctx.defer()
        await self.bot.tree.sync()
        await util.throw_fine(ctx, text="Slash commands synced successfully!", defer=False)
    
    @commands.hybrid_group(name="docs")
    async def docs(self, ctx):
        """Search something related to JS/PY"""
    
    @commands.cooldown(1, 7, commands.BucketType.member)
    @docs.command(name='python', aliases=['py'])
    @discord.app_commands.describe(query='Something to search')
    async def realpython(self, ctx: commands.Context, *, query: str):
        '''Search something in real python website'''
        res = await util.get(url='https://realpython.com/search/api/v1/', params={"q": query, "limit": 15})
        if not res or not _.get(res, 'results') or not len(res['results']):
            return await util.throw_error(ctx, text='I was unable to find some article related to that')
        await ctx.defer()
        articles = _.chunk(res["results"], 3)
        emb = discord.Embed(colour=3447003, title='Search results - Real Python', url=f'https://realpython.com/search?q={quote_plus(query)}', description='Here you go')
        emb.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar)
        emb.set_thumbnail(url='https://cdn.discordapp.com/attachments/852617860404609044/1054972118611279892/pythontocompress_1.png')
        emb.set_footer(text=f'Page: 1/{len(articles)}', icon_url=self.bot.user.display_avatar)
        for article in articles[0]:
            emb.add_field(name=util.cut(unescape(article["title"]), 225), value=f'https://realpython.com{article["url"]}', inline=False)
        
        v = Paginator(data=articles, ctx=ctx, embed=emb)
        def update(item):
            v.embed.clear_fields()
            v.embed.set_footer(text=f'Page: {v.page + 1}/{len(articles)}', icon_url=self.bot.user.display_avatar)
            for article in item:
                v.embed.add_field(name=util.cut(unescape(article["title"]), 225), value=f'https://realpython.com{article["url"]}', inline=False)
        v.update_item = update
        v.message = await ctx.send(embed=emb, view=v)
    
    @commands.cooldown(1, 7, commands.BucketType.member)
    @docs.command(name='javascript', aliases=['js'])
    @discord.app_commands.describe(query='Something to search')
    async def mozilla(self, ctx: commands.Context, query: str, idiom: Literal['en-us', 'de', 'es', 'fr', 'ja', 'ko', 'pl', 'pt-br', 'ru', 'zh-cn', 'zh-tw'] = 'en-us'):
        '''Search something in mozilla'''
        res = await util.get(url='https://developer.mozilla.org/api/v1/search', params={"q": query, "locale": idiom})
        if not res or not _.get(res, 'documents') or not len(res['documents']):
            return await util.throw_error(ctx, text='I was unable to find something related to that')
        await ctx.defer()
        docs = _.get(res, 'documents')
        emb = discord.Embed(colour=3447003, title=docs[0]['title'], url=f'https://developer.mozilla.org{docs[0]["mdn_url"]}')
        emb.set_thumbnail(url='https://cdn.discordapp.com/attachments/778296113123688498/958975232952127488/mozilla.png')
        emb.add_field(name='Locale:', value=docs[0]['locale'])
        emb.add_field(name='Score:', value=str(_.get(docs[0], 'score') or 0))
        emb.add_field(name='Summary:', value=docs[0]['summary'], inline=False)
        emb.set_footer(text=f'Page: 1/{len(docs)}', icon_url=self.bot.user.display_avatar)
        v = Paginator(data=docs, ctx=ctx, embed=emb)
        def update(item):
            v.embed.clear_fields()
            v.embed.set_footer(text=f'Page: {v.page + 1}/{len(docs)}', icon_url=self.bot.user.display_avatar)
            v.embed.add_field(name='Locale:', value=item['locale'])
            v.embed.add_field(name='Score:', value=str(_.get(item, 'score') or 0))
            v.embed.add_field(name='Summary:', value=item['summary'], inline=False)
        v.update_item = update
        v.message = await ctx.send(embed=emb, view=v)
    
    @commands.cooldown(1, 18, commands.BucketType.user)
    @commands.hybrid_command(name="chat", aliases=["ai", "chatgpt", "bing"], example="t!chat Tell me a joke")
    @discord.app_commands.describe(prompt="The prompt to interact with chatgpt")
    async def chatgpt(self, ctx: commands.Context, *, prompt: str):
        """Asks something to ChatGPT (Bing)"""
        if ctx.interaction:
            await ctx.defer()
        else:
            await ctx.message.add_reaction("⏰")
        
        res = await util.get(url="https://penguai.esports-ac3.workers.dev/chatbot", params={"message", prompt[:2000]})
        if not res:
            return await util.throw_error(ctx, text='I was unable to pass that question')
        emb = discord.Embed(colour=3447003)
        emb.set_author(name="Artificial Intelligence")
        emb.description = res["response"][:3000]
        emb.set_footer(text=self.bot.user.name, icon_url=self.bot.user.display_avatar)
        await ctx.send(embed=emb)
        if ctx.message:
            await ctx.message.clear_reactions()

async def setup(bot: commands.Bot):
    await bot.add_cog(Developers(bot))