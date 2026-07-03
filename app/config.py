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


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
