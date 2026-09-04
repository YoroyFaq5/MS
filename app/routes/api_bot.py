"""
API Blueprint  /api/v1/bot/*
============================
JSON REST API специально для Telegram-бота (MS-TelegramBot, отдельный
репозиторий/деплой). Отличается от /api/* (app/routes/api.py) авторизацией:
не сессия, а серверный токен бота (Authorization: Bearer
<MAIN_API_SERVICE_TOKEN>) на каждый запрос — бот сам не имеет сессии
пользователя, только знает telegram_id того, кто ему написал. Сайт сам
резолвит telegram_id -> Player через колонку Player.telegram_id (бот эту
связь у себя не хранит, см. AuthService.link_telegram/PROJECT_CONTEXT).

Версионирование (/v1/) — сознательно, в отличие от /api/*, у которого
версии нет вообще: этот слой проектируется с нуля, есть возможность
не повторять тот пробел.
"""
import hmac
import logging
import time
from collections import defaultdict, deque

from flask import Blueprint, current_app, jsonify, request

from app import db
from app.models import (
    Player, Tournament, TournamentParticipant, WinSide,
    SeriesTournament, TournamentSeries, Season, SeasonStatus,
    ShopItem, ShopCategory, InventoryItem, Game, GameSlot,
)
from app.services import ProfileService, RatingService, TournamentService, FantasyService
from app.services.auth_service import AuthService

logger = logging.getLogger(__name__)

api_bot_bp = Blueprint("api_bot", __name__)

# ── Rate limiting (in-process, best-effort) ──────────────────────────────────
# Not a substitute for a real distributed limiter (Redis, nginx limit_req) —
# each gunicorn worker keeps its own counters, so the effective ceiling under
# N workers is roughly N times these numbers. That's an accepted trade-off
# for "stop an obviously misbehaving/compromised bot process from hammering
# the site" without adding new infrastructure; a proper shared limiter is
# listed as a follow-up in the bot's ARCHITECTURE.md.
_RATE_LIMIT_WINDOW_SECONDS = 60
_RATE_LIMIT_MAX_REQUESTS = 120  # per telegram_id (or bare IP) per window
_rate_buckets: dict[str, deque] = defaultdict(deque)

# Bot requests are small JSON — nothing it legitimately sends should ever
# approach this. Blocks a compromised/buggy bot process from sending huge
# bodies that would otherwise be parsed in full before any validation runs.
_MAX_BODY_BYTES = 32 * 1024


def _rate_limit_key() -> str:
    telegram_id = request.args.get("telegram_id") or (request.get_json(silent=True) or {}).get("telegram_id")
    if telegram_id:
        return f"tg:{telegram_id}"
    return f"ip:{request.remote_addr or 'unknown'}"


def _check_rate_limit() -> bool:
    """True if the request is allowed, False if the caller should be throttled."""
    key = _rate_limit_key()
    now = time.monotonic()
    bucket = _rate_buckets[key]
    cutoff = now - _RATE_LIMIT_WINDOW_SECONDS
    while bucket and bucket[0] < cutoff:
        bucket.popleft()
    if len(bucket) >= _RATE_LIMIT_MAX_REQUESTS:
        return False
    bucket.append(now)
    return True


def _ok(data=None, message: str = "ok") -> tuple:
    return jsonify({"status": "ok", "message": message, "data": data}), 200


def _fail(message: str, code: int = 400) -> tuple:
    return jsonify({"status": "error", "message": message}), code


def _paginate(items: list, page: int, per_page: int) -> dict:
    total = len(items)
    start = (page - 1) * per_page
    return {
        "items": items[start:start + per_page],
        "page": page,
        "per_page": per_page,
        "total": total,
        "total_pages": (total + per_page - 1) // per_page if per_page else 0,
    }


@api_bot_bp.before_request
def _check_service_token():
    expected = current_app.config.get("MAIN_API_SERVICE_TOKEN")
    if not expected:
        return _fail("Bot API не настроен на этом сервере.", 503)
    auth_header = request.headers.get("Authorization", "")
    token = auth_header[len("Bearer "):] if auth_header.startswith("Bearer ") else ""
    # Constant-time comparison — a naive `!=` leaks timing information about
    # how many leading characters matched, in principle usable to brute-force
    # the token byte-by-byte over enough requests.
    if not token or not hmac.compare_digest(token, expected):
        return _fail("Unauthorized", 401)

    if request.content_length and request.content_length > _MAX_BODY_BYTES:
        return _fail("Тело запроса слишком большое.", 413)

    if not _check_rate_limit():
        return _fail("Слишком много запросов, попробуйте позже.", 429)


def _resolve_player(telegram_id: str):
    if not telegram_id:
        return None
    return db.session.query(Player).filter_by(telegram_id=telegram_id).first()


