"""
import_legacy_json.py
======================
Шаг 2 из 2 в переносе данных из старой версии приложения. Читает
JSON-файлы, подготовленные extract_legacy_to_json.py (players.json,
users.json, games.json, gg.json), и отправляет их батчами в уже
развёрнутый Migration API (/migration/*) новой системы — например,
запущенный на PythonAnywhere.

Сетевой доступ к старой БД этому скрипту не нужен — вся нужная информация
уже в JSON-файлах, подготовленных заранее на другой машине.

────────────────────────────────────────────────────────────────────────
Как использовать (например, из Bash-консоли PythonAnywhere)
────────────────────────────────────────────────────────────────────────

1. Скопировать сюда папку legacy_export/ (или другую — см. переменную
   LEGACY_EXPORT_DIR), полученную от extract_legacy_to_json.py.

2. На новой системе временно включить Migration API (.env):

       MIGRATION_API_ENABLED=true
       MIGRATION_API_TOKEN=<длинный случайный секрет>

   и перезапустить (reload) веб-приложение.

3. Задать переменные окружения и запустить:

       NEW_API_BASE_URL=https://<ваш-логин>.pythonanywhere.com
       MIGRATION_API_TOKEN=<тот же секрет, что в п.2>
       LEGACY_EXPORT_DIR=legacy_export   # необязательно, это дефолт
       python import_legacy_json.py

   Порядок отправки (players -> users -> games -> gg) соблюдается сам.

4. Проверить лог: сколько импортировано/пропущено/упало и почему.
   Скрипт безопасно перезапускать — Migration API идемпотентен.

5. После успешного переноса — выключить MIGRATION_API_ENABLED в .env
   новой системы и удалить локальные JSON-файлы (в них пароли в открытом
   виде — см. предупреждение в extract_legacy_to_json.py).
"""
from __future__ import annotations

import json
import logging
import os
import sys
import urllib.error
import urllib.request
from typing import Iterable, List

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("import_legacy_json")

NEW_API_BASE_URL = os.environ.get("NEW_API_BASE_URL", "http://127.0.0.1:5000").rstrip("/")
MIGRATION_API_TOKEN = os.environ.get("MIGRATION_API_TOKEN")
LEGACY_EXPORT_DIR = os.environ.get("LEGACY_EXPORT_DIR", "legacy_export")
# На хостинге с жёстким лимитом времени запроса (например, PythonAnywhere)
# при необходимости уменьшите — каждый батч games обрабатывается одним HTTP
# запросом целиком.
BATCH_SIZE = int(os.environ.get("MIGRATION_BATCH_SIZE", "200"))


def _chunks(seq: List[dict], size: int) -> Iterable[List[dict]]:
    for i in range(0, len(seq), size):
        yield seq[i : i + size]


def _post_batch(path: str, items: List[dict]) -> None:
    if not items:
        return
    url = f"{NEW_API_BASE_URL}/migration/{path}"
    req = urllib.request.Request(
        url,
        data=json.dumps({"items": items}, default=str).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {MIGRATION_API_TOKEN}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=900) as resp:
            body = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        raw = e.read()
        try:
            body = json.loads(raw)
            message = body.get("message")
        except Exception:
            message = raw.decode("utf-8", "ignore")
        logger.error("HTTP %s при POST %s: %s", e.code, url, message)
        return
    except urllib.error.URLError as e:
        logger.error("Не удалось подключиться к %s: %s", url, e)
        return

    data = body.get("data", {}) or {}
    logger.info(
        "%s: imported=%s skipped=%s failed=%s",
        path, data.get("imported"), data.get("skipped"), data.get("failed"),
    )
    for r in data.get("results", []):
        if r.get("status") == "failed":
            logger.warning("  legacy_id=%s FAILED: %s", r.get("legacy_id"), r.get("error"))


def _run_batches(path: str, items: List[dict]) -> None:
    for batch in _chunks(items, BATCH_SIZE):
        _post_batch(path, batch)


def _load(name: str) -> List[dict]:
    file_path = os.path.join(LEGACY_EXPORT_DIR, name)
    if not os.path.exists(file_path):
        sys.exit(f"Не найден файл {file_path} — сначала запустите extract_legacy_to_json.py.")
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)["items"]


def main() -> None:
    if not MIGRATION_API_TOKEN:
        sys.exit("MIGRATION_API_TOKEN не задан (см. докстринг файла).")

    _run_batches("players", _load("players.json"))
    _run_batches("users", _load("users.json"))
    _run_batches("games", _load("games.json"))
    _run_batches("gg", _load("gg.json"))

    logger.info("Готово.")


if __name__ == "__main__":
    main()
