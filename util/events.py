from discord.ext import commands

async def load(bot: commands.Bot, timeouts):
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
            elif timeout['id'] == 'giveaway':
                print('hola gibeway')
                guild = bot.get_guild(timeouts['data']['guild']) or await bot.fetch_guild(timeouts['data']['guild'])
                print(guild)
                channel = bot.get_channel(timeouts['data']['channel']) or await bot.fetch_channel(timeouts['data']['channel'])
                print(channel)
                message = await channel.fetch_message(timeouts['data']['message'])
                print(message)
                users = list(map(lambda reaction: reaction.users, list(filter(lambda reaction: reaction.emoji == '🎁' , message.reactions))))
                print(users)
        except:
            pass

    @timeouts.event
    async def on_create(timeout):
        pass
    
    await timeouts.check()