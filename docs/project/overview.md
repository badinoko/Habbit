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
| HF-006 | REVIEW | Import Besedka redesign knowledge base into HabitFlow docs | Historical import step completed earlier; the bulky reference pack is now being pruned in `HF-013` after adaptation into local HabitFlow artifacts |
| HF-007 | REVIEW | Capture HabitFlow current-state screenshots and page inventory | Captured 20 full-page screenshots in `docs/screenshots/current_state/` for desktop and mobile baseline review |
| HF-008 | BACKLOG | Draft redesign invariants and external artifact prompt | Fix shell constraints first: sticky top navbar, disciplined sidebar behavior, compact theme switcher, mobile-first navigation |
| HF-009 | REVIEW | Clean up documentation navigation and distinguish overview documents | Docs root cleaned up into `contracts/`, `prompts/`, and `reviews/`; waiting for user validation of final handoff structure |
| HF-010 | REVIEW | Implement HabitFlow frontend redesign wave from local artifacts | Shared shell, theme tokens, navbar switcher, partial fetch navigation, and auth overlay fixes are in place; v2 visual tuning is intentionally deferred |
| HF-011 | ACTIVE | Prepare redesign v2 visual iteration | v1 checkpoint is accepted as the base; next wave starts from typography, color balance, and navbar polish with Besedka homepage screenshots as a visual reference |
| HF-012 | REVIEW | Prepare upstream proposal handoff | Upstream comparison note exists, Russian handoff doc is in place, and the result is now shown from `origin/main`; waiting only for user validation of the presentation path |
| HF-013 | REVIEW | Prune imported redesign references after adaptation | Obsolete Besedka import pack removed; only HabitFlow artifacts/prompts/contracts remain for successor work |
| HF-014 | ACTIVE | Define redesign v2 typography and navbar direction | Capture font hierarchy, headline/body pairing, CTA tone, and navbar corrections before the next implementation wave |

## Scope Reminder

- Personal productivity app
- Server-rendered web UI
- No invented team/admin/reminder features unless the user explicitly requests product expansion
