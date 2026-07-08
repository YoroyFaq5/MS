from datetime import datetime, timedelta

from flask import Blueprint, render_template
from app.services import RatingService, TitleService, NominationService
from app.services.nomination_service import SEASONAL_ROLE_TITLES
from app.services.season_service import SeasonService
from app.services.shop_service import ShopService
from app.models import Game, GameSlot, Player, Title, Tournament, PlayerTitle, PlayerAchievement, Achievement, WinSide
from app import db

main_bp = Blueprint("main", __name__)


def _naive(dt):
    """Normalize tz-aware/naive DateTime(timezone=True) values before
    sorting them together — see profile.py::_naive_utc for the same
    MySQL-round-trips-as-naive rationale."""
    return dt.replace(tzinfo=None) if dt and dt.tzinfo else dt


def _sparkline_points(results: list, width: int = 56, height: int = 18, pad: float = 3) -> str:
    """
    SVG <polyline points="..."> for a tiny binary win/loss form sparkline —
    built server-side (plain string math, no JS charting library) so the
    template just drops it straight into an inline <svg>.
    """
    n = len(results)
    if n == 0:
        return ""
    x_step = (width - 2 * pad) / (n - 1) if n > 1 else 0
    return " ".join(
        f"{pad + i * x_step:.1f},{(pad if won else height - pad):.1f}"
        for i, won in enumerate(results)
    )


@main_bp.route("/")
def index():
    top_players = RatingService.compute_all_ratings()[:8]

    # ── Движение в рейтинге за 30 дней ────────────────────────────────────
    # Пересчитываем рейтинг ещё раз, но только по играм ДО (now - 30 дней) —
    # без отдельной таблицы исторических снапшотов: тот же compute_all_ratings,
    # просто с cutoff-датой (см. RatingService.compute_all_ratings(as_of=...)).
    ratings_30d_ago = RatingService.compute_all_ratings(as_of=datetime.now() - timedelta(days=30))
    rank_30d_ago = {r.player_id: r.rank for r in ratings_30d_ago}
    for r in top_players:
        old_rank = rank_30d_ago.get(r.player_id)
        # movement > 0 — поднялся, < 0 — опустился, None — 30 дней назад
        # ранга не было вовсе (новый в рейтинге), 0 — без изменений.
        r.rank_movement = (old_rank - r.rank) if old_rank is not None else None

    # ── Форма: последние результаты + текущая серия (одним батч-запросом
    # на всех показанных топ-игроков, не по одному) ───────────────────────
    recent_form = RatingService.get_recent_form([r.player_id for r in top_players], limit=8)
    sparklines = {pid: _sparkline_points(form.results) for pid, form in recent_form.items()}

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
        .limit(6)
        .all()
    )
    # "Ключевое событие" игры — единственный уже сохранённый показатель,
    # который реально можно назвать примечательным моментом партии: ПУ
    # (первый убитый), вычисливший 2+ мафии в лучшем ходе. Ничего не
    # выдумываем (вроде длительности игры — она в базе не хранится).
    for g in recent_games:
        pu_slot = next((s for s in g.slots if s.is_pu and s.pu_mafia_count >= 2), None)
        g.key_event = (
            {"player": pu_slot.player, "count": pu_slot.pu_mafia_count}
            if pu_slot else None
        )

    total_games = db.session.query(Game).filter(Game.is_finished == True).count()
    club_titles = TitleService.get_current_global_holders()

    # ── Город vs Мафия — доля побед за последние 50 завершённых игр ──────
    recent_sides = (
        db.session.query(Game.win_side)
        .filter(Game.is_finished == True)
        .order_by(Game.played_at.desc())
        .limit(50)
        .all()
    )
    city_wins = sum(1 for (ws,) in recent_sides if ws == WinSide.CITY)
    mafia_wins = sum(1 for (ws,) in recent_sides if ws == WinSide.MAFIA)
    side_total = city_wins + mafia_wins
    city_win_pct = round(city_wins / side_total * 100) if side_total else 50

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
    player_ids.update(g.key_event["player"].id for g in recent_games if g.key_event)
    equipped_bulk = ShopService.get_equipped_bulk(list(player_ids))

    return render_template(
        "index.html",
        top_players=top_players,
        recent_form=recent_form,
        sparklines=sparklines,
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
        city_win_pct=city_win_pct,
        mafia_win_pct=100 - city_win_pct,
        TitleService=TitleService,
        equipped_bulk=equipped_bulk,
    )
