import discord
import re
from calendar import month
from html import unescape
from discord.ext import commands
from main import util, timeouts
from datetime import datetime
from deep_translator import GoogleTranslator
from typing import Optional, Literal
from util.views import Paginator
from urllib.parse import quote_plus
import pydash as _

class Util(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.hybrid_group(name='user')
    async def user(self, ctx: commands.Context):
        '''Fetch some user information'''
        ...
    
    @commands.cooldown(1, 4, commands.BucketType.member)
    @user.command(name='avatar', aliases=['av'])
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
    
    @commands.cooldown(1, 5, commands.BucketType.member)
    @user.command(name='info', aliases=['whois'])
    @discord.app_commands.describe(member='The member to stalk')
    async def userinfo(self, ctx: commands.Context, member: Optional[discord.Member]):
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
    
    @commands.hybrid_group(name='server')
    async def server(self, ctx: commands.Context):
        '''Fetch some server information'''
        ...
    
    @commands.cooldown(1, 5, commands.BucketType.member)
    @server.command(name='info')
    async def serverinfo(self, ctx: commands.Context):
        '''Get the server info'''
        await ctx.defer()
        emb = discord.Embed(colour=3447003)
        emb.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
        emb.add_field(name='<:photoblob:1011458149653426226> '+ctx.guild.name, value=f'**¬ ID:** `{ctx.guild.id}`\n**¬ Owner:** <@{ctx.guild.owner_id}>\n**¬ Created:** <t:{round(ctx.guild.created_at.timestamp())}:D>')
        emb.add_field(name='<:blobhero:1011785174767382568> Staticts', value=f'**¬ Members:** {ctx.guild.member_count}\n**¬ Roles:** {len(ctx.guild.roles)}\n**¬ Channels:** {len(ctx.guild.channels)} (**Text:** {len(ctx.guild.text_channels)}, **Voice:** {len(ctx.guild.voice_channels)}, **Other:** {len(ctx.guild.channels) - len(ctx.guild.text_channels) - len(ctx.guild.voice_channels)})', inline=False)
        await ctx.send(embed=emb)
    
    @commands.cooldown(1, 5, commands.BucketType.member)
    @server.command(name='role')
    @discord.app_commands.describe(role='The role to fetch')
    async def role(self, ctx: commands.Context, role: discord.Role):
        '''Get a role info'''
        await ctx.defer()
        emb = discord.Embed(colour=role.colour or 3447003)
        emb.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon)
        emb.description = f'**¬ Name:** {role.name}\n**¬ ID:** `{role.id}`\n**¬ Created:** <t:{round(role.created_at.timestamp())}:D>\n**¬ Hex:** {role.color}\n**¬ Position:** {role.position}'
        emb.set_thumbnail(url=role.display_icon)
        emb.set_footer(text=f'{ctx.author.name}#{ctx.author.discriminator}', icon_url=ctx.author.display_avatar)
        await ctx.send(embed=emb)
    
    @commands.cooldown(1, 5, commands.BucketType.member)
    @server.command(name='channel')
    @discord.app_commands.describe(channel='The channel to fetch')
    async def channel(self, ctx: commands.Context, channel: Optional[discord.abc.GuildChannel]):
        '''Get a channel info'''
        if not channel:
            channel = ctx.channel
        await ctx.defer()
        emb = discord.Embed(colour=3447003)
        emb.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon)
        emb.description = f'**¬ Name:** {channel.name}\n**¬ ID:** `{channel.id}`\n**¬ Category:** {channel.category.name if channel.category else "None"}\n**¬ Type:** {channel.type}\n**¬ Position:** {channel.position}\n**¬ Created:** <t:{round(channel.created_at.timestamp())}:D>'
        emb.set_footer(text=f'{ctx.author.name}#{ctx.author.discriminator}', icon_url=ctx.author.display_avatar)
        emb.set_thumbnail(url=ctx.guild.icon or self.bot.user.display_avatar)
        await ctx.send(embed=emb)
    
    @server.command(name='members')
    async def members(self, ctx: commands.Context):
        '''Get the member count of this server'''
        await ctx.send(f'***```py\n>>> {ctx.guild.member_count} members```***')
    
    @commands.cooldown(1, 4, commands.BucketType.member)
    @server.command(name='icon')
    async def icon(self, ctx: commands.Context):
        '''Get the server icon'''
        if not ctx.guild.icon:
            return await util.throw_error(ctx, text="This server **doesn't** have an icon yet", bold=False)
        await ctx.defer()
        embed = discord.Embed(colour=3447003)
        embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon.url)
        embed.set_image(url=ctx.guild.icon.url.replace('.webp', '.png'))
        await ctx.send(embed=embed)
    
    @commands.cooldown(1, 5, commands.BucketType.member)
    @commands.hybrid_command(name='calendar', aliases=['date'])
    async def _calendar(self, ctx: commands.Context):
        '''Get the current month calendar'''
        await ctx.defer()
        text = month(datetime.now().year, datetime.now().month)
        t = f':calendar: **{datetime.now().year} {datetime.now().strftime("%B")}**\n```{text}```'
        await ctx.send(t)
    
    @commands.cooldown(1, 8, commands.BucketType.member)
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

    @commands.cooldown(1, 8, commands.BucketType.member)
    @commands.hybrid_command(name='weather')
    @discord.app_commands.describe(city='The city to search')
    async def weather(self, ctx: commands.Context, *, city: str):
        '''Get some city weather'''
        v = await util.get(url="https://api.miduwu.ga/json/weather", params={"query": city}, as_dict=True)
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
    
    @commands.hybrid_group(name='emoji')
    async def emoji_group(self, ctx):
        '''Manage the server emojis'''
        ...
    
    @commands.cooldown(1, 5, commands.BucketType.member)
    @discord.app_commands.describe(emoji='The emoji representation, id or name')
    @emoji_group.command(name='image', aliases=['jumbo'])
    async def jumbo(self, ctx: commands.Context, emoji: str):
        '''Get a custom emoji image (big size)'''
        found = re.findall(r"<(a)?:([a-zA-Z\d_]{2,32}):(\d{18,22})>", emoji)
        found = found[0] if len(found) else None
        url, name = None, None
        if found:
            name = found[1]
            url = f'https://cdn.discordapp.com/emojis/{found[2]}.{"gif" if found[0] else "png"}'
        else:
            try_with_id = self.bot.get_emoji(int(emoji)) if emoji.isdigit() else None
            if try_with_id:
                name = try_with_id.name
                url = f'https://cdn.discordapp.com/emojis/{try_with_id.id}.{"gif" if try_with_id.animated else "png"}'
            else:
                try_with_name = next((e for e in list(ctx.guild.emojis) if emoji in e.name), None)
                if try_with_name:
                    name = try_with_name.name
                    url = f'https://cdn.discordapp.com/emojis/{try_with_name.id}.{"gif" if try_with_name.animated else "png"}'
        if not url and not name:
            return await util.throw_error(ctx, text="Invalid emoji provided, you can use the emoji representation, id or name")
        t = f'> **Name:** {name}\n> **Link:** {url.replace("webp", "png")}'
        await ctx.send(t)
    
    @commands.cooldown(1, 7, commands.BucketType.member)
    @commands.has_guild_permissions(manage_emojis_and_stickers=True)
    @commands.bot_has_guild_permissions(manage_emojis_and_stickers=True)
    @emoji_group.command(name='add')
    @discord.app_commands.describe(emoji='A custom emoji representation or a url', name='An optional name for the emoji')
    async def addemoji(self, ctx: commands.Context, emoji: str, name: str = None):
        '''Add a server emoji'''
        emojis = await ctx.guild.fetch_emojis()
        if(len(emojis) >= ctx.guild.emoji_limit):
            return await util.throw_error(ctx, text="This server can't get more emojis because it reached the limit")
        if name is None:
            name = 'unknown'
        if len(name) < 2:
            name = f'{name}_'
        try:
            found = re.findall(r"<(a)?:([a-zA-Z\d_]{2,32}):(\d{18,22})>", emoji)
            found = found[0] if len(found) else None
            if not found and not emoji.startswith('http'):
                return await util.throw_error(ctx, text="Invalid emoji provided")
            url = f'https://cdn.discordapp.com/emojis/{found[2]}.{"gif" if found[0] else "png"}' if found else emoji
            b = await util.get(url=url, extract='read')
            e = await ctx.guild.create_custom_emoji(name=name[:35], image=b)
            return await util.throw_fine(ctx, f"Successfully i've added {e} to the server")
        except:
            return await util.throw_error(ctx, text="I was unable to add that emoji")
    
    @commands.cooldown(1, 8, commands.BucketType.member)
    @commands.has_guild_permissions(manage_emojis_and_stickers=True)
    @commands.bot_has_guild_permissions(manage_emojis_and_stickers=True)
    @emoji_group.command(name='delete')
    @discord.app_commands.describe(emoji='The emoji representation or id')
    async def delemoji(self, ctx: commands.Context, emoji: str):
        '''Delete a emoji from the server'''
        if emoji.isdigit():
            if len(emoji) > 22 or len(emoji) < 18:
                return await util.throw_error(ctx, text="Invalid emoji ID provided, wtf is that")
            try:
                got = await ctx.guild.fetch_emoji(int(emoji))
            except:
                got = None
            if got is None:
                return await util.throw_error(ctx, text="Invalid emoji ID provided, i didn't find anything")
            try:
                await got.delete()
                await util.throw_fine(ctx, text="I deleted that emoji successfully!")
            except:
                return await util.throw_error(ctx, text="I was unable to delete that emoji")
        else:
            found = re.findall(r"<(a)?:([a-zA-Z\d_]{2,32}):(\d{18,22})>", emoji)
            found = found[0] if len(found) else None
            if not found:
                return await util.throw_error(ctx, text="Invalid emoji representation provided, maybe try with the ID (number)")
            try:
                got = await ctx.guild.fetch_emoji(int(found[2]))
            except:
                got = None
            if got is None:
                return await util.throw_error(ctx, text="Invalid emoji provided")
            try:
                await got.delete()
                await util.throw_fine(ctx, text="I deleted that emoji successfully!")
            except Exception as err:
                return await util.throw_error(ctx, text="I was unable to delete that emoji")
    
    @commands.cooldown(1, 7, commands.BucketType.member)
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
    
    @commands.cooldown(1, 45, commands.BucketType.member)
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
    
    @commands.cooldown(1, 7, commands.BucketType.member)
    @commands.hybrid_command(name='color', aliases=['hex'])
    @discord.app_commands.describe(hex='The color hex code')
    async def color(self, ctx: commands.Context, hex: str):
        '''Get a color information using its HEX code'''
        hex = re.sub('[^a-f\d]', '', hex, flags=re.IGNORECASE)
        if not util.is_hex(hex):
            return await util.throw_error(ctx, text='Invalid hex color code provided')
        r = await util.get(url=f'https://api.alexflipnote.dev/colour/{hex}')
        if not r:
            return await util.throw_error(ctx, text='I was unable to fetch that color')
        await ctx.defer()
        emb = discord.Embed(title=r['name'], color=r['int'])
        emb.set_author(name=f'{ctx.author.name}#{ctx.author.discriminator}', icon_url=ctx.author.display_avatar)
        emb.set_image(url=r['images']['square'])
        emb.add_field(name='HEX:', value=r['hex']['string'])
        emb.add_field(name='RGB:', value=r['rgb']['string'])
        emb.add_field(name='Int:', value=str(r['int']))
        emb.add_field(name='HSL:', value=r['hsl']['string'])
        emb.add_field(name='cmyk', value=r['cmyk']['string'])
        await ctx.send(embed=emb)
    
    @commands.hybrid_group(name='search')
    async def search(self, ctx):
        '''Search something from the internet, use the subcommands'''
        ...
    
    @commands.cooldown(1, 7, commands.BucketType.member)
    @search.command(name='definition')
    @discord.app_commands.describe(word='The term to define')
    async def definition(self, ctx: commands.Context, word: str):
        '''Define a term using the urban dictionary'''
        res = await util.get(url='https://api.urbandictionary.com/v0/define', params={"term": word})
        if not res or not _.has(res, 'list') or 0 >= len(res['list']):
            return await util.throw_error(ctx, text='I was unable to find that term')
        await ctx.defer()
        embed = discord.Embed(colour=3447003, title=res['list'][0]['word'])
        embed.description = res['list'][0]['definition']
        embed.set_author(name=f"{ctx.author.name}#{ctx.author.discriminator}", icon_url=ctx.author.display_avatar)
        embed.add_field(name='Example:', value=util.cut(res['list'][0]['example'], 1020))
        embed.set_footer(text=f'👍: {_.get(res, "list[0].thumbs_up") or 0} | 👎: {_.get(res, "list[0].thumbs_down") or 0} | Page: 1/{len(res["list"])}')
    
        v = Paginator(data=res['list'], ctx=ctx, embed=embed)
        def update(item):
            v.embed.clear_fields()
            v.embed.title = item["word"]
            v.embed.description = item["definition"]
            v.embed.add_field(name='Example:', value=util.cut(item["example"], 1020))
            v.embed.set_footer(text=f'👍: {_.get(item, "thumbs_up") or 0} | 👎: {_.get(item, "thumbs_down") or 0} | Page: {v.page + 1}/{len(_.get(res, "list"))}')
        v.message = await ctx.send(embed=embed, view=v)
        v.update_item = update
    
    @commands.cooldown(1, 7, commands.BucketType.member)
    @search.command(name='github')
    @discord.app_commands.describe(repo='The github repository name')
    async def repo(self, ctx: commands.Context, repo: str):
        '''Search for a github repository'''
        res = await util.get(url='https://api.github.com/search/repositories', params={"q": repo, "page": "1", "per_page": "10"})
        if not res or not _.get(res, 'items') or 0 >= len(res['items']):
            return await util.throw_error(ctx, text='I was unable to find some repository with that name')
        await ctx.defer()
        _year, _month, _day = re.findall('(\d+)-(\d+)-(\d+)', res["items"][0]["created_at"])[0]
        date = datetime(int(_year), int(_month), int(_day))
        embed = discord.Embed(colour=3447003, url=res['items'][0]['owner']['html_url'], title=res['items'][0]['name'])
        embed.description = util.cut(_.get(res['items'][0], 'description') or None, 2000)
        embed.set_author(name=res['items'][0]['owner']['login'], icon_url=_.get(res['items'][0], 'owner.avatar_url'), url=res['items'][0]['owner']['html_url'])
        embed.add_field(name='Information', value=f'**¬ Language:** {res["items"][0]["language"]}\n**¬ Visibility:** {res["items"][0]["visibility"].title()}\n**¬ Default branch:** `{res["items"][0]["default_branch"]}`\n**¬ Created:** <t:{round(date.timestamp())}:D>')
        embed.add_field(name='Staticts', value=f'**¬ Forks:** {res["items"][0]["forks_count"]}\n**¬ Stars:** {res["items"][0]["stargazers_count"]}\n**¬ Issues:** {res["items"][0]["open_issues_count"]}\n**¬ Watchers:** {res["items"][0]["watchers"]}')
        embed.set_footer(text=f'Page: 1/{len(_.get(res, "items"))}', icon_url=ctx.author.display_avatar)
        def update(item):
            _year, _month, _day = re.findall('(\d+)-(\d+)-(\d+)', item["created_at"])[0]
            date = datetime(int(_year), int(_month), int(_day))
            v.embed.clear_fields()
            v.embed.title = item["name"]
            v.embed.url = item["html_url"]
            v.embed.description = util.cut(_.get(item, 'description') or 'None.', 2000)
            v.embed.set_author(name=item['owner']['login'], icon_url=_.get(item, 'owner.avatar_url'), url=item['owner']['html_url'])
            v.embed.add_field(name='Information', value=f'**¬ Language:** {item["language"]}\n**¬ Visibility:** {item["visibility"].title()}\n**¬ Default branch:** `{item["default_branch"]}`\n**¬ Created:** <t:{round(date.timestamp())}:D>')
            v.embed.add_field(name='Staticts', value=f'**¬ Forks:** {item["forks_count"]}\n**¬ Stars:** {item["stargazers_count"]}\n**¬ Issues:** {item["open_issues_count"]}\n**¬ Watchers:** {item["watchers"]}')
            v.embed.set_footer(text=f'Page: {v.page + 1}/{len(_.get(res, "items"))}')

        v = Paginator(data=res['items'], ctx=ctx, embed=embed)
        v.message = await ctx.send(embed=embed, view=v)
        v.update_item = update
    
    @commands.cooldown(1, 8, commands.BucketType.member)
    @search.command(name='image')
    @discord.app_commands.describe(query='Something to search')
    async def bing(self, ctx: commands.Context, *, query: str):
        '''Search something in bing images'''
        res = await util.get(url=f"https://www.bing.com/images/async?q={query}&adlt=on", extract='read')
        if not res:
            return await util.throw_error(ctx, text='I was unable to find something related to that')
        links = re.findall("murl&quot;:&quot;(.*?)&quot;", res.decode("utf8"))
        if len(links) < 1:
            return await util.throw_error(ctx, text='I was unable to find something related to that')
        emb = discord.Embed(colour=3447003)
        emb.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar)
        emb.title = 'Search results'
        emb.set_image(url=links[0])
        emb.set_footer(text=f'Page: 1/{len(links)}', icon_url=self.bot.user.display_avatar)
        v = Paginator(data=links, ctx=ctx, embed=emb)
        def update(item):
            emb.set_image(url=item)
            emb.set_footer(text=f'Page: {v.page + 1}/{len(links)}', icon_url=self.bot.user.display_avatar)
        v.message = await ctx.send(embed=emb, view=v)
        v.update_item = update
    
    @commands.cooldown(1, 7, commands.BucketType.member)
    @search.command(name='python', aliases=['py'])
    @discord.app_commands.describe(query='Something to search')
    async def realpython(self, ctx: commands.Context, *, query: str):
        '''Search something in real python website'''
        res = await util.get(url='https://realpython.com/search/api/v1/', params={"q": query, "limit": 15})
        if not res or not _.get(res, 'results') or not len(res['results']):
            return await util.throw_error(ctx, text='I was unable to find some article related to that')
        await ctx.defer()
        articles = _.chunk(res["results"], 3)
        emb = discord.Embed(colour=3447003, title='Search results - Real Python', url=f'https://realpython.com/search?q={quote_plus(query)}', description='Here you go')
        emb.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar)
        emb.set_thumbnail(url='https://cdn.discordapp.com/attachments/852617860404609044/1054972118611279892/pythontocompress_1.png')
        emb.set_footer(text=f'Page: 1/{len(articles)}', icon_url=self.bot.user.display_avatar)
        for article in articles[0]:
            emb.add_field(name=util.cut(unescape(article["title"]), 225), value=f'https://realpython.com{article["url"]}', inline=False)
        
        v = Paginator(data=articles, ctx=ctx, embed=emb)
        def update(item):
            v.embed.clear_fields()
            v.embed.set_footer(text=f'Page: {v.page + 1}/{len(articles)}', icon_url=self.bot.user.display_avatar)
            for article in item:
                v.embed.add_field(name=util.cut(unescape(article["title"]), 225), value=f'https://realpython.com{article["url"]}', inline=False)
        v.update_item = update
        v.message = await ctx.send(embed=emb, view=v)
    
    @commands.cooldown(1, 7, commands.BucketType.member)
    @search.command(name='javascript', aliases=['js'])
    @discord.app_commands.describe(query='Something to search')
    async def mozilla(self, ctx: commands.Context, query: str, idiom: Literal['en-us', 'de', 'es', 'fr', 'ja', 'ko', 'pl', 'pt-br', 'ru', 'zh-cn', 'zh-tw'] = 'en-us'):
        '''Search something in mozilla'''
        res = await util.gett(url='https://developer.mozilla.org/api/v1/search', params={"q": query, "locale": idiom})
        if not res or not _.get(res, 'documents') or not len(res['documents']):
            return await util.throw_error(ctx, text='I was unable to find something related to that')
        await ctx.defer()
        docs = _.get(res, 'documents')
        emb = discord.Embed(colour=3447003, title=docs[0]['title'], url=f'https://developer.mozilla.org{docs[0]["mdn_url"]}')
        emb.set_thumbnail(url='https://cdn.discordapp.com/attachments/778296113123688498/958975232952127488/mozilla.png')
        emb.add_field(name='Locale:', value=docs[0]['locale'])
        emb.add_field(name='Score:', value=str(_.get(docs[0], 'score') or 0))
        emb.add_field(name='Summary:', value=docs[0]['summary'], inline=False)
        emb.set_footer(text=f'Page: 1/{len(docs)}', icon_url=self.bot.user.display_avatar)
        v = Paginator(data=docs, ctx=ctx, embed=emb)
        def update(item):
            v.embed.clear_fields()
            v.embed.set_footer(text=f'Page: {v.page + 1}/{len(docs)}', icon_url=self.bot.user.display_avatar)
            v.embed.add_field(name='Locale:', value=item['locale'])
            v.embed.add_field(name='Score:', value=str(_.get(item, 'score') or 0))
            v.embed.add_field(name='Summary:', value=item['summary'], inline=False)
        v.update_item = update
        v.message = await ctx.send(embed=emb, view=v)

async def setup(bot: commands.Bot):
    await bot.add_cog(Util(bot))