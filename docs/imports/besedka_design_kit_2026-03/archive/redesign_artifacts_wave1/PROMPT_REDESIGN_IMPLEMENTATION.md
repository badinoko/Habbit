# PROMPT: Visual Redesign Implementation

> **РЕЖИМ:** Implementation (code changes)
> **ПРИОРИТЕТ:** High — визуальный редизайн основных страниц
> **ОЖИДАЕМЫЙ РЕЗУЛЬТАТ:** Обновлённые CSS + templates без потери функциональности
> **ВЕТКА:** main (работаем в main)

---

## КОНТЕКСТ

Визуальный редизайн шести основных страниц Беседки.
Утверждены 6 HTML-прототипов (артефакты Claude). Стиль: ботаническая палитра,
типографика Cormorant Garamond для заголовков + Inter для текста, тёплые природные
акценты вместо холодного монохромного UI.

**ФИЛОСОФИЯ:** Это "смена пиджака" — меняется CSS и HTML-разметка шаблонов,
НЕ ломается backend-логика, НЕ меняются views, models, URLs.

---

## ЧТО ЧИТАТЬ ПЕРЕД НАЧАЛОМ

```
@CLAUDE.md
@templates/base.html
@static/css/besedka_themes_v2.css (первые 200 строк — CSS-переменные)
@static/css/unified_cards.css
@static/css/unified_grid.css
@templates/includes/partials/unified_card.html
```

---

## ПРОТОТИПЫ (РЕФЕРЕНСЫ)

Все 6 прототипов лежат в `docs/artifacts/redesign_2026-03/`.
Прототипы НЕ являются финальным кодом — они показывают ЦЕЛЕВОЙ визуал.

### Прототип 1: Главная страница (`home/homepage-redesign-v1.html`)
- Hero-секция с Cormorant Garamond заголовками
- Stat-карточки (гроурепорты, фото, сорта, участники)
- 3 секции: новости, гроурепорты, галерея
- Community CTA strip внизу

### Прототип 2: Листинг новостей (`listing/listing-redesign-v1.html`)
- Сетка 4 колонки, первая карточка "featured" (2x2)
- Компактные карточки с бейджами и аватарками
- Cormorant для заголовков карточек

### Прототип 3: Листинг галереи (`listing/gallery-list-redesign-v1.html`)
- Фото-сетка 4 колонки с варьирующимися aspect-ratio
- Hover overlay: название + лайки/комменты
- Свитчер Фото/Альбомы в sticky-bar (переключает контент без перезагрузки в прототипе, в реальности — разные URL)
- Альбомы: карточки с 2x2 превью обложки
- Sticky bar: назад | свитчер | фильтры | мои фото | поиск | сетка/список | добавить

### Прототип 4: Детальная новость (`detail/news-detail-redesign-v1.html`)
- Двухколоночный layout (статья + sidebar)
- Cormorant для заголовка и H2/H3
- Sidebar: автор, теги, похожие

### Прототип 5: Детальная фото (`detail/photo-detail-redesign-v1.html`)
- Двухколоночный layout (фото-просмотрщик + sidebar)
- Hero с blur-фоном и centered image
- Навигация prev/next внутри альбома (стрелки + sidebar)
- Sidebar: альбом, EXIF-инфо, навигация, похожие фото

### Прототип 6: Детальный гроурепорт (`detail/growreport-detail-redesign-v1.html`)
- Hero с info-карточками + progress bar + stage dots
- Вертикальный timeline по неделям
- Entry cards: текст + photo grid + metrics strip + reactions

---

## ФАЗА 0: ПОДГОТОВКА (ОБЯЗАТЕЛЬНО ПЕРВЫМ ДЕЛОМ)

### 0.1 Добавить шрифты в base.html

В `<head>` секцию base.html, ПОСЛЕ существующего подключения Inter, ДОБАВИТЬ:

```html
<!-- REDESIGN v1: Decorative typography -->
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;0,700;1,400&family=Caveat:wght@500;700&display=swap" rel="stylesheet">
```

### 0.2 Создать файл static/css/redesign_v1.css

Новый CSS-файл для ВСЕХ стилей редизайна. НЕ редактировать существующие CSS-файлы!
Подключить в base.html ПОСЛЕ unified_styles.css:

```html
<link rel="stylesheet" href="{% static 'css/redesign_v1.css' %}?v=20260310">
```

### 0.3 Добавить CSS-переменные в besedka_themes_v2.css

В секцию `:root, [data-theme="light"]` ДОБАВИТЬ (не заменять существующие!):

```css
/* === REDESIGN V1: Botanical accents === */
--bs-accent-green: #2d8a56;
--bs-accent-green-light: #e8f5e9;
--bs-accent-amber: #d4a24e;
--bs-accent-amber-light: #fff8e1;
--bs-accent-rose: #c06c84;
--bs-accent-rose-light: #fce4ec;

/* === REDESIGN V1: Typography === */
--bs-font-display: 'Cormorant Garamond', 'Georgia', serif;
--bs-font-handwritten: 'Caveat', cursive;
```

