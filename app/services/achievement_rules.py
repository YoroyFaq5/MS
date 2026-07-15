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
    Tournament, TournamentParticipant,
    FantasyDraft, FantasyDraftPick,
    CoinTransaction, CoinSourceType, Season, SeasonStatus,
    InventoryItem, ShopItem, ShopCategory, Rarity,
    Title, PlayerTitle,
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


def _recent_results(player_id: int, limit: int) -> list[bool]:
    """Last `limit` finished-game results, newest first, as a list of booleans."""
    rows = (
        db.session.query(GameSlot.role, Game.win_side)
        .join(Game)
        .filter(GameSlot.player_id == player_id, Game.is_finished == True)
        .order_by(Game.played_at.desc())
        .limit(limit)
        .all()
    )
    results = []
    for role, win_side in rows:
        is_mafia_side = role in (Role.MAFIA, Role.DON)
        is_city_side = role in (Role.CIVILIAN, Role.SHERIFF)
        won = (is_mafia_side and win_side == WinSide.MAFIA) or (is_city_side and win_side == WinSide.CITY)
        results.append(won)
    return results


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


def _lifetime_coins_spent(player_id: int) -> float:
    """Sum of PURCHASE-sourced debits (covers both regular buys and unique-item
    buyouts — both go through EconomyService.spend_coins with the same
    source type). Ledger-based, so it stays correct even after an item is
    later gifted away (unlike summing InventoryItem.price_paid, which would
    undercount once ownership moves to someone else)."""
    total = (
        db.session.query(func.sum(CoinTransaction.amount))
        .filter(
            CoinTransaction.player_id == player_id,
            CoinTransaction.amount < 0,
            CoinTransaction.source_type == CoinSourceType.PURCHASE,
        )
        .scalar()
    )
    return abs(float(total or 0.0))


def _count_tournament_rank_at_most(player_id: int, max_rank: int) -> int:
    """How many FINISHED tournaments this player ended at rank <= max_rank in.
    Same iterate-all-history pattern as _r_season_top3_count below — an
    infrequent, once-per-tournament-finish operation, not a hot path."""
    from app.services.rating_service import RatingService
    tournaments = (
        db.session.query(Tournament).filter(Tournament.status == "finished").all()
    )
    count = 0
    for t in tournaments:
        ratings = RatingService.get_tournament_rating(t.id)
        entry = next((r for r in ratings if r.player_id == player_id), None)
        if entry and entry.rank <= max_rank:
            count += 1
    return count


def _fantasy_leaderboard_rank_count(player_id: int, max_rank: int) -> int:
    """How many finished tournaments this player's fantasy draft ended at
    leaderboard rank <= max_rank in."""
    from app.services.fantasy_service import FantasyService
    player = db.session.get(Player, player_id)
    if not player or not player.user:
        return 0
    user_id = player.user.id
    tournament_ids = {
        d.tournament_id for d in
        db.session.query(FantasyDraft).filter_by(user_id=user_id).all()
    }
    count = 0
    for tid in tournament_ids:
        leaderboard = FantasyService.get_leaderboard(tid)
        entry = next((e for e in leaderboard if e.user_id == user_id), None)
        if entry and entry.rank <= max_rank:
            count += 1
    return count


# ---------------------------------------------------------------------------
# GAME-trigger rules
# ---------------------------------------------------------------------------

def _r_games_played(threshold: int):
    return lambda player_id, ctx: _finished_slots_count(player_id) >= threshold


def _r_role_games_played(threshold: int, roles):
    return lambda player_id, ctx: _finished_slots_count(player_id, roles=roles) >= threshold


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


def _r_global_rank_at_most(max_rank: int):
    def check(player_id, ctx):
        ratings = _cached_global_ratings(ctx)
        return any(r.player_id == player_id and r.rank <= max_rank for r in ratings)
    return check


def _r_coins_earned(threshold: float):
    return lambda player_id, ctx: _lifetime_coins_earned(player_id) >= threshold


def _r_balance_at_least(threshold: float):
    def check(player_id, ctx):
        player = db.session.get(Player, player_id)
        return bool(player and player.coins >= threshold)
    return check


