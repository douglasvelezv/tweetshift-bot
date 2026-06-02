-- =============================================
-- TweetShift Bot - Script de Base de Datos
-- Base de datos: u670415175_tweetswift
-- =============================================

CREATE DATABASE IF NOT EXISTS u670415175_tweetswift
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE u670415175_tweetswift;

-- Tabla: servers
CREATE TABLE IF NOT EXISTS servers (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    guild_id VARCHAR(20) NOT NULL UNIQUE,
    guild_name VARCHAR(100) NOT NULL,
    prefix VARCHAR(5) DEFAULT '/',
    is_active TINYINT(1) DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    INDEX idx_guild_id (guild_id)
  ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla: channels
CREATE TABLE IF NOT EXISTS channels (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    guild_id VARCHAR(20) NOT NULL,
    channel_id VARCHAR(20) NOT NULL,
    channel_name VARCHAR(100),
    channel_type ENUM('tweets','announcements','logs') DEFAULT 'tweets',
    is_active TINYINT(1) DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY unique_guild_channel (guild_id, channel_id),
    INDEX idx_guild_id (guild_id)
  ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla: twitter_feeds
CREATE TABLE IF NOT EXISTS twitter_feeds (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    guild_id VARCHAR(20) NOT NULL,
    channel_id VARCHAR(20) NOT NULL,
    twitter_handle VARCHAR(50) NOT NULL,
    twitter_user_id VARCHAR(30),
    last_tweet_id VARCHAR(30),
    is_active TINYINT(1) DEFAULT 1,
    check_interval INT DEFAULT 300,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY unique_guild_handle (guild_id, twitter_handle),
    INDEX idx_guild_id (guild_id),
    INDEX idx_active (is_active)
  ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla: users
CREATE TABLE IF NOT EXISTS users (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    discord_user_id VARCHAR(20) NOT NULL UNIQUE,
    username VARCHAR(100) NOT NULL,
    discriminator VARCHAR(10),
    guild_id VARCHAR(20),
    role ENUM('admin','moderator','user') DEFAULT 'user',
    is_active TINYINT(1) DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    INDEX idx_discord_user_id (discord_user_id)
  ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla: settings
CREATE TABLE IF NOT EXISTS settings (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    guild_id VARCHAR(20) NOT NULL,
    setting_key VARCHAR(50) NOT NULL,
    setting_value TEXT,
    description VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY unique_guild_setting (guild_id, setting_key),
    INDEX idx_guild_id (guild_id)
  ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla: logs
CREATE TABLE IF NOT EXISTS logs (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    guild_id VARCHAR(20),
    user_id VARCHAR(20),
    action VARCHAR(100) NOT NULL,
    details TEXT,
    level ENUM('INFO','WARNING','ERROR','DEBUG') DEFAULT 'INFO',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    INDEX idx_guild_id (guild_id),
    INDEX idx_created_at (created_at),
    INDEX idx_level (level)
  ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================
-- Indices adicionales para performance
-- =============================================
CREATE INDEX idx_feeds_active_guild ON twitter_feeds (is_active, guild_id);
CREATE INDEX idx_logs_guild_date ON logs (guild_id, created_at);

-- =============================================
-- Datos iniciales de configuracion global
-- =============================================
INSERT IGNORE INTO settings (guild_id, setting_key, setting_value, description)
VALUES 
  ('GLOBAL', 'bot_version', '1.0.0', 'Version actual del bot'),
  ('GLOBAL', 'max_feeds_per_server', '10', 'Maximo de feeds por servidor'),
  ('GLOBAL', 'default_check_interval', '300', 'Intervalo de chequeo en segundos'),
  ('GLOBAL', 'tweet_format', 'embed', 'Formato de publicacion: embed o text');

SELECT 'Base de datos TweetShift creada exitosamente!' AS mensaje;
