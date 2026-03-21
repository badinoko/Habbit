# PROMPT: Wave 2 Recovery Handoff For External Assistant

> РЕЖИМ: Visual recovery / artifact-alignment
> ВЕТКА: `main`
> ЦЕЛЬ: Перерисовать и направить implementation строго по артефактам Wave 2, без возврата к legacy generic UI

---

## Что читать сначала

```text
@CODEX.md
@AGENTS.md
@docs/artifacts/redesign_2026-03/DESIGN_SYSTEM.md
@docs/artifacts/redesign_2026-03/DESIGN_DECISIONS.md
@docs/artifacts/redesign_2026-03/INDEX.md
@docs/artifacts/redesign_2026-03/wave2/shell-wave2-v1.html
@docs/artifacts/redesign_2026-03/wave2/growreports-listing-wave2.html
@docs/artifacts/redesign_2026-03/detail/news-detail-redesign-v1.html
@docs/artifacts/redesign_2026-03/detail/photo-detail-redesign-v1.html
```

---

## Точные целевые поверхности

Нужно работать только с этими поверхностями:

1. Shell rhythm на целевых публичных страницах:
   - navbar
   - sticky bar
   - mobile overflow
   - mobile FAB
2. `templates/news/news_list.html`
3. `templates/growreports/growreports_list.html`
4. `templates/news/post_detail.html`
5. `templates/gallery/photo_detail.html`

---

## Жёстко вне scope

- НЕ переоткрывать `growreport detail`
- НЕ менять `views.py`, `models.py`, `urls.py`
- НЕ ломать `GrowEntry.images -> gallery.Photo`
- НЕ трогать chat/admin/store surfaces
- НЕ откатывать уже принятый gallery listing baseline

---

## Что в текущем репо было не так

Это важно. Не повторять эти ошибки:

1. В `news` и `growreports` runtime слишком долго держался legacy generic слой:
   - `templates/includes/partials/unified_public_listing_card.html`
   - визуальная геометрия оставалась слишком общей и механической
   - карточки выглядели как слегка перекрашенный старый SSOT, а не как Wave 2
2. Mobile sticky поведение на целевых поверхностях было отключено флагами:
   - `mobile_disable_overflow=True`
   - `mobile_force_*_visible=True`
   - в результате UI не соответствовал решению “one-row + overflow”
3. `news detail` и `gallery detail` визуально дрейфовали:
   - общая структура похожа, но typography, sidebar richness, comments/reactions и мета-блоки расходились
4. Старый prompt/индексация упоминали `growreport-detail-wave2-v1.html`, но реальный файл артефакта:
   - `docs/artifacts/redesign_2026-03/wave2/growreport-detail-wave2.html`
   - это naming drift, не ориентируйся на несуществующее имя

---

## Что уже изменено в коде сейчас

В репо уже начат recovery-pass:

- для `news`/`growreports` введены отдельные Wave 2 partials вместо generic listing card
- для `news detail`/`gallery detail` введены shared detail partials
- целевые страницы переведены на реальный mobile overflow path
- `growreport detail` намеренно не тронут

Твоя задача: дать более точный visual direction / prompt-level correction, если текущая recovery-реализация всё ещё недостаточно близка к артефактам.

---

## Что требуется от тебя

Нужен ответ в формате visual brief / correction brief, который:

1. Сравнивает артефакты и текущую реализацию целевых поверхностей.
2. Указывает, где реализация всё ещё держится за legacy geometry.
3. Даёт конкретные визуальные указания, а не общие слова:
   - типографика
   - скругления
   - вертикальный rhythm
   - композиция карточек
   - плотность meta/footer
   - поведение reactions/comments
   - sidebar richness
4. Не уходит в абстрактный “modern / clean / elegant”, а опирается на реальные артефакты.

---

## Ключевые ожидания по surfaces

### 1. Shell

- Navbar должен оставаться компактным.
- Mobile sticky bar: строго один ряд.
- Первичный mobile path: overflow, а не inline-навал controls.
- FAB на мобилке должен чувствоваться как часть Wave 2 shell, а не legacy pill.

### 2. News listing

- Это должен быть packed composition:
  - hero
  - side cards
  - regular cards
  - wide cards
- Нельзя сводить всё к одинаковой generic card с layout modifiers.
- Hero/title hierarchy должна ощущаться как editorial surface.

### 3. GrowReports listing

- Самая проблемная поверхность.
- Нельзя оставлять ощущение “одинаковые карточки разной высоты”.
- Нужен distinct horizontal identity, более сильный visual rhythm и лучшая дисциплина высот.
- Листинг должен восприниматься как отдельный visual family, а не как derivative от news/gallery.

### 4. News detail + Gallery detail

- Это одна structural family:
  - hero/content слева
  - sticky metadata/sidebar справа
- Допустимое отступление от артефакта уже принято:
  - правый блок остаётся sticky
- Но всё остальное должно быть ближе и богаче:
  - Cormorant в нужных местах
  - более выразительные заголовки
  - comments не должны выглядеть механически
  - reaction counters/picker placement должны быть внятными
  - sidebar должен ощущаться как полноценный второй столбец, а не как остаточный набор карточек

---

## Жёсткие правила для рекомендаций

- Не предлагай возвращаться к generic `unified_public_listing_card` для `news/growreports`
- Не предлагай сломать data contracts
- Не предлагай убрать sticky sidebar на detail pages
- Не предлагай новый scope для `growreport detail`
- Не предлагай “потом унифицировать” вместо конкретного visual решения сейчас

---

## Ожидаемый результат

Нужен подробный correction brief, который можно сразу отдать implementation-assistant как источник решений:

- по shell
- по news listing
- по growreports listing
- по news detail
- по gallery detail

Если видишь, что какая-то поверхность всё ещё слишком legacy-heavy, называй это прямо и указывай, чем именно она расходится с артефактом.