def _r_comeback(loss_streak: int):
    """Most recent finished game is a win, immediately preceded by
    `loss_streak` consecutive losses."""
    def check(player_id, ctx):
        results = _recent_results(player_id, loss_streak + 1)  # newest first
        if len(results) < loss_streak + 1:
            return False
        return results[0] and not any(results[1:loss_streak + 1])
    return check


def _r_win_rate_recent(min_games: int, min_pct: float):
    def check(player_id, ctx):
        results = _recent_results(player_id, min_games)
        if len(results) < min_games:
            return False
        return (sum(results) / len(results)) * 100 >= min_pct
    return check


def _r_best_move_count(threshold: int):
    def check(player_id, ctx):
        count = (
            db.session.query(func.count(GameSlot.id))
            .join(Game)
            .filter(
                GameSlot.player_id == player_id,
                Game.is_finished == True,
                GameSlot.was_best_move == True,
            )
            .scalar()
        )
        return (count or 0) >= threshold
    return check


def _r_pu_perfect_call(player_id, ctx):
    exists = (
        db.session.query(GameSlot.id)
        .join(Game)
        .filter(
            GameSlot.player_id == player_id,
            Game.is_finished == True,
            GameSlot.is_pu == True,
            GameSlot.pu_mafia_count == 3,
        )
        .first()
    )
    return exists is not None


def _r_games_in_single_day(threshold: int):
    def check(player_id, ctx):
        rows = (
            db.session.query(Game.played_at)
            .join(GameSlot)
            .filter(GameSlot.player_id == player_id, Game.is_finished == True)
            .all()
        )
        by_day: dict = {}
        for (played_at,) in rows:
            day = played_at.date()
            by_day[day] = by_day.get(day, 0) + 1
        return bool(by_day) and max(by_day.values()) >= threshold
    return check


def _r_tenure_years(years: int):
    from datetime import datetime, timezone
    def check(player_id, ctx):
        player = db.session.get(Player, player_id)
        if not player or not player.created_at:
            return False
        created = player.created_at
        now = datetime.now(timezone.utc) if created.tzinfo else datetime.now()
        return (now - created).days >= years * 365
    return check


def _r_profile_complete(player_id, ctx):
    player = db.session.get(Player, player_id)
    if not player:
        return False
    return bool((player.bio or "").strip()) and bool((player.avatar_url or "").strip())


def _r_veteran_combo(years: int, games: int):
    tenure_check = _r_tenure_years(years)
    def check(player_id, ctx):
        return tenure_check(player_id, ctx) and _finished_slots_count(player_id) >= games
    return check


def _r_legend_combo(player_id, ctx):
    player = db.session.get(Player, player_id)
    if not player or player.elo < 1800:
        return False
    if not _r_global_rank_at_most(3)(player_id, ctx):
        return False
    return _count_tournament_rank_at_most(player_id, 1) >= 1


def _r_unlocked_count(threshold: int):
    def check(player_id, ctx):
        from app.models import PlayerAchievement
        count = (
            db.session.query(func.count(PlayerAchievement.id))
            .filter(PlayerAchievement.player_id == player_id)
            .scalar()
        )
        return (count or 0) >= threshold
    return check


def _r_category_complete(codes: set):
    def check(player_id, ctx):
        from app.models import PlayerAchievement, Achievement
        count = (
            db.session.query(func.count(PlayerAchievement.id))
            .join(Achievement)
            .filter(PlayerAchievement.player_id == player_id, Achievement.code.in_(codes))
            .scalar()
        )
        return (count or 0) >= len(codes)
    return check


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


def _r_tournament_wins_count(threshold: int):
    return lambda player_id, ctx: _count_tournament_rank_at_most(player_id, 1) >= threshold


def _r_tournament_top3_count(threshold: int):
    return lambda player_id, ctx: _count_tournament_rank_at_most(player_id, 3) >= threshold