def _resolve_user(telegram_id: str):
    """
    FantasyService оперирует User (не Player) — вход в фэнтези-драфт
    списывает монеты с Player, но сам драфт принадлежит User.id. Раз
    Login Widget привязывает Telegram только залогиненному User (см.
    /auth/telegram/callback), у любого Player с telegram_id гарантированно
    есть ровно один User с этим player_id — обратная связь всегда цела.
    """
    player = _resolve_player(telegram_id)
    if not player:
        return None
    from app.models.user import User
    return db.session.query(User).filter_by(player_id=player.id).first()


def _can_view_standings(tournament_id: int, tournament: Tournament, viewer_player) -> bool:
    """
    Bot-API equivalent of tournaments.py::_can_view_standings — same rule
    (hidden standings are visible only to an admin who isn't themselves a
    participant), just resolved from telegram_id instead of a Flask-Login
    session, since the bot never carries one. Without this check `/tournaments/
    <id>` handed out player_ratings/team_ratings unconditionally regardless of
    Tournament.hide_standings — the exact leak this closes.
    """
    if not tournament.hide_standings:
        return True
    if not viewer_player:
        return False
    from app.models.user import User
    viewer_user = db.session.query(User).filter_by(player_id=viewer_player.id).first()
    if not viewer_user or not viewer_user.is_admin:
        return False
    is_participant = (
        db.session.query(TournamentParticipant)
        .filter_by(tournament_id=tournament_id, player_id=viewer_player.id)
        .first()
        is not None
    )
    return not is_participant


def _result_response(result) -> tuple:
    if not result.ok:
        return _fail(result.message)
    data = result.data.to_dict() if hasattr(result.data, "to_dict") else None
    return _ok(data, result.message)


# ── Поиск игроков (для инлайн-режима бота) ───────────────────────────────────

@api_bot_bp.route("/players/search")
def players_search():
    from app.services.player_search_service import PlayerSearchService

    query = request.args.get("q", "").strip()
    if not query:
        return _ok([])
    results = PlayerSearchService.find_similar_players(query, limit=10)
    return _ok([{"id": p.id, "display_name": p.display_name, "elo": p.elo} for p in results])


# ── Резолв привязки ──────────────────────────────────────────────────────────

@api_bot_bp.route("/resolve")
def resolve():
    telegram_id = request.args.get("telegram_id", "")
    player = _resolve_player(telegram_id)
    if not player:
        return _ok({"linked": False})
    return _ok({"linked": True, "player_id": player.id, "display_name": player.display_name})


# ── Профиль/статистика ────────────────────────────────────────────────────────

@api_bot_bp.route("/profile")
def profile():
    player = _resolve_player(request.args.get("telegram_id", ""))
    if not player:
        return _fail("Игрок не привязан.", 404)
    data = ProfileService.get_profile(player.id)
    if not data:
        return _fail("Игрок не найден.", 404)
    return _ok(data)


@api_bot_bp.route("/stats")
def stats():
    player = _resolve_player(request.args.get("telegram_id", ""))
    if not player:
        return _fail("Игрок не привязан.", 404)
    extended = ProfileService.get_statistics(player.id)
    if not extended:
        return _fail("Игрок не найден.", 404)
    return _ok({
        "stats": extended.to_dict(),
        "role_stats": ProfileService.get_role_statistics(player.id),
        "partner_stats": ProfileService.get_partner_statistics(player.id),
        "rivalry_stats": ProfileService.get_rivalry_statistics(player.id),
        "comparison_stats": ProfileService.get_comparison_stats(player.id),
    })


@api_bot_bp.route("/compare")
def compare():
    player = _resolve_player(request.args.get("telegram_id", ""))
    if not player:
        return _fail("Игрок не привязан.", 404)
    opponent_id = request.args.get("opponent_id", type=int)
    if not opponent_id:
        return _fail("opponent_id обязателен.")

    result = ProfileService.compare_players(player.id, opponent_id)
    if not result:
        return _fail("Не удалось сравнить — проверьте ID соперника.", 404)
    result = {
        **result,
        "player_a": result["player_a"].to_dict(),
        "player_b": result["player_b"].to_dict(),
    }
    return _ok(result)


@api_bot_bp.route("/players/<int:player_id>")
def player_public_detail(player_id: int):
    """Minimal public identity lookup (id/display_name/elo/active) — used
    wherever the bot only has a player_id in hand (e.g. after a name-search
    pick) and needs the name back for a confirmation screen, without
    exposing anything not already public via /players/search."""
    player = db.session.get(Player, player_id)
    if not player or not player.is_active:
        return _fail("Игрок не найден.", 404)
    return _ok({"id": player.id, "display_name": player.display_name, "elo": player.elo})


@api_bot_bp.route("/players/compare")
def players_compare():
    """
    Сравнение ЛЮБЫХ двух игроков без привязки к telegram_id вызывающего —
    для инлайн-режима бота ("Имя1 vs Имя2" в любом чате). ProfileService.
    compare_players уже принимает произвольную пару id, роут /compare просто
    исторически резолвит игрока A только через привязанный telegram-аккаунт.
    """
    a = request.args.get("a", type=int)
    b = request.args.get("b", type=int)
    if not a or not b:
        return _fail("Параметры a и b обязательны.")

    result = ProfileService.compare_players(a, b)
    if not result:
        return _fail("Не удалось сравнить — проверьте ID игроков.", 404)
    result = {
        **result,
        "player_a": result["player_a"].to_dict(),
        "player_b": result["player_b"].to_dict(),
    }
    return _ok(result)


