# HabitFlow Frontend Safety Guide

## 1. Назначение документа

`docs/FRONTEND_SAFETY.md` дополняет `docs/FRONTEND.md` и `docs/FRONTEND_SMOKE.md`.

Если `docs/FRONTEND.md` отвечает на вопрос "как устроен текущий фронтенд", то этот файл отвечает на вопрос:

- что нельзя менять без проверки;
- какие DOM-контракты уже существуют;
- какие сценарии обязаны не сломаться;
- какие тесты и команды запускать после изменений.

Использовать файлы вместе:

1. сначала `docs/FRONTEND.md`;
2. потом `docs/FRONTEND_SAFETY.md`;
3. потом `docs/FRONTEND_SMOKE.md`;
4. затем уже читать конкретные шаблоны, JS и роуты.

## 2. Главный принцип безопасных изменений

В HabitFlow фронтенд ломается не только из-за "неправильного UI", но и из-за скрытых связей между:

- Jinja templates;
- глобальным CSS;
- глобальным JS;
- серверным template context;
- session state;
- HTML, который ожидают тесты.

Поэтому безопасное изменение почти всегда требует проверки не только визуала, но и:

- DOM-идентификаторов;
- `data-*` атрибутов;
- CSRF flow;
- redirects;
- owner-scoped behavior;
- query/session semantics.

## 3. Критические DOM-контракты

### 3.1 Глобальные контракты из `base.html`

Следующие элементы считаются критическими:

- `meta[name="csrf-token"]`
  - используется JS-функцией `getCsrfToken()`.
- `body[data-page="..."]`
  - используется для page-level CSS/layout ветвления.
- `.theme-filter-link`
  - используется в `list_tasks.js`, `list_habits.js`, `list_themes.js`.
- `#stat-active-tasks`
- `#stat-total-habits`
- `#stat-active-habits`
- `#stat-due-habits-today`
- `#stat-success-rate`
  - эти id используются `main.js` и `list_habits.js`.

Дополнительный контракт:

- у `#stat-success-rate` должны существовать или корректно обновляться
  - `data-due-habits-today`
  - `data-completed-habits-today`

### 3.2 Контракты task UI

Обязательные селекторы для задач:

- `.task-item[data-task-id]`
- `.task-item[data-completed]`
- `.task-checkbox input[type="checkbox"]`
- `.task-checkbox input[data-task-id]`
- `.task-title`
- `.btn-task-delete[data-task-id]`

Если меняется разметка task cards на `/` или `/tasks`, нужно проверить:

- complete/incomplete через `main.js`;
- delete через `main.js`;
- корректное обновление `#stat-active-tasks`.

### 3.3 Контракты habit UI

Обязательные селекторы для привычек:

- `.habit-card[data-habit-id]`
- `.btn-habit-complete[data-habit-id]`
- `.btn-habit-delete[data-habit-id]`
- `.habit-streak`

Критические state-классы:

- `.is-active`
- `.is-completed`
- `.is-archived`
- `.no-progress`

Именно эти классы используются как минимум для:

- логики delete/update stats;
- визуального состояния;
- поведения после complete.

### 3.4 Контракты themes UI

Для тем сейчас важны:

- `.theme-card[data-theme-id][data-theme-name]`
- `.theme-filter-link`

Это важно не только для JS, но и для тестов:

- интеграционные тесты вытаскивают `theme_id` из `data-theme-id`;
- удаление темы обновляет sidebar links по `theme` query.

### 3.5 Контракты form UI

Все CRUD-формы завязаны на:

- `.item-form`
- `input[name="csrf_token"]`

Для edit-форм дополнительно критично:

- `method="put"` на `<form>`
  - именно это перехватывает `update.js`.

Для формы привычек критичны:

- `#schedule_type`
- `#schedule_config`
- `#schedule-config-daily`
- `#schedule-config-weekly-days`
- `#schedule-config-monthly-day`
- `#schedule-config-yearly-date`
- `#schedule-config-interval-cycle`
- `#starts_on`
- `#ends_on`
- `#period-infinite`

### 3.6 Контракты auth UI

Для login/register критичны:

- `.auth-form`
- `input[name="csrf_token"]`
- `input[name="next"]`
- `input[name="email"]`
- `input[name="password"]`
- `[data-auth-client-error]`
- `[data-auth-client-error-text]`

Если включен Google OAuth, шаблон также должен корректно рендерить ссылку:

- `/auth/google/start?next=...`

## 4. Контракты серверного контекста

Следующие поля считаются обязательными для большинства экранов:

- `request`
- `themes`
- `stats`
- `csrf_token`

Часто обязательны также:

- `current_user`
- `current_user_display_name`
- `current_page`

Важно:

- фильтр темы живет в UI session как `selected_theme`;
- query `?theme=...` может менять поведение будущих страниц;
- `"Все темы"` - служебная тема, добавляемая сервером.

