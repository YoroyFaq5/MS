# 🃏 MafiaTracker — Patch Notes

## [Progression Layer] — 2026-07-02

Крупное обновление: клуб получил экономику с реальным применением (магазин),
долгосрочные цели помимо винрейта (достижения, титулы), полностью новый
профиль игрока с графиками и социальной аналитикой, и систему подарков.

Всего добавлено: **11 новых моделей**, **10 новых сервисов**, **8 новых
Blueprint'ов**, **~35 новых шаблонов**, **3 файла миграций**. Ни один
существующий route/service не переписан — только аддитивные изменения
поверх текущей архитектуры (Service Layer → thin routes, `PermissionService`
как единственная точка проверки прав, `Result`-датаклассы вместо исключений).

Работа разбита на 6 последовательных блоков (каждый зависит от предыдущего);
ниже они описаны в том же порядке.

---

## 1. Магазин, Инвентарь, Достижения, Новый профиль

### Магазин (`/shop`, `/admin/shop`)
- **`ShopItem`** — товар с категорией (`profile_customization` / `nickname` /
  `physical`), подкатегорией (= слот экипировки, свободная строка — новые
  слоты не требуют изменений кода), редкостью, ценой, JSON-полем `data` для
  косметического эффекта (цвет, градиент, CSS-класс рамки и т.д. — тот же
  паттерн, что `TournamentParticipant.meta`).
- **`InventoryItem`** — купленный/выданный экземпляр товара у игрока
  (снимок цены на момент покупки, флаг экипировки, источник — покупка /
  выдача админом / подарок).
- `ShopService`: `list_items`, `purchase` (списывает монеты через
  существующий `EconomyService`, не дублирует логику баланса),
  `get_inventory`, `get_equipped` (один запрос, слот = `category:subcategory`),
  `equip_item`/`unequip_item` (экипировка нового предмета в слоте
  автоматически снимает предыдущий), `validate_purchase`.
- `AdminShopService`: создание/редактирование/деактивация товаров,
  ручная выдача игроку с указанием причины.
- Категория `PHYSICAL` (кружки, футболки, сертификаты, билеты) — покупка
  только списывает монеты, выдача полностью ручная, вне приложения.

### Достижения (`/profile/<id>/achievements`, `/admin/shop/achievements`)
- **`Achievement`** — презентационные данные (название, описание, иконка,
  редкость, категория из 9: игры/победы/рейтинг/турниры/сезоны/fantasy/
  экономика/социальные/специальные, флаг «скрытое»), связаны с правилом
  разблокировки через уникальный `code`.
- **`PlayerAchievement`** — факт разблокировки, `pinned`/`pinned_order` для
  закрепления до 3 достижений рядом с ником.
- `app/services/achievement_rules.py` — реестр правил (Open/Closed): новое
  достижение = одна запись в реестре + одна строка в БД с тем же кодом,
  диспетчер (`AchievementService`) никогда не меняется.
- `AchievementService`: `unlock()` (идемпотентно — pre-check перед INSERT),
  `check_after_game/tournament/season()`, `check_after_purchase()`,
  `get_all_with_unlock_status()` (2 запроса, не N+1; скрытые+незаблокированные
  достижения отдаются как «???»), `pin()`/`unpin()`, `admin_grant()`.
- Засеяно 20 примеров достижений (`flask seed-achievements`) на все 9
  категорий.

### Новый профиль (`/profile/<player_id>`)
- Заменяет старые `/players/<id>/stats` и `/auth/profile` (оба стали
  редирект-заглушками — старые ссылки и закладки продолжают работать).
- Доступен для просмотра **любого** игрока, не только своего.
- Главная страница — дешёвая (~5 запросов): аватар, экипированное
  оформление, до 3 закреплённых достижений, монеты, место в общем рейтинге.
- `/profile/<id>/statistics` — тяжёлая подстраница: полная статистика,
  разбивка по ролям, напарники, турниры, fantasy, графики (см. ниже).
- `/profile/<id>/achievements` — все достижения (получено/не получено/скрыто),
  процент выполнения, закрепление.
- `/profile/<id>/customization` — просмотр экипированного оформления
  (управление — на странице `/inventory`).
