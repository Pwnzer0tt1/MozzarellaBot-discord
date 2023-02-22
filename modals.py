import discord, asyncio, re
from discord import app_commands
from utils import EMAIL_REGEX, add_token_role, db, action_handler, send_emails_with_token, GENERAL_TIMEOUT

class GenTokensModal(discord.ui.Modal):
    def __init__(self, roles):
        super().__init__(title="Generate Tokens", timeout=GENERAL_TIMEOUT)
        self.roles = roles
        self.add_item(discord.ui.TextInput(label="Insert the Amount"))
    
    @app_commands.checks.has_permissions(administrator=True)
    async def on_submit(self, interaction):
        amount = interaction.data["components"][0]["components"][0]["value"]
        if not isinstance(amount,str) or not amount.isdigit():
            await interaction.response.edit_message("Please insert a valid amount")
            return
        tokens = await asyncio.gather(*[add_token_role(self.roles, interaction.guild.id) for _ in range(int(amount))])
        token_text = "\n".join(tokens)
        await interaction.response.edit_message(content=f"Here are your generated tokens:\n```\n{token_text}\n```\nSave the tokens before closing this message!", view=None)

class EmailDetailsModal(discord.ui.Modal):
    
    def __init__(self, roles):
        super().__init__(title="Send Emails with Token", timeout=GENERAL_TIMEOUT)
        self.roles = roles
        self.add_item(discord.ui.TextInput(label="To:", placeholder="email1@domain.com, email2@domain.com\nemail3@domain.com [...]", style=discord.TextStyle.paragraph))
        self.add_item(discord.ui.TextInput(label="Subject:", placeholder="Hi there! Welcome to our discord server!", style=discord.TextStyle.short))
        self.add_item(discord.ui.TextInput(label="Message:", placeholder="Under this message will be sent the token to use for the auth", style=discord.TextStyle.paragraph))
    
    @app_commands.checks.has_permissions(administrator=True)
    async def on_submit(self, interaction):
        form = [ele["components"][0]["value"] for ele in interaction.data["components"]]
        emails = re.findall(EMAIL_REGEX, form[0])
        object, message = form[1], form[2]
        if len(emails) == 0:
            await interaction.response.edit_message(content="Please insert at least a valid email")
            return
        
        btn_cancel = discord.ui.Button(label="Cancel", style=discord.ButtonStyle.danger)
        async def cancel_callback(interaction):
            await interaction.response.delete_message()
        btn_cancel.callback = cancel_callback
        
        btn_send = discord.ui.Button(label="Send", style=discord.ButtonStyle.success)
        @app_commands.checks.has_permissions(administrator=True)
        async def send_callback(interaction):
            await interaction.response.edit_message(content="Sending emails... ✉️", view=None)
            failed = await send_emails_with_token(emails, object, message, self.roles, interaction.guild.id)
            if isinstance(failed, Exception):
                await interaction.edit_original_response(content=f"An error occured while sending emails:\n```\n{failed}\n```")
            elif len(failed) == 0:
                await interaction.edit_original_response(content="Emails sent! 👍")
            else:
                await interaction.edit_original_response(
                    content="Emails sent! 👍\n\n{} emails were not sended due to a problem:\n```\n{}```".format(
                        len(failed),
                        "```\n```\n".join([f"Failed to: {email}\nDue to: {error}" for email, error in failed])
                    )
                )
        btn_send.callback = send_callback
        
        view = discord.ui.View()
        view.add_item(btn_cancel)
        view.add_item(btn_send)
        embed = discord.Embed(title=object, description=message+"\n\n---> DISCORD TOKEN: %TOKEN%\n")
        await interaction.response.edit_message(content="The Emails will be sent to {} addresses: `{}` Do you confirm your action?".format(len(emails),"`, `".join(emails)), view=view, embed=embed)
 
class RevokeTokensModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Revoke Tokens", timeout=GENERAL_TIMEOUT)
        self.add_item(discord.ui.TextInput(label="Insert the Token(s)",style=discord.TextStyle.paragraph))
    
    @app_commands.checks.has_permissions(administrator=True)
    async def on_submit(self, interaction):
        tokens = [ele.strip() for ele in interaction.data["components"][0]["components"][0]["value"].split() if ele]
        counter_tokens = 0
        guild_id = str(interaction.guild.id)
        if guild_id in db:
            db[guild_id].create("auth_tokens",{})
            for token in tokens:
                if token in db[guild_id]["auth_tokens"]:
                    counter_tokens+=1
                    del db[guild_id]["auth_tokens"][token]
        await interaction.response.edit_message(content=f"Successfully revoked {counter_tokens} tokens", view=None)


class AuthModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Authentication", custom_id="auth_modal", timeout=None)
        self.add_item(discord.ui.TextInput(label="Insert the Token"))
    
    @app_commands.checks.has_permissions(administrator=True)
    async def on_submit(self, interaction):
        token = interaction.data["components"][0]["components"][0]["value"]
        guild_id = str(interaction.guild.id)
        db.create(guild_id,{})
        db[guild_id].create("auth_tokens",{})
        if token in db[guild_id]["auth_tokens"]:
            action = db[guild_id]["auth_tokens"][token].var()
            del db[guild_id]["auth_tokens"][token]
            return await interaction.response.send_message(await action_handler(action, interaction), ephemeral=True)
        else:
            await interaction.response.send_message("Token invalid or already used :/", ephemeral=True)
