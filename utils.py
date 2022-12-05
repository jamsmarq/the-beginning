import json
import discord

def u_emoji(name, client):
    client.server_emojis = list(client.emojis)

    for i in client.server_emojis:
        if i.name == name:
            return client.get_emoji(i.id)

    return None

def write_config(data_conf):
    with open("config.json", "w", encoding="utf-8") as config:
        json.dump(data_conf, config, indent=4)

def read_config():
    with open("config.json", "r") as config:
        return json.load(config)