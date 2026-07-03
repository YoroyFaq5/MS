#!/usr/bin/env bash
# Запускать на PythonAnywhere (Bash-консоль), не локально.
# Подтягивает последние изменения из GitHub и триггерит перезагрузку
# веб-аппа (PythonAnywhere перезапускает приложение при изменении mtime
# WSGI-файла — так не нужно заходить во вкладку Web и жать Reload вручную).
#
# Использование:
#   bash deploy.sh
#
# Если в этом обновлении менялась схема БД (новые модели/поля) — ПЕРЕД
# запуском reload дополнительно накатите её вручную (flask init-db для
# новых таблиц, либо flask db upgrade, если появятся настоящие Alembic-
# миграции — сейчас их в проекте нет, см. migrations/versions/).
set -euo pipefail

WSGI_FILE="/var/www/mafiastyle_pythonanywhere_com_wsgi.py"

cd "$(dirname "$0")"

echo "== git pull =="
git pull origin main

echo "== reload web app (touch WSGI file) =="
touch "$WSGI_FILE"

echo "Готово. Изменения должны применяться в течение нескольких секунд."
echo "Проверьте: https://mafiastyle.pythonanywhere.com"
