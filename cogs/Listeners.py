from datetime import datetime
from main import util
from discord.ext import commands
from util.coreback import sync
import discord

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
            return await util.throw_error(ctx, text=f"Invalid argument type provided")
        elif isinstance(error, commands.ChannelNotReadable):
            return await util.throw_error(ctx, text=f"I can't read messages in that channel, i don't have access to it")
        else:
            print("\n".join(util.load_exception(error)))

    @commands.Cog.listener()
    async def on_ready(self):
        print("diM is online")
        util.uptime = datetime.now()
        util.app_commands = await sync(self.bot.tree)
    
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

async def setup(bot: commands.Bot):
    await bot.add_cog(Listeners(bot))