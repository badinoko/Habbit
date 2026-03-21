# HabitFlow Frontend Map

## 1. Назначение документа

`docs/FRONTEND.md` фиксирует фактическое состояние фронтенда HabitFlow на `2026-03-21`.

Файл-компаньон:

- `docs/FRONTEND_SAFETY.md` — DOM-контракты, change checklist, regression matrix и команды проверки после фронтенд-правок.
- `docs/FRONTEND_SMOKE.md` — короткий ручной smoke-checklist по страницам и типам изменений.

Маршрут чтения для новой сессии:

1. `docs/FRONTEND.md`
2. `docs/FRONTEND_SAFETY.md`
3. `docs/FRONTEND_SMOKE.md`

Документ нужен как стартовая точка для новых сессий:

- быстро понять, как устроен текущий UI;
- не тратить время на повторное исследование шаблонов, CSS и JS;
- видеть не только структуру, но и фронтенд-инварианты, скрытые связи и известные слабые места.

Если документ расходится с кодом, приоритет у кода и тестов. После фронтенд-изменений документ нужно обновлять.

## 2. Что сейчас является фронтендом проекта

Фронтенд HabitFlow сейчас это:

- серверно-рендеренный UI на `FastAPI + Jinja2`;
- глобальные CSS-файлы из `src/static/css/`;
- ванильный JavaScript без сборщика и без модульной системы в `src/static/js/`;
- частичная интерактивность через `fetch`, работающая поверх HTML-страниц.

Это не SPA и не отдельный frontend-app. Главная единица интерфейса здесь не компонент React/Vue, а связка:

- `router`;
- `template`;
- `page-specific js`;
- общие `base.html`, `main.js`, CSS-слои.

## 3. Где начинается фронтенд

Основные входные точки:

- `src/main.py`:
  - монтирует `/static`;
  - подключает роутеры;
  - рендерит `/` через `index.html`.
- `src/dependencies.py`:
  - `get_template_context()` собирает общий контекст страниц;
  - `add_quote_to_context()` добавляет цитату для главной.
- `src/utils.py`:
  - `build_template_context()` собирает темы, stats, текущего пользователя и CSRF-токен;
  - здесь же живет логика session-based фильтра темы.

Ключевая мысль: почти весь UI завязан на серверный template context, а не на client-side state management.

## 4. Общая архитектура UI

### 4.1 Template hierarchy

Базовый layout:

- `src/templates/base.html`

Базовые специализации:

- `src/templates/base_list.html`
- `src/templates/base_form.html`
- `src/templates/message.html`

Экранные шаблоны:

- `src/templates/index.html`
- `src/templates/stats/stats_page.html`
- `src/templates/tasks/tasks_list.html`
- `src/templates/tasks/tasks_form.html`
- `src/templates/habits/habits_list.html`
- `src/templates/habits/habits_form.html`
- `src/templates/themes/themes_list.html`
- `src/templates/themes/themes_form.html`
- `src/templates/themes/themes_update.html`
- `src/templates/auth/login.html`
- `src/templates/auth/register.html`

Вспомогательные шаблоны:

- `src/templates/macroses.html`

### 4.2 Layout contract

`base.html` задает:

- верхнюю навигацию;
- основной контейнер;
- боковую панель с темами и stats;
- блок `content`;
- глобальное подключение CSS;
- глобальное подключение `shared.js` и `main.js`;
- `body[data-page="..."]` для page-level CSS/JS-ветвления.

### 4.3 Shared server context

Практически все страницы получают общий контекст через `get_template_context()` / `build_template_context()`:

- `request`
- `themes`
- `stats`
- `current_user`
- `current_user_display_name`
- `csrf_token`

Важная особенность:

- активная тема хранится в UI session как `selected_theme`;
- query-параметр `?theme=...` не просто фильтрует текущую страницу, а меняет session state приложения;
- опция `"Все темы"` синтетическая и добавляется на сервере.

## 5. Карта экранов

