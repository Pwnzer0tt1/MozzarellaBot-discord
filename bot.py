from dotenv import load_dotenv
load_dotenv()
# bot.py
import discord, asyncio
from discord import app_commands
from views import AdminView, AuthView
from utils import TOKEN, error_handler
from db import init_db

client = discord.Client(intents=discord.Intents.default())
    
cmd = app_commands.CommandTree(client)

async def reset_auth_channel(channel):
    await channel.set_permissions(channel.guild.default_role, send_messages=False, read_messages=True)
    await channel.purge()
    await channel.send("Welcome to the auth channel, please send your auth token here", view=AuthView())
    

@cmd.command(name="admin", description="Admin commands")
@app_commands.default_permissions(administrator=True)
@app_commands.checks.has_permissions(administrator=True)
async def gen_auth_token(interaction):
    await interaction.response.send_message("Click a button to activate an admin function", view=AdminView(), ephemeral=True)

@cmd.command(name="generate_auth_channel", description="Create the auth channel in the current channel")
@app_commands.default_permissions(administrator=True)
@app_commands.checks.has_permissions(administrator=True)
async def gen_auth_ch(interaction):
    await interaction.response.defer()
    await reset_auth_channel(interaction.channel)
    

@gen_auth_token.error
async def gen_auth_token_error(interaction, error):
    await error_handler(interaction, error)

@gen_auth_ch.error
async def gen_auth_ch_error(interaction, error):
    await error_handler(interaction, error)


async def init_bot():
    await asyncio.gather(
        cmd.sync(),
        init_db()
    )

global synced
synced = False

@client.event
async def on_ready():
    global synced
    print(f'{client.user} has connected to Discord!')
    if not synced:
        await init_bot()
        synced = True



async def setup_hook():
    client.add_view(AuthView())

client.setup_hook = setup_hook

client.run(TOKEN)
