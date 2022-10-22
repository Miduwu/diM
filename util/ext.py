from typing import Literal
from discord.ext import commands
from asyncio import sleep
import discord
import aiohttp

class Util:
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.uptime = None
    
    async def throw_error(self, context: commands.Context, text: str, view: discord.ui.View = None, defer: bool = True, bold: bool = True):
        try:
            m = await context.send(content=f'**{text}** <:bloboohcry:1011458104782758009>' if bold else text + ' <:bloboohcry:1011458104782758009>', view=view)
            if defer:
                await sleep(7)
                await m.delete()
            else:
                return m
        except:
            pass
    
    async def throw_fine(self, context: commands.Context, text: str, view: discord.ui.View = None, defer: bool = True, bold: bool = True):
        try:
            m = await context.send(content=f'**{text}** <:blobheart:1011458084239056977>' if bold else text + ' <:blobheart:1011458084239056977>', view=view)
            if defer:
                await sleep(7)
                await m.delete()
            else:
                return m
        except:
            pass
    
    async def request(self, *, url: str, extract: Literal['json', 'read', 'text'] = 'json'):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url=url) as res:
                    if extract.lower() == 'json':
                        return await res.json()
                    elif extract.lower() == 'read':
                        return await res.read()
                    elif extract.lower() == 'text':
                        return await res.text()
        except:
            return None