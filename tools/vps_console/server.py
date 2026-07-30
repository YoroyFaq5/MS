"""
VPS console — небольшой локальный инструмент для быстрых SSH-команд к
продакшен-серверу (5.129.223.174), с кнопками для часто используемых
команд (статус сайта, деплой, логи, fail2ban и т.д.) вместо того, чтобы
каждый раз вручную собирать SSH-вызов.

НЕ часть сайта — намеренно отдельный процесс, никогда не регистрируется
в app/__init__.py и не деплоится на прод. Держать root-доступ к VPS
внутри публичного приложения было бы опасно (любая дыра в сайте стала
бы дырой в сервер). Работает только на 127.0.0.1 — не открывать наружу.

Запуск:
    pip install -r tools/vps_console/requirements.txt
    Заполнить tools/vps_console/.env (см. .env.example рядом) —
    VPS_HOST/VPS_USER/VPS_PASS. Файл .env уже в общем .gitignore
    репозитория (шаблон "*.env" покрывает любой путь), в git не попадёт.
    python tools/vps_console/server.py
    Открыть http://127.0.0.1:5057
"""
from __future__ import annotations

import os
from pathlib import Path

import paramiko
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request

load_dotenv(Path(__file__).parent / ".env")

VPS_HOST = os.environ.get("VPS_HOST", "5.129.223.174")
VPS_USER = os.environ.get("VPS_USER", "root")
VPS_PASS = os.environ.get("VPS_PASS")
VPS_PORT = int(os.environ.get("VPS_SSH_PORT", "22"))

app = Flask(__name__)

# label -> команда. Осознанно без DB-паролей/секретов внутри пресетов —
# для разовых скриптов с боевыми кредами используйте поле произвольной
# команды (или отдельный DATABASE_URL в .env, см. .env.example).
PRESETS = [
    {"key": "site_status", "label": "🌐 Статус сайта", "command": "systemctl is-active ms-site && systemctl status ms-site --no-pager -l"},
    {"key": "site_restart", "label": "🔄 Рестарт сайта", "command": "systemctl restart ms-site && sleep 2 && systemctl is-active ms-site"},
    {"key": "deploy", "label": "🚀 Деплой (git pull + рестарт)", "command": "cd /root/MS && git pull --no-rebase origin main && systemctl restart ms-site && sleep 2 && systemctl is-active ms-site"},
    {"key": "logs_errors", "label": "📜 Логи: ошибки за 30 мин", "command": "journalctl -u ms-site --since '30 minutes ago' --no-pager | grep -i error | tail -50"},
    {"key": "logs_tail", "label": "📜 Логи: последние 50 строк", "command": "journalctl -u ms-site -n 50 --no-pager"},
    {"key": "git_log", "label": "📌 Последние коммиты на проде", "command": "cd /root/MS && git log --oneline -10"},
    {"key": "git_status", "label": "📋 git status на проде", "command": "cd /root/MS && git status"},
    {"key": "fail2ban", "label": "🛡 fail2ban: статус sshd", "command": "fail2ban-client status sshd"},
    {"key": "disk", "label": "💾 Место на диске", "command": "df -h"},
    {"key": "memory", "label": "🧠 Память", "command": "free -h"},
    {"key": "site_curl", "label": "🌍 Проверка сайта (curl)", "command": "curl -s -o /dev/null -w 'HTTP %{http_code}\\n' --max-time 15 https://www.mafiastyle.ru/"},
]


def run_ssh(command: str, timeout: int = 60) -> dict:
    if not VPS_PASS:
        return {"ok": False, "error": "VPS_PASS не задан — заполните tools/vps_console/.env"}

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(VPS_HOST, port=VPS_PORT, username=VPS_USER, password=VPS_PASS, timeout=15)
        stdin, stdout, stderr = client.exec_command(command, timeout=timeout)
        out = stdout.read().decode(errors="replace")
        err = stderr.read().decode(errors="replace")
        code = stdout.channel.recv_exit_status()
        return {"ok": True, "stdout": out, "stderr": err, "exit_code": code}
    except Exception as e:
        return {"ok": False, "error": f"{type(e).__name__}: {e}"}
    finally:
        client.close()


@app.route("/")
def index():
    return render_template("index.html", presets=PRESETS, host=VPS_HOST, user=VPS_USER)


@app.route("/api/run", methods=["POST"])
def api_run():
    data = request.get_json(silent=True) or {}
    command = (data.get("command") or "").strip()
    if not command:
        return jsonify({"ok": False, "error": "Пустая команда."}), 400
    return jsonify(run_ssh(command))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5057, debug=False)
