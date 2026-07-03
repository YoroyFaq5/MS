from flask import Blueprint, render_template
from app.services import RatingService, TitleService
from app.models import Game, Player
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
    return render_template(
        "index.html",
        top_players=top_players,
        top_rich=top_rich,
        recent_games=recent_games,
        total_games=total_games,
        club_titles=club_titles,
    )