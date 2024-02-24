from datetime import datetime
from main import util, interpreter, mongodb as db, timeouts
from discord.ext import commands
from util.coreback import sync
from util.views import Ticket
import discord, re, sys

URL_REGEXP = "http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"

class Listeners(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, commands.MissingRequiredArgument):
            return await util.throw_error(ctx, text=f"Missing **{error.param.name}** parameter", bold=False, defer=False)
        elif isinstance(error, commands.UserNotFound):
            return await util.throw_error(ctx, text=f"Invalid user provided in **some** parameter", bold=False)
        elif isinstance(error, commands.MemberNotFound):
            return await util.throw_error(ctx, text=f"Invalid member provided in **some** parameter", bold=False)
        elif isinstance(error, commands.RoleNotFound):
            return await util.throw_error(ctx, text=f"Invalid role provided in **some** parameter", bold=False)
        elif isinstance(error, commands.ChannelNotFound):
            return await util.throw_error(ctx, text=f"Invalid channel provided in **some** parameter", bold=False)
        elif isinstance(error, commands.EmojiNotFound):
            return await util.throw_error(ctx, f"Invalid emoji provided in **some** parameter, make sure it is in this server", bold=False)
        elif isinstance(error, commands.BadLiteralArgument):
            return await util.throw_error(ctx, text=f"Invalid argument provided in **{error.param.name}**, please choice:\n{', '.join(list(map(lambda lit: f'**`{lit}`**', error.literals)))}", bold=False, defer=False)
        elif isinstance(error, commands.CommandOnCooldown):
            return await util.throw_error(ctx, text=f"You have to wait **{round(error.retry_after)}** seconds to use this command again", bold=False)
        elif isinstance(error, commands.NotOwner):
            return await util.throw_error(ctx, text=f"**{ctx.author.name}**, you **don't** own this bot", bold=False, ephemeral=True)
        elif isinstance(error, commands.MissingPermissions):
            return await util.throw_error(ctx, text=f"**{ctx.author.name}**, you **don't** have permissions enough to use this command", bold=False)
        elif isinstance(error, commands.BotMissingPermissions):
            return await util.throw_error(ctx, text=f"Sadly i can't execute that command, i need the following permissions:\n{', '.join(list(map(lambda s: f'**`{s}`**', error.missing_permissions)))}")
        elif isinstance(error, commands.BadArgument):
            return await util.throw_error(ctx, text=str(error) or "Invalid argument type provided")
        elif isinstance(error, commands.ChannelNotReadable):
            return await util.throw_error(ctx, text=f"I can't read messages in that channel, i don't have access to it")
        else:
            pass

    @commands.Cog.listener()
    async def on_ready(self):
        timeouts.bot = self.bot
        util.uptime = datetime.now()
        util.app_commands = await sync(self.bot.tree)
        print("\u001b[34;1m>> {:<10}\u001b[0m \u001b[31;1m{:<5}\u001b[0m \u001b[33;1m{:<5}\u001b[0m".format("Name:", "|", self.bot.user.name))
        print("\u001b[34;1m>> {:<10}\u001b[0m \u001b[31;1m{:<5}\u001b[0m \u001b[33;1m{:<5}\u001b[0m".format("Servers:", "|", len(self.bot.guilds)))
        print("\u001b[34;1m>> {:<10}\u001b[0m \u001b[31;1m{:<5}\u001b[0m \u001b[33;1m{:<5}\u001b[0m".format("Commands:", "|", len(util.app_commands)))
    
    @commands.Cog.listener()
    async def on_interaction(self, i: discord.Interaction):
        if i.type == discord.InteractionType.component:
            if i.data["custom_id"] == "dropdown":
                m = []
                for role in i.data["values"]:
                    try:
                        resolved = i.guild.get_role(int(role))
                        if not resolved:
                            all = await i.guild.fetch_roles()
                            resolved = next((x for x in all if x.id == int(role)), None)
                    except:
                        continue
                    if not resolved:
                        continue
                    try:
                        if resolved in i.user.roles:
                            m.append(f"I've removed the **{resolved.name}** role <:blobsip:1011458122239459440>")
                            await i.user.remove_roles(resolved)
                        else:
                            m.append(f"I've added **{resolved.name}** role <:blobsip:1011458122239459440>")
                            await i.user.add_roles(resolved)
                    except:
                        continue
                await i.response.send_message("\n".join(m), ephemeral=True)
            elif i.data["custom_id"] == "tickets":
                try:
                    await i.response.send_modal(Ticket(custom_id="modalticket"))
                except:
                    pass
        elif i.type == discord.InteractionType.modal_submit:
            if i.data["custom_id"] == "modalticket":
                data: dict | None = await db.get(table="guilds", id=i.guild.id, path="tickets")
                if not data or not data.get("enabled", None):
                    return await i.response.send_message("Oops! It seems that this server doesn't have the ticket system enabled! <:bloboutage:1011458109060952154>", ephemeral=True)
                try:
                    thread = await i.channel.create_thread(name=f"T - @{i.user.name}")
                    t = f"**Transcript:** </tickets transcript:{util.get_slash('tickets').id}>\n**Archive:** </tickets archive:{util.get_slash('tickets').id}>"
                    await thread.send(content=f"Hi {i.user.mention}, welcome to your private ticket! <:blobheart:1011458084239056977>\n\nPlease explain be patient to get **support**, anyways you can mention people **(@wumpus)** to invite them to this channel!\n\n{t}\n\n**Support role:** {data.get('role', 'No support role set.')}", allowed_mentions=discord.AllowedMentions(users=True, roles=True))
                    await i.response.send_message(content=f"Your ticket has been created in: {thread.mention} <:blobheart:1011458084239056977>", ephemeral=True)
                except:
                    await i.response.send_message(content="<:bloboutage:1011458109060952154> I was unable to open the ticket, try later or report this error to the bot support server!")
    
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        async def welcome(m: discord.Member):
            data: dict | None = await db.get(table="guilds", id=m.guild.id, path="welcome")
            if not data or not data.get("enabled", None):
                return
            try:
                channel = data.get("channel", None)
                if not channel:
                    return
                channel = m.guild.get_channel(int(channel)) or await m.guild.fetch_channel(int(channel))
                if not channel:
                    return
                message = data.get("message", None) or "Welcome @User.Mention to **@Server.Name**, now we are **@Server.Members** members!"
                d = await interpreter.read(message, author=m, guild=m.guild)
                final = re.sub("FUNC#\d+", "", d.code).strip()
                if not final and not d.embed:
                    return
                await channel.send(content=final if final else None, embed=d.embed)
            except:
                pass
        async def autorole(m: discord.Member):
            _roles_ = await db.get(table="guilds", id=m.guild.id, path="autoroles") or []
            if not len(_roles_):
                return
            try:
                for r in _roles_:
                    try:
                        role = m.guild.get_role(r)
                        if role:
                            await m.add_roles(role, reason="Tokyo Autoroles")
                    except:
                        pass
            except:
                pass

        await autorole(member)
        await welcome(member)
    
    @commands.Cog.listener()
    async def on_raw_member_remove(self, payload: discord.RawMemberRemoveEvent):
        try:
            guild = self.bot.get_guild(payload.guild_id) or await self.bot.fetch_guild(payload.guild_id)
        except:
            return
        if not payload.user:
            return
        async def leave(m: discord.Member | discord.User):
            data: dict | None = await db.get(table="guilds", id=guild.id, path="leave")
            if not data or not data.get("enabled", None):
                return
            try:
                channel = data.get("channel", None)
                if not channel:
                    return
                channel = m.guild.get_channel(int(channel)) or await m.guild.fetch_channel(int(channel))
                if not channel:
                    return
                message = data.get("message", None) or "Uh, oh! **@User.Name** has left us! \:("
                d = await interpreter.read(message, author=m, guild=guild)
                final = re.sub("FUNC#\d+", "", d.code).strip()
                if not final and not d.embed:
                    return
                await channel.send(content=final if final else None, embed=d.embed)
            except:
                pass
        await leave(payload.user)
    
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if str(payload.emoji) != "⭐" or not payload.guild_id:
            return
        m, c = None, None
        try:
            c = self.bot.get_channel(payload.channel_id) or await self.bot.fetch_channel(payload.channel_id)
            m = await c.fetch_message(payload.message_id)
            if not m:
                return
        except:
            return
        star_reaction = discord.utils.get(m.reactions, emoji="⭐")
        data: dict | None = await db.get(table="guilds", id=payload.guild_id, path="starboard")
        channel = self.bot.get_channel(data.get("channel")) or await self.bot.fetch_channel(data.get("channel")) if data.get("channel", None) else None
        if not data.get("enabled", None) or not channel or c.nsfw or data.get("stars", 2) > star_reaction.count:
            return
        try:
            fetched = [message async for message in channel.history(limit=100)]
            star_message = next((x for x in fetched if len(x.embeds) and x.embeds[0].footer and x.embeds[0].footer.text and x.embeds[0].footer.text.endswith(str(m.id)) and x.author.id == self.bot.user.id), None)
            if star_message:
                await star_message.edit(content=f"{load_star(star_reaction.count, data.get('stars', 2))} **{star_reaction.count}** <#{payload.channel_id}>")
            else:
                content = m.content[:4000] if m.content else ""
                image = m.attachments[0].url if m.attachments and len(m.attachments) and "image" in (m.attachments[0].content_type or "") else ""
                if not image:
                    urls = re.findall(URL_REGEXP, content, flags=re.MULTILINE)
                    image = urls[0] if urls and len(urls) and util.is_url(urls[0]) else ""
                if not image and not content:
                    return
                emb = discord.Embed(description=content or None, color=16776960)
                emb.set_author(name=f"@{m.author.name}", icon_url=m.author.display_avatar)
                emb.set_image(url=image)
                emb.set_footer(text=f"{self.bot.user.name} Starboard | {m.id}", icon_url=self.bot.user.display_avatar)
                v = discord.ui.View().add_item(discord.ui.Button(style=discord.ButtonStyle.link, label="Jump to message", url=m.jump_url))
                await channel.send(embed=emb, content=f"{load_star(star_reaction.count, data.get('stars', 2))} **{star_reaction.count}** <#{payload.channel_id}>", view=v)
        except:
            pass
    
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        if str(payload.emoji) != "⭐" or not payload.guild_id:
            return
        m, c = None, None
        try:
            c = self.bot.get_channel(payload.channel_id) or await self.bot.fetch_channel(payload.channel_id)
            m = await c.fetch_message(payload.message_id)
            if not m:
                return
        except:
            return
        star_reaction = discord.utils.get(m.reactions, emoji="⭐")
        data: dict | None = await db.get(table="guilds", id=payload.guild_id, path="starboard")
        channel = self.bot.get_channel(data.get("channel")) or await self.bot.fetch_channel(data.get("channel")) if data.get("channel", None) else None
        if not data.get("enabled", None) or not star_reaction or not channel or c.nsfw:
            return
        try:
            fetched = [message async for message in channel.history(limit=100)]
            star_message = next((x for x in fetched if len(x.embeds) and x.embeds[0].footer and x.embeds[0].footer.text and x.embeds[0].footer.text.endswith(str(m.id)) and x.author.id == self.bot.user.id), None)
            if not star_message:
                return
            # stars = int("".join(star_message.content.split(" ")[1].split("*")))
            if star_reaction.count < data.get("stars", 2):
                await star_message.delete()
            else:
                await star_message.edit(content=f"{load_star(star_reaction.count, data.get('stars', 2))} **{star_reaction.count}** <#{payload.channel_id}>")
        except:
            pass
    
    @commands.Cog.listener()
    async def on_raw_reaction_clear(self, payload: discord.RawReactionClearEvent):
        m, c = None, None
        try:
            c = self.bot.get_channel(payload.channel_id) or await self.bot.fetch_channel(payload.channel_id)
            m = await c.fetch_message(payload.message_id)
            if not m:
                return
        except:
            return
        data: dict | None = await db.get(table="guilds", id=payload.guild_id, path="starboard")
        channel = self.bot.get_channel(data.get("channel")) or await self.bot.fetch_channel(data.get("channel")) if data.get("channel", None) else None
        if not data.get("enabled", None) or not channel:
            return
        try:
            fetched = [message async for message in channel.history(limit=100)]
            star_message = next((x for x in fetched if len(x.embeds) and x.embeds[0].footer and x.embeds[0].footer.text and x.embeds[0].footer.text.endswith(str(m.id)) and x.author.id == self.bot.user.id), None)
            if not star_message:
                return
            await star_message.delete()
        except:
            pass
    
    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        channel = self.bot.get_channel(812549187388178486) or await self.bot.fetch_channel(812549187388178486)
        t = f"**New server!** <:photoblob:1011458149653426226>\n\n> **Name:** {guild.name}\n> **Members:** {guild.member_count}\n> **Owner:** {f'{guild.owner.name}' if guild.owner else 'Unknown'}\n\nNow i am in **{len(self.bot.guilds)}** servers!"
        await channel.send(t)
    
    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        channel = self.bot.get_channel(812549187388178486) or await self.bot.fetch_channel(812549187388178486)
        t = f"**I left a server!** <:blobthump:1011458144947408958>\n\n> **Name:** {guild.name}\n> **Members:** {guild.member_count}\n> **Owner:** {f'{guild.owner.name}' if guild.owner else 'Unknown'}\n\nNow i am in **{len(self.bot.guilds)}** servers!"
        await channel.send(t)
    
    @commands.Cog.listener()
    async def on_error(self, event, *args, **kwargs):
        error_channel_id = 812549187388178486
        error_channel = self.bot.get_channel(error_channel_id)
        error_type, error, traceback = sys.exc_info()
        error_message = f"Error in **{event}**:\n{error_type.__name__} - {error}"
        await error_channel.send(error_message)

def load_star(stars: int, total: int) -> str:
    final = '⭐'
    if stars >= total + 5:
        final = '🌟'
    if stars >= total + 9:
        final = '💫'
    if stars >= total + 13:
        final = '✨'
    return final

async def setup(bot: commands.Bot):
    await bot.add_cog(Listeners(bot))