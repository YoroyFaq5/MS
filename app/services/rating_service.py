"""
Rating Service  (extended — v2)
================================
Handles global rating AND tournament/stage/team scoped ratings.

Design rules:
- Pure Python + SQLAlchemy ORM.  No Flask imports.
- All new methods are additive — original compute_all_ratings() unchanged.
- is_ranked flag on Game controls global rating inclusion.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Sequence

from sqlalchemy.orm import contains_eager

from app import db
from app.models import Player, GameSlot, Game, Role, WinSide


# ---------------------------------------------------------------------------
# Base score table  (unchanged)
# ---------------------------------------------------------------------------

# ── New scoring: 1 point for win, 0 for loss — all roles equal ──────────────
# bonus_score (float, admin-assigned) is added on top via GameSlot.bonus_score.
BASE_SCORES: dict[tuple[Role, WinSide], float] = {
    # Mafia side wins
    (Role.MAFIA,    WinSide.MAFIA): 1.0,
    (Role.DON,      WinSide.MAFIA): 1.0,
    # Mafia side loses
    (Role.MAFIA,    WinSide.CITY):  0.0,
    (Role.DON,      WinSide.CITY):  0.0,
    # City side wins
    (Role.CIVILIAN, WinSide.CITY):  1.0,
    (Role.SHERIFF,  WinSide.CITY):  1.0,
    # City side loses
    (Role.CIVILIAN, WinSide.MAFIA): 0.0,
    (Role.SHERIFF,  WinSide.MAFIA): 0.0,
    # Draw / unfinished
    (Role.MAFIA,    WinSide.NONE):  0.0,
    (Role.DON,      WinSide.NONE):  0.0,
    (Role.CIVILIAN, WinSide.NONE):  0.0,
    (Role.SHERIFF,  WinSide.NONE):  0.0,
}


def calculate_base_score(role: Role, win_side: WinSide) -> float:
    return BASE_SCORES.get((role, win_side), 0.0)


# ---------------------------------------------------------------------------
# DTOs
# ---------------------------------------------------------------------------

@dataclass
class PlayerRating:
    player_id: int
    player_name: str
    display_name: str
    games_played: int = 0
    games_won: int = 0
    total_score: float = 0.0
    avg_score: float = 0.0
    mafia_games: int = 0
    city_games: int = 0
    sheriff_games: int = 0
    don_games: int = 0
    win_rate: float = 0.0
    rank: int = 0
    elo: float = 1000.0

    def to_dict(self) -> dict:
        return {
            "rank": self.rank,
            "player_id": self.player_id,
            "player_name": self.player_name,
            "display_name": self.display_name,
            "games_played": self.games_played,
            "games_won": self.games_won,
            "win_rate": round(self.win_rate, 1),
            "total_score": round(self.total_score, 2),
            "avg_score": round(self.avg_score, 2),
            "mafia_games": self.mafia_games,
            "city_games": self.city_games,
            "sheriff_games": self.sheriff_games,
            "don_games": self.don_games,
            "elo": round(self.elo, 1),
        }


@dataclass
class PlayerForm:
    """Recent-form snapshot for one player — see RatingService.get_recent_form."""
    results: List[bool] = field(default_factory=list)  # oldest -> newest, True=win
    streak_won: Optional[bool] = None  # None if no ranked games at all
    streak_count: int = 0


@dataclass
class TeamRating:
    team_id: int
    team_name: str
    color: Optional[str]
    member_count: int = 0
    games_played: int = 0
    games_won: int = 0
    total_score: float = 0.0
    avg_score: float = 0.0
    win_rate: float = 0.0
    rank: int = 0

    def to_dict(self) -> dict:
        return {
            "rank": self.rank,
            "team_id": self.team_id,
            "team_name": self.team_name,
            "color": self.color,
            "member_count": self.member_count,
            "games_played": self.games_played,
            "games_won": self.games_won,
            "win_rate": round(self.win_rate, 1),
            "total_score": round(self.total_score, 2),
            "avg_score": round(self.avg_score, 2),
        }


@dataclass
class RoleTournamentStats:
    """
    Per-role win/score breakdown + ПУ/Ci/ЛХ totals, scoped to one
    tournament or one stage (series) — see RatingService.get_role_breakdown.
    Attached onto the matching PlayerRating by the caller (as
    `.role_stats`), not merged into the PlayerRating dataclass itself, so
    every existing PlayerRating caller/to_dict() stays untouched.
    """
    wins_sheriff: int = 0
    wins_don: int = 0
    wins_mafia: int = 0     # обычная мафия (не Дон) — "лучший чёрный"
    wins_civilian: int = 0  # мирный без роли шерифа — "лучший красный"
    score_sheriff: float = 0.0
    score_don: float = 0.0
    score_mafia: float = 0.0
    score_civilian: float = 0.0
    pu_count: int = 0        # раз был ПУ ("убийств")
    ci_total: float = 0.0    # компенсационные баллы ФСМ (Ci)
    lh_total: float = 0.0    # бонус за успешный ПУ-звонок ("ЛХ")
    bonus_total: float = 0.0  # bonus_score, любая роль — критерий MVP


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _slots_to_player_rating(player: Player, slots: Sequence[GameSlot]) -> PlayerRating:
    """Aggregate a list of GameSlots into a PlayerRating DTO."""
    pr = PlayerRating(
        player_id=player.id,
        player_name=player.name,
        display_name=player.display_name,
        elo=player.elo,
    )
    for slot in slots:
        pr.games_played += 1
        pr.total_score += slot.total_score
        if slot.role == Role.MAFIA:
            pr.mafia_games += 1
        elif slot.role == Role.DON:
            pr.don_games += 1
        elif slot.role == Role.SHERIFF:
            pr.sheriff_games += 1
        else:
            pr.city_games += 1

        game = slot.game
        won = (
            (slot.is_mafia_side and game.win_side == WinSide.MAFIA)
            or (slot.is_city_side and game.win_side == WinSide.CITY)
        )
        if won:
            pr.games_won += 1

    if pr.games_played > 0:
        pr.avg_score = round(pr.total_score / pr.games_played, 2)
        pr.win_rate = round(pr.games_won / pr.games_played * 100, 1)

    return pr


def _rank(ratings: list) -> list:
    ratings.sort(key=lambda r: (-r.total_score, -r.avg_score))
    for idx, r in enumerate(ratings, 1):
        r.rank = idx
    return ratings


# ---------------------------------------------------------------------------
# RatingService
# ---------------------------------------------------------------------------

class RatingService:

    # ── Global rating ────────────────────────────────────────────────────────

    @staticmethod
    def compute_all_ratings(as_of: Optional[datetime] = None) -> List[PlayerRating]:
        """
        Global rating: only finished, is_ranked=True games count.
        Original API preserved (as_of=None keeps the exact old behaviour).

        as_of (optional): restrict to games played on/before this moment —
        lets a caller reconstruct "what the rating table looked like N
        days ago" (e.g. for a 30-day rank-movement indicator) by calling
        this twice, once with as_of=None and once with as_of=<cutoff>,
        without a separate historical-snapshot table.

        Fetches all qualifying slots in a single query and groups them in
        Python, instead of one query per player (was O(active_players)
        round-trips per call — noticeable when this runs once per game,
        as it does via the top1_global achievement check).
        """
        players = (
            db.session.query(Player)
            .filter(Player.is_active == True)
            .all()
        )
        query = (
            db.session.query(GameSlot)
            .join(Game)
            .options(contains_eager(GameSlot.game))
            .filter(Game.is_finished == True, Game.is_ranked == True)
        )
        if as_of is not None:
            query = query.filter(Game.played_at <= as_of)
        all_slots = query.all()
        slots_by_player: dict[int, list] = {}
        for slot in all_slots:
            slots_by_player.setdefault(slot.player_id, []).append(slot)

        ratings: List[PlayerRating] = []
        for player in players:
            slots = slots_by_player.get(player.id)
            if not slots:
                continue
            ratings.append(_slots_to_player_rating(player, slots))
        return _rank(ratings)

    @staticmethod
    def get_recent_form(player_ids: Sequence[int], limit: int = 8) -> dict:
        """
        Last `limit` ranked/finished results per player (for a mini
        "form" sparkline) plus their current win/loss streak — one batch
        query for the given player_ids, not one query per player. Meant
        for a small, already-selected set (e.g. a top-N leaderboard row
        set on the homepage), not the whole roster.

        Returns {player_id: PlayerForm}. PlayerForm.results is ordered
        oldest -> newest (so a sparkline reads left-to-right chronologically).
        """
        if not player_ids:
            return {}
        rows = (
            db.session.query(GameSlot.player_id, GameSlot.role, Game.win_side)
            .join(Game)
            .filter(
                GameSlot.player_id.in_(list(player_ids)),
                Game.is_finished == True,
                Game.is_ranked == True,
            )
            .order_by(Game.played_at.desc())
            .all()
        )
        by_player: dict[int, list] = {}
        for player_id, role, win_side in rows:
            by_player.setdefault(player_id, []).append((role, win_side))

        forms: dict[int, PlayerForm] = {}
        for pid in player_ids:
            entries = by_player.get(pid, [])[:limit]  # newest-first, capped
            results = []
            for role, win_side in entries:
                is_mafia_side = role in (Role.MAFIA, Role.DON)
                won = (
                    (is_mafia_side and win_side == WinSide.MAFIA)
                    or (not is_mafia_side and win_side == WinSide.CITY)
                )
                results.append(won)

            streak_won = results[0] if results else None
            streak_count = 0
            for won in results:
                if won == streak_won:
                    streak_count += 1
                else:
                    break

            forms[pid] = PlayerForm(
                results=list(reversed(results)),
                streak_won=streak_won,
                streak_count=streak_count,
            )
        return forms

    @staticmethod
    def get_global_rating() -> List[PlayerRating]:
        """Alias for compute_all_ratings() — explicit name for API clarity."""
        return RatingService.compute_all_ratings()

    @staticmethod
    def get_player_rating(player_id: int) -> Optional[PlayerRating]:
        all_ratings = RatingService.compute_all_ratings()
        return next((r for r in all_ratings if r.player_id == player_id), None)

    # ── Tournament scoped ────────────────────────────────────────────────────

    @staticmethod
    def get_tournament_rating(tournament_id: int) -> List[PlayerRating]:
        """
        Rating across ALL stages/games of a tournament.
        Only finished games inside this tournament are aggregated.
        """
        players_in_tourney = (
            db.session.query(Player)
            .join(Player.tournament_participations)
            .filter_by(tournament_id=tournament_id)
            .all()
        )
        ratings: List[PlayerRating] = []
        for player in players_in_tourney:
            slots = (
                db.session.query(GameSlot)
                .join(Game)
                .filter(
                    GameSlot.player_id == player.id,
                    Game.is_finished == True,
                    Game.tournament_id == tournament_id,
                )
                .all()
            )
            if not slots:
                pr = PlayerRating(
                    player_id=player.id,
                    player_name=player.name,
                    display_name=player.display_name,
                    elo=player.elo,
                )
                ratings.append(pr)
                continue
            ratings.append(_slots_to_player_rating(player, slots))
        return _rank(ratings)

    # ── Stage scoped ─────────────────────────────────────────────────────────

    @staticmethod
    def get_stage_rating(stage_id: int) -> List[PlayerRating]:
        """Rating scoped to a single tournament stage."""
        from app.models import TournamentParticipant, TournamentStage
        stage = db.session.get(TournamentStage, stage_id)
        if not stage:
            return []

        players_in_tourney = (
            db.session.query(Player)
            .join(Player.tournament_participations)
            .filter_by(tournament_id=stage.tournament_id)
            .all()
        )
        ratings: List[PlayerRating] = []
        for player in players_in_tourney:
            slots = (
                db.session.query(GameSlot)
                .join(Game)
                .filter(
                    GameSlot.player_id == player.id,
                    Game.is_finished == True,
                    Game.stage_id == stage_id,
                )
                .all()
            )
            if not slots:
                continue
            ratings.append(_slots_to_player_rating(player, slots))
        return _rank(ratings)

    # ── Role/ПУ/Ci breakdown + superlatives ─────────────────────────────────

    @staticmethod
    def get_role_breakdown(
        tournament_id: Optional[int] = None, stage_id: Optional[int] = None
    ) -> dict[int, RoleTournamentStats]:
        """
        Per-role win counts + per-role total_score sums + ПУ count +
        Ci/ЛХ/bonus totals, scoped to one tournament or one stage — a
        single bulk query (unlike get_tournament_rating/get_stage_rating's
        one-query-per-player loop), same is_finished-only filter (no
        is_ranked filter) so numbers line up with those methods' columns.
        """
        query = (
            db.session.query(GameSlot)
            .join(Game)
            .options(contains_eager(GameSlot.game))
            .filter(Game.is_finished == True)
        )
        if tournament_id is not None:
            query = query.filter(Game.tournament_id == tournament_id)
        if stage_id is not None:
            query = query.filter(Game.stage_id == stage_id)
        slots = query.all()

        breakdown: dict[int, RoleTournamentStats] = {}
        for slot in slots:
            stats = breakdown.setdefault(slot.player_id, RoleTournamentStats())
            won = (
                (slot.is_mafia_side and slot.game.win_side == WinSide.MAFIA)
                or (slot.is_city_side and slot.game.win_side == WinSide.CITY)
            )
            score = slot.total_score
            if slot.role == Role.SHERIFF:
                stats.score_sheriff += score
                if won:
                    stats.wins_sheriff += 1
            elif slot.role == Role.DON:
                stats.score_don += score
                if won:
                    stats.wins_don += 1
            elif slot.role == Role.MAFIA:
                stats.score_mafia += score
                if won:
                    stats.wins_mafia += 1
            else:  # CIVILIAN
                stats.score_civilian += score
                if won:
                    stats.wins_civilian += 1

            if slot.is_pu:
                stats.pu_count += 1
            stats.ci_total += slot.compensation_score
            stats.lh_total += slot.pu_bonus
            stats.bonus_total += slot.bonus_score

        return breakdown

    @staticmethod
    def pick_role_superlatives(
        ratings: List[PlayerRating], role_stats: dict[int, RoleTournamentStats]
    ) -> dict[str, Optional[PlayerRating]]:
        """
        MVP (наибольшая сумма bonus_score, любая роль) + "лучший" по каждой
        из 4 ролей (наибольшая сумма total_score именно в этой роли).
        Побеждает только при значении > 0 — если никто не набрал бонусов/
        очков в роли, соответствующий титул остаётся пустым (None), а не
        достаётся случайному игроку с нулём.

        Победившему PlayerRating выставляется `.superlative_value` — то
        самое число, по которому он победил (шаблон не лезет обратно в
        role_stats).
        """
        def pick(attr: str) -> Optional[PlayerRating]:
            best, best_val = None, 0.0
            for r in ratings:
                stats = role_stats.get(r.player_id)
                if not stats:
                    continue
                val = getattr(stats, attr)
                if val > best_val:
                    best_val, best = val, r
            if best is not None:
                best.superlative_value = best_val
            return best

        return {
            "mvp": pick("bonus_total"),
            "don": pick("score_don"),
            "sheriff": pick("score_sheriff"),
            "civilian": pick("score_civilian"),
            "mafia": pick("score_mafia"),
        }

    # ── Team rating ──────────────────────────────────────────────────────────

    @staticmethod
    def get_team_rating(tournament_id: int) -> List[TeamRating]:
        """
        Team rating = sum of all member scores within tournament games.
        Each game slot contributes to its player's team.
        """
        from app.models import Team, TeamPlayer

        teams = (
            db.session.query(Team)
            .filter_by(tournament_id=tournament_id)
            .all()
        )
        ratings: List[TeamRating] = []

        for team in teams:
            tr = TeamRating(
                team_id=team.id,
                team_name=team.name,
                color=team.color,
                member_count=len(team.members),
            )
            # Aggregate individual scores of all team members in this tournament
            member_player_ids = [m.player_id for m in team.members]
            if not member_player_ids:
                ratings.append(tr)
                continue

            slots = (
                db.session.query(GameSlot)
                .join(Game)
                .filter(
                    GameSlot.player_id.in_(member_player_ids),
                    Game.is_finished == True,
                    Game.tournament_id == tournament_id,
                )
                .all()
            )
            for slot in slots:
                tr.games_played += 1
                tr.total_score += slot.total_score
                game = slot.game
                won = (
                    (slot.is_mafia_side and game.win_side == WinSide.MAFIA)
                    or (slot.is_city_side and game.win_side == WinSide.CITY)
                )
                if won:
                    tr.games_won += 1

            if tr.games_played > 0:
                tr.avg_score = round(tr.total_score / tr.games_played, 2)
                tr.win_rate = round(tr.games_won / tr.games_played * 100, 1)

            ratings.append(tr)

        return _rank(ratings)

    # ── Apply scores ─────────────────────────────────────────────────────────

    # ── Season scoped ratings ────────────────────────────────────────────────

    @staticmethod
    def get_season_rating(season_id: int) -> List["SeasonRatingEntry"]:
        """
        Season rating using the canonical SeasonRatingEngine formula:
            SeasonRating = (TotalPoints * WR%) + (GG * 0.2)

        Returns SeasonRatingEntry list (not PlayerRating) — callers that
        only need rank/display_name/total use .season_rating attribute.
        """
        from app.services.season_rating_engine import SeasonRatingEngine
        return SeasonRatingEngine.compute_season_ratings(season_id)

    @staticmethod
    def get_year_rating(year: int) -> List[PlayerRating]:
        """
        Aggregate rating across all 6 seasons of a calendar year.
        Only ranked games whose played_at falls within that year.
        """
        from app.models import Season
        from sqlalchemy import extract

        players = db.session.query(Player).filter_by(is_active=True).all()
        ratings: List[PlayerRating] = []

        # Collect all season IDs for the year
        season_ids = [
            s.id for s in
            db.session.query(Season).filter_by(year=year).all()
        ]
        if not season_ids:
            return []

        for player in players:
            slots = (
                db.session.query(GameSlot)
                .join(Game)
                .filter(
                    GameSlot.player_id == player.id,
                    Game.is_finished == True,
                    Game.is_ranked == True,
                    Game.season_id.in_(season_ids),
                )
                .all()
            )
            if not slots:
                continue
            ratings.append(_slots_to_player_rating(player, slots))

        return _rank(ratings)

    @staticmethod
    def get_player_season_rating(player_id: int, season_id: int) -> Optional[PlayerRating]:
        ratings = RatingService.get_season_rating(season_id)
        return next((r for r in ratings if r.player_id == player_id), None)

    @staticmethod
    def apply_base_scores_to_game(game: Game, commit: bool = False) -> None:
        """
        Recalculate and persist base_score for all slots in a finished game.
        commit defaults to False since this is normally the first step of
        PostGameOrchestrator.run(), which commits once at the end of the
        pipeline; pass commit=True when calling this standalone.
        """
        for slot in game.slots:
            slot.base_score = calculate_base_score(slot.role, game.win_side)
        if commit:
            db.session.commit()

    # ── Компенсационные баллы (Правила ФСМ, п.8.6.1-8.6.5) ──────────────────

    @staticmethod
    def _compensation_coefficient(kills: int, games_played: int) -> float:
        """
        Ci по п.8.6.1-8.6.2: доля 0.4, растущая линейно с частотой
        "отстрелов в 1-ю ночь" игрока на дистанции, с потолком 0.4.

        B = round(0.4 * games_played) — "ожидаемое" число отстрелов.
        Ci = i * 0.4 / B, если i <= B (не более ожидаемого — компенсация
             пропорциональна фактической частоте);
        Ci = 0.4, если i > B (чаще ожидаемого — компенсация капается сверху).
        i == 0 или games_played == 0 (=> B == 0 при i == 0) → 0.0, отстрелов
        не было — компенсировать нечего.
        """
        if kills <= 0:
            return 0.0
        expected = round(0.4 * games_played)
        if expected <= 0 or kills > expected:
            return 0.4
        return round(kills * 0.4 / expected, 4)

    @staticmethod
    def recompute_compensation_points(tournament_id: int, commit: bool = True) -> int:
        """
        Recompute GameSlot.compensation_score for every player who has at
        least one finished game in this tournament ("дистанция" = весь
        турнир целиком, упрощение для v1 — см. п.8.6.5 про раздельные
        дистанции по стадиям, сознательно не реализовано).

        Правило (п.8.6.1-8.6.4): игрок, убитый в 1-ю ночь на роли мирного
        или шерифа ("красная" команда = городская сторона), получает Ci
        основных баллов, если его команда проиграла (п.8.6.3), либо 0.5*Ci,
        если команда выиграла, но он успел в лучшем ходе назвать хотя бы
        одного реального "чёрного" (мафию) — п.8.6.4.

        Полностью пересчитывает compensation_score с нуля для ВСЕХ слотов
        затронутых игроков в этом турнире (включая обнуление у слотов,
        переставших подходить под условия) — безопасно перезапускать сколько
        угодно раз, идемпотентно.

        Returns the number of players recomputed.
        """
        games = (
            db.session.query(Game)
            .filter(Game.tournament_id == tournament_id, Game.is_finished == True)
            .all()
        )
        if not games:
            return 0

        slots_by_player: dict[int, list[GameSlot]] = {}
        for g in games:
            for slot in g.slots:
                slots_by_player.setdefault(slot.player_id, []).append(slot)

        for player_id, slots in slots_by_player.items():
            games_played = len(slots)
            qualifying = [
                s for s in slots
                if s.is_pu and s.role in (Role.CIVILIAN, Role.SHERIFF)
            ]
            ci = RatingService._compensation_coefficient(len(qualifying), games_played)

            for slot in slots:
                if slot not in qualifying:
                    slot.compensation_score = 0.0
                    continue
                win_side = slot.game.win_side
                if win_side == WinSide.MAFIA:
                    # "Красная" (городская) команда проиграла — полная компенсация.
                    slot.compensation_score = ci
                elif win_side == WinSide.CITY and (slot.pu_mafia_count or 0) >= 1:
                    # Команда выиграла, но игрок успел назвать мафию — половина.
                    slot.compensation_score = round(ci * 0.5, 2)
                else:
                    slot.compensation_score = 0.0

        if commit:
            db.session.commit()
        return len(slots_by_player)


