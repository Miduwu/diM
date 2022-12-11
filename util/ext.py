import re
from discord.ext import commands
from typing import Literal
from asyncio import sleep
import discord
import aiohttp
from util.time import load
import random

class Util:
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.uptime = None
    
    async def throw_error(self, context: commands.Context, text: str, view: discord.ui.View = None, defer: bool = True, bold: bool = True, ephemeral: bool = True, emoji: bool = True):
        try:
            m = await context.send(content=f'**{text}** {"<:bloboohcry:1011458104782758009>" if emoji else ""}' if bold else text + f' {"<:bloboohcry:1011458104782758009>" if emoji else ""}', view=view, ephemeral=ephemeral)
            if defer:
                await sleep(7)
                await m.delete()
        except:
            pass
    
    async def throw_fine(self, context: commands.Context, text: str, view: discord.ui.View = None, defer: bool = True, bold: bool = True, ephemeral: bool = False, emoji: bool = True):
        try:
            m = await context.send(content=f'**{text}** {"<:blobheart:1011458084239056977>" if emoji else ""}' if bold else text + f' {"<:blobheart:1011458084239056977>" if emoji else ""}', view=view, ephemeral=ephemeral)
            if defer:
                await sleep(7)
                await m.delete()
        except:
            pass
    
    async def request(self, *, url: str, params: dict = {}, extract: Literal['json', 'read', 'text'] = 'json', as_dict=False):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url=url, params=params) as res:
                    if res.status != 200 and res.status != 201:
                        return None
                    if extract.lower() == 'json':
                        return Response(await res.json(), res.status, res.content_type) if as_dict else await res.json()
                    elif extract.lower() == 'read':
                        return Response(await res.read(), res.status, res.content_type) if as_dict else await res.read()
                    elif extract.lower() == 'text':
                        return Response(await res.text(), res.status, res.content_type) if as_dict else await res.text()
        except Exception as err:
            print(err)
            return None
    
    def ms(self, time, long = False):
        return load(time, long=long)
    
    def is_hex(self, text: str):
        return True if re.match('^([A-F0-9]{6}|[A-F0-9]{3})$', text, flags=re.IGNORECASE) else False
    
    def choice(self, arr: list, amount = 1):
        if amount >= len(arr):
            return arr
        w3 = []
        i = 0
        while i < amount:
            r = random.choice(arr)
            if r in w3:
                continue
            else:
                w3.append(r)
            i += 1
        w3.sort()
        return w3

    def cut(self, text: str, max: int):
        if len(text) >= max:
            return text[:max] + '...'
        else:
            return text

class Response:
    def __init__(self, data, status, contenttype) -> None:
        self.data = data or None
        self.status = status or None
        self.content_type = contenttype or None