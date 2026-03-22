# CLAUDE.md

Короткий operational guide для Claude Desktop / Cowork.

Последнее обновление: 2026-03-22.

## Роль файла

Этот файл не является:

- task-board;
- продуктовым overview;
- журналом прогресса;
- сводкой всех экранов и решений.

Для этого есть canonical docs:

- `docs/project/overview.md` — статусы задач;
- `docs/project/progress.md` — append-only журнал;
- `docs/overview.mdc` — продукт и архитектура;
- `docs/README.md` — карта документации.

## Что читать сначала

1. `docs/README.md`
2. `AGENTS.md`
3. `frontend-redesign-contracts.md`
4. `docs/overview.mdc`
5. `docs/project/overview.md`
6. `docs/project/progress.md`
7. `docs/reviews/upstream-proposal-v2-draft.md`

## Практические правила

- Каноническая рабочая копия: `C:\Users\user\Projects\HabitFlow-git`
- Язык общения: русский
- Язык UI: русский
- Не использовать `CLAUDE.md` как источник статусов задач
- Не дублировать сюда progress notes, release notes или screen inventory
- При сомнениях по текущему состоянию проекта всегда доверять `docs/project/overview.md` и `docs/project/progress.md`

## Runtime-памятка

- Локальный URL для живой проверки: `http://127.0.0.1:8010`
- Перед browser-smoke проверять, что реальный HabitFlow-процесс поднят именно там
- `Ctrl+F5` обновляет только браузер, но не Python backend
- Для предсказуемого локального старта использовать `scripts/run_local_8010.cmd`

## Где искать артефакты

- `docs/screenshots/current_state/` — актуальный screenshot baseline
- `docs/screenshots/current_state/inventory.md` — перечень UI-state для screenshot coverage
- `docs/reviews/v2-direction.md` — зафиксированные v2 design decisions
- `docs/reviews/upstream-proposal-v2-draft.md` — накопительная delta v1→v2→v3

## Для visual work в Artifacts

- Использовать `docs/prompts/artifacts-master-prompt.md`
- Соблюдать `frontend-redesign-contracts.md`
- Не изобретать запрещённые product features
