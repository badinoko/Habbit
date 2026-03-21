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
- Started `HF-010` implementation from the local artifact pack in `docs/artifacts/` and `docs/cursor-prompt.md`: replaced the shared shell, redesigned core templates, added light/dark theme tokens plus navbar toggle, and switched filter/sort/theme navigation to partial fetch-based updates where feasible.
- Added `docs/theme-system.md` as the SSOT for visual themes and linked it from the main documentation map and overview docs.
- Verified the redesign with `compileall`, full `tests/api_unit`, `tests/api_unit/test_auth_router_html_unit.py`, `tests/api_unit/test_stats_router_unit.py`, `tests/integration/test_stats.py`, and `tests/integration/test_unauthorized_create_redirects.py` with one caveat: repeated integration runs can temporarily fail on this Windows host when Docker cannot immediately rebind PostgreSQL test port `5433`.
- No task was marked `DONE`.

## 2026-03-22

- Applied follow-up navbar/auth polish from user feedback: denser navbar controls, larger typography, stable scrollbar gutter handling, and auth overlay behavior that no longer shifts layout.
- Verified that local HabitFlow infrastructure (`postgres` on `5430`, `redis` on `6370`) can coexist with the user's Besedka stack on this machine.
- Reorganized `docs/` for handoff: moved contracts into `docs/contracts/`, prompts into `docs/prompts/`, and the architecture audit into `docs/reviews/`, then updated references in repo docs and handoff files.
- Added `HF-011` as the next redesign-v2 track for later typography/color iteration in a separate session.
- Prepared the repository for successor handoff with a versioned checkpoint tag plan; no task was marked `DONE`.
- Verified that upstream `https://github.com/Qwertyil/HabitFlow` is fetchable but not writable from this workspace (`403` on dry-run push), then added `HF-012` and `docs/reviews/upstream-proposal-v1.md` so the original author can review our fork through `origin` and tag `v1` without any risk to upstream `master`.
- Started `HF-013` to prune the now-obsolete Besedka import pack after adaptation: the repo keeps local HabitFlow artifacts and prompt history, while assistant handoff docs are being updated to stop referencing `docs/imports/`.
- Shifted the v1 readiness checkpoint to the current `main` tip for handoff continuity, started the explicit v2 planning pass from that base, and opened `HF-014` to define typography and navbar direction before the next implementation wave.
- Added two working review notes for v2 research: `docs/reviews/v2-typography-research.md` captures the confirmed Besedka font roles (`Inter`, `Cormorant Garamond`, `Caveat`), while `docs/reviews/v2-landing-reference-scan.md` compares Besedka with current landing references such as Linear, Raycast, and Stripe before any new code changes.
- Added `docs/reviews/v2-navbar-and-stats-notes.md` to capture direct user feedback for the next wave: navbar items feel too airy vertically, shell type needs clearer role separation, and the stats page may benefit from a sticky left-side section switcher instead of one long vertical sequence.
- Established an archive policy for oversized working docs: added `docs/archive/README.md`, updated `AGENTS.md`, `CODEX.md`, `docs/README.md`, and `docs/operations/codex_workflow.md`, and recorded `HF-015` so future `progress.md` / `overview.md` rotations happen via frozen snapshots instead of ad hoc truncation.
