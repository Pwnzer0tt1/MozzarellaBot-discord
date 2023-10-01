import os, discord, asyncio, secrets, re
from email.message import EmailMessage
import aiosmtplib, traceback
from discord import app_commands
from db import Token, RoleOp, RenameOp

TOKEN = os.getenv('DISCORD_TOKEN')
EMAIL_FROM = os.getenv('EMAIL_FROM')
SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_SERVER_PORT = int(os.getenv('SMTP_SERVER_PORT'))
USER_SMTP = os.getenv('USER_SMTP', EMAIL_FROM)
PSW_SMTP = os.getenv('PSW_SMTP')
MONGO_URL = os.getenv('MONGO_URL')
GENERAL_TIMEOUT = int(os.getenv('GENERAL_TIMEOUT', 24*60*60))

EMAIL_REGEX = "(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|\"(?:[\\x01-\\x08\\x0b\\x0c\\x0e-\\x1f\\x21\\x23-\\x5b\\x5d-\\x7f]|\\\\[\\x01-\\x09\\x0b\\x0c\\x0e-\\x7f])*\")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\\x01-\\x08\\x0b\\x0c\\x0e-\\x1f\\x21-\\x5a\\x53-\\x7f]|\\\\[\\x01-\\x09\\x0b\\x0c\\x0e-\\x7f])+)\\])"
EMAIL_FORMAT_REGEX = re.compile("(?P<email>"+EMAIL_REGEX+")(:?[ ]*<(?P<nickname>.*)>)?")

async def add_token(guild_id, roles=None, email=None, rename:str=None):
    roles = list(map(int, roles)) if roles else []
    guild_id = int(guild_id)
    exc = None
    for _ in range(3):
        try:
            new_token = Token(
                token=secrets.token_hex(16),
                guild=guild_id,
                operations=list(filter(lambda ele: not ele is None, [
                        RoleOp(roles) if roles else None,
                        RenameOp(rename) if rename else None
                    ])),
                email=email
            )
            await new_token.save()
            break
        except Exception as e:
            exc = e
    else:
        raise exc
    return new_token.token

def gen_text_description_actions(data):
    res = []
    if "roles" in data:
        res.append(f"I will add {len(data['roles'])} role(s)")
    if "rename" in data:
        res.append(f"I will rename you to `{data['rename']}`")
    if len(res) == 0:
        return "No actions"
    return "- " + "\n- ".join(res)

async def action_handler(action, interaction):
    if action.type == "role":
        roles = []
        async def add_role(interaction, role):
            try:
                await interaction.user.add_roles(role) 
            except Exception:
                pass
        try:
            roles = [discord.utils.get(interaction.guild.roles,id=int(role)) for role in action.roles]
            asyncio.gather(*[add_role(interaction, ele) for ele in roles])
        except Exception:
            traceback.print_exc()
            return "There was a problem trying to add the role(s) :/, if it's necessary, contact the admin, the token has been invalidated :("
        
        return f"Authenticated successfully with role(s) \'"+' \''.join([r.name for r in roles])+"\'"
    elif action.type == "rename":
        try:
            await interaction.user.edit(nick=action.rename)
        except Exception:
            traceback.print_exc()
            return "There was a problem trying to rename you :/, if it's necessary, contact the admin, the token has been invalidated :("
        return f"Renamed successfully with name '{action.rename}'"
    else:
        return "Error: Unknown action 0_0"

async def _send_email_wih_token(email, object, message, roles, guild_id, client=None):
    try:
        msg = EmailMessage()
        msg["From"] = EMAIL_FROM
        msg["To"] = email["email"]
        msg["Subject"] = object
        token = await add_token(guild_id, roles=roles, email=email["email"], rename=email["nickname"])
        if r"%%TOKEN%%" in message:
            msg.set_content(message.replace("%%TOKEN%%", token))
        else:
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
    return [(email, result[i]) for i,email in enumerate(emails) if isinstance(result[i], Exception) or result[i] is None]

async def error_handler(error, interaction):
    if isinstance(error, app_commands.errors.MissingPermissions):
        await interaction.response.send_message("You don't have the permissions to use this command", ephemeral=True)
    else:
        await interaction.response.send_message("Unknown error", ephemeral=True)