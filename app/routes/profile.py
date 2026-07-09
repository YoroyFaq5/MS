from datetime import datetime, timezone, timedelta

from flask import Blueprint, render_template, redirect, url_for, flash, abort, request, current_app, jsonify
from flask_login import current_user

from app import db
from app.models import Player, Title
from app.services import ProfileService, AchievementService, PermissionService, TitleService, ChartDataService, AvatarService
from app.services.shop_service import ShopService
from app.services.nomination_service import NominationService
from app.services.season_service import SeasonService
from app.auth_decorators import login_required

profile_bp = Blueprint("profile", __name__)


def _naive_utc(dt):
    """
    DateTime(timezone=True) columns round-trip as tz-naive once read back
    from MySQL (no real TZ storage there) but stay tz-aware for an
    in-memory object that hasn't been re-queried yet — comparing the two
    forms directly raises. Strip tzinfo from both sides before any diff;
    the app's convention of always writing datetime.now(timezone.utc)
    means a naive value already represents UTC wall-clock time, so this
    doesn't change what it means, just makes it comparable.
    """
    return dt.replace(tzinfo=None) if dt and dt.tzinfo else dt


@profile_bp.route("/")
@login_required
def own_profile():
    if not current_user.player_id:
        flash("Привяжите аккаунт к игроку, чтобы открыть профиль.", "warning")
        return redirect(url_for("auth.link_player_page"))
    return redirect(url_for("profile.view_profile", player_id=current_user.player_id))


@profile_bp.route("/avatar", methods=["POST"])
@login_required
def upload_avatar():
    if not current_user.player_id:
        return jsonify(ok=False, message="Профиль не привязан к игроку."), 403
    player = db.session.get(Player, current_user.player_id)
    result = AvatarService.save_avatar(player, request.files.get("avatar"))
    return jsonify(ok=result.ok, message=result.message, avatar_url=result.data if result.ok else None), (200 if result.ok else 400)


@profile_bp.route("/avatar/remove", methods=["POST"])
@login_required
def remove_avatar():
    if not current_user.player_id:
        return jsonify(ok=False, message="Профиль не привязан к игроку."), 403
    player = db.session.get(Player, current_user.player_id)
    result = AvatarService.remove_avatar(player)
    return jsonify(ok=result.ok, message=result.message), (200 if result.ok else 400)


@profile_bp.route("/<int:player_id>")
def view_profile(player_id: int):
    profile = ProfileService.get_profile(player_id)
    if not profile:
        abort(404)
    is_own = current_user.is_authenticated and current_user.player_id == player_id
    # Титулы — витрина достижений, видна всем посетителям профиля (не
    # только владельцу); управление экипировкой (кнопки "Надеть"/"Снять")
    # остаётся доступно только владельцу — это ограничено в шаблоне через
    # is_own, а не на уровне выборки данных.
    # Сортировка (самое значимое — сверху): экипированный первым, дальше
    # по редкости, дальше по свежести. Jinja's |sort умеет сортировать
    # только по значению атрибута (алфавитно — "legendary" < "rare" по
    # буквам, что не совпадает со значимостью), поэтому порядок считаем
    # здесь через TitleService.RARITY_RANK, а не в шаблоне.
    held_titles = [pt for pt in TitleService.list_player_titles(player_id) if not pt.revoked]
    held_titles.sort(key=lambda pt: (
        not pt.equipped,
        -TitleService.RARITY_RANK.get(pt.title.rarity.value, 0),
        -_naive_utc(pt.awarded_at).timestamp(),
    ))

    # "Новый!" — одноразовая CSS-анимация для титулов, выданных недавно
    # (см. .title-card--new в main.css). Флаг вычисляется здесь, а не в
    # шаблоне — Jinja не умеет сравнивать tz-aware/tz-naive datetime без
    # падения (см. _naive_utc выше).
    now_naive = _naive_utc(datetime.now(timezone.utc))
    for pt in held_titles:
        awarded = _naive_utc(pt.awarded_at)
        pt.is_new = bool(awarded and timedelta(0) <= (now_naive - awarded) < timedelta(days=2))

    # Живая номинация сезона: если у игрока сейчас лучшая формула по роли
    # в активном сезоне — показываем это отдельным "живым" блоком, даже
    # если титул ещё не выдан (выдаётся только при закрытии сезона).
    # Дёшево — переиспользует уже существующий NominationService-превью
    # (те же 4 запроса, что и на странице /titles/nominations).
    leading_titles = []
    current_season = SeasonService.get_current_season()
    if current_season:
        preview = NominationService.get_role_leaders_preview(current_season.id)
        leading_codes = [code for code, pid in preview.items() if pid == player_id]
        if leading_codes:
            leading_titles = (
                db.session.query(Title).filter(Title.code.in_(leading_codes)).all()
            )

    # Статус привязки Telegram — только владельцу, отдельно от to_dict()
    # (telegram_id намеренно не публикуется в общем JSON/профиле).
    telegram_linked = False
    if is_own:
        player = db.session.get(Player, player_id)
        telegram_linked = bool(player and player.telegram_id)

    total_titles_count = db.session.query(Title).filter_by(is_active=True).count()

    return render_template(
        "profile/main.html", profile=profile, player_id=player_id,
        is_own=is_own, held_titles=held_titles,
        leading_titles=leading_titles, current_season=current_season,
        total_titles_count=total_titles_count,
        TitleService=TitleService,
        telegram_linked=telegram_linked,
        telegram_bot_username=current_app.config.get("TELEGRAM_BOT_USERNAME"),
    )


