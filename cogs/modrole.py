import discord
import main

import traceback
import utils
import database

class AddSelect(discord.ui.Select):
    def __init__(self, roles):
        options = [discord.SelectOption(label=x.name, description=str(x.id)) for x in roles if x.name != "@everyone"]
        super().__init__(placeholder="Select an option", options=options)

    async def callback(self, interaction: discord.Interaction):
        if database.get_module_data(modrole)["status"] is not True:
            database.update_one({"module": "modrole"}, {"$set": {"status": True}})

        database.update_one({"module": "modrole"}, {"$push": {"array": message}})

        embed = discord.Embed(description=self.values[0], colour=discord.Colour.brand_green())
        await interaction.response.edit_message(embed=embed, attachments=[], view=None)

class AddSelectView(discord.ui.View):
    def __init__(self, *, timeout=180, roles):
        super().__init__(timeout=timeout)
        self.add_item(AddSelect(roles=roles))

class ModroleView(discord.ui.View):
    def __init__(self, *, timeout=180):
        super().__init__(timeout=timeout)

    @discord.ui.button(label="ADD", emoji="➕", style=discord.ButtonStyle.primary)
    async def add(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="Hello there", view=AddSelectView(roles=interaction.guild.roles))

    @discord.ui.button(label="REMOVE", emoji="➖", style=discord.ButtonStyle.success)
    async def remove(self, interaction: discord.Interaction, button: discord.ui.Button):
        pass

    @discord.ui.button(label="CLOSE", emoji="❌", style=discord.ButtonStyle.danger)
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(description=f":green_circle: The command window has been successfully closed", colour=discord.Colour.brand_green())
        await interaction.response.edit_message(embed=embed, attachments=[], view=None)

@discord.app_commands.command()
async def modrole(interaction: discord.Interaction):
    """management of server moderator role/s"""

    title = "Moderator role/s module setting"
    description = """The `modrole` command manages the server moderator role/s that can use the bot's mods-only commands.
    """
    embed_img = discord.File("assets/embed_line.png", filename="embed_line.png")

    embed = discord.Embed(title=title, description=description, colour=discord.Colour.brand_green())
    embed.set_image(url="attachment://embed_line.png")

    await interaction.response.send_message(file=embed_img, embed=embed, ephemeral=True, view=ModroleView())