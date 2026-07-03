"""
NominationService
==================
Формулы расчёта номинаций и "вечных" титулов клуба. Отделён от TitleService
намеренно — тот же принцип разделения, что у RatingService/SeasonRatingEngine/
GGService: хранение и экипировка титула — это одна ответственность, формулы
расчёта победителя — другая.

Два вида титулов:
  - Сезонные номинации по ролям — постоянный исторический факт, выдаются один
    раз при закрытии сезона и никогда не пересчитываются повторно (идемпотентно).
  - "Вечные" титулы клуба — это текущий рекорд клуба ("action belt"): при
    пересчёте старый обладатель лишается титула, новый — получает.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Dict, List, Optional

from sqlalchemy import func

from app import db
from app.models import Game, GameSlot, Player, Role, WinSide, Season

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Коды титулов (должны совпадать с Title.code, засеянными flask seed-titles)
# ---------------------------------------------------------------------------

SEASONAL_ROLE_TITLES: Dict[Role, str] = {
    Role.CIVILIAN: "season_best_civilian",
    Role.SHERIFF:  "season_best_sheriff",
    Role.MAFIA:    "season_best_mafia",
    Role.DON:      "season_best_don",
}

TITLE_LEGEND        = "club_legend"          # Легенда клуба
TITLE_STREAK_KING   = "streak_king"          # Король серии
TITLE_IRON_PLAYER   = "iron_player"          # Железный игрок
TITLE_MAFIA_TERROR  = "mafia_terror"         # Гроза мафии (лучший WR за город)
TITLE_DARK_GENIUS   = "dark_genius"          # Тёмный гений (лучший WR за мафию)

MIN_GAMES_FOR_GLOBAL_TITLE = 10  # анти-шум: не короновать по 1-2 играм


@dataclass
class NominationResult:
    ok: bool
    message: str
    data: Optional[object] = None

    @classmethod
    def success(cls, msg: str = "OK", data=None) -> "NominationResult":
        return cls(ok=True, message=msg, data=data)

    @classmethod
    def fail(cls, msg: str) -> "NominationResult":
        return cls(ok=False, message=msg)


class NominationService:

    # ── Сезонные номинации по ролям ──────────────────────────────────────────

    @staticmethod
    def compute_seasonal_role_nominations(season_id: int) -> NominationResult:
        """
        Для каждой роли (Мирный/Шериф/Мафия/Дон) находит игрока сезона по
        формуле:  role_bonus_points_sum * WR_for_that_role
        и выдаёт соответствующий титул. Идемпотентно — TitleService.grant_title
        сам не выдаёт повторно уже выданный за этот сезон титул.
        """
        from app.services.title_service import TitleService

        season = db.session.get(Season, season_id)
        if not season:
            return NominationResult.fail("Сезон не найден.")

        awarded = []
        for role, title_code in SEASONAL_ROLE_TITLES.items():
            winner = NominationService._best_player_for_role_in_season(role, season_id)
            if winner is None:
                continue
            result = TitleService.grant_title(
                player_id=winner, title_code=title_code, season_id=season_id,
            )
            if result.ok:
                awarded.append(title_code)

        return NominationResult.success(
            f"Номинации сезона «{season.name}» рассчитаны: {len(awarded)} титулов.",
            data=awarded,
        )

    @staticmethod
    def get_role_leaders_preview(season_id: int) -> Dict[str, Optional[int]]:
        """
        Только для превью на странице номинаций, пока сезон ещё идёт — не
        выдаёт титулы, просто показывает текущего лидера по формуле для
        каждой роли (title_code -> player_id).
        """
        return {
            title_code: NominationService._best_player_for_role_in_season(role, season_id)
            for role, title_code in SEASONAL_ROLE_TITLES.items()
        }

    @staticmethod
    def _best_player_for_role_in_season(role: Role, season_id: int) -> Optional[int]:
        """Один запрос на роль: забирает все завершённые слоты этой роли за
        сезон, агрегирует по игроку в Python (сумма bonus_score, WR)."""
        rows = (
            db.session.query(GameSlot.player_id, GameSlot.bonus_score, Game.win_side)
            .join(Game)
            .filter(
                Game.season_id == season_id,
                Game.is_finished == True,
                GameSlot.role == role,
            )
            .all()
        )
        if not rows:
            return None

        is_mafia_role = role in (Role.MAFIA, Role.DON)
        agg: Dict[int, dict] = {}
        for player_id, bonus_score, win_side in rows:
            a = agg.setdefault(player_id, {"bonus_sum": 0.0, "games": 0, "wins": 0})
            a["bonus_sum"] += bonus_score or 0.0
            a["games"] += 1
            won = (is_mafia_role and win_side == WinSide.MAFIA) or (not is_mafia_role and win_side == WinSide.CITY)
            if won:
                a["wins"] += 1

        def score(d: dict) -> float:
            wr = d["wins"] / d["games"] if d["games"] else 0.0
            return d["bonus_sum"] * wr

        best_player_id = max(agg, key=lambda pid: score(agg[pid]), default=None)
        return best_player_id

    # ── Глобальные ("вечные") титулы клуба ───────────────────────────────────

    @staticmethod
    def recompute_global_titles() -> NominationResult:
        """
        Пересчитывает всех 5 "вечных" держателей рекордов клуба. Если рекорд
        сменился — старый обладатель лишается титула (revoke_current_holder_if_any),
        новый получает его (без автоматической экипировки). Каждый расчёт —
        один агрегирующий GROUP BY запрос (либо один проход по всем игрокам
        для серии побед).
        """
        from app.services.title_service import TitleService

        reassigned = []

        candidates = {
            TITLE_LEGEND:       NominationService._legend_of_the_club(),
            TITLE_IRON_PLAYER:  NominationService._iron_player(),
            TITLE_MAFIA_TERROR: NominationService._best_side_wr(city_side=True),
            TITLE_DARK_GENIUS:  NominationService._best_side_wr(city_side=False),
            TITLE_STREAK_KING:  NominationService._streak_king(),
        }

        for title_code, player_id in candidates.items():
            if player_id is None:
                continue

            existing_holder_id = NominationService._current_holder_player_id(title_code)
            if existing_holder_id == player_id:
                continue  # обладатель не изменился — ничего не делаем

            TitleService.revoke_current_holder_if_any(title_code, commit=False)
            TitleService.grant_title(player_id=player_id, title_code=title_code, commit=False)
            reassigned.append(title_code)

        db.session.commit()
        return NominationResult.success(
            f"Глобальные титулы пересчитаны: {len(reassigned)} изменений.", data=reassigned,
        )

    @staticmethod
    def _current_holder_player_id(title_code: str) -> Optional[int]:
        from app.models import Title, PlayerTitle
        title = db.session.query(Title).filter_by(code=title_code).first()
        if not title:
            return None
        pt = db.session.query(PlayerTitle).filter_by(title_id=title.id, revoked=False).first()
        return pt.player_id if pt else None

    @staticmethod
    def _legend_of_the_club() -> Optional[int]:
        """Легенда клуба: max(sum(bonus_score) * общий WR), мин. MIN_GAMES_FOR_GLOBAL_TITLE игр."""
        rows = (
            db.session.query(
                GameSlot.player_id,
                func.sum(GameSlot.bonus_score),
                func.count(GameSlot.id),
                GameSlot.role,
                Game.win_side,
            )
            .join(Game)
            .filter(Game.is_finished == True)
            .all()
        )
        return NominationService._best_by_bonus_times_wr(rows)

    @staticmethod
    def _best_by_bonus_times_wr(rows) -> Optional[int]:
        agg: Dict[int, dict] = {}
        for player_id, bonus_score, _count, role, win_side in rows:
            a = agg.setdefault(player_id, {"bonus_sum": 0.0, "games": 0, "wins": 0})
            a["bonus_sum"] += bonus_score or 0.0
            a["games"] += 1
            is_mafia_side = role in (Role.MAFIA, Role.DON)
            won = (is_mafia_side and win_side == WinSide.MAFIA) or (not is_mafia_side and win_side == WinSide.CITY)
            if won:
                a["wins"] += 1

        eligible = {pid: d for pid, d in agg.items() if d["games"] >= MIN_GAMES_FOR_GLOBAL_TITLE}
        if not eligible:
            return None

        def score(d: dict) -> float:
            return d["bonus_sum"] * (d["wins"] / d["games"])

        return max(eligible, key=lambda pid: score(eligible[pid]))

    @staticmethod
    def _iron_player() -> Optional[int]:
        """Железный игрок: больше всего сыгранных завершённых игр."""
        row = (
            db.session.query(GameSlot.player_id, func.count(GameSlot.id).label("cnt"))
            .join(Game)
            .filter(Game.is_finished == True)
            .group_by(GameSlot.player_id)
            .order_by(func.count(GameSlot.id).desc())
            .first()
        )
        return row[0] if row else None

    @staticmethod
    def _best_side_wr(city_side: bool) -> Optional[int]:
        """Гроза мафии (city_side=True) / Тёмный гений (city_side=False)."""
        roles = [Role.CIVILIAN, Role.SHERIFF] if city_side else [Role.MAFIA, Role.DON]
        target_win = WinSide.CITY if city_side else WinSide.MAFIA

        rows = (
            db.session.query(GameSlot.player_id, GameSlot.role, Game.win_side)
            .join(Game)
            .filter(Game.is_finished == True, GameSlot.role.in_(roles))
            .all()
        )
        agg: Dict[int, dict] = {}
        for player_id, _role, win_side in rows:
            a = agg.setdefault(player_id, {"games": 0, "wins": 0})
            a["games"] += 1
            if win_side == target_win:
                a["wins"] += 1

        eligible = {pid: d for pid, d in agg.items() if d["games"] >= MIN_GAMES_FOR_GLOBAL_TITLE}
        if not eligible:
            return None
        return max(eligible, key=lambda pid: eligible[pid]["wins"] / eligible[pid]["games"])

    @staticmethod
    def _streak_king() -> Optional[int]:
        """
        Король серии: наибольшая победная серия за всю историю. Использует
        ProfileService.get_extended_stats() (уже готовый однопроходный расчёт
        streak'ов) для каждого активного игрока — не дублирует логику подсчёта.
        """
        from app.services.profile_service import ProfileService

        player_ids = [
            p.id for p in db.session.query(Player.id).filter(Player.is_active == True).all()
        ]
        best_pid, best_streak = None, 0
        for pid in player_ids:
            stats = ProfileService.get_extended_stats(pid)
            if stats and stats.longest_streak > best_streak:
                best_streak = stats.longest_streak
                best_pid = pid
        return best_pid
