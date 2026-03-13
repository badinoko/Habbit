# Statistics v2: PR Plan

Дата фиксации: 13 марта 2026
Статус: agreed scope for implementation

## 1. Цель

Реализовать отдельную страницу `/stats`, которая расширяет текущую `Statistics v1` из сайдбара и показывает пользователю понятную сводку по задачам, привычкам и темам.

Документ нужен как рабочий чеклист для следующих сессий и PR-итераций.

## 2. Текущее состояние проекта

Уже есть:
- базовые агрегаты для сайдбара в `src/utils.py -> get_stats`;
- статистика задач в `src/services/tasks.py -> get_task_statistics`;
- статистика привычек в `src/services/habits.py -> get_habit_statistics`;
- ссылка "Статистика" пока ведет на заглушку `/soon` в `src/main.py`;
- текущий sidebar выводится в `src/templates/base.html`.

Ограничения текущей модели:
- у задач есть `created_at` и `completed_at`, но нет полноценной истории смен статусов;
- у привычек есть история выполнений через `habit_completions`, поэтому аналитика по привычкам может быть глубже;
- текущая статистика задач по темам считает `theme_id`, а не человекочитаемые имена тем, это нужно исправить для новой страницы.

## 3. Согласованный scope `Statistics v2`

### 3.1 Что войдет в `v1`

Верхняя сводка:
- активные задачи;
- выполненные задачи;
- всего привычек;
- активные привычки;
- привычки на сегодня;
- выполнено сегодня;
- текущий `success rate`.

Задачи:
- `completion_rate`;
- разбивка по приоритетам;
- разбивка по темам;
- создано за `7d`;
- создано за `30d`;
- завершено за `7d`;
- завершено за `30d`;
- среднее время до выполнения задачи.

Привычки:
- `success_rate` за `7d` и `30d`;
- daily trend выполнений за выбранный период;
- топ привычек по текущей серии;
- распределение по типам расписания;
- активные vs архивные;
- топ тем по активным привычкам.

Темы:
- самая загруженная тема по активным задачам;
- топ тем по числу задач;
- топ тем по числу привычек.

Инсайты:
- осталось привычек на сегодня;
- лучшая текущая серия;
- самая загруженная тема.

### 3.2 Что не входит в `v1`

- экспорт статистики;
- аналитика авторизации и сессий;
- сравнение пользователей между собой;
- графики с тяжелой frontend-библиотекой;
- полная event-history аналитика задач;
- отдельный JSON API под статистику, если он не нужен для web-страницы прямо сейчас.

## 4. Принципы реализации

- Не ломать текущую `Statistics v1` в сайдбаре.
- Page-level статистику собирать отдельно от sidebar-агрегатов.
- Держать шаблон простым: сложные вычисления должны жить в сервисах, а не в Jinja.
- Для `range` использовать только `7d | 30d`.
- Если query-параметр не передан, по умолчанию использовать `7d`.
- Все агрегаты считаются в рамках текущего пользователя (`owner-scoped`).
- Все блоки должны иметь аккуратные empty states.

## 5. Рекомендуемая структура кода

Рекомендуемый вариант для реализации:

- `src/routers/stats.py`
  Новый web-router для страницы `/stats`.

- `src/services/statistics.py`
  Новый page-composer сервис, который собирает данные задач, привычек и тем в единый context.

- `src/schemas/statistics.py`
  Новые Pydantic-схемы для page-level статистики.

- `src/templates/stats/stats_page.html`
  Новый шаблон страницы статистики.

- `tests/unit/test_statistics_service.py`
  Unit-тесты для page-composer и инсайтов.

- `tests/api_unit/test_stats_router_unit.py`
  Router-level тесты контракта страницы.

- `tests/integration/test_stats.py`
  Интеграционные тесты на реальные данные пользователя.

Важно:
- существующий `Stats` в `src/schemas/base.py` оставить как sidebar-модель;
- page-level схемы вынести в новый модуль, чтобы не смешивать два разных контракта;
- `src/main.py` должен только подключить новый router и перестать быть точкой входа для `/soon`.

## 6. Предлагаемый контракт page-level схем

Рекомендуемые сущности:

- `StatsRange = Literal["7d", "30d"]`
- `StatsKpi`
- `TaskStatisticsPage`
- `HabitStatisticsPage`
- `ThemeStatisticsPage`
- `StatsInsight`
- `StatisticsPageData`

Минимальный состав:

- `StatsKpi`
  Поля: `key`, `label`, `value`, `hint`

- `TaskStatisticsPage`
  Поля: `total`, `active`, `completed`, `completion_rate`, `by_priority`, `by_theme`, `created_in_7d`, `created_in_30d`, `completed_in_7d`, `completed_in_30d`, `avg_completion_time_hours`

