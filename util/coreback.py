import re
from discord.ext import commands
from typing import Literal, List, Optional
from asyncio import sleep
import discord
import aiohttp
from util.modules.time import load
from traceback import format_exception
import random
import pydash as _
import io
from PIL import Image
import regex

class Util:
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.uptime = None
        self.app_commands: List[discord.app_commands.AppCommand] = []
    
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
    
    async def get(self, *, url: str, params: dict = {}, extract: Literal['json', 'read', 'text'] = 'json', as_dict=False):
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
        except:
            pass
    
    async def download_bytes(self, body):
        body = await self.get(url=body, extract='read')
        with Image.open(io.BytesIO(body)) as inp:
            buff = io.BytesIO()
            inp.save(buff, "png")
            buff.seek(0)
            return buff
    
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
    
    def load_exception(self, exception: Exception):
        return format_exception(exception, exception, exception.__traceback__)
    
    def parse_emoji(self, emoji: str, allow: Literal["unicode", "custom", "both"] = "both"):
        if not emoji:
            return None
        is_unicode = regex.match(r"\p{Extended_Pictographic}|\p{Regional_Indicator}", emoji, flags=regex.UNICODE)
        is_custom = regex.findall(r"<(a)?:([a-zA-Z\d_]{2,32}):(\d{18,22})>", emoji)
        if allow == "unicode":
            return emoji if is_unicode else None
        elif allow == "custom":
            return emoji if is_custom else None
        else:
            return emoji if is_custom or is_unicode else None
    
    def resolve_emoji(self, emoji):
        if not emoji:
            return { "animated": False, "id": None, "name": None }
        splits = emoji.split(":")
        if 3 > len(splits):
            return { "animated": False, "id": None, "name": None }
        return { "animated": splits[0] == "a", "id": splits[2], "name": splits[1] }
    
    def is_text(self, channel: discord.abc.GuildChannel):
        return channel.type == discord.ChannelType.text or channel.type == discord.ChannelType.news or channel.type == discord.ChannelType.news_thread or channel.type == discord.ChannelType.private or channel.type == discord.ChannelType.private_thread or channel.type == discord.ChannelType.public_thread
    
    def is_hex(self, text):
        try:
            return True if re.match('^([A-F0-9]{6}|[A-F0-9]{3})$', text.replace("#", ""), flags=re.IGNORECASE) else False
        except:
            return None
        

async def sync(cls, *, guild: Optional[discord.abc.Snowflake] = None) -> List[discord.app_commands.AppCommand]:
        """|coro|
        Syncs the application commands to Discord.
        This also runs the translator to get the translated strings necessary for
        feeding back into Discord.
        This must be called for the application commands to show up.
        Parameters
        -----------
        guild: Optional[:class:`~discord.abc.Snowflake`]
            The guild to sync the commands to. If ``None`` then it
            syncs all global commands instead.
        Raises
        -------
        HTTPException
            Syncing the commands failed.
        CommandSyncFailure
            Syncing the commands failed due to a user related error, typically because
            the command has invalid data. This is equivalent to an HTTP status code of
            400.
        Forbidden
            The client does not have the ``applications.commands`` scope in the guild.
        MissingApplicationID
            The client does not have an application ID.
        TranslationError
            An error occurred while translating the commands.
        Returns
        --------
        List[:class:`AppCommand`]
            The application's commands that got synced.
        """

        if cls.client.application_id is None:
            raise discord.app_commands.MissingApplicationID

        commands: List[discord.app_commands.AppCommand] = cls._get_all_commands(guild=guild)

        translator = cls.translator
        if translator:
            payload = [await command.get_translated_payload(translator) for command in commands]
        else:
            payload = [command.to_dict() for command in commands]
        try:
            for i in range(0, len(payload)):
                payload[i]['dm_permission'] = False
            if guild is None:
                data = await cls._http.bulk_upsert_global_commands(cls.client.application_id, payload=payload)
            else:
                data = await cls._http.bulk_upsert_guild_commands(cls.client.application_id, guild.id, payload=payload)
        except discord.HTTPException as e:
            if e.status == 400 and e.code == 50035:
                raise discord.app_commands.CommandSyncFailure(e, commands) from None
            raise

        return [discord.app_commands.AppCommand(data=d, state=cls._state) for d in data]

class Response:
    def __init__(self, data, status, contenttype) -> None:
        self.data = data or None
        self.status = status or None
        self.content_type = contenttype or None