from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import current_user

from app import db
from app.models import Title, Player
from app.services import TitleService, NominationService
from app.services.nomination_service import SEASONAL_ROLE_TITLES
from app.services.season_service import SeasonService
from app.services.shop_service import ShopService
from app.auth_decorators import login_required

titles_bp = Blueprint("titles", __name__)


RARITY_TIER_ORDER = {"legendary": 0, "mythic": 1, "ultra": 1, "epic": 2, "rare": 3, "common": 4}


@titles_bp.route("/nominations")
def nominations():
    global_holders = TitleService.get_current_global_holders()

    # ── Зал славы: обогащаем каждый "вечный" титул осязаемым значением
    # рекорда, топ-3 претендентов и историей обладателей — всё чтение,
    # без побочных эффектов (recompute остаётся только по кнопке админа).
    hof_cards = []
    for pt in global_holders:
        code = pt.title.code
        record = NominationService.get_eternal_record_value(code, pt.player_id)
        top3 = NominationService.get_eternal_ranking(code, limit=3)
        exclusivity = TitleService.get_exclusivity_stats(pt.title_id)
        hof_cards.append({
            "player_title": pt,
            "title": pt.title,
            "player": pt.player,
            "record": record,
            "top3": top3,
            "history": TitleService.get_title_history(pt.title_id),
            "exclusivity": exclusivity,
            "tier": RARITY_TIER_ORDER.get(pt.title.rarity.value, 4),
        })
    hof_cards.sort(key=lambda c: (c["tier"], c["title"].name))

    # ── Витрина сверху: "Легенда клуба" как центральный герой (общая
    # формула bonus_sum*WR — ближе всего к "лучший игрок клуба" из всех
    # 15 вечных титулов), плюс несколько сопутствующих фактов о нём.
    hero = next((c for c in hof_cards if c["title"].code == "club_legend"), None)
    hero_facts = None
    if hero:
        from app.models import PlayerTitle, Season
        hero_titles_count = (
            db.session.query(PlayerTitle)
            .filter_by(player_id=hero["player"].id, revoked=False)
            .count()
        )
        hero_season_wins = db.session.query(Season).filter_by(
            winner_player_id=hero["player"].id
        ).count()
        hero_facts = {
            "elo": round(hero["player"].elo, 0),
            "titles_count": hero_titles_count,
            "season_wins": hero_season_wins,
        }

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
            current_leaders.append({
                "title": title,
                "player": leader_players.get(player_id) if player_id else None,
            })

    history = TitleService.get_seasonal_history()

    player_ids = {pt.player_id for pt in global_holders}
    player_ids.update(e["player"].id for e in current_leaders if e["player"])
    player_ids.update(award["player_id"] for h in history for award in h["awards"])
    for card in hof_cards:
        player_ids.update(t["player_id"] for t in card["top3"])
        player_ids.update(h.player_id for h in card["history"])
    equipped_bulk = ShopService.get_equipped_bulk(list(player_ids))

    all_players = {
        p.id: p for p in db.session.query(Player).filter(Player.id.in_(player_ids)).all()
    } if player_ids else {}

    return render_template(
        "titles/nominations.html",
        global_holders=global_holders,
        hof_cards=hof_cards,
        hero=hero,
        hero_facts=hero_facts,
        current_season=current_season,
        current_leaders=current_leaders,
        history=history,
        equipped_bulk=equipped_bulk,
        all_players=all_players,
    )


@titles_bp.route("/<int:player_title_id>/equip", methods=["POST"])
@login_required
def equip(player_title_id: int):
    if not current_user.player_id:
        flash("Нет привязанного профиля игрока.", "danger")
        return redirect(url_for("titles.nominations"))

    result = TitleService.equip(current_user.player, player_title_id)
    flash(result.message, "success" if result.ok else "danger")
    return redirect(url_for("profile.own_profile"))


@titles_bp.route("/unequip", methods=["POST"])
@login_required
def unequip():
    if not current_user.player_id:
        flash("Нет привязанного профиля игрока.", "danger")
        return redirect(url_for("titles.nominations"))

    result = TitleService.unequip(current_user.player)
    flash(result.message, "success" if result.ok else "danger")
    return redirect(url_for("profile.own_profile"))
