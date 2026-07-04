import os
from datetime import datetime
from app import create_app, db

app = create_app(os.environ.get("FLASK_ENV", "default"))


@app.context_processor
def inject_now():
    return {"now": datetime.utcnow()}


@app.context_processor
def inject_current_user_customization():
    """Стилизованное имя текущего юзера в шапке (base.html) — один лёгкий
    запрос на страницу, только если юзер залогинен и привязан к игроку."""
    from flask_login import current_user
    if current_user.is_authenticated and current_user.player_id:
        from app.services.shop_service import ShopService
        return {"current_user_equipped": ShopService.get_equipped(current_user.player_id)}
    return {"current_user_equipped": {}}


@app.cli.command("init-db")
def init_db():
    """Create all tables."""
    with app.app_context():
        db.create_all()
        print("OK: Database tables created.")


@app.cli.command("seed-players")
def seed_players():
    """Seed 10 sample players for testing."""
    from app.models import Player
    nicknames = [
        "Aleksey", "Boris", "Viktor", "Grigoriy", "Dmitriy",
        "Elena", "Zhanna", "Zinaida", "Ivan", "Kirill"
    ]
    with app.app_context():
        for nick in nicknames:
            if not db.session.query(Player).filter_by(nickname=nick).first():
                db.session.add(Player(nickname=nick, name=nick))
        db.session.commit()
        print(f"OK: Seeded {len(nicknames)} players.")


def _gradient_bg(c1: str, c2: str) -> str:
    """
    Inline SVG gradient as a data: URI — no external image hosting needed.
    Fully percent-encoded (not just '#'/' ') — the SVG itself uses single
    quotes for its own attributes, and the template embeds this URI inside
    a single-quoted CSS url('...'); an unescaped ' here would prematurely
    close that CSS string and break the background entirely.
    """
    from urllib.parse import quote
    svg = (
        "<svg xmlns='http://www.w3.org/2000/svg' width='400' height='200'>"
        "<defs><linearGradient id='g' x1='0' y1='0' x2='1' y2='1'>"
        f"<stop offset='0%' stop-color='{c1}'/>"
        f"<stop offset='100%' stop-color='{c2}'/>"
        "</linearGradient></defs>"
        "<rect width='400' height='200' fill='url(#g)'/></svg>"
    )
    return "data:image/svg+xml," + quote(svg, safe="")


# Цены по редкости для косметики (профильные рамки/фоны, персонализация ника).
# Откалибровано под ~10-20 игр/неделю на активного игрока (~3.5 монеты/игру
# в среднем) так, чтобы LEGENDARY копился ~5-8 месяцев органической игры, а
# не выкупался за первый же месяц. Мерч (физические товары) — отдельная,
# более высокая шкала ниже: у него есть реальная себестоимость для клуба.
COSMETIC_PRICE_BY_RARITY = {
    "common": 200.0,
    "rare": 500.0,
    "epic": 900.0,
    "legendary": 1500.0,
}

# Отдельная, более дорогая шкала для анимированных тематических эффектов
# (app/routes/admin_shop.py::THEMES — рамка/ник с настоящей CSS-анимацией,
# не плоский цвет). Три волны по цене: epic_wave (12 тем) < mythic
# (31 тема) < ultra (10 тем, переработаны на 3+ независимых слоя —
# самые дорогие и статусные товары в магазине). И рамка, и ник одной
# темы стоят одинаково — экипировка в любой слот одинаково "премиальна".
THEME_TIER_PRICE = {
    "epic_wave": 1800.0,
    "mythic": 2600.0,
    "ultra": 3800.0,
}


