# Беседка — Дизайн-система (Design System)

> Единый источник правды по визуальному языку проекта.
> Обновлено: 2026-03-12

---

## 1. Типографика

### Шрифты (Google Fonts, кириллица)

| Роль | Шрифт | Подключение | Где используется |
|------|-------|-------------|------------------|
| **Заголовки** | Cormorant Garamond 600/700 + italic | `--bs-font-display` | H1-H3, card titles, section titles, логотип "Беседка" |
| **Акцент/eyebrow** | Caveat 500/700 | `--bs-font-handwritten` | Подзаголовки-eyebrow ("Гроурепорт #42"), декоративные метки |
| **Тело текста** | Inter 400/500/600/700/800 | `--font-body` (уже в проекте) | Все остальное: параграфы, кнопки, метаданные, UI |

### Правила использования

- **Cormorant Garamond** — ТОЛЬКО для заголовков. Никогда для мелкого текста. letter-spacing: -0.02em. line-height: 1.1-1.2.
- **Caveat** — ТОЛЬКО для декоративных акцентов. Размер >= 1rem. Цвет всегда accent-green.
- **Inter** — всё остальное. Базовый размер 0.9-1rem. Для мелких элементов 0.72-0.82rem.
- **На мобилке**: заголовки clamp() от 1.5rem до 2.5rem. Тело: min 0.88rem.

---

## 2. Палитра

### Основные цвета

| Токен | Light | Dark | Назначение |
|-------|-------|------|------------|
| `--bs-accent-green` | #2d8a56 | #4caf50 | Основной акцент, ботанический |
| `--bs-accent-green-light` | #e8f5e9 | rgba(76,175,80,0.12) | Фоны кнопок, badges, hover |
| `--bs-accent-green-dim` | rgba(45,138,86,0.08) | rgba(76,175,80,0.06) | Подсветка активных nav links |
| `--bs-accent-amber` | #d4a24e | #ffc107 | Вторичный (harvest, warning) |
| `--bs-accent-amber-light` | #fff8e1 | rgba(255,193,7,0.12) | Фон amber badges |
| `--bs-accent-rose` | #c06c84 | #f48fb1 | Третичный (flower stage) |
| `--bs-accent-rose-light` | #fce4ec | rgba(244,143,177,0.12) | Фон rose badges |

### Стадии гроурепорта

| Стадия | CSS-переменная | Light | Фон |
|--------|---------------|-------|-----|
| Проращивание | `--stage-seed` | #78909c | #eceff1 |
| Вегетация | `--stage-veg` | #2d8a56 | #e8f5e9 |
| Цветение | `--stage-flower` | #e91e63 | #fce4ec |
| Промывка | `--stage-flush` | #0288d1 | #e1f5fe |
| Харвест | `--stage-harvest` | #ff8f00 | #fff8e1 |

### Базовые токены (из besedka_themes_v2.css)

| Токен | Light | Dark |
|-------|-------|------|
| `--bs-body-bg` | #FDFCFA | #1e293b |
| `--bs-card-bg` | #ffffff | #1e293b |
| `--bs-text-primary` | #1e293b | #ffffff |
| `--bs-text-secondary` | #64748b | #a8a8ad |
| `--bs-text-muted` | #94a3b8 | #6c757d |
| `--bs-border-subtle` | rgba(0,0,0,0.06) | rgba(255,255,255,0.05) |

---

## 3. Компоненты

### Shell (Navbar + Sticky Bar)

**Navbar:**
- Высота: 56px (десктоп), 52px (мобилка)
- Фон: glass — `rgba(253,252,250,0.88)` + `blur(24px)`
- Структура: `[гамбургер | логотип] [центр: nav links] [bell | avatar]`
- Мобилка: центр заменяется на `section-title` цветом accent-green

**Sticky Bar:**
- Высота: 44px (десктоп), 40px (мобилка)
- Фон: glass, аналогичен navbar
- Мобилка: ОДИН ряд, overflow-меню (три точки) для остальных контролов
- FAB для "Добавить" на мобилке (правый нижний угол, 52x52px, border-radius 16px)

### Карточки

