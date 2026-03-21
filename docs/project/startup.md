# Startup

Updated: 2026-03-21

## Current Workspace State

- Primary local path: `C:\Users\user\Projects\HabitFlow-git`
- Primary state: real git checkout with upstream history
- Current branch: `main`
- Git bootstrap to personal lab repo: local checkout prepared, push still pending verification
- Reference snapshot still exists at `C:\Users\user\Projects\HabitFlow-master`
- The reference snapshot was accidentally initialized as a standalone local git repo in Cursor and should not be treated as the canonical checkout

## Source References

- Original upstream repository: `https://github.com/Qwertyil/HabitFlow.git`
- Intended personal lab repository: `https://github.com/badinoko/Habbit`

## Read First

1. `AGENTS.md`
2. `CODEX.md`
3. `README.md`
4. `frontend-redesign-contracts.md`
5. `docs/overview.mdc`
6. `docs/api_contract.mdc`
7. `docs/session_contract.mdc`
8. `docs/project/overview.md`
9. `docs/project/progress.md`
10. `docs/imports/besedka_design_kit_2026-03/README.md`

## Current Session Goal

Work from the real checkout so the next chat window can:

1. recognize that this is HabitFlow, not Besedka;
2. understand that `HabitFlow-master` is now only a reference snapshot;
3. continue from a checkout linked to the user's own repository model;
4. start a baseline audit of frontend issues, backend issues, and Google OAuth;
5. keep Besedka redesign knowledge immediately available for HabitFlow adaptation.

## Immediate Next Actions

1. Verify the local checkout remotes and push model:
   - `upstream` = `Qwertyil/HabitFlow`
   - `origin` = `badinoko/Habbit`
2. Run the project locally and capture runtime baseline failures.
3. Audit Google OAuth configuration and callback baseline.
4. Capture HabitFlow current-state screenshots and page inventory.
5. Prepare redesign invariants and an external-artifact prompt adapted from the Besedka kit.

## Notes

- Do not work from `HabitFlow-master` unless reference files are needed.
- Do not claim sync with GitHub until push to `origin` is actually verified.
- Google OAuth is already implemented in code and should be audited as a real feature, not treated as a future stub.
- Frontend redesign must respect current product scope from `frontend-redesign-contracts.md`.
- Imported Besedka redesign references live in `docs/imports/besedka_design_kit_2026-03/`.
