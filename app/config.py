import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Проект работает на MySQL. DATABASE_URL обязателен (без тихого fallback
# на SQLite) — пример: mysql+pymysql://user:password@localhost/mafia_style?charset=utf8mb4
SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
if not SQLALCHEMY_DATABASE_URI:
    raise RuntimeError(
        "DATABASE_URL не задан. Пример для MySQL: "
        "mysql+pymysql://user:password@localhost/mafia_style?charset=utf8mb4"
    )


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-prod")
    SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        # MySQL закрывает простаивающие соединения (wait_timeout) — без
        # pool_recycle это со временем даёт "MySQL server has gone away".
        "pool_recycle": 280,
    }

    # Telegram Login Widget (привязка аккаунта к боту-клиенту) — опционально,
    # без него сайт работает как обычно, просто кнопка привязки не
    # показывается (тот же принцип, что MIGRATION_API_ENABLED: отсутствие
    # переменной выключает фичу, а не роняет приложение).
    # TELEGRAM_BOT_TOKEN нужен здесь для проверки HMAC-подписи виджета
    # (см. AuthService.verify_telegram_login_data) — это требование
    # протокола Login Widget, не только бот его использует.
    TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
    TELEGRAM_BOT_USERNAME = os.environ.get("TELEGRAM_BOT_USERNAME")

    # Fire-and-forget уведомления сайта -> бота (см. BotNotifyService) —
    # опционально по тому же принципу: без обеих переменных уведомления
    # просто не отправляются (тихо логируется), остальной сайт не ломается.
    BOT_EVENTS_URL = os.environ.get("BOT_EVENTS_URL")  # напр. https://<бот>.pythonanywhere.com
    INCOMING_EVENT_SECRET = os.environ.get("INCOMING_EVENT_SECRET")


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
