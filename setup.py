import json
import discord

def init_config(client):

    with open("config.json", "r") as config:
        data = json.load(config)

    if data['MODROLE']:
        pass