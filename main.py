"""
main.py - Punto de entrada principal del TweetShift Bot
"""
import os
import asyncio
import logging
import threading
from dotenv import load_dotenv

import discord
from discord.ext import commands
from bot import TweetShiftBot
from health import start_health_server

# Cargar variables de entorno
load_dotenv()

# Configurar logging
logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)


async def main():
    """Funcion principal del bot."""
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        logger.error("DISCORD_TOKEN no configurado en .env")
        raise ValueError("DISCORD_TOKEN es requerido")

    # Iniciar servidor de health check en hilo separado
    port = int(os.getenv("PORT", os.getenv("HEALTH_CHECK_PORT", 8080)))
    health_thread = threading.Thread(
        target=start_health_server,
        args=(port,),
        daemon=True
    )
    health_thread.start()
    logger.info(f"Health check server iniciado en puerto {port}")

    # Iniciar el bot
    bot = TweetShiftBot()
    logger.info("Iniciando TweetShift Bot...")

    try:
        await bot.start(token)
    except KeyboardInterrupt:
        logger.info("Deteniendo el bot...")
    finally:
        if not bot.is_closed():
            await bot.close()


if __name__ == "__main__":
    asyncio.run(main())
