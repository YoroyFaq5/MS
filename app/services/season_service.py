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
- Winner = player with highest season_rating (TotalPoints*WR% + GG*gg_weight,
  gg_weight fixed per-season on Season.gg_weight — see SeasonRatingEngine and
  NEW_SEASON_GG_WEIGHT below) in that season — but only among players who
  actually occupy a top-5 place (>= SeasonRatingEngine.MIN_GAMES_FOR_TOP5
  ranked games this season); a season can close with no winner at all if
  nobody meets that floor.
- Tie → status = WAITING_TIEBREAK → admin picks manually (same top-5/min-games
  restriction applies to who can be picked).
- TOP-2 of each finished season auto-qualify into "Стол года <year>" (TOP-1
  only for the Nov–Dec season — see NOVEMBER_DECEMBER_SEASON_NUMBER), drawn
  only from players who occupy that season's top-5 — but a player only ever
  qualifies once per year: if already qualified via an earlier-numbered
  season, the next unique eligible player in that season's rating takes the
  slot instead (see compute_year_qualifiers).
- Year-end tournament participant list is (re)synced every time a season
  closes and can also be rebuilt on demand via create_year_tournament() —
  but only while that tournament is still "pending"; once it's active/
  finished, composition is never changed silently (see
  _sync_year_tournament_participants).
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

# Вес GG в формуле сезонного рейтинга для НОВЫХ сезонов (см. Season.gg_weight
# и SeasonRatingEngine). Существующие на момент введения этого поля сезоны
# зафиксированы на 0.2 миграцией (migrate_season_gg_weight.py) и никогда не
# меняются задним числом — это значение применяется только к сезонам,
# создаваемым ensure_year_exists() отсюда и далее. Коэффициент фиксируется
# на самой записи Season в момент создания, а не выводится из даты/номера
# сезона при каждом расчёте — так что смена этой константы в будущем влияет
# только на ещё не созданные сезоны.
NEW_SEASON_GG_WEIGHT = 0.1


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


