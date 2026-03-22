# CODEX.md

Working playbook for Codex in HabitFlow.

Last updated: 2026-03-22.

## 1. Role Of This File

This file is an assistant playbook, not a project status board.

Do not use it as the source for:

- active task status;
- progress history;
- product architecture decisions;
- release notes.

Canonical sources:

- `docs/project/overview.md` = the only task-status source
- `docs/project/progress.md` = append-only work log
- `docs/overview.mdc` = product and architecture overview
- `docs/README.md` = docs navigation map

## 2. Priority Order

1. `AGENTS.md`
2. This file
3. `docs/operations/codex_workflow.md`
4. Live project docs:
   - `docs/README.md`
   - `README.md`
   - `frontend-redesign-contracts.md`
   - `docs/overview.mdc`
   - `docs/contracts/api_contract.mdc`
   - `docs/contracts/session_contract.mdc`
5. Code and tests

## 3. Hard Invariants

1. No automatic `DONE` status changes without explicit user confirmation.
2. `docs/project/overview.md` is the only task-status source.
3. `docs/overview.mdc` is the product and architecture overview, not a task board.
4. `docs/project/progress.md` is append-only.
5. If work is implemented but not yet user-verified, use `REVIEW`, not `DONE`.
6. Do not remove or silently rewrite task rows.
7. Keep product scope aligned with the current backend and `frontend-redesign-contracts.md` unless the user explicitly expands scope.
8. If a long-lived working doc becomes unwieldy, archive it under `docs/archive/` instead of silently rewriting history.

## 4. Git Rules

1. Never push to `Qwertyil/HabitFlow`.
2. Preferred remote model:
   - `upstream` -> `https://github.com/Qwertyil/HabitFlow.git`
   - `origin` -> `https://github.com/badinoko/Habbit`
3. Push only on explicit user command.
4. If `.git` is missing, treat the folder as a plain snapshot and report that limitation explicitly.

## 5. Startup Checklist

1. Confirm this is a real git checkout.
2. Read:
   - `docs/README.md`
   - `docs/project/startup.md`
   - `docs/project/overview.md`
   - tail of `docs/project/progress.md`
3. Re-read product and technical context:
   - `README.md`
   - `frontend-redesign-contracts.md`
   - `docs/overview.mdc`
   - `docs/contracts/api_contract.mdc`
   - `docs/contracts/session_contract.mdc`
4. Work only from tasks that exist in `docs/project/overview.md`.

## 6. Local Runtime Rule

For live browser verification in this repo, treat `http://127.0.0.1:8010` as the intended local HabitFlow URL.

- Before trusting browser output, check which process owns port `8010`.
- Prefer a long-lived `uvicorn ... --reload` process for local work.
- `Ctrl+F5` only refreshes browser assets; it does not reload stale Python route/schema code.
- Frontend changes can appear on an old server process while backend changes remain stale.
- If browser UI and backend behavior disagree, restart the real `8010` app process first.
- Use `scripts/run_local_8010.cmd` for a predictable local launch.

## 7. Task Status Vocabulary

- `BACKLOG`
- `NEXT`
- `ACTIVE`
- `REVIEW`
- `BLOCKED`
- `DONE` only after explicit user confirmation

## 8. Product Guardrails

Keep these assumptions unless the user says otherwise:

- personal app, not a team product;
- server-rendered web UI by default;
- no invented due dates, reminders, teams, or admin layers;
- habits carry the main recurrence complexity;
- theme filtering remains a cross-screen navigation pattern;
- statistics stay lightweight unless the user explicitly expands scope.

## 9. Session-End Report

Every final handoff should state:

1. what changed;
2. what was intentionally not marked as done;
3. what the user should verify next;
4. whether the repo is a real git checkout or still a snapshot.
