"""
ChartDataService
================
Готовит датасеты для Chart.js на странице статистики профиля.
Чистое формирование данных — никакой новой агрегирующей логики сверх той,
что уже есть в ProfileService/EconomyService (переиспользуется, не дублируется).
Держится отдельно от ProfileService, чтобы тот не разрастался в god-service —
здесь только "разложить готовые цифры под конкретную JS-библиотеку".

Все методы возвращают обычные dict/list — JSON-сериализуемые "как есть"
через фильтр Jinja `| tojson`, без build-шага и SPA.
"""
from __future__ import annotations

from collections import Counter
from typing import Dict, List

from app import db
from app.models import Game, GameSlot, WinSide

ROLE_LABELS: Dict[str, str] = {
    "civilian": "Мирный",
    "sheriff": "Шериф",
    "mafia": "Мафия",
    "don": "Дон",
}
ROLE_ORDER = ["civilian", "sheriff", "mafia", "don"]


def _mini_sparkline_points(results: List[bool], width: int = 200, height: int = 30, pad: float = 4) -> str:
    """SVG <polyline points="..."> for a win/loss form sparkline — same
    server-side string-math approach as the homepage's form sparkline
    (see routes/main.py::_sparkline_points), just kept local here since
    it's the only place in this service that needs it."""
    n = len(results)
    if n == 0:
        return ""
    if n == 1:
        y = height / 2
        return f"{pad:.1f},{y:.1f} {width - pad:.1f},{y:.1f}"
    x_step = (width - 2 * pad) / (n - 1)
    return " ".join(
        f"{pad + i * x_step:.1f},{(pad if won else height - pad):.1f}"
        for i, won in enumerate(results)
    )


class ChartDataService:

    # ── ELO history ───────────────────────────────────────────────────────────

    @staticmethod
    def get_elo_history(player_id: int, limit: int = 50) -> dict:
        rows = (
            db.session.query(Game.played_at, GameSlot.elo_after)
            .join(GameSlot, GameSlot.game_id == Game.id)
            .filter(
                GameSlot.player_id == player_id,
                Game.is_finished == True,
                GameSlot.elo_after.isnot(None),
            )
            .order_by(Game.played_at.asc())
            .limit(limit)
            .all()
        )
        return {
            "labels": [played_at.strftime("%d.%m.%Y") for played_at, _ in rows],
            "values": [round(elo, 1) for _, elo in rows],
        }

    # ── Role timeline (последние N игр) ──────────────────────────────────────

    @staticmethod
    def get_role_timeline(player_id: int, limit: int = 20) -> dict:
        rows = (
            db.session.query(GameSlot, Game)
            .join(Game, GameSlot.game_id == Game.id)
            .filter(GameSlot.player_id == player_id, Game.is_finished == True)
            .order_by(Game.played_at.desc())
            .limit(limit)
            .all()
        )
        rows = list(reversed(rows))  # хронологически слева направо

        entries = []
        for slot, game in rows:
            won = (
                (slot.is_mafia_side and game.win_side == WinSide.MAFIA)
                or (slot.is_city_side and game.win_side == WinSide.CITY)
            )
            entries.append({
                "date": game.played_at.strftime("%d.%m.%Y"),
                "role": slot.role.value,
                "role_label": ROLE_LABELS.get(slot.role.value, slot.role.value),
                "won": won,
                "game_id": game.id,
                # Для тултипа таймлайна ролей (профиль → статистика).
                "is_eliminated": slot.is_eliminated,
                "bonus_score": round(slot.bonus_score, 2),  # админский бонус за игру — реально используется
                "total_score": round(slot.total_score, 2),
            })

        # Текущая серия побед подряд — считаем с конца хронологического списка.
        win_streak = 0
        for e in reversed(entries):
            if not e["won"]:
                break
            win_streak += 1

        avg_bonus_score = round(sum(e["bonus_score"] for e in entries) / len(entries), 2) if entries else None

        # Сводка по ролям — за то же окно (последние N игр), не за карьеру
        # целиком (это отдельная метрика — см. ProfileService.get_role_statistics,
        # который скоуплен на все игры).
        role_counts = Counter(e["role"] for e in entries)
        role_summary = [
            {
                "role": role,
                "label": ROLE_LABELS.get(role, role),
                "count": role_counts[role],
                "pct": round(role_counts[role] / len(entries) * 100) if entries else 0,
            }
            for role in ROLE_ORDER
            if role_counts.get(role)
        ]

        return {
            "games": entries,
            "win_streak": win_streak,
            "avg_bonus_score": avg_bonus_score,
            "role_summary": role_summary,
            "sparkline_points": _mini_sparkline_points([e["won"] for e in entries]),
        }

    # ── Win/loss streak timeline ─────────────────────────────────────────────

    @staticmethod
    def get_streak_timeline(player_id: int) -> dict:
        """
        Кумулятивная серия по всей истории (положительная = победная серия,
        отрицательная = серия поражений на этом game index). Один проход по
        тем же строкам, что и ProfileService.get_extended_stats — отдельный
        лёгкий запрос, т.к. нужна только хронология побед/поражений, без
        полного набора статистики.
        """
        rows = (
            db.session.query(GameSlot, Game)
            .join(Game, GameSlot.game_id == Game.id)
            .filter(GameSlot.player_id == player_id, Game.is_finished == True)
            .order_by(Game.played_at.asc())
            .all()
        )

        labels: List[str] = []
        values: List[int] = []
        streak = 0
        for slot, game in rows:
            won = (
                (slot.is_mafia_side and game.win_side == WinSide.MAFIA)
                or (slot.is_city_side and game.win_side == WinSide.CITY)
            )
            if won:
                streak = streak + 1 if streak > 0 else 1
            else:
                streak = streak - 1 if streak < 0 else -1
            labels.append(game.played_at.strftime("%d.%m.%Y"))
            values.append(streak)

        return {"labels": labels, "values": values}

    # ── Role performance (переиспользует ProfileService) ────────────────────

    @staticmethod
    def get_role_performance(player_id: int) -> dict:
        from app.services.profile_service import ProfileService

        role_stats = ProfileService.get_role_statistics(player_id)
        if not role_stats:
            return {"labels": [], "winrate": [], "avg_score": []}

        breakdown = role_stats["role_breakdown"]
        return {
            "labels": [ROLE_LABELS.get(r["role"], r["role"]) for r in breakdown],
            "winrate": [r["win_rate"] for r in breakdown],
            "avg_score": [
                round(r["total_score"] / r["games"], 2) if r["games"] else 0.0
                for r in breakdown
            ],
        }

    # ── Economy timeline (переиспользует EconomyService.get_history) ────────

    @staticmethod
    def get_economy_timeline(player_id: int, limit: int = 100) -> dict:
        from app.services.economy_service import EconomyService

        txs = EconomyService.get_history(player_id, limit=limit)
        txs = list(reversed(txs))  # хронологически

        labels, balance, earned, spent = [], [], [], []
        for tx in txs:
            labels.append(tx.created_at.strftime("%d.%m.%Y"))
            balance.append(round(tx.balance_after, 1))
            earned.append(round(tx.amount, 1) if tx.amount > 0 else 0.0)
            spent.append(round(-tx.amount, 1) if tx.amount < 0 else 0.0)

        return {"labels": labels, "balance": balance, "earned": earned, "spent": spent}
