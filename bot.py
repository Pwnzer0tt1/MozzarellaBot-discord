# bot.py
import discord
from discord import app_commands
from views import AdminView, AuthView
from utils import db, TOKEN, g, error_handler

client = discord.Client(intents=discord.Intents.default())
    
cmd = app_commands.CommandTree(client)

async def reset_auth_channel(channel):
    await channel.set_permissions(g.guild.default_role, send_messages=False, read_messages=True)
    await channel.purge()
    await channel.send("Welcome to the auth channel, please send your auth token here", view=AuthView())
    

@cmd.command(name="admin", description="Admin commands")
@app_commands.default_permissions(administrator=True)
@app_commands.checks.has_permissions(administrator=True)
async def gen_auth_token(interaction):
    await interaction.response.send_message("Click a button to activate an admin function", view=AdminView(), ephemeral=True)

@cmd.command(name="regen_auth_channel", description="Regenerate the auth channel")
@app_commands.default_permissions(administrator=True)
@app_commands.checks.has_permissions(administrator=True)
async def gen_auth_ch(interaction):
    await check_and_create_authchannel()
    await interaction.response.send_message("The Auth channel hash been regenerated!", ephemeral=True)

@gen_auth_token.error
async def gen_auth_token_error(interaction, error):
    await error_handler(interaction, error)

@gen_auth_ch.error
async def gen_auth_ch_error(interaction, error):
    await error_handler(interaction, error)

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
    if not g.synced:
        await cmd.sync()
        g.synced = True

async def setup_hook():
    client.add_view(AuthView())

client.setup_hook = setup_hook

client.run(TOKEN)