# ── Рейтинг ───────────────────────────────────────────────────────────────────

@api_bot_bp.route("/ratings")
def ratings():
    scope = request.args.get("scope", "global")
    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 10, type=int), 50)

    if scope == "global":
        ratings_list = RatingService.get_global_rating()
    elif scope == "season":
        season_id = request.args.get("season_id", type=int)
        if not season_id:
            return _fail("season_id обязателен для scope=season.")
        ratings_list = RatingService.get_season_rating(season_id)
    elif scope == "year":
        year = request.args.get("year", type=int)
        if not year:
            return _fail("year обязателен для scope=year.")
        from app.services.season_service import SeasonService
        SeasonService.ensure_year_exists(year)
        ratings_list = RatingService.get_year_rating(year)
    else:
        return _fail("Неверный scope (global|season|year).")

    data = [r.to_dict() for r in ratings_list]
    return _ok(_paginate(data, page, per_page))


# ── История игр ───────────────────────────────────────────────────────────────

@api_bot_bp.route("/history")
def history():
    player = _resolve_player(request.args.get("telegram_id", ""))
    if not player:
        return _fail("Игрок не привязан.", 404)
    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 10, type=int), 50)

    slots = ProfileService.get_game_history(
        player.id, limit=per_page, offset=(page - 1) * per_page,
    )
    items = []
    for s in slots:
        won = (
            (s.is_mafia_side and s.game.win_side == WinSide.MAFIA)
            or (s.is_city_side and s.game.win_side == WinSide.CITY)
        )
        items.append({
            "slot": s.to_dict(),
            "game": {
                "id": s.game.id,
                "played_at": s.game.played_at.isoformat(),
                "win_side": s.game.win_side.value,
            },
            "won": won,
        })
    return _ok({"items": items, "page": page, "per_page": per_page})


# ── Экономика ─────────────────────────────────────────────────────────────────

@api_bot_bp.route("/economy/balance")
def economy_balance():
    player = _resolve_player(request.args.get("telegram_id", ""))
    if not player:
        return _fail("Игрок не привязан.", 404)
    from app.services.economy_service import EconomyService
    return _ok({"balance": EconomyService.get_balance(player)})


@api_bot_bp.route("/economy/history")
def economy_history():
    player = _resolve_player(request.args.get("telegram_id", ""))
    if not player:
        return _fail("Игрок не привязан.", 404)
    from app.services.economy_service import EconomyService
    limit = min(request.args.get("limit", 20, type=int), 100)
    txs = EconomyService.get_history(player.id, limit=limit)
    return _ok([t.to_dict() for t in txs])


# ── Достижения/титулы ─────────────────────────────────────────────────────────

@api_bot_bp.route("/achievements")
def achievements():
    player = _resolve_player(request.args.get("telegram_id", ""))
    if not player:
        return _fail("Игрок не привязан.", 404)
    return _ok(ProfileService.get_achievements(player.id))


@api_bot_bp.route("/achievements/<int:achievement_id>/pin", methods=["POST"])
def achievement_pin(achievement_id: int):
    data = request.get_json(silent=True) or {}
    player = _resolve_player(data.get("telegram_id", ""))
    if not player:
        return _fail("Игрок не привязан.", 404)
    from app.services.achievement_service import AchievementService
    result = AchievementService.pin(player.id, achievement_id)
    return (_ok(message=result.message) if result.ok else _fail(result.message))


@api_bot_bp.route("/achievements/<int:achievement_id>/unpin", methods=["POST"])
def achievement_unpin(achievement_id: int):
    data = request.get_json(silent=True) or {}
    player = _resolve_player(data.get("telegram_id", ""))
    if not player:
        return _fail("Игрок не привязан.", 404)
    from app.services.achievement_service import AchievementService
    result = AchievementService.unpin(player.id, achievement_id)
    return (_ok(message=result.message) if result.ok else _fail(result.message))


@api_bot_bp.route("/titles")
def titles():
    player = _resolve_player(request.args.get("telegram_id", ""))
    if not player:
        return _fail("Игрок не привязан.", 404)
    from app.services.title_service import TitleService
    return _ok([t.to_dict() for t in TitleService.list_player_titles(player.id)])


@api_bot_bp.route("/titles/<int:player_title_id>/equip", methods=["POST"])
def title_equip(player_title_id: int):
    data = request.get_json(silent=True) or {}
    player = _resolve_player(data.get("telegram_id", ""))
    if not player:
        return _fail("Игрок не привязан.", 404)
    from app.services.title_service import TitleService
    result = TitleService.equip(player, player_title_id)
    return _result_response(result)


