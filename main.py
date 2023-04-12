import asyncio
import discord
import os
import dotenv
from util import coreback
from discord.ext import commands
from util.modules import execs, midb, mongo, interpreter as inter

dotenv.load_dotenv()

db = midb.Database(path='./database', tables=['Main', 'Users', 'Guilds', 'Timeouts'])

mongodb = mongo.MongoDB(os.getenv('MONGO'))

async def get_prefix(client, message: discord.Message):
    if not message.guild:
        return 't!'
    p = await mongodb.get(table='guilds', id=message.guild.id, path='prefix') or 't!'
    return commands.when_mentioned_or(p)

timeouts = execs.Timeouts(db)

@timeouts.event
async def on_expires(timeout):
    try:
        if timeout['id'] == 'reminder':
            user = timeouts.bot.get_user(timeout["data"]["author"]) or await timeouts.bot.fetch_user(timeout['data']['author'])
            if user:
                await user.send(f'**There is a reminder! ⏰**\n{timeout["data"]["note"][:1950]}')
        elif timeout['id'] == 'giveaway':
            guild = timeouts.bot.get_guild(timeout["data"]["guild"]) or await timeouts.bot.fetch_guild(timeout["data"]["guild"])
            channel = guild.get_channel(timeout["data"]["channel"]) or await guild.fetch_channel(timeout["data"]["channel"])
            message = await channel.fetch_message(timeout["data"]["message"])
            users = [user async for user in message.reactions[0].users()]
            users.pop(users.index(timeouts.bot.user))
            winners = util.choice(users, timeout["data"]["winners"]) if len(users) else None
            embed = discord.Embed().from_dict(message.embeds[0].to_dict())
            embed.title = "Giveaway ended!"
            embed.set_footer(text="Giveaway ended.")
            winners_parsed = ", ".join([u.mention for u in winners]) if winners else "No winner."
            embed.description = f"🎁 **Prize:** {timeout['data']['prize']}\n\n🎉 **Hosted by:** <@{timeout['data']['host']}>\n🏆 **Winners:** {winners_parsed}"
            await message.edit(embed=embed)
            if winners:
                await message.reply(content=f"🎊 **Congratulations!** to {winners_parsed}. You won: **{timeout['data']['prize']}**\n\n{message.jump_url}")
    except Exception as err:
        print("\n".join(util.load_exception(err)))

class diM(commands.Bot):
    async def setup_hook(self) -> None:
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
    strip_after_prefix=True,
    intents=intents,
    help_command=None,
    activity=discord.Activity(type=discord.ActivityType.listening, name="new update!")
    )

util = coreback.Util(bot)

interpreter = inter.Interpreter(util)

@bot.check
async def guild_only(ctx: commands.Context):
    if ctx.guild is None:
        await util.throw_error(ctx, text=f'This command is only for servers!')
    return ctx.guild != None

async def main():
    async with bot:
        await bot.start(os.getenv('TOKEN'))

if __name__ == "__main__":
    asyncio.run(main())