# Redesign Wave 2 — Соглашения и решения

> **Дата:** 2026-03-12
> **Статус:** Active — в работе

---

## Утверждённые визуальные решения

### Навбар (все устройства)

**Десктоп (>=768px):**
- Слева: гамбургер + логотип "Беседка" (Cormorant Garamond)
- Центр: кнопки разделов (Новости, Магазин[frozen], Гроурепорты, Галерея, Чат)
- Справа: колокольчик уведомлений + user dropdown
- Три состояния центральной зоны: public / admin / chat

**Мобилка (<768px):**
- Гамбургер | Логотип + название текущего раздела | колокольчик | аватар
- Название раздела — ВЫДЕЛЯТЬ ЦВЕТОМ (не серый текст как сейчас)
- Навигация по разделам — в sidebar (гамбургер)

**Sidebar (утверждён):**
- Минимальный набор: Новости, Магазин (с замком), Гроурепорты, Галерея, Чат
- Иконки FontAwesome + текст
- Магазин заглушен визуально

### Sticky Bar

**Десктоп (>=768px):**
- Один ряд: назад | специфичные контролы раздела | поиск, фильтры, вид, добавить
- Визуально — продолжение навбара (единый glass-stack)

**Мобилка (<768px) — НОВОЕ РЕШЕНИЕ:**
- СТРОГО ОДИН РЯД (не два как раньше!)
- Контролы первого уровня: назад, свитчер/название, поиск, overflow (три точки)
- Overflow-dropdown: сортировка, вид, мои, mark read, фильтры
- FAB для "Добавить" на мобилке
- Суммарная высота navbar + sticky: ~104px (вместо 127px)

---

## Утверждённый дизайн-язык

### Типографика
- Заголовки: Cormorant Garamond (serif с кириллицей)
- Акценты: Caveat (рукописный)
- Тело: Inter

### Палитра (ботаническая)
- Зелёный: #2d8a56 — основной акцент
- Янтарный: #d4a24e — secondary
- Розовый: #c06c84 — tertiary
- CSS-переменные --bs-accent-*

### Стадии гроурепорта (цветовые коды)
- Проращивание (seed): #78909c серый
- Вегетация (veg): #2d8a56 зелёный
- Цветение (flower): #e91e63 розовый
- Промывка (flush): #0288d1 синий
- Харвест (harvest): #ff8f00 янтарный

---

## Статус по страницам

### Главная (homepage)
- Статус: Имплементирована, prototype-like

### Галерея (листинг фото/альбомов)
- Статус: ОК, masonry + hover overlay

### Листинг новостей
- Статус: Wave 2 — packed 12-column grid (hero 8col + side 4col)
- Артефакт: `wave2/shell-news-wave2-v1.html`

### Листинг гроурепортов
- Статус: Wave 2 — горизонтальные карточки с progress bar
- Артефакт: `wave2/growreports-listing-wave2-v1.html`

### Детальная новость
- Статус: ОК (двухколоночный layout + Cormorant)

### Детальная фото
- Статус: ОК (blur-bg hero + sidebar)

### Детальная гроурепорта
- Статус: Wave 2 — полный прототип с реальной иерархией
- Артефакт: `wave2/growreport-detail-wave2-v1.html`
- Структура:
  - Hero: gradient bg, chips вместо equipment bar, Cormorant title, progress + stage dots
  - Equipment bar: компактная сетка под hero
  - Week cards: collapsible, цветной stage badge, chevron toggle
  - Entry (day): фото grid → метрики pills → текст (green border-left) → actions
  - Comments: collapsible per-entry
  - Owner actions: edit/delete per entry
  - "Добавить запись" dashed button внизу каждой недели
  - Sidebar: sticky week navigator с цветными точками по стадиям (скрыт на мобилке)

---

## Реальная структура данных GrowReport (для имплементации)

```
GrowReport (model)
  ├── title, strain_name, breeder_name, medium, status, start_date
  ├── room_type, watering_type, lighting, genetics
  ├── cover_image, likes_count, comments_count, views_count
  └── entries (GrowEntry, FK → GrowReport)
        ├── day_number, date, stage, text
        ├── images (M2M → gallery.Photo)
        ├── metrics (JSONField: height, ec, ph, rh, temp_day, temp_night, ppfd...)
        ├── likes (GrowEntryLike)
        ├── comments (GrowEntryComment, 3 уровня вложенности)
        └── revisions (GrowEntryRevision, для модерации)

Группировка в view:
  Week = entries grouped by ((day_number - 1) // 7) + 1
  Каждая неделя: index, start_date, end_date, entries[], stage, photos[]
  Entries внутри недели: sorted by day_number asc
```

---

## Известные проблемы

1. News desktop composition — featured card ломает сетку
2. Sticky bar на мобилке — два ряда
3. Navbar section title — серый невыразительный
4. Legacy-шаблоны (wizard) — без sticky bar
5. Страница добавления/редактирования entry — очень плохая

---

## Запреты

- НЕ убирать hamburger, bell, user dropdown
- НЕ убирать sticky bar
- НЕ ломать data contracts (GrowEntry.images → gallery.Photo)
- НЕ использовать !important
- НЕ хардкодить цвета
- SSOT-компоненты не дублировать
