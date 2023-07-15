import discord

from discord.ext import commands
from main import TBot

class Misc(commands.Cog):
    def __init__(self, bot: TBot) -> None:
        self.bot = bot
    
    @commands.hybrid_command(brief="This is a small brief", member="No se")
    @discord.app_commands.describe(member="A member")
    async def avatar(self, ctx: commands.Context, member: discord.Member = None):
        """Shows an user avatar
        # Parameters:
            member: nooo
        """
        member = member or ctx.author
        await ctx.send(member.display_avatar)

async def setup(bot: TBot):
    await bot.add_cog(Misc(bot))