@api_bot_bp.route("/titles/unequip", methods=["POST"])
def title_unequip():
    data = request.get_json(silent=True) or {}
    player = _resolve_player(data.get("telegram_id", ""))
    if not player:
        return _fail("Игрок не привязан.", 404)
    from app.services.title_service import TitleService
    result = TitleService.unequip(player)
    return _result_response(result)


# ── Турниры (только просмотр — без регистрации, по решению из
#    согласования функционала бота) ─────────────────────────────────────────────

@api_bot_bp.route("/tournaments")
def tournaments_list():
    status = request.args.get("status")  # pending|active|finished|None(все)
    type_filter = request.args.get("type")  # individual|team|None
    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 10, type=int), 50)

    query = db.session.query(Tournament).order_by(Tournament.created_at.desc())
    if status:
        query = query.filter(Tournament.status == status)
    if type_filter:
        query = query.filter(Tournament.type == type_filter)
    tournaments = query.all()
    series_ids = {
        st.tournament_id: st.id
        for st in db.session.query(SeriesTournament)
        .filter(SeriesTournament.tournament_id.in_([t.id for t in tournaments]))
        .all()
    } if tournaments else {}

    items = []
    for t in tournaments:
        d = t.to_dict()
        d["series_tournament_id"] = series_ids.get(t.id)
        items.append(d)
    return _ok(_paginate(items, page, per_page))


@api_bot_bp.route("/tournaments/<int:tournament_id>")
def tournament_detail(tournament_id: int):
    summary = TournamentService.get_tournament_summary(tournament_id)
    if not summary:
        return _fail("Турнир не найден.", 404)

    tournament = summary["tournament"]
    viewer_player = _resolve_player(request.args.get("telegram_id", ""))
    can_view_standings = _can_view_standings(tournament_id, tournament, viewer_player)
    series_tournament = db.session.query(SeriesTournament).filter_by(tournament_id=tournament_id).first()

    return _ok({
        "tournament": tournament.to_dict(),
        "series_tournament_id": series_tournament.id if series_tournament else None,
        "stages": summary["stages"],
        "games_finished": summary["games_finished"],
        "games_total": summary["games_total"],
        "participant_count": summary["participant_count"],
        "can_view_standings": can_view_standings,
        "player_ratings": [r.to_dict() for r in summary["player_ratings"]] if can_view_standings else [],
        "team_ratings": [r.to_dict() for r in summary["team_ratings"]] if can_view_standings else [],
        "active_stage": summary["active_stage"].to_dict() if summary["active_stage"] else None,
    })


# ── Серийные турниры ─────────────────────────────────────────────────────────
# Отдельная ветка API — сайт сам не смешивает обычный и серийный интерфейс
# (см. tournaments/list.html, series_tournaments/*), бот следует тому же
# правилу: карточка серийного турнира ведёт сюда, а не в /tournaments/<id>.

@api_bot_bp.route("/series-tournaments")
def series_tournaments_list():
    from app.services import SeriesTournamentService
    items = [st.to_dict() for st in SeriesTournamentService.list_series_tournaments()]
    return _ok(items)


@api_bot_bp.route("/series-tournaments/<int:series_tournament_id>")
def series_tournament_detail(series_tournament_id: int):
    from app.services import SeriesTournamentService
    st = SeriesTournamentService.get_series_tournament(series_tournament_id)
    if not st:
        return _fail("Серийный турнир не найден.", 404)
    overall = SeriesTournamentService.get_overall_leaderboard(series_tournament_id)
    return _ok({
        "series_tournament": st.to_dict(),
        "series": [s.to_dict() for s in sorted(st.series, key=lambda s: s.order)],
        "overall_leaderboard": [e.to_dict() for e in overall[:20]],
    })


@api_bot_bp.route("/series/<int:series_id>")
def series_evening_shortcut(series_id: int):
    """Same evening data as series_evening_detail, but addressable by its
    own id alone — used by Fantasy screens, which only ever carry
    (tournament_id, series_id) in their compact callback_data and have no
    reason to also track the series_tournament wrapper id."""
    series = db.session.get(TournamentSeries, series_id)
    if not series:
        return _fail("Вечер серии не найден.", 404)
    st = series.series_tournament
    return _ok({
        "series": series.to_dict(),
        "series_tournament_id": st.id,
        "tournament_id": st.tournament_id,
        "tournament_name": st.tournament.name,
    })


@api_bot_bp.route("/series-tournaments/<int:series_tournament_id>/series/<int:series_id>")
def series_evening_detail(series_tournament_id: int, series_id: int):
    from app.services import SeriesTournamentService
    st = SeriesTournamentService.get_series_tournament(series_tournament_id)
    series = db.session.get(TournamentSeries, series_id)
    if not st or not series or series.series_tournament_id != series_tournament_id:
        return _fail("Вечер серии не найден.", 404)
    leaderboard = SeriesTournamentService.get_series_leaderboard(series_id)
    return _ok({
        "series_tournament": st.to_dict(),
        "series": series.to_dict(),
        "leaderboard": [r.to_dict() for r in leaderboard],
    })


