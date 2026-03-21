# Project Overview

This file is the only task-status source for HabitFlow lab work.

## Status Legend

- `BACKLOG`
- `NEXT`
- `ACTIVE`
- `REVIEW`
- `BLOCKED`
- `DONE` only after explicit user confirmation

## Active Dashboard

| ID | Status | Task | Notes |
|---|---|---|---|
| HF-001 | REVIEW | Bootstrap a real git workspace for HabitFlow lab | Real checkout prepared at `C:\Users\user\Projects\HabitFlow-git`; remotes configured and `origin/main` updated, waiting for user validation of folder cleanup strategy |
| HF-002 | REVIEW | Establish a reproducible local runtime baseline | Poetry deps installed, infra proved locally, Alembic migrated, health endpoint returned OK; local stack then stopped because port `8001` conflicts with Besedka on this machine |
| HF-003 | NEXT | Audit frontend defects and UX debt | Use `docs/screenshots/current_state/` plus direct browser checks to map layout and navigation defects |
| HF-004 | BACKLOG | Audit Google OAuth flow | Verify config, callback flow, error states, and actual usability |
| HF-005 | BACKLOG | Split findings into implementation waves | Convert audit output into small, testable work packages |
| HF-006 | REVIEW | Import Besedka redesign knowledge base into HabitFlow docs | Reference pack copied into `docs/imports/besedka_design_kit_2026-03/`; needs user review and later cleanup |
| HF-007 | REVIEW | Capture HabitFlow current-state screenshots and page inventory | Captured 20 full-page screenshots in `docs/screenshots/current_state/` for desktop and mobile baseline review |
| HF-008 | BACKLOG | Draft redesign invariants and external artifact prompt | Fix shell constraints first: sticky top navbar, disciplined sidebar behavior, compact theme switcher, mobile-first navigation |
| HF-009 | ACTIVE | Clean up documentation navigation and distinguish overview documents | Make product/architecture docs, task docs, prompt handoff docs, and reference imports easier to navigate without changing historical records |

## Scope Reminder

- Personal productivity app
- Server-rendered web UI
- No invented team/admin/reminder features unless the user explicitly requests product expansion