def _shop_items() -> list:
    """Единый источник правды для каталога магазина — используется и
    seed-shop (создание новых товаров), и update-shop-prices (обновление
    цены у уже существующих по имени)."""
    from app.models import ShopCategory, Rarity

    items = [
        # ── Рамки профиля (profile_customization:frame) ──────────────────────
        dict(
            name="Золотая рамка", category=ShopCategory.PROFILE_CUSTOMIZATION,
            subcategory="frame", rarity=Rarity.LEGENDARY, price=1500.0,
            description="Золотая рамка вокруг аватара.",
            data={"color": "#fbbf24"},
        ),
        dict(
            name="Серебряная рамка", category=ShopCategory.PROFILE_CUSTOMIZATION,
            subcategory="frame", rarity=Rarity.RARE, price=500.0,
            description="Серебряная рамка вокруг аватара.",
            data={"color": "#c0c0c0"},
        ),
        dict(
            name="Бронзовая рамка", category=ShopCategory.PROFILE_CUSTOMIZATION,
            subcategory="frame", rarity=Rarity.COMMON, price=200.0,
            description="Бронзовая рамка вокруг аватара.",
            data={"color": "#cd7f32"},
        ),
        dict(
            name="Рубиновая рамка", category=ShopCategory.PROFILE_CUSTOMIZATION,
            subcategory="frame", rarity=Rarity.EPIC, price=900.0,
            description="Рубиновая рамка вокруг аватара.",
            data={"color": "#e11d48"},
        ),
        dict(
            name="Изумрудная рамка", category=ShopCategory.PROFILE_CUSTOMIZATION,
            subcategory="frame", rarity=Rarity.EPIC, price=900.0,
            description="Изумрудная рамка вокруг аватара.",
            data={"color": "#10b981"},
        ),
        dict(
            name="Сапфировая рамка", category=ShopCategory.PROFILE_CUSTOMIZATION,
            subcategory="frame", rarity=Rarity.EPIC, price=900.0,
            description="Сапфировая рамка вокруг аватара.",
            data={"color": "#3b82f6"},
        ),
        dict(
            name="Аметистовая рамка", category=ShopCategory.PROFILE_CUSTOMIZATION,
            subcategory="frame", rarity=Rarity.EPIC, price=900.0,
            description="Аметистовая рамка вокруг аватара.",
            data={"color": "#a855f7"},
        ),
        dict(
            name="Огненная рамка", category=ShopCategory.PROFILE_CUSTOMIZATION,
            subcategory="frame", rarity=Rarity.LEGENDARY, price=1500.0,
            description="Ярко-оранжевая рамка вокруг аватара.",
            data={"color": "#ff6b35"},
        ),

        # ── Фоны профиля (profile_customization:background) ──────────────────
        dict(
            name='Тёмный фон "Ночь города"', category=ShopCategory.PROFILE_CUSTOMIZATION,
            subcategory="background", rarity=Rarity.EPIC, price=900.0,
            description="Атмосферный тёмный фон профиля.",
            data={"image_url": _gradient_bg("#0f172a", "#1e293b")},
        ),
        dict(
            name='Фон "Закат"', category=ShopCategory.PROFILE_CUSTOMIZATION,
            subcategory="background", rarity=Rarity.EPIC, price=900.0,
            description="Оранжево-красный градиентный фон профиля.",
            data={"image_url": _gradient_bg("#f97316", "#e03535")},
        ),
        dict(
            name='Фон "Океан"', category=ShopCategory.PROFILE_CUSTOMIZATION,
            subcategory="background", rarity=Rarity.RARE, price=500.0,
            description="Сине-голубой градиентный фон профиля.",
            data={"image_url": _gradient_bg("#0ea5e9", "#1e3a8a")},
        ),
        dict(
            name='Фон "Лес"', category=ShopCategory.PROFILE_CUSTOMIZATION,
            subcategory="background", rarity=Rarity.RARE, price=500.0,
            description="Зелёный градиентный фон профиля.",
            data={"image_url": _gradient_bg("#166534", "#4ade80")},
        ),
        dict(
            name='Фон "Космос"', category=ShopCategory.PROFILE_CUSTOMIZATION,
            subcategory="background", rarity=Rarity.LEGENDARY, price=1500.0,
            description="Глубокий фиолетово-чёрный фон профиля.",
            data={"image_url": _gradient_bg("#000000", "#4c1d95")},
        ),
        dict(
            name='Фон "Рассвет"', category=ShopCategory.PROFILE_CUSTOMIZATION,
            subcategory="background", rarity=Rarity.RARE, price=500.0,
            description="Розово-жёлтый градиентный фон профиля.",
            data={"image_url": _gradient_bg("#f472b6", "#fde047")},
        ),

        # ── Цвет ника (nickname:nick_color) ───────────────────────────────────
        dict(
            name="Ник цвета золота", category=ShopCategory.NICKNAME,
            subcategory="nick_color", rarity=Rarity.RARE, price=500.0,
            description="Никнейм окрашивается в золотой цвет.",
            data={"color": "#fbbf24"},
        ),
        dict(
            name="Ник цвета огня", category=ShopCategory.NICKNAME,
            subcategory="nick_color", rarity=Rarity.RARE, price=500.0,
            description="Никнейм окрашивается в огненно-красный цвет.",
            data={"color": "#ef4444"},
        ),
        dict(
            name="Ник цвета льда", category=ShopCategory.NICKNAME,
            subcategory="nick_color", rarity=Rarity.RARE, price=500.0,
            description="Никнейм окрашивается в ледяной голубой цвет.",
            data={"color": "#38bdf8"},
        ),
        dict(
            name="Ник цвета изумруда", category=ShopCategory.NICKNAME,
            subcategory="nick_color", rarity=Rarity.RARE, price=500.0,
            description="Никнейм окрашивается в изумрудный цвет.",
            data={"color": "#10b981"},
        ),
        dict(
            name="Ник цвета аметиста", category=ShopCategory.NICKNAME,
            subcategory="nick_color", rarity=Rarity.RARE, price=500.0,
            description="Никнейм окрашивается в фиолетовый цвет.",
            data={"color": "#a855f7"},
        ),
        dict(
            name="Ник цвета розового кварца", category=ShopCategory.NICKNAME,
            subcategory="nick_color", rarity=Rarity.COMMON, price=200.0,
            description="Никнейм окрашивается в нежно-розовый цвет.",
            data={"color": "#f472b6"},
        ),

        # ── Градиент ника (nickname:nick_gradient) ────────────────────────────
        dict(
            name='Градиент "Закат"', category=ShopCategory.NICKNAME,
            subcategory="nick_gradient", rarity=Rarity.EPIC, price=900.0,
            description="Градиентная раскраска никнейма.",
            data={"from": "#f97316", "to": "#e03535"},
        ),
        dict(
            name='Градиент "Океан"', category=ShopCategory.NICKNAME,
            subcategory="nick_gradient", rarity=Rarity.EPIC, price=900.0,
            description="Сине-фиолетовая градиентная раскраска никнейма.",
            data={"from": "#0ea5e9", "to": "#6366f1"},
        ),
        dict(
            name='Градиент "Огонь и лёд"', category=ShopCategory.NICKNAME,
            subcategory="nick_gradient", rarity=Rarity.LEGENDARY, price=1500.0,
            description="Контрастная красно-голубая раскраска никнейма.",
            data={"from": "#ef4444", "to": "#38bdf8"},
        ),
        dict(
            name='Градиент "Северное сияние"', category=ShopCategory.NICKNAME,
            subcategory="nick_gradient", rarity=Rarity.LEGENDARY, price=1500.0,
            description="Зелёно-фиолетовая раскраска никнейма.",
            data={"from": "#10b981", "to": "#a855f7"},
        ),
        dict(
            name='Градиент "Золото"', category=ShopCategory.NICKNAME,
            subcategory="nick_gradient", rarity=Rarity.RARE, price=500.0,
            description="Золотисто-янтарная раскраска никнейма.",
            data={"from": "#fbbf24", "to": "#f59e0b"},
        ),

        # ── Префикс ника (nickname:nick_prefix) ───────────────────────────────
        dict(
            name="Префикс ⭐ Звезда", category=ShopCategory.NICKNAME,
            subcategory="nick_prefix", rarity=Rarity.COMMON, price=200.0,
            description="Значок перед никнеймом.",
            data={"text": "⭐"},
        ),
        dict(
            name="Префикс 🔥 Огонь", category=ShopCategory.NICKNAME,
            subcategory="nick_prefix", rarity=Rarity.COMMON, price=200.0,
            description="Значок перед никнеймом.",
            data={"text": "🔥"},
        ),
        dict(
            name="Префикс 👑 Корона", category=ShopCategory.NICKNAME,
            subcategory="nick_prefix", rarity=Rarity.EPIC, price=900.0,
            description="Значок перед никнеймом.",
            data={"text": "👑"},
        ),
        dict(
            name="Префикс 💎 Бриллиант", category=ShopCategory.NICKNAME,
            subcategory="nick_prefix", rarity=Rarity.LEGENDARY, price=1500.0,
            description="Значок перед никнеймом.",
            data={"text": "💎"},
        ),
        dict(
            name="Префикс ☠️ Череп", category=ShopCategory.NICKNAME,
            subcategory="nick_prefix", rarity=Rarity.RARE, price=500.0,
            description="Значок перед никнеймом.",
            data={"text": "☠️"},
        ),

        # ── Суффикс ника (nickname:nick_suffix) ───────────────────────────────
        dict(
            name="Суффикс MVP", category=ShopCategory.NICKNAME,
            subcategory="nick_suffix", rarity=Rarity.RARE, price=500.0,
            description="Текст после никнейма.",
            data={"text": "MVP"},
        ),
        dict(
            name="Суффикс PRO", category=ShopCategory.NICKNAME,
            subcategory="nick_suffix", rarity=Rarity.COMMON, price=200.0,
            description="Текст после никнейма.",
            data={"text": "PRO"},
        ),
        dict(
            name="Суффикс GOD", category=ShopCategory.NICKNAME,
            subcategory="nick_suffix", rarity=Rarity.LEGENDARY, price=1500.0,
            description="Текст после никнейма.",
            data={"text": "GOD"},
        ),
        dict(
            name="Суффикс ⚡", category=ShopCategory.NICKNAME,
            subcategory="nick_suffix", rarity=Rarity.COMMON, price=200.0,
            description="Значок после никнейма.",
            data={"text": "⚡"},
        ),

        # ── Физический мерч (выдаётся вручную) ────────────────────────────────
        # Отдельная шкала, не по COSMETIC_PRICE_BY_RARITY — у мерча есть
        # реальная себестоимость для клуба, поэтому он в среднем дороже
        # чистой косметики той же формальной редкости.
        dict(
            name="Клубная футболка", category=ShopCategory.PHYSICAL,
            subcategory="merch", rarity=Rarity.COMMON, price=1800.0,
            description="Официальный мерч клуба. Выдаётся вручную администратором.",
            data={}, is_unique_purchase=False,
        ),
        dict(
            name="Клубное худи", category=ShopCategory.PHYSICAL,
            subcategory="merch", rarity=Rarity.RARE, price=3000.0,
            description="Официальный мерч клуба. Выдаётся вручную администратором.",
            data={}, is_unique_purchase=False,
        ),
        dict(
            name="Клубная кепка", category=ShopCategory.PHYSICAL,
            subcategory="merch", rarity=Rarity.COMMON, price=1200.0,
            description="Официальный мерч клуба. Выдаётся вручную администратором.",
            data={}, is_unique_purchase=False,
        ),
        dict(
            name="Клубная кружка", category=ShopCategory.PHYSICAL,
            subcategory="merch", rarity=Rarity.COMMON, price=900.0,
            description="Официальный мерч клуба. Выдаётся вручную администратором.",
            data={}, is_unique_purchase=False,
        ),
        dict(
            name="Стикерпак клуба", category=ShopCategory.PHYSICAL,
            subcategory="merch", rarity=Rarity.COMMON, price=400.0,
            description="Официальный мерч клуба. Выдаётся вручную администратором.",
            data={}, is_unique_purchase=False,
        ),
    ]

    # ── Анимированные тематические эффекты (рамка + ник на каждую тему) ────
    # Генерируются из THEMES вместо ручного перечисления 106 dict'ов —
    # THEMES/THEME_ULTRA/THEME_EPIC_WAVE в admin_shop.py остаются
    # единственным источником правды о том, какие темы вообще существуют.
    from app.routes.admin_shop import THEMES, THEME_ULTRA, THEME_EPIC_WAVE

    # Mythic/Ultra — не просто "дороже Legendary": это отдельные уровни
    # редкости (см. Rarity), которые ShopService трактует как ГЛОБАЛЬНО
    # уникальные предметы (один экземпляр на весь клуб, перекупаемый дороже
    # прежнего владельца — ShopService.buyout_item()). Обычные Legendary-
    # товары (Золотая рамка и т.п.) это правило не затрагивает.
    THEME_TIER_RARITY = {
        "epic_wave": Rarity.EPIC,
        "mythic": Rarity.MYTHIC,
        "ultra": Rarity.ULTRA,
    }

    for code, label in THEMES:
        if code in THEME_ULTRA:
            tier = "ultra"
        elif code in THEME_EPIC_WAVE:
            tier = "epic_wave"
        else:
            tier = "mythic"
        price = THEME_TIER_PRICE[tier]
        rarity = THEME_TIER_RARITY[tier]

        items.append(dict(
            name=f"Рамка «{label}»", category=ShopCategory.PROFILE_CUSTOMIZATION,
            subcategory="frame", rarity=rarity, price=price,
            description=f"Анимированная тематическая рамка профиля — {label}.",
            data={"theme": code},
        ))
        items.append(dict(
            name=f"Ник «{label}»", category=ShopCategory.NICKNAME,
            subcategory="nick_gradient", rarity=rarity, price=price,
            description=f"Анимированное тематическое оформление никнейма — {label}.",
            data={"theme": code},
        ))
        items.append(dict(
            name=f"Фон «{label}»", category=ShopCategory.PROFILE_CUSTOMIZATION,
            subcategory="background", rarity=rarity, price=price,
            description=f"Анимированный тематический фон профиля — {label}.",
            data={"theme": code},
        ))

    return items


