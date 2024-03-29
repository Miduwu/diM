from discord.ext import commands
from wordcloud import WordCloud
from main import util
import discord, io, re, random, os

class Funny(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.api_domain = "https://api.munlai.me"
    
    @commands.hybrid_group(name="image", aliases=["img"])
    async def images(self, ctx):
        """Apply some filters in your images"""
        ...
    
    @commands.cooldown(1, 7, commands.BucketType.member)
    @images.command(name="drake")
    @discord.app_commands.describe(yes_text="Something that Drake would approve", no_text="Something that Drake wouldn't approve")
    async def drake(self, ctx: commands.Context, yes_text: str, no_text: str):
        """Make a drake image"""
        await ctx.defer()
        b = await util.download_bytes(f"https://api.alexflipnote.dev/drake?top={no_text[:50]}&bottom={yes_text[:50]}")
        await ctx.send(file=discord.File(fp=b, filename="drake.png"))
    
    @commands.cooldown(1, 7, commands.BucketType.member)
    @images.command(name="discordjs")
    @discord.app_commands.describe(text="Something for the discord.js logo")
    async def discordjs(self, ctx: commands.Context, text: str):
        """Make a discordjs logo image"""
        b = await util.download_bytes(f"{self.api_domain}/image/discordjs?text={text[0:25]}")
        await ctx.send(file=discord.File(fp=b, filename="discordjs.png"))
    
    @commands.cooldown(1, 7, commands.BucketType.member)
    @images.command(name="rainbow")
    @discord.app_commands.describe(user="Select a user")
    async def rainbow(self, ctx: commands.Context, user: discord.User = None):
        """Make the avatar in rainbow"""
        if user is None:
            user = ctx.author
        b = await util.download_bytes(f"{self.api_domain}/image/gay?image={user.display_avatar}")
        await ctx.send(file=discord.File(fp=b, filename="rainbow.png"))

    @commands.cooldown(1, 7, commands.BucketType.member)
    @images.command(name="deepfry")
    @discord.app_commands.describe(user="Select a user")
    async def deepfry(self, ctx: commands.Context, user: discord.User = None):
        """Make a image deepfry"""
        if user is None: 
            user = ctx.author
        b = await util.download_bytes(f"{self.api_domain}/image/deepfry?image={user.display_avatar}")
        await ctx.send(file=discord.File(fp=b, filename="deepfry.png"))

    @commands.cooldown(1, 7, commands.BucketType.member)
    @images.command(name="spotify")
    @discord.app_commands.describe(user="Select a user")
    async def thisis(self, ctx: commands.Context, user: discord.User = None):
        """Make a this is spotify image card"""
        if user is None:
            user = ctx.author
        b = await util.download_bytes(f"{self.api_domain}/image/thisis?image={user.display_avatar}&text={user.name}")
        await ctx.send(file=discord.File(fp=b, filename="thisis.png"))

    @commands.cooldown(1, 7, commands.BucketType.member)
    @images.command(name="beautiful")
    @discord.app_commands.describe(user="Select a user")
    async def beautiful(self, ctx: commands.Context, user: discord.User = None):
        """Make a image beautiful"""
        if user is None:
            user = ctx.author
        b = await util.download_bytes(f"{self.api_domain}/image/beautiful?image={user.display_avatar}")
        await ctx.send(file=discord.File(fp=b, filename="beautiful.png"))
    
    @commands.cooldown(1, 7, commands.BucketType.member)
    @images.command(name="communism")
    @discord.app_commands.describe(user="Select a user")
    async def communism(self, ctx: commands.Context, user: discord.User = None):
        """Make a communism image"""
        if user is None:
            user = ctx.author
        b = await util.download_bytes(f"{self.api_domain}/image/communist?image={user.display_avatar}")
        await ctx.send(file=discord.File(fp=b, filename="communsim.png"))
    
    @commands.cooldown(1, 7, commands.BucketType.member)
    @images.command(name="sus")
    @discord.app_commands.describe(user="Select a user")
    async def sus(self, ctx: commands.Context, user: discord.User = None):
        """Make an among us image"""
        if user is None:
            user = ctx.author
        b = await util.download_bytes(f"{self.api_domain}/image/sus?image={user.display_avatar}")
        await ctx.send(file=discord.File(fp=b, filename="sus.png"))
    
    @commands.cooldown(1, 7, commands.BucketType.member)
    @images.command(name="pixel")
    @discord.app_commands.describe(user="Select a user")
    async def pixel(self, ctx: commands.Context, user: discord.User = None):
        """Make a pixel image"""
        if user is None:
            user = ctx.author
        b = await util.download_bytes(f"{self.api_domain}/image/pixel?image={user.display_avatar}&amount=10")
        await ctx.send(file=discord.File(fp=b, filename="pixel.png"))

    @commands.hybrid_group(name="text")
    async def texts(self, ctx):
        """Beautify your text using some subcommand"""
        ...
    
    @texts.command(name="reverse")
    @discord.app_commands.describe(text="The text to reverse")
    async def reverse(self, ctx: commands.Context, *, text: str):
        """Reverse your text"""
        await ctx.send(content=text[::-1])
    
    @texts.command(name="choose")
    @discord.app_commands.describe(options="Please separate them by a \"|\". Example: option 1 | option 2", how_many="How many of them i will choose?")
    async def choose(self, ctx: commands.Context, how_many: int, *, options: str):
        """Choose some options from provided"""
        ops = options.split("|")
        if len(ops) < 2:
            return await util.throw_error(ctx, text="Options length must be 2 at less")
        await ctx.send(",".join(util.choice(ops, how_many)))
    
    @texts.command(name="emojify", aliases=["emoji"])
    @discord.app_commands.describe(text="The text to convert to emojis")
    async def emojify(self, ctx: commands.Context, *, text: str):
        """Convert a text to emojis"""
        m = re.sub("([a-zA-Z])",":regional_indicator_\\1:".lower(), text.replace(" ", "  "))
        await ctx.send(m[:2000 - len(":regional_indicator_x:")])
    
    @discord.app_commands.describe(member="Optional member to use its avatar")
    @commands.hybrid_command(name="meme")
    async def meme(self, ctx: commands.Context, *, line: str = None):
        """Make a meme using a member avatar"""
        if not ctx.interaction:
            await ctx.channel.typing()
        expected = ctx.message.mentions[0].display_avatar if len(ctx.message.mentions) else ctx.author.display_avatar
        line = line.replace(ctx.message.mentions[0].mention, "") if len(ctx.message.mentions) else line
        line1 = None
        line2 = None
        if "|" in line:
            split = line.split("|")
            line1 = split[0]
            line2 = split[1]
        else:
            split = line.split()
            if len(split) > 2:
                line1 = " ".join(split[:2])
                line2 = " ".join(split[2:])
            else:
                line1 = split[0]
                if len(split) > 1:
                    line2 = " ".join(split[1:])
                    if line2 is None:
                        line2 = " "
        if not line2:
            return await util.throw_error(ctx, text="You have to provide 2 lines for the meme")
        await ctx.defer()
        rep = [["-","--"],["_","__"],["?","~q"],["%","~p"],[" ","%20"],["''","\""]]
        for s in rep:
            line1 = line1.replace(s[0],s[1])
            line2 = line2.replace(s[0],s[1])
        url = f"http://memegen.link/custom/{line1}/{line2}.jpg?alt={expected}"
        b = await util.download_bytes(url)
        await ctx.send(file=discord.File(fp=b, filename="meme.jpg"))
    
    @commands.cooldown(1, 10, commands.BucketType.channel)
    @commands.hybrid_command(name="wordcloud", aliases=["wc"])
    async def wordcloud(self, ctx: commands.Context):
        """Make an image with the cache messages"""
        await ctx.defer()
        if not ctx.interaction:
            await ctx.message.channel.typing()
        text = ""
        async for m in ctx.channel.history(limit=80):
            text += m.content + " "
        wc = WordCloud().generate(text)
        image = wc.to_image()
        imgbytes = io.BytesIO()
        image.save(imgbytes, format="PNG")
        imgbytes.seek(0)
        await ctx.send(file=discord.File(fp=imgbytes, filename="worcloud.png"))

    @commands.cooldown(1, 10, commands.BucketType.channel)
    @commands.hybrid_command(name="ship")
    @discord.app_commands.describe(user1="user1", user2="user2")
    async def ship(self, ctx: commands.Context, user1: discord.Member, user2: discord.Member = None):
        """Ship two members"""
        await ctx.defer()
        if user2 is None:
            user2 = user1
            user1 = ctx.author
        r = random.randint(1, 101)
        embed = discord.Embed(colour=3447003)
        embed.description = f"**{user1.name}** & **{user2.name}** are **{r}%** compatible! :heart:"
        embed.set_image(url=f"{self.api_domain}/image/ship?image1={user1.display_avatar}&image2={user2.display_avatar}&type={1 if r > 50 else 2}")
        await ctx.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Funny(bot))
