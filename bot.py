# bot.py
import os, asyncio
import discord
from syjson import SyJsonpierantonio.dagostino@gmail.com
from dotenv import load_dotenv
load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client(intents=discord.Intents.default())
db = SyJson("db.json")

class g:
    guild = None
    auth_ch_name = "🔐︱auth"

async def action_handler(action, interaction):
    if action["type"] == "role":
        roles = []
        if isinstance(action["role"],list):
            roles = [discord.utils.get(g.guild.roles,name=role) for role in action["role"]]
        else:
            roles = [discord.utils.get(g.guild.roles,name=action["role"])]
        [await interaction.user.add_roles(ele) for ele in roles]
        return f"Authenticated successfully with role {action['role']} :), Welcome to the server!"
    else:
        return "Error: Unknown action 0_0"


class AuthModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Authentication")
        token_input = discord.ui.TextInput(label="Insert the Token")
        self.add_item(token_input)
    
    async def on_submit(self, interaction):
        token = interaction.data["components"][0]["components"][0]["value"]
        if token in db["auth_tokens"]:
            action = db["auth_tokens"][token].var()
            del db["auth_tokens"][token]
            return await interaction.response.send_message(await action_handler(action, interaction), ephemeral=True)
        else:
            await interaction.response.send_message("Token invalid or already used :/", ephemeral=True)

class AuthBtn(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Authenticate", style=discord.ButtonStyle.primary, emoji="🔐")
        
    async def callback(self, interaction):
        await interaction.response.send_modal(AuthModal())

class AuthView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(AuthBtn())

async def reset_auth_channel(channel):
    await channel.set_permissions(g.guild.default_role, send_messages=False, read_messages=True)
    await channel.purge()
    await channel.send("Welcome to the auth channel, please send your auth token here", view=AuthView())
        

async def check_and_create_authchannel():
    for channel in g.guild.channels:
        if channel.name == g.auth_ch_name:
            await reset_auth_channel(channel)
            return channel
    channel = await g.guild.create_text_channel(g.auth_ch_name)
    await reset_auth_channel(channel)
    return channel

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    if len(client.guilds) != 1:
        print(f"This bot is made to be in 1 server, but it's in {len(client.guilds)} servers")
        exit(1)
    db.create("auth_tokens",{})
    g.guild = client.guilds[0]
    await check_and_create_authchannel()
    

client.run(TOKEN)