@app.cli.command("seed-shop")
def seed_shop():
    """Seed ShopItem rows across all 3 categories. Re-run-safe.
    Subcategories match exactly what app/templates/profile/main.html reads
    from item.data — see profile_customization:{frame,background} and
    nickname:{nick_color,nick_gradient,nick_prefix,nick_suffix}."""
    from app.models import ShopItem

    items = _shop_items()
    with app.app_context():
        created = 0
        for spec in items:
            exists = db.session.query(ShopItem).filter_by(name=spec["name"]).first()
            if exists:
                continue
            data = spec.pop("data", {})
            is_unique = spec.pop("is_unique_purchase", True)
            item = ShopItem(**spec, is_unique_purchase=is_unique)
            item.data = data
            db.session.add(item)
            created += 1
        db.session.commit()
        print(f"OK: Seeded {created} shop items ({len(items) - created} already existed).")


@app.cli.command("update-shop-prices")
def update_shop_prices():
    """
    Обновляет ТОЛЬКО price у уже существующих ShopItem (сверяет по имени
    с _shop_items()) — seed-shop их пропускает, раз они уже есть, так что
    после правки цен в коде их нужно накатить этой командой отдельно.
    Ничего не создаёт и не трогает остальные поля (rarity/data/description).
    """
    from app.models import ShopItem

    items = _shop_items()
    with app.app_context():
        updated = 0
        unchanged = 0
        missing = []
        for spec in items:
            item = db.session.query(ShopItem).filter_by(name=spec["name"]).first()
            if not item:
                missing.append(spec["name"])
                continue
            if item.price != spec["price"]:
                print(f"  {spec['name']}: {item.price} -> {spec['price']}")
                item.price = spec["price"]
                updated += 1
            else:
                unchanged += 1
        db.session.commit()
        print(f"OK: обновлено цен {updated}, без изменений {unchanged}.")
        if missing:
            print(f"Не найдено в БД (запустите сначала seed-shop): {', '.join(missing)}")


