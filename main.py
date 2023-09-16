import asyncio
import discord
import os
from util import coreback
from discord.ext import commands
from util.modules import execs, midb, mongo, interpreter as inter

os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
os.environ["JISHAKU_NO_DM_TRACEBACK"] = "True" 
os.environ["JISHAKU_HIDE"] = "True"

db = midb.Database(path='./database', tables=['Main', 'Users', 'Guilds', 'Timeouts'])

mongodb = mongo.MongoDB(os.getenv('MONGO'))

async def get_prefix(client, message: discord.Message):
    if not message.guild:
        return 't!'
    p = await mongodb.get(table='guilds', id=message.guild.id, path='prefix') or 't!'
    return commands.when_mentioned_or(p)(client, message)

timeouts = execs.Timeouts(db)

@timeouts.event
async def on_expires(timeout):
    try:
        if timeout['id'] == 'reminder':
            user = timeouts.bot.get_user(timeout["data"]["author"]) or await timeouts.bot.fetch_user(timeout['data']['author'])
            if user:
                await user.send(f'**Here is a reminder! ⏰**\n{timeout["data"]["note"][:1950]}')
    except Exception as err:
        print("\n".join(util.load_exception(err)))

class diM(commands.Bot):
    async def setup_hook(self) -> None:
        await bot.load_extension("jishaku") # feature
        for file in os.listdir('./cogs'):
            if file.endswith('.py'):
                await bot.load_extension(f'cogs.{file[:-3]}')

intents = discord.Intents.default()
intents.presences = False
intents.message_content = True
intents.members = True
intents.dm_reactions = False

bot = diM(
    command_prefix=get_prefix,
    owner_ids=[664261902712438784, 930588488590581850],
    case_insensitive=True,
    allowed_mentions=discord.AllowedMentions(everyone=False, roles=True, users=True),
    strip_after_prefix=True,
    intents=intents,
    help_command=None,
    activity=discord.Activity(type=discord.ActivityType.listening, name="new update!")
    )

util = coreback.Util(bot)

interpreter = inter.Interpreter(util)

@bot.check
async def global_check(ctx: commands.Context):
    if ctx.command.__original_kwargs__.get("disabled", None):
        await util.throw_error(ctx, text="This command is under maintenance!")
        return False
    if ctx.guild is None:
        await util.throw_error(ctx, text=f'This command is only for servers!')
        return False
    return True

async def main():
    async with bot:
        await bot.start(os.getenv('TOKEN'))

if __name__ == "__main__":
    asyncio.run(main())
