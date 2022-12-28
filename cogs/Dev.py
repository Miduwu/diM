import contextlib
import io
import re
from traceback import format_exception
from discord.ext import commands
from main import util, db, timeouts
from typing import Optional
import discord
import os

class Dev(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
    
    @commands.hybrid_group(name='mid')
    async def mid(self, ctx):
        '''Developer commands (You can't use these)'''
        ...
    
    @mid.command(name='eval', aliases=['ev', 'e'])
    @discord.app_commands.describe(text='The code to evaluate')
    @commands.is_owner()
    async def _eval(self, ctx: commands.Context, *, text: str):
        '''Eval a Python code'''
        def clean_code(code: str):
            if code.startswith('```') and code.endswith('```'):
                return '\n'.join(code.split('\n')[1:])[:-3]
            return code
        code = clean_code(text)
        if '--p' in code or '--print' in code:
            code = f'print({re.sub("--p(rint)?", "", code, flags=re.IGNORECASE)})'
        local_variables = { "discord": discord, "commands": commands, "bot": ctx.bot, "ctx": ctx, "db": db, "timeouts": timeouts, "util": util }
        stdout = io.StringIO()
        try:
            with contextlib.redirect_stdout(stdout):
                exec(code, local_variables)
        except Exception as err:
            return await ctx.send(f'```py\n{"".join(format_exception(err, err, err.__traceback__))}```')

        await ctx.send(content=f'```py\n{">>> " + stdout.getvalue() if stdout.getvalue() else "[ No output ]" }```')
    
    @mid.command(name='reload', aliases=['update'])
    @discord.app_commands.describe(extension='The cog to reload')
    @commands.is_owner()
    async def _reload(self, ctx: commands.Context, extension: str):
        '''Reload a cog'''
        if not os.path.exists(f'./cogs/{extension}.py'):
            return await util.throw_error(ctx, text="That cog doesn't exist!")
        old = ctx.bot.commands
        await ctx.bot.reload_extension(f'cogs.{extension}')
        view = discord.ui.View().add_item(discord.ui.Button(style=discord.ButtonStyle.blurple, label=f'Commands', custom_id="general", disabled=True)).add_item(discord.ui.Button(style=discord.ButtonStyle.red, label=f'Before: {len(old)}', custom_id="before", disabled=True)).add_item(discord.ui.Button(style=discord.ButtonStyle.green, label=f'After: {len(ctx.bot.commands)}', custom_id="after", disabled=True))
        await util.throw_fine(ctx, text=f'**cogs.{extension}** successfully reloaded!', view=view, bold=False, defer=False)
    
    @mid.command(name='load')
    @discord.app_commands.describe(extension='The cog to load')
    @commands.is_owner()
    async def _load(self, ctx: commands.Context, extension: str):
        '''Load a new cog'''
        if not os.path.exists(f'./cogs/{extension}.py'):
            return await util.throw_error(ctx, text="That cog doesn't exist!")
        await ctx.bot.load_extension(f'cogs.{extension}')
        await util.throw_fine(ctx, text=f'**cogs.{extension}** successfully loaded!', bold=False)
    
    @mid.command(name='sync')
    @commands.is_owner()
    async def _sync(self, ctx: commands.Context):
        '''Sync the slash commands'''
        await ctx.defer()
        await self.bot.tree.sync()
        await util.throw_fine(ctx, text='Slash commands synced successfully!', defer=False)

async def setup(bot: commands.Bot):
    await bot.add_cog(Dev(bot))