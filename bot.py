# bot.py
import os, discord, secrets, asyncio, traceback
from syjson import SyJson
from dotenv import load_dotenv
from discord import app_commands
load_dotenv()

"""
Create Admin Function to revoke a token or a list of tokens
Create the function to send via email the tokens
"""

TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client(intents=discord.Intents.default())
db = SyJson("db.json")
class g:
    guild = None
    auth_ch_name = "🔐︱auth"
    synced = False
    
cmd = app_commands.CommandTree(client)


gen_token_lock = asyncio.Lock()
async def gen_token():
    async with gen_token_lock:
        while True:
            tk = secrets.token_hex(16)
            if tk not in db["auth_tokens"]:
                db["auth_tokens"][tk] = None
                return tk

async def add_token_role(roles):
    roles = list(map(int, roles))
    tk = await gen_token()
    db["auth_tokens"][tk] = {"role":roles,"type":"role"}
    return tk

class GenTokensModal(discord.ui.Modal):
    def __init__(self, roles):
        super().__init__(title="Generate Tokens")
        self.roles = roles
        self.add_item(discord.ui.TextInput(label="Insert the Amount"))
        
    async def on_submit(self, interaction):
        amount = interaction.data["components"][0]["components"][0]["value"]
        if not isinstance(amount,str) or not amount.isdigit():
            await interaction.response.edit_message("Please insert a valid amount")
            return
        tokens = [await add_token_role(self.roles) for _ in range(int(amount))]
        token_text = "\n".join(tokens)
        await interaction.response.edit_message(content=f"Here are your generated tokens:\n```\n{token_text}\n```\nSave the tokens before closing this message!", view=None)

class GenTokensView(discord.ui.View):
    def __init__(self, roles):
        super().__init__()
        self.roles = roles
        self.btn = discord.ui.Button(label="Open", style=discord.ButtonStyle.primary)
        self.add_item(self.btn)
        async def callback(interaction):
            await interaction.response.send_modal(GenTokensModal(roles))
        self.btn.callback = callback

class GenTokensBtn(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Generate Tokens", style=discord.ButtonStyle.primary)
        
    async def callback(self, interaction):
        view = discord.ui.View()
        select_roles = discord.ui.RoleSelect(max_values=10)
        view.add_item(select_roles)
        async def select_roles_callback(interaction):
            await interaction.response.edit_message(content="Insert the amount of tokens to generate", view=GenTokensView(interaction.data["values"]))
        select_roles.callback = select_roles_callback
        await interaction.response.edit_message(content="Select the role to add with tokens", view=view)

class AdminView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(GenTokensBtn())

@cmd.command(name="admin", description="Admin commands")
@app_commands.default_permissions(administrator=True)
@app_commands.checks.has_permissions(administrator=True)
async def gen_auth_token(interaction):
    await interaction.response.send_message("Click a button to activate an admin function", view=AdminView(), ephemeral=True)

@gen_auth_token.error
async def gen_auth_token_error(interaction, error):
    if isinstance(error, app_commands.errors.MissingPermissions):
        await interaction.response.send_message("You don't have the permissions to use this command", ephemeral=True)
    else:
        await interaction.response.send_message("Unknown error", ephemeral=True)


async def action_handler(action, interaction):
    if action["type"] == "role":
        roles = []
        try:
            if isinstance(action["role"],list):
                roles = [discord.utils.get(g.guild.roles,id=int(role)) for role in action["role"]]
            else:
                roles = [discord.utils.get(g.guild.roles,id=int(action["role"]))]
        except Exception:
            return "There was a problem trying to add the role(s) :/, if it's necessary, contact the admin, the token has been invalidated :("
        for ele in roles:
            try:
                await interaction.user.add_roles(ele) 
            except Exception:
                pass
        return f"Authenticated successfully with role(s) `{'` `'.join([r.name for r in roles])}`, Welcome to the server!"
    else:
        return "Error: Unknown action 0_0"


class AuthModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Authentication")
        self.add_item(discord.ui.TextInput(label="Insert the Token"))
    
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
    if not g.synced:
        await cmd.sync()
        g.synced = True

client.run(TOKEN)
