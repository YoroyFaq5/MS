import os
from datetime import datetime
from app import create_app, db

app = create_app(os.environ.get("FLASK_ENV", "default"))


@app.context_processor
def inject_now():
    return {"now": datetime.utcnow()}


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


@app.cli.command("seed-shop")
def seed_shop():
    """Seed example ShopItem rows across all 3 categories. Re-run-safe."""
    from app.models import ShopItem, ShopCategory, Rarity

    items = [
        dict(
            name="Золотая рамка", category=ShopCategory.PROFILE_CUSTOMIZATION,
            subcategory="frame", rarity=Rarity.LEGENDARY, price=500.0,
            description="Золотая рамка вокруг аватара.",
            data={"color": "#fbbf24"},
        ),
        dict(
            name='Тёмный фон "Ночь города"', category=ShopCategory.PROFILE_CUSTOMIZATION,
            subcategory="background", rarity=Rarity.EPIC, price=300.0,
            description="Атмосферный фон профиля.",
            data={"image_url": ""},
        ),
        dict(
            name="Ник цвета золота", category=ShopCategory.NICKNAME,
            subcategory="nick_color", rarity=Rarity.RARE, price=150.0,
            description="Никнейм окрашивается в золотой цвет.",
            data={"color": "#fbbf24"},
        ),
        dict(
            name='Градиент "Закат"', category=ShopCategory.NICKNAME,
            subcategory="nick_gradient", rarity=Rarity.EPIC, price=250.0,
            description="Градиентная раскраска никнейма.",
            data={"from": "#f97316", "to": "#e03535"},
        ),
        dict(
            name="Клубная футболка", category=ShopCategory.PHYSICAL,
            subcategory="merch", rarity=Rarity.COMMON, price=1000.0,
            description="Официальный мерч клуба. Выдаётся вручную администратором.",
            data={}, is_unique_purchase=False,
        ),
    ]

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