@app.cli.command("seed-achievements")
def seed_achievements():
    """Seed example Achievement rows across all 9 categories. Re-run-safe.
    Each code (except 'founder') has a matching rule in
    app/services/achievement_rules.py."""
    from app.models import Achievement, AchievementCategory, AchievementTrigger, Rarity

    achievements = [
        # Games
        ("games_played_10", "Новичок", "Сыграно 10 завершённых игр.", "bi-controller",
         AchievementCategory.GAMES, Rarity.COMMON, AchievementTrigger.GAME, False),
        ("games_played_100", "Ветеран", "Сыграно 100 игр.", "bi-controller",
         AchievementCategory.GAMES, Rarity.RARE, AchievementTrigger.GAME, False),
        ("games_played_500", "Легенда стола", "Сыграно 500 игр.", "bi-controller",
         AchievementCategory.GAMES, Rarity.LEGENDARY, AchievementTrigger.GAME, False),
        # Wins
        ("wins_10", "Первые победы", "10 побед.", "bi-trophy",
         AchievementCategory.WINS, Rarity.COMMON, AchievementTrigger.GAME, False),
        ("wins_streak_5", "Не остановить", "5 побед подряд.", "bi-fire",
         AchievementCategory.WINS, Rarity.EPIC, AchievementTrigger.GAME, False),
        ("perfect_role_mafia_10", "Мастер мафии", "10 побед за мафию/дона.", "bi-mask",
         AchievementCategory.WINS, Rarity.RARE, AchievementTrigger.GAME, False),
        # Rating
        ("elo_1500", "Растущая звезда", "ELO ≥ 1500.", "bi-graph-up-arrow",
         AchievementCategory.RATING, Rarity.RARE, AchievementTrigger.GAME, False),
        ("elo_1800", "Элита", "ELO ≥ 1800.", "bi-graph-up-arrow",
         AchievementCategory.RATING, Rarity.EPIC, AchievementTrigger.GAME, False),
        ("top1_global", "Вершина рейтинга", "1-е место в общем рейтинге.", "bi-crown",
         AchievementCategory.RATING, Rarity.LEGENDARY, AchievementTrigger.GAME, True),
        # Tournaments
        ("tournament_win_1", "Чемпион", "1-е место в турнире.", "bi-trophy-fill",
         AchievementCategory.TOURNAMENTS, Rarity.EPIC, AchievementTrigger.TOURNAMENT, False),
        ("tournament_participant_10", "Завсегдатай турниров", "Участие в 10 турнирах.", "bi-people",
         AchievementCategory.TOURNAMENTS, Rarity.COMMON, AchievementTrigger.TOURNAMENT, False),
        # Seasons
        ("season_win_1", "Король сезона", "Победа в сезоне.", "bi-award",
         AchievementCategory.SEASONS, Rarity.LEGENDARY, AchievementTrigger.SEASON, False),
        ("season_top3_3", "Стабильность", "Топ-3 в 3 сезонах.", "bi-award",
         AchievementCategory.SEASONS, Rarity.RARE, AchievementTrigger.SEASON, False),
        # Fantasy
        ("fantasy_leaderboard_1", "Fantasy-гуру", "1-е место в fantasy-лидерборде турнира.", "bi-joystick",
         AchievementCategory.FANTASY, Rarity.EPIC, AchievementTrigger.TOURNAMENT, False),
        ("fantasy_participant_5", "Фэнтези-игрок", "Участие в 5 fantasy-драфтах.", "bi-joystick",
         AchievementCategory.FANTASY, Rarity.COMMON, AchievementTrigger.TOURNAMENT, False),
        # Economy
        ("coins_earned_1000", "Первая тысяча", "Заработано 1000 монет суммарно.", "bi-coin",
         AchievementCategory.ECONOMY, Rarity.COMMON, AchievementTrigger.GAME, False),
        ("coins_earned_10000", "Магнат", "Заработано 10000 монет суммарно.", "bi-coin",
         AchievementCategory.ECONOMY, Rarity.EPIC, AchievementTrigger.GAME, False),
        # Social
        ("shop_first_purchase", "Модник", "Первая покупка в магазине.", "bi-bag-heart",
         AchievementCategory.SOCIAL, Rarity.COMMON, AchievementTrigger.PURCHASE, False),
        ("account_linked", "Свой человек", "Привязал аккаунт к профилю игрока.", "bi-person-check",
         AchievementCategory.SOCIAL, Rarity.COMMON, AchievementTrigger.MANUAL, True),
        # Special
        ("founder", "Отец-основатель", "Выдаётся вручную администратором.", "bi-gem",
         AchievementCategory.SPECIAL, Rarity.LEGENDARY, AchievementTrigger.MANUAL, True),
    ]

    with app.app_context():
        created = 0
        for code, name, desc, icon, category, rarity, trigger, hidden in achievements:
            exists = db.session.query(Achievement).filter_by(code=code).first()
            if exists:
                continue
            db.session.add(Achievement(
                code=code, name=name, description=desc, icon=icon,
                category=category, rarity=rarity, trigger=trigger, is_hidden=hidden,
            ))
            created += 1
        db.session.commit()
        print(f"OK: Seeded {created} achievements ({len(achievements) - created} already existed).")


