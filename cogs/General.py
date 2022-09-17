import discord
from discord.ext import commands

class General(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
    
    @commands.command(name='ping', aliases=['latency'])
    async def ping(self, ctx: commands.Context):
        await ctx.send(f'Pong! :ping_pong: **{round(self.bot.latency, 2)}s**')

async def setup(bot: commands.Bot):
    await bot.add_cog(General(bot))