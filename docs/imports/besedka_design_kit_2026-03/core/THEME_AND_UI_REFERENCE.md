# Theme System & UI Reference

**Источник:** Консолидировано из BESEDKA_THEME_SYSTEM.md v3.0 и BESEDKA_UI_STANDARDS.md v7.0
**Дата консолидации:** 2026-02-22

> Базовая информация о темах (файлы, API) -- см. CLAUDE.md.
> SSOT компоненты -- см. BESEDKA_SSOT_COMPONENTS.md в корне проекта.

---

## 1. CSS переменные по темам

### Основные цвета

| Переменная | Light | Dark | Cupcake | Emerald | Synthwave |
|------------|-------|------|---------|---------|-----------|
| `--primary-color` | #2EA6FF | #5294E2 | #65C3C8 | #66CC8A | #E779C1 |
| `--success-color` | #30D158 | #30D158 | #1DB584 | #1BC276 | #06FFA5 |
| `--error-color` | #FF453A | #FF453A | #E8175D | #E93D26 | #FF6B9D |
| `--warning-color` | #FAA352 | #FFC069 | #F7C948 | #F7C948 | #FFFF00 |

### Фоны

| Переменная | Light | Dark | Cupcake | Emerald | Synthwave |
|------------|-------|------|---------|---------|-----------|
| `--body-bg` | #FDFCFA | #17212B | #FAF7F5 | #ECFDF5 | #16071E |
| `--card-bg` | #FFFFFF | #1E2733 | #FFFFFF | #FFFFFF | #24153B |
| `--input-bg` | #FFFFFF | #1E2733 | #FFFFFF | #FFFFFF | #24153B |
| `--hover-bg` | #F0F0F0 | #2C353F | #F2F2F2 | #F0FDF4 | #3D2C5A |

### Текст

| Переменная | Light | Dark | Cupcake | Emerald | Synthwave |
|------------|-------|------|---------|---------|-----------|
| `--text-primary` | #000000 | #FFFFFF | #291334 | #14532D | #FFFFFF |
| `--text-secondary` | #6C757D | #A8A8AD | #6F6F6F | #6B7280 | #B794F6 |
| `--text-muted` | #8E8E93 | #6C757D | #999999 | #9CA3AF | #9F7AEA |
| `--text-link` | #2EA6FF | #5294E2 | #65C3C8 | #66CC8A | #E779C1 |

### Границы

| Переменная | Light | Dark | Cupcake | Emerald | Synthwave |
|------------|-------|------|---------|---------|-----------|
| `--border-color` | #E0E0E0 | #2D3845 | #E9E7E7 | #D1FAE5 | #553C9A |

---

## 2. Theme API

### JavaScript API (besedka_master_theme_switcher.js)

```javascript
BesedkaMasterThemes.apply('synthwave');  // Конкретная тема
BesedkaMasterThemes.toggle();            // light <-> dark
BesedkaMasterThemes.cycle();             // Циклическое переключение 5 тем
BesedkaMasterThemes.current();           // Текущая тема
BesedkaMasterThemes.themes;              // Список всех тем
```

### Обратная совместимость

```javascript
window.stableThemeToggle();    // -> BesedkaMasterThemes.toggle()
window.applyTheme('dark');     // -> BesedkaMasterThemes.apply('dark')
```

### Подключение

```html
<link rel="stylesheet" href="{% static 'css/besedka_master_themes.css' %}">
<script src="{% static 'js/besedka_master_theme_switcher.js' %}"></script>
```

Темы переключаются через `data-theme` на `<html>`:
`<html data-theme="light|dark|cupcake|emerald|synthwave">`

---

## 3. Django Daisy CSS мост

Django Daisy использует `.bg-base-100`, `.text-base-content` -- они НЕ связаны с нашими переменными.

Решение (уже в besedka_master_themes.css):
```css
.bg-base-100 { background-color: var(--card-bg) !important; }
.text-base-content { color: var(--text-primary) !important; }
.drawer-side { background-color: var(--card-bg) !important; }
```

---

## 4. Как добавить новую CSS переменную

1. Добавить значение во все 5 тем в `besedka_master_themes.css`:
```css
:root, [data-theme="light"] { --my-var: #value; }
[data-theme="dark"] { --my-var: #value; }
[data-theme="cupcake"] { --my-var: #value; }
[data-theme="emerald"] { --my-var: #value; }
[data-theme="synthwave"] { --my-var: #value; }
```
2. Использовать: `color: var(--my-var);`

---

## 5. Визуальный язык

### Типографика
- Основной шрифт: Inter
- Размеры: относительные единицы (rem)

### Иконография
- Библиотека: Font Awesome

### Сетка
- Модульная: 8px base grid
- Layout: Flexbox и Grid

### Адаптивная сетка карточек
```css
.unified-masonry {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1.5rem;
    padding: 1rem;
}
@media (min-width: 768px) {
    .unified-masonry { grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); }
}
@media (min-width: 1200px) {
    .unified-masonry {
        grid-template-columns: repeat(4, 1fr);
        max-width: 1400px;
        margin: 0 auto;
    }
}
```

---

## 6. Glassmorphism стиль

```css
.modern-element {
    background: linear-gradient(135deg,
        oklch(98% 0.01 240 / 0.9),
        oklch(96% 0.02 240 / 0.95));
    backdrop-filter: blur(20px) saturate(1.1);
    border: 1px solid oklch(90% 0.02 240 / 0.3);
    box-shadow:
        0 1px 3px oklch(20% 0.05 240 / 0.12),
        0 8px 24px oklch(20% 0.05 240 / 0.08);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.modern-element:hover {
    transform: translateY(-2px) scale(1.01);
}
```

---

## 7. UI паттерны

### Уведомления
- Функция: `window.showNotification()`
- Источник: `unified_notifications.js`
- Типы: `success` (зеленый), `error` (красный), `info` (синий), `warning` (оранжевый)
- Стиль: glassmorphism + backdrop-filter blur(20px), по центру экрана

### Система лайков
- Необратимое действие (1 пользователь = 1 лайк)
- Компонент: `unified_like_button.html`
- Кнопка становится disabled после нажатия

### Модальные окна
- SweetAlert2 для подтверждений
- Цвета через CSS переменные:
```javascript
const primaryColor = getComputedStyle(document.documentElement)
    .getPropertyValue('--primary-color').trim();
```

---

## 8. Рекомендуемые базовые классы

- `core.base_views.UnifiedListView` -- базовый View для списков
- `templates/base_list_page.html` -- шаблон-скелет для списков
- `static/css/unified_styles.css` -- базовые глобальные стили

---

## 9. Чек-лист для новых компонентов

- Все цвета через CSS переменные (не HEX)
- Работает во всех 5 темах
- Django Daisy элементы имеют CSS мост
- Нет `!important` без критической причины
- Соответствие WCAG 2.1 для доступности
