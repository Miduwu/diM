import discord
import pydash as _
from discord.ext import commands
from .views import Paginator
from typing import List, Dict
import os

async def get_app_commands_from_cog(cog: str, cache_commands: List[discord.app_commands.AppCommand], bot: commands.Bot):
    cmds = bot.get_cog(cog).get_commands()
    filtered = filter(lambda c: _.find(cache_commands, lambda s: s.name == c.name), cmds)
    children = []
    for command in filtered:
        cmd = [c for c in cache_commands if c.name == command.name][0]
        if cmd.options:
            for option in cmd.options:
                if option.type == discord.AppCommandOptionType.subcommand:
                    children.append({ "id": f"</{cmd.name} {option.name}:{cmd.id}>", "description": option.description })
                elif option.type == discord.AppCommandOptionType.subcommand_group:
                    if option.options:
                        for op in option.options:
                            if option.type == discord.AppCommandOptionType.subcommand:
                                children.append({ "id": f"</{cmd.name} {option.name} {op.name}:{cmd.id}>", "description": op.description })
                else:
                    children.append({ "id": f"</{cmd.name}:{cmd.id}>", "description": cmd.description })
        else:
            children.append({ "id": f"</{cmd.name}:{cmd.id}>", "description": cmd.description })
    not_repeated = []
    for child in children:
        if child['id'] in map(lambda x: x['id'], not_repeated):
            continue
        else:
            not_repeated.append(child)
    return not_repeated

def parse_params(params: Dict[str, commands.Parameter], default=''):
    if not params:
        return default
    keys = params.keys()
    parsed = []
    for key in keys:
        value = params[key]
        parsed.append(f'[{value.name}]' if not value.required else f'<{value.name}>')
    return ' '.join(parsed)

def parse_aliases(command: commands.HybridCommand):
    before = command.full_parent_name
    if len(command.aliases) > 0:
        b = "|".join(command.aliases)
        return f'{before + " " if before else ""}[{command.name}|{b}]'
    else:
        return f'{before + " " if before else ""}' + command.name

class MenuHelpSelect(discord.ui.Select):
    def __init__(self, *, ctx: commands.Context, embed: discord.Embed, commands: List[discord.app_commands.AppCommand]):
        self.ctx = ctx
        self.embed = embed
        self.commands = commands
        self.bot: commands.Bot = self.ctx.bot
        cogs = list(map(lambda cog: cog[0], list(self.bot.cogs.items())))
        ops = []
        for cog in cogs:
            if cog == 'Dev' or cog == 'Listeners':
                continue
            ops.append(discord.SelectOption(label=cog, description=f'Get the {cog} commands'))
        super().__init__(placeholder="Select a module", max_values=1, min_values=1, options=ops)
    
    async def callback(self, interaction: discord.Interaction):
        cmds = await get_app_commands_from_cog(self.values[0], self.commands, self.bot)
        mapped = map(lambda x: f'**{x["id"]}** :: {x["description"]}', cmds)
        try:
            self.embed.clear_fields()
            _chunk = _.chunk(list(mapped), 10)
            self.embed.description = '\n'.join(_chunk[0])
            self.embed.set_footer(text=f'Page: 1/{len(_chunk)}', icon_url=self.bot.user.display_avatar)
            pag = Paginator(data=_chunk, ctx=self.ctx, embed=self.embed, timeout=40)
            def update(item):
                self.embed.description = '\n'.join(item)
                self.embed.set_footer(text=f'Page: {pag.page + 1}/{len(_chunk)}', icon_url=self.bot.user.display_avatar)
            pag.update_item = update
            pag.message = interaction.message
            await interaction.response.edit_message(embed=self.embed, view=pag.add_item(self))
        except:
            pass

class HelpView(discord.ui.View):
    def __init__(self, *, timeout = 30, embed: discord.Embed, ctx: commands.Context, commands: List[discord.app_commands.AppCommand]):
        super().__init__(timeout=timeout)
        self.add_item(MenuHelpSelect(ctx=ctx, embed=embed, commands=commands))
        self.message: discord.Message = None
        self.ctx = ctx
    
    async def on_timeout(self):
        components = self.from_message(await self.message.fetch())
        for i in range(0, len(components.children)):
            components.children[i].disabled = True
        await self.message.edit(view=components)
    
    async def interaction_check(self, interaction: discord.Interaction):
        if self.ctx.author.id != interaction.user.id:
            await interaction.response.send_message(content=f'{interaction.user.mention}, this interaction isn\'t for you :bloboohcry:', ephemeral=True)
        return self.ctx.author.id == interaction.user.id

