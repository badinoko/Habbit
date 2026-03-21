# CODEX.md

Working playbook for Codex in HabitFlow.

Last updated: 2026-03-21.

## 1. Priority Order

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

## 2. Repository Intent

This workspace is an independent lab around HabitFlow.

- Original source repository: `https://github.com/Qwertyil/HabitFlow.git`
- Intended personal lab repository: `https://github.com/badinoko/Habbit`
- Default collaboration language: Russian

The goal is to audit, stabilize, redesign, and improve the project without writing to the original upstream repository.

## 3. Hard Invariants

1. No automatic `DONE` status changes without explicit user confirmation.
2. `docs/project/overview.md` is the only task-status source.
3. `docs/overview.mdc` is the product and architecture overview, not a task board.
4. `docs/project/progress.md` is append-only.
5. If work is implemented but not yet user-verified, use `REVIEW`, not `DONE`.
6. Do not remove or silently rewrite task rows.
7. Keep product scope aligned with the current backend and `frontend-redesign-contracts.md` unless the user explicitly expands scope.

## 4. Git Rules

1. Never push to `Qwertyil/HabitFlow`.
2. Preferred remote model after bootstrap:
   - `upstream` -> `https://github.com/Qwertyil/HabitFlow.git`
   - `origin` -> `https://github.com/badinoko/Habbit`
3. Push only on explicit user command.
4. If `.git` is missing, treat the folder as a plain snapshot:
   - do not claim branch state,
   - do not claim sync state,
   - do not invent remotes,
   - do record that bootstrap is still pending.

## 5. Startup Checklist

1. Check whether `.git` exists.
2. If it exists, inspect:
   - `git status --short`
   - `git branch --show-current`
   - `git remote -v`
3. Read:
   - `docs/README.md`
   - `docs/project/startup.md`
   - `docs/project/overview.md`
   - tail of `docs/project/progress.md`
4. Re-read product and technical context:
   - `README.md`
   - `frontend-redesign-contracts.md`
   - `docs/overview.mdc`
   - `docs/contracts/api_contract.mdc`
   - `docs/contracts/session_contract.mdc`
5. Before implementation, determine which track the request belongs to:
   - bootstrap/git
   - runtime and infrastructure
   - frontend/UI
   - backend/domain logic
   - auth/session/Google OAuth
   - tests/docs

## 6. Task Status Vocabulary

- `BACKLOG` = known but not selected
- `NEXT` = candidate for the next working session
- `ACTIVE` = currently in progress
- `REVIEW` = implemented or prepared, waiting for user validation
- `BLOCKED` = cannot proceed without user input or external dependency
- `DONE` = user explicitly confirmed

## 7. Current Focus Areas

1. Convert the local snapshot into a real git workspace connected to personal lab remotes.
2. Establish a reproducible local baseline:
   - install dependencies,
   - start PostgreSQL and Redis,
   - run migrations,
   - boot the app,
   - run tests.
3. Audit frontend structure and UX issues.
4. Audit Google OAuth behavior end to end.
5. Use local HabitFlow artifacts, prompt history, and theme docs as the redesign reference set.
6. Turn findings into implementation waves with small, testable changes.

## 8. Product Guardrails

Keep these assumptions unless the user says otherwise:

- personal app, not a team product;
- server-rendered web UI, not a SPA rewrite by default;
- tasks have priorities but no due dates;
- habits carry recurrence complexity and deserve careful UX;
- theme filter is a cross-screen navigation pattern;
- statistics are lightweight summaries, not advanced analytics.

## 9. Session-End Report

Every final handoff should state:

1. what changed;
2. what was intentionally not marked as done;
3. what the user should verify next;
4. whether the repo is a real git checkout or still a snapshot.
