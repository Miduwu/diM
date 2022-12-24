import discord
import datetime
from discord.ext import commands
from main import util, timeouts

class Giveaways(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
    
    @commands.is_owner()
    @commands.hybrid_group(name='giveaways')
    async def _gws(self, ctx):
        '''Manage the server giveaways'''
        ...
    
    @commands.is_owner()
    @_gws.command(name='start')
    @discord.app_commands.describe()
    async def start(self, ctx: commands.Context, time: str, winners: int, prize: str):
        '''Start a new giveaway'''
        time = util.ms(time)
        if not time:
            return await util.throw_error(ctx, text='Invalid time provided, use something like: `1d`')
        if time >= util.ms('2w') or util.ms('1m') > time:
            return await util.throw_error(ctx, text='Invalid time provided, it must be between **1 minute** and **2 weeks**', bold=False)
        if winners > 10 or 1 > winners:
            return await util.throw_error(ctx, text='Invalid winners count provided, it must be between **1** and **10**', bold=False)
        prize = util.cut(text=prize, max=200)
        emb = discord.Embed(title='Giveaway started!', color=3912003, description=f'🎁 **Prize:** {prize}\n\n⏰ **Ends:** <t:{round(datetime.datetime.now().timestamp() + (time / 1000))}:R>\n🎉 **Hosted by:** {ctx.author.mention}\n🏆 **Winners:** {winners}')
        emb.set_footer(text='React with 🎁 to join!')
        message = await ctx.channel.send(embed=emb)
        if message:
            await message.add_reaction('🎁')
            await util.throw_fine(ctx, text='The giveaway was created successfully!', ephemeral=True)
            await timeouts.add(time=time / 1000, id='giveaway', data={ 'guild': ctx.guild.id, 'channel': ctx.channel.id, 'message': message.id, 'winners': winners, 'price': prize, 'host': ctx.author.id })
        else:
            await util.throw_error(ctx, text='Ops! Something went wrong!', ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Giveaways(bot))