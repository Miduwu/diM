from discord.ext import commands
from time import sleep

class Util:
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
    
    async def throw_error(self, context: commands.Context, text: str, defer: bool = True, bold: bool = True):
        try:
            m = await context.send(f'**{text}** <:bloboohcry:1011458104782758009>' if bold else text + ' <:bloboohcry:1011458104782758009>')
            if defer:
                sleep(7)
                await m.delete()
        except:
            pass
    
    async def throw_fine(self, context: commands.Context, text: str, defer: bool = True, bold: bool = True):
        try:
            m = await context.send(f'**{text}** <:blobheart:1011458084239056977>' if bold else text + ' <:blobheart:1011458084239056977>')
            if defer:
                sleep(7)
                await m.delete()
        except:
            pass