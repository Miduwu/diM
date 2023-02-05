import discord
from discord.ext import commands

class Data:
    def __init__(self) -> None:
        self.embed = None
        self.buttons = None
        self.metadata = {}
        self.code: str = ""
        self.func = None
        self.ctx: commands.Context = None
        self.interpreter = None

async def title(d: Data):
    await d.interpreter.resolve_overloads(d)
    if not d.func["inside"]:
        return d.code
    if not d.embed:
        d.embed = discord.Embed()
    d.embed.title = d.func["inside"]
    return d.code.replace(d.func["id"], "")

async def description(d: Data):
    await d.interpreter.resolve_overloads(d)
    if not d.func["inside"]:
        return d.code
    if not d.embed:
        d.embed = discord.Embed()
    d.embed.description = d.func["inside"]
    return d.code.replace(d.func["id"], "")

async def thumbnail(d: Data):
    await d.interpreter.resolve_overloads(d)
    if not d.func["inside"]:
        return d.code
    if not d.embed:
        d.embed = discord.Embed()
    d.embed.set_thumbnail(d.func["inside"])
    return d.code.replace(d.func["id"], "")

async def color(d: Data):
    await d.interpreter.resolve_overloads(d)
    if not d.func["inside"]:
        return d.code
    if not d.embed:
        d.embed = discord.Embed()
    d.embed.color = d.func["inside"]
    return d.code.replace(d.func["id"], "")

async def image(d: Data):
    await d.interpreter.resolve_overloads(d)
    if not d.func["inside"]:
        return d.code
    if not d.embed:
        d.embed = discord.Embed()
    d.embed.image = d.func["inside"]
    return d.code.replace(d.func["id"], "")

async def lower(d: Data):
    await d.interpreter.resolve_overloads(d)
    if not d.func["inside"]:
        return d.code
    return d.code.replace(d.func["id"], d.func["inside"].lower())

async def upper(d: Data):
    await d.interpreter.resolve_overloads(d)
    if not d.func["inside"]:
        return d.code
    return d.code.replace(d.func["id"], d.func["inside"].upper())

async def user_name(d: Data):
    return d.code.replace(d.func["id"], d.ctx.author.name)

async def user_tag(d: Data):
    return d.code.replace(d.func["id"], f'{d.ctx.author.name}#{d.ctx.author.discriminator}')

async def user_id(d: Data):
    return d.code.replace(d.func["id"], d.ctx.author.id)

async def server_name(d: Data):
    return d.code.replace(d.func["id"], d.ctx.guild.name)

async def server_id(d: Data):
    return d.code.replace(d.func["id"], d.ctx.guild.id)

async def server_owner_id(d: Data): 
    return d.code.replace(d.func["id"], d.ctx.guild.owner_id)

async def member_count(d: Data):
    return d.code.replace(d.func["id"], d.ctx.guild.member_count)

async def role_count(d: Data):
    return d.code.replace(d.func["id"], d.ctx.guild.roles.count)

FUNCS = {
    "@title": title,
    "@description": description,
    "@image": image,
    "@thumbnail": thumbnail,
    "@color": color,
    "@lower": lower,
    "@upper": upper,
    "@user.name": user_name,
    "@user.tag": user_tag,
    "@user.id": user_id,
    "@server.name": server_name,
    "@server.id": server_id,
    "@member.count": member_count,
    "@owner.id": server_owner_id,
    "@role.count": role_count
}