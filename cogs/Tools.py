import discord
from main import util, db
from discord.ext import commands
import pydash as _

class Tools(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
    
    @commands.command(name='prefix')
    @commands.has_permissions(manage_guild=True)
    async def prefix(self, ctx: commands.Context, new_prefix = None):
        if not new_prefix:
            return await util.throw_error(ctx, text="Missing new prefix argument.")
        db.set(f'{ctx.guild.id}.prefix', new_prefix, 'Guilds')
        await util.throw_fine(ctx, text=f'**Prefix channged to: `{new_prefix}` successfully!**', bold=False)
    
    @commands.command(name='customcommand', aliases=['cc'])
    @commands.has_permissions(manage_guild=True)
    async def cc(self, ctx: commands.Context, sub_command: str = None, name: str = None, *, any_content: str = None):
        if not sub_command:
            return await util.throw_error(ctx, text='You need to provide a subcommand name: `add`, `delete`, `edit`, `list`')
        if sub_command.lower() == 'add':
            if not name:
                return await util.throw_error(ctx, text='You need to give a custom command name')
            if not any_content:
                return await util.throw_error(ctx, text='You need to provide the custom command content')
            cmds = db.get(f'{ctx.guild.id}.commands', 'Guilds') or []
            if len(cmds) >= 50:
                return await util.throw_error(ctx, text='The guild has reached the max commands count')
            if next((item for item in cmds if item['name'] == name.lower()), None):
                return await util.throw_error(ctx, text=f'That command already exist')
            cmds.append({ "name": name, "content": any_content })
            db.set(f'{ctx.guild.id}.commands', cmds, 'Guilds')
            await util.throw_fine(ctx, text=f'**{name}** was added successfully!', bold=False)
        elif sub_command.lower() == 'edit' or sub_command.lower() == 'modify':
            if not name:
                return await util.throw_error(ctx, text='You need to give a custom command name')
            if not any_content:
                return await util.throw_error(ctx, text='Missing argument for new content')
            cmds = db.get(f'{ctx.guild.id}.commands', 'Guilds') or []
            found = next((item for item in cmds if item['name'] == name.lower()), None)
            if not found:
                return await util.throw_error(ctx, text='That command doesn\'t exist')
            index = cmds.index(found)
            found['content'] = any_content
            cmds[index] = found
            db.set(f'{ctx.guild.id}.commands', cmds, 'Guilds')
            await util.throw_fine(ctx, text=f'**{name}** was modified successfully!', bold=False)
        elif sub_command.lower() == 'delete' or sub_command.lower() == 'remove':
            if not name:
                return await util.throw_error(ctx, text='You need to give a custom command name')
            cmds = db.get(f'{ctx.guild.id}.commands', 'Guilds') or []
            if not next((item for item in cmds if item['name'] == name.lower()), None):
                return await util.throw_error(ctx, text='That command doesn\'t exist')
            db.set(f'{ctx.guild.id}.commands', [cmd for cmd in cmds if not (cmd['name'] == name.lower())], 'Guilds')
            await util.throw_fine(ctx, text=f'**{name}** was deleted successfully!', bold=False)
        elif sub_command.lower() == 'list' or sub_command.lower() == 'all':
            cmds = _.chunk(db.get(f'{ctx.guild.id}.commands', 'Guilds') or [], 10)
            if not len(cmds):
                return await util.throw_error(ctx, text='This server doesnt have custom commands yet.')
            emb = discord.Embed(colour=3447003)
            for group in cmds:
                emb.add_field(name=f'Group {cmds.index(group) + 1}', value='\n'.join(list(map(lambda c: f"> {group.index(c) + 1} **`{c['name']}`**", group))) or 'No custom commands yet.', inline=True)
            emb.set_author(name=f'{ctx.author.name}#{ctx.author.discriminator}', icon_url=ctx.author.display_avatar)
            await ctx.send(embed=emb)
        else:
            await util.throw_error(ctx, text=f'Invalid subcommand provided')

async def setup(bot: commands.Bot):
    await bot.add_cog(Tools(bot))