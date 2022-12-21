import discord
from discord.ext import commands

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
                await interaction.response.edit_message(embed=self.embed)
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
                await interaction.response.edit_message(embed=self.embed)
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