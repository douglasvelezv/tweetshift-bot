"""
bot.py - Clase principal del TweetShift Bot
"""
import os
import logging
import discord
from discord.ext import commands, tasks
from database import db

logger = logging.getLogger(__name__)


class TweetShiftBot(commands.Bot):
    """Bot principal de TweetShift."""

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True

        super().__init__(
            command_prefix=os.getenv("BOT_PREFIX", "/"),
            intents=intents,
            help_command=None,
            description="TweetShift - Bot de feeds de Twitter/X para Discord"
        )

    async def setup_hook(self):
        """Carga los cogs y sincroniza los comandos slash."""
        cogs = [
            "cogs.setup",
            "cogs.feeds",
            "cogs.help",
            "cogs.twitter_monitor",
        ]
        for cog in cogs:
            try:
                await self.load_extension(cog)
                logger.info(f"Cog cargado: {cog}")
            except Exception as e:
                logger.error(f"Error cargando cog {cog}: {e}")

        # Sincronizar comandos slash globalmente
        try:
            synced = await self.tree.sync()
            logger.info(f"Sincronizados {len(synced)} comandos slash")
        except Exception as e:
            logger.error(f"Error sincronizando comandos: {e}")

    async def on_ready(self):
        """Evento cuando el bot está listo."""
        logger.info(f"Bot conectado como: {self.user} (ID: {self.user.id})")
        logger.info(f"Servidores conectados: {len(self.guilds)}")

        # Establecer estado del bot
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name="feeds de Twitter/X | /help"
        )
        await self.change_presence(activity=activity, status=discord.Status.online)

        # Verificar conexion a BD
        try:
            if db.test_connection():
                logger.info("Conexion a MySQL establecida correctamente")
            else:
                logger.warning("No se pudo conectar a MySQL")
        except Exception as e:
            logger.error(f"Error verificando BD: {e}")

    async def on_guild_join(self, guild: discord.Guild):
        """Cuando el bot se une a un nuevo servidor."""
        logger.info(f"Nuevo servidor: {guild.name} (ID: {guild.id})")
        try:
            db.register_server(str(guild.id), guild.name)
        except Exception as e:
            logger.error(f"Error registrando servidor {guild.id}: {e}")

    async def on_guild_remove(self, guild: discord.Guild):
        """Cuando el bot es removido de un servidor."""
        logger.info(f"Removido del servidor: {guild.name} (ID: {guild.id})")

    async def on_command_error(self, ctx, error):
        """Manejo global de errores de comandos."""
        if isinstance(error, commands.CommandNotFound):
            return
        logger.error(f"Error en comando: {error}")

    async def on_application_command_error(self, interaction: discord.Interaction, error: Exception):
        """Manejo de errores en comandos slash."""
        logger.error(f"Error en slash command: {error}")
        if not interaction.response.is_done():
            await interaction.response.send_message(
                "❌ Ocurrió un error. Por favor intenta de nuevo.",
                ephemeral=True
            )
