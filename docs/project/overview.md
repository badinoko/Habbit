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
| HF-007 | REVIEW | Capture HabitFlow current-state screenshots and page inventory | Refreshed the 20-shot desktop/mobile baseline pack on `2026-03-22` from the live local app at `http://127.0.0.1:8010`; use `docs/screenshots/current_state/` for current UI review instead of the older v1-era set |
| HF-008 | BACKLOG | Draft redesign invariants and external artifact prompt | Fix shell constraints first: sticky top navbar, disciplined sidebar behavior, compact theme switcher, mobile-first navigation |
| HF-009 | REVIEW | Clean up documentation navigation and distinguish overview documents | Docs root cleaned up into `contracts/`, `prompts/`, and `reviews/`; waiting for user validation of final handoff structure |
| HF-010 | REVIEW | Implement HabitFlow frontend redesign wave from local artifacts | Shared shell, theme tokens, navbar switcher, partial fetch navigation, and auth overlay fixes are in place; v2 visual tuning is intentionally deferred |
| HF-011 | DONE | Prepare redesign v2 visual iteration | User confirmed the v2 visual pass across navbar, stats, forms, theme pages, and related follow-up fixes; the shipped `v2.0` tag now reflects this iteration |
| HF-012 | REVIEW | Prepare upstream proposal handoff | v1 handoff note exists and `docs/reviews/upstream-proposal-v2-draft.md` now captures the v2-over-v1.0 delta set, including shell/stats/theme redesign work, form reliability fixes, delete-modal behavior, and content-safety observations; waiting for user validation of the final presentation path |
| HF-013 | REVIEW | Prune imported redesign references after adaptation | Obsolete Besedka import pack removed; only HabitFlow artifacts/prompts/contracts remain for successor work |
| HF-014 | DONE | Define redesign v2 typography and navbar direction | The direction in `docs/reviews/v2-direction.md` was implemented and user-validated through the final v2 release pass, including navbar density, homepage hierarchy, and stats IA |
| HF-015 | REVIEW | Establish archive policy for oversized working docs | Added `docs/archive/README.md` and updated assistant workflow docs so `progress.md`, `overview.md`, and similar long-lived files are archived instead of silently bloating forever |
| HF-016 | ACTIVE | Harden input validation and baseline web security | Add shared server-side validation for user-facing names, wire baseline security headers, and prepare deploy-facing notes for secure prod flags without regressing current forms or API flows |
| HF-017 | ACTIVE | Expand stats periods and replace pills with dropdown control | Rework `/stats` period selection into a mobile-friendly dropdown, add broader supported ranges, and keep section switching/hash behavior stable across period changes |

## Scope Reminder

- Personal productivity app
- Server-rendered web UI
- No invented team/admin/reminder features unless the user explicitly requests product expansion
