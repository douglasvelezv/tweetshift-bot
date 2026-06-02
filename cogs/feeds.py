"""
cogs/feeds.py - Comandos para gestionar feeds de Twitter/X
TweetShift Bot
"""
import logging
import discord
from discord import app_commands
from discord.ext import commands
from database import db

logger = logging.getLogger(__name__)


class FeedsCog(commands.Cog, name="Feeds"):
    """Comandos para gestionar feeds de Twitter/X."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="add-feed", description="Agregar un feed de Twitter/X al canal actual")
    @app_commands.describe(twitter_handle="Handle de Twitter (sin @). Ejemplo: elonmusk")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def add_feed(self, interaction: discord.Interaction, twitter_handle: str):
        """Agrega un feed de Twitter al canal actual."""
        await interaction.response.defer(ephemeral=True)

        guild_id = str(interaction.guild_id)
        channel_id = str(interaction.channel_id)

        # Limpiar el handle (quitar @ si existe)
        handle = twitter_handle.lstrip("@").strip().lower()

        if not handle:
            await interaction.followup.send("❌ Por favor proporciona un handle de Twitter válido.", ephemeral=True)
            return

        try:
            # Verificar si ya existe
            feeds = db.get_feeds(guild_id)
            existing = [f for f in feeds if f["twitter_handle"].lower() == handle]

            if existing:
                await interaction.followup.send(
                    f"⚠️ El feed de **@{handle}** ya está configurado en este servidor.",
                    ephemeral=True
                )
                return

            # Agregar el feed
            db.add_feed(guild_id, channel_id, handle)

            embed = discord.Embed(
                title="✅ Feed agregado exitosamente",
                description=f"Los tweets de **@{handle}** se publicarán en <#{channel_id}>",
                color=discord.Color.green()
            )
            embed.add_field(name="Handle", value=f"@{handle}", inline=True)
            embed.add_field(name="Canal", value=f"<#{channel_id}>", inline=True)
            embed.set_footer(text="TweetShift Bot • estelarlatam.com/plataforma/tweetswift/")

            await interaction.followup.send(embed=embed, ephemeral=True)

            # Log
            db.add_log(guild_id, str(interaction.user.id), "add_feed", f"Added feed: @{handle}")

        except Exception as e:
            logger.error(f"Error adding feed: {e}")
            await interaction.followup.send(f"❌ Error al agregar el feed: {e}", ephemeral=True)

    @app_commands.command(name="remove-feed", description="Eliminar un feed de Twitter/X")
    @app_commands.describe(twitter_handle="Handle de Twitter a eliminar (sin @)")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def remove_feed(self, interaction: discord.Interaction, twitter_handle: str):
        """Elimina un feed de Twitter."""
        await interaction.response.defer(ephemeral=True)

        guild_id = str(interaction.guild_id)
        handle = twitter_handle.lstrip("@").strip().lower()

        try:
            rows_affected = db.remove_feed(guild_id, handle)

            if rows_affected == 0:
                await interaction.followup.send(
                    f"⚠️ No se encontró el feed de **@{handle}** en este servidor.",
                    ephemeral=True
                )
                return

            embed = discord.Embed(
                title="🗑️ Feed eliminado",
                description=f"El feed de **@{handle}** ha sido eliminado.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            db.add_log(guild_id, str(interaction.user.id), "remove_feed", f"Removed feed: @{handle}")

        except Exception as e:
            logger.error(f"Error removing feed: {e}")
            await interaction.followup.send(f"❌ Error al eliminar el feed: {e}", ephemeral=True)

    @app_commands.command(name="list-feeds", description="Ver todos los feeds activos en este servidor")
    async def list_feeds(self, interaction: discord.Interaction):
        """Lista todos los feeds activos."""
        await interaction.response.defer(ephemeral=True)

        guild_id = str(interaction.guild_id)

        try:
            feeds = db.get_feeds(guild_id)

            if not feeds:
                await interaction.followup.send(
                    "📭 No hay feeds configurados en este servidor.\n"
                    "Usa **/add-feed** para agregar uno.",
                    ephemeral=True
                )
                return

            embed = discord.Embed(
                title="📋 Feeds activos",
                description=f"Total: **{len(feeds)}** feeds configurados",
                color=discord.Color.blue()
            )

            for feed in feeds:
                embed.add_field(
                    name=f"@{feed['twitter_handle']}",
                    value=f"Canal: <#{feed['channel_id']}>",
                    inline=False
                )

            embed.set_footer(text="TweetShift Bot • /add-feed para agregar más")
            await interaction.followup.send(embed=embed, ephemeral=True)

        except Exception as e:
            logger.error(f"Error listing feeds: {e}")
            await interaction.followup.send(f"❌ Error al obtener los feeds: {e}", ephemeral=True)

    @app_commands.command(name="set-channel", description="Configurar el canal donde se publicarán los tweets")
    @app_commands.describe(canal="Canal de Discord donde se publicarán los tweets")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def set_channel(self, interaction: discord.Interaction, canal: discord.TextChannel):
        """Configura el canal de destino para los tweets."""
        await interaction.response.defer(ephemeral=True)

        guild_id = str(interaction.guild_id)

        try:
            db.set_channel(guild_id, str(canal.id), canal.name, "tweets")

            embed = discord.Embed(
                title="✅ Canal configurado",
                description=f"Los tweets se publicarán en {canal.mention}",
                color=discord.Color.green()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            db.add_log(guild_id, str(interaction.user.id), "set_channel", f"Set channel: #{canal.name}")

        except Exception as e:
            logger.error(f"Error setting channel: {e}")
            await interaction.followup.send(f"❌ Error al configurar el canal: {e}", ephemeral=True)

    @add_feed.error
    @remove_feed.error
    @set_channel.error
    async def permission_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                "❌ Necesitas el permiso **Gestionar Canales** para usar este comando.",
                ephemeral=True
            )


async def setup(bot: commands.Bot):
    await bot.add_cog(FeedsCog(bot))
