import discord, aiohttp, os
import jishaku

from discord.ext import commands

description = """
Hi my name is Tokyo
"""

class TBot(commands.Bot):
    def __init__(self):
        allowed_mentions = discord.AllowedMentions(roles=False, everyone=False, users=True)
        intents = discord.Intents(
            guilds=True,
            members=True,
            emojis=True,
            messages=True,
            reactions=True,
            message_content=True,
        )
        super().__init__(
            command_prefix="t?",
            description=description,
            pm_help=None,
            help_attrs=dict(hidden=True),
            heartbeat_timeout=150.0,
            allowed_mentions=allowed_mentions,
            intents=intents
        )
    
    async def setup_hook(self):
        await self.load_extension("jishaku")
        for file in os.listdir("./cogs"):
            if file.endswith(".py"):
                await self.load_extension(f"cogs.{file[:-3]}")
    
    async def close(self):
        await super().close()
    
    async def start(self, reconnect: bool = True):
        return await super().start(os.getenv("TOKEN"), reconnect=reconnect)