В секцию `[data-theme="dark"]` ДОБАВИТЬ:

```css
/* === REDESIGN V1: Botanical accents (dark) === */
--bs-accent-green: #4caf50;
--bs-accent-green-light: rgba(76, 175, 80, 0.12);
--bs-accent-amber: #ffc107;
--bs-accent-amber-light: rgba(255, 193, 7, 0.12);
--bs-accent-rose: #f48fb1;
--bs-accent-rose-light: rgba(244, 143, 177, 0.12);

/* === REDESIGN V1: Typography === */
--bs-font-display: 'Cormorant Garamond', 'Georgia', serif;
--bs-font-handwritten: 'Caveat', cursive;
```

---

## ФАЗА 1: ГЛАВНАЯ СТРАНИЦА (pages/home.html)

### Контекстные переменные (из HomePageView в news/views.py):
- `announcements` — list of dicts (title, content, style, label, preview, has_more)
- `current_tasks` — CurrentTasks object or None
- `homepage_progress_snapshot` — dict or None
- `latest_news` — QuerySet<News>[:4]
- `popular_reports` — QuerySet<GrowReport>[:4]
- `latest_photos` — QuerySet<Photo>[:4]

### Что менять:

1. **templates/pages/home.html** — ПОЛНАЯ замена `{% block extra_css %}` и `{% block main_container %}`
2. **static/css/redesign_v1.css** — все стили главной (секция /* HOMEPAGE */)

### HERO stat cards — подсчёт динамический:

ДОБАВИТЬ в HomePageView.get_context_data() (news/views.py):

```python
# REDESIGN: Stats for hero
try:
    from growreports.models import GrowReport
    reports_count = GrowReport.objects.filter(is_public=True).count()
except Exception:
    reports_count = 0

try:
    from gallery.models import Photo
    photos_count = Photo.objects.filter(is_public=True, is_active=True).count()
except Exception:
    photos_count = 0

context['hero_stats'] = {
    'reports_count': reports_count,
    'photos_count': photos_count,
    'users_count': User.objects.filter(is_active=True).count(),
    'news_count': News.objects.filter(is_published=True).count(),
}
```

### ВАЖНО — НЕ трогать:
- `homepage_announcement_banner.html` — оставить include как есть
- `homepage_current_tasks.html` — оставить include как есть
- `homepage_feedback_modal.html` — оставить include в footer

---

## ФАЗА 2: ТИПОГРАФИКА КАРТОЧЕК (CSS override)

Касается ВСЕХ листингов: новости, галерея (фото/альбомы), гроурепорты.
На этой фазе НЕ трогаем шаблоны. Только CSS-переопределение.

### Что менять:
- **static/css/redesign_v1.css** — секция /* CARD TYPOGRAPHY */
  ```css
  .unified-card .card-title {
    font-family: var(--bs-font-display);
    font-weight: 700;
    letter-spacing: -0.01em;
  }
  ```

### Что НЕ менять:
- news_list.html, gallery_list.html, albums_list.html (шаблоны)
- unified_card.html, unified_list_card.html (SSOT)
- unified_cards.css, gallery_redesign.css (базовые стили)

---

## ФАЗА 3: ДЕТАЛЬНАЯ СТРАНИЦА НОВОСТИ

### Что менять (ТОЛЬКО CSS, через redesign_v1.css):
- Заголовок `.news-detail-title` — font-family: var(--bs-font-display)
- Заголовки h2, h3 в контенте — font-family: var(--bs-font-display)
- Blockquote — border-left: 3px solid var(--bs-accent-green); background: var(--bs-accent-green-light)
- Badge оригинальности — использовать --bs-accent-green palette

### Что НЕ менять:
- HTML-структуру post_detail.html
- Reactions, comments, lightbox (SSOT-компоненты)

---

## ФАЗА 4: ДЕТАЛЬНАЯ СТРАНИЦА ФОТО

### Что менять (ТОЛЬКО CSS, через redesign_v1.css):
- Заголовок `.gall-detail-title` — font-family: var(--bs-font-display)
- Author link — hover с --bs-accent-green
- Reactions — border-radius: 10px, hover с --bs-accent-green-light

### Контекст текущей структуры:
- `gallery/photo_detail.html` — двухколоночный layout аналогичный news detail
- Класс `.gall-detail-main` — обёртка
- Класс `.gall-detail-hero` — hero с blur-bg
- Класс `.gall-detail-title` — заголовок фото
- Sidebar: автор, навигация prev/next, похожие фото

### Что НЕ менять:
- HTML-структуру photo_detail.html
- gallery_detail_redesign.css (базовые layout стили)
- Reactions (unified_reactions.html — SSOT)
- Lightbox (unified_lightbox — SSOT)

---

## ФАЗА 5: ЛИСТИНГ ГАЛЕРЕИ (CSS improvements)

### Что менять (ТОЛЬКО CSS, через redesign_v1.css):
- Фото-карточки `.gall-grid` — усилить hover overlay (gradient + opacity transition)
- Hover на фото — добавить transform: scale(1.03) на img
- Карточки альбомов — font-family: var(--bs-font-display) для заголовка альбома

