import os
import re
import signal
import sys
import logging
import threading
from urllib.parse import urlsplit, urlunsplit, quote
from datetime import datetime, timezone
from flask import Flask, jsonify, request

# Константы ENV
ENV_STU_ID = os.getenv("STU_ID", "220018")
ENV_STU_GROUP = os.getenv("STU_GROUP", "АС-63")
ENV_STU_VARIANT = os.getenv("STU_VARIANT", "14")

PORT = int(os.getenv("APP_PORT", "8062"))
HOST = os.getenv("APP_HOST", "0.0.0.0")

app = Flask(__name__)

# Настройка логгера
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger("app")

shutdown_requested = threading.Event()


def _mask_db_url(url: str) -> str:
    """Вернуть URL базы данных с замаскированным паролем.

    Пытается распарсить URL стандартного формата схемы (например, postgresql://user:pass@host:port/db)
    и заменить пароль на '***'. Если пароля нет или формат нестандартный, возвращает исходный URL
    либо использует безопасную замену по шаблону как запасной вариант.
    """
    try:
        parts = urlsplit(url)
        if not parts.netloc:
            return url

        username = parts.username
        hostname = parts.hostname or ""
        port = parts.port

        # Сборка userinfo: username[:***]@
        userinfo = None
        if username is not None:
            userinfo = quote(username)
            if parts.password is not None:
                userinfo = f"{userinfo}:***"

        # IPv6: оборачиваем в квадратные скобки при необходимости
        netloc_host = hostname
        if ":" in hostname and not hostname.startswith("["):
            netloc_host = f"[{hostname}]"

        hostport = f"{netloc_host}:{port}" if port is not None else netloc_host
        netloc = f"{userinfo}@{hostport}" if userinfo is not None else hostport

        return urlunsplit((parts.scheme, netloc, parts.path, parts.query, parts.fragment))
    except Exception:
        # Запасной вариант: грубая маска по шаблону :password@
        return re.sub(r":([^:@/]+)@", r":***@", url)


def log_startup_metadata():
    logger.info("==== Application Startup ====")
    logger.info("Student ID: %s", ENV_STU_ID)
    logger.info("Student Group: %s", ENV_STU_GROUP)
    logger.info("Student Variant: %s", ENV_STU_VARIANT)
    # DB connection info (masked) if available
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        safe_url = _mask_db_url(db_url)
        logger.info("DATABASE_URL: %s", safe_url)
    for k, v in os.environ.items():
        if k.startswith("STU_"):
            logger.info("ENV %s=%s", k, v)
    logger.info("================================")


@app.route("/healthz", methods=["GET"])  # Health endpoint
def healthz():
    return jsonify({"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}), 200


@app.route("/")
def index():
    return jsonify(
        {
            "message": "Flask service for containerization lab (variant 14)",
            "student": {
                "id": ENV_STU_ID,
                "group": ENV_STU_GROUP,
                "variant": ENV_STU_VARIANT,
            },
            "health": "/healthz",
        }
    )


@app.route("/echo", methods=["POST"])  # small helper endpoint
def echo():
    data = request.get_json(silent=True) or {}
    return jsonify({"echo": data, "received_at": datetime.now(timezone.utc).isoformat()})


def initiate_graceful_shutdown(signum: int, _frame):
    """Обработчик сигнала для корректного завершения работы.

    Аргументы:
        signum (int): номер полученного сигнала.
        _frame: текущий фрейм стека (не используется).
    """
    logger.warning("Received signal %s - initiating graceful shutdown...", signum)
    if not shutdown_requested.is_set():
        logger.info("Stop accepting new connections. Shutdown flag set.")
    shutdown_requested.set()


# Flask dev server не умеет корректно ловить SIGTERM внутри reloader, поэтому используем встроенный сервер без reloader.

SERVER_TIMEOUT = 1  # seconds timeout for per-request wait inside handle_request

def run_server():
    log_startup_metadata()
    logger.info("Starting Flask server on %s:%d", HOST, PORT)
    # Импортируем внутри чтобы не мешать Werkzeug перехватывать сигналы
    from werkzeug.serving import make_server

    http_server = make_server(HOST, PORT, app)
    http_server.timeout = SERVER_TIMEOUT

    try:
        # Главный цикл: обрабатываем по одному запросу с таймаутом.
        # handle_request() блокируется максимум на http_server.timeout секунд,
        # что позволяет регулярно проверять флаг завершения.
        while not shutdown_requested.is_set():
            http_server.handle_request()
    except KeyboardInterrupt:
        logger.warning("KeyboardInterrupt caught. Shutting down...")
        shutdown_requested.set()

    logger.info("Graceful shutdown complete.")


def main():
    signal.signal(signal.SIGTERM, initiate_graceful_shutdown)
    signal.signal(signal.SIGINT, initiate_graceful_shutdown)
    run_server()


if __name__ == "__main__":
    main()
