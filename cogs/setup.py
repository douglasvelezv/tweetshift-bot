"""
cogs/setup.py - Comandos de configuracion del servidor
TweetShift Bot
"""
import logging
import discord
from discord import app_commands
from discord.ext import commands
from database import db

logger = logging.getLogger(__name__)


class SetupCog(commands.Cog, name="Setup"):
    """Comandos de configuracion del servidor."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="setup", description="Configurar TweetShift en este servidor")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup(self, interaction: discord.Interaction):
        """Configura el bot en el servidor."""
        await interaction.response.defer(ephemeral=True)

        guild = interaction.guild
        guild_id = str(guild.id)

        try:
            # Registrar servidor en BD
            db.register_server(guild_id, guild.name)

            embed = discord.Embed(
                title="🚀 TweetShift configurado exitosamente",
                description=(
                    f"¡Bienvenido a **TweetShift**, {guild.name}!\n\n"
                    "El bot ha sido configurado en tu servidor.\n"
                    "Usa los comandos a continuación para empezar:"
                ),
                color=discord.Color.blue()
            )
            embed.add_field(
                name="📌 Próximos pasos:",
                value=(
                    "1. **/set-channel #canal** — Configura el canal de destino\n"
                    "2. **/add-feed handle** — Agrega un feed de Twitter/X\n"
                    "3. **/list-feeds** — Ver feeds activos\n"
                    "4. **/help** — Ver todos los comandos"
                ),
                inline=False
            )
            embed.add_field(
                name="🌐 Web",
                value="[estelarlatam.com/plataforma/tweetswift/](https://estelarlatam.com/plataforma/tweetswift/)",
                inline=True
            )
            embed.set_thumbnail(url=self.bot.user.avatar.url if self.bot.user.avatar else None)
            embed.set_footer(text="TweetShift Bot v1.0.0")

            await interaction.followup.send(embed=embed, ephemeral=True)
            db.add_log(guild_id, str(interaction.user.id), "setup", f"Server setup: {guild.name}")

        except Exception as e:
            logger.error(f"Error in setup: {e}")
            await interaction.followup.send(f"❌ Error durante la configuración: {e}", ephemeral=True)

    @app_commands.command(name="info", description="Ver información del bot y estadísticas del servidor")
    async def info(self, interaction: discord.Interaction):
        """Muestra información del bot."""
        await interaction.response.defer(ephemeral=True)

        guild_id = str(interaction.guild_id)
        guild = interaction.guild

        try:
            feeds = db.get_feeds(guild_id)
            channel = db.get_channel(guild_id)

            embed = discord.Embed(
                title="ℹ️ TweetShift Bot - Información",
                color=discord.Color.blue()
            )
            embed.add_field(name="Bot", value=f"{self.bot.user.name}", inline=True)
            embed.add_field(name="Versión", value="1.0.0", inline=True)
            embed.add_field(name="Servidores", value=str(len(self.bot.guilds)), inline=True)
            embed.add_field(name="Feeds activos", value=str(len(feeds)), inline=True)
            embed.add_field(
                name="Canal configurado",
                value=f"<#{channel['channel_id']}>" if channel else "No configurado",
                inline=True
            )
            embed.add_field(name="Servidor", value=guild.name, inline=True)
            embed.add_field(
                name="🌐 Página web",
                value="[estelarlatam.com/plataforma/tweetswift/](https://estelarlatam.com/plataforma/tweetswift/)",
                inline=False
            )
            embed.set_footer(text="TweetShift Bot • Powered by Railway")

            await interaction.followup.send(embed=embed, ephemeral=True)

        except Exception as e:
            logger.error(f"Error in info: {e}")
            await interaction.followup.send(f"❌ Error: {e}", ephemeral=True)

    @setup.error
    async def setup_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                "❌ Necesitas permisos de **Administrador** para usar este comando.",
                ephemeral=True
            )


async def setup(bot: commands.Bot):
    await bot.add_cog(SetupCog(bot))
