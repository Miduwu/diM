import asyncio
import discord
import os
import dotenv
from util import ext, midb
from discord.ext import commands

dotenv.load_dotenv()

bot = commands.Bot(command_prefix=(lambda client, message: db.get(f'{message.guild.id}.prefix', 'Guilds') or '$'), owner_ids=[664261902712438784], strip_after_prefix=True, intents=discord.Intents.all())

util = ext.Util(bot)
db = midb.Database(path='./database', tables=['Main', 'Users', 'Guilds'])

async def main():
    for file in os.listdir('./cogs'):
        if file.endswith('.py'):
            await bot.load_extension(f'cogs.{file[:-3]}')

    async with bot:
        await bot.start(os.getenv('TOKEN'))

if __name__ == "__main__":
    asyncio.run(main())