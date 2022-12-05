import discord
import asyncio
import utils

from discord import app_commands
from typing import Optional

@app_commands.command()
@app_commands.describe(
    message = "enter custom activity status message",
)
async def activity(interaction: discord.Interaction, message: str):
    """customize the bot's activity presence"""   
    await interaction.response.defer(ephemeral=True)

    database = interaction.client.database.bot_modules
    activity = discord.Game(message)
    query = {"module": "activity"}

    try:
        if database.find_one(query)["status"] is not True:
            database.update_one(query, {"$set": {"status": True}})

        await interaction.client.change_presence(activity=activity)
    except discord.DiscordException as error:        
        embed = discord.Embed(description=f""":red_circle: Something went wrong! Please send a report to the developer.
        
        Error Message:
        {error}
        """, colour=discord.Colour.red())
        await interaction.followup.send(embed=embed, ephemeral=True)
    else:
        database.update_one(query, {"$set": {"message": message}})

        embed = discord.Embed(description=":green_circle: The Bot's activity status successfully changed.", colour=discord.Colour.brand_green())
        await interaction.followup.send(embed=embed, ephemeral=True)

@app_commands.command()
async def about(interaction: discord.Interaction):
    """return information about the bot"""
    embed = discord.Embed(description="still in development", colour=discord.Colour.yellow())
    await interaction.response.send_message(embed=embed, ephemeral=True)
    
@app_commands.command()
async def info(interaction: discord.Interaction):
    """return information about the server"""
    embed = discord.Embed(description="still in development", colour=discord.Colour.yellow())
    await interaction.response.send_message(embed=embed, ephemeral=True)

@app_commands.command()
async def ping(interaction: discord.Interaction):
    """replies with Pong! and the bot's latency"""
    description = f":ping_pong: Pong! The bot is running on **{round(interaction.client.latency * 1000)}ms** latency."
                
    embed = discord.Embed(description=description, colour=discord.Colour.brand_green())
    await interaction.response.send_message(embed=embed, ephemeral=True)

@app_commands.command()
@app_commands.describe(
    count = "number of messages to delete (limit: 1000)",
    channel = "delete message/s from this channel",
)
async def purge(interaction: discord.Interaction, count: int, channel: Optional[discord.TextChannel]):
    """delete the message/s on a channel"""
    await interaction.response.defer(ephemeral=True)

    channel = channel if channel is not None else interaction.channel

    try:
        message_list = await channel.purge(limit=count)
    except discord.Forbidden:
        embed = discord.Embed(description=f":red_circle: The bot lacks proper permission/s on the channel", colour=discord.Colour.brand_red())
        await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        if len(message_list) == 0:
            embed = discord.Embed(description=f":red_circle: There is nothing to delete on the channel", colour=discord.Colour.brand_red())
            await interaction.followup.send(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(description=f":green_circle: Successfully found and deleted **{len(message_list)}** messages", colour=discord.Colour.brand_green())
            await interaction.followup.send(embed=embed, ephemeral=True)

