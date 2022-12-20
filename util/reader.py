from main import bot
from discord.ext import commands
import re

def parse(text: str, ctx: commands.Context):
    return text.replace(
        '{user.name}', ctx.author.name
        ).replace(
            '{user.avatar}', str(ctx.author.display_avatar)
        ).replace(
            '{user.discriminator}', ctx.author.discriminator
        ).replace(
            '{user.mention}', ctx.author.mention
        ).replace(
            '{user.id}', str(ctx.author.id)
        ).replace(
            '{server.id}', str(ctx.guild.id)
        ).replace(
            '{server.name}', ctx.guild.name
        ).replace(
            '{server.icon}', str(ctx.guild.icon)
        ).replace(
            '{server.members}', str(ctx.guild.member_count)
        ).replace(
            '{server.owner}', str(ctx.guild.owner_id)
        )