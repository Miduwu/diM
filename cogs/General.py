import discord
import sys
import datetime
from discord.ext import commands
from main import util
from util.helpcmd import send_help, send_help_cog, send_help_group, send_help_command

class General(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
    
    @commands.hybrid_group(name='bot')
    async def _bot(self, ctx):
        '''Get information related to the bot'''
        ...

    @_bot.command(name='ping')
    async def ping(self, ctx: commands.Context):
        '''Get the bot websocket latency'''
        await ctx.send(f'Pong! :ping_pong: **{round(self.bot.latency, 2)}s**')
    
    @commands.cooldown(1, 5, commands.BucketType.member)
    @_bot.command(name='info')
    async def stats(self, ctx: commands.Context):
        '''Get the bot info'''
        await ctx.defer()
        uptime = datetime.timedelta(milliseconds=(round(datetime.datetime.now().timestamp()) - round(util.uptime.timestamp())) * 1000)
        embed = discord.Embed(title=f'{self.bot.user.name}\'s stats', colour=3447003)
        embed.add_field(name='Tracking', value=f'¬ **Servers:** {len(self.bot.guilds)}\n¬ **Users:** {len(self.bot.users)}\n¬ **Commands:** {len(self.bot.commands)}', inline=True)
        embed.add_field(name='Software', value=f'¬ **Python:** `{sys.version.split(" ")[0]}`\n¬ **Discord.py:** `{discord.__version__}`\n¬ **Platform:** `{sys.platform}`')
        embed.set_thumbnail(url=self.bot.user.display_avatar)
        embed.set_footer(text=f'Uptime: {uptime} hrs.')
        await ctx.send(embed=embed)
    
    @commands.cooldown(1, 8, commands.BucketType.member)
    @commands.hybrid_command(name='help')
    @discord.app_commands.describe(query='The module, command or subcommand to search')
    async def help_command(self, ctx: commands.Context, *, query: str = None):
        '''Get help about the bot'''
        await ctx.defer()
        if not query:
            await send_help(ctx, util.app_commands)
        else:
            cog = self.bot.get_cog(query.title())
            if cog:
                await send_help_cog(ctx, query.title(), util.app_commands)
            else:
                cmd = self.bot.get_command(query.lower())
                if isinstance(cmd, commands.HybridGroup):
                    await send_help_group(ctx, cmd, util.app_commands)
                elif isinstance(cmd, commands.HybridCommand):
                    await send_help_command(ctx, cmd, util.app_commands)
                else:
                    return await util.throw_error(ctx, text='I was unable to find something related to that')

async def setup(bot: commands.Bot):
    await bot.add_cog(General(bot))