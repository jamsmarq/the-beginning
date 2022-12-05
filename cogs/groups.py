import discord
from discord import app_commands
from typing import Optional
import mimetypes

import views
import utils

class Message(app_commands.Group):
    """send a message to the specified channel"""
    def __init__(self, *, name="message", client, database):
        super().__init__(name=name)
        self.client = client
        self.database = database.find_one({"module": "modrole"})
        self.responses = {
            0: ":blue_circle: Please send the message to be posted:",
            1: ":one: Please send the embed **title**:",
            2: ":two: Please send the embed **message**:",
            3: ":green_circle: The message is successfully posted.",
            4: ":red_circle: Missing permission in the channel.",
        }

    @app_commands.command()
    @app_commands.describe(channel = 'Channel you want the message to be posted')
    async def normal(self, interaction: discord.Interaction, channel: discord.TextChannel):
        """send a normal message to a channel"""

        data_conf = utils.read_config()
        cancel_view = views.CancelView()

        embed = discord.Embed(description=self.responses[0], colour=discord.Colour.blue())
        await interaction.response.send_message(embed=embed, ephemeral=True, view=cancel_view)
        
        def check(message):
            return message.author == interaction.user and message.channel == interaction.channel

        message = await self.client.wait_for("message", check=check, timeout=30)

        try:
            if cancel_view.cancel:
                pass
            else:
                await message.delete()
                try:
                    sent = await channel.send(message.content)
                    data_conf["MESSAGE"]["normal"][sent.id] = sent.content
                    utils.write_config(data_conf)

                    embed = discord.Embed(description=self.responses[3], colour=discord.Colour.brand_green())
                    await interaction.edit_original_response(embed=embed, view=None)
                except discord.Forbidden:
                    embed = discord.Embed(description=self.responses[4], colour=discord.Colour.brand_red())
                    await interaction.edit_original_response(embed=embed, view=None)
                     
        except asyncio.TimeoutError:
            await interaction.edit_original_response(embed=embed)

    @app_commands.command()
    @app_commands.describe(
        channel = 'Channel you want the embed to be posted',
        image = "Upload an image for the message (placed below)",
    )
    async def embed(self, interaction: discord.Interaction, channel: discord.TextChannel, image: Optional[discord.Attachment]):        
        """send an embed message to a channel"""
        def check(message):
            return message.author == interaction.user and message.channel == interaction.channel
 
        data_conf = utils.read_config()
        cancel_view = views.CancelView()

        embed = discord.Embed(description=self.responses[1], colour=discord.Colour.blue())
        await interaction.response.send_message(embed=embed, ephemeral=True, view=cancel_view) 

        # Get the embed title
        title = await self.client.wait_for("message", check=check, timeout=30)                                    
        if cancel_view.cancel:
            pass
        else:
            await title.delete()

            embed = discord.Embed(description=self.responses[2], colour=discord.Colour.blue())
 
            await interaction.edit_original_response(embed=embed)
                
            # Get the embed message
            description = await self.client.wait_for("message", check=check, timeout=30)

            if cancel_view.cancel:
                pass
            else:
                await description.delete()

                # Initialize the embed object         
                embed = discord.Embed(title=title.content, description=description.content, colour=discord.Colour.brand_green())
            
                if image:
                    embed.set_image(url=image.url)
            
                # Send the embed to the specified channel
                try:
                    sent = await channel.send(embed=embed)

                    data_conf["MESSAGE"]["embed"][sent.id] = {
                        "title": title.content,
                        "description": description.content,
                        "image": image.url if image is not None else None
                    }
                    utils.write_config(data_conf)
                        
                    embed = discord.Embed(description=self.responses[3], colour=discord.Colour.brand_green())
                       
                    await interaction.edit_original_response(embed=embed, view=None)
                except discord.Forbidden:
                    embed = discord.Embed(description=self.responses[4], colour=discord.Colour.brand_red())
                    await interaction.edit_original_response(embed=embed, view=None)
   
