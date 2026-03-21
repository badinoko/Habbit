# GrowReports — Design Tokens
> **Docs Map:** [GROWDIARIES_REFERENCE_DEEP_RESEARCH_PROMPT_v2.md] · [GROWREPORTS_REFERENCE_AUDIT.md] · [GROWREPORTS_COMPONENT_SPECS.md] · [GROWREPORTS_PROGRESS.md]

**Назначение:** Токены дизайна, извлечённые из референса growdiaries.com, и их маппинг в переменные проекта "Беседка".

## Типографика

### Семейства шрифтов
- **Основной**: `-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Noto Sans", Ubuntu, "Droid Sans", "Helvetica Neue", sans-serif`
- **Маппинг**: → `var(--bs-font-sans-serif)` (Bootstrap 5)

### Размеры шрифтов (измерены с реальных страниц)
- **13.6px** — базовый текст (измерено в DOM)
- **19.2px** — заголовки detail страниц (hero titles)
- **48px** — крупные заголовки главной страницы
- **Маппинг**: 
  - 13.6px → `var(--bs-body-font-size)` или 0.85rem
  - 19.2px → `1.2rem` (detail hero)
  - 48px → `3rem` (h1 размер)

### Межстрочный интервал
- **19.4286px** (≈1.43) — базовый line-height
- **68.5714px** (≈1.43) — заголовки
- **Маппинг**: → `var(--bs-body-line-height): 1.43`

## Цвета

### Основная палитра (измерено с реальных страниц)
- **Текст основной**: `rgb(0, 0, 0)` — черный текст
- **Текст заголовков**: `rgb(72, 72, 72)` — #484848 (detail hero)
- **Фон основной**: `rgba(0, 0, 0, 0)` (прозрачный)
- **Маппинг**: 
  - rgb(0,0,0) → `var(--growreports-text)`
  - #484848 → `var(--growreports-text-muted)`
  - transparent → `var(--growreports-bg)`

### Цвета проекта "Беседка"
- **Акцент синий**: `#2EA6FF` (используется для кнопок FAB)
- **Маппинг**: создать CSS custom property `--besedka-primary: #2EA6FF`

## Размеры компонентов (из артефактов)

### Detail Hero
- **375px**: 170×115
- **768px**: 179×121  
- **1440px**: 180×122
- **Маппинг**: responsive `clamp()` функция

### Detail Week Cards
- **375px**: 170×3750 (первая карточка)
- **768px**: 179×209
- **1440px**: 180×210

### Author Profile Stats
- **375px**: 161×48 (top: 188px)
- **764px**: 263×263px аватар, 267×19px статус, различные размеры stats
- **768px**: 267×48 (top: 241px)
- **Маппинг**: flexbox layout с адаптивными размерами

### Detail Timeline/Weeks (реальные измерения 764px)
- **Week Cards**: 674×53px (стандартная), 182×48px (компактная)
- **Изображения**: 674×175px размер галереи
- **Hero Header**: 539×32px заголовок секция

## Viewport/Контейнеры

### Брейкпоинты
- **320px** — mobile mini
- **375px** — mobile
- **768px** — tablet
- **992px** — desktop small
- **1200px** — desktop medium
- **1440px** — desktop large
- **1920px** — desktop extra large

### Маппинг Bootstrap 5
```css
$grid-breakpoints: (
  xs: 0,
  sm: 375px,
  md: 768px,
  lg: 992px,
  xl: 1200px,
  xxl: 1440px
);
```

## Сетка

### Grid параметры (из list metrics)
- **Колонки**: 1 (мобильные), адаптивно для больших экранов
- **Gap**: `normal` (16px default)
- **Маппинг**: CSS Grid с `gap: 1rem`

## CSS Custom Properties для проекта

```css
:root {
  /* Typography */
  --growreports-font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  --growreports-font-size-base: 0.85rem; /* 13.6px */
  --growreports-font-size-xl: 3rem; /* 48px */
  --growreports-line-height: 1.43;
  
  /* Colors */
  --growreports-text: rgb(0, 0, 0);
  --growreports-bg: rgba(0, 0, 0, 0);
  --growreports-primary: #2EA6FF;
  
  /* Spacing */
  --growreports-gap: 1rem;
  
  /* Component sizes */
  --growreports-hero-height-mobile: 115px;
  --growreports-hero-height-tablet: 121px;
  --growreports-hero-height-desktop: 122px;
}
```

## Реализационная матрица

| Референс компонент | Наш файл/компонент | Трудозатраты |
|---|---|---|
| List Grid | `templates/growreports/list.html` | 4-6 часов |
| Detail Hero | `templates/growreports/detail.html` | 3-4 часа |
| Detail Timeline | `templates/growreports/detail.html` | 8-10 часов |
| Author Profile | `templates/growreports/author.html` | 4-6 часов |
| Cards | `templates/includes/partials/growreport_card.html` | 6-8 часов |
| Lightbox | JavaScript + CSS modal | 6-8 часов |

**Общие трудозатраты**: 31-42 часа разработки
