# Progress

## 2026-03-21

- Added initial assistant workflow files: `AGENTS.md`, `CODEX.md`, `docs/operations/codex_workflow.md`, `docs/project/startup.md`, `docs/project/overview.md`.
- Recorded that `C:\Users\user\Projects\HabitFlow-master` is currently a local snapshot without `.git`.
- Seeded the initial lab task list for bootstrap, runtime baseline, frontend audit, OAuth audit, and implementation wave planning.
- Imported a Besedka redesign reference pack into `docs/imports/besedka_design_kit_2026-03/` with core UI references, redesign artifacts, prompts, homepage context, screenshots, and dense gallery/growreports reference packs.
- No task was marked `DONE`.
- Cursor accidentally initialized `C:\Users\user\Projects\HabitFlow-master` as a standalone local git repo; the folder remains a reference snapshot and is not treated as the canonical checkout.
- Created a real upstream-based checkout at `C:\Users\user\Projects\HabitFlow-git`, configured remotes for `upstream = Qwertyil/HabitFlow` and `origin = badinoko/Habbit`, and copied the latest local HabitFlow docs/imports into that checkout.
- Created local git commit `f5d5a3a` (`Bootstrap HabitFlow lab workspace`) in `C:\Users\user\Projects\HabitFlow-git` and force-updated `origin/main` on `badinoko/Habbit` to that history.
- Added tracking tasks for HabitFlow current-state capture and a redesign invariants/artifact-prompt pass.
- No task was marked `DONE`.
- Established a reproducible local baseline in `C:\Users\user\Projects\HabitFlow-git`: installed Poetry dependencies, started `postgres` and `redis`, ran Alembic migrations, launched the app on `http://127.0.0.1:8001`, and confirmed `/healthz/ready` returns OK.
- Captured a full current-state screenshot pack under `docs/screenshots/current_state/` with 10 desktop and 10 mobile full-page screens plus a local README manifest.
- Recorded in startup docs that `HabitFlow-master` remains an accidental standalone repo and should not be used as the canonical workspace in Cursor.
- Recorded the external HabitFlow deployment URL `https://www.amir-vps.ru/` in startup docs for future audits and handoff.
- Stopped the local HabitFlow runtime and `docker-compose` services after confirming they conflicted with Besedka on port `8001`; future local HabitFlow runs should use a different port.
- No task was marked `DONE`.
- Added `docs/README.md` as a navigation index and clarified across `AGENTS.md`, `CODEX.md`, `CLAUDE.md`, `README.md`, `docs/overview.mdc`, `docs/project/startup.md`, and `docs/operations/codex_workflow.md` that `docs/overview.mdc` is product/architecture context while `docs/project/overview.md` is the only task-status dashboard.
- Added active task `HF-009` to track documentation navigation cleanup without rewriting historical records.
- Indexed the user-provided Artifacts handoff file at `docs/artifacts-master-prompt.md` so future sessions can find the prompt from the normal docs entry points.
- No task was marked `DONE`.
