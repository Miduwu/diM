import discord
from main import util, mongodb
from discord.ext import commands
import pydash as _
from util.views import Paginator, Confirmation
from util.reader import parse

class Tools(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
    
    async def cog_check(self, ctx: commands.Context):
        if ctx.guild is None:
            await util.throw_error(ctx, text=f'This command is only for servers!')
        return ctx.guild != None
    
    @commands.hybrid_command(name='prefix')
    @commands.has_permissions(manage_guild=True)
    @discord.app_commands.guild_only()
    @discord.app_commands.describe(new_prefix="The new prefix to set")
    async def prefix(self, ctx: commands.Context, new_prefix: str):
        '''Set the server prefix'''
        if not new_prefix:
            return await util.throw_error(ctx, text="Missing new prefix argument.")
        await ctx.defer()
        await mongodb.set(table='guilds', id=ctx.guild.id, path='prefix', value=new_prefix)
        await util.throw_fine(ctx, text=f'**Prefix channged to: `{new_prefix}` successfully!**', bold=False)
    
    @commands.hybrid_group(name='tag')
    async def tags(self, ctx):
        '''Manage the server tags'''
        ...
    
    @commands.has_permissions(manage_guild=True)
    @tags.command(name='add')
    @discord.app_commands.describe(name='The tag name', content='The tag content')
    async def tag_add(self, ctx: commands.Context, name: str, content: str):
        '''Adds a server tag'''
        await ctx.defer()
        _tags_ = await mongodb.get(table='guilds', id=ctx.guild.id, path='tags.list') or []
        if len(_tags_) >= 50:
            return await util.throw_error(ctx, text='This server has reached the tags limit')
        if len(name) >= 100:
            return await util.throw_error(ctx, text="The tag name can't exceed 100 letters")
        if next((item for item in _tags_ if item['name'] == name.lower()), None):
            return await util.throw_error(ctx, text=f'That tag already exists')
        _tags_.append({ "name": name, "content": content[:1950], "author": ctx.author.id })
        await mongodb.set(table='guilds', id=ctx.guild.id, path='tags.list', value=_tags_)
        await util.throw_fine(ctx, text=f'**{name}** was added successfully!', bold=False)
    
    @commands.has_permissions(manage_guild=True)
    @tags.command(name='modify')
    @discord.app_commands.describe(tag='The tag name to modify', content='The new tag contet')
    async def tag_modify(self, ctx: commands.Context, tag: str, content: str):
        '''Edits a server tag'''
        await ctx.defer()
        _tags_ = await mongodb.get(table='guilds', id=ctx.guild.id, path='tags.list') or []
        found = next((item for item in _tags_ if item['name'] == tag.lower()), None)
        if not found:
            return await util.throw_error(ctx, text="That tag doesn't exist")
        index = _tags_.index(found)
        found['content'] = content[:1950]
        _tags_[index] = found
        await mongodb.set(table='guilds', id=ctx.guild.id, path='tags.list', value=_tags_)
        await util.throw_fine(ctx, text=f'**{tag}** was modified successfully!', bold=False)
    
    @commands.has_permissions(manage_guild=True)
    @tags.command(name='delete')
    @discord.app_commands.describe(tag='The tag to delete')
    async def tag_delete(self, ctx: commands.Context, tag: str):
        '''Deletes a server tag'''
        await ctx.defer()
        _tags_ = await mongodb.get(table='guilds', id=ctx.guild.id, path='tags.list') or []
        if not next((item for item in _tags_ if item['name'] == tag.lower()), None):
            return await util.throw_error(ctx, text="That tag doesn't exist")
        await mongodb.set(table='guilds', id=ctx.guild.id, path='tags.list', value=[cmd for cmd in _tags_ if not (cmd['name'] == tag.lower())])
        await util.throw_fine(ctx, text=f'**{tag}** was deleted successfully!', bold=False)
    
    @commands.has_permissions(administrator=True)
    @tags.command(name='purge')
    async def tag_purge(self, ctx: commands.Context):
        '''Purge all the server tags, this is a dangerous command'''
        await ctx.defer()
        v = Confirmation(ctx=ctx)
        v.message = await ctx.send('Are you sure to delete **EVERY** tag in this server?', view=v)
        async def f(i: discord.Interaction):
            await i.response.defer()
            await mongodb.set(table='guilds', id=ctx.guild.id, path='tags.list', value=[])
            await util.throw_fine(ctx, text='Every tag in this server was deleted!')
        v.continue_forcing = f
    
    @tags.command(name='list')
    async def tag_list(self, ctx: commands.Context):
        '''Views the server tags'''
        await ctx.defer()
        _tags_ = _.chunk(await mongodb.get(table='guilds', id=ctx.guild.id, path='tags.list') or [], 5)
        if not len(_tags_):
            return await util.throw_error(ctx, text="This server doesn't have tags yet")
        func = lambda arr: '\n'.join(list(map(lambda obj: f'>>> {obj["name"]} [AUTHOR: {self.bot.get_user(obj["author"]).name if self.bot.get_user(obj["author"]) else "Unknown"}]', arr)))
        v = Paginator(data=_tags_, ctx=ctx)
        def update(item):
            v.content = f'**[Page: {v.page + 1}/{len(_tags_)}]** ```py\n{func(item)}```'
        v.update_item = update
        v.message = await ctx.send(f'**[Page: {v.page + 1}/{len(_tags_)}]**```py\n{func(_tags_[0])}```', view=v)
    
    @tags.command(name='view')
    @discord.app_commands.describe(tag='The tag to view')
    async def tag_view(self, ctx: commands.Context, tag: str):
        '''Views a server tag'''
        await ctx.defer()
        _tags_ = await mongodb.get(table='guilds', id=ctx.guild.id, path='tags.list') or []
        found = next((item for item in _tags_ if item['name'] == tag.lower()), None)
        if not found:
            return await util.throw_error(ctx, text="That tag doesn't exist")
        await ctx.send(parse(found['content'], ctx))

async def setup(bot: commands.Bot):
    await bot.add_cog(Tools(bot))