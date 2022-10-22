import contextlib
import io
import re
from traceback import format_exception
from discord.ext import commands
from main import util, db
import discord
import os
import aiohttp

class Dev(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
    
    @commands.command(name='eval', aliases=['ev', 'e'])
    @commands.is_owner()
    async def _eval(self, ctx: commands.Context, *, text = None):
        if not text:
            return await util.throw_error(ctx, text="You need to provide a code to evaluate!")
        def clean_code(code: str):
            if code.startswith('```') and code.endswith('```'):
                return '\n'.join(code.split('\n')[1:])[:-3]
            return code
        code = clean_code(text)
        if '--p' in code or '--print' in code:
            code = f'print({re.sub("--p(rint)?", "", code, flags=re.IGNORECASE)})'
        local_variables = { "discord": discord, "commands": commands, "bot": commands.Bot, "ctx": ctx, "db": db }
        stdout = io.StringIO()
        try:
            with contextlib.redirect_stdout(stdout):
                exec(code, local_variables)
        except Exception as err:
            return await ctx.send(f'```py\n{"".join(format_exception(err, err, err.__traceback__))}```')

        await ctx.send(content=f'```py\n{">>> " + stdout.getvalue() if stdout.getvalue() else "[ No output ]" }```')
    
    @commands.command(name='reload', aliases=['update'])
    @commands.is_owner()
    async def _reload(self, ctx: commands.Context, extension = None):
        if not os.path.exists(f'./cogs/{extension}.py'):
            return await util.throw_error(ctx, text="That cog doesn't exist!")
        old = ctx.bot.commands
        await ctx.bot.reload_extension(f'cogs.{extension}')
        view = discord.ui.View().add_item(discord.ui.Button(style=discord.ButtonStyle.blurple, label=f'Commands', custom_id="general", disabled=True)).add_item(discord.ui.Button(style=discord.ButtonStyle.red, label=f'Before: {len(old)}', custom_id="before", disabled=True)).add_item(discord.ui.Button(style=discord.ButtonStyle.green, label=f'After: {len(ctx.bot.commands)}', custom_id="after", disabled=True))
        await util.throw_fine(ctx, text=f'**cogs.{extension}** successfully reloaded!', view=view, bold=False, defer=False)
    
    @commands.command(name='load')
    @commands.is_owner()
    async def _load(self, ctx: commands.Context, extension = None):
        if not os.path.exists(f'./cogs/{extension}.py'):
            return await util.throw_error(ctx, text="That cog doesn't exist!")
        await ctx.bot.load_extension(f'cogs.{extension}')
        await util.throw_fine(ctx, text=f'**cogs.{extension}** successfully loaded!', bold=False)

async def setup(bot: commands.Bot):
    await bot.add_cog(Dev(bot))