from flask import Blueprint, render_template
from app.services import RatingService, TitleService, NominationService
from app.services.nomination_service import SEASONAL_ROLE_TITLES
from app.services.season_service import SeasonService
from app.services.shop_service import ShopService
from app.models import Game, Player, Title
from app import db

main_bp = Blueprint("main", __name__)


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

    player_ids = {r.player_id for r in top_players} | {p.id for p in top_rich}
    player_ids.update(pt.player_id for pt in club_titles)
    player_ids.update(e["player"].id for e in current_leaders if e["player"])
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
        TitleService=TitleService,
        equipped_bulk=equipped_bulk,
    )