# ── Сезоны ────────────────────────────────────────────────────────────────────

@api_bot_bp.route("/seasons/current")
def season_current():
    from app.services.season_service import SeasonService
    season = SeasonService.get_current_season()
    if not season:
        return _ok(None)
    return _ok(season.to_dict())


@api_bot_bp.route("/seasons")
def seasons_list():
    from app.services.season_service import SeasonService
    year = request.args.get("year", type=int)
    if not year:
        from datetime import datetime, timezone
        year = datetime.now(timezone.utc).year
    seasons = SeasonService.get_seasons_for_year(year)
    return _ok({"year": year, "seasons": [s.to_dict() for s in seasons]})


@api_bot_bp.route("/seasons/<int:season_id>")
def season_detail(season_id: int):
    from app.services.season_rating_engine import SeasonRatingEngine
    season = db.session.get(Season, season_id)
    if not season:
        return _fail("Сезон не найден.", 404)
    ratings = SeasonRatingEngine.compute_season_ratings(season_id)
    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 10, type=int), 50)
    data = [r.to_dict() for r in ratings]
    return _ok({
        "season": season.to_dict(),
        "min_games_for_top5": SeasonRatingEngine.MIN_GAMES_FOR_TOP5,
        "ratings": _paginate(data, page, per_page),
    })


@api_bot_bp.route("/seasons/<int:season_id>/my-place")
def season_my_place(season_id: int):
    """
    "Моё место" — карточка игрока текущего сезона: игры, порог топ-5, очки,
    GG и два ближайших соперника (по рейтингу выше/ниже), чтобы боту не
    приходилось скачивать всю таблицу целиком ради одной строки.
    """
    from app.services.season_rating_engine import SeasonRatingEngine
    player = _resolve_player(request.args.get("telegram_id", ""))
    if not player:
        return _fail("Игрок не привязан.", 404)
    season = db.session.get(Season, season_id)
    if not season:
        return _fail("Сезон не найден.", 404)

    ratings = SeasonRatingEngine.compute_season_ratings(season_id)
    idx_by_pid = {r.player_id: i for i, r in enumerate(ratings)}
    idx = idx_by_pid.get(player.id)
    if idx is None:
        return _ok({
            "season": season.to_dict(),
            "min_games_for_top5": SeasonRatingEngine.MIN_GAMES_FOR_TOP5,
            "entry": None,
            "neighbor_above": None,
            "neighbor_below": None,
        })
    entry = ratings[idx]
    neighbor_above = ratings[idx - 1].to_dict() if idx > 0 else None
    neighbor_below = ratings[idx + 1].to_dict() if idx + 1 < len(ratings) else None
    return _ok({
        "season": season.to_dict(),
        "min_games_for_top5": SeasonRatingEngine.MIN_GAMES_FOR_TOP5,
        "entry": entry.to_dict(),
        "neighbor_above": neighbor_above,
        "neighbor_below": neighbor_below,
    })


@api_bot_bp.route("/seasons/winners")
def season_winners():
    """History of season winners, most recent first — for the "История
    победителей" screen. finished_only implied (a season without a winner
    yet has winner_player_id=None and is simply skipped)."""
    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 10, type=int), 50)
    seasons = (
        db.session.query(Season)
        .filter(Season.status == SeasonStatus.FINISHED, Season.winner_player_id.isnot(None))
        .order_by(Season.year.desc(), Season.number.desc())
        .all()
    )
    data = [s.to_dict() for s in seasons]
    return _ok(_paginate(data, page, per_page))


# ── Карточка игры ─────────────────────────────────────────────────────────────

@api_bot_bp.route("/games/<int:game_id>")
def game_detail(game_id: int):
    """
    Bot-safe game card: result, date, roster, roles, scores/bonuses, and a
    link to its tournament/series — deliberately mirrors only what
    games/detail.html shows an ordinary (non-admin) visitor. Live-protocol
    fields (live_phase/live_turn/live_role), quality_score (judge-only ELO
    input) and elimination_type are admin/broadcast-only on the site and
    are not included here.
    """
    game = db.session.get(Game, game_id)
    if not game:
        return _fail("Игра не найдена.", 404)

    series = None
    if game.stage_id:
        series = db.session.query(TournamentSeries).filter_by(stage_id=game.stage_id).first()

    slots = sorted(game.slots, key=lambda s: s.seat_number)
    return _ok({
        "game": game.to_dict(),
        "slots": [
            {
                "seat_number": s.seat_number,
                "player_id": s.player_id,
                "player_name": s.player.display_name if s.player else None,
                "role": s.role.value,
                "base_score": s.base_score,
                "bonus_score": s.bonus_score,
                "total_score": s.total_score,
                "is_pu": s.is_pu,
                "is_eliminated": s.is_eliminated,
            }
            for s in slots
        ],
        "tournament_id": game.tournament_id,
        "tournament_series_id": series.series_tournament_id if series else None,
        "series_id": series.id if series else None,
    })


