"""
health.py - Servidor de Health Check para Railway
TweetShift Bot
"""
import os
import json
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime

logger = logging.getLogger(__name__)

START_TIME = datetime.utcnow()


class HealthCheckHandler(BaseHTTPRequestHandler):
    """Handler para el endpoint de health check."""

    def do_GET(self):
        if self.path in ("/health", "/", "/ping"):
            self._respond_health()
        elif self.path == "/status":
            self._respond_status()
        else:
            self._respond_404()

    def _respond_health(self):
        uptime = (datetime.utcnow() - START_TIME).total_seconds()
        response = {
            "status": "ok",
            "bot": "TweetShift",
            "version": "1.0.0",
            "uptime_seconds": int(uptime),
            "timestamp": datetime.utcnow().isoformat()
        }
        self._send_json(200, response)

    def _respond_status(self):
        uptime = (datetime.utcnow() - START_TIME).total_seconds()
        hours, remainder = divmod(int(uptime), 3600)
        minutes, seconds = divmod(remainder, 60)
        response = {
            "status": "running",
            "bot_name": "TweetShift",
            "platform": "Railway",
            "uptime": f"{hours}h {minutes}m {seconds}s",
            "environment": os.getenv("RAILWAY_ENVIRONMENT", "development"),
            "timestamp": datetime.utcnow().isoformat()
        }
        self._send_json(200, response)

    def _respond_404(self):
        self._send_json(404, {"error": "Not found"})

    def _send_json(self, status_code: int, data: dict):
        response_body = json.dumps(data).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(response_body))
        self.end_headers()
        self.wfile.write(response_body)

    def log_message(self, format, *args):
        # Suprimir logs HTTP para no saturar el log
        pass


def start_health_server(port: int = 8080):
    """Inicia el servidor HTTP de health check."""
    try:
        server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
        logger.info(f"Health check server iniciado en http://0.0.0.0:{port}")
        server.serve_forever()
    except Exception as e:
        logger.error(f"Error en health check server: {e}")


# Para uso con uvicorn (Procfile web process)
try:
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse

    app = FastAPI(title="TweetShift Health Check")

    @app.get("/health")
    @app.get("/")
    async def health():
        uptime = (datetime.utcnow() - START_TIME).total_seconds()
        return JSONResponse({
            "status": "ok",
            "bot": "TweetShift",
            "version": "1.0.0",
            "uptime_seconds": int(uptime),
            "timestamp": datetime.utcnow().isoformat()
        })

    @app.get("/ping")
    async def ping():
        return {"ping": "pong", "timestamp": datetime.utcnow().isoformat()}

except ImportError:
    app = None
