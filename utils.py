from dotenv import load_dotenv
load_dotenv()
from syjson import SyJson
import os, discord, asyncio, secrets
from email.message import EmailMessage
import aiosmtplib
from discord import app_commands

TOKEN = os.getenv('DISCORD_TOKEN')

EMAIL_FROM = os.getenv('EMAIL_FROM')
SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_SERVER_PORT = int(os.getenv('SMTP_SERVER_PORT'))
USER_SMTP = os.getenv('USER_SMTP', EMAIL_FROM)
PSW_SMTP = os.getenv('PSW_SMTP')
GENERAL_TIMEOUT = int(os.getenv('GENERAL_TIMEOUT', 24*60*60))
EMAIL_REGEX = "(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|\"(?:[\\x01-\\x08\\x0b\\x0c\\x0e-\\x1f\\x21\\x23-\\x5b\\x5d-\\x7f]|\\\\[\\x01-\\x09\\x0b\\x0c\\x0e-\\x7f])*\")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\\x01-\\x08\\x0b\\x0c\\x0e-\\x1f\\x21-\\x5a\\x53-\\x7f]|\\\\[\\x01-\\x09\\x0b\\x0c\\x0e-\\x7f])+)\\])"

if not os.path.exists("data"):
    os.mkdir("data")
db = SyJson("data/db.json")

gen_token_lock = asyncio.Lock()
async def gen_token(guild_id):
    async with gen_token_lock:
        while True:
            tk = secrets.token_hex(16)
            if tk not in db[guild_id]["auth_tokens"]:
                db["auth_tokens"][tk] = None
                return tk

async def add_token_role(roles, guild_id, description=None):
    roles = list(map(int, roles))
    tk = await gen_token(guild_id)
    db[guild_id]["auth_tokens"][tk] = {"role":roles,"type":"role","description":description}
    return tk

async def action_handler(action, interaction):
    if action["type"] == "role":
        roles = []
        try:
            if isinstance(action["role"],list):
                roles = [discord.utils.get(interaction.guild.roles,id=int(role)) for role in action["role"]]
            else:
                roles = [discord.utils.get(interaction.guild.roles,id=int(action["role"]))]
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

async def _send_email_wih_token(email, object, message, roles, guild_id, client=None):
    try:
        msg = EmailMessage()
        msg["From"] = EMAIL_FROM
        msg["To"] = email
        msg["Subject"] = object
        token = await add_token_role(roles, guild_id, {"email":email,"object":object})
        msg.set_content(message+f"\n\n---> DISCORD TOKEN: {token}\n")
        if client:
            return await client.send_message(msg)
        else:
            return await aiosmtplib.send(msg, hostname=SMTP_SERVER, port=SMTP_SERVER_PORT, username=USER_SMTP, password=PSW_SMTP)
    except Exception as e:
        return e

async def send_emails_with_token(emails, object, message, roles, guild_id):
    try:
        client = aiosmtplib.SMTP(hostname=SMTP_SERVER, port=SMTP_SERVER_PORT, username=USER_SMTP, password=PSW_SMTP)
        await client.connect()
    except Exception as e:
        return e
    result = await asyncio.gather(*[_send_email_wih_token(email, object, message, roles, guild_id, client) for email in emails])
    try:
        await client.quit()
    except Exception:
        client.close()
    return [(email, result[i])for i,email in enumerate(emails) if isinstance(result[i], Exception) or result[i] is None]

async def error_handler(error, interaction):
    if isinstance(error, app_commands.errors.MissingPermissions):
        await interaction.response.send_message("You don't have the permissions to use this command", ephemeral=True)
    else:
        await interaction.response.send_message("Unknown error", ephemeral=True)