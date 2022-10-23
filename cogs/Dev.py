import contextlib
import io
import re
from traceback import format_exception
from discord.ext import commands
from main import util, db
import discord
import os

class Dev(commands.GroupCog, name="mid"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        super().__init__()
    
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
    
    @discord.app_commands.command(name='reload', description="Reload a cog")
    @commands.is_owner()
    async def _reload(self, i: discord.Interaction, extension: str):
        if not os.path.exists(f'./cogs/{extension}.py'):
            return await util.throw_error(i, text="That cog doesn't exist!")
        old = self.bot.commands
        await self.bot.reload_extension(f'cogs.{extension}')
        view = discord.ui.View().add_item(discord.ui.Button(style=discord.ButtonStyle.blurple, label=f'Commands', custom_id="general", disabled=True)).add_item(discord.ui.Button(style=discord.ButtonStyle.red, label=f'Before: {len(old)}', custom_id="before", disabled=True)).add_item(discord.ui.Button(style=discord.ButtonStyle.green, label=f'After: {len(self.bot.commands)}', custom_id="after", disabled=True))
        await util.throw_fine(i, text=f'**cogs.{extension}** successfully reloaded!', view=view, bold=False)
    
    @discord.app_commands.command(name='sync', description="Sync all slash commands")
    @commands.is_owner()
    async def _sync(self, i: discord.Interaction):
        await util.throw_fine(i, text="Synced commands sucessfully!")
    
    @commands.command(name='load')
    @commands.is_owner()
    async def _load(self, ctx: commands.Context, extension = None):
        if not os.path.exists(f'./cogs/{extension}.py'):
            return await util.throw_error(ctx, text="That cog doesn't exist!")
        await ctx.bot.load_extension(f'cogs.{extension}')
        await util.throw_fine(ctx, text=f'**cogs.{extension}** successfully loaded!', bold=False)

async def setup(bot: commands.Bot):
    await bot.add_cog(Dev(bot))