"""
Миграция: создаёт таблицу notify_outbox_events.

Запустить один раз на существующей базе:

    python migrate_notify_outbox.py

Долговечная очередь исходящих уведомлений сайт -> Telegram-бот (см.
app/models::NotifyOutboxEvent, app/services/notify_outbox_service.py).
Заменяет старый полностью синхронный HTTP POST в BotNotifyService —
событие сначала надёжно сохраняется здесь, доставка (с ретраями и
экспоненциальной паузой) выполняется отдельно (`flask outbox-drain` из
cron, либо опциональный фоновый поток при OUTBOX_WORKER_ENABLED=true).

Безопасно перезапускать: перед CREATE TABLE проверяется текущее состояние
схемы.
"""
from app import create_app, db
from sqlalchemy import text

app = create_app("development")

with app.app_context():
    with db.engine.connect() as conn:
        table = "notify_outbox_events"

        existing = conn.execute(text(
            "SELECT COUNT(*) FROM information_schema.tables "
            "WHERE table_schema = DATABASE() AND table_name = :t"
        ), {"t": table}).scalar()

        if existing:
            print(f"Пропущено: таблица {table} уже существует.")
        else:
            conn.execute(text(
                """
                CREATE TABLE notify_outbox_events (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    event_id VARCHAR(36) NOT NULL UNIQUE,
                    event_type VARCHAR(50) NOT NULL,
                    payload TEXT NOT NULL,
                    status ENUM('pending','processing','delivered','failed')
                        NOT NULL DEFAULT 'pending',
                    attempts INT NOT NULL DEFAULT 0,
                    max_attempts INT NOT NULL DEFAULT 8,
                    next_attempt_at DATETIME NOT NULL,
                    last_error TEXT NULL,
                    created_at DATETIME NOT NULL,
                    delivered_at DATETIME NULL,
                    INDEX ix_notify_outbox_events_status_next_attempt (status, next_attempt_at)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                """
            ))
            conn.commit()
            print(f"OK: создана таблица {table}.")

print("Готово.")