# ── Fantasy (полное управление драфтом из бота, включая серии/группы/
#    practice-режим — см. FantasyService module docstring) ───────────────────

def _fantasy_scope_args():
    tournament_id = request.args.get("tournament_id", type=int)
    tournament_series_id = request.args.get("tournament_series_id", type=int)
    is_practice = request.args.get("is_practice", "0") in ("1", "true", "True")
    return tournament_id, tournament_series_id, is_practice


def _fantasy_scope_body(data: dict):
    tournament_id = data.get("tournament_id")
    tournament_series_id = data.get("tournament_series_id")
    is_practice = bool(data.get("is_practice", False))
    return tournament_id, tournament_series_id, is_practice


@api_bot_bp.route("/fantasy/events")
def fantasy_events():
    """
    Everything currently draftable, without the caller ever having to know
    a tournament_id up front — mirrors fantasy/index.html's own query
    (see routes/fantasy.py::index): recent tournaments + all ACTIVE series
    evenings, each enriched with pool info and the caller's own draft
    status (paid + practice) so the bot can render "✅ Есть драфт" vs
    "➕ Создать" without a second round-trip per item.
    """
    from app.models import FantasyDraft, SeriesStatus as _SeriesStatus
    user = _resolve_user(request.args.get("telegram_id", ""))

    tournaments = (
        db.session.query(Tournament)
        .filter(Tournament.status.in_(["pending", "active", "finished"]))
        .order_by(Tournament.created_at.desc())
        .limit(20)
        .all()
    )
    active_series = (
        db.session.query(TournamentSeries)
        .filter_by(status=_SeriesStatus.ACTIVE)
        .order_by(TournamentSeries.created_at.desc())
        .all()
    )

    my_drafts = {}
    if user:
        for d in db.session.query(FantasyDraft).filter_by(user_id=user.id).all():
            key = (d.tournament_id, d.tournament_series_id, d.is_practice)
            my_drafts[key] = d.id

    tournament_items = [
        {
            "kind": "tournament",
            "tournament": t.to_dict(),
            "pool": FantasyService.get_pool_info(t.id),
            "my_draft_id": my_drafts.get((t.id, None, False)),
            "my_practice_draft_id": my_drafts.get((t.id, None, True)),
        }
        for t in tournaments
    ]
    series_items = [
        {
            "kind": "series",
            "series": s.to_dict(),
            "tournament_id": s.series_tournament.tournament_id,
            "tournament_name": s.series_tournament.tournament.name,
            "pool": FantasyService.get_pool_info(s.series_tournament.tournament_id, s.id),
            "my_draft_id": my_drafts.get((s.series_tournament.tournament_id, s.id, False)),
            "my_practice_draft_id": my_drafts.get((s.series_tournament.tournament_id, s.id, True)),
        }
        for s in active_series
    ]
    return _ok({"tournaments": tournament_items, "series": series_items})


@api_bot_bp.route("/fantasy/history")
def fantasy_history():
    user = _resolve_user(request.args.get("telegram_id", ""))
    if not user:
        return _fail("Игрок не привязан.", 404)
    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 10, type=int), 50)
    drafts = FantasyService.get_user_draft_history(user.id)
    data = [d.to_dict() for d in drafts]
    return _ok(_paginate(data, page, per_page))


@api_bot_bp.route("/fantasy/my")
def fantasy_my():
    user = _resolve_user(request.args.get("telegram_id", ""))
    if not user:
        return _fail("Игрок не привязан.", 404)
    tournament_id, tournament_series_id, is_practice = _fantasy_scope_args()
    if not tournament_id:
        return _fail("tournament_id обязателен.")
    draft = FantasyService.get_user_draft(user.id, tournament_id, tournament_series_id, is_practice)
    if not draft:
        return _fail("У вас нет драфта для этого события.", 404)
    return _ok(draft.to_dict())


@api_bot_bp.route("/fantasy/draft/<int:draft_id>")
def fantasy_draft_by_id(draft_id: int):
    """Fetch one draft directly by id — used after an action (remove-pick)
    whose own response carries no data, so the bot can re-render the
    updated draft without having to re-derive (tournament_id, series_id,
    is_practice) to look it up by scope instead."""
    from app.models import FantasyDraft
    user = _resolve_user(request.args.get("telegram_id", ""))
    if not user:
        return _fail("Игрок не привязан.", 404)
    draft = db.session.get(FantasyDraft, draft_id)
    if not draft or (draft.user_id != user.id and not user.is_admin):
        return _fail("Драфт не найден.", 404)
    return _ok(draft.to_dict())


