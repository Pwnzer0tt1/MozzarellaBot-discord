from dotenv import load_dotenv
load_dotenv()
from syjson import SyJson
import os, discord, asyncio, secrets

TOKEN = os.getenv('DISCORD_TOKEN')

EMAIL_FROM = os.getenv('EMAIL_FROM')
SMTP_SERVER = os.getenv('SMTP_SERVER')
USER_SMTP = os.getenv('USER_SMTP')
PSW_SMTP = os.getenv('PSW_SMTP')

EMAIL_REGEX = "(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|\"(?:[\\x01-\\x08\\x0b\\x0c\\x0e-\\x1f\\x21\\x23-\\x5b\\x5d-\\x7f]|\\\\[\\x01-\\x09\\x0b\\x0c\\x0e-\\x7f])*\")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\\x01-\\x08\\x0b\\x0c\\x0e-\\x1f\\x21-\\x5a\\x53-\\x7f]|\\\\[\\x01-\\x09\\x0b\\x0c\\x0e-\\x7f])+)\\])"

class g:
    guild = None
    auth_ch_name = "🔐︱auth"
    synced = False

db = SyJson("db.json")

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

async def send_emails_with_token(emails, object, message, roles):
    await asyncio.sleep(1) #to implement!