| Свойство | Значение |
|----------|----------|
| border-radius | 16-18px |
| border | 1px solid var(--bs-border-subtle) |
| shadow | var(--bs-shadow-sm) |
| hover | translateY(-3..4px) + var(--bs-shadow) |
| transition | 0.3s cubic-bezier(0.4,0,0.2,1) |

### Кнопки

| Тип | Стиль |
|-----|-------|
| Primary (зелёная) | bg: accent-green, color: #fff, border-radius: 8-12px, shadow |
| Ghost | bg: transparent, border: 1px solid border-subtle, border-radius: 8-10px |
| Icon (30x30) | border: 1px solid border-subtle, border-radius: 8px |
| FAB (52x52) | bg: accent-green, border-radius: 16px, shadow: 0 6px 20px rgba(45,138,86,0.35) |

### Badges

- border-radius: 6-8px
- font-size: 0.65-0.72rem, font-weight: 700
- text-transform: uppercase, letter-spacing: 0.03-0.06em
- Фон: rgba + backdrop-filter blur

### Метрики (GrowReports)

- Inline pills: border-radius 8px, background #f8fafc, border 1px solid border-subtle
- Иконка + значение + единица
- font-size: 0.75rem
- На мобилке: 0.7rem, padding уменьшен

---

## 4. Сетки (Layouts)

### Листинг новостей
- 12-column CSS Grid
- Hero card: span 8 (горизонтальная), side cards: span 4
- Regular cards: span 4 (по 3 в ряд)
- Wide cards: span 6 (по 2 в ряд)
- Мобилка: 1 column, всё вертикальное

### Листинг гроурепортов
- 2-column grid
- Горизонтальные карточки (фото слева 180px, инфо справа)
- Featured card: span 2 (фото 280px)
- Мобилка: 1 column, фото 120px

### Листинг галереи (фото)
- 4-column grid, варьирующиеся aspect-ratio через nth-child
- Hover overlay с gradient + info
- Мобилка: 2 columns, 480px: 1 column

### Листинг галереи (альбомы)
- 4-column grid
- Обложка: 2x2 мини-grid фотографий
- Мобилка: 2 columns

### Детальные страницы (новость, фото)
- 2-column: контент (flex 1) + sidebar (320px, sticky)
- Мобилка: 1 column, sidebar под контентом

### Детальная гроурепорта
- Контент (flex 1) + week-nav sidebar (180px, sticky)
- Week cards: collapsible, entries внутри
- Мобилка: 1 column, week-nav скрыт

---

## 5. Анимации и эффекты

### Glassmorphism
- background: rgba(..., 0.88)
- backdrop-filter: blur(24px)
- border: 1px solid var(--bs-border-subtle)
- Применяется: navbar, sticky bar, dropdown меню

### Hover эффекты
- Карточки: translateY(-3..4px) + shadow усиление
- Фото: img scale(1.04-1.06) через overflow:hidden
- Ссылки: color transition 0.2s
- Кнопки: border-color + color transition

### Градиенты
- Hero backgrounds: linear-gradient(135deg, stage-veg-bg, body-bg, stage-flower-bg)
- Progress bars: linear-gradient(90deg, stage-veg, stage-flower)
- Photo overlay: linear-gradient(to top, rgba(0,0,0,0.6), transparent)

---

## 6. Breakpoints

| Имя | Ширина | Что меняется |
|-----|--------|-------------|
| Desktop | >= 768px | Полный navbar, sticky bar в один ряд, multi-column grids |
| Mobile | < 768px | Navbar: section-title вместо links, sticky: overflow menu, FAB, 1-2 column grids |
| Compact | < 480px | 1 column everywhere, уменьшенные font-size и padding |

Внутри мобильного диапазона вёрстка РЕЗИНОВАЯ (flex, %, clamp).
НЕ создавать отдельные правила для 375px, 390px, 430px и т.д.

---

## 7. Запреты

- НЕ использовать `!important`
- НЕ хардкодить цвета (только CSS-переменные)
- НЕ inline styles (style="...")
- НЕ дублировать SSOT-компоненты
- НЕ убирать hamburger, bell, user dropdown, sticky bar
- Все новые стили — через `redesign_v1.css` или компонентные CSS