| Маршрут | Router / handler | Template | JS | Особенности |
|---|---|---|---|---|
| `/` | `src/main.py::root` | `src/templates/index.html` | глобально `main.js` | Дашборд: до 5 задач, до 4 привычек, цитата |
| `/stats` | `src/routers/stats.py::stats_page` | `src/templates/stats/stats_page.html` | только глобальные | Отдельный визуально более новый экран |
| `/themes` | `src/routers/themes.py::get_themes` | `src/templates/themes/themes_list.html` | `src/static/js/list_themes.js` | CRUD-менеджер тем, pagination серверная |
| `/themes/new` | `src/routers/themes.py::create_theme_page` | `src/templates/themes/themes_form.html` | `forms.js` | Создание темы |
| `/themes/{id}` | `src/routers/themes.py::get_theme` | `src/templates/themes/themes_update.html` | `forms.js`, `update.js` | Редактирование темы через `PUT` fetch |
| `/tasks` | `src/routers/tasks.py::tasks_page` | `src/templates/tasks/tasks_list.html` | `src/static/js/list_tasks.js`, глобально `main.js` | Список задач, фильтры, сортировка, delete, complete/incomplete |
| `/tasks/new` | `src/routers/tasks.py::create_task_page` | `src/templates/tasks/tasks_form.html` | `forms.js`, `update.js` | Создание задачи, `update.js` загружен даже на create-page |
| `/tasks/{id}` | `src/routers/tasks.py::task_page` | `src/templates/tasks/tasks_form.html` | `forms.js`, `update.js` | Редактирование задачи через `PUT` fetch |
| `/habits` | `src/routers/habits.py::habits_page` | `src/templates/habits/habits_list.html` | `src/static/js/list_habits.js`, глобально `main.js` | Самый насыщенный экран: фильтры, delete, complete, stats updates |
| `/habits/new` | `src/routers/habits.py::create_habit_page` | `src/templates/habits/habits_form.html` | `forms.js`, `habit_form.js`, `update.js` | Создание привычки |
| `/habits/{id}` | `src/routers/habits.py::habit_page` | `src/templates/habits/habits_form.html` | `forms.js`, `habit_form.js`, `update.js` | Редактирование привычки через `PUT` fetch |
| `/auth/login` | `src/routers/auth.py` | `src/templates/auth/login.html` | `auth_validation.js` | hide-sidebar, email/password, optional Google OAuth |
| `/auth/register` | `src/routers/auth.py` | `src/templates/auth/register.html` | `auth_validation.js` | hide-sidebar, client validation |
| Ошибки / сообщения | exception handlers + auth helpers | `src/templates/message.html` | только глобальные | Общий экран ошибок, CSRF, OAuth failures |

## 6. Карта шаблонов по ролям

### 6.1 `base.html`

Это главный каркас интерфейса. Важные зависимости:

- все CSS подключаются глобально на всех страницах;
- `shared.js` и `main.js` тоже подключаются на всех страницах;
- meta-тег с CSRF живет здесь;
- user-menu logout отправляет обычную HTML-форму.

### 6.2 `base_list.html`

Общий каркас для `/themes`, `/tasks`, `/habits`:

- page header;
- create button;
- theme pills для `tasks` и `habits`;
- слот для filters;
- слот для list content.

### 6.3 `base_form.html`

Общий каркас для форм:

- header;
- error banner;
- `<form class="item-form">`;
- hidden `csrf_token`;
- нижние actions;
- автоматическое подключение `src/static/js/forms.js`.

Важно: метод формы берется из HTML-атрибута, но `PUT` физически работает не браузером, а через `update.js`.

### 6.4 `message.html`

Общий экран для:

- ошибок CRUD;
- CSRF проблем;
- некоторых auth / OAuth сценариев;
- универсальных сообщений пользователю.

## 7. CSS-карта

Все CSS подключаются глобально из `base.html` в таком порядке:

1. `src/static/css/style.css`
2. `src/static/css/layout-fixes.css`
3. `src/static/css/lists.css`
4. `src/static/css/forms.css`
5. `src/static/css/dashboard.css`
6. `src/static/css/stats.css`

Распределение ответственности:

- `style.css`:
  - базовые переменные;
  - navbar;
  - sidebar;
  - базовые utility/component styles.
- `layout-fixes.css`:
  - responsive container/layout overrides;
  - sticky sidebar;
  - page width tuning.
- `lists.css`:
  - list pages;
  - filters;
  - cards for themes/tasks/habits;
  - pagination UI.
- `forms.css`:
  - form pages;
  - radio/select UI;
  - auth screen styling;
  - hidden stats container for sidebar-less pages.
- `dashboard.css`:
  - homepage/dashboard-specific overrides;
  - empty states;
  - dashboard habit/task tuning.
