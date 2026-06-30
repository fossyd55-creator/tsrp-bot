import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
import json
import os

class StaffManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.server_logo = "https://cdn.discordapp.com/attachments/1521347039051382784/1521363327488360529/file_000000001ff8722fbcfafc041f4d1322.png?ex=6a453842&is=6a43e6c2&hm=552eaa24f4409fb1770324802daef56f47424f16281618953d971a05434dc18c"
        self.config_file = "tsrp_config.json"
        self.embeds_file = "tsrp_embeds.json"
        self.load_config()
        self.load_embeds()
    
    def load_config(self):
        """Load configuration from JSON file"""
        if os.path.exists(self.config_file):
            with open(self.config_file, "r") as f:
                self.config = json.load(f)
        else:
            self.config = {
                "server_name": "Tennessee State Roleplay",
                "infraction_channel": None,
                "promotion_channel": None,
                "announcements_channel": None,
                "staff_ranks": ["Moderator", "Senior Moderator", "Admin", "Head Admin"],
                "infraction_types": {
                    "Warning": "Warning",
                    "Strike One": "Strike One",
                    "Strike Two": "Strike Two",
                    "Strike Three": "Strike Three",
                    "Staff Suspension": "Staff Suspension",
                    "Termination": "Termination",
                    "Staff Blacklist": "Staff Blacklist"
                }
            }
            self.save_config()
    
    def load_embeds(self):
        """Load embeds from JSON file"""
        if os.path.exists(self.embeds_file):
            with open(self.embeds_file, "r") as f:
                self.stored_embeds = json.load(f)
        else:
            self.stored_embeds = {}
    
    def save_config(self):
        """Save configuration to JSON file"""
        with open(self.config_file, "w") as f:
            json.dump(self.config, f, indent=4)
    
    def save_embeds(self):
        """Save embeds to JSON file"""
        with open(self.embeds_file, "w") as f:
            json.dump(self.stored_embeds, f, indent=4)
    
    @app_commands.command(name="tsrp_dashboard", description="Open the Tennessee State Roleplay staff management dashboard")
    async def tsrp_dashboard(self, interaction: discord.Interaction):
        """Opens the main management dashboard"""
        
        embed = discord.Embed(
            title="📊 Tennessee State Roleplay - Staff Management",
            description="Manage all staff operations from this dashboard",
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
        
        embed.add_field(
            name="🎯 Quick Actions",
            value="Use the buttons below to access all management features",
            inline=False
        )
        
        embed.set_thumbnail(url=self.server_logo)
        embed.set_footer(text="TSRP Staff Management System", icon_url=interaction.guild.icon)
        
        view = DashboardView(self, interaction.guild)
        
        await interaction.response.send_message(embed=embed, view=view)


class DashboardView(discord.ui.View):
    def __init__(self, cog, guild):
        super().__init__(timeout=None)
        self.cog = cog
        self.guild = guild
    
    @discord.ui.button(label="Create Infraction", style=discord.ButtonStyle.danger, emoji="⚠️")
    async def infraction_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Open infraction creation modal"""
        modal = InfractionModal(self.cog, self.guild)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="Create Promotion", style=discord.ButtonStyle.success, emoji="🎉")
    async def promotion_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Open promotion creation modal"""
        modal = PromotionModal(self.cog, self.guild)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="Create Embed", style=discord.ButtonStyle.primary, emoji="📝")
    async def create_embed_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Open embed creation modal"""
        modal = CreateEmbedModal(self.cog, self.guild)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="Manage Embeds", style=discord.ButtonStyle.blurple, emoji="📚")
    async def manage_embeds_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Show embed management options"""
        await interaction.response.defer()
        
        self.cog.load_embeds()
        
        if not self.cog.stored_embeds:
            await interaction.followup.send("❌ No custom embeds found!", ephemeral=True)
            return
        
        embed_list = "\n".join([f"• {name}" for name in self.cog.stored_embeds.keys()])
        
        embed = discord.Embed(
            title="📚 Manage Custom Embeds",
            description=f"**Available Embeds:**\n{embed_list}",
            color=discord.Color.blurple()
        )
        
        embed.set_thumbnail(url=self.cog.server_logo)
        embed.set_footer(text="Select an embed to manage", icon_url=self.guild.icon)
        
        view = ManageEmbedsView(self.cog, list(self.cog.stored_embeds.keys()), self.guild)
        
        await interaction.followup.send(embed=embed, view=view, ephemeral=True)
    
    @discord.ui.button(label="Settings", style=discord.ButtonStyle.gray, emoji="⚙️")
    async def settings_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Open settings menu"""
        await interaction.response.defer()
        
        embed = discord.Embed(
            title="⚙️ Settings Menu",
            description="Configure your staff management system",
            color=discord.Color.gray()
        )
        
        embed.add_field(
            name="📋 Options",
            value="Choose an option below to configure:",
            inline=False
        )
        
        embed.set_thumbnail(url=self.cog.server_logo)
        embed.set_footer(text="TSRP Staff Management", icon_url=self.guild.icon)
        
        view = SettingsView(self.cog, self.guild)
        
        await interaction.followup.send(embed=embed, view=view, ephemeral=True)


class SettingsView(discord.ui.View):
    def __init__(self, cog, guild):
        super().__init__(timeout=None)
        self.cog = cog
        self.guild = guild
    
    @discord.ui.button(label="Configure Channels", style=discord.ButtonStyle.blurple, emoji="📺")
    async def configure_channels_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Show channel configuration"""
        await interaction.response.defer()
        
        self.cog.load_config()
        
        infraction_ch = self.guild.get_channel(self.cog.config["infraction_channel"]) if self.cog.config["infraction_channel"] else None
        promotion_ch = self.guild.get_channel(self.cog.config["promotion_channel"]) if self.cog.config["promotion_channel"] else None
        announcements_ch = self.guild.get_channel(self.cog.config["announcements_channel"]) if self.cog.config["announcements_channel"] else None
        
        embed = discord.Embed(
            title="📺 Channel Configuration",
            description="Set channels for different message types",
            color=discord.Color.blurple()
        )
        
        embed.add_field(
            name="⚠️ Infraction Channel",
            value=infraction_ch.mention if infraction_ch else "❌ Not set",
            inline=False
        )
        embed.add_field(
            name="🎉 Promotion Channel",
            value=promotion_ch.mention if promotion_ch else "❌ Not set",
            inline=False
        )
        embed.add_field(
            name="📢 Announcements Channel",
            value=announcements_ch.mention if announcements_ch else "❌ Not set",
            inline=False
        )
        
        embed.set_thumbnail(url=self.cog.server_logo)
        embed.set_footer(text="Click buttons in your target channel to set it", icon_url=self.guild.icon)
        
        view = ChannelSettingsView(self.cog, self.guild)
        
        await interaction.followup.send(embed=embed, view=view, ephemeral=True)
    
    @discord.ui.button(label="Manage Staff Ranks", style=discord.ButtonStyle.green, emoji="👥")
    async def manage_ranks_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Manage staff ranks"""
        await interaction.response.defer()
        
        self.cog.load_config()
        ranks_list = "\n".join([f"• {rank}" for rank in self.cog.config["staff_ranks"]])
        
        embed = discord.Embed(
            title="👥 Manage Staff Ranks",
            description=f"**Current Ranks:**\n{ranks_list}",
            color=discord.Color.green()
        )
        
        embed.set_thumbnail(url=self.cog.server_logo)
        embed.set_footer(text="Use buttons to manage ranks", icon_url=self.guild.icon)
        
        view = RanksManagementView(self.cog, self.guild)
        
        await interaction.followup.send(embed=embed, view=view, ephemeral=True)
    
    @discord.ui.button(label="Manage Infraction Types", style=discord.ButtonStyle.danger, emoji="⚠️")
    async def manage_infractions_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Manage infraction types"""
        await interaction.response.defer()
        
        self.cog.load_config()
        types_list = "\n".join([f"• {infraction_type}" for infraction_type in self.cog.config["infraction_types"].keys()])
        
        embed = discord.Embed(
            title="⚠️ Manage Infraction Types",
            description=f"**Current Types:**\n{types_list}",
            color=discord.Color.red()
        )
        
        embed.set_thumbnail(url=self.cog.server_logo)
        embed.set_footer(text="Use buttons to manage infraction types", icon_url=self.guild.icon)
        
        view = InfractionsManagementView(self.cog, self.guild)
        
        await interaction.followup.send(embed=embed, view=view, ephemeral=True)


