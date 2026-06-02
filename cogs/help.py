"""
cogs/help.py - Comandos de ayuda del TweetShift Bot
"""
import logging
import discord
from discord import app_commands
from discord.ext import commands

logger = logging.getLogger(__name__)


class HelpCog(commands.Cog, name="Ayuda"):
    """Comandos de ayuda e informacion."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="help", description="Ver todos los comandos disponibles de TweetShift")
    async def help_command(self, interaction: discord.Interaction):
        """Muestra el menu de ayuda."""
        await interaction.response.defer(ephemeral=True)

        embed = discord.Embed(
            title="TweetShift Bot - Comandos",
            description="TweetShift publica automaticamente tweets de Twitter/X en tus canales de Discord.",
            color=discord.Color.blue()
        )

        embed.add_field(
            name="Configuracion",
            value="/setup - Iniciar configuracion del bot en tu servidor\n/set-channel #canal - Definir canal donde se publicaran tweets\n/info - Ver informacion y estadisticas",
            inline=False
        )

        embed.add_field(
            name="Feeds de Twitter/X",
            value="/add-feed handle - Agregar feed\n/remove-feed handle - Eliminar un feed activo\n/list-feeds - Ver todos los feeds configurados",
            inline=False
        )

        embed.add_field(
            name="Permisos requeridos",
            value="/setup, /info: Administrador\n/add-feed, /remove-feed, /set-channel: Gestionar Canales\n/list-feeds, /help, /ping: Todos",
            inline=False
        )

        embed.add_field(
            name="Recursos",
            value="Pagina Web: https://estelarlatam.com/plataforma/tweetswift/\nDocumentacion: https://help.tweetshift.com/",
            inline=False
        )

        embed.set_footer(text="TweetShift v1.0.0 - estelarlatam.com")
        await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name="ping", description="Verificar latencia y estado del bot")
    async def ping(self, interaction: discord.Interaction):
        """Muestra la latencia del bot."""
        latency = round(self.bot.latency * 1000)
        if latency < 100:
            status = "Excelente"
            color = discord.Color.green()
        elif latency < 200:
            status = "Normal"
            color = discord.Color.yellow()
        else:
            status = "Lento"
            color = discord.Color.red()

        embed = discord.Embed(title="Pong!", color=color)
        embed.add_field(name="Latencia", value=f"{latency}ms", inline=True)
        embed.add_field(name="Estado", value=status, inline=True)
        embed.set_footer(text="TweetShift Bot")
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(HelpCog(bot))
