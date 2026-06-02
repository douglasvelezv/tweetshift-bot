"""
twitter_monitor.py - Monitor de feeds de Twitter/X con Tweepy
TweetShift Bot
"""
import os
import logging
import asyncio
from datetime import datetime, timezone
import tweepy
import discord
from discord.ext import tasks
from database import db

logger = logging.getLogger(__name__)


def get_twitter_client():
    """Crea y retorna el cliente de Twitter API v2."""
    bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
    if not bearer_token:
        raise ValueError("TWITTER_BEARER_TOKEN no configurado")
    return tweepy.Client(
        bearer_token=bearer_token,
        consumer_key=os.getenv("TWITTER_API_KEY"),
        consumer_secret=os.getenv("TWITTER_API_SECRET"),
        access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
        access_token_secret=os.getenv("TWITTER_ACCESS_TOKEN_SECRET"),
        wait_on_rate_limit=True
    )


class TwitterMonitor:
    """Monitor de feeds de Twitter/X."""

    def __init__(self, bot: discord.Client):
        self.bot = bot
        self.twitter_client = None
        self._setup_client()

    def _setup_client(self):
        """Inicializa el cliente de Twitter."""
        try:
            self.twitter_client = get_twitter_client()
            logger.info("Cliente de Twitter API v2 inicializado")
        except Exception as e:
            logger.error(f"Error iniciando Twitter client: {e}")

    async def get_user_id(self, handle: str) -> str:
        """Obtiene el ID de usuario de Twitter por handle."""
        try:
            user = self.twitter_client.get_user(username=handle)
            if user.data:
                return str(user.data.id)
        except Exception as e:
            logger.error(f"Error obteniendo user_id para @{handle}: {e}")
        return None

    async def get_latest_tweets(self, twitter_user_id: str, since_id: str = None) -> list:
        """Obtiene los tweets mas recientes de un usuario."""
        try:
            params = {
                "id": twitter_user_id,
                "max_results": 5,
                "tweet_fields": ["created_at", "text", "author_id", "public_metrics"],
                "expansions": ["author_id", "attachments.media_keys"],
                "media_fields": ["url", "preview_image_url", "type"],
                "exclude": ["retweets", "replies"]
            }
            if since_id:
                params["since_id"] = since_id

            response = self.twitter_client.get_users_tweets(**params)
            if response.data:
                return response.data
        except tweepy.errors.TooManyRequests:
            logger.warning("Rate limit alcanzado en Twitter API")
        except Exception as e:
            logger.error(f"Error obteniendo tweets: {e}")
        return []

    async def build_tweet_embed(self, tweet, handle: str) -> discord.Embed:
        """Construye un embed de Discord para un tweet."""
        tweet_url = f"https://twitter.com/{handle}/status/{tweet.id}"

        embed = discord.Embed(
            description=tweet.text,
            color=discord.Color.from_rgb(29, 161, 242),
            url=tweet_url,
            timestamp=tweet.created_at if hasattr(tweet, "created_at") else datetime.now(timezone.utc)
        )
        embed.set_author(
            name=f"@{handle}",
            url=f"https://twitter.com/{handle}",
            icon_url="https://abs.twimg.com/icons/apple-touch-icon-192x192.png"
        )
        embed.set_footer(text="Twitter/X • TweetShift Bot")

        if hasattr(tweet, "public_metrics") and tweet.public_metrics:
            metrics = tweet.public_metrics
            embed.add_field(
                name="Stats",
                value=f"Likes: {metrics.get(chr(108)+chr(105)+chr(107)+chr(101)+chr(95)+chr(99)+chr(111)+chr(117)+chr(110)+chr(116), 0)} | RT: {metrics.get(chr(114)+chr(101)+chr(116)+chr(119)+chr(101)+chr(101)+chr(116)+chr(95)+chr(99)+chr(111)+chr(117)+chr(110)+chr(116), 0)}",
                inline=True
            )

        return embed

    async def check_feeds(self):
        """Verifica todos los feeds activos y publica nuevos tweets."""
        if not self.twitter_client:
            logger.warning("Twitter client no disponible")
            return

        try:
            feeds = db.get_all_active_feeds()
            if not feeds:
                return

            for feed in feeds:
                try:
                    handle = feed["twitter_handle"]
                    guild_id = feed["guild_id"]
                    channel_id = feed["channel_id"]
                    last_tweet_id = feed.get("last_tweet_id")

                    # Obtener user_id si no lo tenemos
                    twitter_user_id = feed.get("twitter_user_id")
                    if not twitter_user_id:
                        twitter_user_id = await self.get_user_id(handle)
                        if not twitter_user_id:
                            continue

                    # Obtener tweets nuevos
                    tweets = await self.get_latest_tweets(twitter_user_id, last_tweet_id)

                    if not tweets:
                        continue

                    # Obtener canal de Discord
                    channel = self.bot.get_channel(int(channel_id))
                    if not channel:
                        logger.warning(f"Canal no encontrado: {channel_id}")
                        continue

                    # Publicar tweets en orden cronologico
                    for tweet in reversed(tweets):
                        embed = await self.build_tweet_embed(tweet, handle)
                        await channel.send(embed=embed)
                        await asyncio.sleep(1)

                    # Actualizar last_tweet_id
                    db.update_last_tweet(feed["id"], str(tweets[0].id))

                except Exception as e:
                    logger.error(f"Error procesando feed @{feed.get(chr(116)+chr(119)+chr(105)+chr(116)+chr(116)+chr(101)+chr(114)+chr(95)+chr(104)+chr(97)+chr(110)+chr(100)+chr(108)+chr(101), chr(63))}: {e}")
                    continue

                await asyncio.sleep(2)

        except Exception as e:
            logger.error(f"Error en check_feeds: {e}")