@dataclass
class YearSyncResult:
    """Result of SeasonService._sync_year_tournament_participants — see its
    docstring. `warning` is set (and the tournament's participants are left
    untouched) exactly when the year tournament is no longer 'pending' and
    its composition would otherwise have needed to change."""
    tournament: Tournament
    added: List[str]
    removed: List[str]
    warning: Optional[str] = None


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
                gg_weight=NEW_SEASON_GG_WEIGHT,
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
        """Determine winner and transition season to FINISHED or WAITING_TIEBREAK.

        Winner must actually occupy a top-5 place (see SeasonRatingEngine —
        requires >= MIN_GAMES_FOR_TOP5 ranked games this season). If nobody
        in the season met that floor, the season closes with no winner,
        exactly like the "no games played" case — a season can end without
        crowning anyone.
        """
        from app.services.rating_service import RatingService
        from app.services.season_rating_engine import SeasonRatingEngine

        ratings = RatingService.get_season_rating(season.id)
        top5 = SeasonRatingEngine.top5_entries(ratings)

        if not top5:
            # No games played, or nobody met the top-5 games-played floor —
            # mark finished with no winner either way.
            season.status = SeasonStatus.FINISHED
            db.session.commit()
            msg = (
                f"{season.name}: нет игр, завершён без победителя."
                if not ratings else
                f"{season.name}: ни один игрок не набрал минимум "
                f"{SeasonRatingEngine.MIN_GAMES_FOR_TOP5} игр — завершён без победителя."
            )
            return SeasonResult.success(msg, data=season)

        top_score = top5[0].season_rating
        leaders   = [r for r in top5 if r.season_rating == top_score]

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
        from app.services.season_rating_engine import SeasonRatingEngine
        ratings = RatingService.get_season_rating(season_id)
        player_rating = next((r for r in ratings if r.player_id == winner_player_id), None)
        if not player_rating:
            return SeasonResult.fail(
                f"Игрок «{player.display_name}» не участвовал в этом сезоне."
            )
        if player_rating.rank > SeasonRatingEngine.TOP5_SLOTS:
            return SeasonResult.fail(
                f"«{player.display_name}» сыграл(а) {player_rating.games_played} игр(ы) "
                f"в этом сезоне — минимум {SeasonRatingEngine.MIN_GAMES_FOR_TOP5} требуется, "
                f"чтобы претендовать на победу."
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
        - кандидат обязан реально занимать место 1-5 сезона (см. задачу про
          минимум 8 игр — SeasonRatingEngine.MIN_GAMES_FOR_TOP5); игрок,
          которого правило top-5 отодвинуло на ранг 6+, кандидатом не
          считается, даже если его season_rating выше, чем у пятого места;
        - если подходящих кандидатов в сезоне меньше N — берётся сколько есть.

        Чистая функция чтения (ничего не пишет в БД). Расчёт рейтинга сезона
        не дублируется — переиспользуется RatingService.get_season_rating()
        (= SeasonRatingEngine), эта функция только выбирает из готового,
        уже отсортированного по месту (rank 1..N по возрастанию) рейтинга
        нужных кандидатов.

        Возвращает список (Season, [SeasonRatingEntry, ...]) по всем
        рассмотренным сезонам, в порядке номера сезона.
        """
        from app.services.rating_service import RatingService
        from app.services.season_rating_engine import SeasonRatingEngine

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
            # top5_entries — уже отсортированы по rank (1..N, N<=5), тот же
            # детерминированный порядок при равенстве очков (по player_id),
            # что использует сам SeasonRatingEngine для присвоения rank.
            candidates = SeasonRatingEngine.top5_entries(ratings)

            slots = _qualifier_slots_for_season(season.number)
            picks = []
            for entry in candidates:
                if entry.player_id in qualified or entry.player_id not in active_ids:
                    continue
                picks.append(entry)
                if len(picks) == slots:
                    break

            qualified.update(e.player_id for e in picks)
            result.append((season, picks))

        return result

    @staticmethod
    def _sync_year_tournament_participants(year: int) -> "YearSyncResult":
        """
        Пересчитывает квалификантов «Стола года» по всем завершённым сезонам
        года (compute_year_qualifiers) и приводит состав турнира ТОЧНО к
        этому набору — не только добавляет недостающих, но и убирает
        устаревших автоматических квалификантов (например, если сезоны
        закрылись не по порядку и пересчёт отдал чей-то слот игроку с
        приоритетом более раннего сезона).

        Различие "автоматический / ручной" участник — TournamentParticipant.
        qualified_via_season_id: НЕ NULL значит "эту строку добавила именно
        эта функция, как квалификанта через сезон с этим id" — только такие
        строки может удалить повторная синхронизация. Участник с
        qualified_via_season_id IS NULL (обычная регистрация — вручную или
        через участие в игре турнира) НИКОГДА не удаляется и не
        переклассифицируется здесь, даже если его player_id совпадает с
        кем-то из актуальных квалификантов (в этом случае просто ничего не
        делаем — он и так уже в турнире).

        Идемпотентно: повторный вызов с тем же набором квалификантов не
        создаёт дублей и не производит лишних добавлений/удалений.

        Состав меняется молча ТОЛЬКО пока турнир в статусе "pending" — для
        уже активного или завершённого «Стола года» состав никогда не
        трогается автоматически; вместо этого возвращается предупреждение
        (YearSyncResult.warning), которое вызывающий код обязан показать
        администратору, а не проглотить.
        """
        qualifiers = SeasonService.compute_year_qualifiers(year)
        t = _get_or_create_year_tournament(year)

        # desired[player_id] = id сезона, через который он квалифицировался —
        # уникальность игрока по всему году уже гарантирована compute_year_
        # qualifiers, так что здесь каждый player_id встречается максимум
        # у одного сезона.
        desired: dict[int, int] = {}
        name_by_pid: dict[int, str] = {}
        for season, picks in qualifiers:
            if picks:
                season.year_tournament_id = t.id
            for entry in picks:
                desired[entry.player_id] = season.id
                name_by_pid[entry.player_id] = entry.display_name

        existing = (
            db.session.query(TournamentParticipant)
            .filter_by(tournament_id=t.id)
            .all()
        )
        existing_by_pid = {p.player_id: p for p in existing}

        missing_pids = [pid for pid in desired if pid not in existing_by_pid]
        stale_auto = [
            p for p in existing
            if p.qualified_via_season_id is not None and p.player_id not in desired
        ]

        if t.status != "pending":
            # Метаданные на самих Season (какой сезон "ведёт" в какой год-
            # турнир) — не состав турнира — можно фиксировать всегда.
            db.session.commit()
            if missing_pids or stale_auto:
                warning = (
                    f"«{t.name}» уже в статусе «{t.status}» — автосинхронизация "
                    f"состава пропущена, хотя актуальные квалификанты отличаются "
                    f"(не хватает: {len(missing_pids)}, устарело: {len(stale_auto)}). "
                    f"Проверьте состав вручную."
                )
                logger.warning(warning)
                return YearSyncResult(tournament=t, added=[], removed=[], warning=warning)
            return YearSyncResult(tournament=t, added=[], removed=[])

        added: List[str] = []
        removed: List[str] = []

        for p in stale_auto:
            removed.append(p.player.display_name if p.player else str(p.player_id))
            db.session.delete(p)

        for pid, season_id in desired.items():
            row = existing_by_pid.get(pid)
            if row is None:
                db.session.add(TournamentParticipant(
                    tournament_id=t.id,
                    player_id=pid,
                    qualified_via_season_id=season_id,
                ))
                added.append(name_by_pid[pid])
            elif row.qualified_via_season_id is not None and row.qualified_via_season_id != season_id:
                # Уже был авто-квалификантом, но через другой сезон (сезоны
                # закрылись не по порядку) — переклассифицируем. Ручные
                # регистрации (qualified_via_season_id is None) сюда не
                # попадают вообще — ветка elif требует "not None".
                row.qualified_via_season_id = season_id

        db.session.commit()
        if added:
            logger.info(f"Year tournament {t.name!r} synced: added {added}")
        if removed:
            logger.info(f"Year tournament {t.name!r} synced: removed stale auto-qualifiers {removed}")
        return YearSyncResult(tournament=t, added=added, removed=removed)

    @staticmethod
    def _register_winner_in_year_tournament(season: Season) -> None:
        """
        Вызывается сразу после того, как сезон закрыт с определённым
        победителем. Раньше регистрировала только TOP-1 этого сезона;
        теперь квалификация — TOP-2 на сезон с уникальностью по всему году
        (см. compute_year_qualifiers), поэтому пересчитывается весь год
        целиком, а не только этот сезон — сигнатура/точки вызова не
        изменились, обратная совместимость сохранена. Предупреждение (если
        «Стол года» уже не pending) уже залогировано внутри sync — здесь
        нет UI, которому можно было бы его показать (сезон закрывается сам,
        без отдельного flash-сообщения про год-турнир).
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

        sync = SeasonService._sync_year_tournament_participants(year)
        t = sync.tournament

        if sync.warning:
            return SeasonResult.fail(sync.warning)

        msg = (
            f"«{t.name}» готов. "
            f"Завершено сезонов: {finished_count}/6. "
            f"Добавлено участников: {len(sync.added)}."
            + (f" Удалено устаревших: {len(sync.removed)}." if sync.removed else "")
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
        """Return top-tied players for admin tiebreak UI — restricted to
        players who actually occupy a top-5 place (>= MIN_GAMES_FOR_TOP5
        games this season, see SeasonRatingEngine); a player below that
        floor can never be a tiebreak candidate even if their raw score
        happens to match the top5 leaders' score."""
        from app.services.rating_service import RatingService
        from app.services.season_rating_engine import SeasonRatingEngine
        ratings = RatingService.get_season_rating(season_id)
        top5 = SeasonRatingEngine.top5_entries(ratings)
        if not top5:
            return []
        top = top5[0].season_rating
        return [r for r in top5 if r.season_rating == top]

    # ── Season stat panel (nominations page) ──────────────────────────────────

    @staticmethod
    def get_season_stats(season_id: int) -> Optional[dict]:
        """
        Живая статистика сезона для страницы номинаций: сыграно игр,
        игроков, средний текущий ELO участников, лучший винрейт сезона,
        самая длинная победная серия сезона. Размер стола сюда намеренно
        не включён — в этой мафии он всегда ровно 10 (constraint в БД,
        см. GameSlot.seat_number), считать его "средним" бессмысленно.

        Один bulk-запрос по всем слотам сезона + один Python-проход
        (сортировка по player_id/id уже даёт нужную группировку для
        победной серии за один проход) — НЕ цикл с отдельным запросом на
        игрока (см. инцидент с зависанием /titles/nominations в этой же
        сессии: там ровно такой цикл положил страницу на проде).
        """
        from app.models import Role, WinSide
        from sqlalchemy import func

        games_count = db.session.query(func.count(Game.id)).filter(
            Game.season_id == season_id, Game.is_finished == True
        ).scalar() or 0
        if games_count == 0:
            return None

        rows = (
            db.session.query(GameSlot.player_id, GameSlot.role, Game.win_side)
            .join(Game)
            .filter(Game.season_id == season_id, Game.is_finished == True)
            .order_by(GameSlot.player_id.asc(), Game.id.asc())
            .all()
        )

        agg: dict = {}
        current_pid = None
        current_streak = 0
        best_streak_for_player = 0
        longest_streak = 0
        longest_streak_pid = None

        def _flush_player():
            nonlocal longest_streak, longest_streak_pid
            if current_pid is not None and best_streak_for_player > longest_streak:
                longest_streak = best_streak_for_player
                longest_streak_pid = current_pid

        for player_id, role, win_side in rows:
            if player_id != current_pid:
                _flush_player()
                current_pid = player_id
                current_streak = 0
                best_streak_for_player = 0
            a = agg.setdefault(player_id, {"games": 0, "wins": 0})
            a["games"] += 1
            is_mafia_side = role in (Role.MAFIA, Role.DON)
            won = (is_mafia_side and win_side == WinSide.MAFIA) or (not is_mafia_side and win_side == WinSide.CITY)
            if won:
                a["wins"] += 1
                current_streak += 1
                best_streak_for_player = max(best_streak_for_player, current_streak)
            else:
                current_streak = 0
        _flush_player()

        MIN_GAMES_FOR_BEST_WR = 3
        best_wr_pid, best_wr = None, 0.0
        for pid, d in agg.items():
            if d["games"] < MIN_GAMES_FOR_BEST_WR:
                continue
            wr = d["wins"] / d["games"] * 100
            if wr > best_wr:
                best_wr, best_wr_pid = wr, pid

        avg_elo = db.session.query(func.avg(Player.elo)).filter(
            Player.id.in_(agg.keys())
        ).scalar()

        def _name(pid):
            if pid is None:
                return None
            p = db.session.get(Player, pid)
            return p.display_name if p else None

        return {
            "games_count": games_count,
            "players_count": len(agg),
            "avg_elo": round(avg_elo) if avg_elo else None,
            "best_win_rate": round(best_wr, 1) if best_wr_pid else None,
            "best_win_rate_player": _name(best_wr_pid),
            "longest_streak": longest_streak or None,
            "longest_streak_player": _name(longest_streak_pid) if longest_streak else None,
        }
