"""
SeasonService
=============
All season lifecycle logic. Zero Flask imports.

Business rules (immutable):
- A year is divided into exactly 6 seasons of 2 calendar months each.
  Jan–Feb, Mar–Apr, May–Jun, Jul–Aug, Sep–Oct, Nov–Dec.
- Seasons are NEVER created manually — only via ensure_year_exists().
- A game is auto-assigned to a season by its played_at date.
- Season is closed automatically once its period ends.
- Winner = player with highest season_rating (TotalPoints*WR% + GG*0.2) in that season.
- Tie → status = WAITING_TIEBREAK → admin picks manually.
- TOP-2 of each finished season auto-qualify into "Стол года <year>" (TOP-1
  only for the Nov–Dec season — see NOVEMBER_DECEMBER_SEASON_NUMBER) — but a
  player only ever qualifies once per year: if already qualified via an
  earlier-numbered season, the next unique player in that season's rating
  takes the slot instead (see compute_year_qualifiers).
- Year-end tournament participant list is (re)synced every time a season
  closes and can also be rebuilt on demand via create_year_tournament().
"""
from __future__ import annotations

import logging
from calendar import monthrange
from dataclasses import dataclass
from datetime import datetime, timezone, date
from typing import List, Optional, Tuple

from app import db
from app.models import (
    Season, SeasonStatus, Game, Player,
    Tournament, TournamentType, TournamentParticipant,
    GameSlot,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants — the only place where season structure is defined
# ---------------------------------------------------------------------------

# (season_number, start_month, end_month)
SEASON_PERIODS: Tuple[Tuple[int, int, int], ...] = (
    (1, 1,  2),
    (2, 3,  4),
    (3, 5,  6),
    (4, 7,  8),
    (5, 9,  10),
    (6, 11, 12),
)

MONTH_NAMES_RU = {
    1: "Янв", 2: "Фев", 3: "Мар", 4: "Апр",
    5: "Май", 6: "Июн", 7: "Июл", 8: "Авг",
    9: "Сен", 10: "Окт", 11: "Ноя", 12: "Дек",
}

YEAR_TOURNAMENT_NAME_TEMPLATE = "Стол года {year}"

# Сезон №6 (Ноябрь–Декабрь, см. SEASON_PERIODS) — особый случай квалификации
# в «Стол года»: только 1 слот вместо 2. Остальные 5 сезонов — по 2 слота.
NOVEMBER_DECEMBER_SEASON_NUMBER = 6


def _qualifier_slots_for_season(season_number: int) -> int:
    """Сколько уникальных слотов «Стола года» разыгрывает сезон.

    Все сезоны — 2 слота, кроме ноября-декабря — 1 слот. Правило
    приоритета более раннего сезона и уникальности по всему году
    (см. compute_year_qualifiers) при этом не меняется — просто для
    ноября-декабря нужен на один уникальный слот меньше.
    """
    return 1 if season_number == NOVEMBER_DECEMBER_SEASON_NUMBER else 2


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _season_bounds(year: int, start_month: int, end_month: int):
    """Return (starts_at, ends_at) as timezone-aware datetimes (UTC)."""
    starts_at = datetime(year, start_month, 1, 0, 0, 0, tzinfo=timezone.utc)
    last_day  = monthrange(year, end_month)[1]
    ends_at   = datetime(year, end_month, last_day, 23, 59, 59, tzinfo=timezone.utc)
    return starts_at, ends_at


def _season_name(year: int, number: int, start_month: int, end_month: int) -> str:
    m1 = MONTH_NAMES_RU[start_month]
    m2 = MONTH_NAMES_RU[end_month]
    return f"Сезон {number} ({m1}–{m2}) {year}"


def _get_or_create_year_tournament(year: int) -> Tournament:
    """Find or create the 'Стол года <year>' tournament."""
    name = YEAR_TOURNAMENT_NAME_TEMPLATE.format(year=year)
    t = db.session.query(Tournament).filter_by(name=name).first()
    if not t:
        t = Tournament(
            name=name,
            description=(
                f"Итоговый турнир {year} года. "
                f"Участвуют Топ-2 каждого сезона (Топ-1 для ноября-декабря), "
                f"без повторной квалификации одного игрока дважды."
            ),
            type=TournamentType.INDIVIDUAL,
            is_ranked=True,
            has_stages=False,
            status="pending",
        )
        db.session.add(t)
        db.session.flush()
        logger.info(f"Created year tournament: {name!r} id={t.id}")
    return t


# ---------------------------------------------------------------------------
# Result type
# ---------------------------------------------------------------------------

@dataclass
class SeasonResult:
    ok: bool
    message: str
    data: Optional[object] = None

    @classmethod
    def success(cls, msg: str = "OK", data=None) -> "SeasonResult":
        return cls(ok=True, message=msg, data=data)

    @classmethod
    def fail(cls, msg: str) -> "SeasonResult":
        return cls(ok=False, message=msg)


# ---------------------------------------------------------------------------
# SeasonService
# ---------------------------------------------------------------------------

class SeasonService:

    # ── Ensure seasons exist for a year ──────────────────────────────────────

    @staticmethod
    def ensure_year_exists(year: int) -> List[Season]:
        """
        Idempotently create all 6 seasons for the given year.
        Safe to call on every app start or before game creation.
        Returns the list of 6 Season objects (existing + newly created).
        """
        seasons = []
        for number, start_month, end_month in SEASON_PERIODS:
            existing = db.session.query(Season).filter_by(
                year=year, number=number
            ).first()
            if existing:
                seasons.append(existing)
                continue

            starts_at, ends_at = _season_bounds(year, start_month, end_month)
            name = _season_name(year, number, start_month, end_month)

            # Determine initial status: if the period is already over → FINISHED
            # (handles backfill of historical years)
            now = datetime.now(timezone.utc)
            if now > ends_at:
                status = SeasonStatus.FINISHED
            else:
                status = SeasonStatus.ACTIVE

            s = Season(
                year=year,
                number=number,
                name=name,
                starts_at=starts_at,
                ends_at=ends_at,
                status=status,
            )
            db.session.add(s)
            seasons.append(s)
            logger.info(f"Created season: {name!r}")

        db.session.commit()
        return seasons

    # ── Auto-resolve season for a game ───────────────────────────────────────

    @staticmethod
    def resolve_season_for_game(game: Game) -> Optional[Season]:
        """
        Find the correct season for game.played_at and assign game.season_id.
        Ensures the year's seasons exist first.
        Returns the Season or None if game is not ranked.
        """
        if not game.is_ranked:
            return None

        played_at = game.played_at
        if played_at.tzinfo is None:
            played_at = played_at.replace(tzinfo=timezone.utc)

        year = played_at.year
        SeasonService.ensure_year_exists(year)

        season = db.session.query(Season).filter(
            Season.year == year,
            Season.starts_at <= played_at,
            Season.ends_at >= played_at,
        ).first()

        if season:
            game.season_id = season.id
            logger.debug(f"Game #{game.id} assigned to {season.name!r}")

        return season

    # ── Close expired seasons ─────────────────────────────────────────────────

    @staticmethod
    def close_expired_seasons() -> List[SeasonResult]:
        """
        Find all ACTIVE seasons whose period has ended and close them.
        Call this on app startup or via a scheduler.
        Returns a list of SeasonResult for each season processed.
        """
        now = datetime.now(timezone.utc)
        expired = db.session.query(Season).filter(
            Season.status == SeasonStatus.ACTIVE,
            Season.ends_at < now,
        ).all()

        results = []
        for season in expired:
            r = SeasonService._close_season(season)
            results.append(r)

        return results

    @staticmethod
    def _close_season(season: Season) -> SeasonResult:
        """Determine winner and transition season to FINISHED or WAITING_TIEBREAK."""
        from app.services.rating_service import RatingService

        ratings = RatingService.get_season_rating(season.id)

        if not ratings:
            # No games played — mark finished with no winner
            season.status = SeasonStatus.FINISHED
            db.session.commit()
            return SeasonResult.success(
                f"{season.name}: нет игр, завершён без победителя.", data=season
            )

        top_score = ratings[0].season_rating
        leaders   = [r for r in ratings if r.season_rating == top_score]

        if len(leaders) == 1:
            winner = leaders[0]
            season.status       = SeasonStatus.FINISHED
            season.winner_player_id = winner.player_id
            season.winner_score = winner.season_rating
            db.session.commit()

            # Auto-register winner in year tournament
            SeasonService._register_winner_in_year_tournament(season)

            # Pay out season coin rewards (winner / top-3 / top-10).
            # This was previously never invoked anywhere, so season rewards
            # were silently never paid despite being fully implemented.
            try:
                from app.services.economy_service import EconomyService
                EconomyService.apply_season_rewards(season.id)
            except Exception:
                logger.exception(f"Failed to apply season rewards for season #{season.id}")

            try:
                from app.services.achievement_service import AchievementService
                AchievementService.check_after_season(season)
            except Exception:
                logger.exception(f"Failed to check achievements for season #{season.id}")

            try:
                from app.services.nomination_service import NominationService
                NominationService.compute_seasonal_role_nominations(season.id)
            except Exception:
                logger.exception(f"Failed to compute seasonal nominations for season #{season.id}")

            logger.info(
                f"Season {season.name!r} closed. "
                f"Winner: {winner.display_name} ({winner.season_rating} pts)"
            )
            return SeasonResult.success(
                f"{season.name}: победитель — {winner.display_name}.",
                data=season,
            )
        else:
            # Tie — admin must resolve
            season.status = SeasonStatus.WAITING_TIEBREAK
            db.session.commit()
            names = ", ".join(r.display_name for r in leaders)
            logger.warning(
                f"Season {season.name!r}: TIE between {names} at {top_score} pts"
            )
            return SeasonResult.success(
                f"{season.name}: ничья между {names} — требуется ручной выбор победителя.",
                data=season,
            )

    # ── Admin: resolve tiebreak ───────────────────────────────────────────────

    @staticmethod
    def resolve_tiebreak(season_id: int, winner_player_id: int) -> SeasonResult:
        """
        Admin manually picks the winner when there's a tiebreak.
        """
        season = db.session.get(Season, season_id)
        if not season:
            return SeasonResult.fail("Сезон не найден.")
        if season.status != SeasonStatus.WAITING_TIEBREAK:
            return SeasonResult.fail(
                f"Сезон не в состоянии ожидания выбора (текущий статус: {season.status.value})."
            )

        player = db.session.get(Player, winner_player_id)
        if not player:
            return SeasonResult.fail("Игрок не найден.")

        from app.services.rating_service import RatingService
        ratings = RatingService.get_season_rating(season_id)
        player_rating = next((r for r in ratings if r.player_id == winner_player_id), None)
        if not player_rating:
            return SeasonResult.fail(
                f"Игрок «{player.display_name}» не участвовал в этом сезоне."
            )

        season.status           = SeasonStatus.FINISHED
        season.winner_player_id = winner_player_id
        season.winner_score     = player_rating.season_rating
        db.session.commit()

        SeasonService._register_winner_in_year_tournament(season)

        try:
            from app.services.economy_service import EconomyService
            EconomyService.apply_season_rewards(season.id)
        except Exception:
            logger.exception(f"Failed to apply season rewards for season #{season.id}")

        try:
            from app.services.achievement_service import AchievementService
            AchievementService.check_after_season(season)
        except Exception:
            logger.exception(f"Failed to check achievements for season #{season.id}")

        try:
            from app.services.nomination_service import NominationService
            NominationService.compute_seasonal_role_nominations(season.id)
        except Exception:
            logger.exception(f"Failed to compute seasonal nominations for season #{season.id}")

        return SeasonResult.success(
            f"Победитель сезона «{season.name}» — {player.display_name}.",
            data=season,
        )

    # ── Year tournament qualification (TOP-2 per season, year-unique) ─────────

    @staticmethod
    def compute_year_qualifiers(year: int) -> List[Tuple[Season, list]]:
        """
        Определяет квалификантов «Стола года» по каждому завершённому сезону.

        Правила:
        - учитываются только сезоны в статусе FINISHED (ACTIVE/WAITING_TIEBREAK
          в квалификации не участвуют — сезон должен быть решён окончательно);
        - сезоны обрабатываются в порядке номера — более ранний сезон имеет
          приоритет;
        - из каждого сезона проходят первые N УНИКАЛЬНЫХ по всему году игрока
          из его рейтинга сезона, которые ещё не квалифицировались через более
          ранний сезон (если кандидат уже квалифицирован — берётся следующий
          по рейтингу этого же сезона); N = 2 для всех сезонов, КРОМЕ
          ноября-декабря — там N = 1 (см. _qualifier_slots_for_season);
        - неактивные (soft-deleted) игроки в квалификацию не допускаются —
          тот же флаг Player.is_active, что уже используется в
          TournamentService.register_participant;
        - если подходящих кандидатов в сезоне меньше N — берётся сколько есть.

        Чистая функция чтения (ничего не пишет в БД). Расчёт рейтинга сезона
        не дублируется — переиспользуется RatingService.get_season_rating()
        (= SeasonRatingEngine), эта функция только выбирает из готового
        рейтинга нужных кандидатов.

        Возвращает список (Season, [SeasonRatingEntry, ...]) по всем
        рассмотренным сезонам, в порядке номера сезона.
        """
        from app.services.rating_service import RatingService

        seasons = (
            db.session.query(Season)
            .filter(Season.year == year, Season.status == SeasonStatus.FINISHED)
            .order_by(Season.number)
            .all()
        )
        if not seasons:
            return []

        active_ids = {
            pid for (pid,) in db.session.query(Player.id).filter(Player.is_active == True).all()
        }

        qualified: set = set()
        result: List[Tuple[Season, list]] = []

        for season in seasons:
            ratings = RatingService.get_season_rating(season.id)
            # Вторичная сортировка по player_id — только для детерминированного
            # выбора кандидатов при равенстве очков; исходный список/rank
            # (используемый для отображения рейтинга) не изменяется.
            ordered = sorted(ratings, key=lambda e: (-e.season_rating, e.player_id))

            slots = _qualifier_slots_for_season(season.number)
            picks = []
            for entry in ordered:
                if entry.player_id in qualified or entry.player_id not in active_ids:
                    continue
                picks.append(entry)
                if len(picks) == slots:
                    break

            qualified.update(e.player_id for e in picks)
            result.append((season, picks))

        return result

    @staticmethod
    def _sync_year_tournament_participants(year: int) -> Tuple[Tournament, List[str]]:
        """
        Пересчитывает квалификантов «Стола года» по всем завершённым сезонам
        года (compute_year_qualifiers) и добавляет недостающих участников.

        Идемпотентно и безопасно вызывать многократно, в любой момент и в
        любом порядке закрытия сезонов — уже зарегистрированные участники
        никогда не удаляются, только добавляются недостающие (если более
        ранний сезон закрывается позже более позднего, второй слот позднего
        сезона мог быть временно занят игроком, который по приоритету должен
        был пройти через более ранний сезон — но т.к. TournamentParticipant
        не хранит «через какой сезон» игрок квалифицировался, а полный
        пересчёт всегда добавляет недостающих, итоговый набор всегда
        сходится к корректному без необходимости удалений).
        """
        qualifiers = SeasonService.compute_year_qualifiers(year)
        t = _get_or_create_year_tournament(year)

        existing_ids = {
            pid for (pid,) in
            db.session.query(TournamentParticipant.player_id)
            .filter_by(tournament_id=t.id).all()
        }

        added: List[str] = []
        for season, picks in qualifiers:
            if picks:
                season.year_tournament_id = t.id
            for entry in picks:
                if entry.player_id not in existing_ids:
                    db.session.add(TournamentParticipant(
                        tournament_id=t.id,
                        player_id=entry.player_id,
                    ))
                    existing_ids.add(entry.player_id)
                    added.append(entry.display_name)

        db.session.commit()
        if added:
            logger.info(f"Year tournament {t.name!r} synced: added {added}")
        return t, added

    @staticmethod
    def _register_winner_in_year_tournament(season: Season) -> None:
        """
        Вызывается сразу после того, как сезон закрыт с определённым
        победителем. Раньше регистрировала только TOP-1 этого сезона;
        теперь квалификация — TOP-2 на сезон с уникальностью по всему году
        (см. compute_year_qualifiers), поэтому пересчитывается весь год
        целиком, а не только этот сезон — сигнатура/точки вызова не
        изменились, обратная совместимость сохранена.
        """
        if not season.winner_player_id:
            return
        SeasonService._sync_year_tournament_participants(season.year)

    # ── Create year-end tournament (manual trigger or scheduler) ──────────────

    @staticmethod
    def create_year_tournament(year: int) -> SeasonResult:
        """
        Create (or return existing) 'Стол года <year>' tournament and
        populate it with the TOP-2-per-season qualifiers of all finished
        seasons (see compute_year_qualifiers for the uniqueness/priority
        rules). Can be called at any time — idempotent.
        """
        SeasonService.ensure_year_exists(year)

        seasons = (
            db.session.query(Season)
            .filter_by(year=year)
            .order_by(Season.number)
            .all()
        )

        finished_count = sum(1 for s in seasons if s.status == SeasonStatus.FINISHED)
        tiebreaks = [s for s in seasons if s.status == SeasonStatus.WAITING_TIEBREAK]

        if tiebreaks:
            names = ", ".join(s.name for s in tiebreaks)
            return SeasonResult.fail(
                f"Нельзя создать «Стол года» — не разрешены ничьи: {names}."
            )

        t, added = SeasonService._sync_year_tournament_participants(year)

        msg = (
            f"«{t.name}» готов. "
            f"Завершено сезонов: {finished_count}/6. "
            f"Добавлено участников: {len(added)}."
        )
        return SeasonResult.success(msg, data=t)

    # ── Queries ───────────────────────────────────────────────────────────────

    @staticmethod
    def get_season_by_date(dt: datetime) -> Optional[Season]:
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return db.session.query(Season).filter(
            Season.starts_at <= dt,
            Season.ends_at   >= dt,
        ).first()

    @staticmethod
    def get_seasons_for_year(year: int) -> List[Season]:
        SeasonService.ensure_year_exists(year)
        return (
            db.session.query(Season)
            .filter_by(year=year)
            .order_by(Season.number)
            .all()
        )

    @staticmethod
    def get_current_season() -> Optional[Season]:
        return SeasonService.get_season_by_date(datetime.now(timezone.utc))

    @staticmethod
    def get_tiebreak_candidates(season_id: int) -> list:
        """Return top-tied players for admin tiebreak UI."""
        from app.services.rating_service import RatingService
        ratings = RatingService.get_season_rating(season_id)
        if not ratings:
            return []
        top = ratings[0].season_rating
        return [r for r in ratings if r.season_rating == top]
