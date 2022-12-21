from datetime import datetime
from main import util
from discord.ext import commands

class Listeners(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, commands.UserNotFound):
            return await util.throw_error(ctx, text=f"**Missing or invalid user provided**", bold=False)
        elif isinstance(error, commands.MemberNotFound):
            return await util.throw_error(ctx, text=f"**Missing or invalid member provided**", bold=False)
        elif isinstance(error, commands.NotOwner):
            return await util.throw_error(ctx, text=f"**{ctx.author.name}**, you **don't** own this bot", bold=False, ephemeral=True)
        elif isinstance(error, commands.MissingPermissions):
            return await util.throw_error(ctx, text=f"**{ctx.author.name}**, you **don't** have permissions enough to use this command", bold=False)
        elif isinstance(error, commands.MissingRequiredArgument):
            return await util.throw_error(ctx, text=f"Missing **{error.param.name}** parameter", bold=False, defer=False)
        elif isinstance(error, commands.RoleNotFound):
            return await util.throw_error(ctx, text=f"**Missing or invalid role provided**", bold=False)
        elif isinstance(error, commands.ChannelNotFound):
            return await util.throw_error(ctx, text=f"**Missing or invalid channel provided**", bold=False)
        raise error

    @commands.Cog.listener()
    async def on_ready(self):
        print('diM is online')
        util.uptime = datetime.now()
        await self.bot.tree.sync()

async def setup(bot: commands.Bot):
    await bot.add_cog(Listeners(bot))