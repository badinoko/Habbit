# Redesign Artifact Adaptation Plan

> Updated: 2026-03-10
> Mode: `reference-first`

Цель: разложить пакет HTML-артефактов на `visual reference` и `structural adaptation`, чтобы в следующей реализации не копировать артефакты в Django-шаблоны напрямую.

---

## Общие правила

- Navbar, sticky bar, footer и shell-каркас внутри HTML-артефактов считаются `visual reference only`: на сайте уже есть реальные shared-слои в `base.html` и `templates/includes/partials/unified_sticky_bar.html`.
- Navbar из артефактов можно брать только как visual direction: текущий runtime-navbar и admin-switcher/dropdown считаются хрупкими, поэтому первую implementation-wave нельзя начинать с их функционального переписывания.
- Для листингов не переносить artifact-карточки 1:1: сначала адаптировать shared-слой `templates/includes/partials/unified_list_card.html`, затем уже page-shell каждого раздела.
- В redesign-target для публичных preview/list cards не тянуть owner edit/delete controls наружу: destructive/edit actions должны жить на detail/admin/workbench surface, а не на внешних карточках.
- Для detail-страниц переиспользовать существующие SSOT-блоки (`unified_sticky_bar`, `unified_reactions`, `unified_comment_section`, shared lightbox), а не дублировать их локальными версиями.
- Для GrowReports запрещено ломать текущий контракт `Неделя -> записи дней`, `toggle-week`, фото/комментарии/реакции на уровне `day-entry`.

---

## Artifact Map

### `home/homepage-redesign-v1.html`

- Django target: `templates/pages/home.html`
- Shared dependencies: `homepage_announcement_banner.html`, `homepage_current_tasks.html`
- `Visual reference`:
  - botanical hero mood;
  - типографика секций;
  - ритм секций `Новости / GrowReports / Gallery`;
  - финальный community CTA.
- `Structural adaptation`:
  - текущие announcement/progress/current-tasks блоки уже живут отдельными partials;
  - виджеты главной тянут реальные данные и не совпадают с демо-card markup из artifact;
  - navbar/footer нельзя переносить из artifact.
- Phase order:
  - tokens + hero wrapper;
  - section spacing and headings;
  - homepage widget card polish;
  - CTA/footer-adjacent finish.

### `listing/listing-redesign-v1.html`

- Django targets:
  - `templates/news/news_list.html`
  - `templates/gallery/gallery_list.html`
  - `templates/growreports/growreports_list.html`
  - `templates/includes/partials/unified_list_card.html`
- Shared dependencies: `unified_list_card.html`, `unified_pagination.html`, `unified_sticky_bar.html`
- `Visual reference`:
  - более плотная карточка;
  - featured-card hierarchy;
  - background blobs and calmer spacing;
  - footer/meta density.
- `Structural adaptation`:
  - текущие list/grid toggle, drawer, search, sort pills, pagination и module-specific filters уже живут отдельно;
  - один artifact должен сесть на три разных модуля и один shared card partial;
  - featured-card pattern нельзя внедрять, пока не решено, как он ведёт себя в `grid/list` и AJAX/filter flows.
- Phase order:
  - shared card geometry in `unified_list_card.html`;
  - shared grid rhythm in module CSS;
  - sticky-bar/pagination visual alignment;
  - optional featured-card experiment only after base grid pass.

### `detail/news-detail-redesign-v1.html`

- Django target: `templates/news/post_detail.html`
- Shared dependencies: `unified_sticky_bar.html`, `unified_reactions.html`, `unified_comment_section.html`
- `Visual reference`:
  - hero/meta composition;
  - quieter sidebar cards;
  - author/tags/related-news hierarchy;
  - article typography rhythm.
- `Structural adaptation`:
  - news detail already uses shared sticky bar, reaction picker, comments, original-content logic, placeholders and source metadata;
  - artifact sidebar is simpler than current functional sidebar and must be mapped onto existing context, not replace it.
  - right sidebar must stay pinned immediately below sticky bar; redesign work should remove the late upward drift near the bottom of the document instead of reintroducing it.
- Phase order:
  - hero and meta strip;
  - article typography;
  - sidebar polish;
  - comments spacing only as final pass.

### `detail/growreport-detail-redesign-v1.html`

- Django target: `templates/growreports/report_detail.html`
- Shared dependencies: `unified_sticky_bar.html`, `unified_reactions.html`, `unified_comment_section.html`
- `Visual reference`:
  - hero atmosphere;
  - timeline card language;
  - stage chips;
  - metrics strip and entry footer mood.
- `Structural adaptation`:
  - текущий шаблон уже содержит сложный runtime-контракт `weeks -> entries`;
  - per-entry comments/reactions/collapse и mixed media roadmap нельзя потерять ради красивой обёртки;
  - текущий detail технически самый тяжёлый и требует CSS extraction, а не прямого HTML-переноса;
  - report-level destructive action не должен уезжать под нижний week-switcher/footer overlay.
- Phase order:
  - hero/info/stage progress layer;
  - week-card shell;
  - day-entry shell;
  - per-entry photos/metrics/reactions/comments visual pass.

---

## Recommended Implementation Order

1. `Homepage`
   Причина: изолированная страница, можно утвердить визуальный язык без риска сломать shared list/detail flows.
2. `Listing shared system`
   Причина: один visual pass даст эффект сразу для `News / Gallery / GrowReports`, но начинать нужно с `unified_list_card.html`, а не с page-level копипаста.
3. `News detail`
   Причина: ближе всего к текущей структуре и может стать эталоном detail-language для следующего публичного detail wave.
4. `GrowReport detail`
   Причина: максимальная structural adaptation, лучше заходить только после согласования visual language и подготовки richer test data.

---

## Missing Inputs Before Runtime Wave

- Следующий artifact-запрос в внешний генератор имеет смысл направить на `Gallery photo detail page`.
  Причина: в текущем пакете нет public gallery-detail artifact, а именно `photo_detail` остаётся активной UX-зоной (`#GALL-044`).
- Для GrowReports не хватает richer visual dataset:
  - минимум `1-3` публичных репорта;
  - у одного репорта должно быть несколько недель;
  - внутри недели нужны `day-entry` с комментариями;
  - достаточно placeholder/color-fill изображений, реальные фото не обязательны.

---

## What Is Reference-Only Right Now

- Все четыре HTML-артефакта остаются `reference-only`.
- В следующей сессии сначала согласовывается phase map и target files.
- Прямой перенос shell markup из artifact в runtime-шаблоны запрещён до отдельного go-ahead.

## Extra UI guardrails from user QA before implementation

- Убрать edit/delete controls с внешних preview cards в `News / Gallery / GrowReports`; detail pages остаются основным местом для этих действий.
- Для `News detail` и `Photo detail` правая колонка должна быть реально sticky сразу под верхним sticky bar и не начинать ползти вверх только в конце длинного скролла.
- Для `GrowReport detail` нижняя delete/action зона не должна перекрываться week-switcher/footer surface.
