"""
database.py - Modulo de conexion y operaciones de base de datos MySQL
TweetShift Bot
"""
import os
import logging
import mysql.connector
from mysql.connector import Error, pooling
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class DatabaseManager:
    """Gestor de conexion a MySQL con connection pooling."""

    def __init__(self):
        self.pool = None
        self._create_pool()

    def _create_pool(self):
        """Crea el pool de conexiones a MySQL."""
        try:
            self.pool = pooling.MySQLConnectionPool(
                pool_name="tweetshift_pool",
                pool_size=5,
                pool_reset_session=True,
                host=os.getenv("DB_HOST", "auth-db1439.hstgr.io"),
                port=int(os.getenv("DB_PORT", 3306)),
                database=os.getenv("DB_NAME", "u670415175_tweetswift"),
                user=os.getenv("DB_USER", "u670415175_tweetswift"),
                password=os.getenv("DB_PASSWORD"),
                charset="utf8mb4",
                use_unicode=True,
                autocommit=True,
                connect_timeout=30,
            )
            logger.info("Pool de conexiones MySQL creado exitosamente.")
        except Error as e:
            logger.error(f"Error creando pool de conexiones: {e}")
            raise

    def get_connection(self):
        """Obtiene una conexion del pool."""
        try:
            return self.pool.get_connection()
        except Error as e:
            logger.error(f"Error obteniendo conexion: {e}")
            raise

    def execute_query(self, query: str, params: tuple = None, fetch: bool = False):
        """Ejecuta una query con manejo de errores."""
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, params or ())
            if fetch:
                return cursor.fetchall()
            conn.commit()
            return cursor.rowcount
        except Error as e:
            logger.error(f"Error ejecutando query: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    # ===== SERVERS =====
    def register_server(self, guild_id: str, guild_name: str):
        query = """INSERT INTO servers (guild_id, guild_name)
                   VALUES (%s, %s)
                   ON DUPLICATE KEY UPDATE guild_name=%s, is_active=1"""
        return self.execute_query(query, (guild_id, guild_name, guild_name))

    def get_server(self, guild_id: str):
        query = "SELECT * FROM servers WHERE guild_id = %s"
        result = self.execute_query(query, (guild_id,), fetch=True)
        return result[0] if result else None

    # ===== TWITTER FEEDS =====
    def add_feed(self, guild_id: str, channel_id: str, twitter_handle: str):
        query = """INSERT INTO twitter_feeds (guild_id, channel_id, twitter_handle)
                   VALUES (%s, %s, %s)"""
        return self.execute_query(query, (guild_id, channel_id, twitter_handle))

    def remove_feed(self, guild_id: str, twitter_handle: str):
        query = """UPDATE twitter_feeds SET is_active = 0
                   WHERE guild_id = %s AND twitter_handle = %s"""
        return self.execute_query(query, (guild_id, twitter_handle))

    def get_feeds(self, guild_id: str):
        query = """SELECT * FROM twitter_feeds
                   WHERE guild_id = %s AND is_active = 1"""
        return self.execute_query(query, (guild_id,), fetch=True)

    def get_all_active_feeds(self):
        query = """SELECT tf.*, c.channel_id as dest_channel
                   FROM twitter_feeds tf
                   LEFT JOIN channels c ON tf.guild_id = c.guild_id AND c.channel_type='tweets'
                   WHERE tf.is_active = 1"""
        return self.execute_query(query, fetch=True)

    def update_last_tweet(self, feed_id: int, tweet_id: str):
        query = "UPDATE twitter_feeds SET last_tweet_id = %s WHERE id = %s"
        return self.execute_query(query, (tweet_id, feed_id))

    # ===== CHANNELS =====
    def set_channel(self, guild_id: str, channel_id: str, channel_name: str, channel_type: str = "tweets"):
        query = """INSERT INTO channels (guild_id, channel_id, channel_name, channel_type)
                   VALUES (%s, %s, %s, %s)
                   ON DUPLICATE KEY UPDATE channel_name=%s, is_active=1"""
        return self.execute_query(query, (guild_id, channel_id, channel_name, channel_type, channel_name))

    def get_channel(self, guild_id: str, channel_type: str = "tweets"):
        query = """SELECT * FROM channels
                   WHERE guild_id = %s AND channel_type = %s AND is_active = 1"""
        result = self.execute_query(query, (guild_id, channel_type), fetch=True)
        return result[0] if result else None

    # ===== LOGS =====
    def add_log(self, guild_id: str, user_id: str, action: str, details: str = None, level: str = "INFO"):
        query = """INSERT INTO logs (guild_id, user_id, action, details, level)
                   VALUES (%s, %s, %s, %s, %s)"""
        return self.execute_query(query, (guild_id, user_id, action, details, level))

    def test_connection(self) -> bool:
        """Prueba la conexion a la base de datos."""
        try:
            result = self.execute_query("SELECT 1 AS test", fetch=True)
            return result[0]["test"] == 1
        except Exception:
            return False


# Instancia global
db = DatabaseManager()