- `stats.css`:
  - statistics v2 page;
  - KPI grid;
  - section cards;
  - visual identity for `/stats`.

Практический вывод:

- CSS не изолирован по страницам;
- почти любой класс потенциально глобален;
- перед локальными правками нужно проверять, не используется ли селектор в другом экране.

## 8. JavaScript-карта

### 8.1 Глобальные файлы

- `src/static/js/shared.js`
  - создает `window.habitFlowUtils.parseNonNegativeInt`.
- `src/static/js/main.js`
  - загружается везде;
  - управляет task complete/incomplete;
  - habit complete;
  - delete task;
  - notification system;
  - csrf lookup;
  - инициализацией bind-обработчиков.

### 8.2 Page-specific JS

- `src/static/js/list_themes.js`
  - edit redirect;
  - delete theme;
  - обновление sidebar themes после удаления.
- `src/static/js/list_tasks.js`
  - синхронизация фильтров;
  - сортировка;
  - пересборка theme-filter ссылок.
- `src/static/js/list_habits.js`
  - фильтры и сортировка привычек;
  - delete habit;
  - обновление stats после удаления привычки.
- `src/static/js/forms.js`
  - общая валидация `.item-form`;
  - loading state submit-кнопок;
  - field-level validation.
- `src/static/js/habit_form.js`
  - логика schedule_type;
  - сериализация `schedule_config`;
  - валидация period fields.
- `src/static/js/update.js`
  - перехватывает submit форм с `method="put"`;
  - отправляет JSON `PUT`;
  - после успеха делает redirect на list page.
- `src/static/js/auth_validation.js`
  - client-side validation для login/register.

### 8.3 Текущая JS-архитектура

Фактически сейчас это глобальный script-based frontend:

- нет bundler-а;
- нет ES modules;
- почти все функции живут в global scope;
- page-specific файлы не импортируют зависимости явно, а рассчитывают, что глобальные helpers уже загружены.

Это нужно помнить перед любым рефакторингом.

## 9. Важные фронтенд-инварианты

### 9.1 CSRF

Для JS-запросов CSRF берется через `getCsrfToken()` из:

- meta `csrf-token`;
- hidden input `csrf_token`;
- и нескольких legacy fallback-вариантов.

Если меняется layout формы или meta-разметка, легко сломать `fetch`-запросы.

### 9.2 `hide_sidebar` не означает, что stats DOM можно удалить

В `base.html` при `hide_sidebar=True` sidebar визуально скрывается, но stat-элементы могут рендериться в `.sidebar-stats-hidden`.

Это важно, потому что:

- `main.js` обновляет stats по DOM-id;
- `list_habits.js` тоже пересчитывает stats;
- часть интеграционных тестов ожидает наличие этих id в DOM.

То есть на form/list pages stats DOM является скрытым контрактом.

### 9.3 Тема - это session state, а не только фильтр URL

Выбор темы:

- идет через query `?theme=...`;
- записывается в `request.session["selected_theme"]`;
- дальше влияет на списки и главную страницу.

Нельзя относиться к theme-filter только как к локальному UI state.

### 9.4 PUT-формы на самом деле AJAX-формы

Редактирование тем, задач и привычек использует:

- HTML-форму с `method="put"`;
- `update.js`, который ловит submit;
- `fetch(..., { method: "PUT" })`.

Если убрать `update.js`, редактирование сломается.

### 9.5 `main.js` - общий runtime для нескольких экранов

`main.js` опирается на общие DOM-паттерны:

- `.task-item`
- `.task-checkbox`
- `.task-title`
- `.btn-task-delete`
- `.btn-habit-complete`
- `.habit-card`
- `#stat-*`

Любая смена этих классов/ID требует проверки сразу в нескольких экранах.

## 10. Что уже выглядит цельно

- Есть понятный SSR-каркас: `base -> list/form/page`.
- Статистика, auth и habits уже имеют более зрелые UI-сценарии.
- У проекта есть единый visual baseline: navbar, cards, buttons, filters.
- Theme filter и sidebar stats интегрированы в общий app flow.
- `/stats` уже показывает направление более современного UI внутри текущего стека.

## 11. Текущий фронтенд-долг и ловушки

### 11.1 Глобальный JS и переопределение функций

`update.js` объявляет свой `showNotification()`, хотя `main.js` уже объявляет функцию с тем же именем.

