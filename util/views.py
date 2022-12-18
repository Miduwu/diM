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

    async def on_timeout(self):
        for i in range(0, len(self.children)):
            self.children[i].disabled = True
        await self.message.edit(view=self)
    
    async def interaction_check(self, interaction: discord.Interaction):
        if self.ctx.author.id != interaction.user.id:
            await interaction.response.send_message(content=f'{interaction.user.mention}, this interaction isn\'t for you <:bloboohcry:1011458104782758009>', ephemeral=True)
        return self.ctx.author.id == interaction.user.id
    
    def update_item(self, item):
        self.embed.description = item
        self.embed.set_footer(text=f'Page: {self.page + 1}/{len(self.data)}')
    
    @discord.ui.button(label='Previous', style=discord.ButtonStyle.blurple)
    async def previous(self, interaction: discord.Interaction, button):
        try:
            if 0 >= self.page:
                self.page = len(self.data) - 1
            else:
                self.page -= 1
            if self.embed:
                self.update_item(self.data[self.page])
                await interaction.response.edit_message(embed=self.embed)
            else:
                await interaction.response.edit_message(content=self.data[self.page])
        except:
            pass
    
    @discord.ui.button(label='Next', style=discord.ButtonStyle.blurple)
    async def next(self, interaction: discord.Interaction, button):
        try:
            if self.page + 1 >= len(self.data):
                self.page = 0
            else:
                self.page += 1
            if self.embed:
                self.update_item(self.data[self.page])
                await interaction.response.edit_message(embed=self.embed)
            else:
                await interaction.response.edit_message(content=self.data[self.page])
        except:
            pass