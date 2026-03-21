# PROMPT: Wave 2 Redesign Implementation

> **РЕЖИМ:** Implementation (code changes)
> **ПРИОРИТЕТ:** High
> **ОЖИДАЕМЫЙ РЕЗУЛЬТАТ:** Обновлённый shell (navbar + sticky bar) + переработанные листинги + детальная гроурепорта
> **ВЕТКА:** main

---

## ОБЯЗАТЕЛЬНО ПРОЧИТАТЬ ПЕРЕД РАБОТОЙ

```
@CLAUDE.md
@docs/artifacts/redesign_2026-03/DESIGN_SYSTEM.md     — дизайн-система (шрифты, палитра, компоненты)
@docs/artifacts/redesign_2026-03/DESIGN_DECISIONS.md   — UX-решения (navbar, sticky, overflow, FAB)
@docs/artifacts/redesign_2026-03/INDEX.md              — инвентаризация всех артефактов
@templates/base.html
@static/css/besedka_themes_v2.css                      — CSS-переменные (первые 200 строк)
```

---

## АРТЕФАКТЫ-РЕФЕРЕНСЫ (полные HTML в папке)

```
@docs/artifacts/redesign_2026-03/wave2/shell-wave2-v1.html            — Shell + News listing
@docs/artifacts/redesign_2026-03/wave2/growreports-listing-wave2.html  — GrowReports listing
@docs/artifacts/redesign_2026-03/wave2/growreport-detail-wave2.html    — GrowReport detail (weeks → entries)
```

Эти файлы — ВИЗУАЛЬНЫЙ РЕФЕРЕНС. Не копировать буквально, а адаптировать под реальные Django-шаблоны.

---

## КОНТЕКСТ

Wave 1 (главная страница) уже имплементирована. Сейчас нужно:
1. Обновить shell (navbar + sticky bar) — компактнее, один ряд на мобилке
2. Переработать листинг новостей — packed 12-column grid
3. Переработать листинг гроурепортов — горизонтальные карточки
4. Переработать детальную гроурепорта — timeline weeks → entries

---

## ФАЗА 1: SHELL — NAVBAR

### Что менять:
- **static/css/navbar_v2.css** — уменьшить высоту, обновить стили
- **static/css/redesign_v1.css** — дополнительные стили

### Ключевые изменения:
- Высота: 56px десктоп, 52px мобилка (было 64px)
- Активный nav link: цвет accent-green + фон accent-green-dim (не подчёркивание)
- Логотип "Беседка": font-family Cormorant Garamond
- Мобилка: section-title цветом var(--bs-accent-green), НЕ серый
- Hamburger hover: background accent-green-dim

### Что НЕ менять:
- HTML-структуру navbar_unified.html (три части: left/center/right)
- JS-логику (toggleSidebar, toggleMainSidebar)
- center_chat.html, center_admin.html

### Коммит: `[REDESIGN-W2] Phase 1: navbar compact + accent-green`

---

## ФАЗА 2: SHELL — STICKY BAR

### Что менять:
- **static/css/unified_sticky_bar.css** — компактнее, один ряд на мобилке
- **templates/includes/partials/unified_sticky_bar.html** — добавить overflow-menu wrapper

### Ключевые изменения:
- Высота: 44px десктоп, 40px мобилка (было 63px)
- Мобилка: скрывать sort buttons, view toggle, filter, mark read
- Мобилка: добавить кнопку overflow (три точки) — при клике показывает dropdown
- Overflow dropdown: сортировка, вид, мои, фильтры, mark read
- FAB "Добавить": `position:fixed; bottom:24px; right:20px` только на мобилке

### Overflow dropdown HTML (добавить в unified_sticky_bar.html):
```html
{# Mobile overflow trigger #}
<button class="bs-sticky-overflow-btn" data-toggle-overflow>
  <i class="fas fa-ellipsis-v"></i>
</button>

{# Overflow menu #}
<div class="bs-sticky-overflow-menu" data-overflow-menu hidden>
  {# Sort buttons, view toggle, etc. — rendered here on mobile #}
</div>
```

### FAB (добавить в base.html, перед закрывающим </body>):
```html
{% if user.is_authenticated %}
<button class="bs-fab bs-fab--mobile-only" id="global-fab" hidden>
  <i class="fas fa-plus"></i>
</button>
{% endif %}
```

### JS: minimal toggle logic в unified_sticky_bar.js

### Что НЕ менять:
- Набор контролов (все остаются, просто перемещаются в overflow на мобилке)
- Desktop layout (один ряд как есть)

### Коммит: `[REDESIGN-W2] Phase 2: sticky bar compact + overflow menu + FAB`

---

## ФАЗА 3: NEWS LISTING

### Что менять:
- **templates/news/news_list.html** — новая grid-структура карточек
- **static/css/news_redesign.css** — packed 12-column grid

