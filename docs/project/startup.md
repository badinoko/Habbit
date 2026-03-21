# Startup

Updated: 2026-03-21

## Current Workspace State

- Primary local path: `C:\Users\user\Projects\HabitFlow-git`
- Primary state: real git checkout with upstream history
- Current branch: `main`
- Git bootstrap to personal lab repo: verified
- Reference snapshot still exists at `C:\Users\user\Projects\HabitFlow-master`
- The reference snapshot was accidentally initialized as a standalone local git repo in Cursor and should not be treated as the canonical checkout
- Reproducible runtime baseline was established in the canonical checkout: dependencies installed, `postgres` and `redis` started via Docker, migrations applied, app served locally, `/healthz/ready` returned OK
- The local HabitFlow runtime was then intentionally stopped because port `8001` conflicts with the user's Besedka stack on this machine
- Current-state screenshot pack exists at `docs/screenshots/current_state/` with desktop and mobile full-page captures

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
9. `docs/api_contract.mdc`
10. `docs/session_contract.mdc`
11. `docs/imports/besedka_design_kit_2026-03/README.md`
12. `docs/artifacts-master-prompt.md`

## Current Session Goal

Work from the real checkout so the next chat window can:

1. recognize that this is HabitFlow, not Besedka;
2. understand that `HabitFlow-master` is now only a reference snapshot;
3. continue from a checkout linked to the user's own repository model;
4. start a baseline audit of frontend issues, backend issues, and Google OAuth;
5. keep Besedka redesign knowledge immediately available for HabitFlow adaptation.

## Immediate Next Actions

1. Open `C:\Users\user\Projects\HabitFlow-git` in Cursor and continue only from that checkout.
2. Audit frontend defects against `docs/screenshots/current_state/` and direct browser behavior.
3. Audit Google OAuth configuration and callback baseline.
4. Prepare redesign invariants and an external-artifact prompt adapted from the Besedka kit.
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
- Imported Besedka redesign references live in `docs/imports/besedka_design_kit_2026-03/`.
- Screenshot baseline for redesign work lives in `docs/screenshots/current_state/README.md`.
