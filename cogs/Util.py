import discord
import re
from calendar import month
from discord.ext import commands
from main import util, timeouts
from datetime import datetime
from deep_translator import GoogleTranslator
from typing import Optional

class Util(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
    
    @commands.hybrid_command(name='avatar', aliases=['av', 'pfp'])
    @discord.app_commands.describe(member='The member to stalk')
    async def avatar(self, ctx: commands.Context, member: Optional[discord.Member]):
        '''Get someone's avatar'''
        await ctx.defer()
        if member is None:
            member = ctx.author
        user = member._user
        embed = discord.Embed(colour=3447003)
        embed.set_author(name=f'{user.name}#{user.discriminator}', icon_url=user.display_avatar)
        embed.set_image(url=str(user.display_avatar).replace('.webp', '.png'))
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name='user', aliases=['userinfo', 'whois'])
    @discord.app_commands.describe(member='The member to stalk')
    async def user(self, ctx: commands.Context, member: Optional[discord.Member]):
        '''Get someone's user info'''
        await ctx.defer()
        if member is None:
            member = ctx.author
        user = member._user
        emb = discord.Embed(colour=3447003)
        emb.set_author(name=f'{user.name}#{user.discriminator}', icon_url=user.display_avatar)
        emb.set_thumbnail(url=user.display_avatar)
        emb.description = f'**¬ Tag:** {user.name}#{user.discriminator}\n**¬ ID:** `{user.id}`\n**¬ Highest role:** {member.top_role.mention if member else "~~None~~"}\n**¬ Created:** <t:{round(user.created_at.timestamp())}:D>\n**¬ Joined:** <t:{round(member.joined_at.timestamp())}:D>\n\n**¬ Roles [{len(member.roles) if member else "~~0~~"}]:**\n{", ".join(list(map(lambda r: r.mention, member.roles))) if member else "~~None~~"}'
        await ctx.send(embed=emb)
    
    @commands.hybrid_command(name='server', aliases=['serverinfo'])
    async def server(self, ctx: commands.Context):
        '''Get the server info'''
        await ctx.defer()
        emb = discord.Embed(colour=3447003)
        emb.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
        emb.add_field(name='<:photoblob:1011458149653426226> '+ctx.guild.name, value=f'**¬ ID:** `{ctx.guild.id}`\n**¬ Owner:** <@{ctx.guild.owner_id}>\n**¬ Created:** <t:{round(ctx.guild.created_at.timestamp())}:D>')
        emb.add_field(name='<:blobhero:1011785174767382568> Staticts', value=f'**¬ Members:** {ctx.guild.member_count}\n**¬ Roles:** {len(ctx.guild.roles)}\n**¬ Channels:** {len(ctx.guild.channels)} (**Text:** {len(ctx.guild.text_channels)}, **Voice:** {len(ctx.guild.voice_channels)}, **Other:** {len(ctx.guild.channels) - len(ctx.guild.text_channels) - len(ctx.guild.voice_channels)})', inline=False)
        await ctx.send(embed=emb)
    
    @commands.command(name='servericon', aliases=['icon'])
    async def icon(self, ctx: commands.Context):
        '''Get the server icon'''
        if not ctx.guild.icon:
            return await util.throw_error(ctx, text="This server **doesn't** have an icon yet", bold=False)
        await ctx.defer()
        embed = discord.Embed(colour=3447003)
        embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon.url)
        embed.set_image(url=ctx.guild.icon.url.replace('.webp', '.png'))
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name='calendar', aliases=['date'])
    async def _calendar(self, ctx: commands.Context):
        '''Get the current month calendar'''
        await ctx.defer()
        text = month(datetime.now().year, datetime.now().month)
        t = f':calendar: **{datetime.now().year} {datetime.now().strftime("%B")}**\n```{text}```'
        await ctx.send(t)
    
    @commands.hybrid_command(name='translate', aliases=['tr'])
    @discord.app_commands.describe(target='The target idiom', text='The text to translate')
    async def translate(self, ctx: commands.Context, target: str, *, text: str):
        '''Translate a text'''
        try:
            target = target.lower().replace('zh-cn', 'zh-CN').replace('zh-tw', 'zh-TW').replace('ch', 'zh-CN')
            g = GoogleTranslator(source="auto", target='en')
            if target not in list(g.get_supported_languages(as_dict=True).values()):
                b = discord.ui.Button(style=discord.ButtonStyle.blurple, label="Show supported languages")
                async def _i(i: discord.Interaction):
                    if i.user.id is not ctx.author.id:
                        return await i.response.send_message("This interaction isn't for you <:bloboohcry:1011458104782758009>", ephemeral=True)
                    langs = ', '.join(list(map(lambda lang: f'**`{lang}`**', list(g.get_supported_languages(as_dict=True).values()))))
                    await i.response.send_message(langs, ephemeral=True)    
                b.callback = _i
                v = discord.ui.View(timeout=60.0).add_item(b)
                message = await util.throw_error(ctx, text="Invalid target language provided", view=v, defer=False)
                v.message = message
                async def _t():
                    try:
                        b.disabled = True
                        await v.message.edit(view=v.clear_items().add_item(b))
                    except:
                        pass
                v.on_timeout = _t
                return
            await ctx.defer()
            g.target = target
            await ctx.send(f'**__{g.source.upper()}__ > __{g.target.upper()}__**```fix\n{g.translate(text)}```')
        except:
            await util.throw_error(ctx, text="Invalid translation, something went wrong")

    @commands.hybrid_command(name='weather')
    @discord.app_commands.describe(city='The city to search')
    async def weather(self, ctx: commands.Context, *, city: str):
        '''Get some city weather'''
        v = await util.request(url="https://api.miduwu.ga/json/weather", params={"query": city}, as_dict=True)
        if not v or v.status != 200:
            return await util.throw_error(ctx, text=f"Invalid city provided")
        await ctx.defer()
        emb = discord.Embed(title=v.data["data"]["location"]["name"], color=3447003)
        emb.set_author(name=f'{ctx.author.name}#{ctx.author.discriminator}', icon_url=ctx.author.display_avatar)
        emb.add_field(name="Coordinates:", value=f'{v.data["data"]["location"]["lat"]}, {v.data["data"]["location"]["long"]}')
        emb.add_field(name="Timezone:", value=v.data["data"]["location"]["timezone"])
        emb.add_field(name="Temperature:", value=f'{v.data["data"]["current"]["temperature"]} °C')
        emb.add_field(name="Sky:", value=v.data["data"]["current"]["skytext"])
        emb.add_field(name="Humidity:", value=v.data["data"]["current"]["humidity"])
        emb.add_field(name="Wind Speed:", value=v.data["data"]["current"]["windspeed"])
        emb.set_thumbnail(url=v.data["data"]["current"]["imageUrl"])
        emb.timestamp = datetime.now()
        await ctx.send(embed=emb)
    
    @commands.hybrid_command(name='quote', aliases=['q'])
    @discord.app_commands.describe(url='The message URL that i will quote')
    async def quote(self, ctx: commands.Context, url: str):
        '''Quote a message in this server'''
        found = re.findall('channels\/[\d]+\/[\d]+\/[\d]+', url)
        if not found:
            return await util.throw_error(ctx, text='Invalid message URL provided')
        g, c, m = found[0].split('/')[1:]
        if int(g) != ctx.guild.id:
            return await util.throw_error(ctx, text='That message is not in this server')
        channel = self.bot.get_channel(int(c))
        if not channel:
            return await util.throw_error(ctx, text='I was unable to find that channel')
        try:
            message = await channel.fetch_message(int(m))
        except:
            message = None
        if not message:
            return await util.throw_error(ctx, text='I was unable to find that message')
        await ctx.defer()
        at = await message.attachments[0].to_file() if message.attachments else None
        try:
            await ctx.defer()
            await ctx.send(content=message.content, embeds=message.embeds, file=at if at else None)
        except:
            await util.throw_error(ctx, text='I was unable to quote that message')
    
    @commands.hybrid_command(name='reminder', aliases=['remindme', 'remind'])
    @discord.app_commands.describe(time='The readable time to wait. Ex: 3m = 3 minutes', note='The text to remind you (send after provided time)')
    async def _add(self, ctx: commands.Context, time: str, *, note: str):
        '''Set a reminder'''
        as_ms = util.ms(time)
        if not as_ms:
            return await util.throw_error(ctx, text='Invalid time provided, use something like: `1d`')
        if as_ms >= util.ms('1mo') or util.ms('10s') >= as_ms:
            return await util.throw_error(ctx, text='Invalid time provided, it must be between **10 seconds** and **2 weeks**', bold=False)
        await ctx.defer()
        as_long = util.ms(as_ms, long=True)
        await timeouts.add(time=as_ms / 1000, id='reminder', data={ 'author': ctx.author.id, 'note': note })
        await util.throw_fine(ctx, text=f"I've saved your reminder, i will notify you in **{as_long}** the next:\n\n{note[:1900]}", defer=False, bold=False, emoji=False)
    
    @commands.hybrid_command(name='color', aliases=['hex'])
    @discord.app_commands.describe(hex='The color hex code')
    async def color(self, ctx: commands.Context, hex: str):
        '''Get a color information using its HEX code'''
        hex = re.sub('[^a-f\d]', '', hex, flags=re.IGNORECASE)
        if not util.is_hex(hex):
            return await util.throw_error(ctx, text='Invalid hex color code provided')
        r = await util.request(url=f'https://api.alexflipnote.dev/colour/{hex}')
        if not r:
            return await util.throw_error(ctx, text='I was unable to fetch that color')
        await ctx.defer()
        emb = discord.Embed(title=r['name'], color=r['int'])
        emb.set_author(name=f'{ctx.author.name}#{ctx.author.discriminator}', icon_url=ctx.author.display_avatar)
        emb.set_image(url=r['image'])
        emb.add_field(name='HEX:', value=r['hex'])
        emb.add_field(name='RGB:', value=r['rgb'])
        emb.add_field(name='Int', value=str(r['int']))
        await ctx.send(embed=emb)

async def setup(bot: commands.Bot):
    await bot.add_cog(Util(bot))