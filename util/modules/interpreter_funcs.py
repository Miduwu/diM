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

FUNCS = {
    "@title": title,
    "@description": description,
    "@lower": lower,
    "@upper": upper,
    "@user.name": user_name
}