### Контекст:
- `gallery/gallery_list.html` — фото (sticky bar со свитчером `show_switcher=True`)
- `gallery/albums_list.html` — альбомы (sticky bar со свитчером `switcher_albums_active=True`)
- Оба используют `unified_sticky_bar.html` с параметром `show_switcher=True`
- Свитчер работает через ССЫЛКИ (разные URL), не через JS-табы

### Что НЕ менять:
- gallery_list.html, albums_list.html (шаблоны)
- unified_sticky_bar.html (SSOT)
- gallery_redesign.css (базовые стили)

---

## ФАЗА 6: ДЕТАЛЬНАЯ ГРОУРЕПОРТА

### Что менять (CSS в `<style>` блоке report_detail.html):
- Hero `.bs-hero h1` — font-family: var(--bs-font-display)
- Stage badge colors — через --bs-accent-* переменные
- Entry cards — border-radius: 18px, обновить shadows

### Что НЕ менять:
- Python-логику во view
- Существующие Django template tags и includes

---

## CSS-ШПАРГАЛКА: ключевые стили из прототипов

```css
/* Заголовки разделов */
.bs-section-title {
  font-family: var(--bs-font-display);
  font-weight: 700;
  letter-spacing: -0.02em;
}

/* Акцентные надписи */
.bs-eyebrow {
  font-family: var(--bs-font-handwritten);
  color: var(--bs-accent-green);
}

/* Карточки */
.bs-card-redesign {
  border-radius: 18px;
  border: 1px solid var(--bs-border-subtle);
  box-shadow: var(--bs-shadow-sm);
  transition: transform 0.3s cubic-bezier(0.4,0,0.2,1), box-shadow 0.3s;
}
.bs-card-redesign:hover {
  transform: translateY(-4px);
  box-shadow: var(--bs-shadow);
}

/* Кнопки */
.bs-btn-green {
  background: var(--bs-accent-green);
  color: #fff;
  border: none;
  border-radius: 12px;
  padding: 0.75rem 1.75rem;
  font-weight: 600;
  box-shadow: 0 4px 16px rgba(45, 138, 86, 0.3);
}

/* Теги */
.bs-tag {
  padding: 0.3rem 0.65rem;
  border-radius: 8px;
  font-size: 0.78rem;
  background: var(--bs-tertiary-bg);
  color: var(--bs-text-secondary);
}
.bs-tag:hover {
  background: var(--bs-accent-green-light);
  color: var(--bs-accent-green);
}
```

---

## ТЕСТИРОВАНИЕ (ОБЯЗАТЕЛЬНО после каждой фазы)

### Smoke-тест: Django запускается без ошибок
```bash
docker-compose -f docker-compose.local.yml restart django
docker-compose -f docker-compose.local.yml logs -f django 2>&1 | head -50
```

### Визуальный тест через Playwright (MCP Docker):
```
1. http://host.docker.internal:8001/ — главная
2. http://host.docker.internal:8001/news/ — листинг новостей
3. Любая новость — детальная новость
4. http://host.docker.internal:8001/gallery/ — листинг фото
5. http://host.docker.internal:8001/gallery/albums/ — листинг альбомов
6. Любое фото — детальная фото
7. http://host.docker.internal:8001/growreports/ — листинг гроурепортов
8. Любой гроурепорт — детальная
9. Тёмная тема (localStorage theme=dark)
10. Мобилка (viewport 375x812)
```

### Критерии успеха:
- [ ] Нет 500 ошибок
- [ ] Нет broken templates (TemplateSyntaxError)
- [ ] Нет console errors в браузере
- [ ] Шрифты загружаются (Cormorant Garamond видно в заголовках)
- [ ] Тёмная тема не ломается
- [ ] Мобилка не ломается
- [ ] Свитчер Фото/Альбомы работает

---

## ПОРЯДОК РАБОТЫ

1. Фаза 0 → коммит `[REDESIGN] Phase 0: fonts + CSS variables`
2. Фаза 1 → коммит `[REDESIGN] Phase 1: homepage redesign`
3. Фаза 2 → коммит `[REDESIGN] Phase 2: card typography`
4. Фаза 3 → коммит `[REDESIGN] Phase 3: news detail typography`
5. Фаза 4 → коммит `[REDESIGN] Phase 4: photo detail typography`
6. Фаза 5 → коммит `[REDESIGN] Phase 5: gallery listing improvements`
7. Фаза 6 → коммит `[REDESIGN] Phase 6: growreport detail styles`

Между каждой фазой — smoke-тест!

---

## ЗАПРЕТЫ

- НЕ менять views.py (кроме добавления hero_stats в HomePageView)
- НЕ менять models.py
- НЕ менять urls.py
- НЕ удалять существующие CSS-файлы
- НЕ использовать !important
- НЕ хардкодить цвета — только CSS-переменные
- НЕ трогать SSOT-компоненты (unified_card.html, unified_pagination.html, unified_sticky_bar.html и т.д.)
- НЕ трогать JS-файлы (всё работает через CSS)
- НЕ делать git push без явной команды