@app.cli.command("seed-titles")
def seed_titles():
    """Seed the 4 seasonal role titles + 5 global club titles. Re-run-safe.
    Codes must match app/services/nomination_service.py constants."""
    from app.models import Title, TitleType, Rarity

    titles = [
        # Сезонные (по ролям)
        ("season_best_civilian", "Лучший мирный сезона", "Лучший результат за роль мирного жителя в этом сезоне.",
         "bi-person-check", Rarity.RARE, TitleType.SEASONAL),
        ("season_best_sheriff", "Лучший шериф сезона", "Лучший результат за роль шерифа в этом сезоне.",
         "bi-search", Rarity.RARE, TitleType.SEASONAL),
        ("season_best_mafia", "Лучший мафиози сезона", "Лучший результат за роль мафии в этом сезоне.",
         "bi-mask", Rarity.RARE, TitleType.SEASONAL),
        ("season_best_don", "Лучший дон сезона", "Лучший результат за роль дона в этом сезоне.",
         "bi-crown", Rarity.EPIC, TitleType.SEASONAL),
        # Вечные (текущие рекордсмены клуба)
        ("club_legend", "Легенда клуба", "Максимальная сумма бонусных баллов, умноженная на общий винрейт.",
         "bi-gem", Rarity.LEGENDARY, TitleType.ETERNAL),
        ("streak_king", "Король серии", "Самая длинная победная серия за всю историю клуба.",
         "bi-fire", Rarity.EPIC, TitleType.ETERNAL),
        ("iron_player", "Железный игрок", "Больше всего сыгранных завершённых игр.",
         "bi-shield-fill", Rarity.RARE, TitleType.ETERNAL),
        ("mafia_terror", "Гроза мафии", "Лучший винрейт за город (мирный/шериф).",
         "bi-lightning-fill", Rarity.EPIC, TitleType.ETERNAL),
        ("dark_genius", "Тёмный гений", "Лучший винрейт за мафию (мафия/дон).",
         "bi-moon-stars-fill", Rarity.EPIC, TitleType.ETERNAL),
    ]

    with app.app_context():
        created = 0
        for code, name, desc, icon, rarity, ttype in titles:
            exists = db.session.query(Title).filter_by(code=code).first()
            if exists:
                continue
            db.session.add(Title(
                code=code, name=name, description=desc, icon=icon,
                rarity=rarity, type=ttype,
            ))
            created += 1
        db.session.commit()
        print(f"OK: Seeded {created} titles ({len(titles) - created} already existed).")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=app.config.get("DEBUG", False))