def _r_tournament_flawless(player_id, ctx):
    tournament = ctx.get("tournament")
    if not tournament:
        return False
    rows = (
        db.session.query(GameSlot.role, Game.win_side)
        .join(Game)
        .filter(
            GameSlot.player_id == player_id,
            Game.is_finished == True,
            Game.tournament_id == tournament.id,
        )
        .all()
    )
    if not rows:
        return False
    for role, win_side in rows:
        is_mafia_side = role in (Role.MAFIA, Role.DON)
        is_city_side = role in (Role.CIVILIAN, Role.SHERIFF)
        won = (is_mafia_side and win_side == WinSide.MAFIA) or (is_city_side and win_side == WinSide.CITY)
        if not won:
            return False
    return True


def _r_tournament_advanced_final_count(threshold: int):
    def check(player_id, ctx):
        count = (
            db.session.query(func.count(TournamentParticipant.id))
            .filter(
                TournamentParticipant.player_id == player_id,
                TournamentParticipant.advanced_to_final == True,
            )
            .scalar()
        )
        return (count or 0) >= threshold
    return check


def _r_team_tournament_win(player_id, ctx):
    from app.models import TournamentType
    tournament = ctx.get("tournament")
    if not tournament or tournament.type != TournamentType.TEAM:
        return False
    participant = (
        db.session.query(TournamentParticipant)
        .filter_by(tournament_id=tournament.id, player_id=player_id)
        .first()
    )
    if not participant or not participant.team_id:
        return False
    from app.services.rating_service import RatingService
    team_ratings = RatingService.get_team_rating(tournament.id)
    entry = next((t for t in team_ratings if t.team_id == participant.team_id), None)
    return bool(entry and entry.rank == 1)


def _r_fantasy_leaderboard_1(player_id, ctx):
    from app.services.fantasy_service import FantasyService
    tournament = ctx.get("tournament")
    player = db.session.get(Player, player_id)
    if not tournament or not player or not player.user:
        return False
    leaderboard = FantasyService.get_leaderboard(tournament.id)
    return any(e.user_id == player.user.id and e.rank == 1 for e in leaderboard)


def _r_fantasy_leaderboard_top3_count(threshold: int):
    return lambda player_id, ctx: _fantasy_leaderboard_rank_count(player_id, 3) >= threshold


def _r_fantasy_leaderboard_win_count(threshold: int):
    return lambda player_id, ctx: _fantasy_leaderboard_rank_count(player_id, 1) >= threshold


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


def _r_fantasy_drafted_champion(player_id, ctx):
    tournament = ctx.get("tournament")
    ratings = ctx.get("ratings") or []
    if not tournament or not ratings:
        return False
    champion = next((r for r in ratings if r.rank == 1), None)
    if not champion:
        return False
    player = db.session.get(Player, player_id)
    if not player or not player.user:
        return False
    draft_ids = [
        d.id for d in
        db.session.query(FantasyDraft)
        .filter_by(user_id=player.user.id, tournament_id=tournament.id)
        .all()
    ]
    if not draft_ids:
        return False
    pick = (
        db.session.query(FantasyDraftPick)
        .filter(
            FantasyDraftPick.draft_id.in_(draft_ids),
            FantasyDraftPick.player_id == champion.player_id,
        )
        .first()
    )
    return pick is not None


def _r_fantasy_points_total(threshold: float):
    def check(player_id, ctx):
        player = db.session.get(Player, player_id)
        if not player or not player.user:
            return False
        total = (
            db.session.query(func.sum(FantasyDraft.total_points))
            .filter(FantasyDraft.user_id == player.user.id)
            .scalar()
        )
        return float(total or 0.0) >= threshold
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


def _r_season_wins_count(threshold: int):
    def check(player_id, ctx):
        count = (
            db.session.query(func.count(Season.id))
            .filter(Season.winner_player_id == player_id)
            .scalar()
        )
        return (count or 0) >= threshold
    return check


def _r_season_win_consecutive(n: int):
    def check(player_id, ctx):
        seasons = (
            db.session.query(Season)
            .order_by(Season.year.asc(), Season.number.asc())
            .all()
        )
        run = 0
        for s in seasons:
            if s.winner_player_id == player_id:
                run += 1
                if run >= n:
                    return True
            else:
                run = 0
        return False
    return check


