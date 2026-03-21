# Docs Map

This file is the navigation index for documentation in this repository.

## Canonical Roles

- `docs/overview.mdc` = product and architecture overview.
- `docs/api_contract.mdc` = HTTP and route contract.
- `docs/session_contract.mdc` = auth/session contract.
- `docs/theme-system.md` = SSOT for visual themes, theme tokens, and runtime theme switching.
- `docs/project/startup.md` = new-session handoff and current workspace state.
- `docs/project/overview.md` = the only task-status dashboard.
- `docs/project/progress.md` = append-only work log.
- `docs/operations/codex_workflow.md` = assistant workflow rules.

## Evidence And Inputs

- `docs/screenshots/current_state/` = baseline UI captures for audit and redesign.
- `docs/artifacts-master-prompt.md` = master prompt to paste into the Artifacts tab before visual exploration.
- `docs/cursor-prompt.md` = reverse implementation prompt for Cursor based on the generated redesign artifacts.
- `docs/artifacts/` = local HTML artifact pack that drives the current frontend implementation wave.
- `docs/imports/besedka_design_kit_2026-03/` = imported reference kit from Besedka.

## Naming Rule

- `overview.mdc` in `docs/` is not the same thing as `docs/project/overview.md`.
- If the question is "what is the product and how is it built?" read `docs/overview.mdc`.
- If the question is "what task is active and what status is it in?" read `docs/project/overview.md`.

## Read Order

1. `AGENTS.md`
2. `CODEX.md`
3. `docs/README.md`
4. `docs/project/startup.md`
5. `docs/project/overview.md`
6. `docs/project/progress.md`
7. `README.md`
8. `frontend-redesign-contracts.md`
9. `docs/overview.mdc`
10. `docs/theme-system.md`
11. `docs/api_contract.mdc`
12. `docs/session_contract.mdc`