async def send_help(ctx: commands.Context, slash):
    emb = discord.Embed(description=f"Welcome to **{ctx.bot.user.name}**'s help.\nI'm a super discord bot and i will help you with some tasks in this server!", colour=3447003)
    emb.add_field(name='Useful links', value=f'[Invite]({os.getenv("INVITE")}) | [Server]({os.getenv("SERVER")})')
    emb.set_author(name=f'{ctx.author.name}#{ctx.author.discriminator}', icon_url=ctx.author.display_avatar)
    emb.set_thumbnail(url=ctx.bot.user.display_avatar)
    emb.set_footer(text=f'Use {ctx.clean_prefix}help <command> to get more information about a command. :)', icon_url=ctx.bot.user.display_avatar)
    v = HelpView(embed=emb, ctx=ctx, commands=slash)
    v.message = await ctx.send(embed=emb, view=v)

async def send_help_cog(ctx: commands.Context, cog: str, slash: List[discord.app_commands.AppCommand]):
    cmds = await get_app_commands_from_cog(cog, slash, ctx.bot)
    mapped = map(lambda x: f'**{x["id"]}** :: {x["description"]}', cmds)
    _chunk = _.chunk(list(mapped), 10)
    emb = discord.Embed(title=f'{cog} [1/{len(_chunk)}]', colour=3447003, description='\n'.join(_chunk[0]))
    emb.set_author(name=f'{ctx.author.name}#{ctx.author.discriminator}', icon_url=ctx.author.display_avatar)
    emb.set_footer(text=f'Use {ctx.clean_prefix}help <command> to get more information about a command. :)', icon_url=ctx.bot.user.display_avatar)
    v = Paginator(data=_chunk, ctx=ctx, embed=emb)
    def update(item):
        v.embed.title = f'{cog} [{v.page + 1}/{len(_chunk)}]'
        v.embed.description = '\n'.join(item)
    v.update_item = update
    v.message = await ctx.send(embed=emb, view=v)

async def send_help_group(ctx: commands.Context, group: commands.HybridGroup, slash: List[discord.app_commands.AppCommand]):
    as_slash: discord.app_commands.AppCommand = _.find(slash, lambda x: x.name == group.name)
    subcmds = []
    for subcmd in as_slash.options:
        if subcmd.type == discord.AppCommandOptionType.subcommand:
            subcmds.append({ "id": f"</{as_slash.name} {subcmd.name}:{as_slash.id}>", "description": subcmd.description })
    mapped = list(map(lambda s: f'**{s["id"]}** :: {s["description"]}', subcmds))
    emb = discord.Embed(title=group.name, colour=3447003, description=as_slash.description or 'No description.')
    emb.set_author(name=f'{ctx.author.name}#{ctx.author.discriminator}', icon_url=ctx.author.display_avatar)
    emb.set_footer(text=f'Use {ctx.clean_prefix}help <command> to get more information about a command. :)', icon_url=ctx.bot.user.display_avatar)
    if len(mapped) != 0:
        emb.add_field(name='Subcommands:', value='\n'.join(mapped))
    await ctx.send(embed=emb)

async def send_help_command(ctx: commands.Context, command: commands.HybridCommand, slash: List[discord.app_commands.AppCommand]):
    as_slash: discord.app_commands.AppCommand = _.find(slash, lambda x: x.name == command.name)
    emb = discord.Embed(title=command.name, colour=3447003)
    emb.set_author(name=f'{ctx.author.name}#{ctx.author.discriminator}', icon_url=ctx.author.display_avatar)
    emb.set_footer(text=f"{ctx.bot.user.name}#{ctx.bot.user.discriminator}", icon_url=ctx.bot.user.display_avatar)
    if not command.app_command.parent:
        slash = f"</{as_slash.name}:{as_slash.id}>"
        module = command.cog.__cog_name__
        cooldown = round(command.cooldown.per) if command.cooldown else "None"
        usage = f'```fix\n{ctx.clean_prefix}{parse_aliases(command)} {parse_params(command.params)}```'
        example = f"\n**Example:** {command.__original_kwargs__.get('example') if command.__original_kwargs__.get('example', None) else ''}"
        emb.description = f"**Description:** {as_slash.description or 'No description.'}\n**Slash:** {slash}\n**Category:** {module}\n**Cooldown:** {cooldown}s{example}\n**Usage:** {usage}"
    else:
        group: discord.app_commands.AppCommand = _.find(slash, lambda x: x.name == command.app_command.parent.name)
        subcmd = _.find(group.options, lambda c: c.name == command.name and c.type == discord.AppCommandOptionType.subcommand)
        slash = f"</{group.name} {subcmd.name}:{group.id}>"
        module = command.cog.__cog_name__
        cooldown = round(command.cooldown.per) if command.cooldown else "None"
        example = f"\n**Example:** {command.__original_kwargs__.get('example') if command.__original_kwargs__.get('example', None) else ''}"
        usage = f'```fix\n{ctx.clean_prefix}{parse_aliases(command)} {parse_params(command.params)}```'
        emb.description = f"**Description:** {subcmd.description or 'No description.'}\n**Slash:** {slash}\n**Category:** {module}\n**Cooldown:** {cooldown}s{example}\n**Usage:** {usage}"

    await ctx.send(embed=emb)