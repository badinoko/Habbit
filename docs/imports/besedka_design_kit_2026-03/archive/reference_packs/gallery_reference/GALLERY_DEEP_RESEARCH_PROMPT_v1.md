# 🖼️ GALLERY DEEP REDESIGN — Master AI Agent Prompt 2025

**Версия:** 1.0 (28 января 2025)  
**Статус:** ГОТОВ К ЗАПУСКУ — ИССЛЕДОВАТЕЛЬСКАЯ ФАЗА  
**Фаза:** Глубокое исследование референса 500px.com для редизайна раздела "Галерея"

---

## 🚨 КРИТИЧЕСКИ ВАЖНО: ПОДХОД ПО ОБРАЗЦУ GROWREPORTS

### ✅ ПРОВЕРЕННАЯ МЕТОДОЛОГИЯ

**Используй точно такой же подход, как для GrowReports:**
- Детальное исследование референса с помощью автоматизации
- Playwright + CDP + DevTools + Content7 MCP
- Сбор артефактов на всех брейкпоинтах (320-1920px)
- Полная фиксация фактов без домыслов
- Structured approach с четкими критериями готовности

### 🎯 РЕФЕРЕНС: 500px.com

**Выбранная платформа**: https://500px.com/
- Современная профессиональная фото-галерея
- Отличный UX и производительность
- Богатый функционал (фильтры, поиск, социальные функции)
- Responsive дизайн
- Качественная реализация lightbox системы

---

## 📋 СТРУКТУРА ИССЛЕДОВАНИЯ

### **🔍 Phase 1: АВТОМАТИЗИРОВАННОЕ ИССЛЕДОВАНИЕ (2-3 дня)**

#### **Основные страницы для анализа:**
1. **Главная галерея** — https://500px.com/popular
2. **Страница фотографии** — клик по любому фото
3. **Профиль фотографа** — клик по автору
4. **Поиск и фильтры** — https://500px.com/search

#### **Артефакты для сбора:**
```
docs/GALLERY_REFERENCE_SPECS/<page>/
├── screens/     # Скриншоты 320/375/768/992/1200/1440/1920
├── dom/         # DOM структура и селекторы
├── metrics/     # Размеры, цвета, типографика
├── flows/       # UX сценарии взаимодействия
├── perf/        # Performance метрики
└── a11y/        # Accessibility отчеты
```

#### **Playwright сценарии для создания:**
```typescript
// tests/playwright/500px_reference_*.spec.ts
- 500px_reference_gallery.spec.ts     // Главная галерея
- 500px_reference_photo_detail.spec.ts // Страница фото
- 500px_reference_profile.spec.ts     // Профиль фотографа  
- 500px_reference_search.spec.ts      // Поиск и фильтры
```

#### **CDP скрипты для обхода ограничений:**
```javascript
// tests/playwright/cdp_capture_*.js
- cdp_capture_gallery.js  // Главная через CDP
- cdp_capture_photo.js     // Детальная страница через CDP
- cdp_capture_profile.js   // Профиль через CDP
```

---

### **📊 Phase 2: АНАЛИЗ И СПЕЦИФИКАЦИЯ (1-2 дня)**

#### **Component Analysis:**
- **Photo Grid System** — layout engine, responsive behavior
- **Photo Card Component** — hover effects, social metrics
- **Lightbox System** — full-screen viewer, navigation
- **Filter & Search** — interface, advanced options
- **Profile Gallery** — portfolio layout, navigation tabs
- **Upload Interface** — drag&drop, metadata forms

#### **Content7 MCP Analysis:**
```markdown
Современные библиотеки для анализа:
□ PhotoSwipe — современный lightbox
□ GLightbox — легкий lightbox 
□ Masonry — cascading grid layout
□ Swiper — touch slider/gallery
□ Isotope — filter & sort layouts
```

#### **Design Tokens Extraction:**
- Color palette и semantic colors
- Typography scale (fonts, sizes, weights)
- Spacing system и grid parameters
- Shadows, borders, animations
- Responsive breakpoints

---

### **🎨 Phase 3: ТЕХНИЧЕСКОЕ ЗАДАНИЕ (1 день)**

