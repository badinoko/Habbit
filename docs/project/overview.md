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
| HF-001 | ACTIVE | Bootstrap a real git workspace for HabitFlow lab | Real checkout prepared at `C:\Users\user\Projects\HabitFlow-git`; remotes configured, commit/push verification still pending |
| HF-002 | NEXT | Establish a reproducible local runtime baseline | Install deps, start infra, migrate DB, run app, record failures |
| HF-003 | BACKLOG | Audit frontend defects and UX debt | Use local screenshots and direct browser checks |
| HF-004 | BACKLOG | Audit Google OAuth flow | Verify config, callback flow, error states, and actual usability |
| HF-005 | BACKLOG | Split findings into implementation waves | Convert audit output into small, testable work packages |
| HF-006 | REVIEW | Import Besedka redesign knowledge base into HabitFlow docs | Reference pack copied into `docs/imports/besedka_design_kit_2026-03/`; needs user review and later cleanup |
| HF-007 | NEXT | Capture HabitFlow current-state screenshots and page inventory | Build a local `current_state` pack for desktop and mobile before redesign work |
| HF-008 | BACKLOG | Draft redesign invariants and external artifact prompt | Fix shell constraints first: sticky top navbar, disciplined sidebar behavior, compact theme switcher, mobile-first navigation |

## Scope Reminder

- Personal productivity app
- Server-rendered web UI
- No invented team/admin/reminder features unless the user explicitly requests product expansion
