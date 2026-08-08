"""
Миграция: добавляет pinned_game_id в overlay_controls.

Запустить один раз на существующей базе:

    python migrate_overlay_control_pinned_game.py

pinned_game_id (INT NULL, FK -> games.id ON DELETE SET NULL) — админ может
закрепить в правой панели «С комментаторами» результат КОНКРЕТНОГО (любого)
тура вместо автоматического "последняя завершённая игра". NULL (значение
по умолчанию) = старое поведение "авто", ничего не меняется для уже идущих
трансляций, пока админ явно не выберет тур на /control или в OBS-панели.

Безопасно перезапускать: перед ALTER TABLE проверяется текущее состояние
схемы.
"""
from app import create_app, db
from sqlalchemy import text

app = create_app("development")

with app.app_context():
    with db.engine.connect() as conn:
        column = "pinned_game_id"

        existing = conn.execute(text(
            "SELECT COUNT(*) FROM information_schema.columns "
            "WHERE table_schema = DATABASE() "
            "AND table_name = 'overlay_controls' AND column_name = :col"
        ), {"col": column}).scalar()

        if existing:
            print(f"Пропущено: overlay_controls.{column} уже существует.")
        else:
            conn.execute(text(
                "ALTER TABLE overlay_controls ADD COLUMN pinned_game_id INT NULL;"
            ))
            conn.execute(text(
                "ALTER TABLE overlay_controls "
                "ADD CONSTRAINT fk_overlay_controls_pinned_game "
                "FOREIGN KEY (pinned_game_id) REFERENCES games(id) ON DELETE SET NULL;"
            ))
            conn.commit()
            print(f"OK: добавлена колонка overlay_controls.{column} + FK на games.id.")

print("Готово.")