- `ProfileService` расширен методами `get_profile`, `get_statistics`,
  `get_role_statistics`, `get_partner_statistics`, `get_inventory`,
  `get_achievements`, `get_profile_customization`, `get_tournament_summary`,
  `get_fantasy_summary` — существующие методы (`get_extended_stats`,
  `head_to_head` и др.) не тронуты.

### Права доступа
Новые `Permission`: `VIEW_SHOP`, `PURCHASE_ITEM`, `EQUIP_ITEM`,
`MANAGE_SHOP_ITEMS`, `VIEW_ACHIEVEMENTS`, `PIN_ACHIEVEMENT`,
`MANAGE_ACHIEVEMENTS` — добавлены в `PermissionService` тем же способом,
что и существующие группы (Economy, Fantasy).

### Миграция
Все 4 таблицы новые → подхватываются `flask init-db` (`db.create_all()`),
ALTER TABLE не требуется.

---

## 2. Титулы и номинации

### Модели и сервисы
- **`Title`** (определение: код, название, редкость, тип —
  `SEASONAL`/`ETERNAL`/`MANUAL`) + **`PlayerTitle`** (факт награды, слот
  экипировки — **только один титул одновременно**, мягкий отзыв `revoked`
  по аналогии с `GG.revoked`).
- `TitleService` — хранение/выдача/экипировка/отзыв, включая
  `get_equipped_titles_bulk()` для лидербордов без N+1.
- `NominationService` (отдельно от `TitleService` — та же логика разделения,
  что у `RatingService`/`SeasonRatingEngine`/`GGService`):
  - **Сезонные номинации по ролям**: «Лучший мирный/шериф/мафиози/дон
    сезона» — формула `role_bonus_points_sum × WR_роли`, постоянный
    исторический факт, не пересчитывается повторно.
  - **«Вечные» титулы клуба** («Легенда клуба», «Король серии», «Железный
    игрок», «Гроза мафии», «Тёмный гений») — модель «текущий рекордсмен»:
    при пересчёте, если рекорд сменился, старый обладатель лишается титула,
    новый — получает (не автоэкипируется). Порог от шума — минимум 10 игр.

### Где отображается
Рядом с ником в профиле, на главной странице («Титулы клуба»), в таблицах
лидеров (рейтинг + турнирный лидерборд, bulk-запрос без N+1), на странице
сезона («Номинации сезона»), отдельная страница `/titles/nominations`
(текущие держатели + лидеры активного сезона + история прошлых сезонов).

### Интеграция
Хук `NominationService.compute_seasonal_role_nominations()` добавлен в оба
пути закрытия сезона (`SeasonService._close_season` и `resolve_tiebreak`),
сразу после существующего вызова `AchievementService.check_after_season()`.

### Права и админка
Новые `Permission`: `VIEW_TITLES`, `EQUIP_TITLE`, `MANAGE_TITLES`.
`/admin/titles` — ручная выдача/отзыв титулов, пересчёт номинаций по
конкретному сезону, полный пересчёт «вечных» титулов.

### Миграция
2 новые таблицы → `flask init-db`. Засеяно 9 определений титулов
(`flask seed-titles`).

---

## 3. Визуализация истории матчей (Chart.js)

### Схема
Добавлено **`GameSlot.elo_after`** (nullable Float) — снимок ELO сразу
после матча. Раньше хранился только текущий `Player.elo`, без истории —
построить график изменения рейтинга было невозможно. `EloEngine.apply_match()`
получил одну дополнительную строку (`slot.elo_after = d.new_elo`), сам
движок не переписан.

⚠️ Это ALTER TABLE к уже существующей таблице `game_slots` — требует
запуска `migrate_elo_history.py` (см. раздел «Как накатить обновление»).
Игры, сыгранные до миграции, просто не дадут точку на графике ELO — это
ожидаемо, не баг.

### Новый сервис
`ChartDataService` — отдельно от `ProfileService` (чтобы тот не разросся в
god-service), только формирует датасеты, переиспользуя существующие методы
(`ProfileService.get_role_statistics`, `EconomyService.get_history`), без
дублирования агрегирующей логики:
- `get_elo_history()` — линия ELO по времени.
- `get_role_timeline()` — последние игры, цвет = роль, рамка = победа/поражение.
- `get_streak_timeline()` — кумулятивная серия побед/поражений.
- `get_role_performance()` — WR и средние баллы по ролям.
- `get_economy_timeline()` — баланс + заработано/потрачено по времени.

