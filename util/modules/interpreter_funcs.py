import discord
from discord.ext import commands
import re

URL_REGEXP = "^https?:\\/\\/(?:www\\.)?[-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{2,6}"

class Data:
    def __init__(self) -> None:
        self.embed: discord.Embed | None = None
        self.buttons = None
        self.metadata = {}
        self.code: str = ""
        self.func = None
        self.ctx: commands.Context = None
        self.interpreter = None

async def title(d: Data, u):
    await d.interpreter.resolve_overloads(d)
    if not d.func["inside"]:
        return d.code
    if not d.embed:
        d.embed = discord.Embed()
    d.embed.title = d.func["inside"]
    return d.code.replace(d.func["id"], "")

async def description(d: Data, u):
    await d.interpreter.resolve_overloads(d)
    if not d.func["inside"]:
        return d.code
    if not d.embed:
        d.embed = discord.Embed()
    d.embed.description = d.func["inside"]
    return d.code.replace(d.func["id"], "")

async def thumbnail(d: Data, u):
    await d.interpreter.resolve_overloads(d)
    if not d.func["inside"] or not re.match(URL_REGEXP, d.func["inside"]):
        return d.code
    if not d.embed:
        d.embed = discord.Embed()
    d.embed.set_thumbnail(url=d.func["inside"])
    return d.code.replace(d.func["id"], "")

async def color(d: Data, u):
    await d.interpreter.resolve_overloads(d)
    if not d.func["inside"] or not u.is_hex(d.func["inside"]):
        return d.code
    if not d.embed:
        d.embed = discord.Embed()
    d.embed.color = int(d.func["inside"].replace("#", ""), 16)
    return d.code.replace(d.func["id"], "")

async def image(d: Data, u):
    await d.interpreter.resolve_overloads(d)
    if not d.func["inside"] or not re.match(URL_REGEXP, d.func["inside"]):
        return d.code
    if not d.embed:
        d.embed = discord.Embed()
    d.embed.set_image(url=d.func["inside"])
    return d.code.replace(d.func["id"], "")

async def author(d: Data, u):
    await d.interpreter.resolve_overloads(d)
    if not d.func["inside"]:
        return d.code
    if not d.embed:
        d.embed = discord.Embed()
    if len(d.func["fields"]) >= 2 and re.match(URL_REGEXP, d.func["fields"][1]["value"]):
        d.embed.set_author(name=d.func["fields"][0]["value"], icon_url=d.func["fields"][1]["value"])
    else:
        d.embed.set_author(name=d.func["fields"][0]["value"])

async def footer(d: Data, u):
    await d.interpreter.resolve_overloads(d)
    if not d.func["inside"]:
        return d.code
    if not d.embed:
        d.embed = discord.Embed()
    if len(d.func["fields"]) >= 2 and re.match(URL_REGEXP, d.func["fields"][1]["value"]):
        d.embed.set_footer(text=d.func["fields"][0]["value"], icon_url=d.func["fields"][1]["value"])
    else:
        d.embed.set_footer(text=d.func["fields"][0]["value"])

async def lower(d: Data, u):
    await d.interpreter.resolve_overloads(d)
    if not d.func["inside"]:
        return d.code
    return d.code.replace(d.func["id"], d.func["inside"].lower())

async def upper(d: Data, u):
    await d.interpreter.resolve_overloads(d)
    if not d.func["inside"]:
        return d.code
    return d.code.replace(d.func["id"], d.func["inside"].upper())

async def user_name(d: Data, u):
    return d.code.replace(d.func["id"], d.ctx.author.name)

async def user_tag(d: Data, u):
    return d.code.replace(d.func["id"], f'{d.ctx.author.name}#{d.ctx.author.discriminator}')

async def user_id(d: Data, u):
    return d.code.replace(d.func["id"], str(d.ctx.author.id))

async def user_avatar(d: Data, u):
    return d.code.replace(d.func["id"], str(d.ctx.author.display_avatar).replace(".webp", ".png"))

async def server_name(d: Data, u):
    return d.code.replace(d.func["id"], d.ctx.guild.name)

async def server_id(d: Data, u):
    return d.code.replace(d.func["id"], str(d.ctx.guild.id))

async def server_owner_id(d: Data, u): 
    return d.code.replace(d.func["id"], str(d.ctx.guild.owner_id))

async def server_icon(d: Data, u):
    return d.code.replace(d.func["id"], str(d.ctx.guild.icon).replace(".webp", ".png"))

async def member_count(d: Data, u):
    return d.code.replace(d.func["id"], str(d.ctx.guild.member_count))

async def role_count(d: Data, u):
    return d.code.replace(d.func["id"], str(len(d.ctx.guild.roles)))

FUNCS = {
    "@title": title,
    "@description": description,
    "@image": image,
    "@thumbnail": thumbnail,
    "@color": color,
    "@author": author,
    "@footer": footer,
    "@lower": lower,
    "@upper": upper,
    "@user.name": user_name,
    "@user.tag": user_tag,
    "@user.id": user_id,
    "@user.avatar": user_avatar,
    "@server.name": server_name,
    "@server.id": server_id,
    "@server.owner": server_owner_id,
    "@server.members": member_count,
    "@server.roles": role_count,
    "@server.icon": server_icon
}