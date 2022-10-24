from discord.ext import commands
from typing import Literal
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
        except:
            pass
    
    async def throw_fine(self, context: commands.Context, text: str, view: discord.ui.View = None, defer: bool = True, bold: bool = True):
        try:
            m = await context.send(content=f'**{text}** <:blobheart:1011458084239056977>' if bold else text + ' <:blobheart:1011458084239056977>', view=view)
            if defer:
                await sleep(7)
                await m.delete()
        except:
            pass
    async def request(self, *, url: str, params: dict = {}, extract: Literal['json', 'read', 'text'] = 'json', as_dict=False):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url=url, params=params) as res:
                    if extract.lower() == 'json':
                        return Response(await res.json(), res.status, res.content_type) if as_dict else await res.json()
                    elif extract.lower() == 'read':
                        return Response(await res.read(), res.status, res.content_type) if as_dict else await res.read()
                    elif extract.lower() == 'text':
                        return Response(await res.text(), res.status, res.content_type) if as_dict else await res.text()
        except Exception as err:
            print(err)
            return None

class Response:
    def __init__(self, data, status, contenttype) -> None:
        self.data = data or None
        self.status = status or None
        self.content_type = contenttype or None