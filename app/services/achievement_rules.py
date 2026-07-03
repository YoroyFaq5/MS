"""
achievement_rules
==================
Rule registry — the Open/Closed core of the achievement system.

Each Achievement DB row (app/models/Achievement) is admin-editable
presentation data (name/description/icon/rarity/hidden/category) linked to
exactly one entry here via its unique `code`. AchievementService's dispatch
loops (check_after_game/tournament/season/purchase) never change when a new
achievement is added — you only ever add a new AchievementRule below (plus
a matching seeded Achievement row with the same code).

check(player_id, context) -> bool must be a *fast* read — it runs once per
candidate player per hook firing. Rules that need something expensive
(e.g. the full global rating list) should memoize it onto `context` so it's
computed once per hook call, not once per rule per player.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, List

from sqlalchemy import func

from app import db
from app.models import (
    Player, Game, GameSlot, Role, WinSide,
    TournamentParticipant, FantasyDraft,
    CoinTransaction, Season, SeasonStatus,
    AchievementTrigger,
)


@dataclass
class AchievementRule:
    code: str
    trigger: AchievementTrigger
    check: Callable[[int, dict], bool]


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _finished_slots_count(player_id: int, won_only: bool = False, roles=None) -> int:
    q = (
        db.session.query(func.count(GameSlot.id))
        .join(Game)
        .filter(GameSlot.player_id == player_id, Game.is_finished == True)
    )
    if roles:
        q = q.filter(GameSlot.role.in_(roles))
    if not won_only:
        return q.scalar() or 0

    # Winning requires joining win_side vs role side — do it in Python over
    # a small projection rather than a complex SQL boolean expression.
    rows = (
        db.session.query(GameSlot.role, Game.win_side)
        .join(Game)
        .filter(GameSlot.player_id == player_id, Game.is_finished == True)
        .all()
    )
    if roles:
        rows = [r for r in rows if r[0] in roles]
    count = 0
    for role, win_side in rows:
        is_mafia_side = role in (Role.MAFIA, Role.DON)
        is_city_side = role in (Role.CIVILIAN, Role.SHERIFF)
        won = (is_mafia_side and win_side == WinSide.MAFIA) or (is_city_side and win_side == WinSide.CITY)
        if won:
            count += 1
    return count


def _current_win_streak_at_least(player_id: int, n: int) -> bool:
    """Fetch only the last n finished games — bounded query, not a full scan."""
    slots = (
        db.session.query(GameSlot.role, Game.win_side)
        .join(Game)
        .filter(GameSlot.player_id == player_id, Game.is_finished == True)
        .order_by(Game.played_at.desc())
        .limit(n)
        .all()
    )
    if len(slots) < n:
        return False
    for role, win_side in slots:
        is_mafia_side = role in (Role.MAFIA, Role.DON)
        is_city_side = role in (Role.CIVILIAN, Role.SHERIFF)
        won = (is_mafia_side and win_side == WinSide.MAFIA) or (is_city_side and win_side == WinSide.CITY)
        if not won:
            return False
    return True


def _cached_global_ratings(context: dict):
    """Memoized onto context so it's computed at most once per hook call,
    regardless of how many GAME-trigger rules or players need it."""
    if "_global_ratings" not in context:
        from app.services.rating_service import RatingService
        context["_global_ratings"] = RatingService.get_global_rating()
    return context["_global_ratings"]


def _lifetime_coins_earned(player_id: int) -> float:
    total = (
        db.session.query(func.sum(CoinTransaction.amount))
        .filter(CoinTransaction.player_id == player_id, CoinTransaction.amount > 0)
        .scalar()
    )
    return float(total or 0.0)


# ---------------------------------------------------------------------------
# GAME-trigger rules
# ---------------------------------------------------------------------------

def _r_games_played(threshold: int):
    return lambda player_id, ctx: _finished_slots_count(player_id) >= threshold


def _r_wins(threshold: int):
    return lambda player_id, ctx: _finished_slots_count(player_id, won_only=True) >= threshold


def _r_win_streak(n: int):
    return lambda player_id, ctx: _current_win_streak_at_least(player_id, n)


def _r_role_wins(threshold: int, roles):
    return lambda player_id, ctx: _finished_slots_count(player_id, won_only=True, roles=roles) >= threshold


def _r_elo_at_least(threshold: float):
    def check(player_id, ctx):
        player = db.session.get(Player, player_id)
        return bool(player and player.elo >= threshold)
    return check


def _r_global_rank_1(player_id, ctx):
    ratings = _cached_global_ratings(ctx)
    return any(r.player_id == player_id and r.rank == 1 for r in ratings)


def _r_coins_earned(threshold: float):
    return lambda player_id, ctx: _lifetime_coins_earned(player_id) >= threshold


# ---------------------------------------------------------------------------
# TOURNAMENT-trigger rules — expect ctx["ratings"] (List[PlayerRating],
# precomputed once per tournament by AchievementService.check_after_tournament)
# ---------------------------------------------------------------------------

def _r_tournament_rank_1(player_id, ctx):
    ratings = ctx.get("ratings") or []
    return any(r.player_id == player_id and r.rank == 1 for r in ratings)


def _r_tournament_participations(threshold: int):
    def check(player_id, ctx):
        count = (
            db.session.query(func.count(TournamentParticipant.id))
            .filter(TournamentParticipant.player_id == player_id)
            .scalar()
        )
        return (count or 0) >= threshold
    return check


def _r_fantasy_leaderboard_1(player_id, ctx):
    from app.services.fantasy_service import FantasyService
    tournament = ctx.get("tournament")
    player = db.session.get(Player, player_id)
    if not tournament or not player or not player.user:
        return False
    leaderboard = FantasyService.get_leaderboard(tournament.id)
    return any(e.user_id == player.user.id and e.rank == 1 for e in leaderboard)


def _r_fantasy_draft_count(threshold: int):
    def check(player_id, ctx):
        player = db.session.get(Player, player_id)
        if not player or not player.user:
            return False
        count = (
            db.session.query(func.count(FantasyDraft.id))
            .filter(FantasyDraft.user_id == player.user.id)
            .scalar()
        )
        return (count or 0) >= threshold
    return check


# ---------------------------------------------------------------------------
# SEASON-trigger rules — expect ctx["season"] (Season, precomputed once by
# AchievementService.check_after_season)
# ---------------------------------------------------------------------------

def _r_season_winner(player_id, ctx):
    season = ctx.get("season")
    return bool(season and season.winner_player_id == player_id)


def _r_season_top3_count(threshold: int):
    def check(player_id, ctx):
        from app.services.season_rating_engine import SeasonRatingEngine
        seasons = (
            db.session.query(Season)
            .filter(Season.status == SeasonStatus.FINISHED)
            .all()
        )
        top3_count = 0
        for s in seasons:
            entry = SeasonRatingEngine.get_player_rank(player_id, s.id)
            if entry and entry.rank <= 3:
                top3_count += 1
        return top3_count >= threshold
    return check


# ---------------------------------------------------------------------------
# PURCHASE-trigger rules
# ---------------------------------------------------------------------------

def _r_first_purchase(player_id, ctx):
    from app.models import InventoryItem
    count = (
        db.session.query(func.count(InventoryItem.id))
        .filter(InventoryItem.player_id == player_id, InventoryItem.source == "purchase")
        .scalar()
    )
    return (count or 0) >= 1


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

RULES: List[AchievementRule] = [
    # ── Games ────────────────────────────────────────────────────
    AchievementRule("games_played_10",  AchievementTrigger.GAME, _r_games_played(10)),
    AchievementRule("games_played_100", AchievementTrigger.GAME, _r_games_played(100)),
    AchievementRule("games_played_500", AchievementTrigger.GAME, _r_games_played(500)),

    # ── Wins ─────────────────────────────────────────────────────
    AchievementRule("wins_10",              AchievementTrigger.GAME, _r_wins(10)),
    AchievementRule("wins_streak_5",        AchievementTrigger.GAME, _r_win_streak(5)),
    AchievementRule("perfect_role_mafia_10", AchievementTrigger.GAME, _r_role_wins(10, (Role.MAFIA, Role.DON))),

    # ── Rating ───────────────────────────────────────────────────
    AchievementRule("elo_1500",   AchievementTrigger.GAME, _r_elo_at_least(1500)),
    AchievementRule("elo_1800",   AchievementTrigger.GAME, _r_elo_at_least(1800)),
    AchievementRule("top1_global", AchievementTrigger.GAME, _r_global_rank_1),

    # ── Tournaments ──────────────────────────────────────────────
    AchievementRule("tournament_win_1",         AchievementTrigger.TOURNAMENT, _r_tournament_rank_1),
    AchievementRule("tournament_participant_10", AchievementTrigger.TOURNAMENT, _r_tournament_participations(10)),

    # ── Seasons ──────────────────────────────────────────────────
    AchievementRule("season_win_1",   AchievementTrigger.SEASON, _r_season_winner),
    AchievementRule("season_top3_3",  AchievementTrigger.SEASON, _r_season_top3_count(3)),

    # ── Fantasy (scored alongside tournament finish) ────────────
    AchievementRule("fantasy_leaderboard_1", AchievementTrigger.TOURNAMENT, _r_fantasy_leaderboard_1),
    AchievementRule("fantasy_participant_5", AchievementTrigger.TOURNAMENT, _r_fantasy_draft_count(5)),

    # ── Economy ──────────────────────────────────────────────────
    AchievementRule("coins_earned_1000",  AchievementTrigger.GAME, _r_coins_earned(1000)),
    AchievementRule("coins_earned_10000", AchievementTrigger.GAME, _r_coins_earned(10000)),

    # ── Social ───────────────────────────────────────────────────
    AchievementRule("shop_first_purchase", AchievementTrigger.PURCHASE, _r_first_purchase),
    # "account_linked" is unlocked directly (unconditionally, one-shot) from
    # the account-linking action — no rule needed, see AchievementService.

    # "founder" (SPECIAL) is admin-granted only via AchievementService.admin_grant
    # — intentionally no rule entry.
]


def get_rules_for_trigger(trigger: AchievementTrigger) -> List[AchievementRule]:
    return [r for r in RULES if r.trigger == trigger]
