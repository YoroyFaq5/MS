"""
NominationService
==================
Формулы расчёта номинаций и "вечных" титулов клуба. Отделён от TitleService
намеренно — тот же принцип разделения, что у RatingService/SeasonRatingEngine/
GGService: хранение и экипировка титула — это одна ответственность, формулы
расчёта победителя — другая.

Два вида титулов:
  - Сезонные номинации — постоянный исторический факт, выдаются один раз при
    закрытии сезона и никогда не пересчитываются повторно (идемпотентно).
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

# ── Вечные титулы, раунд 2 ───────────────────────────────────────────────────
TITLE_PEAK_ELO           = "peak_elo"             # Пик формы
TITLE_FINANCIAL_BARON    = "financial_baron"      # Финансовый барон
TITLE_CUP_KING           = "cup_king"             # Кубковый король
TITLE_SEASON_CROWNED     = "season_crowned"       # Коронованный сезонами
TITLE_CLUB_SNIPER        = "club_sniper"          # Снайпер клуба
TITLE_MOVE_MASTER        = "move_master"          # Мастер хода
TITLE_FANTASY_ORACLE     = "fantasy_oracle"       # Fantasy-оракул
TITLE_STABILITY          = "stability"            # Стабильность
TITLE_TOURNAMENT_TERROR  = "tournament_terror"    # Гроза турниров
TITLE_ACHIEVEMENT_KEEPER = "achievement_keeper"   # Хранитель наград

# ── Сезонные титулы, раунд 2 (сверх 4 ролевых) ───────────────────────────────
TITLE_SEASON_CHAMPION         = "season_champion"          # Чемпион сезона
TITLE_SEASON_MVP              = "season_mvp"               # MVP сезона
TITLE_SEASON_DISCOVERY        = "season_discovery"         # Открытие сезона
TITLE_SEASON_BREAKTHROUGH     = "season_breakthrough"      # Прорыв сезона
TITLE_SEASON_MAFIA_TERROR     = "season_mafia_terror"      # Гроза города сезона
TITLE_SEASON_CITY_SHIELD      = "season_city_shield"       # Щит города сезона
TITLE_SEASON_FANTASY_CHAMPION = "season_fantasy_champion"  # Fantasy-чемпион сезона
TITLE_YEAR_PLAYER             = "year_player"               # Игрок года
TITLE_SEASON_SHARPSHOOTER     = "season_sharpshooter"      # Меткий стрелок сезона
TITLE_SEASON_MARATHONER       = "season_marathoner"        # Марафонец сезона

MIN_GAMES_FOR_GLOBAL_TITLE = 10  # анти-шум: не короновать по 1-2 играм
MIN_PU_GAMES_FOR_SNIPER = 5       # анти-шум для "Снайпер клуба"
MIN_TOURNAMENTS_FOR_TERROR = 3    # анти-шум для "Гроза турниров"
MAX_LIFETIME_GAMES_FOR_DISCOVERY = 50  # порог "небольшого стажа" для "Открытие сезона"
MIN_SEASON_GAMES_FOR_DISCOVERY = 5


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
        Считает и выдаёт ВСЕ сезонные титулы разом: 4 ролевых (формула
        role_bonus_points_sum * WR_for_that_role) + чемпион/MVP/открытие/
        прорыв/гроза-города/щит-города/fantasy-чемпион/меткий
        стрелок/марафонец сезона, плюс "Игрок года", если закрываемый сезон —
        последний в своём календарном году. Один вызов на закрытие сезона
        (см. season_service.py), идемпотентно — TitleService.grant_title сам
        не выдаёт повторно уже выданный за этот сезон титул.
        """
        from app.services.title_service import TitleService

        season = db.session.get(Season, season_id)
        if not season:
            return NominationResult.fail("Сезон не найден.")

        awarded = []

        def _grant(title_code: str, player_id: Optional[int]) -> None:
            if player_id is None:
                return
            result = TitleService.grant_title(
                player_id=player_id, title_code=title_code, season_id=season_id,
            )
            if result.ok:
                awarded.append(title_code)

        for role, title_code in SEASONAL_ROLE_TITLES.items():
            _grant(title_code, NominationService._best_player_for_role_in_season(role, season_id))

        _grant(TITLE_SEASON_CHAMPION, season.winner_player_id)
        _grant(TITLE_SEASON_MVP, NominationService._season_mvp(season_id))
        _grant(TITLE_SEASON_DISCOVERY, NominationService._season_discovery(season_id))
        _grant(TITLE_SEASON_BREAKTHROUGH, NominationService._season_breakthrough(season))
        _grant(TITLE_SEASON_MAFIA_TERROR, NominationService._best_side_wr_in_season(season_id, city_side=False))
        _grant(TITLE_SEASON_CITY_SHIELD, NominationService._best_side_wr_in_season(season_id, city_side=True))
        _grant(TITLE_SEASON_FANTASY_CHAMPION, NominationService._season_fantasy_champion(season_id))
        _grant(TITLE_SEASON_SHARPSHOOTER, NominationService._season_sharpshooter(season_id))
        _grant(TITLE_SEASON_MARATHONER, NominationService._season_marathoner(season_id))

        if NominationService._is_last_season_of_year(season):
            _grant(TITLE_YEAR_PLAYER, NominationService._year_player(season.year))

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

    # ── Сезонные номинации, раунд 2 ──────────────────────────────────────────

    @staticmethod
    def _season_mvp(season_id: int) -> Optional[int]:
        """MVP сезона: наибольшая сумма bonus_score за сезон, любая роль."""
        row = (
            db.session.query(GameSlot.player_id, func.sum(GameSlot.bonus_score))
            .join(Game)
            .filter(Game.season_id == season_id, Game.is_finished == True)
            .group_by(GameSlot.player_id)
            .order_by(func.sum(GameSlot.bonus_score).desc())
            .first()
        )
        return row[0] if row and (row[1] or 0) > 0 else None

    @staticmethod
    def _season_discovery(season_id: int) -> Optional[int]:
        """
        Открытие сезона: лучший WR сезона среди игроков с небольшим общим
        (пожизненным) стажем игр — не путать с "новичком" по дате регистрации,
        только фактическая сыгранность имеет значение.
        """
        rows = (
            db.session.query(GameSlot.player_id, GameSlot.role, Game.win_side)
            .join(Game)
            .filter(Game.season_id == season_id, Game.is_finished == True)
            .all()
        )
        agg: Dict[int, dict] = {}
        for player_id, role, win_side in rows:
            a = agg.setdefault(player_id, {"games": 0, "wins": 0})
            a["games"] += 1
            is_mafia_side = role in (Role.MAFIA, Role.DON)
            won = (is_mafia_side and win_side == WinSide.MAFIA) or (not is_mafia_side and win_side == WinSide.CITY)
            if won:
                a["wins"] += 1

        candidates = {pid: d for pid, d in agg.items() if d["games"] >= MIN_SEASON_GAMES_FOR_DISCOVERY}
        if not candidates:
            return None

        eligible = {}
        for pid in candidates:
            lifetime_games = (
                db.session.query(func.count(GameSlot.id))
                .join(Game)
                .filter(GameSlot.player_id == pid, Game.is_finished == True)
                .scalar()
            ) or 0
            if lifetime_games < MAX_LIFETIME_GAMES_FOR_DISCOVERY:
                eligible[pid] = candidates[pid]

        if not eligible:
            return None
        return max(eligible, key=lambda pid: eligible[pid]["wins"] / eligible[pid]["games"])

    @staticmethod
    def _previous_season(season: Season) -> Optional[Season]:
        """Сезон, хронологически идущий непосредственно перед данным (по
        (year, number)) — для "Прорыв сезона"."""
        candidates = (
            db.session.query(Season)
            .filter(
                (Season.year < season.year)
                | ((Season.year == season.year) & (Season.number < season.number))
            )
            .order_by(Season.year.desc(), Season.number.desc())
            .first()
        )
        return candidates

    @staticmethod
    def _season_breakthrough(season: Season) -> Optional[int]:
        """
        Прорыв сезона: наибольший рост места в сезонном рейтинге относительно
        предыдущего (хронологически) сезона, среди игроков, участвовавших в
        обоих. Первый сезон клуба закономерно не выдаёт этот титул — сравнивать
        не с чем.
        """
        prev_season = NominationService._previous_season(season)
        if not prev_season:
            return None

        from app.services.season_rating_engine import SeasonRatingEngine
        current_ratings = SeasonRatingEngine.compute_season_ratings(season.id)
        prev_ratings = SeasonRatingEngine.compute_season_ratings(prev_season.id)
        prev_rank_by_pid = {r.player_id: r.rank for r in prev_ratings}

        best_pid, best_improvement = None, 0
        for r in current_ratings:
            prev_rank = prev_rank_by_pid.get(r.player_id)
            if prev_rank is None:
                continue
            improvement = prev_rank - r.rank
            if improvement > best_improvement:
                best_improvement = improvement
                best_pid = r.player_id
        return best_pid

    @staticmethod
    def _best_side_wr_in_season(season_id: int, city_side: bool) -> Optional[int]:
        """Сезонная версия _best_side_wr — "Гроза города сезона" (city_side=False,
        лучший WR за мафию) / "Щит города сезона" (city_side=True, лучший WR
        за город), сравнение только внутри одного сезона."""
        roles = [Role.CIVILIAN, Role.SHERIFF] if city_side else [Role.MAFIA, Role.DON]
        target_win = WinSide.CITY if city_side else WinSide.MAFIA

        rows = (
            db.session.query(GameSlot.player_id, Game.win_side)
            .join(Game)
            .filter(Game.season_id == season_id, Game.is_finished == True, GameSlot.role.in_(roles))
            .all()
        )
        agg: Dict[int, dict] = {}
        for player_id, win_side in rows:
            a = agg.setdefault(player_id, {"games": 0, "wins": 0})
            a["games"] += 1
            if win_side == target_win:
                a["wins"] += 1

        if not agg:
            return None
        return max(agg, key=lambda pid: agg[pid]["wins"] / agg[pid]["games"])

    @staticmethod
    def _season_fantasy_champion(season_id: int) -> Optional[int]:
        """
        Fantasy-чемпион сезона: наибольшая сумма fantasy-очков за турниры,
        в которых были игры этого сезона (Tournament не хранит season_id
        напрямую — принадлежность определяется через Game.season_id).
        """
        from app.models import FantasyDraft
        from app.models.user import User

        tournament_ids = [
            tid for (tid,) in
            db.session.query(func.distinct(Game.tournament_id))
            .filter(Game.season_id == season_id, Game.tournament_id.isnot(None))
            .all()
        ]
        if not tournament_ids:
            return None

        row = (
            db.session.query(User.player_id, func.sum(FantasyDraft.total_points))
            .join(FantasyDraft, FantasyDraft.user_id == User.id)
            .filter(FantasyDraft.tournament_id.in_(tournament_ids), User.player_id.isnot(None))
            .group_by(User.player_id)
            .order_by(func.sum(FantasyDraft.total_points).desc())
            .first()
        )
        return row[0] if row and (row[1] or 0) > 0 else None

    @staticmethod
    def _season_sharpshooter(season_id: int) -> Optional[int]:
        """Меткий стрелок сезона: больше всего идеальных ПУ-звонков (все 3
        мафии угаданы) за сезон."""
        row = (
            db.session.query(GameSlot.player_id, func.count(GameSlot.id))
            .join(Game)
            .filter(
                Game.season_id == season_id, Game.is_finished == True,
                GameSlot.is_pu == True, GameSlot.pu_mafia_count == 3,
            )
            .group_by(GameSlot.player_id)
            .order_by(func.count(GameSlot.id).desc())
            .first()
        )
        return row[0] if row and row[1] > 0 else None

    @staticmethod
    def _season_marathoner(season_id: int) -> Optional[int]:
        """Марафонец сезона: больше всего сыгранных завершённых игр за сезон."""
        row = (
            db.session.query(GameSlot.player_id, func.count(GameSlot.id))
            .join(Game)
            .filter(Game.season_id == season_id, Game.is_finished == True)
            .group_by(GameSlot.player_id)
            .order_by(func.count(GameSlot.id).desc())
            .first()
        )
        return row[0] if row else None

    @staticmethod
    def _is_last_season_of_year(season: Season) -> bool:
        """True, если у сезона максимальный номер среди всех уже созданных
        сезонов этого календарного года (обычно 6, но не жёстко зашито —
        клуб мог провести года и с меньшим числом сезонов)."""
        max_number = (
            db.session.query(func.max(Season.number))
            .filter(Season.year == season.year)
            .scalar()
        )
        return max_number is not None and season.number == max_number

    @staticmethod
    def _year_player(year: int) -> Optional[int]:
        """Игрок года: победитель по агрегированному рейтингу всех сезонов
        календарного года — переиспользует RatingService.get_year_rating."""
        from app.services.rating_service import RatingService
        ratings = RatingService.get_year_rating(year)
        return ratings[0].player_id if ratings else None

    # ── Глобальные ("вечные") титулы клуба ───────────────────────────────────

    @staticmethod
    def recompute_global_titles() -> NominationResult:
        """
        Пересчитывает всех "вечных" держателей рекордов клуба. Если рекорд
        сменился — старый обладатель лишается титула (revoke_current_holder_if_any),
        новый получает его (без автоматической экипировки). Каждый расчёт —
        один агрегирующий GROUP BY запрос (либо один проход по всем игрокам/
        турнирам, там где точечного SQL-агрегата недостаточно).
        """
        from app.services.title_service import TitleService

        reassigned = []

        candidates = {
            TITLE_LEGEND:       NominationService._legend_of_the_club(),
            TITLE_IRON_PLAYER:  NominationService._iron_player(),
            TITLE_MAFIA_TERROR: NominationService._best_side_wr(city_side=True),
            TITLE_DARK_GENIUS:  NominationService._best_side_wr(city_side=False),
            TITLE_STREAK_KING:  NominationService._streak_king(),
            TITLE_PEAK_ELO:           NominationService._peak_elo(),
            TITLE_FINANCIAL_BARON:    NominationService._financial_baron(),
            TITLE_CUP_KING:           NominationService._cup_king(),
            TITLE_SEASON_CROWNED:     NominationService._season_crowned(),
            TITLE_CLUB_SNIPER:        NominationService._club_sniper(),
            TITLE_MOVE_MASTER:        NominationService._move_master(),
            TITLE_FANTASY_ORACLE:     NominationService._fantasy_oracle(),
            TITLE_STABILITY:          NominationService._stability(),
            TITLE_TOURNAMENT_TERROR:  NominationService._tournament_terror(),
            TITLE_ACHIEVEMENT_KEEPER: NominationService._achievement_keeper(),
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

    # ── Вечные титулы, раунд 2 ────────────────────────────────────────────────

    @staticmethod
    def _peak_elo() -> Optional[int]:
        """Пик формы: наивысший ELO среди активных игроков клуба на данный
        момент (история максимумов ELO в БД не хранится — см. известные
        ограничения проекта, — поэтому это "текущий пик", а не исторический)."""
        row = (
            db.session.query(Player.id)
            .filter(Player.is_active == True)
            .order_by(Player.elo.desc())
            .first()
        )
        return row[0] if row else None

    @staticmethod
    def _financial_baron() -> Optional[int]:
        """Финансовый барон: наибольшая сумма заработанных монет за карьеру."""
        from app.models import CoinTransaction
        row = (
            db.session.query(CoinTransaction.player_id, func.sum(CoinTransaction.amount))
            .filter(CoinTransaction.amount > 0)
            .group_by(CoinTransaction.player_id)
            .order_by(func.sum(CoinTransaction.amount).desc())
            .first()
        )
        return row[0] if row and (row[1] or 0) > 0 else None

    @staticmethod
    def _cup_king() -> Optional[int]:
        """Кубковый король: больше всего побед (1-е место) в турнирах за всю
        историю клуба."""
        from app.models import Tournament
        from app.services.rating_service import RatingService

        tournaments = db.session.query(Tournament).filter(Tournament.status == "finished").all()
        wins: Dict[int, int] = {}
        for t in tournaments:
            ratings = RatingService.get_tournament_rating(t.id)
            champion = next((r for r in ratings if r.rank == 1), None)
            if champion:
                wins[champion.player_id] = wins.get(champion.player_id, 0) + 1

        if not wins:
            return None
        return max(wins, key=lambda pid: wins[pid])

    @staticmethod
    def _season_crowned() -> Optional[int]:
        """Коронованный сезонами: больше всего побед в сезонах за всю историю."""
        row = (
            db.session.query(Season.winner_player_id, func.count(Season.id))
            .filter(Season.winner_player_id.isnot(None))
            .group_by(Season.winner_player_id)
            .order_by(func.count(Season.id).desc())
            .first()
        )
        return row[0] if row else None

    @staticmethod
    def _club_sniper() -> Optional[int]:
        """Снайпер клуба: лучшая точность ПУ-звонка за карьеру (доля угаданных
        мафий из 3 возможных за игру, где игрок был ПУ), мин. MIN_PU_GAMES_FOR_SNIPER
        ПУ-игр."""
        rows = (
            db.session.query(GameSlot.player_id, GameSlot.pu_mafia_count)
            .join(Game)
            .filter(Game.is_finished == True, GameSlot.is_pu == True)
            .all()
        )
        agg: Dict[int, dict] = {}
        for player_id, pu_mafia_count in rows:
            a = agg.setdefault(player_id, {"count": 0, "correct": 0})
            a["count"] += 1
            a["correct"] += pu_mafia_count or 0

        eligible = {pid: d for pid, d in agg.items() if d["count"] >= MIN_PU_GAMES_FOR_SNIPER}
        if not eligible:
            return None
        return max(eligible, key=lambda pid: eligible[pid]["correct"] / (eligible[pid]["count"] * 3))

    @staticmethod
    def _move_master() -> Optional[int]:
        """Мастер хода: больше всего раз признан "лучшим ходом" партии."""
        row = (
            db.session.query(GameSlot.player_id, func.count(GameSlot.id))
            .join(Game)
            .filter(Game.is_finished == True, GameSlot.was_best_move == True)
            .group_by(GameSlot.player_id)
            .order_by(func.count(GameSlot.id).desc())
            .first()
        )
        return row[0] if row and row[1] > 0 else None

    @staticmethod
    def _fantasy_oracle() -> Optional[int]:
        """Fantasy-оракул: больше всего fantasy-очков за всю историю."""
        from app.models import FantasyDraft
        from app.models.user import User
        row = (
            db.session.query(User.player_id, func.sum(FantasyDraft.total_points))
            .join(FantasyDraft, FantasyDraft.user_id == User.id)
            .filter(User.player_id.isnot(None))
            .group_by(User.player_id)
            .order_by(func.sum(FantasyDraft.total_points).desc())
            .first()
        )
        return row[0] if row and (row[1] or 0) > 0 else None

    @staticmethod
    def _stability() -> Optional[int]:
        """Стабильность: лучший общий винрейт за карьеру (не по стороне
        отдельно — общий WR по всем ролям), мин. MIN_GAMES_FOR_GLOBAL_TITLE игр."""
        rows = (
            db.session.query(GameSlot.player_id, GameSlot.role, Game.win_side)
            .join(Game)
            .filter(Game.is_finished == True)
            .all()
        )
        agg: Dict[int, dict] = {}
        for player_id, role, win_side in rows:
            a = agg.setdefault(player_id, {"games": 0, "wins": 0})
            a["games"] += 1
            is_mafia_side = role in (Role.MAFIA, Role.DON)
            won = (is_mafia_side and win_side == WinSide.MAFIA) or (not is_mafia_side and win_side == WinSide.CITY)
            if won:
                a["wins"] += 1

        eligible = {pid: d for pid, d in agg.items() if d["games"] >= MIN_GAMES_FOR_GLOBAL_TITLE}
        if not eligible:
            return None
        return max(eligible, key=lambda pid: eligible[pid]["wins"] / eligible[pid]["games"])

    @staticmethod
    def _tournament_terror() -> Optional[int]:
        """Гроза турниров: лучший % топ-3 финишей среди всех своих турниров,
        мин. MIN_TOURNAMENTS_FOR_TERROR турниров участия."""
        from app.models import Tournament, TournamentParticipant
        from app.services.rating_service import RatingService

        participations: Dict[int, int] = {}
        for pid, cnt in (
            db.session.query(TournamentParticipant.player_id, func.count(TournamentParticipant.id))
            .group_by(TournamentParticipant.player_id)
            .all()
        ):
            participations[pid] = cnt

        top3_counts: Dict[int, int] = {}
        tournaments = db.session.query(Tournament).filter(Tournament.status == "finished").all()
        for t in tournaments:
            for r in RatingService.get_tournament_rating(t.id):
                if r.rank <= 3:
                    top3_counts[r.player_id] = top3_counts.get(r.player_id, 0) + 1

        eligible = {
            pid: top3_counts.get(pid, 0) / count
            for pid, count in participations.items()
            if count >= MIN_TOURNAMENTS_FOR_TERROR
        }
        if not eligible:
            return None
        return max(eligible, key=lambda pid: eligible[pid])

    @staticmethod
    def _achievement_keeper() -> Optional[int]:
        """Хранитель наград: больше всего разблокированных достижений."""
        from app.models import PlayerAchievement
        row = (
            db.session.query(PlayerAchievement.player_id, func.count(PlayerAchievement.id))
            .group_by(PlayerAchievement.player_id)
            .order_by(func.count(PlayerAchievement.id).desc())
            .first()
        )
        return row[0] if row and row[1] > 0 else None