class ChannelSettingsView(discord.ui.View):
    def __init__(self, cog, guild):
        super().__init__(timeout=None)
        self.cog = cog
        self.guild = guild
    
    @discord.ui.button(label="Set Infraction Channel", style=discord.ButtonStyle.danger, emoji="⚠️")
    async def set_infraction_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Set infraction channel"""
        self.cog.load_config()
        self.cog.config["infraction_channel"] = interaction.channel.id
        self.cog.save_config()
        await interaction.response.send_message(f"✅ Infraction channel set to {interaction.channel.mention}", ephemeral=True)
    
    @discord.ui.button(label="Set Promotion Channel", style=discord.ButtonStyle.success, emoji="🎉")
    async def set_promotion_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Set promotion channel"""
        self.cog.load_config()
        self.cog.config["promotion_channel"] = interaction.channel.id
        self.cog.save_config()
        await interaction.response.send_message(f"✅ Promotion channel set to {interaction.channel.mention}", ephemeral=True)
    
    @discord.ui.button(label="Set Announcements Channel", style=discord.ButtonStyle.blurple, emoji="📢")
    async def set_announcements_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Set announcements channel"""
        self.cog.load_config()
        self.cog.config["announcements_channel"] = interaction.channel.id
        self.cog.save_config()
        await interaction.response.send_message(f"✅ Announcements channel set to {interaction.channel.mention}", ephemeral=True)


class RanksManagementView(discord.ui.View):
    def __init__(self, cog, guild):
        super().__init__(timeout=None)
        self.cog = cog
        self.guild = guild
    
    @discord.ui.button(label="Add Rank", style=discord.ButtonStyle.green, emoji="➕")
    async def add_rank_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Add a new rank"""
        modal = AddRankModal(self.cog, self.guild)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="Remove Rank", style=discord.ButtonStyle.red, emoji="➖")
    async def remove_rank_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Remove a rank"""
        await interaction.response.defer()
        
        self.cog.load_config()
        
        if not self.cog.config["staff_ranks"]:
            await interaction.followup.send("❌ No ranks to remove!", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="➖ Remove Rank",
            description="Select a rank to remove:",
            color=discord.Color.red()
        )
        
        embed.set_thumbnail(url=self.cog.server_logo)
        
        view = RemoveRankView(self.cog, self.cog.config["staff_ranks"], self.guild)
        
        await interaction.followup.send(embed=embed, view=view, ephemeral=True)


class AddRankModal(discord.ui.Modal, title="Add New Rank"):
    rank_name = discord.ui.TextInput(label="Rank Name", placeholder="e.g., Head Admin")
    
    def __init__(self, cog, guild):
        super().__init__()
        self.cog = cog
        self.guild = guild
    
    async def on_submit(self, interaction: discord.Interaction):
        self.cog.load_config()
        
        if self.rank_name.value in self.cog.config["staff_ranks"]:
            await interaction.response.send_message("❌ This rank already exists!", ephemeral=True)
            return
        
        self.cog.config["staff_ranks"].append(self.rank_name.value)
        self.cog.save_config()
        
        await interaction.response.send_message(f"✅ Rank **{self.rank_name.value}** added!", ephemeral=True)


class RemoveRankView(discord.ui.View):
    def __init__(self, cog, ranks, guild):
        super().__init__(timeout=None)
        self.cog = cog
        self.guild = guild
        
        options = [discord.SelectOption(label=rank) for rank in ranks]
        self.select.options = options
    
    @discord.ui.select(placeholder="Select a rank to remove")
    async def select_rank(self, interaction: discord.Interaction, select: discord.ui.Select):
        rank = select.values[0]
        
        self.cog.load_config()
        if rank in self.cog.config["staff_ranks"]:
            self.cog.config["staff_ranks"].remove(rank)
            self.cog.save_config()
            await interaction.response.send_message(f"✅ Rank **{rank}** removed!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Rank not found!", ephemeral=True)


class InfractionsManagementView(discord.ui.View):
    def __init__(self, cog, guild):
        super().__init__(timeout=None)
        self.cog = cog
        self.guild = guild
    
    @discord.ui.button(label="Add Type", style=discord.ButtonStyle.green, emoji="➕")
    async def add_type_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Add new infraction type"""
        modal = AddInfractionTypeModal(self.cog, self.guild)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="Remove Type", style=discord.ButtonStyle.red, emoji="➖")
    async def remove_type_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Remove infraction type"""
        await interaction.response.defer()
        
        self.cog.load_config()
        
        if not self.cog.config["infraction_types"]:
            await interaction.followup.send("❌ No infraction types to remove!", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="➖ Remove Infraction Type",
            description="Select a type to remove:",
            color=discord.Color.red()
        )
        
        embed.set_thumbnail(url=self.cog.server_logo)
        
        view = RemoveInfractionTypeView(self.cog, list(self.cog.config["infraction_types"].keys()), self.guild)
        
        await interaction.followup.send(embed=embed, view=view, ephemeral=True)


class AddInfractionTypeModal(discord.ui.Modal, title="Add Infraction Type"):
    type_name = discord.ui.TextInput(label="Infraction Type", placeholder="e.g., Unprofessional Behavior")
    
    def __init__(self, cog, guild):
        super().__init__()
        self.cog = cog
        self.guild = guild
    
    async def on_submit(self, interaction: discord.Interaction):
        self.cog.load_config()
        
        if self.type_name.value in self.cog.config["infraction_types"]:
            await interaction.response.send_message("❌ This infraction type already exists!", ephemeral=True)
            return
        
        self.cog.config["infraction_types"][self.type_name.value] = self.type_name.value
        self.cog.save_config()
        
        await interaction.response.send_message(f"✅ Infraction type **{self.type_name.value}** added!", ephemeral=True)


class RemoveInfractionTypeView(discord.ui.View):
    def __init__(self, cog, types, guild):
        super().__init__(timeout=None)
        self.cog = cog
        self.guild = guild
        
        options = [discord.SelectOption(label=inf_type) for inf_type in types]
        self.select.options = options
    
    @discord.ui.select(placeholder="Select a type to remove")
    async def select_type(self, interaction: discord.Interaction, select: discord.ui.Select):
        inf_type = select.values[0]
        
        self.cog.load_config()
        if inf_type in self.cog.config["infraction_types"]:
            del self.cog.config["infraction_types"][inf_type]
            self.cog.save_config()
            await interaction.response.send_message(f"✅ Infraction type **{inf_type}** removed!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Type not found!", ephemeral=True)


class ManageEmbedsView(discord.ui.View):
    def __init__(self, cog, embed_names, guild):
        super().__init__(timeout=None)
        self.cog = cog
        self.embed_names = embed_names
        self.guild = guild
        
        options = [discord.SelectOption(label=name) for name in embed_names]
        self.select.options = options
    
    @discord.ui.select(placeholder="Select an embed to manage")
    async def select_embed(self, interaction: discord.Interaction, select: discord.ui.Select):
        embed_name = select.values[0]
        
        embed_data = self.cog.stored_embeds.get(embed_name)
        if not embed_data:
            await interaction.response.send_message("❌ Embed not found!", ephemeral=True)
            return
        
        color_int = int(embed_data["color"].replace("#", ""), 16)
        embed = discord.Embed(
            title=embed_data["title"],
            description=embed_data["description"],
            color=discord.Color(color_int),
            timestamp=datetime.now()
        )
        embed.set_thumbnail(url=embed_data.get("thumbnail", self.cog.server_logo))
        embed.set_footer(text=embed_data.get("footer", "TSRP Staff Management"))
        
        view = EmbedActionView(self.cog, embed_name, self.guild)
        
        await interaction.response.send_message(f"**Embed:** {embed_name}", embed=embed, view=view, ephemeral=True)


class EmbedActionView(discord.ui.View):
    def __init__(self, cog, embed_name, guild):
        super().__init__(timeout=None)
        self.cog = cog
        self.embed_name = embed_name
        self.guild = guild
    
    @discord.ui.button(label="Edit", style=discord.ButtonStyle.primary, emoji="✏️")
    async def edit_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Edit the embed"""
        modal = EditEmbedModal(self.cog, self.embed_name, self.guild)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="Send", style=discord.ButtonStyle.success, emoji="📤")
    async def send_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Send the embed"""
        await interaction.response.defer()
        
        self.cog.load_config()
        
        channel_id = self.cog.config.get("announcements_channel")
        if not channel_id:
            await interaction.followup.send("❌ Announcements channel not configured! Use Settings → Configure Channels", ephemeral=True)
            return
        
        channel = self.guild.get_channel(channel_id)
        if not channel:
            await interaction.followup.send("❌ Announcements channel not found!", ephemeral=True)
            return
        
        self.cog.load_embeds()
        embed_data = self.cog.stored_embeds.get(self.embed_name)
        if not embed_data:
            await interaction.followup.send("❌ Embed not found!", ephemeral=True)
            return
        
        color_int = int(embed_data["color"].replace("#", ""), 16)
        embed = discord.Embed(
            title=embed_data["title"],
            description=embed_data["description"],
            color=discord.Color(color_int),
            timestamp=datetime.now()
        )
        embed.set_thumbnail(url=embed_data.get("thumbnail", self.cog.server_logo))
        embed.set_footer(text=embed_data.get("footer", "TSRP Staff Management"))
        
        try:
            await channel.send(embed=embed)
            await interaction.followup.send(f"✅ Embed sent to {channel.mention}!", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Error sending embed: {str(e)}", ephemeral=True)
    
    @discord.ui.button(label="Delete", style=discord.ButtonStyle.danger, emoji="🗑️")
    async def delete_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Delete the embed"""
        self.cog.load_embeds()
        if self.embed_name in self.cog.stored_embeds:
            del self.cog.stored_embeds[self.embed_name]
            self.cog.save_embeds()
            await interaction.response.send_message(f"✅ Embed **{self.embed_name}** deleted!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Embed not found!", ephemeral=True)


