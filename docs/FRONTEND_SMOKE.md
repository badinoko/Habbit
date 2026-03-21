# HabitFlow Frontend Smoke Checklist

## 1. Назначение документа

`docs/FRONTEND_SMOKE.md` нужен для быстрой ручной проверки фронтенда после изменений.

Этот файл отвечает на вопрос:

- что открыть в браузере после правок;
- какие пользовательские сценарии быстро прогнать руками;
- какие smoke-проверки обязательны для разных типов фронтенд-изменений.

Это не архитектурная карта и не DOM-спецификация.

Использование вместе с другими файлами:

1. `docs/FRONTEND.md`
2. `docs/FRONTEND_SAFETY.md`
3. `docs/FRONTEND_SMOKE.md`

## 2. Когда читать этот файл

Открывать `docs/FRONTEND_SMOKE.md` нужно, если:

- менялись шаблоны;
- менялся глобальный CSS;
- менялся глобальный JS;
- менялись формы;
- менялись списки, фильтры, пагинация, complete/delete действия;
- автотесты прошли, но нужен быстрый ручной sanity-check.

## 3. Как пользоваться

1. Определи область правок.
2. Выбери минимальный набор smoke-сценариев из раздела ниже.
3. Если правка трогает shared слой, прогоняй и page-specific, и global smoke.
4. Если ручная проверка выявила новый хрупкий контракт, обнови:
   - `docs/FRONTEND.md` если это карта/структура;
   - `docs/FRONTEND_SAFETY.md` если это инвариант или обязательная проверка;
   - `docs/FRONTEND_SMOKE.md` если это новый ручной smoke-сценарий.

## 4. Минимальный global smoke

Этот набор нужен почти всегда после заметных фронтенд-правок.

Проверить:

- открывается `/`;
- открывается `/tasks`;
- открывается `/habits`;
- открывается `/themes`;
- открывается `/stats`;
- открывается `/auth/login`;
- navbar не сломан;
- активные ссылки в навигации не выглядят сломанными;
- layout не разваливается на desktop;
- layout не разваливается на mobile width;
- ошибок в браузерной консоли нет или нет новых ошибок;
- формы и `fetch`-действия не падают из-за CSRF.

## 5. Page-by-page smoke

### 5.1 Home `/`

Проверить:

- страница загружается без 500;
- отображаются navbar и основной контент;
- блок задач рендерится;
- блок привычек рендерится;
- цитата рендерится или корректно показывается fallback;
- клик по task checkbox работает;
- клик по habit complete работает;
- после действия обновляются уведомления;
- после действия не ломаются счетчики в stats.

### 5.2 Tasks list `/tasks`

Проверить:

- список открывается;
- theme pills отображаются;
- смена `status` фильтра работает;
- смена сортировки работает;
- переключение порядка `asc/desc` работает;
- pagination links работают;
- чекбокс complete/incomplete работает;
- delete работает;
- переход в edit работает;
- create button ведет на `/tasks/new`.

### 5.3 Task form `/tasks/new` и `/tasks/{id}`

Проверить:

- форма открывается;
- поля name/description/theme/priority видны;
- submit create работает;
- submit edit работает;
- после успешного edit есть redirect обратно в `/tasks`;
- ошибки валидации показываются предсказуемо;
- CSRF не ломает submit.

### 5.4 Habits list `/habits`

Проверить:

- список открывается;
- фильтр `status` работает;
- фильтр `schedule_type` работает;
- сортировка работает;
- pagination links работают;
- complete today работает;
- delete работает;
- archive/todays/completed состояния визуально различимы;
- stats корректно меняются после complete/delete;
- переход в edit работает;
- create button ведет на `/habits/new`.

### 5.5 Habit form `/habits/new` и `/habits/{id}`

Проверить:

- форма открывается;
- `schedule_type` переключает нужные блоки;
- weekly/monthly/yearly/interval поля показываются корректно;
- `period-infinite` корректно выключает/включает `ends_on`;
- create работает;
- edit работает;
- после успешного edit есть redirect обратно в `/habits`;
- ошибки валидации понятны и не ломают форму.

### 5.6 Themes list `/themes`

Проверить:

- список открывается;
- карточки тем рендерятся;
- create button ведет на `/themes/new`;
- edit работает;
- delete работает;
- после delete страница не ломается;
- sidebar/theme links остаются согласованными;
- pagination links работают.

### 5.7 Theme form `/themes/new` и `/themes/{id}`

Проверить:

- форма открывается;
- поле названия работает;
- выбор цвета работает;
- create работает;
- edit работает;
- после edit есть redirect в `/themes`;
- ошибки отображаются предсказуемо.

### 5.8 Stats `/stats`

Проверить:

- страница открывается;
- `7d` работает;
- `30d` работает;
- range links не ломают верстку;
- KPI cards рендерятся;
- секции задач/привычек/тем рендерятся;
- empty states выглядят корректно при пустых данных;
- контент не разваливается на mobile width.

### 5.9 Auth `/auth/login` и `/auth/register`

Проверить:

- страницы открываются;
- email/password поля видны;
- client validation работает;
- CSRF hidden input присутствует;
- `next` hidden input присутствует;
- login/register submit не ломается;
- logout из navbar работает;
- если включен Google OAuth, ссылка на Google рендерится и выглядит корректно.

## 6. Smoke by change type

### 6.1 Если менялся `base.html`

Прогнать:

- раздел `4. Минимальный global smoke`;
- Home;
- Tasks list;
- Habits list;
- Auth;

### 6.2 Если менялся `main.js`

Прогнать:

- Home;
- Tasks list;
- Habits list.

### 6.3 Если менялись `forms.js` или `update.js`

Прогнать:

- Task form create/edit;
- Habit form create/edit;
- Theme form create/edit.

### 6.4 Если менялся `lists.css`, `style.css` или `layout-fixes.css`

Прогнать:

- раздел `4. Минимальный global smoke`;
- Tasks list;
- Habits list;
- Themes list;
- Stats;
- mobile width проверку.

### 6.5 Если менялся `auth_validation.js` или auth templates

Прогнать:

- Auth;
- logout через navbar;
- redirect в login для неавторизованного create flow, если правка затрагивала auth/layout.

## 7. Базовый viewport smoke

Минимально проверить две ширины:

- desktop: около `1440px`;
- mobile: около `390px`.

На mobile особенно смотреть:

- navbar wrap;
- filters;
- cards list pages;
- form spacing;
- stats page sections.

## 8. Что считать достаточным ручным smoke

Для небольшой локальной правки:

- 1 relevant page;
- 1 adjacent page;
- 1 mobile check.

Для shared-правки:

- global smoke;
- минимум 1 create/edit/list flow из `tasks`, `habits`, `themes`;
- login page;
- stats page;
- desktop + mobile.

## 9. Как обновлять этот файл

Поддерживать файл нужно просто:

- один раздел = одна страница или один тип правок;
- каждый пункт формулировать как короткую проверку в инфинитиве или как observable outcome;
- не дублировать архитектуру и DOM-контракты отсюда в другие файлы;
- если smoke-пункт стал автоматическим тестом, можно оставить его здесь, но сократить комментарий.

Если появляется новый экран:

1. добавить его в раздел `Page-by-page smoke`;
2. при необходимости добавить в `Smoke by change type`;
3. обновить ссылки в `docs/FRONTEND.md` и `docs/FRONTEND_SAFETY.md`, если изменился маршрут чтения документов.