@api_bot_bp.route("/fantasy/draft", methods=["POST"])
def fantasy_create_draft():
    data = request.get_json(silent=True) or {}
    user = _resolve_user(data.get("telegram_id", ""))
    if not user:
        return _fail("Игрок не привязан.", 404)
    tournament_id, tournament_series_id, is_practice = _fantasy_scope_body(data)
    if not tournament_id:
        return _fail("tournament_id обязателен.")
    result = FantasyService.create_draft(
        user, int(tournament_id),
        int(tournament_series_id) if tournament_series_id else None,
        is_practice=is_practice,
    )
    return _result_response(result)


@api_bot_bp.route("/fantasy/pick", methods=["POST"])
def fantasy_add_pick():
    data = request.get_json(silent=True) or {}
    user = _resolve_user(data.get("telegram_id", ""))
    if not user:
        return _fail("Игрок не привязан.", 404)
    draft_id, player_id = data.get("draft_id"), data.get("player_id")
    if not draft_id or not player_id:
        return _fail("draft_id и player_id обязательны.")
    result = FantasyService.add_pick(user, int(draft_id), int(player_id))
    return _result_response(result)


@api_bot_bp.route("/fantasy/pick", methods=["DELETE"])
def fantasy_remove_pick():
    data = request.get_json(silent=True) or {}
    user = _resolve_user(data.get("telegram_id", ""))
    if not user:
        return _fail("Игрок не привязан.", 404)
    draft_id, player_id = data.get("draft_id"), data.get("player_id")
    if not draft_id or not player_id:
        return _fail("draft_id и player_id обязательны.")
    result = FantasyService.remove_pick(user, int(draft_id), int(player_id))
    return _result_response(result)


@api_bot_bp.route("/fantasy/draft/<int:draft_id>/cancel", methods=["POST"])
def fantasy_cancel_draft(draft_id: int):
    data = request.get_json(silent=True) or {}
    user = _resolve_user(data.get("telegram_id", ""))
    if not user:
        return _fail("Игрок не привязан.", 404)
    result = FantasyService.cancel_draft(user, draft_id)
    return _result_response(result)


@api_bot_bp.route("/fantasy/leaderboard")
def fantasy_leaderboard():
    tournament_id, tournament_series_id, is_practice = _fantasy_scope_args()
    if not tournament_id:
        return _fail("tournament_id обязателен.")
    group_number = request.args.get("group_number", type=int)
    entries = FantasyService.get_leaderboard(
        tournament_id, tournament_series_id, group_number=group_number, is_practice=is_practice,
    )
    return _ok([e.to_dict() for e in entries])


@api_bot_bp.route("/fantasy/available")
def fantasy_available():
    user = _resolve_user(request.args.get("telegram_id", ""))
    if not user:
        return _fail("Игрок не привязан.", 404)
    tournament_id, tournament_series_id, is_practice = _fantasy_scope_args()
    if not tournament_id:
        return _fail("tournament_id обязателен.")
    players = FantasyService.get_available_picks(user, tournament_id, tournament_series_id, is_practice)
    return _ok([{"id": p.id, "name": p.display_name, "elo": p.elo} for p in players])


# ── Аккаунт ───────────────────────────────────────────────────────────────────

@api_bot_bp.route("/account/unlink", methods=["POST"])
def account_unlink():
    data = request.get_json(silent=True) or {}
    player = _resolve_player(data.get("telegram_id", ""))
    if not player:
        return _fail("Игрок не привязан.", 404)
    result = AuthService.unlink_telegram(player)
    return (_ok(message=result.message) if result.ok else _fail(result.message))


# ── Магазин ───────────────────────────────────────────────────────────────────

@api_bot_bp.route("/shop/items")
def shop_items():
    from app.services.shop_service import ShopService

    category = request.args.get("category")
    sort = request.args.get("sort")
    player = _resolve_player(request.args.get("telegram_id", ""))
    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 8, type=int), 30)

    try:
        category_enum = ShopCategory(category) if category else None
    except ValueError:
        return _fail("Неверная категория.")

    items = ShopService.list_items(category=category_enum, sort=sort)
    owned_ids = set()
    if player:
        owned_ids = {
            inv.item_id for inv in
            db.session.query(InventoryItem).filter_by(player_id=player.id).all()
        }
    data = []
    for item in items:
        d = item.to_dict()
        d["already_owned"] = item.id in owned_ids
        d["current_owner_id"] = None
        if item.rarity.value in ("mythic", "ultra"):
            owner = ShopService.get_current_owner(item.id)
            d["current_owner_id"] = owner.player_id if owner else None
        data.append(d)
    return _ok(_paginate(data, page, per_page))


@api_bot_bp.route("/shop/items/<int:item_id>")
def shop_item_detail(item_id: int):
    from app.services.shop_service import ShopService

    item = ShopService.get_item(item_id)
    if not item or not item.is_active:
        return _fail("Товар не найден.", 404)
    player = _resolve_player(request.args.get("telegram_id", ""))
    d = item.to_dict()
    d["already_owned"] = False
    d["current_owner_id"] = None
    d["balance"] = None
    if player:
        d["already_owned"] = db.session.query(InventoryItem).filter_by(
            player_id=player.id, item_id=item.id,
        ).first() is not None
        from app.services.economy_service import EconomyService
        d["balance"] = EconomyService.get_balance(player)
    if item.rarity.value in ("mythic", "ultra"):
        owner = ShopService.get_current_owner(item.id)
        d["current_owner_id"] = owner.player_id if owner else None
    return _ok(d)


