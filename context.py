import discord
from discord import app_commands

async def setup(client):
    """Setup all the required context menus"""

    @client.tree.context_menu()
    async def test(interaction: discord.Interaction, message: discord.Message):
        await interaction.response.send_message("Hello there", ephmeral=True)
