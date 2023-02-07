import discord, asyncio
from modals import GenTokensModal, EmailDetailsModal, RevokeTokensModal, AuthModal

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
            roles = interaction.data["values"]
            await asyncio.gather(
                interaction.response.send_modal(GenTokensModal(roles)),
                interaction.edit_original_response(content="Insert the amount of tokens to generate", view=GenTokensView(roles)),
            )
        select_roles.callback = select_roles_callback
        await interaction.response.edit_message(content="Select the role to add with tokens", view=view)

class EmailDetailsView(discord.ui.View):
    def __init__(self, roles):
        super().__init__()
        self.roles = roles
        self.btn = discord.ui.Button(label="Open", style=discord.ButtonStyle.primary)
        self.add_item(self.btn)
        async def callback(interaction):
            await interaction.response.send_modal(EmailDetailsModal(roles))
        self.btn.callback = callback

class EmailTokensBtn(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Emails with Token", style=discord.ButtonStyle.success)
        
    async def callback(self, interaction):
        view = discord.ui.View()
        select_roles = discord.ui.RoleSelect(max_values=10)
        view.add_item(select_roles)
        async def select_roles_callback(interaction):
            roles = interaction.data["values"]
            await interaction.response.send_modal(EmailDetailsModal(roles))
            await interaction.edit_original_response(content="Insert the infromation about the emails", view=EmailDetailsView(roles))
        select_roles.callback = select_roles_callback
        await interaction.response.edit_message(content="Select the role to add with tokens", view=view)

class RevokeTokensBtn(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Revoke Tokens", style=discord.ButtonStyle.danger)
        
    async def callback(self, interaction):
        await interaction.response.send_modal(RevokeTokensModal())

class AdminView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(GenTokensBtn())
        self.add_item(RevokeTokensBtn())
        self.add_item(EmailTokensBtn())
        
class AuthBtn(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Authenticate", style=discord.ButtonStyle.primary, emoji="🔐")
        
    async def callback(self, interaction):
        await interaction.response.send_modal(AuthModal())

class AuthView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(AuthBtn())
