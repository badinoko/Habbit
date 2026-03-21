# Docs Map

This file is the navigation index for documentation in this repository.

## Canonical Roles

- `docs/overview.mdc` = product and architecture overview.
- `docs/contracts/api_contract.mdc` = HTTP and route contract.
- `docs/contracts/session_contract.mdc` = auth/session contract.
- `docs/contracts/theme-system.md` = SSOT for visual themes, theme tokens, and runtime theme switching.
- `docs/project/startup.md` = new-session handoff and current workspace state.
- `docs/project/overview.md` = the only task-status dashboard.
- `docs/project/progress.md` = append-only work log.
- `docs/archive/README.md` = archive policy and index for frozen large working documents.
- `docs/operations/codex_workflow.md` = assistant workflow rules.

## Evidence And Inputs

- `docs/screenshots/current_state/` = baseline UI captures for audit and redesign.
- `docs/prompts/artifacts-master-prompt.md` = master prompt to paste into the Artifacts tab before visual exploration.
- `docs/prompts/cursor-prompt.md` = reverse implementation prompt for Cursor based on the generated redesign artifacts.
- `docs/artifacts/` = local HTML artifact pack that drives the current frontend implementation wave.
- `docs/reviews/architecture-audit.md` = local architecture review snapshot for handoff/reference.
- `docs/reviews/upstream-proposal-v1.md` = concise note for the original upstream author about what changed and how to review our fork safely.
- `docs/reviews/v2-typography-research.md` = working note on Besedka typography and transferability into HabitFlow v2.
- `docs/reviews/v2-landing-reference-scan.md` = external landing reference scan for v2 hierarchy, typography, and navbar direction.
- `docs/reviews/v2-navbar-and-stats-notes.md` = direct user feedback notes on navbar density/readability and possible stats-page sticky section navigation.

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
10. `docs/contracts/theme-system.md`
11. `docs/contracts/api_contract.mdc`
12. `docs/contracts/session_contract.mdc`