## 5. Change Checklist

### 5.1 Если меняется `base.html`

Обязательно проверить:

- navbar links;
- logout form;
- CSRF meta tag;
- наличие скрытого stats DOM при `hide_sidebar`;
- theme links;
- загрузку `shared.js` и `main.js`;
- desktop/mobile layout.

Запустить минимум:

- `tests/unit/test_utils.py`
- `tests/integration/test_tasks.py`
- `tests/integration/test_habits.py`
- `tests/api_unit/test_auth_router_html_unit.py`

### 5.2 Если меняется `main.js`

Обязательно проверить:

- task complete;
- task incomplete;
- task delete;
- habit complete;
- sidebar stats update;
- уведомления;
- CSRF extraction.

Запустить минимум:

- `tests/integration/test_tasks.py`
- `tests/integration/test_habits.py`
- `tests/unit/test_utils.py`

И дополнительно нужен ручной smoke в браузере, потому что прямых browser e2e-тестов сейчас нет.

### 5.3 Если меняются task templates / task JS / task CSS

Обязательно проверить:

- список `/tasks`;
- create `/tasks/new`;
- edit `/tasks/{id}`;
- complete/incomplete;
- delete;
- filters;
- sort;
- pagination;
- theme filter persistence;
- task cards на `/`.

Запустить минимум:

- `tests/integration/test_tasks.py`
- `tests/api_unit/test_tasks_router_unit.py`

### 5.4 Если меняются habit templates / habit JS / habit CSS

Обязательно проверить:

- список `/habits`;
- create `/habits/new`;
- edit `/habits/{id}`;
- complete today;
- delete;
- filters by `status`;
- filters by `schedule_type`;
- archive behavior;
- due-today behavior;
- stats after complete/delete;
- habit cards на `/`.

Запустить минимум:

- `tests/integration/test_habits.py`
- `tests/api_unit/test_habits_router_unit.py`
- `tests/unit/test_habit_service.py`

### 5.5 Если меняются themes templates / JS / CSS

Обязательно проверить:

- список `/themes`;
- create `/themes/new`;
- edit `/themes/{id}`;
- delete;
- pagination redirects;
- sidebar theme links;
- session behavior для активной темы.

Запустить минимум:

- `tests/integration/test_themes.py`
- `tests/api_unit/test_themes_router_unit.py`
- `tests/unit/test_utils.py`

### 5.6 Если меняются auth templates / auth JS

Обязательно проверить:

- `/auth/login`;
- `/auth/register`;
- client validation;
- `next` normalization;
- logout;
- Google OAuth link rendering;
- CSRF presence in forms.

Запустить минимум:

- `tests/integration/test_auth.py`
- `tests/integration/test_unauthorized_create_redirects.py`
- `tests/api_unit/test_auth_router_html_unit.py`

### 5.7 Если меняется `/stats`

Обязательно проверить:

- `range=7d`;
- `range=30d`;
- KPI cards;
- sections for tasks/habits/themes;
- empty states;
- current period copy.

Запустить минимум:

- `tests/integration/test_stats.py`
- `tests/api_unit/test_stats_router_unit.py`

### 5.8 Если меняется `forms.js` или `update.js`

Обязательно проверить все edit/create flows:

- `/themes/new`
- `/themes/{id}`
- `/tasks/new`
- `/tasks/{id}`
- `/habits/new`
- `/habits/{id}`

Потому что это shared code для всех `.item-form`.

## 6. Regression Matrix

### 6.1 Global UI regressions

Обязательные сценарии:

- страница рендерится без 500 и без сломанной навигации;
- CSRF-токен присутствует на HTML-странице;
- theme filter links остаются рабочими;
- скрытый stats DOM не пропал на страницах с `hide_sidebar=True`.

Автотесты:

- `tests/unit/test_utils.py`
- `tests/api_unit/test_auth_router_html_unit.py`

### 6.2 Tasks regressions

Обязательные сценарии:

- create task;
- edit task;
- delete task;
- complete task;
- incomplete task;
- status filter;
- sort by name/date/priority;
- pagination;
- theme filter persists in session;
- foreign task hidden from another user.

Автотесты:

- `tests/integration/test_tasks.py`
- `tests/api_unit/test_tasks_router_unit.py`

### 6.3 Habits regressions

Обязательные сценарии:

- create habit;
- edit habit;
- delete habit;
- complete today;
- `todays`, `active`, `completed`, `archived` filters;
- schedule-type-sensitive visibility;
- archive after period end;
- foreign habit hidden and immutable.

Автотесты:

- `tests/integration/test_habits.py`
- `tests/api_unit/test_habits_router_unit.py`
- `tests/unit/test_habit_service.py`

### 6.4 Themes regressions

Обязательные сценарии:

