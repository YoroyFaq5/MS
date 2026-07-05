import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()


def create_app(config_name: str = "default") -> Flask:
    from .config import config_map

    app = Flask(__name__)
    app.config.from_object(config_map[config_name])

    db.init_app(app)
    migrate.init_app(app, db)

    # Flask-Login setup
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Войдите в аккаунт для доступа к этой странице."
    login_manager.login_message_category = "warning"

    @login_manager.user_loader
    def load_user(user_id: str):
        from .models.user import User
        return db.session.get(User, int(user_id))

    # current_user_equipped — используется в base.html навбаре (аватар/ник
    # текущего пользователя через player_name()) для ЛЮБОЙ страницы, но ни
    # один роут его не передавал явно — базовый шаблон крашился для любого
    # залогиненного пользователя (equipped.get(...) на Undefined). Один
    # глобальный context_processor вместо "не забыть добавить в каждый
    # render_template" — тот же принцип, что get_equipped_bulk для списков.
    @app.context_processor
    def inject_current_user_equipped():
        from flask_login import current_user as _current_user
        if _current_user.is_authenticated and _current_user.player_id:
            from .services.shop_service import ShopService
            return {"current_user_equipped": ShopService.get_equipped(_current_user.player_id)}
        return {"current_user_equipped": {}}

    # Blueprints
    from .routes.main import main_bp
    from .routes.players import players_bp
    from .routes.games import games_bp
    from .routes.ratings import ratings_bp
    from .routes.tournaments import tournaments_bp
    from .routes.auth import auth_bp
    from .routes.seasons import seasons_bp
    from .routes.api import api_bp
    from .routes.fantasy import fantasy_bp
    from .routes.shop import shop_bp
    from .routes.inventory import inventory_bp
    from .routes.profile import profile_bp
    from .routes.admin_shop import admin_shop_bp
    from .routes.titles import titles_bp
    from .routes.admin_titles import admin_titles_bp
    from .routes.gifts import gifts_bp
    from .routes.admin_analytics import admin_analytics_bp
    from .routes.series_tournaments import series_tournaments_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(players_bp, url_prefix="/players")
    app.register_blueprint(games_bp, url_prefix="/games")
    app.register_blueprint(ratings_bp, url_prefix="/ratings")
    app.register_blueprint(tournaments_bp, url_prefix="/tournaments")
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(seasons_bp, url_prefix="/seasons")
    app.register_blueprint(api_bp, url_prefix="/api")
    app.register_blueprint(fantasy_bp, url_prefix="/fantasy")
    app.register_blueprint(shop_bp, url_prefix="/shop")
    app.register_blueprint(inventory_bp, url_prefix="/inventory")
    app.register_blueprint(profile_bp, url_prefix="/profile")
    app.register_blueprint(admin_shop_bp, url_prefix="/admin/shop")
    app.register_blueprint(titles_bp, url_prefix="/titles")
    app.register_blueprint(admin_titles_bp, url_prefix="/admin/titles")
    app.register_blueprint(gifts_bp, url_prefix="/gifts")
    app.register_blueprint(admin_analytics_bp, url_prefix="/admin/analytics")
    app.register_blueprint(series_tournaments_bp, url_prefix="/series-tournaments")

    # Migration API — только для одноразового переноса данных из старой
    # версии приложения. Регистрируется исключительно при явном
    # MIGRATION_API_ENABLED=true — без этой переменной роутов /migration/*
    # не существует вообще (404, а не 403). После завершения переноса
    # переменную нужно убрать из .env — это и есть выключатель.
    if os.environ.get("MIGRATION_API_ENABLED", "").lower() == "true":
        from .routes.migration import migration_bp
        app.register_blueprint(migration_bp, url_prefix="/migration")

    # 403 handler
    from flask import render_template as rt
    @app.errorhandler(403)
    def forbidden(e):
        return rt("errors/403.html"), 403

    # On startup: ensure current-year seasons exist and close expired ones
    with app.app_context():
        from datetime import datetime, timezone as tz
        try:
            from .services.season_service import SeasonService
            current_year = datetime.now(tz.utc).year
            SeasonService.ensure_year_exists(current_year)
            SeasonService.close_expired_seasons()
        except Exception:
            pass  # Tables may not exist yet on first run (before init-db)

    return app
