# Gallery — Design Tokens
> **Docs Map:** [GALLERY_DEEP_REDESIGN_MASTER_PROMPT_2025.md] · [GALLERY_REFERENCE_AUDIT.md] · [GALLERY_COMPONENT_SPECS.md] · [GALLERY_PROGRESS.md]

**Назначение:** Токены дизайна, извлечённые из референса 500px.com, и их маппинг в переменные проекта "Беседка".

---

## 🎨 Типографика

### Семейства шрифтов (измерено из DOM)
- **Основной**: `Outfit, "Helvetica Neue", HelveticaNeue, Helvetica, TeXGyreHeros, FreeSans, "Nimbus Sans L", "Liberation Sans", Arial, sans-serif`
- **Маппинг**: → `--gallery-font-family` (новая CSS custom property)
- **Интеграция**: Outfit через Google Fonts или аналог

### Размеры шрифтов (измерены с реальных страниц)
- **14px** — базовый текст (body, навигация)
- **16px** — заголовки карточек фото  
- **18px** — заголовки профилей
- **24px** — основные заголовки страниц
- **32px** — крупные заголовки hero секций

**Маппинг**: 
```css
--gallery-font-size-sm: 14px;    /* Базовый текст */
--gallery-font-size-base: 16px;  /* Карточки */
--gallery-font-size-lg: 18px;    /* Профили */
--gallery-font-size-xl: 24px;    /* Заголовки */
--gallery-font-size-xxl: 32px;   /* Hero */
```

### Веса шрифтов
- **400** — обычный текст (normal)
- **500** — средний (medium) для акцентов
- **600** — полужирный (semi-bold) для заголовков
- **700** — жирный (bold) для важных элементов

---

## 🌈 Цвета

### Основная палитра (измерено с реальных страниц)
- **Текст основной**: `rgba(0, 0, 0, 0.65)` — основной контент
- **Текст насыщенный**: `rgba(0, 0, 0, 0.87)` — заголовки, важные элементы  
- **Текст вторичный**: `rgba(0, 0, 0, 0.54)` — описания, метаданные
- **Фон основной**: `rgb(255, 255, 255)` — белый фон
- **Фон прозрачный**: `rgba(0, 0, 0, 0)` — прозрачные элементы

**Маппинг**: 
```css
--gallery-text-primary: rgba(0, 0, 0, 0.65);
--gallery-text-strong: rgba(0, 0, 0, 0.87);
--gallery-text-muted: rgba(0, 0, 0, 0.54);
--gallery-bg-primary: rgb(255, 255, 255);
--gallery-bg-transparent: rgba(0, 0, 0, 0);
```

### Акцентные цвета проекта "Беседка"
- **Первичный синий**: `#2EA6FF` — кнопки, ссылки, активные элементы
- **Второстепенные цвета**: сохраняем существующую палитру проекта

**Интеграция с проектом**:
```css
--gallery-accent-primary: var(--bs-primary, #2EA6FF);
--gallery-accent-secondary: var(--bs-secondary);
```

---

## 📏 Размеры и отступы

### Spacing System (анализ из метрик)
- **4px** — минимальные отступы
- **8px** — малые отступы между элементами
- **16px** — стандартные отступы
- **24px** — большие отступы
- **32px** — секционные отступы
- **48px** — блочные отступы

**Маппинг Bootstrap**:
```css
--gallery-space-xs: 0.25rem;  /* 4px */
--gallery-space-sm: 0.5rem;   /* 8px */
--gallery-space-md: 1rem;     /* 16px */
--gallery-space-lg: 1.5rem;   /* 24px */
--gallery-space-xl: 2rem;     /* 32px */
--gallery-space-xxl: 3rem;    /* 48px */
```

### Responsive Breakpoints (из артефактов)
```css
--gallery-bp-xs: 320px;   /* Mobile portrait */
--gallery-bp-sm: 375px;   /* Mobile landscape */
--gallery-bp-md: 768px;   /* Tablet */
--gallery-bp-lg: 992px;   /* Desktop small */
--gallery-bp-xl: 1200px;  /* Desktop */
--gallery-bp-xxl: 1440px; /* Desktop large */
--gallery-bp-fhd: 1920px; /* Full HD */
```

---

## 🖼️ Photo Grid System

### Grid Parameters (из reference)
- **Columns**: 2 (mobile) → 3 (tablet) → 4 (desktop) → 5 (large desktop)
- **Gap**: 16px (mobile) → 20px (desktop) → 24px (large)
- **Card aspect**: Динамический (сохраняет пропорции фото)

**CSS Grid Variables**:
```css
--gallery-grid-columns-xs: 2;
--gallery-grid-columns-sm: 2;
--gallery-grid-columns-md: 3;
--gallery-grid-columns-lg: 4;
--gallery-grid-columns-xl: 5;
--gallery-grid-gap: 16px;
--gallery-grid-gap-lg: 20px;
--gallery-grid-gap-xl: 24px;
```

---

## 🎭 Lightbox System

### Modal Parameters
- **Background**: `rgba(0, 0, 0, 0.9)` — темный оверлей
- **Content**: `100vw x 100vh` — полноэкранный
- **Image**: `max-width: 90vw, max-height: 90vh` — с отступами
- **Z-index**: `1050` — выше всех элементов

**Lightbox Variables**:
```css
--gallery-lightbox-bg: rgba(0, 0, 0, 0.9);
--gallery-lightbox-z-index: 1050;
--gallery-lightbox-image-max-w: 90vw;
--gallery-lightbox-image-max-h: 90vh;
```

---

## 🔗 Интеграция с существующим проектом

### CSS Custom Properties
```css
:root {
  /* Gallery Typography */
  --gallery-font-family: Outfit, "Helvetica Neue", HelveticaNeue, Helvetica, sans-serif;
  --gallery-font-size-base: 14px;
  
  /* Gallery Colors */
  --gallery-text-primary: rgba(0, 0, 0, 0.65);
  --gallery-bg-primary: rgb(255, 255, 255);
  
  /* Gallery Layout */
  --gallery-grid-gap: 16px;
  --gallery-space-md: 1rem;
  
  /* Integration with Besedka */
  --gallery-accent: var(--bs-primary, #2EA6FF);
}
```

### Conditional Loading
```html
<!-- Загружаем Outfit только для галереи -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&display=swap" rel="stylesheet">
```

---

**📊 Источники данных**: Извлечено из 102 артефактов reference/GALLERY_REFERENCE_SPECS/
**🎯 Применение**: Использовать для создания компонентной системы Gallery
