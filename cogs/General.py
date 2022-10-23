import discord
import sys
import datetime
from discord.ext import commands
from main import util

@discord.app_commands.guild_only()
class General(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
    @discord.app_commands.command(name='ping')
    async def ping(self, i: discord.Interaction):
        await i.response.send_message(f'Pong! :ping_pong: **{round(self.bot.latency, 2)}s**')
    
    @discord.app_commands.command(name='stats', description="Look at the bot stats and information about the software")
    async def stats(self, i: discord.Interaction):
        uptime = datetime.timedelta(milliseconds=(round(datetime.datetime.now().timestamp()) - round(util.uptime.timestamp())) * 1000)
        # view = discord.ui.View().add_item(discord.ui.Button(style=discord.ButtonStyle.link, label="Click this", url="https://google.com"))
        embed = discord.Embed(title=f'{self.bot.user.name}\'s stats', colour=3447003)
        embed.add_field(name='Tracking', value=f'¬ **Servers:** {len(self.bot.guilds)}\n¬ **Users:** {len(self.bot.users)}\n¬ **Commands:** {len(self.bot.commands)}', inline=True)
        embed.add_field(name='Software', value=f'¬ **Python:** `{sys.version.split(" ")[0]}`\n¬ **Discord.py:** `{discord.__version__}`\n¬ **Platform:** `{sys.platform}`')
        embed.set_thumbnail(url=self.bot.user.display_avatar)
        embed.set_footer(text=f'Uptime: {uptime} hrs.')
        await i.response.send_message(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(General(bot))