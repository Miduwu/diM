from discord.ext import commands
from typing_extensions import Annotated
from main import util
import discord
import datetime

class Mod(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.has_guild_permissions(manage_channels=True)
    @commands.hybrid_group(name="lockdown")
    async def lockdown(self, ctx: commands.Context):
        """Set or unset a lockdown in a text channel"""
        ...
    
    @commands.cooldown(1, 8, commands.BucketType.member)
    @commands.bot_has_guild_permissions(manage_channels=True)
    @commands.has_guild_permissions(manage_channels=True)
    @discord.app_commands.describe(channel="The channel to lock")
    @lockdown.command(name="set")
    async def lockdown_set(self, ctx: commands.Context, channel: discord.TextChannel = None):
        """Set a text channel as locked"""
        if channel is None:
            channel = ctx.channel
        if not channel.permissions_for(ctx.guild.default_role).send_messages:
            return await util.throw_error(ctx, text="That channel is already locked, so i can't lock it again")
        await channel.set_permissions(ctx.guild.default_role, send_messages=False)
        await util.throw_fine(ctx, text=f"{channel.mention} has been locked!", defer=False)
    
    @commands.cooldown(1, 6, commands.BucketType.member)
    @commands.bot_has_guild_permissions(manage_channels=True)
    @commands.has_guild_permissions(manage_channels=True)
    @discord.app_commands.describe(channel="The channel to unlock")
    @lockdown.command(name="unset")
    async def lockdown_unset(self, ctx: commands.Context, channel: discord.TextChannel = None):
        """Set a text channel as unlocked"""
        if channel is None:
            channel = ctx.channel
        if channel.permissions_for(ctx.guild.default_role).send_messages:
            return await util.throw_error(ctx, text="That channel isn't locked, so i can't unlock it")
        await channel.set_permissions(ctx.guild.default_role, send_messages=None)
        await util.throw_fine(ctx, text=f"{channel.mention} has been unlocked!", defer=False)
    
    @commands.has_guild_permissions(moderate_members=True)
    @commands.hybrid_group(name="timeout")
    async def timeoutgroup(self, ctx):
        """Timeour or untimeout a member"""
        ...
    
    @commands.cooldown(1, 6, commands.BucketType.member)
    @commands.bot_has_guild_permissions(moderate_members=True)
    @commands.has_guild_permissions(moderate_members=True)
    @discord.app_commands.describe(member="The member to timeout", duration="The timeout duration. Ex: 1d", reason="Optional reason for this timeout")
    @timeoutgroup.command(name="set", aliases=["add"])
    async def timeoutset(self, ctx: commands.Context, member: discord.Member, duration: str = None, *, reason: str = None):
        """Add a member a timeout"""
        if member.id == ctx.author.id:
            return await util.throw_error(ctx, text="You can't timeout yourself")
        if member.id == self.bot.user.id:
            return await util.throw_error(ctx, text="nooooo, please don't timeout me")
        if member.id == ctx.guild.owner_id:
            return await util.throw_error(ctx, text="You can't timeout to the server owner")
        if member.guild_permissions.administrator:
            return await util.throw_error(ctx, text="You can't timeout administrators")
        if member.top_role.position >= ctx.author.top_role.position:
            return await util.throw_error(ctx, text="This user has the same or higher role than yours")
        if member.top_role.position >= ctx.guild.me.top_role.position:
            return await util.throw_error(ctx, text="This user has the same or higher role than mine")
        time = util.ms(duration or "1h")
        if not time or time >= util.ms("1w") or time < util.ms("1m"):
            return await util.throw_error(ctx, text="That is not a valid duration, make sure its readable time like: '1d', and i can't be higher than 1 week or lower than 1 minute")
        if member.is_timed_out():
            return await util.throw_error(ctx, text="That member is already in timeout lol")
        await member.timeout(datetime.timedelta(milliseconds=time), reason=reason)
        await util.throw_fine(ctx, text=f"***{member.name}*** was timeouted successfully!", bold=False)
    
    @commands.cooldown(1, 4, commands.BucketType.member)
    @commands.bot_has_guild_permissions(moderate_members=True)
    @commands.has_guild_permissions(moderate_members=True)
    @discord.app_commands.describe(member="The member to untimeout")
    @timeoutgroup.command(name="unset", aliases=["remove"])
    async def timeoutunset(self, ctx: commands.Context, member: discord.Member):
        """Remove a member a timeout"""
        if not member.is_timed_out():
            return await util.throw_error(ctx, text="That member is not in timeout")
        await member.timeout(None)
        await util.throw_fine(ctx, text=f"***{member.name}*** was untimeouted successfully!", bold=False)
    
    @commands.cooldown(1, 8, commands.BucketType.member)
    @commands.bot_has_guild_permissions(manage_messages=True)
    @commands.has_guild_permissions(manage_messages=True)
    @commands.hybrid_command(name="clear", aliases=["purge", "clean"])
    @discord.app_commands.describe(amount="The amount of messages to delete", member="Optional filter, the member author to delete the messages")
    async def clear(self, ctx: commands.Context, amount: int, member: discord.Member = None):
        """Delete X messages in this channel with optional filter"""
        if amount > 100:
            return await util.throw_error(ctx, text="You can't exceed 100 messages")
        elif 1 > amount:
            return await util.throw_error(ctx, text="Invalid amount provide, try with +1")
        if ctx.interaction:
            await ctx.send(content="Deleting messages...", ephemeral=True, delete_after=5.0)
        try:
            if not member:
                messages = await ctx.channel.purge(limit=amount)
                await ctx.channel.send(f"**{len(messages)}** message(s) has been deleted successfully! <:blobheart:1011458084239056977>", delete_after=7.0)
            else:
                messages = await ctx.channel.purge(limit=amount, check=lambda m: m.author.id == member.id)
                await ctx.channel.send(f"**{len(messages)}** message(s) has beel deleted successfully! <:blobheart:1011458084239056977>", delete_after=7.0)
        except:
            await util.throw_error(ctx, text="I was unable to do that, due discord API limitation i can't delete messages older than 14 days")
    
    @commands.cooldown(1, 10, commands.BucketType.member)
    @commands.bot_has_guild_permissions(kick_members=True)
    @commands.has_guild_permissions(kick_members=True)
    @commands.hybrid_command(name="kick")
    @discord.app_commands.describe(member="The member to kick", reason="Optional reason")
    async def kick(self, ctx: commands.Context, member: discord.Member, * , reason = "Unknown reason"):
        """Kick a member from this server"""
        if member.id == ctx.author.id:
            return await util.throw_error(ctx, text="You can't kick yourself")
        if member.id == self.bot.user.id:
            return await util.throw_error(ctx, text="nooooo, please don't kick me")
        if member.id == ctx.guild.owner_id:
            return await util.throw_error(ctx, text="You can't kick to the server owner")
        if member.guild_permissions.administrator:
            return await util.throw_error(ctx, text="You can't kick administrators")
        if member.top_role.position >= ctx.author.top_role.position:
            return await util.throw_error(ctx, text="This user has the same or higher role than yours")
        if member.top_role.position >= ctx.guild.me.top_role.position:
            return await util.throw_error(ctx, text="This user has the same or higher role than mine")
        try:
            await member.kick(reason=reason)
            await util.throw_fine(ctx, text=f"***{member.name}*** was kicked successfully!", bold=False)
        except:
            await util.throw_error(ctx, text="I was unable to kick that member")
    
    @commands.cooldown(1, 10, commands.BucketType.member)
    @commands.bot_has_guild_permissions(ban_members=True)
    @commands.has_guild_permissions(ban_members=True)
    @commands.hybrid_command(name="ban")
    @discord.app_commands.describe(member="The member to ban", delete_messages="If i should delete the banned user messages", reason="Optional reason")
    async def ban(self, ctx: commands.Context, member: discord.Member, delete_messages: bool = True, *, reason = "Unknown reason"):
        """Ban a member from this server"""
        if member.id == ctx.author.id:
            return await util.throw_error(ctx, text="You can't ban yourself")
        if member.id == self.bot.user.id:
            return await util.throw_error(ctx, text="nooooo, please don't ban me")
        if member.id == ctx.guild.owner_id:
            return await util.throw_error(ctx, text="You can't ban to the server owner")
        if member.guild_permissions.administrator:
            return await util.throw_error(ctx, text="You can't ban administrators")
        if member.top_role.position >= ctx.author.top_role.position:
            return await util.throw_error(ctx, text="This user has the same or higher role than yours")
        if member.top_role.position >= ctx.guild.me.top_role.position:
            return await util.throw_error(ctx, text="This user has the same or higher role than mine")
        try:
            await member.ban(reason=reason, delete_message_days=0 if not delete_messages else 7)
            await util.throw_fine(ctx, text=f"***{member._user.name}*** was banned successfully!", bold=False)
        except:
            await util.throw_error(ctx, text="I was unable to ban that member")

    @commands.cooldown(1, 10, commands.BucketType.member)
    @commands.bot_has_guild_permissions(ban_members=True)
    @commands.has_guild_permissions(ban_members=True)
    @commands.hybrid_command(name="unban")
    @discord.app_commands.describe(user="The user to unban", reason="Optional reason")
    async def unban(self, ctx: commands.Context, user: discord.User, *, reason: str = "Unknown reason"):
        """Unban a user from this server"""
        try:
            await ctx.guild.fetch_ban(user)
        except:
            return await util.throw_error(ctx, text="That user isn't banned")
        try:
            await ctx.guild.unban(user, reason=reason)
            await util.throw_fine(ctx, text=f"***{user.name}*** was unbanned successfully!", bold=False)
        except:
            await util.throw_error(ctx, text="I was unable to unban that user")
    
    @commands.cooldown(1, 30, commands.BucketType.channel)
    @commands.bot_has_guild_permissions(manage_messages=True, add_reactions=True, embed_links=True)
    @commands.hybrid_command(name="poll", aliases=["survey"], example='!poll my title | option 1 | option 2')
    @discord.app_commands.describe(text="The poll title and options separated by a space, you can use quotation marks for multiple word option, example: \"option one\" ")
    async def poll(self, ctx: commands.Context, *, text: str):
        """Make a poll"""
        ops = text.split("|")
        title, question, ops = f"📫 New poll started by **@{ctx.author.name}**", ops[0], ops[1:] if len(ops) > 1 else []
        ops = [x.strip() for x in ops]
        if ops and len(ops) > 15:
            return await util.throw_error(ctx, text="You can't add more than 15 options")
        if not len(ops):
            emb = discord.Embed(color=3447003, description=f"{title}\n```fix\n{question[:300]}```")
            emb.set_author(name=f"@{ctx.author.name}", icon_url=ctx.author.display_avatar)
            m = await ctx.channel.send(embed=emb)
            await m.add_reaction("tokyo_like:964965007647445012")
            await m.add_reaction("tokyo_dislike:964965207485075506")
            await m.add_reaction("tokyo_question:962507048321441792")
            if ctx.interaction:
                await util.throw_fine(ctx, text="I've created the poll successfully!")
            else:
                await ctx.message.delete()
        else:
            ALPHABET = ['🇦', '🇧', '🇨', '🇩', '🇪', '🇫', '🇬', '🇭', '🇮', '🇯', '🇰', '🇱', '🇲', '🇳', '🇴', '🇵', '🇶', '🇷', '🇸', '🇹', '🇺', '🇻', '🇼', '🇽', '🇾', '🇿']
            arr = []
            for index, item in enumerate(ops):
                arr.append(f"{ALPHABET[index]}:: {item[:100]}")
            arr = "\n".join(arr)
            emb = discord.Embed(color=3447003, description=f"```fix\n{question[:300]}```\n{arr}")
            emb.set_author(name=f"@{ctx.author.name}", icon_url=ctx.author.display_avatar)
            m = await ctx.channel.send(content=title, embed=emb)
            for index, item in enumerate(ops):
                await m.add_reaction(ALPHABET[index])


async def setup(bot: commands.Bot):
    await bot.add_cog(Mod(bot))