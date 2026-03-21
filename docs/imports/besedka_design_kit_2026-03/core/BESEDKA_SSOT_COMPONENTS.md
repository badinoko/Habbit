# 🎯 BESEDKA SSOT COMPONENTS - Единые компоненты проекта

**Версия:** 3.0 (22 февраля 2026)
**Статус:** АКТИВНАЯ РАЗРАБОТКА - Sticky Bar пилот (Gallery), карточки унифицированы

## 📚 СВЯЗАННЫЕ ДОКУМЕНТЫ

- **[docs/platform/THEME_AND_UI_REFERENCE.md](docs/platform/THEME_AND_UI_REFERENCE.md)** - текущие темы, CSS переменные, theme API и общие UI-правила
- **[docs/PROJECT_MAP.md](docs/PROJECT_MAP.md)** - текущая архитектура проекта и карта модулей

---

## 📚 Оглавление

**Примечание:** Этот документ дополняет [docs/platform/THEME_AND_UI_REFERENCE.md](docs/platform/THEME_AND_UI_REFERENCE.md), предоставляя технические детали по реализации единого источника истины (SSOT) для компонентов интерфейса.



1. [Философия SSOT](#философия-ssot)
2. [🆕 Sticky Bar (Пилот Gallery)](#sticky-bar-пилот-gallery)
3. [Компонент кнопок (Unified Button)](#компонент-кнопок-unified-button)
4. [Компонент форм (Unified Forms)](#компонент-форм-unified-forms)
5. [Компонент табов (Unified Tabs)](#компонент-табов-unified-tabs)
6. [Компонент сетки (Grid)](#компонент-сетки-grid)
7. [Компонент карточки (Card)](#компонент-карточки-card)
8. [Компонент карточки списка (List Card)](#компонент-карточки-списка-list-card)
9. [Компонент пагинации (Pagination)](#компонент-пагинации-pagination)
10. [Компонент комментариев (Comments)](#компонент-комментариев-comments)
11. [Компонент реакций (Reactions)](#компонент-реакций-reactions)
12. [Компонент лайков (Likes)](#компонент-лайков-likes)
13. [Остаточные проблемы](#остаточные-проблемы)

---

## 🎯 Философия SSOT

**SSOT (Single Source of Truth)** - принцип, при котором каждый компонент определяется ОДИН раз и переиспользуется везде.

### Принципы:
- **Согласованность** - одинаковое поведение во всех разделах
- **Простота поддержки** - изменения в одном месте применяются везде
- **Надежность** - если что-то ломается, ломается везде одинаково (легче найти и исправить)
- **Эталон** - Gallery = пилотный раздел, затем распространяется на News и GrowReports

### Текущее состояние (февраль 2026):
- ✅ Карточки унифицированы через SSOT-компоненты, везде одинаковые
- ✅ Сетка работает на CSS Grid во всех разделах
- ✅ Sticky Bar пилот завершён в Gallery, планируется распространение
- ⚠️ Техдолг: ~2483 !important в CSS (новые добавлять запрещено)

---

## 🆕 Sticky Bar (Пилот Gallery)

### Текущее состояние: ✅ РАБОТАЕТ (Gallery = эталон)

Sicky Bar — панель навигации с glassmorphism, прикреплённая к верху при прокрутке. Пилотная реализация в Gallery, планируется распространение на News и GrowReports.

### Структура Sticky Bar:

```
┌─────────────────────────── STICKY BAR ───────────────────────────┐
│ LEFT                                           RIGHT           │
│ [← Назад] [Фильтры...] [|] [Все] [Поп.] [Обс.]   [🔍] [▼] [✔] [■] [≡] │
└────────────────────────────────────────────────────────────────────┘
```

### Универсальные компоненты (одинаковы воВСЕХ разделах):

**Правый блок (5 кнопок, всегда на одном месте):**
1. Поиск
2. Вызов фильтров (drawer)
3. Прочитать все (mark all read)
4. Переключение вида: сетка (grid)
5. Переключение вида: список (list)

**Левый блок:**
- Кнопка "Назад" (`unified_back_button.html`) — есть везде
- Кнопки фильтрации: Все, Популярные, Обсуждаемые (3 базовых, для FullHD)
- Специфичные кнопки раздела (например, Фото/Альбомы в Gallery)

**Важно:** Правый блок должен быть идентичным во всех разделах. При переходе между Gallery/News/GrowReports пользователь не должен замечать разницу в положении этих кнопок.

### Файлы (эталонные в Gallery):
- CSS: `static/css/gallery_redesign.css` (классы `.gall-sticky-*`)
- JS: `static/js/gallery_redesign.js` (drawer, фильтры, view toggle)
- Templates: `gallery/gallery_list.html`, `gallery/albums_list.html`

### План распространения:
1. ✅ Gallery — реализован на всех уровнях вложенности
2. ⭕ News — следующий этап
3. ⭕ GrowReports — после News
4. ⭕ Извлечение в отдельный SSOT-компонент (#GALL-052)

### CSS классы (Gallery эталон):
```css
.gall-sticky-bar         /* Главный контейнер */
.gall-sticky-left        /* Левая группа кнопок */
.gall-sticky-right       /* Правая группа кнопок */
.gall-sticky-btn         /* Унифицированный стиль кнопки */
.gall-sticky-btn--active /* Активное состояние */
```

---

## Компонент кнопок (Unified Button)

### Текущее состояние: ✅ РАБОТАЕТ

**Файлы:**
- Template: `templates/includes/partials/unified_button.html`
- Стили: `static/css/unified_buttons.css`

### Параметры компонента:
- **type** - Тип кнопки: primary, success, warning, error, neutral, return
- **text** - Текст кнопки
- **size** - Размер: sm, md (default), lg
- **icon** - Font Awesome иконка (опционально)
- **icon_only** - Только иконка без текста (default: False)
- **disabled** - Заблокирована ли кнопка
- **button_type** - Тип: submit, button (default), reset
- **href** - URL для кнопки-ссылки

### Примеры использования:
```django
{% include 'includes/partials/unified_button.html' with
    type='primary'
    text='Сохранить'
    icon='fa-save'
    button_type='submit'
%}

{% include 'includes/partials/unified_button.html' with
    type='return'
    text='Назад'
    icon='fa-arrow-left'
    href='/admin/'
%}
```

### Ключевые особенности:
- ✨ Объёмные кнопки с elevation по умолчанию
- 🎨 Поддержка всех 5 тем через CSS переменные
- 🚫 БЕЗ transform при hover (только border подсветка)
- 📱 Адаптивность для touch-устройств

---

## Компонент форм (Unified Forms)

### Текущее состояние: ✅ РАБОТАЕТ

**Файлы:**
- Стили: `static/css/unified_forms.css`

### Поддерживаемые элементы:
- `.unified-input` - текстовые поля
- `.unified-textarea` - многострочный текст
- `.unified-select` - выпадающие списки
- `.unified-checkbox` - чекбоксы
- `.unified-radio` - радио-кнопки

### Особенности дизайна:
```css
/* Чёткие границы для всех полей */
border: 2px solid var(--bs-border-strong);

/* Контрастный focus */
border-color: var(--bs-primary);
box-shadow: 0 0 0 3px rgba(46, 166, 255, 0.15);
```

### Размеры:
- `.unified-input--sm` - маленький
- По умолчанию - средний
- `.unified-input--lg` - большой

### Группировка:
```html
<div class="unified-form-group">
    <label class="unified-form-label">Email</label>
    <input type="email" class="unified-input">
    <div class="unified-form-help">Введите ваш email</div>
</div>
```

---

## Компонент табов (Unified Tabs)

### Текущее состояние: ✅ РАБОТАЕТ

**Файлы:**
- Стили: `static/css/unified_tabs.css`

### Структура:
```html
<ul class="unified-tabs">
    <li class="unified-tab unified-tab--active">Активный</li>
    <li class="unified-tab">Неактивный</li>
</ul>
```

### Варианты стилей:
- `.unified-tabs--pills` - закруглённые табы
- `.unified-tabs--boxed` - табы в контейнере
- `.unified-tabs--underline` - только нижняя линия
- `.unified-tabs--vertical` - вертикальные табы

### Особенности:
- 📦 Объёмные табы с box-shadow
- 🎯 Активный таб: border 2px solid primary
- 🚫 НЕТ цветной подложки для активного таба
- ✨ Анимация при переключении

---

## Компонент сетки (Grid)

### Текущее состояние: ✅ РАБОТАЕТ

#### Файл: `templates/includes/partials/unified_grid.html`

Сетка работает на CSS Grid во всех разделах (Gallery, News, GrowReports). Адаптивные колонки: 1 → 2 → 3 → 4 в зависимости от ширины экрана.

```css
/* Брейкпоинты */
@media (min-width: 640px)  { 2 колонки }
@media (min-width: 1024px) { 3 колонки }
@media (min-width: 1280px) { 4 колонки }
```

### Использование:
```django
{% include 'includes/partials/unified_grid.html' with
    items=photo_list
    grid_type='grid'
%}
```

---

## Компонент карточки (Card)

### Текущее состояние: ✅ РАБОТАЕТ

Карточки унифицированы через SSOT. Везде одинаковый размер, структура и поведение.

#### Файлы:
- Template: `templates/includes/partials/unified_card.html`
- CSS: `static/css/unified_cards.css`
- CSS классы: `.bs-card`, `.bs-card-grid`, `.bs-card-image`, `.bs-card-body`, `.bs-card-title`, `.bs-card-meta`

### Использование:
```django
{% include 'includes/partials/unified_card.html' with
    card_data=news_item
    grid_item=True
    compact_mode=False
%}
```

### Правила:
- Высота только через `var(--card-min-height)` (не хардкодить!)
- НЕ переопределять в специфичных CSS файлах разделов
- НЕ использовать !important для карточек

---

## Компонент карточки списка (List Card)

### Текущее состояние: ✅ РАБОТАЕТ

Карточка для отображения в сетке и списке. Используется в Gallery (фото и альбомы), планируется применение в News и GrowReports.

#### Файл:
- Template: `templates/includes/partials/unified_list_card.html`

### Использование:
```django
{# Карточка фото #}
{% include 'includes/partials/unified_list_card.html' with
    item=photo
%}

{# Карточка альбома #}
{% include 'includes/partials/unified_list_card.html' with
    item=album
    is_album=True
%}
```

---

## 📄 Компонент пагинации (Pagination)

### Текущее состояние: ⚠️ ПРОБЛЕМЫ С КОНФИГУРАЦИЕЙ

#### Файл: `templates/includes/partials/_unified_pagination.html` ✅

### Проблемы:
- News/Store показывают "Загрузить еще" (не передают `disable_load_more`)
- Несогласованное поведение между разделами

### ✅ РЕШЕНИЕ:

```python
# views.py - для ВСЕХ разделов
context['disable_load_more'] = True  # Отключаем везде
```

Или удалить кнопку "Загрузить еще" совсем из шаблона.

---

## 💬 Компонент комментариев (Comments)

### Текущее состояние: ✅ ХОРОШИЙ ПРИМЕР SSOT

#### Файлы:
- `templates/includes/partials/unified_comments_block.html`
- `static/js/unified_comments.js`
- `static/css/unified_comments_modal.css`

### Почему работает:
- Один компонент для всех разделов
- Единая логика обработки
- Если ломается - ломается везде одинаково

---

## Компонент лайков (Likes)

### Текущее состояние: ✅ РАБОТАЕТ

#### Файлы:
- `templates/includes/partials/unified_like_button.html`
- `core/views.py:unified_like_api`

Единый API endpoint, один шаблон, переиспользуется везде.

---

## Компонент реакций (Reactions)

### Текущее состояние: ✅ РАБОТАЕТ

Универсальный 10-emoji picker для реакций на любой контент.

#### Файл:
- Template: `templates/includes/partials/unified_reactions.html`

### Типы реакций (10):
`heart`, `thumbsup`, `thumbsdown`, `laugh`, `wow`, `think`, `sad`, `angry`, `fire`, `poop`

### Использование:
```django
{% include 'includes/partials/unified_reactions.html' with
    content_type='photo'
    object_id=photo.id
%}
```

---

## Дополнительные SSOT-компоненты

### Кнопка "Назад" (Back Button)
- Template: `templates/includes/partials/unified_back_button.html`
- Используется в sticky-bar и детальных страницах

### Detail Footer (Back to Top)
- Template: `templates/includes/partials/unified_detail_footer.html`
- Кнопка возврата наверх страницы

### Detail Hero
- Template: `templates/includes/partials/unified_detail_hero.html`
- Hero-секция для детальных страниц (фото, альбом, новость)

### Skeleton Card
- Template: `templates/includes/partials/unified_skeleton_card.html`
- Placeholder-карточка для загрузки

---

## Остаточные проблемы

### 1. Пагинация
"Показать ещё" может появляться неконсистентно между разделами (нужна проверка).

### 2. Техдолг !important
~2483 использования !important. Новые добавлять запрещено. Постепенно сокращать.

### 3. Sticky Bar ещё не извлечён в SSOT
Пока реализован в Gallery с `.gall-*` префиксами. Задача #GALL-052: извлечь в универсальный компонент.

---

## Чек-лист для новых разделов

При создании нового раздела:

- [ ] Проверить `templates/includes/partials/` на существующие компоненты
- [ ] Использовать `unified_grid.html` + `unified_card.html` + `unified_list_card.html`
- [ ] Использовать `unified_reactions.html` и `unified_comment_section.html`
- [ ] НЕ хардкодить цвета (только CSS переменные)
- [ ] НЕ добавлять !important
- [ ] НЕ переопределять `--card-min-height`
- [ ] Смотреть на Gallery как эталон для sticky-bar и layout

---

**Правило:** Если компонент уже существует — используй его, не создавай новый!

---

## 🛠️ ADMIN SSOT - Административные компоненты

**КОНТЕКСТ:** Унификация между 4 админками проекта (Owner, Moderator, Store Owner, Store Admin). НЕ унифицировать с основным сайтом - это отдельные типы страниц.

### 📋 ТЕКУЩИЙ ФОКУС: Owner + Moderator админки

#### ✅ ЧТО УНИФИЦИРОВАТЬ:
1. **Навбар** - использовать основной проект (`templates/includes/navigation.html`)
2. **Система тем** - admin-light/admin-dark через `localStorage.adminTheme`
3. **Базовые стили** - кнопки, формы, таблицы, типографика
4. **CSS переменные** - изолированные `--admin-*` токены

#### ❌ ЧТО НЕ УНИФИЦИРОВАТЬ:
- С основным сайтом (разные контексты)
- Специфичную логику каждой админки
- Content-типы и данные

#### 🔧 СТРУКТУРА АДМИНСКИХ КОМПОНЕНТОВ:
```
static/admin/css/
├─ admin_base.css         # --admin-* переменные
├─ admin_navbar.css       # интеграция основного навбара
└─ admin_unified.css      # единые стили между админками

static/css/
├─ besedka_master_themes.css     # ЕДИНАЯ система 5 тем для всего сайта
└─ static/js/besedka_master_theme_switcher.js  # единый API тем

templates/admin/partials/
└─ admin_navbar.html      # адаптированный навбар с единым переключателем
```

#### 🎯 ПРИНЦИПЫ:
- **Одна админка исправлена** = применить ко всем остальным
- **Изоляция от основного сайта** - никаких конфликтов CSS/JS
- **Bootstrap 5 совместимость** с основным проектом

### 🎨 РЕАЛИЗОВАННЫЕ ADMIN SSOT КОМПОНЕНТЫ (ОБНОВЛЕНО 2025-09-13):

#### ✅ **ЕДИНАЯ СИСТЕМА ТЕМ - РЕВОЛЮЦИЯ ЗАВЕРШЕНА:**
1. **`static/css/besedka_master_themes.css`** - 5 тем для ВСЕГО сайта включая админки
2. **`static/js/besedka_master_theme_switcher.js`** - единый API переключения тем  
3. **CSS мост Django Daisy** → автоматическое применение тем к админкам
4. **templates/admin/partials/admin_navbar_unified.html`** - единый навбар для всех админок
5. **`static/admin/css/jazzmin_fixes_modern.css`** - исправления багов Jazzmin
6. **`static/admin/css/admin_mobile_responsive.css`** - mobile-first адаптивность

#### ✅ **РЕЗУЛЬТАТЫ РЕВОЛЮЦИИ ТЕМ - 85% ГОТОВНОСТИ:**
- ✅ **Единые темы работают везде** - основной сайт + все админки
- ✅ **Конец визуальному браку** - нет различий при переключении тем
- ✅ **Django Daisy интегрирован** - через CSS мост переменных
- ✅ **5 тем доступны везде** - Classic, Dark, Warm, Cold, Contrast
- ✅ **Переключатель в навбаре** - единый интерфейс управления

#### 📱 **MOBILE-FIRST ОСОБЕННОСТИ:**
- Touch-friendly элементы минимум 44px
- Полноэкранный sidebar на мобильных
- Адаптивные сетки: 1→2→3→4 колонки
- Оптимизация производительности на слабых устройствах
---
