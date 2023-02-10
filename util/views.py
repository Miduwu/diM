import discord
from discord.ext import commands
from typing import List, Optional
from main import mongodb

class Base(discord.ui.View):
    def __init__(self, *, timeout=30, ctx: commands.Context):
        self.ctx = ctx
        self.message: discord.Message | None = None
        super().__init__(timeout=timeout)
    
    async def on_timeout(self):
        for i in range(0, len(self.children)):
            self.children[i].disabled = True
        await self.message.edit(view=self)
    
    async def interaction_check(self, interaction: discord.Interaction):
        if self.ctx.author.id != interaction.user.id:
            await interaction.response.send_message(content=f'{interaction.user.mention}, this interaction isn\'t for you <:bloboohcry:1011458104782758009>', ephemeral=True)
        return self.ctx.author.id == interaction.user.id
    

class Paginator(discord.ui.View):
    def __init__(self, *, timeout=30, data: list, ctx: commands.Context, embed = None):
        super().__init__(timeout=timeout)
        self.data = data
        self.page = 0
        self.ctx = ctx
        self.message: discord.Message = None
        self.embed = embed
        self.content = None

    async def on_timeout(self):
        for i in range(0, len(self.children)):
            self.children[i].disabled = True
        await self.message.edit(view=self)
    
    async def interaction_check(self, interaction: discord.Interaction):
        if self.ctx.author.id != interaction.user.id:
            await interaction.response.send_message(content=f'{interaction.user.mention}, this interaction isn\'t for you <:bloboohcry:1011458104782758009>', ephemeral=True)
        return self.ctx.author.id == interaction.user.id
    
    def update_item(self, item):
        if self.embed:
            self.embed.description = item
            self.embed.set_footer(text=f'Page: {self.page + 1}/{len(self.data)}')
        else:
            pass
    
    @discord.ui.button(label='Previous', style=discord.ButtonStyle.blurple)
    async def previous(self, interaction: discord.Interaction, button):
        try:
            if 0 >= self.page:
                self.page = len(self.data) - 1
            else:
                self.page -= 1
            self.update_item(self.data[self.page])
            if self.embed:
                await interaction.response.edit_message(embed=self.embed, content=self.content)
            else:
                await interaction.response.edit_message(content=self.content or self.data[self.page])
        except:
            pass
    
    @discord.ui.button(label='Next', style=discord.ButtonStyle.blurple)
    async def next(self, interaction: discord.Interaction, button):
        try:
            if self.page + 1 >= len(self.data):
                self.page = 0
            else:
                self.page += 1
            self.update_item(self.data[self.page])
            if self.embed:
                await interaction.response.edit_message(embed=self.embed, content=self.content)
            else:
                await interaction.response.edit_message(content=self.content or self.data[self.page])
        except:
            pass

class Confirmation(discord.ui.View):
    def __init__(self, *, timeout=30, ctx: commands.Context):
        super().__init__(timeout=timeout)
        self.ctx = ctx
        self.message: discord.Message = None
    
    async def on_timeout(self):
        for i in range(0, len(self.children)):
            self.children[i].disabled = True
        await self.message.edit(view=self)
    
    async def call_me(self, interaction: discord.Interaction):
        await interaction.response.defer()
    
    async def interaction_check(self, interaction: discord.Interaction):
        if self.ctx.author.id != interaction.user.id:
            await interaction.response.send_message(content=f'{interaction.user.mention}, this interaction isn\'t for you <:bloboohcry:1011458104782758009>', ephemeral=True)
        return self.ctx.author.id == interaction.user.id
    
    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.green)
    async def cancel(self, interaction: discord.Interaction, button: discord.Button):
        await interaction.response.defer()
        for i in range(0, len(self.children)):
            self.children[i].disabled = True
        self.children[0].label = 'Cancelled'
        self.children[0].style = discord.ButtonStyle.green
        self.children[1].style = discord.ButtonStyle.gray
        await self.message.edit(view=self)
    
    @discord.ui.button(label='Continue', style=discord.ButtonStyle.red)
    async def _continue(self, interaction: discord.Interaction, button: discord.Button):
        for i in range(0, len(self.children)):
            self.children[i].disabled = True
        self.children[0].style = discord.ButtonStyle.gray
        self.children[1].label = 'Continuing'
        await self.message.edit(view=self)
        await self.call_me(interaction)

