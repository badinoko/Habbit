# Upstream Proposal: HabitFlow v1 Fork

This note explains what our fork changes relative to the upstream repository and how the original author can review it safely without risking the upstream `master` branch.

## Repositories

- Upstream source: `https://github.com/Qwertyil/HabitFlow`
- Our fork/lab repository: `https://github.com/badinoko/Habbit`
- Review checkpoint tag in our fork: `v1`

## Upstream Safety

We verified that the upstream repository is readable but not writable from our side.

- `git ls-remote upstream` works
- `git push --dry-run upstream HEAD:refs/heads/codex-v1-proposal` fails with `403 Permission denied`

That means:

- we did not modify upstream;
- we cannot create a proposal branch there from this environment;
- the safe review path is to share our repository or tag and let the upstream owner decide whether to pull anything in.

## Recommended Review Path For The Upstream Author

### Lowest-risk option

Open our fork and inspect tag `v1`:

- repo: `https://github.com/badinoko/Habbit`
- tag: `v1`

### If they want to compare locally

```bash
git clone https://github.com/Qwertyil/HabitFlow.git
cd HabitFlow
git remote add proposal https://github.com/badinoko/Habbit.git
git fetch proposal --tags
git diff master..proposal/v1 -- src/templates src/static src/routers/stats.py docs README.md
```

### If they want to cherry-pick only the handoff-ready UI wave

The two most relevant commits for the redesign package are:

- `b5187ad` - `Implement HabitFlow redesign shell and theme system`
- `2ded4fa` - `Prepare v1 handoff and docs cleanup`

If they do not want the documentation cleanup, they can start by reviewing only `b5187ad`.

## What Changed In Product Terms

This fork does more than repaint templates, but it does not intentionally expand the core product scope.

### User-facing changes

- New shared shell with sticky top navbar and a more deliberate page layout
- Redesigned home, tasks, habits, themes, stats, auth, forms, and message screens
- Light/dark visual theme switcher in the navbar
- Better auth overlay behavior instead of layout-shifting auth pages
- Partial client-side updates for list filters/sorts/theme navigation instead of full page reloads where feasible

### UX/implementation changes that support the redesign

- Introduced semantic design tokens and a dedicated theme system
- Added lightweight enhanced navigation logic in vanilla JS
- Preserved existing server-rendered architecture instead of rewriting into SPA/frontend framework
- Kept current product constraints: no teams, reminders, due dates, or admin dashboards added

## What Changed In Code Terms

### Added

- `src/static/css/design-system.css`
- `src/static/css/navbar.css`
- `src/static/css/app-shell.css`
- page-level CSS files for home/tasks/habits/themes/auth/message
- `src/static/js/ui.js` for theme persistence and partial navigation
- docs for contracts, prompts, reviews, screenshots, and handoff

### Reworked

- `src/templates/base.html`
- list/form/auth/stats templates
- several small vanilla JS files for filters, forms, and state updates

### Small logic/architecture touchpoints

- `src/routers/stats.py` now passes `hide_sidebar=True` for the stats page shell behavior
- Auth/template rendering now relies on a safer base-template fallback for missing sidebar stats context
- The UI theme is intentionally browser-local (`localStorage`) rather than stored in server session

These are implementation-support changes, not a backend domain redesign.

## What Did Not Change

- No database schema migration was added
- No new domain entities were introduced
- No intentional change to core task/habit business rules
- No attempt was made to push directly into upstream

## Documentation For Reviewers

If the upstream author wants a concise repo-local map, these files matter most:

- `README.md`
- `docs/README.md`
- `docs/contracts/theme-system.md`
- `docs/reviews/architecture-audit.md`
- `docs/project/overview.md`

## Practical Recommendation

The simplest way to show the work is:

1. send them the fork URL;
2. point them to tag `v1`;
3. mention that upstream was not touched and cannot be pushed from our side;
4. point them to commit `b5187ad` if they only want the design implementation pass.
