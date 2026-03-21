# Mobile Adaptation - Progress Journal

> **SSOT:** Полная хронология работы над мобильной адаптацией
> **Создан:** 2026-02-20

---

## === Session #1 (2026-02-20) ===

**Тема:** Анализ мобильных проблем на Xiaomi 12 PRO

### Контекст:

Пользователь предоставил 10 скриншотов с реального устройства Xiaomi 12 PRO:
- `docs/mobile_screenshots/photo_1-10_*.jpg`
- Доступ через Cloudflare Tunnel (besedka.org)

### Обнаруженные проблемы:

**1. Главная страница (photo_4):**
- Огромные пустые поля по бокам (~40% экрана)
- Контент сжат к центру
- Неэффективное использование пространства

**2. Navbar кнопки (photo_1, photo_2, photo_3):**
- Заголовки обрезаются
- Текст не влезает в кнопки
- Нет адаптивного уменьшения шрифта

**3. Списочный вид (photo_7, photo_8):**
- News: превью огромное, заголовок "Техники тр..."
- GrowReports: превью огромное, название "Второй тест..."
- Почти не отличается от плиточного вида
- Мало метаданных

**4. Панели управления:**
- News (photo_1): 1 строка - относительно норм
- GrowReports (photo_2): 2 строки - громоздко
- Gallery (photo_3): 2 строки с пустым пространством
- Три разных подхода

**5. Gallery виды:**
- Плиточный и списочный почти идентичны
- Оба показывают большие изображения
- Нет смысла переключаться

### Действия:

**[CREATED] Документация:**
- `docs/MOBILE_REDESIGN.md` - полный анализ с решениями
- `docs/mobile/overview.md` - Dashboard задач
- `docs/mobile/feedback.md` - дословный фидбэк
- `docs/mobile/progress.md` - этот журнал

**Статус:** [ACTIVE] - проблемы зафиксированы, готов к началу исправлений

---

## === Session #2 (2026-02-20) ===

