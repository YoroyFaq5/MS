"""
Миграция: live-пульт для карточек игроков на оверлее + протокол игры.

Запустить один раз на существующей базе:

    python migrate_live_game_control.py

Добавляет:
  - games.live_phase (ENUM('night','day') NULL), games.live_turn (INT NULL)
  - game_slots.elimination_type (ENUM('killed','voted') NULL)
  - game_slots.live_role (тот же ENUM, что и у существующей role-колонки)
  - новую таблицу game_events (протокол live-событий)

Все новые колонки NULL по умолчанию — ничего не меняется для уже
существующих игр/слотов, пока ведущий явно не воспользуется новым
пультом (app/services/live_game_control_service.py).

Безопасно перезапускать: каждый шаг проверяет текущее состояние схемы
перед изменением.
"""
from app import create_app, db
from sqlalchemy import text

app = create_app("development")


def column_exists(conn, table: str, column: str) -> bool:
    return bool(conn.execute(text(
        "SELECT COUNT(*) FROM information_schema.columns "
        "WHERE table_schema = DATABASE() AND table_name = :t AND column_name = :c"
    ), {"t": table, "c": column}).scalar())


def table_exists(conn, table: str) -> bool:
    return bool(conn.execute(text(
        "SELECT COUNT(*) FROM information_schema.tables "
        "WHERE table_schema = DATABASE() AND table_name = :t"
    ), {"t": table}).scalar())


with app.app_context():
    with db.engine.connect() as conn:
        if column_exists(conn, "games", "live_phase"):
            print("Пропущено: games.live_phase уже существует.")
        else:
            conn.execute(text(
                "ALTER TABLE games ADD COLUMN live_phase ENUM('night','day') NULL;"
            ))
            conn.commit()
            print("OK: добавлена колонка games.live_phase.")

        if column_exists(conn, "games", "live_turn"):
            print("Пропущено: games.live_turn уже существует.")
        else:
            conn.execute(text(
                "ALTER TABLE games ADD COLUMN live_turn INT NULL;"
            ))
            conn.commit()
            print("OK: добавлена колонка games.live_turn.")

        if column_exists(conn, "game_slots", "elimination_type"):
            print("Пропущено: game_slots.elimination_type уже существует.")
        else:
            conn.execute(text(
                "ALTER TABLE game_slots ADD COLUMN elimination_type ENUM('killed','voted') NULL;"
            ))
            conn.commit()
            print("OK: добавлена колонка game_slots.elimination_type.")

        if column_exists(conn, "game_slots", "live_role"):
            print("Пропущено: game_slots.live_role уже существует.")
        else:
            conn.execute(text(
                "ALTER TABLE game_slots ADD COLUMN live_role "
                "ENUM('civilian','mafia','don','sheriff') NULL;"
            ))
            conn.commit()
            print("OK: добавлена колонка game_slots.live_role.")

        if table_exists(conn, "game_events"):
            print("Пропущено: таблица game_events уже существует.")
        else:
            conn.execute(text("""
                CREATE TABLE game_events (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    game_id INT NOT NULL,
                    slot_id INT NULL,
                    event_type ENUM('killed','voted','revived','role_revealed','phase_changed') NOT NULL,
                    phase ENUM('night','day') NULL,
                    turn_number INT NULL,
                    admin_id INT NULL,
                    created_at DATETIME NOT NULL,
                    revoked_at DATETIME NULL,
                    revoked_by_admin_id INT NULL,
                    CONSTRAINT fk_game_events_game FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE,
                    CONSTRAINT fk_game_events_slot FOREIGN KEY (slot_id) REFERENCES game_slots(id) ON DELETE CASCADE,
                    CONSTRAINT fk_game_events_admin FOREIGN KEY (admin_id) REFERENCES users(id),
                    CONSTRAINT fk_game_events_revoked_by FOREIGN KEY (revoked_by_admin_id) REFERENCES users(id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """))
            conn.commit()
            print("OK: создана таблица game_events.")

print("Готово.")
