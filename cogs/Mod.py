from discord.ext import commands
from main import util
import discord

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
    
    @commands.cooldown(1, 8, commands.BucketType.member)
    @commands.bot_has_guild_permissions(manage_messages=True)
    @commands.has_guild_permissions(manage_messages=True)
    @discord.app_commands.describe(amount="The amount of messages to delete", member="Optional filter, the member author to delete the messages")
    @commands.hybrid_command(name="clear", aliases=["purge", "clean"])
    async def clear(self, ctx: commands.Context, amount: int, member: discord.Member = None):
        """Bulk delete X messages in this channel with optional filter"""
        if amount > 100:
            return await util.throw_error(ctx, text="You can't exceed 100 messages")
        elif 1 > amount:
            return await util.throw_error(ctx, text="Invalid amount provide, try with +1")
        if not member:
            messages = await ctx.channel.purge(limit=amount)
            await util.throw_fine(ctx, text=f"**{len(messages)}** message(s) has been deleted successfully!", bold=False)
        else:
            messages = await ctx.channel.purge(limit=amount, check=lambda m: m.author.id == member.id)
            await util.throw_fine(ctx, text=f"**{len(messages)}** message(s) has beel deleted successfully!", bold=False)
    
    @commands.cooldown(1, 10, commands.BucketType.member)
    @commands.bot_has_guild_permissions(kick_members=True)
    @commands.has_guild_permissions(kick_members=True)
    @commands.command(name="kick")
    @discord.app_commands.describe(member="The member to kick", reason="Optional reason")
    async def kick(self, ctx: commands.Context, member: discord.Member, * , reason = "Unknown reason"):
        """Kick a user from this server"""
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
        await member.kick(reason=reason)
        await util.throw_fine(ctx, text=f"**{member.name}#{member.discriminator}** was kicked successfully!")

async def setup(bot: commands.Bot):
    await bot.add_cog(Mod(bot))