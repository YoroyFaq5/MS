"""
Одноразовый фикс: конвертирует все таблицы текущей БД в utf8mb4, устраняя
'Illegal mix of collations'. Безопасно — CONVERT TO CHARACTER SET не удаляет
данные (utf8mb3 является строгим подмножеством utf8mb4).

Запускать на PythonAnywhere (Bash-консоль, venv активирован):
    export DATABASE_URL='mysql+pymysql://...'
    python scratchpad_fix_charset.py
"""
import os
from sqlalchemy import create_engine, text

url = os.environ["DATABASE_URL"]
engine = create_engine(url)

TARGET_CHARSET = "utf8mb4"
TARGET_COLLATION = "utf8mb4_0900_ai_ci"

with engine.connect() as conn:
    db_name = conn.execute(text("SELECT DATABASE()")).scalar()
    print(f"База: {db_name}")

    conn.execute(text(
        f"ALTER DATABASE `{db_name}` CHARACTER SET {TARGET_CHARSET} COLLATE {TARGET_COLLATION}"
    ))
    conn.commit()
    print("Charset базы по умолчанию изменён (для будущих таблиц).")

    tables = [
        row[0] for row in conn.execute(text(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = DATABASE()"
        ))
    ]
    print(f"Найдено таблиц: {len(tables)}")

    for t in tables:
        print(f"  конвертирую {t} ...", end=" ")
        conn.execute(text(
            f"ALTER TABLE `{t}` CONVERT TO CHARACTER SET {TARGET_CHARSET} COLLATE {TARGET_COLLATION}"
        ))
        conn.commit()
        print("OK")

print("Готово.")