#### **Создание итоговых документов:**
- `GALLERY_DESIGN_PROMPT_v1.md` — Master техзадание
- `GALLERY_COMPONENT_SPECS.md` — Спецификации компонентов  
- `GALLERY_TOKENS.md` — Дизайн-токены и CSS переменные
- `GALLERY_IMPLEMENTATION_ROADMAP.md` — План реализации

---

## 🛠️ ИНСТРУМЕНТЫ И КОМАНДЫ

### **Доступные MCP серверы:**
- **🎭 Playwright MCP** — автоматизация браузера, скриншоты
- **📚 Content7 MCP** — анализ современных библиотек

### **Команды для запуска:**
```bash
# Перезапуск Django (при необходимости)
pwsh -NoProfile -File scripts/besedka_ops.ps1 -Action restart_django_full

# Запуск Playwright исследования
npx playwright test tests/playwright/500px_reference_*.spec.ts --reporter line

# CDP анализ (если нужен обход ограничений)
node tests/playwright/cdp_capture_gallery.js
```

---

## 📝 ПРАВИЛА ДОКУМЕНТИРОВАНИЯ

### **В docs/gallery/GALLERY_PROGRESS.md записывать ТОЛЬКО:**
✅ **РАЗРЕШЕНО:**
- `[СОЗДАН] tests/playwright/500px_reference_gallery.spec.ts`
- `[ДОБАВЛЕНО] GALLERY_REFERENCE_SPECS/main_gallery/screens/1440.png`
- `[СОБРАНО] DOM структура главной галереи в dom/main.json`
- `[ИЗВЛЕЧЕНО] Design tokens: цвета #XXX, размеры YYYpx`

❌ **ЗАПРЕЩЕНО:**
- "Исследование завершено"
- "Артефакты готовы"
- "Анализ проведен успешно"
- Любые выводы без конкретных артефактов

---

## 🎯 КРИТЕРИИ ГОТОВНОСТИ ИССЛЕДОВАНИЯ

### **✅ Phase 1 считается завершенной когда:**
- [ ] Все 4 основные страницы проанализированы
- [ ] Собраны скриншоты на всех 7 брейкпоинтах
- [ ] DOM структура зафиксирована в JSON файлах
- [ ] Метрики размеров/цветов/типографики извлечены
- [ ] Performance и A11y отчеты созданы
- [ ] `GALLERY_REFERENCE_AUDIT.md` заполнен ссылками на артефакты

### **✅ Phase 2 считается завершенной когда:**
- [ ] Все основные компоненты описаны в спецификациях
- [ ] Content7 анализ современных библиотек проведен
- [ ] Design tokens извлечены и структурированы
- [ ] Маппинг в наши переменные подготовлен

### **✅ Phase 3 считается завершенной когда:**
- [ ] Master prompt для реализации создан
- [ ] Implementation roadmap с оценками времени готов
- [ ] Техническая архитектура спроектирована
- [ ] Integration plan с существующей галереей подготовлен

---

## 🚀 КОМАНДА К ДЕЙСТВИЮ

**НАЧИНАЙ НЕМЕДЛЕННО С PHASE 1 — АВТОМАТИЗИРОВАННОГО ИССЛЕДОВАНИЯ!**

### **Первые шаги:**
1. Создай Playwright сценарий для https://500px.com/popular
2. Собери скриншоты на всех брейкпоинтах  
3. Извлеки DOM структуру главной галереи
4. Зафиксируй метрики фото-карточек и grid layout
5. Проанализируй performance и accessibility

### **Документирование:**
- Каждый собранный артефакт записывай в progress журнал
- Обновляй GALLERY_REFERENCE_AUDIT.md ссылками на файлы
- Не делай выводов — только фиксируй факты

---

**🎯 ЦЕЛЬ**: Создать такой же детальный анализ 500px.com, какой был сделан для GrowDiaries.com, чтобы затем реализовать современную галерею фотографий в проекте "Беседка" с превосходным UX!

**✨ ИСПОЛЬЗУЙ ВСЕ ДОСТУПНЫЕ ИНСТРУМЕНТЫ БЕЗ ОГРАНИЧЕНИЙ!**
