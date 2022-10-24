import discord
import sys
import datetime
from discord.ext import commands
from main import util

class General(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
    @commands.command(name='ping', aliases=['latency'])
    async def ping(self, ctx: commands.Context):
        await ctx.send(f'Pong! :ping_pong: **{round(self.bot.latency, 2)}s**')
    
    @commands.command(name='stats', aliases=['botinfo'])
    async def stats(self, ctx: commands.Context):
        uptime = datetime.timedelta(milliseconds=(round(datetime.datetime.now().timestamp()) - round(util.uptime.timestamp())) * 1000)
        # view = discord.ui.View().add_item(discord.ui.Button(style=discord.ButtonStyle.link, label="Click this", url="https://google.com"))
        embed = discord.Embed(title=f'{ctx.bot.user.name}\'s stats', colour=3447003)
        embed.add_field(name='Tracking', value=f'¬ **Servers:** {len(ctx.bot.guilds)}\n¬ **Users:** {len(ctx.bot.users)}\n¬ **Commands:** {len(ctx.bot.commands)}', inline=True)
        embed.add_field(name='Software', value=f'¬ **Python:** `{sys.version.split(" ")[0]}`\n¬ **Discord.py:** `{discord.__version__}`\n¬ **Platform:** `{sys.platform}`')
        embed.set_thumbnail(url=ctx.bot.user.display_avatar)
        embed.set_footer(text=f'Uptime: {uptime} hrs.')
        await ctx.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(General(bot))