class InfractionModal(discord.ui.Modal, title="Create Infraction"):
    member = discord.ui.TextInput(label="Member (@mention)", placeholder="@member")
    infraction_type = discord.ui.TextInput(label="Infraction Type", placeholder="e.g., Warning, Strike One, etc.")
    reason = discord.ui.TextInput(label="Reason", placeholder="Detailed reason for infraction", style=discord.TextStyle.long)
    notes = discord.ui.TextInput(label="Additional Notes (Optional)", placeholder="Any additional information", required=False)
    
    def __init__(self, cog, guild):
        super().__init__()
        self.cog = cog
        self.guild = guild
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            member = await commands.MemberConverter().convert(interaction, self.member.value)
            
            embed = discord.Embed(
                title="⚠️ Staff Infraction Report",
                description=f"{member.mention} has received an infraction",
                color=discord.Color.red(),
                timestamp=datetime.now()
            )
            
            embed.add_field(name="👤 Member", value=member.mention, inline=False)
            embed.add_field(name="⚠️ Infraction Type", value=self.infraction_type.value, inline=False)
            embed.add_field(name="👨‍💼 Reported By", value=interaction.user.mention, inline=False)
            embed.add_field(name="📋 Reason", value=self.reason.value, inline=False)
            
            if self.notes.value:
                embed.add_field(name="📝 Additional Notes", value=self.notes.value, inline=False)
            
            embed.set_thumbnail(url=self.cog.server_logo)
            embed.set_footer(text=f"Tennessee State Roleplay | ID: {member.id}", icon_url=self.guild.icon)
            
            self.cog.load_config()
            
            channel_id = self.cog.config.get("infraction_channel")
            if channel_id:
                channel = self.guild.get_channel(channel_id)
                if channel:
                    await channel.send(embed=embed)
                    await interaction.response.send_message(f"✅ Infraction report sent to {channel.mention}", ephemeral=True)
                else:
                    await interaction.response.send_message("❌ Infraction channel not found!", ephemeral=True)
            else:
                await interaction.response.send_message("❌ Infraction channel not configured! Use Settings → Configure Channels.", ephemeral=True)
        
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {str(e)}", ephemeral=True)