- `HabitStatisticsPage`
  Поля: `total`, `active`, `archived`, `due_today`, `completed_today`, `success_rate_today`, `success_rate_7d`, `success_rate_30d`, `schedule_type_distribution`, `completions_by_day`, `top_streaks`, `top_themes`

- `ThemeStatisticsPage`
  Поля: `top_task_themes`, `top_habit_themes`, `busiest_theme`

- `StatsInsight`
  Поля: `title`, `description`, `severity`

- `StatisticsPageData`
  Поля: `range`, `kpis`, `tasks`, `habits`, `themes`, `insights`

Примечание:
- в `by_theme` и `top_*_themes` отдавать не UUID, а уже нормализованные названия тем;
- задачи и привычки без темы отдавать под единым label, например `Без темы`.

## 7. PR-шаги и implementation checklist

### PR 1. Contract + route skeleton

Цель:
- заменить заглушку `/soon` на реальный маршрут `/stats`;
- зафиксировать page contract и пустой каркас страницы.

Изменения:
- добавить `src/routers/stats.py`;
- подключить router в `src/main.py`;
- обновить ссылки в `src/templates/base.html` и `src/templates/index.html` с `/soon` на `/stats`;
- добавить `src/schemas/statistics.py` с page-level схемами;
- добавить `src/templates/stats/stats_page.html` с пустыми секциями и фильтром `7d/30d`;
- при необходимости добавить helper для чтения `range` из query.

Тесты:
- `tests/api_unit/test_stats_router_unit.py`:
  - `GET /stats` возвращает `200`;
  - invalid `range` дает `422` или нормализуется, если будет выбран мягкий контракт;
  - в context приходит `current_page = "stats"`;
- smoke integration test на `GET /stats`.

Документация:
- обновить `docs/api_contract.mdc`;
- при необходимости обновить `docs/backend_roadmap.mdc`, если реализация реально стартовала.

Риски:
- не смешать новую страницу с текущим sidebar-контрактом;
- не раздувать этот PR бизнес-логикой агрегатов.

### PR 2. Task statistics expansion

Цель:
- добавить page-level аналитику задач без поломки `TaskService.get_task_statistics()`.

Предпочтительный подход:
- не перегружать текущую sidebar-функцию;
- добавить новую page-oriented функцию, например `get_task_page_statistics()`;
- если потребуется много выборок, аккуратно расширить `TaskRepository`.

Изменения:
- `src/services/tasks.py`:
  - добавить расчет `completion_rate`;
  - добавить `created_in_7d`, `created_in_30d`;
  - добавить `completed_in_7d`, `completed_in_30d`;
  - добавить `avg_completion_time_hours`;
  - нормализовать `by_theme` в человекочитаемые названия;
- `src/repositories/tasks.py`:
  - расширять только если реально нужен SQL-level helper;
  - в MVP допустимо считать агрегаты из списка задач пользователя.

Тесты:
- `tests/unit/test_task_service.py`:
  - completion rate при `0` задач;
  - average completion time считает только completed tasks;
  - задачи без темы попадают в `Без темы`;
  - created/completed counters корректно режутся по датам;
- `tests/integration/test_stats.py`:
  - данные `/stats` отражают реальные задачи текущего пользователя и не смешиваются с чужими.

Риски:
- timezone/UTC при расчете `7d/30d`;
- округление среднего времени выполнения;
- не использовать UUID темы в UI-контракте.

### PR 3. Habit statistics expansion

Цель:
- добавить page-level аналитику привычек на основе `habit_completions`.

Предпочтительный подход:
- sidebar-метод `get_habit_statistics()` оставить совместимым;
- page-level аналитику вынести в отдельную функцию, например `get_habit_page_statistics(range)`.

Изменения:
- `src/services/habits.py`:
  - добавить `success_rate_7d` и `success_rate_30d`;
  - добавить `completions_by_day` для выбранного периода;
  - добавить `top_streaks`;
  - добавить `schedule_type_distribution`;
  - добавить `archived vs active`;
  - добавить `top_themes` по активным привычкам;
- переиспользовать существующие helpers по streak/due logic, а не дублировать правила расписаний;
- если логика начинает разрастаться, вынести page-level расчеты в `src/services/statistics.py`, а в `HabitService` оставить точечные помощники.

Тесты:
- `tests/unit/test_habit_service.py`:
  - success rate за период считает правильный знаменатель по due occurrences;
  - archived привычки не попадают туда, где не должны;
  - top streaks сортируются стабильно;
  - trend корректен при днях без выполнений;
- `tests/integration/test_stats.py`:
  - история выполнений пользователя собирается корректно.

Риски:
- не путать `completed_today` и `due_today`;
- для `7d/30d` считать успех по обязательным появлениям привычек, а не просто по числу записей в `habit_completions`;
- аккуратно обработать привычки с `starts_on`, `ends_on`, `interval_cycle`.

