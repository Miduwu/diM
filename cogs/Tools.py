import discord
from main import util, mongodb, interpreter
from discord.ext import commands
import pydash as _
from util.views import Paginator, Confirmation
from difflib import get_close_matches
import re

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
        d = await interpreter.read(text[:2000], ctx)
        final = re.sub("FUNC#\d+", "", d.code).strip()
        if not d.embed and not final:
            return await util.throw_error(ctx, text="Invalid text provided, it doesn't return anything")
        await ctx.send(content=final if final else None, embed=d.embed)
    
    @commands.cooldown(1, 4, commands.BucketType.member)
    @commands.hybrid_group(name="tag", fallback="view", aliases=["t"])
    @discord.app_commands.describe(tag="The tag to view")
    async def tags(self, ctx: commands.Context, tag: str):
        """Manage the server tags, or view one"""
        await ctx.defer()
        _tags_ = await mongodb.get(table="guilds", id=ctx.guild.id, path="tags.list") or []
        found = next((item for item in _tags_ if item["name"].lower() == tag.lower()), None)
        if not found:
            return await util.throw_error(ctx, text="That tag doesn't exist")
        d = await interpreter.read(found["content"], ctx)
        final = re.sub("FUNC#\d+", "", d.code).strip()
        await ctx.send(content=final if final or d.embed else "No content, lmao i know this is crazy, please modify this tag", embed=d.embed)
    
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 25, commands.BucketType.member)
    @tags.command(name="add")
    @discord.app_commands.describe(name="The tag name", content="The tag content")
    async def tag_add(self, ctx: commands.Context, name: str, *, content: str):
        """Add a server tag"""
        await ctx.defer()
        _tags_ = await mongodb.get(table="guilds", id=ctx.guild.id, path="tags.list") or []
        if len(_tags_) >= 50:
            return await util.throw_error(ctx, text="This server has reached the tags limit")
        if len(name) >= 100:
            return await util.throw_error(ctx, text="The tag name can't exceed 100 letters")
        if next((item for item in _tags_ if item["name"].lower() == name.lower()), None):
            return await util.throw_error(ctx, text=f"That tag already exists")
        _tags_.append({ "name": name, "content": content[:1950], "author": ctx.author.id })
        await mongodb.set(table="guilds", id=ctx.guild.id, path="tags.list", value=_tags_)
        await util.throw_fine(ctx, text=f"**{name}** was added successfully!", bold=False)
    
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 15, commands.BucketType.member)
    @tags.command(name="modify")
    @discord.app_commands.describe(tag="The tag name to modify", content="The new tag contet")
    async def tag_modify(self, ctx: commands.Context, tag: str, *, content: str):
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
    async def tag_delete(self, ctx: commands.Context, tag: str):
        """Delete a server tag"""
        await ctx.defer()
        _tags_ = await mongodb.get(table="guilds", id=ctx.guild.id, path="tags.list") or []
        if not next((item for item in _tags_ if item["name"].lower() == tag.lower()), None):
            return await util.throw_error(ctx, text="That tag doesn't exist")
        await mongodb.set(table="guilds", id=ctx.guild.id, path="tags.list", value=[cmd for cmd in _tags_ if not (cmd["name"] == tag.lower())])
        await util.throw_fine(ctx, text=f"**{tag}** was deleted successfully!", bold=False)
    
    @commands.cooldown(1, 7, commands.BucketType.member)
    @tags.command(name="search")
    @discord.app_commands.describe(tag="Query to search in server tags")
    async def tag_search(self, ctx: commands.Context, tag: str):
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
        emb.set_author(name=f"{ctx.author.name}#{ctx.author.discriminator}", icon_url=ctx.author.display_avatar)
        emb.description = func(_chunk_[0])
        v = Paginator(data=_chunk_, ctx=ctx, embed=emb)
        def update(item):
            v.content = f"**[Page: {v.page + 1}/{len(_chunk_)}]**"
            v.embed.description = func(item)
        v.update_item = update
        v.message = await ctx.send(content=f"**[Page: {v.page + 1}/{len(_chunk_)}]**", view=v, embed=emb)
    
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 180, commands.BucketType.member)
    @tags.command(name="purge")
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
        emb.set_author(name=f"{ctx.author.name}#{ctx.author.discriminator}", icon_url=ctx.author.display_avatar)
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
        ]
    
    @commands.hybrid_group(name="dropdown", aliases=["menuroles"])
    async def dropdown(self, ctx):
        """Manage the dropdown roles"""
        ...
    
    @commands.cooldown(1, 60, commands.BucketType.guild)
    @commands.has_guild_permissions(manage_roles=True)
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
        
async def setup(bot: commands.Bot):
    await bot.add_cog(Tools(bot))