Следствие:

- на form pages глобальный helper silently переопределяется;
- поведение уведомлений зависит от порядка подключения скриптов.

### 11.2 В `forms.js` остался legacy-код

Сейчас в `forms.js` есть логика для:

- `goal_type`;
- `goal_value`;
- проверки `form.action.includes('/new/habit')`.

Текущие шаблоны привычек это уже не используют. Это признак старого кода, который может запутывать будущие сессии.

### 11.3 Inline JS в themes list

`themes_list.html` использует inline `onclick`:

- `editTheme(...)`
- `deleteTheme(...)`

Остальные страницы больше опираются на data-атрибуты и bind-обработчики. Подходы сейчас смешаны.

### 11.4 Pagination JS для tasks/habits недоведена

В `list_tasks.js` и `list_habits.js` есть `renderPagination()`, но:

- функция нигде не вызывается;
- она ожидает `data-*` атрибуты у pagination container;
- такие атрибуты сейчас не рендерятся шаблонами.

То есть реальная pagination сейчас серверно-рендеренная, а кусок JS выглядит как незавершенный или устаревший рефакторинг.

### 11.5 CSS загружается целиком на всех страницах

Это упрощает подключение, но повышает риск:

- пересечений селекторов;
- случайных визуальных регрессий;
- накопления устаревших правил.

### 11.6 Stats DOM используется как скрытая инфраструктура

Это неочевидный контракт. Если в будущем кто-то попытается “почистить разметку” на pages без sidebar, он легко сломает:

- client-side updates;
- часть тестов;
- счетчики после delete/complete действий.

### 11.7 `main.js` знает слишком много о разных экранах

Сейчас один файл отвечает и за:

- задачи;
- привычки;
- notifications;
- loading;
- delete handlers;
- stats refresh.

Это рабочий вариант, но он уже становится центральным хрупким узлом.

## 12. Быстрый старт для новой сессии

Если в новой сессии нужно быстро войти во фронтенд, читать в таком порядке:

1. `docs/FRONTEND.md`
2. `src/templates/base.html`
3. `src/dependencies.py`
4. `src/utils.py`
5. Нужный page template:
   - `src/templates/tasks/...`
   - `src/templates/habits/...`
   - `src/templates/themes/...`
   - `src/templates/stats/...`
   - `src/templates/auth/...`
6. Соответствующий page JS из `src/static/js/`
7. Нужный router из `src/routers/`

Если задача касается визуала:

1. проверить `base.html`;
2. найти экранный template;
3. посмотреть page CSS-слой;
4. проверить `main.js`, не задевает ли он нужный DOM.

Если задача касается форм:

1. `base_form.html`
2. экранная форма
3. `forms.js`
4. `update.js`
5. для привычек дополнительно `habit_form.js`

## 13. Как соотносится с другими документами

- `docs/overview.mdc`:
  - общий снимок продукта и архитектуры.
- `docs/api_contract.mdc`:
  - HTTP-контракты и поведение роутов.
- `docs/session_contract.mdc`:
  - cookies, Redis sessions, UI session.
- `frontend-redesign-contracts.md`:
  - продуктовый бриф и ориентир для редизайна;
  - это не карта текущей реализации.
- `docs/FRONTEND_SAFETY.md`:
  - безопасный протокол изменений;
  - DOM-контракты, обязательные проверки, матрица регрессий.
- `docs/FRONTEND_SMOKE.md`:
  - ручной smoke-checklist;
  - быстрые пользовательские сценарии после правок.

`docs/FRONTEND.md` описывает именно текущую реализацию UI.

## 14. Что обновлять при фронтенд-изменениях

Обновлять этот документ нужно, если меняется хотя бы одно из следующего:

- список экранов;
- template hierarchy;
- карта CSS/JS;
- page-specific scripts;
- общий layout;
- theme/session/filter behavior;
- DOM-контракты, на которые завязан JS;
- известные долги и ограничения.

Минимальный стандарт обновления:

- если изменился маршрут и экранный шаблон, обновить разделы `Карта экранов` и `Быстрый старт`;
- если изменился общий layout или shared context, обновить разделы `Общая архитектура UI` и `Фронтенд-инварианты`;
- если изменился JS/CSS responsibility, обновить `CSS-карту`, `JavaScript-карту` и `Текущий фронтенд-долг`.
