# Startup

Updated: 2026-03-22

## Current Workspace State

- Primary local path: `C:\Users\user\Projects\HabitFlow-git`
- Primary state: real git checkout with upstream history
- Current branch: `main`
- Git bootstrap to personal lab repo: verified
- Reference snapshot still exists at `C:\Users\user\Projects\HabitFlow-master`
- The reference snapshot was accidentally initialized as a standalone local git repo in Cursor and should not be treated as the canonical checkout
- Reproducible runtime baseline was established in the canonical checkout: dependencies installed, `postgres` and `redis` started via Docker, migrations applied, app served locally, `/healthz/ready` returned OK
- Local Docker services for HabitFlow (`postgres` on `5430`, `redis` on `6370`) were later relaunched alongside Besedka without port conflicts
- Current local UI check path used during handoff: `http://127.0.0.1:8010`
- Current-state screenshot pack exists at `docs/screenshots/current_state/` with desktop and mobile full-page captures
- v1/v1.0 tags now point to the current v2-planning base on `origin/main`

## Open This Folder

- Open `C:\Users\user\Projects\HabitFlow-git` in Cursor.
- Do not use `C:\Users\user\Projects\HabitFlow-master` as the active workspace.
- If Cursor shows hundreds of `untracked` files, the wrong folder is open.

## Source References

- Original upstream repository: `https://github.com/Qwertyil/HabitFlow.git`
- Intended personal lab repository: `https://github.com/badinoko/Habbit`
- External HabitFlow deployment: `https://www.amir-vps.ru/`

## Read First

1. `AGENTS.md`
2. `CODEX.md`
3. `docs/README.md`
4. `README.md`
5. `frontend-redesign-contracts.md`
6. `docs/overview.mdc` (`product + architecture`)
7. `docs/project/overview.md` (`task dashboard`)
8. `docs/project/progress.md` (`append-only log`)
9. `docs/contracts/api_contract.mdc`
10. `docs/contracts/session_contract.mdc`
11. `docs/contracts/theme-system.md`
12. `docs/prompts/artifacts-master-prompt.md`
13. `docs/prompts/cursor-prompt.md`
14. `docs/reviews/v2-typography-research.md`
15. `docs/reviews/v2-landing-reference-scan.md`
16. `docs/reviews/v2-navbar-and-stats-notes.md`
17. `docs/reviews/v2-direction.md`
18. `docs/reviews/upstream-proposal-v2-draft.md`
19. `docs/archive/README.md`

## Current Session Goal

Work from the real checkout so the next chat window can:

1. recognize that this is HabitFlow, not Besedka;
2. understand that `HabitFlow-master` is now only a reference snapshot;
3. continue from a checkout linked to the user's own repository model;
4. continue the planned `v2` redesign wave from the accepted `v1` base;
5. use the current typography/navbar/stats research notes before writing new UI code.

## Immediate Next Actions

1. Open `C:\Users\user\Projects\HabitFlow-git` in Cursor and continue only from that checkout.
2. Read `docs/reviews/v2-typography-research.md`, `docs/reviews/v2-landing-reference-scan.md`, and `docs/reviews/v2-navbar-and-stats-notes.md`.
3. Use `docs/reviews/v2-direction.md` as the implementation baseline for navbar, homepage typography, and stats IA.
4. Keep `docs/project/overview.md` and `docs/project/progress.md` current while leaving tasks in `REVIEW`/`ACTIVE` until user confirmation.
5. If local HabitFlow runtime is needed again, use a port other than `8001`.

## Notes

- Do not work from `HabitFlow-master` unless reference files are needed.
- The canonical working copy is `C:\Users\user\Projects\HabitFlow-git`.
- `docs/overview.mdc` and `docs/project/overview.md` are different documents with different roles; do not use them interchangeably.
- Push to `origin/main` was verified on 2026-03-21.
- Cursor will still show hundreds of `untracked` files if the IDE is opened on `HabitFlow-master`; that is the wrong workspace, not a broken GitHub link.
- Avoid `8001` for future local HabitFlow launches on this machine; Besedka already occupies that port through Docker/WSL.
- Google OAuth is already implemented in code and should be audited as a real feature, not treated as a future stub.
- Frontend redesign must respect current product scope from `frontend-redesign-contracts.md`.
- Current local artifact inputs live in `docs/artifacts/` and `docs/prompts/cursor-prompt.md`.
- Root `docs/` has been cleaned up so contracts, prompts, and reviews now live in dedicated subfolders.
- Oversized working docs should be rotated through `docs/archive/` according to `docs/archive/README.md`.
- Upstream proposal handoff note for the original author lives in `docs/reviews/upstream-proposal-v1.md`.
- Current release-prep delta log for `v2.0` lives in `docs/reviews/upstream-proposal-v2-draft.md`.
- Screenshot baseline for redesign work lives in `docs/screenshots/current_state/README.md`.
- Current v2 research layer lives in `docs/reviews/v2-typography-research.md`, `docs/reviews/v2-landing-reference-scan.md`, and `docs/reviews/v2-navbar-and-stats-notes.md`.
- Current v2 decision baseline lives in `docs/reviews/v2-direction.md`.
