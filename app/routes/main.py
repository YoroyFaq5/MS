from datetime import datetime, timedelta

from flask import Blueprint, render_template
from app.services import RatingService, TitleService, NominationService
from app.services.nomination_service import SEASONAL_ROLE_TITLES
from app.services.season_service import SeasonService
from app.services.shop_service import ShopService
from app.models import Game, GameSlot, Player, Title, Tournament, PlayerTitle, PlayerAchievement, Achievement
from app import db

main_bp = Blueprint("main", __name__)


def _naive(dt):
    """Normalize tz-aware/naive DateTime(timezone=True) values before
    sorting them together — see profile.py::_naive_utc for the same
    MySQL-round-trips-as-naive rationale."""
    return dt.replace(tzinfo=None) if dt and dt.tzinfo else dt


@main_bp.route("/")
def index():
    top_players = RatingService.compute_all_ratings()[:5]
    top_rich = (
        db.session.query(Player)
        .filter(Player.is_active == True)
        .order_by(Player.coins.desc())
        .limit(5)
        .all()
    )
    recent_games = (
        db.session.query(Game)
        .filter(Game.is_finished == True)
        .order_by(Game.played_at.desc())
        .limit(5)
        .all()
    )
    total_games = db.session.query(Game).filter(Game.is_finished == True).count()
    club_titles = TitleService.get_current_global_holders()

    # Номинации сезона — то же превью, что и на /titles/nominations (см.
    # titles.py::nominations), только компактно на главной: живой лидер по
    # формуле каждой роли, пока сезон ещё не закрыт.
    current_season = SeasonService.get_current_season()
    current_leaders = []
    if current_season:
        preview = NominationService.get_role_leaders_preview(current_season.id)
        role_titles = {
            t.code: t for t in db.session.query(Title).filter(
                Title.code.in_(SEASONAL_ROLE_TITLES.values())
            ).all()
        }
        leader_ids = [pid for pid in preview.values() if pid]
        leader_players = {
            p.id: p for p in db.session.query(Player).filter(Player.id.in_(leader_ids)).all()
        } if leader_ids else {}
        for role, title_code in SEASONAL_ROLE_TITLES.items():
            title = role_titles.get(title_code)
            player_id = preview.get(title_code)
            if title and player_id:
                current_leaders.append({"title": title, "player": leader_players.get(player_id)})

    # ── Статистика клуба (масштаб за всё время) ──────────────────────────────
    total_players = db.session.query(Player).filter(Player.is_active == True).count()
    total_tournaments = db.session.query(Tournament).count()
    total_titles_awarded = db.session.query(PlayerTitle).filter(PlayerTitle.revoked == False).count()

    # ── Живые метрики "сегодня/на этой неделе" для hero ──────────────────────
    # Naive datetime-границы — тот же приём, что и у месячного фильтра в
    # games.py::list_games (DateTime(timezone=True) на MySQL всё равно
    # округляется до naive при чтении, сравнивать нужно однородно).
    now = datetime.now()
    today_start = datetime(now.year, now.month, now.day)
    week_start = today_start - timedelta(days=7)

    games_today = (
        db.session.query(Game)
        .filter(Game.is_finished == True, Game.played_at >= today_start)
        .count()
    )
    active_this_week = (
        db.session.query(GameSlot.player_id)
        .join(Game)
        .filter(Game.is_finished == True, Game.played_at >= week_start)
        .distinct()
        .count()
    )
    active_tournaments_count = db.session.query(Tournament).filter(Tournament.status == "active").count()

    # ── Лента активности клуба: последние достижения + выданные титулы,
    # объединённые в одну хронологическую ленту (никаких вымышленных
    # событий вроде "MVP недели" — только то, что реально есть в БД). ──────
    recent_unlocks = (
        db.session.query(PlayerAchievement)
        .join(Achievement)
        .order_by(PlayerAchievement.unlocked_at.desc())
        .limit(6)
        .all()
    )
    recent_grants = (
        db.session.query(PlayerTitle)
        .join(Title)
        .filter(PlayerTitle.revoked == False)
        .order_by(PlayerTitle.awarded_at.desc())
        .limit(6)
        .all()
    )
    activity_feed = [
        {"kind": "achievement", "player_id": pa.player_id, "player": pa.player,
         "icon": pa.achievement.icon or "bi-trophy", "name": pa.achievement.name,
         "rarity": pa.achievement.rarity.value, "at": pa.unlocked_at}
        for pa in recent_unlocks if pa.player
    ] + [
        {"kind": "title", "player_id": pt.player_id, "player": pt.player,
         "icon": pt.title.icon or "bi-award", "name": pt.title.name,
         "rarity": pt.title.rarity.value, "at": pt.awarded_at}
        for pt in recent_grants if pt.player
    ]
    activity_feed.sort(key=lambda e: _naive(e["at"]), reverse=True)
    activity_feed = activity_feed[:8]

    player_ids = {r.player_id for r in top_players} | {p.id for p in top_rich}
    player_ids.update(pt.player_id for pt in club_titles)
    player_ids.update(e["player"].id for e in current_leaders if e["player"])
    player_ids.update(e["player_id"] for e in activity_feed)
    equipped_bulk = ShopService.get_equipped_bulk(list(player_ids))

    return render_template(
        "index.html",
        top_players=top_players,
        top_rich=top_rich,
        recent_games=recent_games,
        total_games=total_games,
        club_titles=club_titles,
        current_season=current_season,
        current_leaders=current_leaders,
        total_players=total_players,
        total_tournaments=total_tournaments,
        total_titles_awarded=total_titles_awarded,
        games_today=games_today,
        active_this_week=active_this_week,
        active_tournaments_count=active_tournaments_count,
        activity_feed=activity_feed,
        TitleService=TitleService,
        equipped_bulk=equipped_bulk,
    )
