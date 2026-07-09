from flask import Blueprint, render_template, jsonify
from app import db
from app.models import Player
from app.services import RatingService, TitleService
from app.services.shop_service import ShopService

ratings_bp = Blueprint("ratings", __name__)


@ratings_bp.route("/")
def leaderboard():
    ratings = RatingService.compute_all_ratings()
    # Один bulk-запрос на весь лидерборд — без N+1 на каждую строку.
    player_ids = [r.player_id for r in ratings]
    equipped_titles = TitleService.get_equipped_titles_bulk(player_ids)
    equipped_bulk = ShopService.get_equipped_bulk(player_ids)
    avatars = dict(
        db.session.query(Player.id, Player.avatar_url)
        .filter(Player.id.in_(player_ids))
        .all()
    ) if player_ids else {}
    # Средний винрейт по всем игрокам таблицы — для hero-блока, чисто
    # агрегация уже полученного списка, без новых запросов к БД.
    avg_win_rate = round(sum(r.win_rate for r in ratings) / len(ratings), 1) if ratings else 0.0
    return render_template(
        "ratings/leaderboard.html", ratings=ratings,
        equipped_titles=equipped_titles, equipped_bulk=equipped_bulk,
        avatars=avatars, avg_win_rate=avg_win_rate,
    )


@ratings_bp.route("/api")
def api_ratings():
    ratings = RatingService.compute_all_ratings()
    return jsonify([r.to_dict() for r in ratings])
