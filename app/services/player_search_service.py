"""
PlayerSearchService
====================
Поиск игрока по нику для формы создания игры + защита от транслит-дублей
("Virus" / "Вирус" — один и тот же человек, разными алфавитами).

Нормализация — через unidecode (кириллица → латиница) + приведение к
нижнему регистру и вычищение всего, кроме букв/цифр. Один и тот же
normalize_for_match() используется и для поиска (подстрока), и для
проверки дублей при создании (точное совпадение) — единая логика,
без дублирования правил в двух местах.
"""
from __future__ import annotations

import re
from typing import List

from unidecode import unidecode

from app import db
from app.models import Player

_NON_ALNUM_RE = re.compile(r"[^a-z0-9]+")


def normalize_for_match(text: str) -> str:
    """«Вирус» и «Virus» → одинаковая нормализованная форма ("virus")."""
    if not text:
        return ""
    return _NON_ALNUM_RE.sub("", unidecode(text).lower())


class PlayerSearchService:

    @staticmethod
    def find_similar_players(query: str, limit: int = 8) -> List[Player]:
        """Поиск для автокомплита — подстрока в нормализованном имени/нике."""
        norm_query = normalize_for_match(query)
        if not norm_query:
            return []

        candidates = db.session.query(Player).filter(Player.is_active == True).all()
        matches = [
            p for p in candidates
            if norm_query in normalize_for_match(p.display_name)
            or norm_query in normalize_for_match(p.name)
        ]
        # Точное совпадение (после нормализации) — выше в списке.
        matches.sort(key=lambda p: normalize_for_match(p.display_name) != norm_query)
        return matches[:limit]

    @staticmethod
    def find_exact_duplicates(nickname: str) -> List[Player]:
        """
        Проверка транслит-дубля при создании нового игрока — строгое
        равенство нормализованных форм (не подстрока, чтобы «Максим» и
        «Максимилиан» не считались одним и тем же человеком).
        """
        norm_target = normalize_for_match(nickname)
        if not norm_target:
            return []

        candidates = db.session.query(Player).filter(Player.is_active == True).all()
        return [
            p for p in candidates
            if normalize_for_match(p.display_name) == norm_target
            or normalize_for_match(p.name) == norm_target
            or (p.nickname and normalize_for_match(p.nickname) == norm_target)
        ]