### Где отображается
5 графиков на `/profile/<id>/statistics`, секция «Графики». Chart.js
подключён через CDN (`cdn.jsdelivr.net`, как и Bootstrap/Icons) — без
сборки, без SPA, данные сериализуются через `| tojson` в инлайн-скрипт.

---

## 4. Соперничество / социальный слой

Общий агрегирующий запрос `get_partner_statistics()` вынесен в приватный
`ProfileService._compute_partner_aggregates()` — тот же O(games), 2-запросный
подход, теперь ещё и с учётом конкретной роли на каждом ходу (нужно для
дуэтов мафии и связки шериф-дон). Один и тот же расчёт переиспользуют и
старый метод, и новый — бизнес-логика не задублирована.

Новый **`ProfileService.get_rivalry_statistics()`** — без единого лишнего
запроса поверх общего агрегата:
- **Немезида** / **любимая жертва** — лучший/худший WR против конкретного
  соперника.
- **Лучший/худший тиммейт по WR** — в отличие от «лучшего напарника» из
  блока 1 (там ранжирование по числу побед/поражений), здесь именно процент.
- **Дуэт мафии** — самый частый напарник по мафии/дону + совместный WR.
- **Шериф vs Дон** — самый частый оппонент в связке ролей + WR в этой связке.
- Порог `min_shared_games` (по умолчанию 3) отсекает случайные пары от шума
  во всех вышеперечисленных метриках.

Блок «⚔️ Соперничество» добавлен на `/profile/<id>/statistics` — новых
роутов не потребовалось.

---

## 5. Магазин подарков

### Схема
- `ShopItem.is_transferable` (можно ли вообще дарить) и
  `ShopItem.giftable_message` (можно ли прикладывать личное сообщение) —
  ALTER TABLE к существующей таблице `shop_items`
  (`migrate_gifting.py`).
- **`GiftTransfer`** (новая таблица) — лог передачи: от кого, кому, какой
  предмет, сообщение, `seen` (флаг для бейджа непрочитанных).

### Модель передачи
Подарок **мгновенный**, без pending/accept-состояния — владение
`InventoryItem.player_id` меняется сразу в `GiftService.send_gift()`.
"Уведомление о подарке" = счётчик непрочитанных + страница входящих,
читаются при обычной загрузке страницы (тот же паттерн, что существующий
`#nav-coins` в `base.html`) — никакого websocket.

### `GiftService`
`send_gift()` проверяет: владение предметом, что предмет **не экипирован**
(жёсткая ошибка валидации, а не автоснятие), `is_transferable`, что
сообщение разрешено только если `giftable_message`, что получатель
существует/активен/не сам отправитель. Плюс `get_incoming_gifts`,
`get_transfer_history`, `mark_seen`, `get_unseen_count`,
и отдельный админский `get_all_transfers`.

### Где отображается
Кнопка «Подарить» в `/inventory` (скрыта для экипированных и
нетрансферабельных предметов), `/gifts/incoming`, `/gifts/history`, бейдж
непрочитанных подарков в навбаре.

---

## 6. Клубная аналитика для админов

Новый **`AdminAnalyticsService`** — клубная (не персональная) аналитика,
отдельно от `ProfileService`/`GiftService`:
- `get_top_rivalries()` — самые частые пары игроков за всю историю клуба
  (порог от шума — минимум 2 совместные игры).
- `get_most_gifted_items()` — самые часто дарёные товары.

`/admin/analytics/social` и `/admin/analytics/gifts` (пагинация) —
основная админ-функциональность (ручная выдача/отзыв титулов и достижений,
пересчёт номинаций) была доставлена ещё в блоках 1 и 2, здесь только
недостающие read-only обзорные страницы.

---

## Изменённые существующие файлы

