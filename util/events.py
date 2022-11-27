from main import timeouts
from discord.ext import commands

async def load(bot: commands.Bot):
    @timeouts.event
    async def on_check():
        pass

    @timeouts.event
    async def on_expires(timeout):
        await bot.wait_until_ready()
        try:
            if timeout['id'] == 'reminder':
                user = bot.get_user(timeout['data']['author']) or await bot.fetch_user(timeout['data']['author'])
                if user:
                    await user.send(f'**There is a reminder! ⏰**\n{timeout["data"]["note"][:1950]}')
        except:
            pass

    @timeouts.event
    async def on_create(timeout):
        pass
    
    await timeouts.check()