class Modrole(app_commands.Group):
    """manage server moderator role/s"""
    def __init__(self, *, name="modrole", client, database):
        super().__init__(name=name)
        self.client = client
        self.database = database
        self.key = {"module": "modrole"}

    @app_commands.command()
    @app_commands.describe(
        role = "role you want to the modrole list",
    )
    async def add(self, interaction: discord.Interaction, role: discord.Role):
        """add a role to the modrole list"""
        self.database.bot_modules.update_one(self.key, {"$set": {"status": True}})

        if role.id in data_conf["MODROLE"]["roles"]:
            embed = discord.Embed(description=":green_circle: Role is already added to the list.", colour=discord.Colour.brand_green())
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            self.database.bot_modules.update_one(self.key, {"$set": {"roles": [role.id, ]}})

            embed = discord.Embed(description=":green_circle: Role is successfully added to the list.", colour=discord.Colour.brand_green())
            await interaction.response.send_message(embed=embed, ephemeral=True)
        
    @app_commands.command()
    @app_commands.describe(
        role = "role you want to remove from moderole/s",
    )
    async def remove(self, interaction: discord.Interaction, role: discord.Role):
        """remove a role from the modrole list"""
        data_conf = utils.read_config()
        
        if role.id in data_conf["MODROLE"]["roles"]:
            data_conf["MODROLE"]["roles"].remove(role.id)
            utils.write_config(data_conf)

            embed = discord.Embed(description=":green_circle: Role is successfully removed from the list.", colour=discord.Colour.brand_green())
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(description=":red_circle: Role is not on the list thus cannot be removed.", colour=discord.Colour.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)
        
class Sticky(app_commands.Group):
    """manage sticky message on the server"""
    def __init__(self, *, name="sticky", client):
        super().__init__(name=name)
        self.client = client
        self.responses = {
            0: ":blue_circle: Please send the message you want to stick:",
            1: ":green_circle: The message is successfully sticked",
            2: ":yellow_circle: The sticky command has been cancelled",
            3: ":red_circle: Missing required permission on the channel",
            4: ":yellow_circle: Channel already have a sticky message",
            5: ":yellow_circle: Channel have no sticky message attached",
            6: ":green_circle: The sticky message has been deleted"
        }

 
    @staticmethod
    # [] fix KeyError: 'last_message' exception
    async def check_sticky(client, message):
        data_conf = utils.read_config()

        if data_conf["STICKY"]["status"] is False or str(message.channel.id) not in data_conf["STICKY"]["sticky"].keys() or message.id == data_conf["STICKY"]["sticky"][str(message.channel.id)]["last_message"]:
            return None

        # sticky bot functionality
        last_message_id = data_conf["STICKY"]["sticky"][str(message.channel.id)]["last_message"]

        if message.author == client.user or message.id == last_message_id:
            return None
        else:
            async for message in message.channel.history(limit=5):
                if message.id == last_message_id:
                    try:
                        await message.delete()
                    except discord.NotFound:
                        continue 

            content = data_conf["STICKY"]["sticky"][str(message.channel.id)]["content"]

            embed = discord.Embed(description=content, title="Sticky Message:", colour=discord.Colour.blue())

            s_message = await message.channel.send(embed=embed)

            data_conf["STICKY"]["sticky"][str(message.channel.id)]["last_message"] = s_message.id
            utils.write_config(data_conf)

    @app_commands.command()
    @app_commands.describe(
        channel = "channel to send the sticky message",
    )
    async def send(self, interaction: discord.Interaction, channel: discord.TextChannel):
        """send a sticky message to a channel"""

        def check(message):
            return message.author == interaction.user and message.channel == interaction.channel
 
        data_conf = utils.read_config()
        cancel_view = views.CancelView()
 
        if str(channel.id) in data_conf["STICKY"]["sticky"].keys():
            embed = discord.Embed(description=self.responses[4], colour=discord.Colour.yellow())
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(description=self.responses[0], colour=discord.Colour.blue())
            await interaction.response.send_message(embed=embed, ephemeral=True, view=cancel_view)
 
            message = await self.client.wait_for("message", check=check, timeout=30)                                    

            if cancel_view.cancel:
                embed = discord.Embed(description=self.responses[2], colour=discord.Colour.blue())
                await interaction.edit_original_response(embed=embed, view=None)
            else:
                if data_conf["STICKY"]["status"] is False:
                    data_conf["STICKY"]["status"] = True
                    utils.write_config(data_conf)

                data_conf["STICKY"]["sticky"][str(channel.id)] = {"content": message.content}
                utils.write_config(data_conf)

                await message.delete()

                eformat = discord.Embed(description=message.content, title="Sticky Message:", colour=discord.Colour.blue())
                message = await channel.send(embed=eformat)

                data_conf["STICKY"]["sticky"][str(channel.id)]["last_message"] = message.id
                utils.write_config(data_conf)
                
                embed = discord.Embed(description=self.responses[1], colour=discord.Colour.brand_green())
                await interaction.edit_original_response(embed=embed, view=None)

    # [] be mindful of the 3-seconds interaction response time
    @app_commands.command()
    @app_commands.describe(
        channel = "channel of the sticky message to edit",
    )
    async def delete(self, interaction: discord.Interaction, channel: discord.TextChannel):
        """delete a sticky message from a channel"""
        data_conf = utils.read_config()
 
        if str(channel.id) in data_conf["STICKY"]["sticky"].keys():
            try:
                async for message in channel.history(limit=5):
                    if message.id == data_conf["STICKY"]["sticky"][str(channel.id)]["last_message"]:
                        try:
                            await message.delete()
                        except discord.NotFound:
                            continue 
            except discord.Forbidden:
                embed = discord.Embed(description=self.responses[3], colour=discord.Colour.brand_red())
                await interaction.response.send_message(embed=embed)
            else:
                del data_conf["STICKY"]["sticky"][str(channel.id)]

                if len(data_conf["STICKY"]["sticky"]) == 0 and data_conf["STICKY"]["status"]:
                    data_conf["STICKY"]["status"] = False

                utils.write_config(data_conf)
    
                embed = discord.Embed(description=self.responses[6], colour=discord.Colour.brand_green())
                await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(description=self.responses[5], colour=discord.Colour.yellow())
            await interaction.response.send_message(embed=embed, ephemeral=True)
 
