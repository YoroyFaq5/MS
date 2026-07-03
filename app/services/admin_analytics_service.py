"""
AdminAnalyticsService
======================
Клубная (не персональная) аналитика для страниц /admin/analytics/*.
Отдельный сервис — не ProfileService (тот всегда про конкретного игрока)
и не GiftService (тот про конкретного отправителя/получателя).
Read-only, никаких мутаций.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from itertools import combinations
from typing import List

from sqlalchemy import func

from app import db
from app.models import Game, GameSlot, Player, GiftTransfer, ShopItem

MIN_GAMES_FOR_RIVALRY = 2  # анти-шум: пара из одной случайной игры не рейтингуется


class AdminAnalyticsService:

    @staticmethod
    def get_top_rivalries(limit: int = 10) -> List[dict]:
        """
        Самые частые пары игроков (по числу совместных завершённых игр —
        неважно, союзники или соперники, просто "часто пересекаются").
        Один запрос за все слоты + один проход в Python: для каждой игры
        строим все пары участников (C(10,2)=45), считаем Counter по парам.
        Клубный масштаб — счётное число игр, приемлемо для редкой
        admin-only страницы.
        """
        rows = (
            db.session.query(GameSlot.game_id, GameSlot.player_id)
            .join(Game)
            .filter(Game.is_finished == True)
            .all()
        )
        by_game: dict[int, list[int]] = {}
        for game_id, player_id in rows:
            by_game.setdefault(game_id, []).append(player_id)

        pair_counts: Counter = Counter()
        for player_ids in by_game.values():
            for a, b in combinations(sorted(set(player_ids)), 2):
                pair_counts[(a, b)] += 1

        top_pairs = [
            (pair, count) for pair, count in pair_counts.most_common()
            if count >= MIN_GAMES_FOR_RIVALRY
        ][:limit]
        if not top_pairs:
            return []

        player_ids = {pid for pair, _ in top_pairs for pid in pair}
        players = {p.id: p for p in db.session.query(Player).filter(Player.id.in_(player_ids)).all()}

        return [
            {
                "player_a_id": a, "player_a_name": players[a].display_name if a in players else "?",
                "player_b_id": b, "player_b_name": players[b].display_name if b in players else "?",
                "games_together": count,
            }
            for (a, b), count in top_pairs
        ]

    @staticmethod
    def get_most_gifted_items(limit: int = 10) -> List[dict]:
        rows = (
            db.session.query(GiftTransfer.shop_item_id, func.count(GiftTransfer.id).label("cnt"))
            .filter(GiftTransfer.shop_item_id.isnot(None))
            .group_by(GiftTransfer.shop_item_id)
            .order_by(func.count(GiftTransfer.id).desc())
            .limit(limit)
            .all()
        )
        if not rows:
            return []
        item_ids = [r[0] for r in rows]
        items = {i.id: i for i in db.session.query(ShopItem).filter(ShopItem.id.in_(item_ids)).all()}
        return [
            {"shop_item_id": item_id, "name": items[item_id].name if item_id in items else "?", "gift_count": count}
            for item_id, count in rows
        ]