def _r_season_participations(threshold: int):
    def check(player_id, ctx):
        count = (
            db.session.query(func.count(func.distinct(Game.season_id)))
            .join(GameSlot)
            .filter(
                GameSlot.player_id == player_id,
                Game.is_finished == True,
                Game.season_id.isnot(None),
            )
            .scalar()
        )
        return (count or 0) >= threshold
    return check


def _r_seasonal_title_held(title_code: str):
    def check(player_id, ctx):
        exists = (
            db.session.query(PlayerTitle.id)
            .join(Title)
            .filter(PlayerTitle.player_id == player_id, Title.code == title_code)
            .first()
        )
        return exists is not None
    return check


def _r_all_seasonal_role_titles(player_id, ctx):
    from app.services.nomination_service import SEASONAL_ROLE_TITLES
    codes = set(SEASONAL_ROLE_TITLES.values())
    held = {
        code for (code,) in
        db.session.query(Title.code)
        .join(PlayerTitle)
        .filter(PlayerTitle.player_id == player_id, Title.code.in_(codes))
        .all()
    }
    return codes.issubset(held)


def _r_season_reward_received(player_id, ctx):
    exists = (
        db.session.query(CoinTransaction.id)
        .filter(
            CoinTransaction.player_id == player_id,
            CoinTransaction.source_type == CoinSourceType.SEASON_REWARD,
        )
        .first()
    )
    return exists is not None


# ---------------------------------------------------------------------------
# PURCHASE-trigger rules (also used for gift/equip events — see
# AchievementService.check_after_purchase callers in shop_service.py /
# gift_service.py; the trigger name predates those extra call sites but the
# checks below are all plain state facts, not tied to the word "purchase")
# ---------------------------------------------------------------------------

def _r_first_purchase(player_id, ctx):
    count = (
        db.session.query(func.count(InventoryItem.id))
        .filter(InventoryItem.player_id == player_id, InventoryItem.source == "purchase")
        .scalar()
    )
    return (count or 0) >= 1


def _r_inventory_count(threshold: int):
    def check(player_id, ctx):
        count = (
            db.session.query(func.count(InventoryItem.id))
            .filter(InventoryItem.player_id == player_id)
            .scalar()
        )
        return (count or 0) >= threshold
    return check


def _r_owns_all_rarities(player_id, ctx):
    owned = {
        r for (r,) in
        db.session.query(ShopItem.rarity)
        .join(InventoryItem)
        .filter(InventoryItem.player_id == player_id)
        .distinct()
        .all()
    }
    return set(Rarity).issubset(owned)


def _r_owns_unique_item(player_id, ctx):
    exists = (
        db.session.query(InventoryItem.id)
        .join(ShopItem)
        .filter(
            InventoryItem.player_id == player_id,
            ShopItem.rarity.in_((Rarity.MYTHIC, Rarity.ULTRA)),
        )
        .first()
    )
    return exists is not None


def _r_owns_physical_merch(player_id, ctx):
    exists = (
        db.session.query(InventoryItem.id)
        .join(ShopItem)
        .filter(InventoryItem.player_id == player_id, ShopItem.category == ShopCategory.PHYSICAL)
        .first()
    )
    return exists is not None


def _r_shop_all_categories(player_id, ctx):
    owned = {
        c for (c,) in
        db.session.query(ShopItem.category)
        .join(InventoryItem)
        .filter(InventoryItem.player_id == player_id)
        .distinct()
        .all()
    }
    return set(ShopCategory).issubset(owned)


def _r_full_outfit_equipped(player_id, ctx):
    from app.services.shop_service import ShopService
    equipped = ShopService.get_equipped(player_id)
    required = {
        "profile_customization:frame",
        "profile_customization:background",
        "nickname:nick_prefix",
        "nickname:nick_suffix",
    }
    has_nick_color = "nickname:nick_color" in equipped or "nickname:nick_gradient" in equipped
    return required.issubset(equipped.keys()) and has_nick_color


def _r_coins_spent(threshold: float):
    return lambda player_id, ctx: _lifetime_coins_spent(player_id) >= threshold


def _r_gift_sent_count(threshold: int):
    def check(player_id, ctx):
        from app.models import GiftTransfer
        count = (
            db.session.query(func.count(GiftTransfer.id))
            .filter(GiftTransfer.from_player_id == player_id)
            .scalar()
        )
        return (count or 0) >= threshold
    return check


