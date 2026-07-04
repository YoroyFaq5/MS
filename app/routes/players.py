from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, abort
from app import db
from app.models import Player
from app.services import RatingService
from app.services.economy_service import EconomyService
from app.services.shop_service import ShopService
from app.auth_decorators import admin_required

players_bp = Blueprint("players", __name__)


@players_bp.route("/")
def list_players():
    players = db.session.query(Player).order_by(Player.name).all()
    equipped_bulk = ShopService.get_equipped_bulk([p.id for p in players])
    return render_template("players/list.html", players=players, equipped_bulk=equipped_bulk)


@players_bp.route("/add", methods=["GET", "POST"])
@admin_required
def add_player():
    if request.method == "POST":
        nickname = request.form.get("nickname", "").strip()
        name = request.form.get("name", "").strip() or None

        if not nickname:
            flash("Никнейм обязателен.", "danger")
            return redirect(url_for("players.add_player"))

        exists = db.session.query(Player).filter_by(nickname=nickname).first()
        if exists:
            flash(f"Никнейм «{nickname}» уже занят.", "danger")
            return redirect(url_for("players.add_player"))

        player = Player(nickname=nickname, name=name)
        db.session.add(player)
        db.session.commit()
        EconomyService.grant_welcome_bonus(player)
        flash(f"Игрок «{player.nickname}» добавлен.", "success")
        return redirect(url_for("players.list_players"))

    return render_template("players/form.html", player=None)


@players_bp.route("/<int:player_id>/edit", methods=["GET", "POST"])
@admin_required
def edit_player(player_id: int):
    player = db.session.get(Player, player_id) or abort(404)

    if request.method == "POST":
        nickname = request.form.get("nickname", "").strip()
        name = request.form.get("name", "").strip() or None

        if not nickname:
            flash("Никнейм обязателен.", "danger")
            return redirect(url_for("players.edit_player", player_id=player_id))

        conflict = (
            db.session.query(Player)
            .filter(Player.nickname == nickname, Player.id != player_id)
            .first()
        )
        if conflict:
            flash(f"Никнейм «{nickname}» уже занят.", "danger")
            return redirect(url_for("players.edit_player", player_id=player_id))

        player.nickname = nickname
        player.name = name
        db.session.commit()
        flash("Данные игрока обновлены.", "success")
        return redirect(url_for("players.list_players"))

    return render_template("players/form.html", player=player)


@players_bp.route("/<int:player_id>/delete", methods=["POST"])
@admin_required
def delete_player(player_id: int):
    player = db.session.get(Player, player_id) or abort(404)
    player.is_active = False  # soft delete
    db.session.commit()
    flash(f"Игрок «{player.display_name}» деактивирован.", "info")
    return redirect(url_for("players.list_players"))


@players_bp.route("/<int:player_id>/stats")
def player_stats(player_id: int):
    # Retired — superseded by the new /profile page. Kept as a redirect
    # shim so old links/bookmarks keep working.
    db.session.get(Player, player_id) or abort(404)
    return redirect(url_for("profile.view_profile", player_id=player_id))


# JSON API endpoint (for future SPA / mobile use)
@players_bp.route("/api")
def api_players():
    players = db.session.query(Player).filter_by(is_active=True).order_by(Player.name).all()
    return jsonify([p.to_dict() for p in players])
