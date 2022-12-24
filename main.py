import asyncio
import discord
import os
import dotenv
from util import coreback, events, helpcmd
from discord.ext import commands
from util.modules import execs, midb, mongo

dotenv.load_dotenv()

db = midb.Database(path='./database', tables=['Main', 'Users', 'Guilds', 'Timeouts'])
timeouts = execs.Timeouts(db)

mongodb = mongo.MongoDB(os.getenv('MONGO'))

async def Task(bot: commands.Bot):
    await bot.wait_until_ready()
    await events.load(bot, timeouts)

async def get_prefix(client, message: discord.Message):
    if not message.guild:
        return '$'
    return await mongodb.get(table='guilds', id=message.guild.id, path='prefix') or '$'

class diM(commands.Bot):
    async def setup_hook(self):
        self.loop.create_task(Task(self))

bot = diM(command_prefix=get_prefix, owner_ids=[664261902712438784, 930588488590581850], strip_after_prefix=True, intents=discord.Intents.all(), help_command=None)

util = coreback.Util(bot)

async def main():
    for file in os.listdir('./cogs'):
        if file.endswith('.py'):
            await bot.load_extension(f'cogs.{file[:-3]}')

    async with bot:
        await bot.start(os.getenv('TOKEN'))

if __name__ == "__main__":
    asyncio.run(main())