def _r_gift_received_count(threshold: int):
    def check(player_id, ctx):
        from app.models import GiftTransfer
        count = (
            db.session.query(func.count(GiftTransfer.id))
            .filter(GiftTransfer.to_player_id == player_id)
            .scalar()
        )
        return (count or 0) >= threshold
    return check


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

# Full achievement-code coverage per category, used only by the "category
# complete" meta-achievements below — kept as plain literal sets (matches
# the rest of this file's style of explicit, not derived, thresholds).
_GAMES_CATEGORY_CODES = {
    "games_played_10", "games_played_100", "games_played_500",
    "games_played_25", "games_played_50", "games_played_250", "games_played_1000",
    "civilian_games_100", "sheriff_games_50", "don_games_50", "mafia_games_100",
    "games_10_in_one_day", "tenure_1_year", "tenure_3_years",
}
_WINS_CATEGORY_CODES = {
    "wins_10", "wins_streak_5", "perfect_role_mafia_10",
    "win_streak_3", "win_streak_10", "win_streak_15", "win_streak_20",
    "comeback_after_5_losses", "win_rate_70_last_20",
    "sheriff_wins_50", "sheriff_wins_100", "don_wins_50",
    "civilian_wins_50", "civilian_wins_100",
    "best_move_5", "best_move_25", "best_move_100", "pu_perfect_call",
}
_TOURNAMENTS_CATEGORY_CODES = {
    "tournament_win_1", "tournament_participant_10",
    "tournament_participant_5", "tournament_participant_25", "tournament_participant_50",
    "tournament_win_2", "tournament_win_3", "tournament_win_5",
    "tournament_top3_1", "tournament_top3_5", "tournament_flawless",
    "tournament_advanced_final", "tournament_advanced_final_5", "team_tournament_win",
}

