# TweetShift Bot

> Bot de Discord que publica automáticamente feeds de Twitter/X en canales de Discord.

**Página Web:** https://estelarlatam.com/plataforma/tweetswift/
**Documentación oficial:** https://help.tweetshift.com/
**Hosting:** Railway.com

---

## Características

- Monitorea cuentas de Twitter/X y publica nuevos tweets en Discord
- Soporte para múltiples servidores y múltiples feeds por servidor
- Comandos slash (/) modernos de Discord
- Base de datos MySQL para persistencia de datos
- Health check endpoint para Railway
- Embeds personalizados con métricas de los tweets
- Sistema de logs integrado

---

## Estructura del Proyecto

```
tweetshift-bot/
├── main.py                  # Punto de entrada principal
├── bot.py                   # Clase del bot Discord
├── database.py              # Gestor de base de datos MySQL
├── health.py                # Health check para Railway
├── twitter_monitor.py       # Monitor de feeds de Twitter/X
├── cogs/
│   ├── __init__.py
│   ├── feeds.py             # Comandos de feeds
│   ├── setup.py             # Comandos de configuración
│   └── help.py              # Comandos de ayuda
├── database.sql             # Script SQL de tablas
├── requirements.txt         # Dependencias Python
├── Procfile                 # Configuración Railway/Heroku
├── runtime.txt              # Versión de Python
├── railway.json             # Configuración Railway
├── .env.example             # Variables de entorno (ejemplo)
└── .gitignore
```

---

## Requisitos Previos

- Python 3.11+
- MySQL 8.0+ (Hostinger: auth-db1439.hstgr.io)
- Token de Discord Bot
- Twitter API v2 Bearer Token
- Cuenta en Railway.com

---

## Instalación Local

### 1. Clonar el repositorio

```bash
git clone https://github.com/estelar-latam/tweetshift-bot.git
cd tweetshift-bot
```

### 2. Crear entorno virtual

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

```bash
cp .env.example .env
# Editar .env con tus credenciales
```

### 5. Crear tablas en MySQL

```bash
mysql -h auth-db1439.hstgr.io -u u670415175_tweetswift -p u670415175_tweetswift < database.sql
```

### 6. Ejecutar el bot

```bash
python main.py
```

---

## Variables de Entorno (.env)

```env
# Discord
DISCORD_TOKEN=tu_discord_bot_token

# Twitter/X API v2
TWITTER_API_KEY=tu_api_key
TWITTER_API_SECRET=tu_api_secret
TWITTER_BEARER_TOKEN=tu_bearer_token
TWITTER_ACCESS_TOKEN=tu_access_token
TWITTER_ACCESS_TOKEN_SECRET=tu_access_token_secret

# Base de Datos MySQL
DB_HOST=auth-db1439.hstgr.io
DB_USER=u670415175_tweetswift
DB_PASSWORD=tu_password
DB_NAME=u670415175_tweetswift
DB_PORT=3306

# Bot Config
HEALTH_CHECK_PORT=8080
LOG_LEVEL=INFO
FEED_CHECK_INTERVAL=300
```

---

## Comandos Disponibles

| Comando | Descripción | Permiso |
|---------|-------------|---------|
| `/setup` | Configurar el bot en tu servidor | Admin |
| `/set-channel #canal` | Definir canal para tweets | Gestionar Canales |
| `/add-feed handle` | Agregar feed de Twitter/X | Gestionar Canales |
| `/remove-feed handle` | Eliminar un feed | Gestionar Canales |
| `/list-feeds` | Ver feeds activos | Todos |
| `/info` | Ver información del bot | Admin |
| `/help` | Ver ayuda | Todos |
| `/ping` | Verificar latencia | Todos |

---

## Deployment en Railway

### Pasos:

1. **Fork o conecta** el repositorio en Railway.com
2. **Configura las variables de entorno** en el dashboard de Railway
3. **Deploy automático** - Railway detecta el Procfile y railway.json

### Variables en Railway:

En el dashboard de Railway, agrega todas las variables del archivo `.env.example`.

### Health Check:

El bot expone un endpoint en `https://tu-app.railway.app/health` que Railway usa para mantener el bot activo 24/7.

---

## Base de Datos MySQL

**Host:** auth-db1439.hstgr.io
**Database:** u670415175_tweetswift

### Tablas:

- `servers` - Configuración por servidor de Discord
- `twitter_feeds` - Feeds de Twitter/X configurados
- `channels` - Canales de destino
- `users` - Usuarios del bot
- `settings` - Configuración global
- `logs` - Registro de actividades

---

## Cómo obtener las API Keys

### Discord Bot Token
1. Ve a https://discord.com/developers/applications
2. Crea una nueva aplicación
3. Ve a "Bot" y copia el token
4. Activa los Privileged Gateway Intents necesarios

### Twitter API v2
1. Ve a https://developer.twitter.com
2. Crea un proyecto y app
3. Aplica para acceso "Elevated" o usa el Bearer Token Free Tier
4. Copia las credenciales

---

## Tecnologías

- **Python 3.11** - Lenguaje principal
- **discord.py 2.3** - Librería de Discord
- **Tweepy 4.14** - Twitter API v2
- **MySQL Connector Python** - Base de datos
- **FastAPI + Uvicorn** - Health check endpoint
- **Railway** - Hosting 24/7

---

## Soporte

- **Página Web:** https://estelarlatam.com/plataforma/tweetswift/
- **Documentación:** https://help.tweetshift.com/

---

*TweetShift Bot v1.0.0 - estelar-latam*