### Ключевые изменения:
- CSS Grid 12 columns вместо текущего 4-column uniform grid
- Первая карточка: hero (span 8, горизонтальная: фото 55% + текст)
- Следующие 2: side (span 4, вертикальные)
- Далее: regular (span 4, по 3 в ряд) и wide (span 6, по 2 в ряд)
- Заголовки карточек: font-family Cormorant Garamond для hero
- Мобилка: всё в 1 column

### Data contract (не менять!):
- news_list.html использует `{% for news_item in news_list %}` с unified_list_card.html
- Либо адаптировать unified_list_card, либо создать inline card markup в news_list.html

### Коммит: `[REDESIGN-W2] Phase 3: news listing packed grid`

---

## ФАЗА 4: GROWREPORTS LISTING

### Что менять:
- **templates/growreports/growreports_list.html** — горизонтальные карточки
- **static/css/growreports_redesign.css** — новый card layout

### Ключевые изменения:
- 2-column grid (было 4-column uniform)
- Горизонтальная карточка: фото слева (180px) + инфо справа
- Stage badge на фото (цветной: veg/flower/harvest/seed)
- Progress bar с gradient по стадиям
- Сорт + сидбанк видны
- Week badge
- Featured card: span 2
- Мобилка: 1 column, фото 120px

### Data contract:
- `GrowReport` fields: title, strain_name, breeder_name, status, cover_image, likes_count, comments_count, views_count, current_week
- Stages: seedling, veg, flower, flush, harvest, finished

### Коммит: `[REDESIGN-W2] Phase 4: growreports horizontal cards`

---

## ФАЗА 5: GROWREPORT DETAIL

### Что менять:
- **templates/growreports/report_detail.html** — hero + equipment + timeline
- **templates/growreports/partials/timeline_week.html** — week card + entries
- **CSS в `<style>` блоке report_detail.html** — полная переработка

### Ключевые изменения:

**Hero:**
- Gradient background (veg-bg → body-bg → flower-bg)
- Eyebrow: Caveat font, accent-green
- Title: Cormorant Garamond
- Chips вместо таблицы equipment (сорт, сидбанк, среда, свет, горшок, площадь)
- Progress bar + stage dots

**Equipment bar (под hero):**
- Compact grid: repeat(auto-fit, minmax(130px, 1fr))
- Label (uppercase tiny) + Value

**Week cards:**
- Collapsible (chevron toggle)
- Header: week title (Cormorant) + date range + stage badge (colored)
- Border на hover: accent-green

**Entry (day) внутри week:**
- Header: "Day N" (accent-green) + date + owner edit/delete buttons
- Photos grid: repeat(auto-fill, minmax(80px, 1fr)), aspect-ratio 1:1
- Metrics: inline pills (icon + value + unit)
- Text: border-left 3px accent-green-light + padding-left
- Actions: like/fire/thumbsup buttons + "N комментариев" (collapsible)
- Comments: collapsible per-entry

**Week sidebar nav (desktop only):**
- Sticky, top: shell-h + 1rem
- Colored dots per stage
- Скрыт на мобилке

### Data contract (НЕ менять):
- `report` → GrowReport object
- Weeks grouped in view: `weeks_map[week_index]` → {index, start_date, end_date, entries, stage, photos}
- Entry: day_number, date, stage, text, images (M2M → gallery.Photo), metrics (JSON), likes, comments
- Reactions: ReactionCountMixin на GrowEntry

### Коммит: `[REDESIGN-W2] Phase 5: growreport detail — hero + timeline + entries`

---

## ТЕСТИРОВАНИЕ (после КАЖДОЙ фазы!)

```bash
docker-compose -f docker-compose.local.yml restart django
docker-compose -f docker-compose.local.yml logs -f django 2>&1 | head -50
```

### Playwright (MCP Docker):
```
1. http://host.docker.internal:8001/ — главная
2. http://host.docker.internal:8001/news/ — news listing
3. Любая новость — detail
4. http://host.docker.internal:8001/growreports/ — grow listing
5. Любой гроурепорт — grow detail (проверить: weeks toggle, entries, comments)
6. http://host.docker.internal:8001/gallery/ — gallery listing
7. Dark theme (localStorage theme=dark)
8. Мобилка (375x812): navbar section title, sticky bar overflow, FAB
```

### Чеклист:
- [ ] Нет 500 ошибок
- [ ] Нет TemplateSyntaxError
- [ ] Нет console errors
- [ ] Cormorant Garamond отображается в заголовках
- [ ] Тёмная тема не ломается
- [ ] Мобилка: один ряд sticky bar, overflow работает, FAB видна
- [ ] Week toggle работает (collapse/expand)
- [ ] Комментарии к entry раскрываются

---

## ЗАПРЕТЫ

- НЕ менять views.py, models.py, urls.py
- НЕ удалять CSS-файлы
- НЕ использовать !important
- НЕ хардкодить цвета
- НЕ ломать data contracts (GrowEntry.images → gallery.Photo)
- НЕ ломать SSOT-компоненты (unified_reactions, unified_comment_section, unified_lightbox)
- НЕ трогать chat, admin, store шаблоны
- НЕ делать git push без команды
