"""
Миграция для панели управления оверлеем турнира.

Запустить один раз на существующей базе:

    python migrate_overlay_control.py

Создаёт таблицу overlay_controls (по одной строке на турнир, лениво
создаётся при первом обращении — см. OverlayControlService.get_control):
show_ticker (BOOL), standings_mode (top5/full/hidden), reveal_override
(NULL=авто/on/off), updated_at.

Безопасно перезапускать: используется CREATE TABLE IF NOT EXISTS.
"""
from app import create_app, db
from app.models import OverlayControl

app = create_app("development")

with app.app_context():
    OverlayControl.__table__.create(bind=db.engine, checkfirst=True)
    print("OK: таблица overlay_controls готова (создана или уже существовала).")

print("Готово.")
