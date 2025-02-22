import discord
import asyncio
from modals import GenTokensModal, EmailDetailsModal, RevokeTokensModal, AuthModal, RenameModal, GenPasswordModal
from discord import app_commands
from utils import GENERAL_TIMEOUT, gen_text_description_actions

class OpenModalView(discord.ui.View):
    def __init__(self, modal):
        super().__init__(timeout=GENERAL_TIMEOUT)
        self.btn = discord.ui.Button(label="Open", style=discord.ButtonStyle.primary)
        self.add_item(self.btn)
        async def callback(interaction):
            await interaction.response.send_modal(modal)
        self.btn.callback = callback

class GenTokensBtn(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Generate Tokens", style=discord.ButtonStyle.primary)
    
    @app_commands.checks.has_permissions(administrator=True)
    async def callback(self, interaction):
        await interaction.response.edit_message(content="Select the action to enable with this token", view=GenTokenSelectOperations())

class GenPasswordTokenBtn(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Create a password token", style=discord.ButtonStyle.blurple)
    
    @app_commands.checks.has_permissions(administrator=True)
    async def callback(self, interaction):
        await interaction.response.edit_message(content="Select the action to enable with this password", view=GenPasswordSelectOperations())

class OkBtn(discord.ui.Button):
    def __init__(self, next_action=None):
        super().__init__(label="Ok", style=discord.ButtonStyle.green)
        self.next_action=next_action
    
    @app_commands.checks.has_permissions(administrator=True)
    async def callback(self, interaction):
        if callable(self.next_action):
            await self.next_action(interaction)
        
class SelectRoleBtn(discord.ui.Button):
    def __init__(self, data:dict=None, class_to_use=None):
        super().__init__(label="Assign some roles", style=discord.ButtonStyle.primary)
        self.class_to_use = class_to_use
        self.data = data if data else {}
    
    @app_commands.checks.has_permissions(administrator=True)
    async def callback(self, interaction):
        view = discord.ui.View(timeout=GENERAL_TIMEOUT)
        select_roles = discord.ui.RoleSelect(max_values=10)
        view.add_item(select_roles)
        @app_commands.checks.has_permissions(administrator=True)
        async def select_roles_callback(interact):
            self.data["roles"] = interact.data["values"]
            await interact.response.edit_message(content=gen_text_description_actions(self.data), view=self.class_to_use(self.data))
        select_roles.callback = select_roles_callback
        await interaction.response.edit_message(content="Select the role to add with tokens", view=view)

class RenameBtn(discord.ui.Button):
    def __init__(self, data:dict=None, class_to_use=None):
        super().__init__(label="Rename", style=discord.ButtonStyle.primary)
        self.class_to_use = class_to_use
        self.data = data if data else {}
    
    @app_commands.checks.has_permissions(administrator=True)
    async def callback(self, interaction):
        async def next_action(interact):
            self.data["rename"] = interact.data["components"][0]["components"][0]["value"]
            await interact.response.edit_message(content=gen_text_description_actions(self.data), view=self.class_to_use(self.data))
        modal = RenameModal(self.data, next_action=next_action)
        await asyncio.gather(
            interaction.response.send_modal(modal),
            interaction.edit_original_response(content="Insert the name to rename", view=OpenModalView(modal)),
        )

class GenPasswordSelectOperations(discord.ui.View):
    def __init__(self, data=None):
        super().__init__(timeout=GENERAL_TIMEOUT)
        self.data = data if data else {}
        self.add_item(SelectRoleBtn(self.data, class_to_use=GenPasswordSelectOperations))
        self.add_item(RenameBtn(self.data, class_to_use=GenPasswordSelectOperations))
        async def nextop(interaction):
            modal = GenPasswordModal(self.data)
            await asyncio.gather(
                interaction.response.send_modal(modal),
                interaction.edit_original_response(content="Insert the password to use", view=OpenModalView(modal)),
            )
        self.add_item(OkBtn(next_action=nextop))

class GenTokenSelectOperations(discord.ui.View):
    def __init__(self, data=None):
        super().__init__(timeout=GENERAL_TIMEOUT)
        self.data = data if data else {}
        self.add_item(SelectRoleBtn(self.data, class_to_use=GenTokenSelectOperations))
        self.add_item(RenameBtn(self.data, class_to_use=GenTokenSelectOperations))
        async def nextop(interaction):
            modal = GenTokensModal(self.data)
            await asyncio.gather(
                interaction.response.send_modal(modal),
                interaction.edit_original_response(content="Insert the amount of tokens to generate", view=OpenModalView(modal)),
            )
        self.add_item(OkBtn(next_action=nextop))

class EmailDetailsView(discord.ui.View):
    def __init__(self, data=None):
        super().__init__(timeout=GENERAL_TIMEOUT)
        self.data = data if data else {}
        self.btn = discord.ui.Button(label="Open", style=discord.ButtonStyle.primary)
        self.add_item(self.btn)
        @app_commands.checks.has_permissions(administrator=True)
        async def callback(interaction):
            await interaction.response.send_modal(EmailDetailsModal(self.data))
        self.btn.callback = callback

class EmailTokensBtn(discord.ui.Button):
    def __init__(self, data=None):
        super().__init__(label="Emails with Token", style=discord.ButtonStyle.success)
        self.data = data if data else {}
    
    @app_commands.checks.has_permissions(administrator=True)
    async def callback(self, interaction):
        view = discord.ui.View(timeout=GENERAL_TIMEOUT)
        select_roles = discord.ui.RoleSelect(max_values=10)
        view.add_item(select_roles)
        @app_commands.checks.has_permissions(administrator=True)
        async def select_roles_callback(interaction):
            self.data["roles"] = interaction.data["values"]
            await interaction.response.send_modal(EmailDetailsModal(self.data))
            await interaction.edit_original_response(content="Insert the infromation about the emails", view=EmailDetailsView(self.data))
        select_roles.callback = select_roles_callback
        await interaction.response.edit_message(content="Select the role to add with tokens", view=view)

class RevokeTokensBtn(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Revoke Tokens", style=discord.ButtonStyle.danger)
    
    @app_commands.checks.has_permissions(administrator=True)
    async def callback(self, interaction):
        await interaction.response.send_modal(RevokeTokensModal())

class AdminView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=GENERAL_TIMEOUT)
        self.add_item(GenTokensBtn())
        self.add_item(GenPasswordTokenBtn())
        self.add_item(RevokeTokensBtn())
        self.add_item(EmailTokensBtn())
       
        
class AuthBtn(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Authenticate", style=discord.ButtonStyle.primary, emoji="🔐", custom_id="auth_btn")
    
    @app_commands.checks.has_permissions(administrator=True)
    async def callback(self, interaction):
        await interaction.response.send_modal(AuthModal())

class AuthView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(AuthBtn())