class Settings(discord.ui.View):
    def __init__(self, *, ctx: commands.Context, timeout = 180, embed: discord.Embed):
        self.message: discord.Message | None = None
        self.embed = embed
        self.system: str | None = None
        self.ctx = ctx
        super().__init__(timeout=timeout)
    
    async def on_timeout(self):
        for i in range(0, len(self.children)):
            self.children[i].disabled = True
        await self.message.edit(view=self)
    
    async def interaction_check(self, interaction: discord.Interaction):
        if self.ctx.author.id != interaction.user.id:
            await interaction.response.send_message(content=f'{interaction.user.mention}, this interaction isn\'t for you <:bloboohcry:1011458104782758009>', ephemeral=True)
        return self.ctx.author.id == interaction.user.id
    
    @discord.ui.button(label="Enable this system", style=discord.ButtonStyle.green, disabled=True)
    async def enable(self, interaction: discord.Interaction, button: discord.Button):
        await mongodb.set(table="guilds", id=self.ctx.guild.id, path=f"{self.system.lower()}.enabled", value=True)
        self.embed.remove_field(0)
        self.embed.insert_field_at(0, name="Status", value="Enabled")
        self.children[0].disabled = True
        self.children[1].disabled = False
        await interaction.response.edit_message(embed=self.embed, view=self)
    
    @discord.ui.button(label="Disable this system", style=discord.ButtonStyle.red, disabled=True)
    async def disable(self, interaction: discord.Interaction, button: discord.Button):
        await mongodb.delete(table="guilds", id=self.ctx.guild.id, path=f"{self.system.lower()}.enabled")
        self.embed.remove_field(0)
        self.embed.insert_field_at(0, name="Status", value="Disabled")
        self.children[0].disabled = False
        self.children[1].disabled = True
        await interaction.response.edit_message(embed=self.embed, view=self)

    @discord.ui.select(placeholder="Select a system in this server", options=[
        discord.SelectOption(label="Main", description="Home page"),
        discord.SelectOption(label="Welcome", description="Manage the welcome system"),
        discord.SelectOption(label="Leave", description="Manage the leave/goodbye system"),
    ])
    async def callback(self, i: discord.Interaction, select: discord.ui.select):
        VALUE = i.data['values'][0]
        if VALUE == "Main":
            self.embed.clear_fields()
            self.children[0].disabled = True
            self.children[1].disabled = True
            self.embed.title = None
            self.embed.description = f"Thanks for using **{self.ctx.bot.user.name}** tools! You can see a system by using the select menu below this."
            await i.response.edit_message(view=self, embed=self.embed)
        elif VALUE == "Welcome":
            self.embed.clear_fields()
            self.system = "welcome"
            data = await mongodb.get(table="guilds", id=self.ctx.guild.id, path="welcome") or {}
            self.children[0].disabled = data.get("enabled", False) == True
            self.children[1].disabled = not data.get("enabled", False)
            channel = self.ctx.guild.get_channel(data.get("channel")) if data.get("channel", None) else None
            self.embed.title = "Welcome System"
            self.embed.description = f"To see the full commands of this module use `{self.ctx.clean_prefix}help Tools` or `/help Tools`"
            self.embed.add_field(name="Status", value="Enabled" if data.get("enabled", None) else "Disabled")
            self.embed.add_field(name="Channel", value=channel.mention if channel else "Not in cache")
            self.embed.add_field(name="Custom message?", value="True" if data.get("message", None) else "False")
            self.embed.add_field(name="Commands", value="```$Pwelcome channel\n$Pwelcome message\n$Pwelcome preview```".replace("$P", self.ctx.clean_prefix))
            await i.response.edit_message(view=self, embed=self.embed)
        elif VALUE == "Leave":
            self.embed.clear_fields()
            self.system = "leave"
            data = await mongodb.get(table="guilds", id=self.ctx.guild.id, path="leave") or {}
            self.children[0].disabled = data.get("enabled", False) == True
            self.children[1].disabled = not data.get("enabled", False)
            channel = self.ctx.guild.get_channel(data.get("channel")) if data.get("channel", None) else None
            self.embed.title = "Leave System"
            self.embed.description = f"To see the full commands of this module use `{self.ctx.clean_prefix}help Tools` or `/help Tools`"
            self.embed.add_field(name="Status", value="Enabled" if data.get("enabled", None) else "Disabled")
            self.embed.add_field(name="Channel", value=channel.mention if channel else "Not in cache")
            self.embed.add_field(name="Custom message?", value="True" if data.get("message", None) else "False")
            self.embed.add_field(name="Commands", value="```$Pleave channel\n$Pleave message\n$Pleave preview```".replace("$P", self.ctx.clean_prefix))
            await i.response.edit_message(view=self, embed=self.embed)