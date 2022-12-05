import discord
import logging
import os
import dotenv
import json
from discord import app_commands
import asyncio

import setup
import context
import utils
import database
import pymongo
from cogs import general
from cogs import modrole

class MyClient(discord.Client):
    def __init__(self, *, activity: discord.Activity, intents: discord.Intents, database):
        super().__init__(intents=intents, activity=activity)
        # A CommandTree is a special type that holds all the application command state required to make it work.
        # Whenever you want to work with application commands, your tree is used to store and work with them.
        self.tree = app_commands.CommandTree(self)

        # Setup the database initial configs
        self.database = database
        
    async def setup_hook(self):
        """Setup necessary things for the program""" 
        # Set client activity status

        # Initialize the user-defined commands
        self.tree.add_command(modrole.modrole)
        self.tree.add_command(general.about)
        self.tree.add_command(general.activity)
        self.tree.add_command(general.info)
        self.tree.add_command(general.ping)
        self.tree.add_command(general.purge)
        # self.tree.add_command(groups.Modrole(client=self, database=self.database))

        # Initialize all the context menus
        # await context.setup(self)
    
        # Syncs the application commands to Discord
        await self.tree.sync()

    async def on_ready(self):
        print(f'Logged in as {self.user}')

    async def on_message(self, message):
        pass

    async def on_raw_message_delete(self, message):
        pass

# Set up the database for data
database = database.setup_database()

# Set the initial activity status
temp = database.bot_modules.find_one({"module": "activity"})
activity = discord.Game(temp["message"] if temp["status"] else "/activity to change this")

# Iniatialize the intents for the bot
intents = discord.Intents.all()

# Instantiate client program
client = MyClient(activity=activity, intents=intents, database=database)
# handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode='w')

if __name__ == '__main__':
    # dotenv.load_dotenv()
    client.run("TOKEN HERE")