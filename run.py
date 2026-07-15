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

    # Точечные исключения из шкалы THEME_TIER_PRICE — для тем, которые
    # статуснее остальных ULTRA (например "admin", зарезервированная за
    # админской ролью), а не просто "ещё одна тема того же уровня".
    THEME_PRICE_OVERRIDE: dict[str, float] = {
        "admin": 10000.0,
    }

    for code, label in THEMES:
        if code in THEME_ULTRA:
            tier = "ultra"
        elif code in THEME_EPIC_WAVE:
            tier = "epic_wave"
        else:
            tier = "mythic"
        price = THEME_PRICE_OVERRIDE.get(code, THEME_TIER_PRICE[tier])
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


@app.cli.command("update-shop-rarity")
def update_shop_rarity():
    """
    Обновляет ТОЛЬКО rarity у уже существующих ShopItem (сверяет по имени
    с _shop_items()) — нужно после того, как в коде поменялась привязка
    темы к уровню редкости (появление Mythic/Ultra), чтобы уже созданные
    товары получили правильный уровень редкости задним числом.
    Ничего не создаёт и не трогает остальные поля (price/data/description).

    Mythic/Ultra — ГЛОБАЛЬНО уникальные предметы для ShopService (см.
    UNIQUE_RARITIES/get_current_owner в shop_service.py — не более одного
    владельца на весь клуб). Пока предмет был обычным is_unique_purchase
    (макс. 1 на игрока), его вполне могли купить НЕСКОЛЬКО разных игроков
    по отдельности. Если так — rarity для него НЕ трогается автоматически:
    печатается предупреждение, чтобы админ вручную решил, кто из
    владельцев остаётся (остальным — компенсация/удаление записи), не
    полагаясь молча на "единственного владельца", которого на самом деле
    ещё нет.
    """
    from app.models import ShopItem, InventoryItem, Rarity

    UNIQUE_RARITIES = {Rarity.MYTHIC, Rarity.ULTRA}
    items = _shop_items()
    with app.app_context():
        updated = 0
        unchanged = 0
        missing = []
        skipped_multi_owner = []
        for spec in items:
            item = db.session.query(ShopItem).filter_by(name=spec["name"]).first()
            if not item:
                missing.append(spec["name"])
                continue
            if item.rarity == spec["rarity"]:
                unchanged += 1
                continue
            if spec["rarity"] in UNIQUE_RARITIES:
                owners = (
                    db.session.query(InventoryItem).filter_by(item_id=item.id).count()
                )
                if owners > 1:
                    skipped_multi_owner.append((spec["name"], owners))
                    continue
            print(f"  {spec['name']}: {item.rarity.value} -> {spec['rarity'].value}")
            item.rarity = spec["rarity"]
            updated += 1
        db.session.commit()
        print(f"OK: обновлено редкости {updated}, без изменений {unchanged}.")
        if missing:
            print(f"Не найдено в БД (запустите сначала seed-shop): {', '.join(missing)}")
        if skipped_multi_owner:
            print("ПРОПУЩЕНО (у предмета больше 1 владельца — решите вручную перед переводом в Mythic/Ultra):")
            for name, count in skipped_multi_owner:
                print(f"  {name}: {count} владельцев")


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
        ("top1_global", "Вершина рейтинга", "1-е место в общем рейтинге.", "bi-award-fill",
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

        # ── Игры (доп.) ──────────────────────────────────────────────
        ("games_played_25", "Разминка окончена", "Сыграно 25 завершённых игр.", "bi-controller",
         AchievementCategory.GAMES, Rarity.COMMON, AchievementTrigger.GAME, False),
        ("games_played_50", "На волне", "Сыграно 50 завершённых игр.", "bi-controller",
         AchievementCategory.GAMES, Rarity.COMMON, AchievementTrigger.GAME, False),
        ("games_played_250", "Завсегдатай стола", "Сыграно 250 завершённых игр.", "bi-controller",
         AchievementCategory.GAMES, Rarity.RARE, AchievementTrigger.GAME, False),
        ("games_played_1000", "Тысяча партий", "Сыграно 1000 завершённых игр.", "bi-controller",
         AchievementCategory.GAMES, Rarity.LEGENDARY, AchievementTrigger.GAME, False),
        ("civilian_games_100", "Мирный житель", "Сыграно 100 игр за мирного жителя.", "bi-person-badge",
         AchievementCategory.GAMES, Rarity.RARE, AchievementTrigger.GAME, False),
        ("sheriff_games_50", "Страж порядка", "Сыграно 50 игр за шерифа.", "bi-shield-check",
         AchievementCategory.GAMES, Rarity.RARE, AchievementTrigger.GAME, False),
        ("don_games_50", "Хозяин ночи", "Сыграно 50 игр за дона.", "bi-suit-spade-fill",
         AchievementCategory.GAMES, Rarity.RARE, AchievementTrigger.GAME, False),
        ("mafia_games_100", "Тёмная сторона", "Сыграно 100 игр за мафию.", "bi-mask",
         AchievementCategory.GAMES, Rarity.RARE, AchievementTrigger.GAME, False),
        ("games_10_in_one_day", "Марафон", "10 завершённых игр за один день.", "bi-lightning-charge-fill",
         AchievementCategory.GAMES, Rarity.EPIC, AchievementTrigger.GAME, False),
        ("tenure_1_year", "Год в клубе", "В клубе минимум 1 год с первой игры.", "bi-calendar-heart",
         AchievementCategory.GAMES, Rarity.COMMON, AchievementTrigger.GAME, False),
        ("tenure_3_years", "Старожил", "В клубе минимум 3 года с первой игры.", "bi-calendar-heart-fill",
         AchievementCategory.GAMES, Rarity.EPIC, AchievementTrigger.GAME, False),

        # ── Победы (доп.) ─────────────────────────────────────────────
        ("win_streak_3", "Разогрев", "3 победы подряд.", "bi-fire",
         AchievementCategory.WINS, Rarity.RARE, AchievementTrigger.GAME, False),
        ("win_streak_10", "Не остановить", "10 побед подряд.", "bi-fire",
         AchievementCategory.WINS, Rarity.EPIC, AchievementTrigger.GAME, False),
        ("win_streak_15", "Огненная серия", "15 побед подряд.", "bi-fire",
         AchievementCategory.WINS, Rarity.LEGENDARY, AchievementTrigger.GAME, False),
        ("win_streak_20", "Неудержимый", "20 побед подряд.", "bi-fire",
         AchievementCategory.WINS, Rarity.LEGENDARY, AchievementTrigger.GAME, True),
        ("comeback_after_5_losses", "Возвращение", "Победа сразу после серии из 5 поражений подряд.", "bi-arrow-repeat",
         AchievementCategory.WINS, Rarity.EPIC, AchievementTrigger.GAME, False),
        ("win_rate_70_last_20", "На пике формы", "Винрейт от 70% за последние 20 игр.", "bi-graph-up",
         AchievementCategory.WINS, Rarity.EPIC, AchievementTrigger.GAME, False),
        ("sheriff_wins_50", "Меткий глаз", "50 побед за шерифа.", "bi-bullseye",
         AchievementCategory.WINS, Rarity.RARE, AchievementTrigger.GAME, False),
        ("sheriff_wins_100", "Гроза города", "100 побед за шерифа.", "bi-bullseye",
         AchievementCategory.WINS, Rarity.LEGENDARY, AchievementTrigger.GAME, False),
        ("don_wins_50", "Кукловод", "50 побед за дона.", "bi-suit-spade-fill",
         AchievementCategory.WINS, Rarity.RARE, AchievementTrigger.GAME, False),
        ("civilian_wins_50", "Голос города", "50 побед за мирного жителя.", "bi-megaphone",
         AchievementCategory.WINS, Rarity.RARE, AchievementTrigger.GAME, False),
        ("civilian_wins_100", "Совесть города", "100 побед за мирного жителя.", "bi-megaphone",
         AchievementCategory.WINS, Rarity.LEGENDARY, AchievementTrigger.GAME, False),
        ("best_move_5", "Лучший ход", "Признан лучшим ходом партии 5 раз.", "bi-star",
         AchievementCategory.WINS, Rarity.COMMON, AchievementTrigger.GAME, False),
        ("best_move_25", "Тактик", "Признан лучшим ходом партии 25 раз.", "bi-stars",
         AchievementCategory.WINS, Rarity.RARE, AchievementTrigger.GAME, False),
        ("best_move_100", "Гроссмейстер стола", "Признан лучшим ходом партии 100 раз.", "bi-stars",
         AchievementCategory.WINS, Rarity.LEGENDARY, AchievementTrigger.GAME, False),
        ("pu_perfect_call", "Идеальный расчёт", "Убит первым в ночь и назвал всех троих мафий верно.", "bi-crosshair",
         AchievementCategory.WINS, Rarity.EPIC, AchievementTrigger.GAME, False),

        # ── Рейтинг (доп.) ────────────────────────────────────────────
        ("elo_1200", "Уверенный старт", "ELO ≥ 1200.", "bi-graph-up-arrow",
         AchievementCategory.RATING, Rarity.COMMON, AchievementTrigger.GAME, False),
        ("elo_1300", "На подъёме", "ELO ≥ 1300.", "bi-graph-up-arrow",
         AchievementCategory.RATING, Rarity.COMMON, AchievementTrigger.GAME, False),
        ("elo_1600", "Крепкий игрок", "ELO ≥ 1600.", "bi-graph-up-arrow",
         AchievementCategory.RATING, Rarity.RARE, AchievementTrigger.GAME, False),
        ("elo_1700", "Мастер", "ELO ≥ 1700.", "bi-graph-up-arrow",
         AchievementCategory.RATING, Rarity.RARE, AchievementTrigger.GAME, False),
        ("elo_1900", "Элита клуба", "ELO ≥ 1900.", "bi-graph-up-arrow",
         AchievementCategory.RATING, Rarity.EPIC, AchievementTrigger.GAME, False),
        ("elo_2000", "Гроссмейстер", "ELO ≥ 2000.", "bi-graph-up-arrow",
         AchievementCategory.RATING, Rarity.LEGENDARY, AchievementTrigger.GAME, False),
        ("elo_2200", "Живая легенда", "ELO ≥ 2200.", "bi-graph-up-arrow",
         AchievementCategory.RATING, Rarity.LEGENDARY, AchievementTrigger.GAME, True),
        ("rank_top3_global", "Пьедестал", "Топ-3 общего рейтинга клуба.", "bi-award-fill",
         AchievementCategory.RATING, Rarity.EPIC, AchievementTrigger.GAME, False),
        ("rank_top5_global", "Высшая лига", "Топ-5 общего рейтинга клуба.", "bi-award",
         AchievementCategory.RATING, Rarity.RARE, AchievementTrigger.GAME, False),
        ("rank_top10_global", "Первая десятка", "Топ-10 общего рейтинга клуба.", "bi-award",
         AchievementCategory.RATING, Rarity.COMMON, AchievementTrigger.GAME, False),

        # ── Турниры (доп.) ────────────────────────────────────────────
        ("tournament_participant_5", "Турнирный боец", "Участие в 5 турнирах.", "bi-people",
         AchievementCategory.TOURNAMENTS, Rarity.COMMON, AchievementTrigger.TOURNAMENT, False),
        ("tournament_participant_25", "Турнирный волк", "Участие в 25 турнирах.", "bi-people-fill",
         AchievementCategory.TOURNAMENTS, Rarity.RARE, AchievementTrigger.TOURNAMENT, False),
        ("tournament_participant_50", "Ветеран турниров", "Участие в 50 турнирах.", "bi-people-fill",
         AchievementCategory.TOURNAMENTS, Rarity.EPIC, AchievementTrigger.TOURNAMENT, False),
        ("tournament_win_2", "Дважды чемпион", "Победа в 2 турнирах.", "bi-trophy-fill",
         AchievementCategory.TOURNAMENTS, Rarity.RARE, AchievementTrigger.TOURNAMENT, False),
        ("tournament_win_3", "Серийный победитель", "Победа в 3 турнирах.", "bi-trophy-fill",
         AchievementCategory.TOURNAMENTS, Rarity.EPIC, AchievementTrigger.TOURNAMENT, False),
        ("tournament_win_5", "Коллекционер кубков", "Победа в 5 турнирах.", "bi-trophy-fill",
         AchievementCategory.TOURNAMENTS, Rarity.LEGENDARY, AchievementTrigger.TOURNAMENT, False),
        ("tournament_top3_1", "На подиуме", "Топ-3 в турнире.", "bi-award",
         AchievementCategory.TOURNAMENTS, Rarity.COMMON, AchievementTrigger.TOURNAMENT, False),
        ("tournament_top3_5", "Постоянный призёр", "Топ-3 в турнире 5 раз.", "bi-award-fill",
         AchievementCategory.TOURNAMENTS, Rarity.RARE, AchievementTrigger.TOURNAMENT, False),
        ("tournament_flawless", "Безупречный турнир", "Победа во всех своих играх турнира.", "bi-gem",
         AchievementCategory.TOURNAMENTS, Rarity.LEGENDARY, AchievementTrigger.TOURNAMENT, False),
        ("tournament_advanced_final", "В финал!", "Прошёл отбор в финальную стадию турнира.", "bi-signpost-split-fill",
         AchievementCategory.TOURNAMENTS, Rarity.RARE, AchievementTrigger.TOURNAMENT, False),
        ("tournament_advanced_final_5", "Постоянный финалист", "Прошёл в финальную стадию турнира 5 раз.", "bi-signpost-split-fill",
         AchievementCategory.TOURNAMENTS, Rarity.EPIC, AchievementTrigger.TOURNAMENT, False),
        ("team_tournament_win", "Командный дух", "Победа в командном турнире.", "bi-people-fill",
         AchievementCategory.TOURNAMENTS, Rarity.EPIC, AchievementTrigger.TOURNAMENT, False),

        # ── Сезоны (доп.) ─────────────────────────────────────────────
        ("season_participant_5", "Сезонный игрок", "Участие в 5 сезонах.", "bi-calendar3",
         AchievementCategory.SEASONS, Rarity.COMMON, AchievementTrigger.SEASON, False),
        ("season_participant_10", "Календарь клуба", "Участие в 10 сезонах.", "bi-calendar3-range",
         AchievementCategory.SEASONS, Rarity.RARE, AchievementTrigger.SEASON, False),
        ("season_top3_1", "Призёр сезона", "Топ-3 сезона.", "bi-award",
         AchievementCategory.SEASONS, Rarity.COMMON, AchievementTrigger.SEASON, False),
        ("season_top3_5", "Стабильный результат", "Топ-3 сезона 5 раз.", "bi-award-fill",
         AchievementCategory.SEASONS, Rarity.EPIC, AchievementTrigger.SEASON, False),
        ("season_win_2", "Дважды король", "Победа в 2 сезонах.", "bi-award-fill",
         AchievementCategory.SEASONS, Rarity.RARE, AchievementTrigger.SEASON, False),
        ("season_win_3", "Династия", "Победа в 3 сезонах.", "bi-award-fill",
         AchievementCategory.SEASONS, Rarity.EPIC, AchievementTrigger.SEASON, False),
        ("season_win_5", "Император сезонов", "Победа в 5 сезонах.", "bi-award-fill",
         AchievementCategory.SEASONS, Rarity.LEGENDARY, AchievementTrigger.SEASON, True),
        ("season_win_consecutive_2", "Несменный чемпион", "Победа в сезоне два раза подряд, без перерыва.", "bi-repeat",
         AchievementCategory.SEASONS, Rarity.LEGENDARY, AchievementTrigger.SEASON, False),
        ("seasonal_title_sheriff", "Именной шериф", "Получен титул «Лучший шериф сезона».", "bi-search",
         AchievementCategory.SEASONS, Rarity.RARE, AchievementTrigger.SEASON, False),
        ("seasonal_title_don", "Именной дон", "Получен титул «Лучший дон сезона».", "bi-suit-spade-fill",
         AchievementCategory.SEASONS, Rarity.RARE, AchievementTrigger.SEASON, False),
        ("seasonal_title_mafia", "Именной мафиози", "Получен титул «Лучший мафиози сезона».", "bi-mask",
         AchievementCategory.SEASONS, Rarity.RARE, AchievementTrigger.SEASON, False),
        ("seasonal_title_civilian", "Именной мирный", "Получен титул «Лучший мирный сезона».", "bi-person-check",
         AchievementCategory.SEASONS, Rarity.RARE, AchievementTrigger.SEASON, False),
        ("seasonal_titles_all_roles", "Мастер на все роли", "Получены все 4 сезонных ролевых титула хотя бы раз за карьеру.", "bi-collection-fill",
         AchievementCategory.SEASONS, Rarity.LEGENDARY, AchievementTrigger.SEASON, False),
        ("season_reward_received", "Заслуженная награда", "Получена сезонная награда.", "bi-gift-fill",
         AchievementCategory.SEASONS, Rarity.COMMON, AchievementTrigger.SEASON, False),

        # ── Fantasy (доп.) ────────────────────────────────────────────
        ("fantasy_participant_10", "Фэнтези-энтузиаст", "Участие в 10 fantasy-драфтах.", "bi-joystick",
         AchievementCategory.FANTASY, Rarity.RARE, AchievementTrigger.TOURNAMENT, False),
        ("fantasy_participant_25", "Фэнтези-ветеран", "Участие в 25 fantasy-драфтах.", "bi-joystick",
         AchievementCategory.FANTASY, Rarity.EPIC, AchievementTrigger.TOURNAMENT, False),
        ("fantasy_leaderboard_top3_1", "Призовая тройка", "Топ-3 fantasy-лидерборда турнира.", "bi-award",
         AchievementCategory.FANTASY, Rarity.RARE, AchievementTrigger.TOURNAMENT, False),
        ("fantasy_leaderboard_top3_5", "Постоянный аналитик", "Топ-3 fantasy-лидерборда 5 раз.", "bi-award-fill",
         AchievementCategory.FANTASY, Rarity.EPIC, AchievementTrigger.TOURNAMENT, False),
        ("fantasy_leaderboard_win_3", "Fantasy-оракул", "Победа в fantasy-лидерборде 3 раза.", "bi-joystick",
         AchievementCategory.FANTASY, Rarity.LEGENDARY, AchievementTrigger.TOURNAMENT, False),
        ("fantasy_drafted_champion", "Чуйка на победителя", "Задрафтил будущего чемпиона турнира.", "bi-crosshair",
         AchievementCategory.FANTASY, Rarity.EPIC, AchievementTrigger.TOURNAMENT, False),
        ("fantasy_points_500", "Fantasy-стратег", "Набрано 500 fantasy-очков суммарно.", "bi-graph-up",
         AchievementCategory.FANTASY, Rarity.RARE, AchievementTrigger.TOURNAMENT, False),
        ("fantasy_points_2000", "Fantasy-гений", "Набрано 2000 fantasy-очков суммарно.", "bi-graph-up-arrow",
         AchievementCategory.FANTASY, Rarity.LEGENDARY, AchievementTrigger.TOURNAMENT, False),

        # ── Экономика (доп.) ──────────────────────────────────────────
        ("coins_earned_500", "Первые сбережения", "Заработано 500 монет суммарно.", "bi-coin",
         AchievementCategory.ECONOMY, Rarity.COMMON, AchievementTrigger.GAME, False),
        ("coins_earned_25000", "Крупный вкладчик", "Заработано 25000 монет суммарно.", "bi-cash-stack",
         AchievementCategory.ECONOMY, Rarity.EPIC, AchievementTrigger.GAME, False),
        ("coins_earned_50000", "Финансовый воротила", "Заработано 50000 монет суммарно.", "bi-cash-stack",
         AchievementCategory.ECONOMY, Rarity.LEGENDARY, AchievementTrigger.GAME, False),
        ("coins_earned_100000", "Клубный богач", "Заработано 100000 монет суммарно.", "bi-gem",
         AchievementCategory.ECONOMY, Rarity.LEGENDARY, AchievementTrigger.GAME, True),
        ("balance_10000", "На чёрный день", "Баланс от 10000 монет одновременно.", "bi-piggy-bank-fill",
         AchievementCategory.ECONOMY, Rarity.EPIC, AchievementTrigger.GAME, False),
        ("coins_spent_5000", "Любитель шоппинга", "Потрачено в магазине 5000 монет суммарно.", "bi-bag-check-fill",
         AchievementCategory.ECONOMY, Rarity.RARE, AchievementTrigger.PURCHASE, False),
        ("coins_spent_20000", "Модный магнат", "Потрачено в магазине 20000 монет суммарно.", "bi-bag-heart-fill",
         AchievementCategory.ECONOMY, Rarity.EPIC, AchievementTrigger.PURCHASE, False),
        ("owns_physical_merch", "Часть клуба", "Приобретён физический мерч клуба.", "bi-box-seam-fill",
         AchievementCategory.ECONOMY, Rarity.RARE, AchievementTrigger.PURCHASE, False),

        # ── Социальные / магазин (доп.) ───────────────────────────────
        ("inventory_5_items", "Коллекционер", "Владеет 5 предметами одновременно.", "bi-collection",
         AchievementCategory.SOCIAL, Rarity.COMMON, AchievementTrigger.PURCHASE, False),
        ("inventory_10_items", "Гардеробная", "Владеет 10 предметами одновременно.", "bi-collection-fill",
         AchievementCategory.SOCIAL, Rarity.RARE, AchievementTrigger.PURCHASE, False),
        ("inventory_20_items", "Витрина магазина", "Владеет 20 предметами одновременно.", "bi-collection-fill",
         AchievementCategory.SOCIAL, Rarity.EPIC, AchievementTrigger.PURCHASE, False),
        ("owns_all_rarities", "Полный набор", "Владеет хотя бы одним предметом каждой редкости.", "bi-gem",
         AchievementCategory.SOCIAL, Rarity.LEGENDARY, AchievementTrigger.PURCHASE, False),
        ("full_outfit_equipped", "Полный образ", "Экипирован полный образ: рамка, фон, цвет ника, префикс и суффикс одновременно.", "bi-person-vcard-fill",
         AchievementCategory.SOCIAL, Rarity.EPIC, AchievementTrigger.PURCHASE, False),
        ("gift_sent_1", "Щедрая душа", "Отправлен первый подарок другому игроку.", "bi-gift",
         AchievementCategory.SOCIAL, Rarity.COMMON, AchievementTrigger.PURCHASE, False),
        ("gift_sent_10", "Дед Мороз клуба", "Отправлено 10 подарков.", "bi-gift-fill",
         AchievementCategory.SOCIAL, Rarity.RARE, AchievementTrigger.PURCHASE, False),
        ("gift_received_10", "Любимец клуба", "Получено 10 подарков.", "bi-heart-fill",
         AchievementCategory.SOCIAL, Rarity.RARE, AchievementTrigger.PURCHASE, False),
        ("owns_unique_item", "Обладатель редкости", "Владеет уникальным товаром редкости Mythic или Ultra.", "bi-gem",
         AchievementCategory.SOCIAL, Rarity.EPIC, AchievementTrigger.PURCHASE, False),
        ("profile_complete", "Визитная карточка", "Заполнены аватар и описание профиля.", "bi-person-lines-fill",
         AchievementCategory.SOCIAL, Rarity.COMMON, AchievementTrigger.GAME, False),
        ("shop_all_categories", "Всесторонний покупатель", "Куплены товары из всех категорий магазина.", "bi-shop",
         AchievementCategory.SOCIAL, Rarity.RARE, AchievementTrigger.PURCHASE, False),
        ("pinned_first_achievement", "На видном месте", "Закреплено первое достижение на профиле.", "bi-pin-angle-fill",
         AchievementCategory.SOCIAL, Rarity.COMMON, AchievementTrigger.MANUAL, False),

        # ── Специальные / мета (доп.) ─────────────────────────────────
        ("achievements_unlocked_10", "Коллекция растёт", "Разблокировано 10 достижений.", "bi-trophy",
         AchievementCategory.SPECIAL, Rarity.COMMON, AchievementTrigger.GAME, False),
        ("achievements_unlocked_25", "Охотник за достижениями", "Разблокировано 25 достижений.", "bi-trophy-fill",
         AchievementCategory.SPECIAL, Rarity.RARE, AchievementTrigger.GAME, False),
        ("achievements_unlocked_40", "Мастер достижений", "Разблокировано 40 достижений.", "bi-trophy-fill",
         AchievementCategory.SPECIAL, Rarity.EPIC, AchievementTrigger.GAME, False),
        ("achievements_unlocked_60", "Полное собрание", "Разблокировано 60 достижений.", "bi-gem",
         AchievementCategory.SPECIAL, Rarity.LEGENDARY, AchievementTrigger.GAME, True),
        ("category_complete_games", "Знаток игр", "Разблокированы все достижения категории «Игры».", "bi-controller",
         AchievementCategory.SPECIAL, Rarity.EPIC, AchievementTrigger.GAME, False),
        ("category_complete_wins", "Знаток побед", "Разблокированы все достижения категории «Победы».", "bi-trophy-fill",
         AchievementCategory.SPECIAL, Rarity.EPIC, AchievementTrigger.GAME, False),
        ("category_complete_tournaments", "Знаток турниров", "Разблокированы все достижения категории «Турниры».", "bi-award-fill",
         AchievementCategory.SPECIAL, Rarity.EPIC, AchievementTrigger.TOURNAMENT, False),
        ("veteran_2y_500g", "Ветеран клуба", "В клубе от 2 лет и сыграно от 500 игр.", "bi-shield-fill-check",
         AchievementCategory.SPECIAL, Rarity.LEGENDARY, AchievementTrigger.GAME, False),
        ("legend_combo", "Легенда", "Одновременно ELO ≥1800, топ-3 общего рейтинга и хотя бы одна победа в турнире.", "bi-crown-fill",
         AchievementCategory.SPECIAL, Rarity.LEGENDARY, AchievementTrigger.GAME, True),
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
         "bi-suit-spade-fill", Rarity.EPIC, TitleType.SEASONAL),
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