- create theme;
- duplicate-name error;
- edit theme;
- delete theme;
- list render;
- pagination redirects;
- foreign theme hidden and immutable;
- `data-theme-id` / `data-theme-name` still present where expected.

Автотесты:

- `tests/integration/test_themes.py`
- `tests/api_unit/test_themes_router_unit.py`
- `tests/unit/test_utils.py`

### 6.5 Stats regressions

Обязательные сценарии:

- `/stats` opens;
- `/stats?range=30d` opens;
- range switch changes copy and widgets;
- sections still show expected content and empty states.

Автотесты:

- `tests/integration/test_stats.py`
- `tests/api_unit/test_stats_router_unit.py`

### 6.6 Auth regressions

Обязательные сценарии:

- login page renders;
- register page renders;
- safe `next` behavior;
- logout works;
- Google OAuth start link renders correctly when enabled;
- invalid CSRF shows HTML error;
- unauthorized creates redirect to login.

Автотесты:

- `tests/integration/test_auth.py`
- `tests/integration/test_unauthorized_create_redirects.py`
- `tests/api_unit/test_auth_router_html_unit.py`

## 7. Verification Commands

### 7.1 Быстрые таргетные команды

Tasks:

```bash
PYTHONPATH=. poetry run pytest -x \
  tests/integration/test_tasks.py \
  tests/api_unit/test_tasks_router_unit.py -v
```

Habits:

```bash
PYTHONPATH=. poetry run pytest -x \
  tests/integration/test_habits.py \
  tests/api_unit/test_habits_router_unit.py \
  tests/unit/test_habit_service.py -v
```

Themes:

```bash
PYTHONPATH=. poetry run pytest -x \
  tests/integration/test_themes.py \
  tests/api_unit/test_themes_router_unit.py \
  tests/unit/test_utils.py -v
```

Stats:

```bash
PYTHONPATH=. poetry run pytest -x \
  tests/integration/test_stats.py \
  tests/api_unit/test_stats_router_unit.py -v
```

Auth:

```bash
PYTHONPATH=. poetry run pytest -x \
  tests/integration/test_auth.py \
  tests/integration/test_unauthorized_create_redirects.py \
  tests/api_unit/test_auth_router_html_unit.py -v
```

### 7.2 Если менялись shared layout / shared JS / shared CSS

Рекомендуемый минимальный набор:

```bash
PYTHONPATH=. poetry run pytest -x \
  tests/unit/test_utils.py \
  tests/integration/test_tasks.py \
  tests/integration/test_habits.py \
  tests/integration/test_themes.py \
  tests/integration/test_stats.py \
  tests/api_unit/test_auth_router_html_unit.py -v
```

### 7.3 Полная проверка

```bash
make test
```

Если менялись Python-контракты, shared templates или общие зависимости, дополнительно:

```bash
poetry run ruff check . --force-exclude
poetry run mypy src --explicit-package-bases
```

## 8. Что тесты сейчас НЕ гарантируют

Нужно помнить о текущих пробелах:

- в репозитории нет полноценных browser e2e-тестов на Playwright;
- нет прямых тестов на реальное выполнение глобального JS в браузере;
- нет визуальных regression tests по CSS;
- часть DOM-контрактов проверяется косвенно, а не напрямую.

Следствие:

- после крупных JS/CSS/markup-правок нужен ручной smoke-run в браузере;
- особенно это касается:
  - `main.js`;
  - `base.html`;
  - `forms.js`;
  - `update.js`;
  - `lists.css`;
  - `forms.css`;
  - `layout-fixes.css`.

## 9. Безопасный алгоритм изменений

Перед правкой:

1. Найти экран в `docs/FRONTEND.md`.
2. Проверить соответствующий раздел в `docs/FRONTEND_SAFETY.md`.
3. Найти все связанные селекторы и контракты:

```bash
rg -n "selector_or_id_or_data_attr" src/templates src/static/js tests
```

4. Если меняется shared DOM или shared JS, сразу расширить набор проверок.

После правки:

1. Запустить таргетные тесты по области.
2. Если тронут shared слой, запустить расширенный набор.
3. Если правка UI-heavy, сделать ручной smoke в браузере.
4. Обновить `docs/FRONTEND.md` и/или `docs/FRONTEND_SAFETY.md`, если изменился контракт.

## 10. Когда обновлять этот файл

Обновлять `docs/FRONTEND_SAFETY.md` нужно, если меняется хотя бы одно из следующего:

- обязательный DOM-id / class / `data-*` атрибут;
- JS, завязанный на DOM-контракт;
- логика safe-edit checklist;
- regression matrix;
- набор рекомендуемых тестов;
- known gaps в тестовом покрытии.

Если изменилась только ручная последовательность проверки страниц, без новых контрактов и без новых тестовых требований, обновлять нужно `docs/FRONTEND_SMOKE.md`, а не этот файл.