class PromotionModal(discord.ui.Modal, title="Create Promotion"):
    member = discord.ui.TextInput(label="Member (@mention)", placeholder="@member")
    new_rank = discord.ui.TextInput(label="New Rank", placeholder="e.g., Senior Moderator")
    reason = discord.ui.TextInput(label="Reason for Promotion", placeholder="Why are they being promoted?", style=discord.TextStyle.long)
    promoted_by = discord.ui.TextInput(label="Promoted By (@mention)", placeholder="@promoter", required=False)
    notes = discord.ui.TextInput(label="Additional Notes (Optional)", placeholder="Any additional information", required=False)
    
    def __init__(self, cog, guild):
        super().__init__()
        self.cog = cog
        self.guild = guild
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            member = await commands.MemberConverter().convert(interaction, self.member.value)
            
            if self.promoted_by.value:
                promoter = await commands.MemberConverter().convert(interaction, self.promoted_by.value)
            else:
                promoter = interaction.user
            
            embed = discord.Embed(
                title="🎉 Staff Promotion",
                description=f"{member.mention} has been promoted!",
                color=discord.Color.gold(),
                timestamp=datetime.now()
            )
            
            embed.add_field(name="👤 Member", value=member.mention, inline=False)
            embed.add_field(name="📈 New Rank", value=self.new_rank.value, inline=False)
            embed.add_field(name="👨‍💼 Promoted By", value=promoter.mention, inline=False)
            embed.add_field(name="📝 Reason", value=self.reason.value, inline=False)
            
            if self.notes.value:
                embed.add_field(name="📌 Additional Notes", value=self.notes.value, inline=False)
            
            embed.set_thumbnail(url=self.cog.server_logo)
            embed.set_footer(text=f"Tennessee State Roleplay | ID: {member.id}", icon_url=self.guild.icon)
            
            self.cog.load_config()
            
            channel_id = self.cog.config.get("promotion_channel")
            if channel_id:
                channel = self.guild.get_channel(channel_id)
                if channel:
                    await channel.send(embed=embed)
                    await interaction.response.send_message(f"✅ Promotion sent to {channel.mention}", ephemeral=True)
                else:
                    await interaction.response.send_message("❌ Promotion channel not found!", ephemeral=True)
            else:
                await interaction.response.send_message("❌ Promotion channel not configured! Use Settings → Configure Channels.", ephemeral=True)
        
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {str(e)}", ephemeral=True)


