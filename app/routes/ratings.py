from flask import Blueprint, render_template, jsonify
from app.services import RatingService, TitleService

ratings_bp = Blueprint("ratings", __name__)


@ratings_bp.route("/")
def leaderboard():
    ratings = RatingService.compute_all_ratings()
    # Один bulk-запрос на весь лидерборд — без N+1 на каждую строку.
    equipped_titles = TitleService.get_equipped_titles_bulk([r.player_id for r in ratings])
    return render_template("ratings/leaderboard.html", ratings=ratings, equipped_titles=equipped_titles)


@ratings_bp.route("/api")
def api_ratings():
    ratings = RatingService.compute_all_ratings()
    return jsonify([r.to_dict() for r in ratings])
