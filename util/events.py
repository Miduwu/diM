from main import timeouts
from traceback import format_exception
from discord.ext import commands

async def load(bot: commands.Bot):
    @timeouts.event
    async def on_check():
        pass

    @timeouts.event
    async def on_expires(timeout):
        await bot.wait_until_ready()
        try:
            ch = bot.get_channel(timeout["data"]["channel"]) or await bot.fetch_channel(timeout["data"]["channel"])
            user = bot.get_user(timeout["data"]["author"]) or await bot.fetch_user(timeout["data"]["author"])
            await ch.send(f'Helou {user.name}')
        except Exception as err:
            print("".join(format_exception(err, err, err.__traceback__)))

    @timeouts.event
    async def on_create(timeout):
        pass
    
    await timeouts.check()