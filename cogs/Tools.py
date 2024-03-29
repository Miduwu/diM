import discord
from main import util, mongodb, interpreter
from discord.ext import commands
import pydash as _
from util.views import Paginator, Confirmation, Base, Settings
from difflib import get_close_matches
from typing_extensions import Annotated
import re
import io

class TagName(commands.clean_content):
    def __init__(self, *, lower: bool = False):
        self.lower: bool = lower
        super().__init__()

    async def convert(self, ctx: commands.Context, argument: str) -> str:
        converted = await super().convert(ctx, argument)
        lower = converted.lower().strip()

        if not lower:
            return await util.throw_error(ctx, text="Missing tag name")

        if len(lower) > 100:
            return await util.throw_error(ctx, text="Tag name length is too long")

        first_word, _, _ = lower.partition(' ')

        # get tag command.
        root: commands.GroupMixin = ctx.bot.get_command('tag')  # type: ignore
        if first_word in root.all_commands:
            return await util.throw_error(ctx, text="This tag name starts with a reserved word")

        return converted.strip() if not self.lower else lower

class Tools(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
    
    @commands.cooldown(1, 120, commands.BucketType.member)
    @commands.hybrid_command(name="prefix")
    @commands.has_permissions(manage_guild=True)
    @discord.app_commands.describe(new_prefix="The new prefix to set")
    async def prefix(self, ctx: commands.Context, new_prefix: str):
        """Set the server prefix"""
        if not new_prefix:
            return await util.throw_error(ctx, text="Missing new prefix argument.")
        await ctx.defer()
        await mongodb.set(table="guilds", id=ctx.guild.id, path="prefix", value=new_prefix)
        await util.throw_fine(ctx, text=f"**Prefix channged to: `{new_prefix}` successfully!**", bold=False)
    
    @commands.cooldown(1, 5, commands.BucketType.member)
    @commands.hybrid_command("test", aliases=["interprete"])
    @discord.app_commands.describe(text="The content to test")
    async def interprete(self, ctx: commands.Context, *, text: str):
        """Interprete some text (used for some Tools)"""
        d = await interpreter.read(text[:2000], author=ctx.author, guild=ctx.guild)
        final = re.sub("FUNC#\d+", "", d.code).strip()
        if not d.embed and not final:
            return await util.throw_error(ctx, text="Invalid text provided, it doesn't return anything")
        await ctx.send(content=final if final else None, embed=d.embed)
    
    @commands.cooldown(1, 4, commands.BucketType.member)
    @commands.hybrid_group(name="tag", fallback="view", aliases=["t"])
    @discord.app_commands.describe(tag="The tag to view")
    async def tags(self, ctx: commands.Context, *, tag: str):
        """Manage the server tags, or view one"""
        await ctx.defer()
        _tags_ = await mongodb.get(table="guilds", id=ctx.guild.id, path="tags.list") or []
        found = next((item for item in _tags_ if item["name"].lower() == tag.lower()), None)
        if not found:
            return await util.throw_error(ctx, text="That tag doesn't exist")
        d = await interpreter.read(found["content"], author=ctx.author, guild=ctx.guild)
        final = re.sub("FUNC#\d+", "", d.code).strip()
        await ctx.send(content=final if final or d.embed else "No content, lmao i know this is crazy, please modify this tag", embed=d.embed)
    
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 25, commands.BucketType.member)
    @tags.command(name="add")
    @discord.app_commands.describe(name="The tag name", content="The tag content")
    async def tag_add(self, ctx: commands.Context, name: Annotated[str, TagName], *, content: str):
        """Add a server tag"""
        await ctx.defer()
        _tags_ = await mongodb.get(table="guilds", id=ctx.guild.id, path="tags.list") or []
        if len(_tags_) >= 50:
            return await util.throw_error(ctx, text="This server has reached the tags limit")
        if len(name) >= 100:
            return await util.throw_error(ctx, text="The tag name can't exceed 100 letters")
        if next((item for item in _tags_ if item["name"].lower() == name.lower()), None):
            return await util.throw_error(ctx, text=f"That tag already exists")
        _tags_.append({ "name": name.lower(), "content": content[:1950], "author": ctx.author.id })
        await mongodb.set(table="guilds", id=ctx.guild.id, path="tags.list", value=_tags_)
        await util.throw_fine(ctx, text=f"**{name}** was added successfully!", bold=False)
    
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 15, commands.BucketType.member)
    @tags.command(name="modify")
    @discord.app_commands.describe(tag="The tag name to modify", content="The new tag contet")
    async def tag_modify(self, ctx: commands.Context, tag: Annotated[str, TagName(lower=True)], *, content: str):
        """Edit a server tag"""
        await ctx.defer()
        _tags_ = await mongodb.get(table="guilds", id=ctx.guild.id, path="tags.list") or []
        found = next((item for item in _tags_ if item["name"].lower() == tag.lower()), None)
        if not found:
            return await util.throw_error(ctx, text="That tag doesn't exist")
        index = _tags_.index(found)
        found["content"] = content[:1950]
        _tags_[index] = found
        await mongodb.set(table="guilds", id=ctx.guild.id, path="tags.list", value=_tags_)
        await util.throw_fine(ctx, text=f"**{tag}** was modified successfully!", bold=False)
    
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 9, commands.BucketType.member)
    @tags.command(name="delete")
    @discord.app_commands.describe(tag="The tag to delete")
    async def tag_delete(self, ctx: commands.Context, *, tag: str):
        """Delete a server tag"""
        await ctx.defer()
        _tags_ = await mongodb.get(table="guilds", id=ctx.guild.id, path="tags.list") or []
        if not next((item for item in _tags_ if item["name"].lower() == tag.lower()), None):
            return await util.throw_error(ctx, text="That tag doesn't exist")
        await mongodb.set(table="guilds", id=ctx.guild.id, path="tags.list", value=[cmd for cmd in _tags_ if not (cmd["name"].lower() == tag.lower())])
        await util.throw_fine(ctx, text=f"**{tag}** was deleted successfully!", bold=False)
    
    @commands.cooldown(1, 5, commands.BucketType.member)
    @tags.command(name="raw", aliases=["source"])
    @discord.app_commands.describe(tag="The tag to get the source")
    async def tag_raw(self, ctx: commands.Context, *, tag: str):
        """Get a tag contet source"""
        await ctx.defer()
        _tags_ = await mongodb.get(table="guilds", id=ctx.guild.id, path="tags.list") or []
        found = next((item for item in _tags_ if item["name"].lower() == tag.lower()), None)
        if not found:
            return await util.throw_error(ctx, text="That tag doesn't exist")
        button = discord.ui.Button(style=discord.ButtonStyle.blurple, label="Show file", emoji="📝")
        async def call(i: discord.Interaction):
            await i.response.send_message(file=discord.File(io.StringIO(found["content"][:1950]), f"{found['name']}.txt"), ephemeral=True)
        button.callback = call
        v = Base(ctx=ctx).add_item(button)
        emb = discord.Embed(title=f'"{found["name"]}" source', description=f'```txt\n{found["content"][:1950]}```', colour=3447003)
        emb.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar)
        v.message = await ctx.send(embed=emb, view=v)
    
    @commands.cooldown(1, 7, commands.BucketType.member)
    @tags.command(name="search")
    @discord.app_commands.describe(tag="Query to search in server tags")
    async def tag_search(self, ctx: commands.Context, *, tag: str):
        """Search something in the server tags"""
        await ctx.defer()
        _tags_ = await mongodb.get(table="guilds", id=ctx.guild.id, path="tags.list") or []
        _names_ = list(map(lambda x: x["name"], _tags_))
        if not len(_tags_):
            return await util.throw_error(ctx, text="This server doesn't have tags yet")
        query = tag[:150]
        similar = get_close_matches(query.lower(), _names_)
        if not len(similar):
            return await util.throw_error(ctx, text="I didn't find anything related to that")
        _resolved_ = list(map(lambda x: next((t for t in _tags_ if t["name"] == x), None), similar))
        func = lambda arr: "\n".join(list(map(lambda obj: f"{_.flatten_deep(_resolved_).index(obj) + 1} :: **`{obj['name']}`** [Author: {self.bot.get_user(obj['author']).name if self.bot.get_user(obj['author']) else 'Unknown'}]", arr)))
        _chunk_ = _.chunk(_resolved_, 10)
        emb = discord.Embed(colour=3447003, title=f"Similar to: {query}")
        emb.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar)
        emb.description = func(_chunk_[0])
        v = Paginator(data=_chunk_, ctx=ctx, embed=emb)
        def update(item):
            v.content = f"**[Page: {v.page + 1}/{len(_chunk_)}]**"
            v.embed.description = func(item)
        v.update_item = update
        v.message = await ctx.send(content=f"**[Page: {v.page + 1}/{len(_chunk_)}]**", view=v, embed=emb)
    
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 180, commands.BucketType.member)
    @tags.command(name="purge", aliases=["reset"])
    async def tag_purge(self, ctx: commands.Context):
        """Purge all the server tags"""
        await ctx.defer()
        v = Confirmation(ctx=ctx)
        v.message = await ctx.send("Are you sure to delete **EVERY** tag in this server?", view=v)
        async def f(i: discord.Interaction):
            await i.response.defer()
            await mongodb.delete(table="guilds", id=ctx.guild.id, path="tags.list")
            await util.throw_fine(ctx, text="Every tag in this server was deleted!")
        v.call_me = f
    
    @commands.cooldown(1, 7, commands.BucketType.member)
    @tags.command(name="list")
    async def tag_list(self, ctx: commands.Context):
        """View the server tags"""
        await ctx.defer()
        _tags_ = _.chunk(await mongodb.get(table="guilds", id=ctx.guild.id, path="tags.list") or [], 10)
        if not len(_tags_):
            return await util.throw_error(ctx, text="This server doesn't have tags yet")
        func = lambda arr: "\n".join(list(map(lambda obj: f"{_.flatten_deep(_tags_).index(obj) + 1} :: **`{obj['name']}`** [Author: {self.bot.get_user(obj['author']).name if self.bot.get_user(obj['author']) else 'Unknown'}]", arr)))
        emb = discord.Embed(colour=3447003)
        emb.description = func(_tags_[0])
        emb.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar)
        v = Paginator(data=_tags_, ctx=ctx, embed=emb)
        def update(item):
            v.content = f"**[Page: {v.page + 1}/{len(_tags_)}]**"
            v.embed.description = func(item)
        v.update_item = update
        v.message = await ctx.send(content=f"**[Page: {v.page + 1}/{len(_tags_)}]**", view=v, embed=emb)
    
    @tags.autocomplete(name="tag")
    async def tag_autocomplete(self, interaction: discord.Interaction, current: str):
        _tags_ = await mongodb.get(table="guilds", id=interaction.guild.id, path="tags.list") or []
        return [
            discord.app_commands.Choice(name=item["name"], value=item["name"]) for item in _tags_ if current.lower() in item["name"].lower()
        ][:25]
    
    @tag_raw.autocomplete(name="tag")
    async def tag_autocomplete_raw(self, interaction: discord.Interaction, current: str):
        _tags_ = await mongodb.get(table="guilds", id=interaction.guild.id, path="tags.list") or []
        return [
            discord.app_commands.Choice(name=item["name"], value=item["name"]) for item in _tags_ if current.lower() in item["name"].lower()
        ][:25]
    
    @commands.hybrid_group(name="dropdown", aliases=["menuroles"])
    async def dropdown(self, ctx):
        """Manage the dropdown roles"""
        ...
    
    @commands.cooldown(1, 60, commands.BucketType.guild)
    @commands.has_guild_permissions(manage_roles=True)
    @commands.bot_has_permissions(embed_links=True)
    @dropdown.command(name="create", aliases=["new"])
    @discord.app_commands.describe(channel="The channel to send the void dropdown", description="The description for this dropdown")
    async def dropdown_create(self, ctx: commands.Context, channel: discord.TextChannel, *, description: str):
        """Create a new dropdown menu in this server"""
        emb = discord.Embed(colour=3447003, title="Dropdown roles")
        emb.description = description[:2000]
        emb.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon)
        emb.set_footer(text=self.bot.user.name, icon_url=self.bot.user.display_avatar)
        if not channel.permissions_for(ctx.guild.me).send_messages:
            return await util.throw_error(ctx, text="I can't send messages in that channel")
        message = await channel.send(embed=emb)
        await util.throw_fine(ctx, text=f"**The dropdown was sent! Now you can use the next to add the first role:**\n```/dropdown add {message.jump_url} @MyRole``` Good luck!", defer=False, bold=False, ephemeral=True)
    
    @commands.cooldown(1, 5, commands.BucketType.guild)
    @commands.has_guild_permissions(manage_roles=True)
    @dropdown.command(name="add")
    @discord.app_commands.describe(url="The existing dropdown message URL", role="The role to add to that dropdown", emoji="A custom or default emoji for this role")
    async def dropdown_add(self, ctx: commands.Context, url: str, role: discord.Role, emoji: str = None):
        """Add a role to a dropdown"""
        links = re.findall("channels\/[\d]+\/[\d]+\/[\d]+", url)
        if not links:
            return await util.throw_error(ctx, text="Invalid message URL provided in first parameter")
        if role.position >= ctx.guild.me.top_role.position:
            return await util.throw_error(ctx, text="That role is higher or equal than mine")
        if role.position >= ctx.author.top_role.position:
            return await util.throw_error(ctx, text="That role is higher or equal than yours")
        emoji = util.parse_emoji(emoji) if emoji else "role:846171090484461579"
        if not emoji:
            return await util.throw_error(ctx, text="That is not a valid emoji")
        g, c, m = links[0].split("/")[1:]
        if int(g) != ctx.guild.id:
            return await util.throw_error(ctx, text="That message is not in this server")
        try:
            channel = self.bot.get_channel(int(c)) or await self.bot.fetch_channel(int(c))
            if not util.is_text(channel):
                return await util.throw_error(ctx, text="Invalid channel type")
        except:
            return await util.throw_error(ctx, text="I was unable to find that channel")
        try:
            message = await channel.fetch_message(m)
        except:
            return await util.throw_error(ctx, text="I was unable to find that message")
        view = discord.ui.View().from_message(message)
        child: discord.ui.Select | None = view.children[0] if len(view.children) else None
        if child and _.some(child.options, lambda o: str(o.value) == str(role.id)):
            return await util.throw_error(ctx, text="That role is already in the dropdown")
        if child:
            if len(child.options) >= 20:
                return await util.throw_error(ctx, text="This server has reached the role limit in a dropdown")
            child.add_option(label=role.name, value=role.id, description="Get this role", emoji=emoji)
            child.max_values = len(child.options)
            view.children[0] = child
            view.children[0].custom_id = "dropdown"
            await message.edit(view=view)
            await util.throw_fine(ctx, text="Your changes has been saved successfully!")
        else:
            view.add_item(discord.ui.Select(custom_id="dropdown", placeholder="Select your roles", options=[discord.SelectOption(label=role.name, value=role.id, description="Get this role", emoji=emoji)]))
            view.children[0].custom_id = "dropdown"
            await message.edit(view=view)
            await util.throw_fine(ctx, text="Your changes has been saved successfully!")
    
    @commands.cooldown(1, 5, commands.BucketType.guild)
    @commands.has_guild_permissions(manage_roles=True)
    @dropdown.command(name="remove")
    @discord.app_commands.describe(url="The existing dropdown message URL", role="The role from the dropdown to remove")
    async def dropdown_remove(self, ctx: commands.Context, url: str, role: discord.Role):
        """Remove a role from a dropdown"""
        links = re.findall("channels\/[\d]+\/[\d]+\/[\d]+", url)
        if not links:
            return await util.throw_error(ctx, text="Invalid message URL provided in first parameter")
        g, c, m = links[0].split("/")[1:]
        if int(g) != ctx.guild.id:
            return await util.throw_error(ctx, text="That message is not in this server")
        try:
            channel = self.bot.get_channel(int(c)) or await self.bot.fetch_channel(int(c))
            if not util.is_text(channel):
                return await util.throw_error(ctx, text="Invalid channel type")
        except:
            return await util.throw_error(ctx, text="I was unable to find that channel")
        try:
            message = await channel.fetch_message(m)
        except:
            return await util.throw_error(ctx, text="I was unable to find that message")
        if message.author.id != self.bot.user.id and not len(message.embeds) and message.embeds[0].title != "Dropdown roles":
            return await util.throw_error(ctx, text="The provided message is not a dropdown sent by me, create one using: **`/dropdown create`**")
        view = discord.ui.View().from_message(message)
        child: discord.ui.Select | None = view.children[0] if len(view.children) else None
        if not child or not len(child.options):
            return await util.throw_error(ctx, text="The dropdown doesn't have roles yet")
        if not _.some(child.options, lambda o: str(o.value) == str(role.id)):
            return await util.throw_error(ctx, text="That dropdown doesn't have that role")
        child.options = list(filter(lambda o: str(o.value) != str(role.id), child.options))
        child.max_values = len(child.options)
        view.children[0] = child
        view.children[0].custom_id = "dropdown"
        await message.edit(view=view if len(child.options) else None)
        await util.throw_fine(ctx, text="Your changes has been saved successfully!")
    
    @commands.cooldown(1, 5, commands.BucketType.guild)
    @commands.has_guild_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_messages=True)
    @dropdown.command(name="delete")
    @discord.app_commands.describe(url="The existing dropdown message URL")
    async def dropdown_delete(self, ctx: commands.Context, url: str):
        """Delete a dropdown"""
        links = re.findall("channels\/[\d]+\/[\d]+\/[\d]+", url)
        if not links:
            return await util.throw_error(ctx, text="Invalid message URL provided in first parameter")
        g, c, m = links[0].split("/")[1:]
        if int(g) != ctx.guild.id:
            return await util.throw_error(ctx, text="That message is not in this server")
        try:
            channel = self.bot.get_channel(int(c)) or await self.bot.fetch_channel(int(c))
            if not util.is_text(channel):
                return await util.throw_error(ctx, text="Invalid channel type")
        except:
            return await util.throw_error(ctx, text="I was unable to find that channel")
        try:
            message = await channel.fetch_message(m)
        except:
            return await util.throw_error(ctx, text="I was unable to find that message")
        if message.author.id != self.bot.user.id and not len(message.embeds) and message.embeds[0].title != "Dropdown roles":
            return await util.throw_error(ctx, text="The provided message is not a dropdown sent by me, create one using: **`/dropdown create`**")
        await message.delete()
        await util.throw_fine(ctx, text="Your changes has been saved successfully!")
    
    @commands.cooldown(1, 5, commands.BucketType.guild)
    @commands.has_guild_permissions(manage_roles=True)
    @dropdown.command(name="modify")
    @discord.app_commands.describe(url="The existing dropdown message URL", description = "A new description for this dropdown")
    async def dropdown_modify(self, ctx: commands.Context, url: str, *, description: str):
        """Modify a dropdown description"""
        links = re.findall("channels\/[\d]+\/[\d]+\/[\d]+", url)
        if not links:
            return await util.throw_error(ctx, text="Invalid message URL provided in first parameter")
        g, c, m = links[0].split("/")[1:]
        if int(g) != ctx.guild.id:
            return await util.throw_error(ctx, text="That message is not in this server")
        try:
            channel = self.bot.get_channel(int(c)) or await self.bot.fetch_channel(int(c))
            if not util.is_text(channel):
                return await util.throw_error(ctx, text="Invalid channel type")
        except:
            return await util.throw_error(ctx, text="I was unable to find that channel")
        try:
            message = await channel.fetch_message(m)
        except:
            return await util.throw_error(ctx, text="I was unable to find that message")
        if message.author.id != self.bot.user.id and not len(message.embeds) and message.embeds[0].title != "Dropdown roles":
            return await util.throw_error(ctx, text="The provided message is not a dropdown sent by me, create one using: **`/dropdown create`**")
        message.embeds[0].description = description[:2000]
        await message.edit(embed=message.embeds[0])
        await util.throw_fine(ctx, text="Your changes has been saved successfully!")

    @commands.cooldown(1, 5, commands.BucketType.guild)
    @commands.has_guild_permissions(manage_roles=True)
    @dropdown.command(name="singlerole")
    @discord.app_commands.describe(url="The existing dropdown message URL")
    async def dropdown_singlerole(self, ctx: commands.Context, url: str):
        """Set a dropdown message as a singlerole system"""
        links = re.findall("channels\/[\d]+\/[\d]+\/[\d]+", url)
        if not links:
            return await util.throw_error(ctx, text="Invalid message URL provided in first parameter")
        g, c, m = links[0].split("/")[1:]
        if int(g) != ctx.guild.id:
            return await util.throw_error(ctx, text="That message is not in this server")
        try:
            channel = self.bot.get_channel(int(c)) or await self.bot.fetch_channel(int(c))
            if not util.is_text(channel):
                return await util.throw_error(ctx, text="Invalid channel type")
        except:
            return await util.throw_error(ctx, text="I was unable to find that channel")
        try:
            message = await channel.fetch_message(m)
        except:
            return await util.throw_error(ctx, text="I was unable to find that message")
        if message.author.id != self.bot.user.id and not len(message.embeds) and message.embeds[0].title != "Dropdown roles":
            return await util.throw_error(ctx, text="The provided message is not a dropdown sent by me, create one using: **`/dropdown create`**")
        view = discord.ui.View().from_message(message)
        child: discord.ui.Select | None = view.children[0] if len(view.children) else None
        if not child or not len(child.options):
            return await util.throw_error(ctx, text="The dropdown doesn't have roles yet")
        child.max_values = 1
        view.children[0] = child
        view.children[0].custom_id = "dropdown"
        await message.edit(view=view if len(child.options) else None)
        await util.throw_fine(ctx, text="Your changes has been saved successfully!")
    
    @commands.cooldown(1, 30, commands.BucketType.guild)
    @commands.has_guild_permissions(manage_guild=True)
    @commands.hybrid_command(name="settings")
    async def settings(self, ctx: commands.Context):
        """Manage the settings in this server"""
        emb = discord.Embed(colour=3447003, title="Settings", description=f"Thanks for using **{ctx.bot.user.name}** tools! You can see a system by using the select menu below this.")
        emb.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar)
        emb.set_footer(text=f"{self.bot.user.name} settings", icon_url=self.bot.user.display_avatar)
        emb.set_thumbnail(url=self.bot.user.display_avatar)
        try:
            v = Settings(ctx=ctx, embed=emb, timeout=30)
            v.message = await ctx.send(embed=emb, view=v)
        except:
            pass
    
    @commands.hybrid_group(name="welcome")
    async def welcome(self, ctx):
        """Manage the welcome setting in this server"""
        ...

    @commands.cooldown(1, 15, commands.BucketType.guild)
    @commands.has_guild_permissions(manage_guild=True)
    @welcome.command(name="channel")
    @discord.app_commands.describe(channel="The text channel for the welcome message")
    async def welcome_channel(self, ctx: commands.Context, channel: discord.TextChannel):
        """Set the welcome channel"""
        if not channel.permissions_for(ctx.guild.me).send_messages:
            return await util.throw_error(ctx, text="I can't send messages in that channel")
        await mongodb.set(table="guilds", id=ctx.guild.id, path="welcome.channel", value=channel.id)
        await mongodb.set(table="guilds", id=ctx.guild.id, path="welcome.enabled", value=True)
        await util.throw_fine(ctx, text=f"I've set {channel.mention} as the welcome channel")
    
    @commands.cooldown(1, 15, commands.BucketType.guild)
    @commands.has_guild_permissions(manage_guild=True)
    @welcome.command(name="message")
    @discord.app_commands.describe(message="The welcome message")
    async def welcome_message(self, ctx: commands.Context, *, message: str):
        """Set the welcome message"""
        if 5 > len(message):
            return await util.throw_error(ctx, text="Your message is too short (-5)")
        if len(message) > 1900:
            return await util.throw_error(ctx, text="Your message is too long (+1900)")
        await mongodb.set(table="guilds", id=ctx.guild.id, path="welcome.message", value=message)
        await mongodb.set(table="guilds", id=ctx.guild.id, path="welcome.enabled", value=True)
        await util.throw_fine(ctx, text=f"I've set the welcome message sucessfully!")
    
    @commands.cooldown(1, 15, commands.BucketType.member)
    @commands.has_guild_permissions(manage_guild=True)
    @welcome.command(name="preview", aliases=["example"])
    async def welcome_preview(self, ctx: commands.Context):
        """See the welcome message preview"""
        data: dict | None = await mongodb.get(table="guilds", id=ctx.guild.id)
        if not data or not data.get("welcome", {}).get("enabled", None):
            return await util.throw_error(ctx, text="This server doesn't have the welcome system enabled, enable it using: `/settings`")
        if not data.get("welcome", {}).get("channel", None):
            return await util.throw_error(ctx, text="This server doesn't have a welcome channel, set it using `/welcome channel`")
        m = data.get("welcome", {}).get("message", None) or "Welcome @User.Mention to **@Server.Name**, now we are **@Server.Members** members!"
        d = await interpreter.read(m, author=ctx.author, guild=ctx.guild)
        final = re.sub("FUNC#\d+", "", d.code).strip()
        if not final and not d.embed:
            return await util.throw_error(ctx, text="This server doesn't have a valid message, re-set it using `/welcome message`")
        await ctx.send(content=final if final else None, embed=d.embed) 
    
    @commands.hybrid_group(name="leave", aliases=["goodbye"])
    async def leave(self, ctx):
        """Manage the leave setting in this server"""
        ...
    
    @commands.cooldown(1, 15, commands.BucketType.guild)
    @commands.has_guild_permissions(manage_guild=True)
    @leave.command(name="channel")
    @discord.app_commands.describe(channel="The text channel for the leave message")
    async def leave_channel(self, ctx: commands.Context, channel: discord.TextChannel):
        """Set the leave channel"""
        if not channel.permissions_for(ctx.guild.me).send_messages:
            return await util.throw_error(ctx, text="I can't send messages in that channel")
        await mongodb.set(table="guilds", id=ctx.guild.id, path="leave.channel", value=channel.id)
        await mongodb.set(table="guilds", id=ctx.guild.id, path="leave.enabled", value=True)
        await util.throw_fine(ctx, text=f"I've set {channel.mention} as the leave channel")
    
    @commands.cooldown(1, 15, commands.BucketType.guild)
    @commands.has_guild_permissions(manage_guild=True)
    @leave.command(name="message")
    @discord.app_commands.describe(message="The welcome message")
    async def leave_message(self, ctx: commands.Context, *, message: str):
        """Set the leave message"""
        if 5 > len(message):
            return await util.throw_error(ctx, text="Your message is too short (-5)")
        if len(message) > 1900:
            return await util.throw_error(ctx, text="Your message is too long (+1900)")
        await mongodb.set(table="guilds", id=ctx.guild.id, path="leave.message", value=message)
        await mongodb.set(table="guilds", id=ctx.guild.id, path="leave.enabled", value=True)
        await util.throw_fine(ctx, text=f"I've set the leave message sucessfully!")
    
    @commands.cooldown(1, 15, commands.BucketType.member)
    @commands.has_guild_permissions(manage_guild=True)
    @leave.command(name="preview", aliases=["example"])
    async def leave_preview(self, ctx: commands.Context):
        """See the leave message preview"""
        data: dict | None = await mongodb.get(table="guilds", id=ctx.guild.id)
        if not data or not data.get("leave", {}).get("enabled", None):
            return await util.throw_error(ctx, text="This server doesn't have the leave system enabled, enable it using: `/settings`")
        if not data.get("leave", {}).get("channel", None):
            return await util.throw_error(ctx, text="This server doesn't have a leave channel, set it using `/leave channel`")
        m = data.get("leave", {}).get("message", None) or "Uh, oh! **@User.Name** has left us! \:("
        d = await interpreter.read(m, author=ctx.author, guild=ctx.guild)
        final = re.sub("FUNC#\d+", "", d.code).strip()
        if not final and not d.embed:
            return await util.throw_error(ctx, text="This server doesn't have a valid message, re-set it using `/leave message`")
        await ctx.send(content=final if final else None, embed=d.embed)
    
    @commands.hybrid_group(name="tickets", aliases=["ticket"])
    async def tickets(self, ctx):
        """Manage the server tickets"""
        ...
    
    @commands.cooldown(1, 15, commands.BucketType.guild)
    @commands.has_guild_permissions(manage_guild=True)
    @tickets.command(name="channel")
    @discord.app_commands.describe(channel="The tickets channel where a message will be sent")
    async def tickets_channel(self, ctx: commands.Context, channel: discord.TextChannel):
        """Set the tickets channel"""
        if not channel.permissions_for(ctx.guild.me).send_messages or not channel.permissions_for(ctx.guild.me).embed_links:
            return await util.throw_error(ctx, text="I can't send messages/embeds in that channel")
        emb = discord.Embed(colour=3447003, title="Tickets", description="To open a ticket, press the button below!")
        emb.set_thumbnail(url=ctx.guild.icon or self.bot.user.display_avatar)
        emb.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon)
        emb.set_footer(text=f"{self.bot.user.name}'s Ticket System", icon_url=self.bot.user.display_avatar)
        emb.set_image(url="https://cdn.discordapp.com/attachments/1067294291992510575/1073427368246517820/IMG_20230209_201659.png")
        v = discord.ui.View().add_item(discord.ui.Button(label="Open", emoji="📩", style=discord.ButtonStyle.blurple, custom_id="tickets"))
        await channel.send(embed=emb, view=v)
        await mongodb.set(table="guilds", id=ctx.guild.id, path="tickets.enabled", value=True)
        await util.throw_fine(ctx, text=f"I've set {channel.mention} as the tickets channel")
    
    @commands.cooldown(1, 15, commands.BucketType.guild)
    @commands.has_guild_permissions(manage_guild=True)
    @tickets.command(name="role")
    @discord.app_commands.describe(role="This role will be mentioned when someone opens a ticket")
    async def tickets_role(self, ctx: commands.Context, role: discord.Role):
        """Set the tickets support role"""
        await mongodb.set(table="guilds", id=ctx.guild.id, path="tickets.role", value=role.mention)
        await util.throw_fine(ctx, text=f"I've set {role.mention} as the tickets support role")
    
    @commands.cooldown(1, 60, commands.BucketType.channel)
    @tickets.command(name="transcript")
    async def tickets_transcript(self, ctx: commands.Context):
        """Transcript the last 50 messages to a text file"""
        if ctx.channel.type != discord.ChannelType.private_thread and ctx.channel.type != discord.ChannelType.public_thread and ctx.channel.type != discord.ChannelType.news_thread and not ctx.channel.name.startswith("T - "):
            return await util.throw_error(ctx, text="This isn't a valid ticket")
        messages = [message async for message in ctx.channel.history(limit=50)]
        if len(messages) == 0:
            return await util.throw_error(ctx, text="There aren't messages yet to show")
        t = []
        for message in reversed(messages):
            t.append(f"\n@{message.author.name} [{message.created_at}]:\n{message.content}")
        await ctx.send(file=discord.File(io.StringIO("\n".join(t)), "transcript.txt"))
    
    @tickets.command(name="archive")
    async def tickets_archive(self, ctx: commands.Context):
        """Archives this ticket"""
        if ctx.channel.type != discord.ChannelType.private_thread and ctx.channel.type != discord.ChannelType.public_thread and ctx.channel.type != discord.ChannelType.news_thread and not ctx.channel.name.startswith("T - "):
            return await util.throw_error(ctx, text="This isn't a valid ticket")
        v = Confirmation(ctx=ctx)
        v.message = await ctx.send("Are you sure to archive this ticket?", view=v)
        async def f(i: discord.Interaction):
            await i.response.defer()
            await ctx.channel.edit(archived=True)
            await v.message.edit(content="This ticket was archived.")
        v.call_me = f
    
    @commands.hybrid_group(name="starboard", aliases=["star"])
    async def starboard(self, ctx: commands.Context):
        """Manage the starboard settings"""
        ...
    
    @commands.cooldown(1, 15, commands.BucketType.guild)
    @commands.has_guild_permissions(manage_guild=True)
    @starboard.command(name="channel")
    @discord.app_commands.describe(channel="The text channel for the starboard")
    async def starboard_channel(self, ctx: commands.Context, channel: discord.TextChannel):
        """Set the starboard channel"""
        if not channel.permissions_for(ctx.guild.me).send_messages:
            return await util.throw_error(ctx, text="I can't send messages in that channel")
        await mongodb.set(table="guilds", id=ctx.guild.id, path="starboard.channel", value=channel.id)
        await mongodb.set(table="guilds", id=ctx.guild.id, path="starboard.enabled", value=True)
        await util.throw_fine(ctx, text=f"I've set {channel.mention} as the starboard channel")

    @commands.cooldown(1, 15)
    @commands.has_guild_permissions(manage_guild=True)
    @starboard.command(name="stars")
    @discord.app_commands.describe()
    async def starboard_stars(self, ctx: commands.Context, stars: int):
        """Set the starboard stars (default is 3)"""
        if stars > 20 or 2 > stars:
            return await util.throw_error(ctx, text="Invalid range provided, it must be lower than 20 and higher than 2")
        await mongodb.set(table="guilds", id=ctx.guild.id, path="starboard.stars", value=stars)
        await util.throw_fine(ctx, text=f"I've set **{stars}** as the required stars for a message in the starboard")

    @commands.hybrid_group(name="autoroles")
    async def autoroles(self, ctx: commands.Context):
        """Manage the autoroles in the server"""
        ...

    @autoroles.command(name="add")
    @commands.has_guild_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    @discord.app_commands.describe(role="The role to add when someone joins the server")
    async def autoroles_add(self, ctx: commands.Context, role: discord.Role):
        """Add a new autorole"""
        _roles_ = await mongodb.get(table="guilds", id=ctx.guild.id, path="autoroles") or []
        if len(_roles_) >= 50:
            return await util.throw_error(ctx, text="This server has reached the autoroles limit")
        if next((r for r in _roles_ if r == role.id), None):
            return await util.throw_error(ctx, text=f"That autorole already exists")
        _roles_.append(role.id)
        await mongodb.set(table="guilds", id=ctx.guild.id, path="autoroles", value=_roles_)
        await util.throw_fine(ctx, text=f"**{role.name}** was added successfully!", bold=False)

    @autoroles.command(name="remove")
    @commands.has_guild_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    @discord.app_commands.describe(role="The role to remove from the autoroles")
    async def autoroles_remove(self, ctx: commands.Context, role: discord.Role):
        """Remove an autorole"""
        if role.position >= ctx.me.top_role.position:
            return await util.throw_error(ctx, text="The position of that role is higher than my top role, consider moving my role above the autorole you want to set")
        _roles_ = await mongodb.get(table="guilds", id=ctx.guild.id, path="autoroles") or []
        if role.id not in _roles_:
            return await util.throw_error(ctx, "That role isn't in the autoroles list")
        _roles_ =  [r for r in _roles_ if r != role.id]
        await mongodb.set(table="guilds", id=ctx.guild.id, path="autoroles", value=_roles_)
        await util.throw_fine(ctx, f"Removed **{role.name}** from the autoroles list")

    @autoroles.command(name="purge", aliases=["reset"])
    @commands.has_guild_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def autoroles_purge(self, ctx: commands.Context):
        """Purge all autoroles in this server"""
        await ctx.defer()
        v = Confirmation(ctx=ctx)
        v.message = await ctx.send("Are you sure to delete **EVERY** autorole in this server?", view=v)
        async def f(i: discord.Interaction):
            await i.response.defer()
            await mongodb.delete(table="guilds", id=ctx.guild.id, path="autoroles")
            await util.throw_fine(ctx, "Autoroles have been reset.")
        v.call_me = f
    
    @commands.cooldown(1, 7, commands.BucketType.member)
    @autoroles.command(name="list")
    async def tag_list(self, ctx: commands.Context):
        """View the server autoroles"""
        await ctx.defer()
        _roles_ = await mongodb.get(table="guilds", id=ctx.guild.id, path="autoroles") or []
        if not len(_roles_):
            return await util.throw_error(ctx, text="This server doesn't have tags yet")
        emb = discord.Embed(colour=3447003, description="\n".join([f'<@&{r}>' for r in _roles_]), title="Autoroles")
        emb.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar)

        await ctx.send(embed=emb)


async def setup(bot: commands.Bot):
    await bot.add_cog(Tools(bot))