RULES: List[AchievementRule] = [
    # ── Games ────────────────────────────────────────────────────
    AchievementRule("games_played_10",  AchievementTrigger.GAME, _r_games_played(10)),
    AchievementRule("games_played_100", AchievementTrigger.GAME, _r_games_played(100)),
    AchievementRule("games_played_500", AchievementTrigger.GAME, _r_games_played(500)),
    AchievementRule("games_played_25",   AchievementTrigger.GAME, _r_games_played(25)),
    AchievementRule("games_played_50",   AchievementTrigger.GAME, _r_games_played(50)),
    AchievementRule("games_played_250",  AchievementTrigger.GAME, _r_games_played(250)),
    AchievementRule("games_played_1000", AchievementTrigger.GAME, _r_games_played(1000)),
    AchievementRule("civilian_games_100", AchievementTrigger.GAME, _r_role_games_played(100, (Role.CIVILIAN,))),
    AchievementRule("sheriff_games_50",   AchievementTrigger.GAME, _r_role_games_played(50, (Role.SHERIFF,))),
    AchievementRule("don_games_50",       AchievementTrigger.GAME, _r_role_games_played(50, (Role.DON,))),
    AchievementRule("mafia_games_100",    AchievementTrigger.GAME, _r_role_games_played(100, (Role.MAFIA,))),
    AchievementRule("games_10_in_one_day", AchievementTrigger.GAME, _r_games_in_single_day(10)),
    AchievementRule("tenure_1_year",  AchievementTrigger.GAME, _r_tenure_years(1)),
    AchievementRule("tenure_3_years", AchievementTrigger.GAME, _r_tenure_years(3)),

    # ── Wins ─────────────────────────────────────────────────────
    AchievementRule("wins_10",              AchievementTrigger.GAME, _r_wins(10)),
    AchievementRule("wins_streak_5",        AchievementTrigger.GAME, _r_win_streak(5)),
    AchievementRule("perfect_role_mafia_10", AchievementTrigger.GAME, _r_role_wins(10, (Role.MAFIA, Role.DON))),
    AchievementRule("win_streak_3",  AchievementTrigger.GAME, _r_win_streak(3)),
    AchievementRule("win_streak_10", AchievementTrigger.GAME, _r_win_streak(10)),
    AchievementRule("win_streak_15", AchievementTrigger.GAME, _r_win_streak(15)),
    AchievementRule("win_streak_20", AchievementTrigger.GAME, _r_win_streak(20)),
    AchievementRule("comeback_after_5_losses", AchievementTrigger.GAME, _r_comeback(5)),
    AchievementRule("win_rate_70_last_20",     AchievementTrigger.GAME, _r_win_rate_recent(20, 70.0)),
    AchievementRule("sheriff_wins_50",  AchievementTrigger.GAME, _r_role_wins(50, (Role.SHERIFF,))),
    AchievementRule("sheriff_wins_100", AchievementTrigger.GAME, _r_role_wins(100, (Role.SHERIFF,))),
    AchievementRule("don_wins_50",      AchievementTrigger.GAME, _r_role_wins(50, (Role.DON,))),
    AchievementRule("civilian_wins_50",  AchievementTrigger.GAME, _r_role_wins(50, (Role.CIVILIAN,))),
    AchievementRule("civilian_wins_100", AchievementTrigger.GAME, _r_role_wins(100, (Role.CIVILIAN,))),
    AchievementRule("best_move_5",   AchievementTrigger.GAME, _r_best_move_count(5)),
    AchievementRule("best_move_25",  AchievementTrigger.GAME, _r_best_move_count(25)),
    AchievementRule("best_move_100", AchievementTrigger.GAME, _r_best_move_count(100)),
    AchievementRule("pu_perfect_call", AchievementTrigger.GAME, _r_pu_perfect_call),

    # ── Rating ───────────────────────────────────────────────────
    AchievementRule("elo_1500",   AchievementTrigger.GAME, _r_elo_at_least(1500)),
    AchievementRule("elo_1800",   AchievementTrigger.GAME, _r_elo_at_least(1800)),
    AchievementRule("top1_global", AchievementTrigger.GAME, _r_global_rank_1),
    AchievementRule("elo_1200", AchievementTrigger.GAME, _r_elo_at_least(1200)),
    AchievementRule("elo_1300", AchievementTrigger.GAME, _r_elo_at_least(1300)),
    AchievementRule("elo_1600", AchievementTrigger.GAME, _r_elo_at_least(1600)),
    AchievementRule("elo_1700", AchievementTrigger.GAME, _r_elo_at_least(1700)),
    AchievementRule("elo_1900", AchievementTrigger.GAME, _r_elo_at_least(1900)),
    AchievementRule("elo_2000", AchievementTrigger.GAME, _r_elo_at_least(2000)),
    AchievementRule("elo_2200", AchievementTrigger.GAME, _r_elo_at_least(2200)),
    AchievementRule("rank_top3_global",  AchievementTrigger.GAME, _r_global_rank_at_most(3)),
    AchievementRule("rank_top5_global",  AchievementTrigger.GAME, _r_global_rank_at_most(5)),
    AchievementRule("rank_top10_global", AchievementTrigger.GAME, _r_global_rank_at_most(10)),

    # ── Tournaments ──────────────────────────────────────────────
    AchievementRule("tournament_win_1",         AchievementTrigger.TOURNAMENT, _r_tournament_rank_1),
    AchievementRule("tournament_participant_10", AchievementTrigger.TOURNAMENT, _r_tournament_participations(10)),
    AchievementRule("tournament_participant_5",  AchievementTrigger.TOURNAMENT, _r_tournament_participations(5)),
    AchievementRule("tournament_participant_25", AchievementTrigger.TOURNAMENT, _r_tournament_participations(25)),
    AchievementRule("tournament_participant_50", AchievementTrigger.TOURNAMENT, _r_tournament_participations(50)),
    AchievementRule("tournament_win_2", AchievementTrigger.TOURNAMENT, _r_tournament_wins_count(2)),
    AchievementRule("tournament_win_3", AchievementTrigger.TOURNAMENT, _r_tournament_wins_count(3)),
    AchievementRule("tournament_win_5", AchievementTrigger.TOURNAMENT, _r_tournament_wins_count(5)),
    AchievementRule("tournament_top3_1", AchievementTrigger.TOURNAMENT, _r_tournament_top3_count(1)),
    AchievementRule("tournament_top3_5", AchievementTrigger.TOURNAMENT, _r_tournament_top3_count(5)),
    AchievementRule("tournament_flawless", AchievementTrigger.TOURNAMENT, _r_tournament_flawless),
    AchievementRule("tournament_advanced_final",   AchievementTrigger.TOURNAMENT, _r_tournament_advanced_final_count(1)),
    AchievementRule("tournament_advanced_final_5", AchievementTrigger.TOURNAMENT, _r_tournament_advanced_final_count(5)),
    AchievementRule("team_tournament_win", AchievementTrigger.TOURNAMENT, _r_team_tournament_win),

    # ── Seasons ──────────────────────────────────────────────────
    AchievementRule("season_win_1",   AchievementTrigger.SEASON, _r_season_winner),
    AchievementRule("season_top3_3",  AchievementTrigger.SEASON, _r_season_top3_count(3)),
    AchievementRule("season_participant_5",  AchievementTrigger.SEASON, _r_season_participations(5)),
    AchievementRule("season_participant_10", AchievementTrigger.SEASON, _r_season_participations(10)),
    AchievementRule("season_top3_1", AchievementTrigger.SEASON, _r_season_top3_count(1)),
    AchievementRule("season_top3_5", AchievementTrigger.SEASON, _r_season_top3_count(5)),
    AchievementRule("season_win_2", AchievementTrigger.SEASON, _r_season_wins_count(2)),
    AchievementRule("season_win_3", AchievementTrigger.SEASON, _r_season_wins_count(3)),
    AchievementRule("season_win_5", AchievementTrigger.SEASON, _r_season_wins_count(5)),
    AchievementRule("season_win_consecutive_2", AchievementTrigger.SEASON, _r_season_win_consecutive(2)),
    AchievementRule("seasonal_title_sheriff",  AchievementTrigger.SEASON, _r_seasonal_title_held("season_best_sheriff")),
    AchievementRule("seasonal_title_don",      AchievementTrigger.SEASON, _r_seasonal_title_held("season_best_don")),
    AchievementRule("seasonal_title_mafia",    AchievementTrigger.SEASON, _r_seasonal_title_held("season_best_mafia")),
    AchievementRule("seasonal_title_civilian", AchievementTrigger.SEASON, _r_seasonal_title_held("season_best_civilian")),
    AchievementRule("seasonal_titles_all_roles", AchievementTrigger.SEASON, _r_all_seasonal_role_titles),
    AchievementRule("season_reward_received", AchievementTrigger.SEASON, _r_season_reward_received),

    # ── Fantasy (scored alongside tournament finish) ────────────
    AchievementRule("fantasy_leaderboard_1", AchievementTrigger.TOURNAMENT, _r_fantasy_leaderboard_1),
    AchievementRule("fantasy_participant_5", AchievementTrigger.TOURNAMENT, _r_fantasy_draft_count(5)),
    AchievementRule("fantasy_participant_10", AchievementTrigger.TOURNAMENT, _r_fantasy_draft_count(10)),
    AchievementRule("fantasy_participant_25", AchievementTrigger.TOURNAMENT, _r_fantasy_draft_count(25)),
    AchievementRule("fantasy_leaderboard_top3_1", AchievementTrigger.TOURNAMENT, _r_fantasy_leaderboard_top3_count(1)),
    AchievementRule("fantasy_leaderboard_top3_5", AchievementTrigger.TOURNAMENT, _r_fantasy_leaderboard_top3_count(5)),
    AchievementRule("fantasy_leaderboard_win_3",  AchievementTrigger.TOURNAMENT, _r_fantasy_leaderboard_win_count(3)),
    AchievementRule("fantasy_drafted_champion",   AchievementTrigger.TOURNAMENT, _r_fantasy_drafted_champion),
    AchievementRule("fantasy_points_500",  AchievementTrigger.TOURNAMENT, _r_fantasy_points_total(500)),
    AchievementRule("fantasy_points_2000", AchievementTrigger.TOURNAMENT, _r_fantasy_points_total(2000)),

    # ── Economy ──────────────────────────────────────────────────
    AchievementRule("coins_earned_1000",  AchievementTrigger.GAME, _r_coins_earned(1000)),
    AchievementRule("coins_earned_10000", AchievementTrigger.GAME, _r_coins_earned(10000)),
    AchievementRule("coins_earned_500",   AchievementTrigger.GAME, _r_coins_earned(500)),
    AchievementRule("coins_earned_25000", AchievementTrigger.GAME, _r_coins_earned(25000)),
    AchievementRule("coins_earned_50000", AchievementTrigger.GAME, _r_coins_earned(50000)),
    AchievementRule("coins_earned_100000", AchievementTrigger.GAME, _r_coins_earned(100000)),
    AchievementRule("balance_10000", AchievementTrigger.GAME, _r_balance_at_least(10000)),
    AchievementRule("coins_spent_5000",  AchievementTrigger.PURCHASE, _r_coins_spent(5000)),
    AchievementRule("coins_spent_20000", AchievementTrigger.PURCHASE, _r_coins_spent(20000)),
    AchievementRule("owns_physical_merch", AchievementTrigger.PURCHASE, _r_owns_physical_merch),

    # ── Social / shop / profile ──────────────────────────────────
    AchievementRule("shop_first_purchase", AchievementTrigger.PURCHASE, _r_first_purchase),
    # "account_linked" is unlocked directly (unconditionally, one-shot) from
    # the account-linking action — no rule needed, see AchievementService.
    AchievementRule("inventory_5_items",  AchievementTrigger.PURCHASE, _r_inventory_count(5)),
    AchievementRule("inventory_10_items", AchievementTrigger.PURCHASE, _r_inventory_count(10)),
    AchievementRule("inventory_20_items", AchievementTrigger.PURCHASE, _r_inventory_count(20)),
    AchievementRule("owns_all_rarities",  AchievementTrigger.PURCHASE, _r_owns_all_rarities),
    AchievementRule("full_outfit_equipped", AchievementTrigger.PURCHASE, _r_full_outfit_equipped),
    AchievementRule("gift_sent_1",  AchievementTrigger.PURCHASE, _r_gift_sent_count(1)),
    AchievementRule("gift_sent_10", AchievementTrigger.PURCHASE, _r_gift_sent_count(10)),
    AchievementRule("gift_received_10", AchievementTrigger.PURCHASE, _r_gift_received_count(10)),
    AchievementRule("owns_unique_item",  AchievementTrigger.PURCHASE, _r_owns_unique_item),
    AchievementRule("profile_complete",  AchievementTrigger.GAME, _r_profile_complete),
    AchievementRule("shop_all_categories", AchievementTrigger.PURCHASE, _r_shop_all_categories),
    # "pinned_first_achievement" is unlocked directly from AchievementService.pin()
    # — a one-shot user action, no polling rule needed.

    # "founder" (SPECIAL) is admin-granted only via AchievementService.admin_grant
    # — intentionally no rule entry.

    # ── Special / meta ───────────────────────────────────────────
    AchievementRule("achievements_unlocked_10", AchievementTrigger.GAME, _r_unlocked_count(10)),
    AchievementRule("achievements_unlocked_25", AchievementTrigger.GAME, _r_unlocked_count(25)),
    AchievementRule("achievements_unlocked_40", AchievementTrigger.GAME, _r_unlocked_count(40)),
    AchievementRule("achievements_unlocked_60", AchievementTrigger.GAME, _r_unlocked_count(60)),
    AchievementRule("category_complete_games",       AchievementTrigger.GAME, _r_category_complete(_GAMES_CATEGORY_CODES)),
    AchievementRule("category_complete_wins",        AchievementTrigger.GAME, _r_category_complete(_WINS_CATEGORY_CODES)),
    AchievementRule("category_complete_tournaments", AchievementTrigger.TOURNAMENT, _r_category_complete(_TOURNAMENTS_CATEGORY_CODES)),
    AchievementRule("veteran_2y_500g", AchievementTrigger.GAME, _r_veteran_combo(2, 500)),
    AchievementRule("legend_combo",    AchievementTrigger.GAME, _r_legend_combo),
]


def get_rules_for_trigger(trigger: AchievementTrigger) -> List[AchievementRule]:
    return [r for r in RULES if r.trigger == trigger]
