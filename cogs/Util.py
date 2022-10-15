import discord
from discord.ext import commands
from main import util

class Util(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
    
    @commands.command(name='avatar', aliases=['av', 'pfp'])
    async def avatar(self, ctx: commands.Context, user: discord.User = None):
        if user is None:
            user = ctx.author
        embed = discord.Embed(colour=3447003)
        embed.set_author(name=f'{user.name}#{user.discriminator}', icon_url=user.display_avatar)
        embed.set_image(url=str(user.display_avatar).replace('.webp', '.png'))
        await ctx.send(embed=embed)
    
    @commands.command(name='user', aliases=['userinfo', 'whois'])
    async def user(self, ctx: commands.Context, user: discord.User = None):
        if user is None:
            user = ctx.author
        member = ctx.guild.get_member(user.id)
        emb = discord.Embed(colour=3447003)
        emb.set_author(name=f'{user.name}#{user.discriminator}', icon_url=user.display_avatar)
        emb.set_thumbnail(url=user.display_avatar)
        emb.description = f'**¬ Tag:** {user.name}#{user.discriminator}\n**¬ ID:** `{user.id}`\n**¬ Highest role:** {member.top_role.mention if member else "~~None~~"}\n**¬ Created:** <t:{round(user.created_at.timestamp())}:D>\n**¬ Joined:** <t:{round(member.joined_at.timestamp())}:D>\n\n**¬ Roles [{len(member.roles) if member else "~~0~~"}]:**\n{", ".join(list(map(lambda r: r.mention, member.roles))) if member else "~~None~~"}'
        await ctx.send(embed=emb)
    
    @commands.command(name='server', aliases=['serverinfo'])
    async def server(self, ctx: commands.Context):
        emb = discord.Embed(colour=3447003)
        emb.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
        emb.add_field(name='<:photoblob:1011458149653426226> '+ctx.guild.name, value=f'**¬ ID:** `{ctx.guild.id}`\n**¬ Owner:** <@{ctx.guild.owner_id}>\n**¬ Created:** <t:{round(ctx.guild.created_at.timestamp())}:D>')
        emb.add_field(name='<:blobhero:1011785174767382568> Staticts', value=f'**¬ Members:** {ctx.guild.member_count}\n**¬ Roles:** {len(ctx.guild.roles)}\n**¬ Channels:** {len(ctx.guild.channels)} (**Text:** {len(ctx.guild.text_channels)}, **Voice:** {len(ctx.guild.voice_channels)}, **Other:** {len(ctx.guild.channels) - len(ctx.guild.text_channels) - len(ctx.guild.voice_channels)})', inline=False)
        await ctx.send(embed=emb)
    
    @commands.command(name='servericon', aliases=['icon'])
    async def icon(self, ctx: commands.Context):
        if not ctx.guild.icon:
            return await util.throw_error(ctx, text="This server **doesn't** have an icon yet.", bold=False)
        embed = discord.Embed(colour=3447003)
        embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon.url)
        embed.set_image(url=ctx.guild.icon.url.replace('.webp', '.png'))
        await ctx.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Util(bot))