class CreateEmbedModal(discord.ui.Modal, title="Create Custom Embed"):
    embed_name = discord.ui.TextInput(label="Embed Name", placeholder="e.g., server_rules")
    title = discord.ui.TextInput(label="Title", placeholder="Embed title")
    description = discord.ui.TextInput(label="Description", placeholder="Embed description", style=discord.TextStyle.long)
    color = discord.ui.TextInput(label="Color (hex)", placeholder="e.g., FF0000", default="0000FF")
    
    def __init__(self, cog, guild):
        super().__init__()
        self.cog = cog
        self.guild = guild
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            color_int = int(self.color.value.replace("#", ""), 16)
            embed_color = discord.Color(color_int)
            
            embed = discord.Embed(
                title=self.title.value,
                description=self.description.value,
                color=embed_color,
                timestamp=datetime.now()
            )
            
            embed.set_thumbnail(url=self.cog.server_logo)
            embed.set_footer(text="Tennessee State Roleplay", icon_url=self.guild.icon)
            
            self.cog.stored_embeds[self.embed_name.value] = {
                "title": self.title.value,
                "description": self.description.value,
                "color": self.color.value,
                "thumbnail": self.cog.server_logo,
                "footer": "Tennessee State Roleplay"
            }
            self.cog.save_embeds()
            
            await interaction.response.send_message(f"✅ Embed **{self.embed_name.value}** created!", embed=embed, ephemeral=True)
        
        except ValueError:
            await interaction.response.send_message("❌ Invalid color format! Use hex format (e.g., FF0000)", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {str(e)}", ephemeral=True)


class EditEmbedModal(discord.ui.Modal, title="Edit Embed"):
    title = discord.ui.TextInput(label="Title", placeholder="Leave blank to keep current", required=False)
    description = discord.ui.TextInput(label="Description", placeholder="Leave blank to keep current", style=discord.TextStyle.long, required=False)
    color = discord.ui.TextInput(label="Color (hex)", placeholder="Leave blank to keep current", required=False)
    
    def __init__(self, cog, embed_name, guild):
        super().__init__()
        self.cog = cog
        self.embed_name = embed_name
        self.guild = guild
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            self.cog.load_embeds()
            
            if self.embed_name not in self.cog.stored_embeds:
                await interaction.response.send_message("❌ Embed not found!", ephemeral=True)
                return
            
            embed_data = self.cog.stored_embeds[self.embed_name]
            
            if self.title.value:
                embed_data["title"] = self.title.value
            if self.description.value:
                embed_data["description"] = self.description.value
            if self.color.value:
                color_int = int(self.color.value.replace("#", ""), 16)
                embed_data["color"] = self.color.value
            
            self.cog.save_embeds()
            
            color_int = int(embed_data["color"].replace("#", ""), 16)
            embed = discord.Embed(
                title=embed_data["title"],
                description=embed_data["description"],
                color=discord.Color(color_int),
                timestamp=datetime.now()
            )
            embed.set_thumbnail(url=embed_data.get("thumbnail", self.cog.server_logo))
            embed.set_footer(text=embed_data.get("footer", "TSRP"))
            
            view = EmbedActionView(self.cog, self.embed_name, self.guild)
            
            await interaction.response.send_message(f"✅ Embed updated!", embed=embed, view=view, ephemeral=True)
        
        except ValueError:
            await interaction.response.send_message("❌ Invalid color format! Use hex format (e.g., FF0000)", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {str(e)}", ephemeral=True)


async def setup(bot):
    await bot.add_cog(StaffManagement(bot))
