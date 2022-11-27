import discord
import sys
import datetime
from discord.ext import commands
from main import util, timeouts

class General(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
    
    @commands.hybrid_group(name='bot')
    async def _bot(self, ctx):
        '''Get information related to the bot'''
        ...

    @commands.is_owner()
    @_bot.command(name='ping')
    async def ping(self, ctx: commands.Context):
        '''Get the bot websocket latency'''
        await ctx.send(f'Pong! :ping_pong: **{round(self.bot.latency, 2)}s**')
    
    @_bot.command(name='info')
    async def stats(self, ctx: commands.Context):
        '''Get the bot info'''
        uptime = datetime.timedelta(milliseconds=(round(datetime.datetime.now().timestamp()) - round(util.uptime.timestamp())) * 1000)
        # view = discord.ui.View().add_item(discord.ui.Button(style=discord.ButtonStyle.link, label="Click this", url="https://google.com"))
        embed = discord.Embed(title=f'{self.bot.user.name}\'s stats', colour=3447003)
        embed.add_field(name='Tracking', value=f'¬ **Servers:** {len(self.bot.guilds)}\n¬ **Users:** {len(self.bot.users)}\n¬ **Commands:** {len(self.bot.commands)}', inline=True)
        embed.add_field(name='Software', value=f'¬ **Python:** `{sys.version.split(" ")[0]}`\n¬ **Discord.py:** `{discord.__version__}`\n¬ **Platform:** `{sys.platform}`')
        embed.set_thumbnail(url=self.bot.user.display_avatar)
        embed.set_footer(text=f'Uptime: {uptime} hrs.')
        await ctx.send(embed=embed)
    
    @commands.command(name='cocacola')
    @commands.is_owner()
    async def test(self, ctx: commands.Context, time: str):
        await ctx.send('antes')
        await timeouts.add(time=int(time), id='test', data={"channel": ctx.channel.id, "author": ctx.author.id})

async def setup(bot: commands.Bot):
    await bot.add_cog(General(bot))