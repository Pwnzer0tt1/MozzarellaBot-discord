import discord, asyncio, re
from utils import EMAIL_REGEX, add_token_role, db, action_handler, send_emails_with_token

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
        tokens = await asyncio.gather(*[add_token_role(self.roles) for _ in range(int(amount))])
        token_text = "\n".join(tokens)
        await interaction.response.edit_message(content=f"Here are your generated tokens:\n```\n{token_text}\n```\nSave the tokens before closing this message!", view=None)


class EmailDetailsModal(discord.ui.Modal):
    
    def __init__(self, roles):
        super().__init__(title="Send Emails with Token")
        self.roles = roles
        self.add_item(discord.ui.TextInput(label="To:", placeholder="email1@domain.com, email2@domain.com\nemail3@domain.com [...]", style=discord.TextStyle.paragraph))
        self.add_item(discord.ui.TextInput(label="Subject:", placeholder="Hi there! Welcome to our discord server!", style=discord.TextStyle.short))
        self.add_item(discord.ui.TextInput(label="Message:", placeholder="Under this message will be sent the token to use for the auth", style=discord.TextStyle.paragraph))
    
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
        async def send_callback(interaction):
            await asyncio.gather(
                interaction.response.edit_message(content="Sending emails... ✉️", view=None),
                send_emails_with_token(emails, object, message, self.roles)
            )
            await interaction.edit_original_response(content="Emails sent! 👍"),
        btn_send.callback = send_callback
        
        view = discord.ui.View()
        view.add_item(btn_cancel)
        view.add_item(btn_send)
        embed = discord.Embed(title=object, description=message+"\n\n DISCORD TOKEN: %TOKEN%")
        await interaction.response.edit_message(content="The Emails will be sent to {} addresses: `{}` Do you confirm your action?".format(len(emails),"`, `".join(emails)), view=view, embed=embed)
 
class RevokeTokensModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Revoke Tokens")
        self.add_item(discord.ui.TextInput(label="Insert the Token(s)",style=discord.TextStyle.paragraph))
        
    async def on_submit(self, interaction):
        tokens = [ele.strip() for ele in interaction.data["components"][0]["components"][0]["value"].split() if ele]
        for token in tokens:
            if token in db["auth_tokens"]:
                del db["auth_tokens"][token]
        await interaction.response.edit_message(content=f"Successfully revoked {len(tokens)} tokens", view=None)


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