@api_bot_bp.route("/shop/items/<int:item_id>/buy", methods=["POST"])
def shop_item_buy(item_id: int):
    from app.services.shop_service import ShopService

    data = request.get_json(silent=True) or {}
    player = _resolve_player(data.get("telegram_id", ""))
    if not player:
        return _fail("Игрок не привязан.", 404)
    result = ShopService.purchase(player, item_id)
    return _result_response(result)


# ── Инвентарь ─────────────────────────────────────────────────────────────────

@api_bot_bp.route("/inventory")
def inventory_list():
    from app.services.shop_service import ShopService

    player = _resolve_player(request.args.get("telegram_id", ""))
    if not player:
        return _fail("Игрок не привязан.", 404)
    category = request.args.get("category")
    try:
        category_enum = ShopCategory(category) if category else None
    except ValueError:
        return _fail("Неверная категория.")
    items = ShopService.get_inventory(player.id, category=category_enum)
    data = [
        {
            "id": inv.id,
            "item": inv.item.to_dict(),
            "is_equipped": inv.is_equipped,
            "acquired_at": inv.acquired_at.isoformat(),
            "source": inv.source,
        }
        for inv in items
    ]
    return _ok(data)


@api_bot_bp.route("/inventory/<int:inventory_item_id>/equip", methods=["POST"])
def inventory_equip(inventory_item_id: int):
    from app.services.shop_service import ShopService

    data = request.get_json(silent=True) or {}
    player = _resolve_player(data.get("telegram_id", ""))
    if not player:
        return _fail("Игрок не привязан.", 404)
    result = ShopService.equip_item(player, inventory_item_id)
    return _result_response(result)


@api_bot_bp.route("/inventory/<int:inventory_item_id>/unequip", methods=["POST"])
def inventory_unequip(inventory_item_id: int):
    from app.services.shop_service import ShopService

    data = request.get_json(silent=True) or {}
    player = _resolve_player(data.get("telegram_id", ""))
    if not player:
        return _fail("Игрок не привязан.", 404)
    result = ShopService.unequip_item(player, inventory_item_id)
    return _result_response(result)


# ── Подарки ───────────────────────────────────────────────────────────────────

@api_bot_bp.route("/gifts/inbox")
def gifts_inbox():
    from app.services.gift_service import GiftService

    player = _resolve_player(request.args.get("telegram_id", ""))
    if not player:
        return _fail("Игрок не привязан.", 404)
    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 10, type=int), 50)
    transfers = GiftService.get_incoming_gifts(player.id)
    data = [t.to_dict() for t in transfers]
    GiftService.mark_seen(player.id)
    return _ok(_paginate(data, page, per_page))


@api_bot_bp.route("/gifts/history")
def gifts_history():
    from app.services.gift_service import GiftService

    player = _resolve_player(request.args.get("telegram_id", ""))
    if not player:
        return _fail("Игрок не привязан.", 404)
    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 10, type=int), 50)
    transfers = GiftService.get_transfer_history(player.id)
    data = [t.to_dict() for t in transfers]
    return _ok(_paginate(data, page, per_page))


@api_bot_bp.route("/gifts/giftable-items")
def gifts_giftable_items():
    """Own inventory items that are actually sendable: transferable and
    not currently equipped (send_gift rejects an equipped item, see
    GiftService) — filtered here so the bot never even offers a choice
    the site would reject."""
    player = _resolve_player(request.args.get("telegram_id", ""))
    if not player:
        return _fail("Игрок не привязан.", 404)
    items = (
        db.session.query(InventoryItem)
        .filter_by(player_id=player.id, is_equipped=False)
        .all()
    )
    data = [
        {"id": inv.id, "item": inv.item.to_dict()}
        for inv in items
        if inv.item.is_transferable
    ]
    return _ok(data)


@api_bot_bp.route("/gifts/send", methods=["POST"])
def gifts_send():
    from app.services.gift_service import GiftService

    data = request.get_json(silent=True) or {}
    sender = _resolve_player(data.get("telegram_id", ""))
    if not sender:
        return _fail("Игрок не привязан.", 404)
    inventory_item_id = data.get("inventory_item_id")
    to_player_id = data.get("to_player_id")
    if not inventory_item_id or not to_player_id:
        return _fail("inventory_item_id и to_player_id обязательны.")
    message = data.get("message")
    if message is not None and len(str(message)) > 200:
        return _fail("Слишком длинная заметка (максимум 200 символов).")
    result = GiftService.send_gift(sender, int(inventory_item_id), int(to_player_id), message)
    return _result_response(result)