### PR 4. Statistics page composer

Цель:
- собрать единый backend-контекст страницы статистики.

Изменения:
- добавить `src/services/statistics.py`;
- composer получает task/habit/theme services через зависимости;
- composer собирает:
  - `kpis`;
  - `tasks`;
  - `habits`;
  - `themes`;
  - `insights`;
- добавить простые инсайты:
  - `Осталось привычек на сегодня: due_today - completed_today`;
  - `Лучшая серия: habit_name + streak`;
  - `Самая загруженная тема: theme_name + active_tasks`;
- router получает уже готовый `StatisticsPageData`.

Тесты:
- `tests/unit/test_statistics_service.py`:
  - composer корректно агрегирует секции;
  - empty-state не падает;
  - инсайты не дублируются и не содержат пустых значений;
- `tests/api_unit/test_stats_router_unit.py`:
  - route отдает ожидаемый template context.

Риски:
- не переносить вычисления инсайтов в шаблон;
- не завязать composer на HTTP-объекты.

### PR 5. UI implementation

Цель:
- реализовать полноценную страницу статистики в web UI.

Изменения:
- `src/templates/stats/stats_page.html`:
  - верхние KPI-карточки;
  - секция задач;
  - секция привычек;
  - секция тем;
  - блок инсайтов;
  - empty states;
- `src/static/css/style.css`:
  - стили страницы статистики;
  - адаптивность для mobile/tablet;
- при необходимости:
  - `src/static/js/stats.js` для переключения диапазона или легких интеракций.

UI-принципы:
- без тяжелой chart library в `v1`;
- простые бар-чарты и trend-line можно отрисовать HTML/CSS;
- длинные названия тем не должны ломать layout;
- мобильный режим должен быть читаемым без горизонтального скролла.

Тесты:
- template smoke checks;
- integration test на наличие ключевых блоков страницы;
- ручная проверка desktop/mobile.

Риски:
- не превратить UI в копию сайдбара;
- не перегрузить страницу десятком второстепенных метрик.

### PR 6. Polish + docs + verification

Цель:
- довести фичу до демонстрационного состояния.

Изменения:
- прогнать релевантные проверки:
  - `poetry run pytest -x tests -v`
  - `poetry run ruff check src tests`
  - `poetry run mypy src --explicit-package-bases`
- обновить документацию;
- проверить consistency цифр между sidebar и stats page;
- зафиксировать known limitations.

Тесты и проверка:
- сверить цифры на `/stats` и в sidebar для общих метрик;
- убедиться, что `owner-scoped` данные не протекают между пользователями;
- проверить пустой аккаунт, аккаунт без тем, аккаунт без привычек, аккаунт без выполнений.

## 8. Набор файлов по PR

Новые файлы:
- `src/routers/stats.py`
- `src/services/statistics.py`
- `src/schemas/statistics.py`
- `src/templates/stats/stats_page.html`
- `tests/unit/test_statistics_service.py`
- `tests/api_unit/test_stats_router_unit.py`
- `tests/integration/test_stats.py`

Изменяемые файлы:
- `src/main.py`
- `src/services/tasks.py`
- `src/services/habits.py`
- `src/repositories/tasks.py` при необходимости
- `src/repositories/habits.py` при необходимости
- `src/schemas/__init__.py`
- `src/templates/base.html`
- `src/templates/index.html`
- `src/static/css/style.css`
- `src/static/js/shared.js` или новый `src/static/js/stats.js` при необходимости
- `docs/api_contract.mdc`
- `docs/backend_roadmap.mdc` при старте реализации

## 9. Edge cases, которые нельзя забыть

- пользователь без задач и привычек;
- задачи без темы;
- привычки без выполнений;
- привычки, которые уже архивированы;
- привычки с `ends_on` в прошлом;
- привычки с редкими расписаниями (`monthly_day`, `yearly_date`, `interval_cycle`);
- одинаковые счетчики при фильтре `7d` и `30d`, если данных мало;
- корректный UTC-based расчет дат для `created_at` и `completed_at`.

## 10. Definition of Done для страницы `/stats`

Страница считается готовой, когда:
- `/stats` работает вместо заглушки `/soon`;
- диапазон `7d/30d` работает стабильно;
- основные блоки страницы отрисовываются без падений;
- текущий sidebar по-прежнему работает;
- расчеты покрыты unit + integration тестами;
- документация обновлена;
- известные ограничения задачной аналитики честно зафиксированы.

## 11. Рекомендуемый порядок работы

Если делать без лишнего риска, идти так:
1. PR 1
2. PR 2
3. PR 3
4. PR 4
5. PR 5
6. PR 6

Такой порядок минимизирует регрессии и позволяет в любой момент остановиться на рабочем промежуточном состоянии.
