from discord.ext import commands
from time import sleep
import discord

class Util:
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.uptime = None
    
    async def throw_error(self, context: commands.Context, text: str, view: discord.ui.View = None, defer: bool = True, bold: bool = True):
        try:
            m = await context.send(content=f'**{text}** <:bloboohcry:1011458104782758009>' if bold else text + ' <:bloboohcry:1011458104782758009>', view=view)
            if defer:
                sleep(7)
                await m.delete()
        except:
            pass
    
    async def throw_fine(self, context: commands.Context, text: str, view: discord.ui.View = None, defer: bool = True, bold: bool = True):
        try:
            m = await context.send(content=f'**{text}** <:blobheart:1011458084239056977>' if bold else text + ' <:blobheart:1011458084239056977>', view=view)
            if defer:
                sleep(7)
                await m.delete()
        except:
            pass