**Тема:** Исправление критических проблем P0 (#MOBILE-001, #MOBILE-002)

### Изменения:

**[CHANGED] #MOBILE-001: templates/pages/home.html (строки 283-334)**
- Добавлен media query @media (max-width: 767px)
- Убраны огромные отступы: max-width: 100%, padding: 0 16px
- Уменьшен padding карточек: 20px 16px вместо 32px 40px
- Адаптивные размеры шрифтов для заголовков
- Изменена сетка section-row для компактности
- РЕЗУЛЬТАТ: Контент теперь занимает всю ширину экрана на мобильных

**[CHANGED] #MOBILE-002: static/css/navbar_v2.css (строки 1110-1158)**
- Добавлен media query @media (max-width: 767px)
- Уменьшены размеры nav-link: font-size 0.75rem, padding 0.4rem 0.65rem
- Уменьшены иконки в кнопках: 0.9rem
- Уменьшены отступы контейнера: padding 0.5rem, gap 0.5rem
- Добавлен вложенный query @media (max-width: 520px):
  - Скрыт текст в кнопках (только иконки)
  - Квадратные кнопки padding 0.5rem, min-width 40px
- РЕЗУЛЬТАТ: Текст влезает в кнопки, на узких экранах только иконки

### Статус текущих задач:

- ✅ #MOBILE-001: Главная страница - ГИПОТЕЗА (требует тестирования на besedka.org)
- ✅ #MOBILE-002: Navbar кнопки - ГИПОТЕЗА (требует тестирования на besedka.org)
- 🔄 #MOBILE-003: Списочный вид - в процессе (изучение gallery_list.html)
- ⏸️ #MOBILE-004: Унификация панелей - ожидание
- ⏸️ #MOBILE-005: Gallery виды - ожидание

### Следующие шаги:

1. Протестировать изменения на реальном устройстве через besedka.org
2. Продолжить работу над #MOBILE-003 (списочный вид с маленьким превью)
3. После подтверждения P0 задач - приступить к P1 (#MOBILE-004)

---

## === Session #3 (2026-02-20) ===

**Тема:** Завершение всех запланированных мобильных адаптаций

### Контекст:

Пользователь разрешил продолжить все правки без остановки. Выполнены все задачи #MOBILE-001 - #MOBILE-006.

### Изменения:

**[CHANGED] #MOBILE-003: static/css/unified_cards.css (строки 720-786)**
- Добавлен раздел "MOBILE ADAPTATION FOR LIST VIEW"
- Уменьшены размеры превью: 5rem x 5rem (80x80px квадрат) вместо 12rem x 9rem
- Компактная типографика: заголовок 0.95rem, описание 0.85rem, мета 0.75rem
- Описание показывает 3 строки вместо 2 для большей информативности
- Уменьшены отступы: padding 0.75rem, gap 0.75rem, min-height 96px
- РЕЗУЛЬТАТ: Списочный вид действительно компактный с маленьким превью

**[CHANGED] #MOBILE-004: static/css/gallery_redesign.css (строки 268-273, 1104-1108)**
- Убран `flex-wrap: wrap` из `.gall-filter-bar` на мобильных
- Удалены правила перестройки кнопок на 2 строки (order, width: 100%)
- Добавлен gap: 0.375rem для компактности (унификация с News)
- РЕЗУЛЬТАТ: Панель фильтров Gallery теперь одна строка как в News и GrowReports

**[CHANGED] #MOBILE-005: Уже реализовано через #MOBILE-003**
- SSOT стили списочного вида в unified_cards.css применяются ко всем модулям
- Gallery автоматически получила улучшения списочного вида
- РЕЗУЛЬТАТ: Реальная разница между grid и list режимами

**[CHANGED] #MOBILE-006: static/css/project.css (строки 700-809)**
- Добавлена "ADAPTIVE TYPOGRAPHY SYSTEM"
- Base font-size: 15px (было 16px), line-height: 1.5
- Заголовки: h1=1.75rem, h2=1.5rem, h3=1.25rem, h4=1.1rem, h5=1rem, h6=0.9rem
- Кнопки: 0.9rem font-size, компактный padding
- Формы: 15px font-size (важно для iOS - не зумит), компактный padding
- Карточки: title=1.05rem, text=0.85rem
- Small text: 0.8rem, badges: 0.75rem, lead: 1.1rem
- РЕЗУЛЬТАТ: Унифицированная адаптивная типографика для всего сайта

### Сводка всех изменённых файлов:

1. `templates/pages/home.html:283-334` - мобильные стили главной страницы
2. `static/css/navbar_v2.css:1110-1158` - адаптивные кнопки navbar
3. `static/css/unified_cards.css:720-786` - мобильный списочный вид (SSOT)
4. `static/css/gallery_redesign.css:268-273, 1104-1108` - унификация панели фильтров
5. `static/css/project.css:700-809` - адаптивная типографика

### Статус всех задач:

- ✅ #MOBILE-001: Главная страница - ГИПОТЕЗА (full width, компактные отступы)
- ✅ #MOBILE-002: Navbar кнопки - ГИПОТЕЗА (адаптивный текст, иконки на <520px)
- ✅ #MOBILE-003: Списочный вид - ГИПОТЕЗА (80x80px превью, 3 строки описания)
- ✅ #MOBILE-004: Унификация панелей - ГИПОТЕЗА (Gallery теперь 1 строка как News)
- ✅ #MOBILE-005: Gallery виды - ГИПОТЕЗА (SSOT стили применяются автоматически)
- ✅ #MOBILE-006: Адаптивная типографика - ГИПОТЕЗА (система базовых размеров)

### Технические детали:

**Принципы реализации:**
- Breakpoint: max-width: 767px (до планшетов)
- SSOT подход: unified_cards.css для всех модулей
- Мобильный первый: компактность и читаемость
- iOS-friendly: font-size 15px+ чтобы не зумило
- Консистентность: одинаковые паттерны везде

**Что НЕ трогали:**
- JavaScript функциональность (работает как есть)
- Серверный код (только CSS/HTML)
- Desktop версии (изменения только на мобильных)

### Следующие шаги:

1. **КРИТИЧНО:** Протестировать на реальном Xiaomi 12 PRO через besedka.org
2. Собрать фидбэк по каждой из 6 задач
3. Внести корректировки если потребуется
4. После подтверждения - создать коммит

**Готово к тестированию!** 🎯

---

## === Session #6 (2026-02-20) ===

**Тема:** Реализация SSOT unified_list_card.html (#MOBILE-107)

### Контекст:

Продолжение Session #5. Реализован sticky bar и drawer footer, теперь создание SSOT компонента для list view.

### Изменения:

**[CREATED] #MOBILE-107: templates/includes/partials/unified_list_card.html**
- Универсальный SSOT компонент для карточек list view
- Поддержка трёх модулей: News, GrowReports, Gallery
- Параметры: item, type ('news'|'grow'|'gall'), user, show_actions
- Полная совместимость с существующими CSS классами
- Документация в {% comment %} блоках

**Структура компонента:**
```
┌────────────────────────────────────────────────────────────┐
│ ┌──────┐                                                   │
│ │IMAGE │  Заголовок (h3, truncate)                         │
│ │AREA  │  Описание/Excerpt/Strain                          │
│ │      │  [badge] Автор              дата                  │
│ │      │                             👁️ 123  💬 5          │
│ └──────┘                                                   │
│ [ACTION BUTTONS - owner only]                              │
└────────────────────────────────────────────────────────────┘
```

**Поддерживаемые элементы по модулям:**
- NEWS: category badge, original content badge, unread dot, source/author
- GROWREPORTS: room/stage/draft badges, weeks grid, strain info
- GALLERY: album badge, photo count

### Тестирование через Playwright:

- 1920px desktop: list view работает корректно
- Sticky bar показывает все sort buttons с labels
- Переключение grid/list работает
- Карточки имеют горизонтальный layout

### Статус:

- ✅ #MOBILE-102: Sticky bar - ГИПОТЕЗА (реализовано в Session #5)
- ✅ #MOBILE-103: Drawer sticky footer - ГИПОТЕЗА (реализовано в Session #5)
- ✅ #MOBILE-107: unified_list_card.html - ГИПОТЕЗА (компонент создан)

### Файлы:

- `templates/includes/partials/unified_list_card.html` - СОЗДАН (270 строк)

---

## === Session #5 (2026-02-20) ===

**Тема:** Реализация sticky bar (#MOBILE-102) и drawer sticky footer (#MOBILE-103)

### Контекст:

Продолжение Session #4. Начало реализации по утверждённому плану.

### Изменения:

**[CHANGED] #MOBILE-102: templates/news/news_list.html**
- Объединены header и filter-bar в единый .news-sticky-bar
- View toggle перенесён в sticky bar (action buttons справа)
- Position: fixed, top: 64px (под navbar)

**[CHANGED] #MOBILE-102: static/css/news_redesign.css**
- Добавлен .news-sticky-bar:
  - position: fixed, top: 64px, left/right: 0, z-index: 150
  - glassmorphism: var(--glass-navbar), backdrop-filter: blur(20px)
  - height: 56px, flex layout
- Responsive breakpoints:
  - <900px: labels скрыты (.news-sort-label display: none)
  - <576px: sort buttons скрыты полностью (доступны в drawer)
- Overflow handling: flex-shrink, overflow: hidden

**[CHANGED] #MOBILE-103: static/css/news_redesign.css**
- .news-drawer: display: flex, flex-direction: column, overflow: hidden
- .news-drawer-sections: flex: 1 1 auto, overflow-y: auto
- .news-drawer-footer: flex-shrink: 0, border-top, background: glassmorphism

### Тестирование через Playwright:

- 320px: sticky bar в одну линию, только action buttons
- 412px: sticky bar работает, drawer footer sticky
- 780px: sort buttons icons only
- 1920px: полные labels на sort buttons

### Статус:

- ✅ #MOBILE-102: Sticky bar - ГИПОТЕЗА (работает на всех breakpoints)
- ✅ #MOBILE-103: Drawer sticky footer - ГИПОТЕЗА (footer прилипает к низу)

---

## === Session #8 (2026-02-20) ===

**Тема:** Исправление фидбэка Session #7 - позиционирование, emoji, навигация

### Контекст:

Пользователь предоставил детальный фидбэк по результатам тестирования Session #7:
- Gallery навигация занимает 5 рядов вместо 2
- Drawer смещает контент влево (компенсация scrollbar)
- Author name в "полуподвисшем" состоянии
- News emoji блёклый, без текста "Новости"
- #MOBILE-109 подтверждена как решённая

### Изменения:

**[CHANGED] #MOBILE-110: templates/includes/partials/unified_list_card.html**
- Полная реструктуризация META секции
- Дата вынесена в отдельный ряд (date-row), выровнена вправо
- Author + Stats размещены на последней строке:
  - Author/Source слева
  - Stats (views, comments) справа
- Добавлен новый класс: `{prefix}-card-date-row`
- РЕЗУЛЬТАТ: Чёткое разделение элементов, нет "подвисших" элементов

**[CHANGED] #MOBILE-110: static/css/unified_cards.css**
- Добавлены стили для date-row:
  ```css
  .news-grid--list .news-card-date-row { display: flex; justify-content: flex-end; }
  ```
- Обновлены стили meta row для list view:
  ```css
  .news-grid--list .news-card-bottom { margin-top: auto; display: flex; justify-content: space-between; }
  ```
- Версия: `?v=20260220-mobile5`

**[CHANGED] #MOBILE-111: static/css/news_redesign.css**
- Увеличен размер emoji: 1.5rem (было 1.25rem)
- Добавлен filter: `saturate(1.3) brightness(1.1)` для яркости
- Текст "Новости" остаётся видимым на мобильных:
  - @media <449px: font-size 0.875rem (уменьшен, но виден)
  - Emoji на мобильных: 1.375rem

**[CHANGED] #MOBILE-112: templates/gallery/gallery_list.html**
- ПОЛНАЯ реструктуризация навигации
- УДАЛЕНЫ: отдельные `.gall-header` и `.gall-filter-bar`
- СОЗДАН: единый `.gall-sticky-bar`
- Структура sticky bar:
  ```
  [gall-sticky-left: Title + User buttons]
  [gall-sort-buttons: All/New/Popular/Commented]
  [spacer]
  [gall-sticky-right: Search + Filter + ReadAll + View Toggle]
  ```
- Версия: `?v=20260220-mobile8`

**[CHANGED] #MOBILE-112: static/css/gallery_redesign.css**
- Добавлен полный CSS для gall-sticky-bar:
  ```css
  .gall-sticky-bar {
      position: fixed;
      top: 64px;
      left: 0; right: 0;
      z-index: 150;
      background: var(--glass-navbar);
      backdrop-filter: blur(20px);
      display: flex;
      align-items: center;
      min-height: 56px;
  }
  ```
- Responsive стили:
  - <575px: скрыть sort labels
  - <449px: компактный режим, скрыть sort buttons (в drawer)
- Скрыты legacy элементы: `.gall-header`, `.gall-filter-bar { display: none; }`

### Тестирование через Playwright:

- 410px width: Gallery показывает single sticky bar
- Sort buttons с иконками видны
- Title "Галерея" с emoji на месте
- View toggle работает

### Статус задач:

- [DONE] #MOBILE-109: Sort buttons overlap - подтверждено пользователем
- [HYPOTHESIS] #MOBILE-110: Author position - реструктурировано
- [HYPOTHESIS] #MOBILE-111: News emoji - увеличено, текст сохранён
- [HYPOTHESIS] #MOBILE-112: Gallery 5 rows - переделано на sticky-bar
- [ACTIVE] #MOBILE-113: Drawer shifts content - НЕ РЕАЛИЗОВАНО

### Файлы (сводка):

1. `templates/includes/partials/unified_list_card.html` - META rows restructure
2. `static/css/unified_cards.css:720+` - date-row, meta styles
3. `static/css/news_redesign.css` - emoji size, filters
4. `templates/gallery/gallery_list.html` - full sticky-bar rewrite
5. `static/css/gallery_redesign.css` - sticky-bar CSS, hide legacy

### Ожидает:

- Тестирование #MOBILE-110, 111, 112 на реальном устройстве
- Реализация #MOBILE-113 (drawer scrollbar compensation)

---

## === Session #8.1 (2026-02-20) ===

**Тема:** Исправление структуры карточки по фидбэку пользователя

### Контекст:

Пользователь протестировал изменения Session #8 и дал детальный фидбэк:
- Gallery sticky bar "революционные изменения" - но view toggle не помещается
- #MOBILE-113 ПОДТВЕРЖДЕНО РЕШЁННЫМ ("никакого смещения нигде не вижу")
- SSOT карточки ПОДТВЕРЖДЕНО ("карточки одинаковые во всех разделах")
- Дата оказалась "под описанием" - неправильно!
- Автор в "полуподвисшем состоянии"
- Идея: emoji раздела в Navbar (#MOBILE-114)

### Изменения:

**[CHANGED] #MOBILE-110: templates/includes/partials/unified_list_card.html**
- ПОЛНАЯ реструктуризация META секции
- Удалён отдельный `date-row`
- Создан единый `meta-bottom` с новой структурой:
  ```
  [Author] ─────────── [Date] [Stats]
  ```
- Добавлен `right-group` для группировки даты и счётчиков
- Описание: уменьшено количество слов (truncatewords:12 вместо 35)

**[CHANGED] #MOBILE-110: static/css/unified_cards.css**
- Описание: 1 строка (white-space: nowrap, line-clamp удалён)
- Новые классы:
  - `.meta-bottom` - последняя строка (justify-content: space-between)
  - `.right-group` - дата + счётчики справа
- Скрыты старые классы (`date-row`, `card-bottom`, `card-meta`)
- Превью: изменено на квадратные 96x96px (было 112x84)
- CSS переменные: `--list-thumb-width/height: 6rem`

### Тестирование через Playwright:

- 1920px: list view работает
- 410px: структура карточки правильная:
  - Title: 1 строка
  - Description: 1 строка (truncate)
  - Meta: 👑 Buddy | 27.12.2025 | 👁️52 💬10

### Статус задач:

- [DONE] #MOBILE-113: Drawer смещает контент - ПОДТВЕРЖДЕНО пользователем
- [DONE] #MOBILE-107: SSOT карточки - ПОДТВЕРЖДЕНО пользователем
- [HYPOTHESIS] #MOBILE-110: Структура meta-bottom - реструктурировано
- [NEW] #MOBILE-114: Emoji раздела в Navbar - записано как идея

### Файлы (сводка):

1. `templates/includes/partials/unified_list_card.html` - META restructure
2. `static/css/unified_cards.css` - meta-bottom, right-group, square thumbs
3. `templates/news/news_list.html` - version bump to mobile9
4. `templates/gallery/gallery_list.html` - version bump to mobile9
5. `templates/growreports/growreports_list.html` - version bump to mobile9
6. `templates/base.html` - version bump to mobile9
7. `templates/base_list_page.html` - version bump to mobile9

---

## === Session #7 (2026-02-20) ===

**Тема:** Sticky bar, list view cards, drawer fixes

Сессия содержала реализацию и ожидала фидбэка.
Результаты фидбэка обработаны в Session #8.

---

## === Session #4 (2026-02-20) ===

**Тема:** Планирование и документирование (БЕЗ кода!)

### Контекст:

После критики в Session #3 (код был написан без утверждения плана), вся работа Session #4 велась ТОЛЬКО в режиме обсуждения и документирования.

### Ключевые обсуждения:

**1. Drawer в GrowReports - проблема со скроллом:**
- Скриншот: `docs/mobile_screenshots/drawer_mobile.jpg`
- Кнопки "Сбросить/Применить" обрезаны
- Раздел "Генетика" не виден

**2. Радикальная идея - 2 линии вместо 3:**
- Заголовок раздела переносится в ЦЕНТР navbar
- Убираются кнопки фильтрации из панели (они в drawer)
- Экономия ~50px вертикального пространства

**3. Утверждённые sticky bar конфигурации:**
```
NEWS:     [🔲][≡] ─────spacer───── [🔍] [🎚️]
РЕПОРТЫ:  [Мои] [➕] [🔲][≡] ─────spacer───── [🔍] [🎚️]
ГАЛЕРЕЯ:  [Фото] [Альбомы] [➕] [🔲][≡] ─────spacer───── [🔍] [🎚️]
```

**4. Drawer улучшения:**
- Скролл внутри + sticky footer
- Glassmorphism blur на footer
- Иконки вместо текста
- Стадии как timeline: 🌱→🌿→🌸→💧→✂️→🏁
- Иконка "Завершено": ✅ → 🏁

**5. Баг Gallery drawer:**
- В News фильтрация работает на лету
- В Gallery - НЕ работает (кнопки переключаются, контент не меняется)

**6. Gallery архитектура (уточнение):**
- Фото и Альбомы - отдельные вкладки
- "Мои альбомы" внутри "Альбомы"
- НЕ нужна отдельная кнопка на sticky bar

### Созданные/обновлённые файлы:

**[CREATED] docs/mobile/startup.md**
- Полный startup prompt для новой сессии
- Порядок реализации 8 задач
- Технические заметки (breakpoints, glassmorphism)
- Чеклист для подтверждения пользователем

**[UPDATED] docs/mobile/overview.md**
- Dashboard с 8 задачами (#MOBILE-101 - #MOBILE-106, #MOBILE-003, #MOBILE-001)
- Утверждённые решения
- Детальные спецификации каждой задачи
- Порядок реализации

**[UPDATED] docs/mobile/feedback.md**
- Дословный фидбэк Session #4
- Проблемы drawer
- Идеи пользователя

**[UPDATED] docs/mobile/design_proposals.md**
- ASCII-эскизы всех вариантов
- Финальные утверждённые решения

### Статус:

- **Код НЕ МЕНЯЛСЯ** - только документация
- **Готово к реализации** в новой сессии
- **Startup prompt создан** - можно начинать новый чат

### Следующие шаги:

1. Закоммитить все изменения документации
2. Запустить новую сессию с startup prompt
3. Реализовать все 8 задач автономно
4. Получить подтверждение от пользователя

---

## === Session #10 (2026-02-21) ===

**Тема:** Theme switcher в dropdown + финализация + критический фидбэк

### Выполненные изменения:

**[CHANGED] templates/includes/partials/unified_user_dropdown.html**
- Добавлена кнопка "Сменить тему" между "Настройки" и "Предложить улучшение"
- Добавлен JavaScript для обновления иконки темы при смене
- Работает через BesedkaMasterThemes.cycle()

**[CHANGED] templates/includes/navbar/navbar_unified.html**
- Убран отдельный theme switcher из navbar-right
- Заменён комментарием: `{# Theme Switcher ПЕРЕНЕСЁН в User Dropdown (#MOBILE-114) #}`

**[CHANGED] static/css/user_dropdown_unified.css**
- Добавлены стили для `.dropdown-theme-switcher`
- Высота 48px (как остальные кнопки)
- Hover эффект с вращением иконки

### Фидбэк от пользователя (КРИТИЧЕСКИЙ):

#### DESKTOP (Full HD):

1. **#MOBILE-113 РЕГРЕССИЯ:** Drawer смещает контент
   - Теперь sticky bar смещается ВПРАВО
   - Контент ниже смещается ВЛЕВО
   - Раньше sticky bar не двигался

2. **#MOBILE-117:** Кнопки "Тип контента" в drawer - ЛИШНИЕ
   - У нас есть switcher Фото/Альбомы
   - Убрать секцию

3. **#MOBILE-118:** Кнопка "Все" = "Новые"
   - Нет разницы - вводит в заблуждение

4. **#MOBILE-119:** Switcher прыгает
   - Нет фиксированной ширины
   - Кнопка "Добавить" скачет

5. **#MOBILE-120:** Крестик сброса микроскопический
   - Не видно, трудно попасть

6. **#MOBILE-115:** Theme switcher иконка смещена
   - Не в линии с другими иконками
   - Надпись далеко от иконки

#### MOBILE:

7. **#MOBILE-116:** Кнопка "Прочитать все" НЕ вернулась

8. **#MOBILE-122:** View toggle ОГРОМНЫЕ
   - Больше чем аватар пользователя

9. **#MOBILE-123:** Кнопка плюсика
   - Маленькая
   - Значок смещён влево

10. **#MOBILE-124:** Drawer кнопка
    - Огромная рамка
    - Минимальный значок внутри

11. **#MOBILE-121:** ХАОС РАЗМЕРОВ КНОПОК
    - 5-6 разных размеров в sticky bar
    - "В пизду это все" (цитата)

### Статус задач:

- [HYPOTHESIS] #MOBILE-115 - Theme switcher перенесён, но иконка смещена
- [ACTIVE] #MOBILE-113 - РЕГРЕССИЯ drawer смещения
- [ACTIVE] #MOBILE-116 - #MOBILE-124 - новые проблемы зафиксированы
- [BLOCKED] Остальные - отложены до унификации кнопок

### Коммит:

```
[MOBILE] Session 10: Theme switcher в dropdown + критический фидбэк

- Перенесён theme switcher из navbar в user dropdown
- Добавлены стили и JS для переключения тем
- Зафиксирован критический фидбэк:
  - Drawer ВСЁ ЕЩЁ смещает контент (регрессия)
  - Хаос размеров кнопок (5-6 разных)
  - Крестик сброса микроскопический
  - View toggle огромные
  - Кнопка "Прочитать все" пропала

Требуется: УНИФИКАЦИЯ всех кнопок в sticky bar
```

---
