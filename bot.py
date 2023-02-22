# bot.py
import discord
from discord import app_commands
from views import AdminView, AuthView
from utils import db, TOKEN, error_handler

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
    await reset_auth_channel(interaction.channel)
    await interaction.response.send_message("The Auth channel has been generated!", ephemeral=True)

@gen_auth_token.error
async def gen_auth_token_error(interaction, error):
    await error_handler(interaction, error)

@gen_auth_ch.error
async def gen_auth_ch_error(interaction, error):
    await error_handler(interaction, error)

global synced
synced = False

@client.event
async def on_ready():
    global synced
    print(f'{client.user} has connected to Discord!')
    if not synced:
        await cmd.sync()
        synced = True

async def setup_hook():
    client.add_view(AuthView())

client.setup_hook = setup_hook

client.run(TOKEN)
