from typing import Literal
import discord
from main import util, db
from discord.ext import commands

class Listeners(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, commands.UserNotFound):
            return await util.throw_error(ctx, text=f"**Missing or invalid user provided...**", bold=False)
        elif isinstance(error, commands.NotOwner):
            return await util.throw_error(ctx, text=f"**{ctx.author.name}**, you **don't** own this bot", bold=False)
        elif isinstance(error, commands.MissingPermissions):
            return await util.throw_error(ctx, text=f"**{ctx.author.name}**, you **don't** have permissions enough to use this command", bold=False)
        raise error

    @commands.Cog.listener()
    async def on_ready(self):
        print('diM is online')
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        prefix = db.get(f'{message.guild.id}.prefix', 'Guilds') or '$'
        if not message.content.startswith(prefix) or message.author.bot:
            return
        else:
            name = message.content[len(prefix):].strip().split(' ')[0]
            cmds = db.get(f'{message.guild.id}.commands', 'Guilds') or []
            found = next((item for item in cmds if item['name'] == name.lower()), None)
            if not found:
                return
            await message.channel.send(found['content'])

async def setup(bot: commands.Bot):
    await bot.add_cog(Listeners(bot))