| Файл | Что изменилось |
|---|---|
| `app/models/__init__.py` | +11 моделей/enum'ов, +3 колонки к существующим таблицам |
| `app/services/permission_service.py` | +12 прав доступа (Shop/Achievements/Titles) |
| `app/services/__init__.py` | Регистрация 8 новых сервисов |
| `app/services/orchestrator.py` | +вызов `AchievementService.check_after_game/tournament()` |
| `app/services/season_service.py` | +вызов `AchievementService.check_after_season()` и `NominationService.compute_seasonal_role_nominations()` в обоих путях закрытия сезона |
| `app/services/elo_engine.py` | +1 строка (`slot.elo_after = d.new_elo`) в обоих циклах `apply_match()` |
| `app/services/profile_service.py` | +9 новых методов, рефакторинг общей агрегации напарников в приватный helper |
| `app/routes/players.py`, `app/routes/auth.py` | `player_stats`/`profile` стали редирект-заглушками на новый `/profile` |
| `app/routes/main.py`, `ratings.py`, `tournaments.py`, `seasons.py` | +данные для бейджей титулов/номинаций |
| `app/routes/api.py` | +`GET /api/gifts/unseen-count`, +`GET /api/players/<id>/achievements` |
| `app/templates/base.html` | +пункты навигации (Магазин, Номинации, Инвентарь, Подарки, 3 админ-раздела), +бейдж непрочитанных подарков |
| `run.py` | +CLI-команды `seed-shop`, `seed-achievements`, `seed-titles`; исправлен `seed_players` (не задавал `Player.name`) и Unicode-краш эмодзи `✅` на Windows-консоли |

## Новые файлы

**Сервисы**: `shop_service.py`, `admin_shop_service.py`, `achievement_rules.py`,
`achievement_service.py`, `title_service.py`, `nomination_service.py`,
`chart_data_service.py`, `gift_service.py`, `admin_analytics_service.py`.

**Роуты**: `shop.py`, `inventory.py`, `profile.py`, `admin_shop.py`,
`titles.py`, `admin_titles.py`, `gifts.py`, `admin_analytics.py`.

**Шаблоны**: директории `shop/`, `inventory/`, `admin_shop/`, `profile/`,
`titles/`, `admin_titles/`, `gifts/`, `admin_analytics/`.

**Миграции**: `migrate_elo_history.py`, `migrate_gifting.py`.

---

## Как накатить обновление

```bash
# 1. Новые таблицы (Shop/Achievements/Titles/Gifts) — идемпотентно
flask --app run.py init-db

# 2. ALTER TABLE к уже существующим таблицам — обязательно, если БД не пустая
python migrate_elo_history.py     # game_slots.elo_after
python migrate_gifting.py         # shop_items.is_transferable/giftable_message + gift_transfers

# 3. (Опционально) базовые данные
flask --app run.py seed-shop
flask --app run.py seed-achievements
flask --app run.py seed-titles
```

Все `seed-*` и `migrate_*` команды безопасны для повторного запуска.

---

## Обратная совместимость

- `/players/<id>/stats` и `/auth/profile` продолжают работать — редиректят
  на новый `/profile/<id>`.
- Ни один существующий route, service-метод или шаблон не переписан —
  только новые методы/файлы и точечные аддитивные правки (хуки в
  оркестраторе, новые пункты меню).
- Игры, сыгранные до обновления, полноценно участвуют во всей новой
  статистике, достижениях, номинациях и титулах — эти расчёты используют
  `bonus_score`/`win_side`/роль, не `elo_after`. Единственное, чего не будет
  у старых игр — точки на графике ELO (см. блок 3): `elo_after` начинает
  записываться только с момента миграции.

## Известные ограничения (осознанные компромиссы, не баги)

- Уникальность покупки (`InventoryItem.is_unique_purchase`) проверяется на
  уровне сервиса, не БД-constraint'ом — тот же уровень доверия, что у
  существующего `TeamPlayer` («enforced via app logic»).
- Правила достижений — по одному лёгкому запросу на правило на игрока за
  хук; клубный масштаб это выдерживает, при росте числа правил — кандидат
  на батчинг.
- `get_tournament_summary`/`get_fantasy_summary` в профиле пересчитываются
  «на лету» по всем турнирам/драфтам игрока при каждом заходе на
  `/statistics` — README отмечает это как первую точку для будущего
  кэширования, если объём данных вырастет.
- `AdminAnalyticsService.get_top_rivalries()` строит все пары игроков по
  каждой игре в памяти (C(10,2)=45 пар/игру) — приемлемо для редкой
  admin-only страницы при клубных объёмах, не рассчитано на десятки тысяч игр.
