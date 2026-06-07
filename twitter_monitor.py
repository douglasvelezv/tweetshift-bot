"""
twitter_monitor.py - Monitor de feeds de Twitter/X con Tweepy
TweetShift Bot
"""
import os
import logging
from datetime import datetime, timezone
import tweepy
import discord
from discord.ext import tasks, commands
from database import db

logger = logging.getLogger(__name__)


def get_twitter_client():
    """Crea y retorna el cliente de Twitter API v2."""
    bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
    if not bearer_token:
        raise ValueError("TWITTER_BEARER_TOKEN no configurado")
    return tweepy.Client(
        bearer_token=bearer_token,
        wait_on_rate_limit=True
    )


class TwitterMonitor(commands.Cog):
    """Monitor de feeds de Twitter/X."""

    def __init__(self, bot: discord.Client):
        self.bot = bot
        self.twitter_client = None
        self._setup_client()
        self.check_feeds.start()

    def _setup_client(self):
        """Inicializa el cliente de Twitter."""
        try:
            self.twitter_client = get_twitter_client()
            logger.info("Cliente de Twitter API v2 inicializado")
        except Exception as e:
            logger.error(f"Error iniciando Twitter client: {e}")

    async def get_latest_tweets(self, handle: str, since_id: str = None) -> list:
        """Obtiene los tweets mas recientes usando search_recent_tweets."""
        try:
            query = f"from:{handle} -is:retweet -is:reply"
            params = {
                "query": query,
                "max_results": 10,
                "tweet_fields": ["created_at", "text", "author_id", "public_metrics"],
            }
            if since_id:
                params["since_id"] = since_id

            response = self.twitter_client.search_recent_tweets(**params)
            if response.data:
                return response.data
        except tweepy.errors.TooManyRequests:
            logger.warning("Rate limit alcanzado en Twitter API")
        except Exception as e:
            logger.error(f"Error obteniendo tweets para @{handle}: {e}")
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
        embed.set_footer(text="Twitter/X | TweetShift Bot")

        if hasattr(tweet, "public_metrics") and tweet.public_metrics:
            metrics = tweet.public_metrics
            likes = metrics.get("like_count", 0)
            rts = metrics.get("retweet_count", 0)
            embed.add_field(name="Stats", value=f"Likes: {likes} | RT: {rts}", inline=True)

        return embed

    @tasks.loop(seconds=60)
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
                handle = feed.get("twitter_handle")
                channel_id = feed.get("channel_id")
                last_tweet_id = feed.get("last_tweet_id")

                if not handle or not channel_id:
                    continue

                channel = self.bot.get_channel(int(channel_id))
                if not channel:
                    logger.warning(f"Canal {channel_id} no encontrado")
                    continue

                tweets = await self.get_latest_tweets(handle, since_id=last_tweet_id)
                if not tweets:
                    continue

                tweets_sorted = sorted(tweets, key=lambda t: t.id)
                new_last_id = None

                for tweet in tweets_sorted:
                    try:
                        embed = await self.build_tweet_embed(tweet, handle)
                        await channel.send(embed=embed)
                        new_last_id = str(tweet.id)
                        logger.info(f"Tweet publicado: @{handle} tweet {tweet.id}")
                    except Exception as e:
                        logger.error(f"Error enviando tweet al canal: {e}")

                if new_last_id:
                    db.update_last_tweet(handle, new_last_id)

        except Exception as e:
            logger.error(f"Error en check_feeds: {e}")

    @check_feeds.before_loop
    async def before_check_feeds(self):
        """Espera a que el bot este listo antes de iniciar el loop."""
        await self.bot.wait_until_ready()
        logger.info("TwitterMonitor iniciado y esperando tweets...")


async def setup(bot: commands.Bot):
    await bot.add_cog(TwitterMonitor(bot))