class Channel(app_commands.Group):
    """create various special-purpose channels"""
    def __init__(self, *, name="channel", client):
        super().__init__(name=name)
        self.client = client
        self.responses = {
            1: ":green_circle: Channel is successfully converted to picsonly",
            2: ":yellow_circle: Channel is already a pictures-only channel",
        }

    # [] don't delete bot's sticky message on the channel
    @staticmethod
    async def check_visualmedia(client, message):
        data_conf = utils.read_config()

        if message.channel.id not in data_conf["CHANNEL"]["visualmedia"]:
            return None
        
        mime_types = ['image/jpeg', 'image/png', 'image/gif', 'video/mp4', 'video/webm', 'video/quicktime']

        if message.id == data_conf["STICKY"]["sticky"]["1036310677180121199"]["last_message"]:
            return None

        if len(message.attachments) == 0:
            await message.delete()
        else:
            for attachment in message.attachments:
                filetype = mimetypes.guess_type(attachment.url, strict=False)
                if filetype[0] is not None and filetype[0] not in mime_types:
                    await message.delete()

    @app_commands.command()
    @app_commands.describe(
        channel = "channel to be converted to visual-media-only",
    )
    async def visualmedia(self, interaction: discord.Interaction, channel: discord.TextChannel):
        """create a visual-media-only channel"""
        data_conf = utils.read_config()

        if channel.id in data_conf["CHANNEL"]["visualmedia"]:
            embed = discord.Embed(description=self.responses[2], colour=discord.Colour.yellow())
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            data_conf["CHANNEL"]["visualmedia"].append(channel.id)
            utils.write_config(data_conf)

            embed = discord.Embed(description=self.responses[1], colour=discord.Colour.yellow())
            await interaction.response.send_message(embed=embed, ephemeral=True)