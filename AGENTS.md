# AGENTS.md

Entry point for assistants in this repository.

1. Read `CODEX.md` first.
2. Primary project context:
   - `README.md`
   - `frontend-redesign-contracts.md`
   - `docs/overview.mdc`
   - `docs/api_contract.mdc`
   - `docs/session_contract.mdc`
   - `docs/imports/besedka_design_kit_2026-03/README.md`
3. Critical laws:
   - Do not set any task to `DONE` without explicit user confirmation.
   - `docs/project/overview.md` is the only task-status source.
   - `docs/project/progress.md` is append-only during normal work.
   - Do not rewrite old progress entries or remove tasks without explicit user approval.
   - Work from tasks that exist in `docs/project/overview.md`.
   - If the repo is opened from a ZIP snapshot and `.git` is missing, do not invent git state; report the limitation explicitly.
   - Never push to the original author repository. The intended model is:
     - `upstream` = `https://github.com/Qwertyil/HabitFlow.git`
     - `origin` = personal lab repository controlled by the user
   - Preserve current product scope unless the user explicitly expands it.
   - Do not invent features forbidden by `frontend-redesign-contracts.md` such as task due dates, teams, reminders, or admin dashboards.
   - Imported Besedka design materials are reference-only. Adapt them to HabitFlow instead of copying product semantics blindly.
4. Shared process contract:
   - Follow `docs/operations/codex_workflow.md`.
5. Session handoff files:
   - `docs/project/startup.md`
   - `docs/project/overview.md`
   - `docs/project/progress.md`