@profile_bp.route("/<int:player_id>/statistics")
def statistics(player_id: int):
    player = db.session.get(Player, player_id) or abort(404)
    stats = ProfileService.get_statistics(player_id)
    role_stats = ProfileService.get_role_statistics(player_id)
    partner_stats = ProfileService.get_partner_statistics(player_id)
    rivalry_stats = ProfileService.get_rivalry_statistics(player_id)
    tournament_summary = ProfileService.get_tournament_summary(player_id)
    fantasy_summary = ProfileService.get_fantasy_summary(player_id)
    comparison_stats = ProfileService.get_comparison_stats(player_id)

    # Датасеты для Chart.js — считаются только на этой (тяжёлой) подстранице.
    chart_data = {
        "elo": ChartDataService.get_elo_history(player_id),
        "roles": ChartDataService.get_role_timeline(player_id),
        "streaks": ChartDataService.get_streak_timeline(player_id),
        "role_performance": ChartDataService.get_role_performance(player_id),
        "economy": ChartDataService.get_economy_timeline(player_id),
    }

    # Персонализация — сам игрок страницы + все упомянутые в статистике
    # партнёры/соперники (partner_stats/rivalry_stats — dict-записи с
    # player_id, см. ProfileService.get_partner_statistics).
    other_ids = {
        e["player_id"] for e in list(partner_stats.values()) + list(rivalry_stats.values())
        if isinstance(e, dict) and "player_id" in e
    }
    equipped_bulk = ShopService.get_equipped_bulk(list(other_ids) + [player_id])

    return render_template(
        "profile/statistics.html",
        player=player,
        player_id=player_id,
        stats=stats,
        role_stats=role_stats,
        partner_stats=partner_stats,
        rivalry_stats=rivalry_stats,
        tournament_summary=tournament_summary,
        fantasy_summary=fantasy_summary,
        comparison_stats=comparison_stats,
        chart_data=chart_data,
        equipped_bulk=equipped_bulk,
    )


@profile_bp.route("/compare")
def compare():
    a_id = request.args.get("a", type=int)
    b_id = request.args.get("b", type=int)

    comparison = None
    if a_id and b_id:
        if a_id == b_id:
            flash("Выберите двух разных игроков для сравнения.", "warning")
        else:
            comparison = ProfileService.compare_players(a_id, b_id)
            if not comparison:
                abort(404)

    players = (
        db.session.query(Player)
        .filter_by(is_active=True)
        .order_by(Player.name)
        .all()
    )
    equipped_bulk = ShopService.get_equipped_bulk([a_id, b_id]) if comparison else {}

    return render_template(
        "profile/compare.html",
        players=players,
        a_id=a_id,
        b_id=b_id,
        comparison=comparison,
        equipped_bulk=equipped_bulk,
    )


@profile_bp.route("/<int:player_id>/achievements")
def achievements(player_id: int):
    player = db.session.get(Player, player_id) or abort(404)
    items = ProfileService.get_achievements(player_id)
    unlocked_count = sum(1 for i in items if i["unlocked"])
    total_count = len(items)
    completion_pct = round(unlocked_count / total_count * 100, 1) if total_count else 0.0
    is_own = current_user.is_authenticated and current_user.player_id == player_id
    equipped = ShopService.get_equipped(player_id)
    return render_template(
        "profile/achievements.html",
        player=player,
        player_id=player_id,
        items=items,
        unlocked_count=unlocked_count,
        total_count=total_count,
        completion_pct=completion_pct,
        is_own=is_own,
        equipped=equipped,
    )


@profile_bp.route("/<int:player_id>/achievements/<int:achievement_id>/pin", methods=["POST"])
@login_required
def pin_achievement(player_id: int, achievement_id: int):
    player = db.session.get(Player, player_id) or abort(404)
    if not PermissionService.can_edit_player(current_user, player):
        abort(403)
    result = AchievementService.pin(player_id, achievement_id)
    flash(result.message, "success" if result.ok else "danger")
    return redirect(url_for("profile.achievements", player_id=player_id))


@profile_bp.route("/<int:player_id>/achievements/<int:achievement_id>/unpin", methods=["POST"])
@login_required
def unpin_achievement(player_id: int, achievement_id: int):
    player = db.session.get(Player, player_id) or abort(404)
    if not PermissionService.can_edit_player(current_user, player):
        abort(403)
    result = AchievementService.unpin(player_id, achievement_id)
    flash(result.message, "success" if result.ok else "danger")
    return redirect(url_for("profile.achievements", player_id=player_id))


@profile_bp.route("/<int:player_id>/customization")
def customization(player_id: int):
    player = db.session.get(Player, player_id) or abort(404)
    data = ProfileService.get_profile_customization(player_id)
    is_own = current_user.is_authenticated and current_user.player_id == player_id
    equipped = ShopService.get_equipped(player_id)
    return render_template(
        "profile/customization.html",
        player=player,
        player_id=player_id,
        customization=data,
        is_own=is_own,
        equipped=equipped,
    )
