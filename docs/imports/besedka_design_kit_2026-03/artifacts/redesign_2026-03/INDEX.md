# Redesign Artifacts — Инвентаризация

> Обновлено: 2026-03-12

---

## Документация (3 файла)

| Файл | Назначение |
|------|-----------|
| `DESIGN_SYSTEM.md` | Дизайн-система: шрифты, палитра, компоненты, сетки, анимации |
| `DESIGN_DECISIONS.md` | UX-решения: navbar, sticky bar, overflow, FAB, структура данных |
| `PROMPT_WAVE2_IMPLEMENTATION.md` | Промпт для Cursor — 5 фаз имплементации |

## Актуальные артефакты (7 полных HTML)

| Файл | Страница | Django template |
|------|----------|----------------|
| `home/homepage-redesign-v1.html` | Главная (лендинг) | `templates/pages/home.html` |
| `listing/gallery-list-redesign-v1.html` | Галерея: фото + альбомы | `templates/gallery/gallery_list.html` + `albums_list.html` |
| `detail/news-detail-redesign-v1.html` | Детальная новость | `templates/news/post_detail.html` |
| `detail/photo-detail-redesign-v1.html` | Детальная фото | `templates/gallery/photo_detail.html` |
| `wave2/shell-wave2-v1.html` | Shell (navbar+sticky) + News listing | navbar + sticky bar + `templates/news/news_list.html` |
| `wave2/growreports-listing-wave2.html` | Листинг гроурепортов | `templates/growreports/growreports_list.html` |
| `wave2/growreport-detail-wave2.html` | Детальная гроурепорта | `templates/growreports/report_detail.html` |

## Архив

Устаревшие файлы (9 шт.) перенесены в `docs/archive/visual_redesign/redesign_artifacts_wave1/`.
