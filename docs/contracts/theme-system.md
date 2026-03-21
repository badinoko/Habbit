# Theme System

`docs/contracts/theme-system.md` is the SSOT for HabitFlow UI theming.

## Current Contract

- Two runtime themes are supported: `light` and `dark`.
- The active theme is stored only in browser `localStorage` under `habitflow-ui-theme`.
- The active theme is applied on `<html>` via `data-ui-theme="light|dark"`.
- Theme switching is client-side only and must not trigger a full page reload.
- Server-side UI session still stores only the selected data filter theme (`selected_theme`) for `tasks` and `habits`; it does not store the visual color theme.

## Source Files

- `src/static/css/design-system.css` defines the semantic tokens and the `html[data-ui-theme="dark"]` overrides.
- `src/static/css/navbar.css` and the page/module CSS files consume those tokens.
- `src/static/js/ui.js` owns theme persistence, toggle behavior, and label/icon sync.
- `src/templates/base.html` bootstraps the saved theme before CSS paints and exposes toggle controls in the navbar and user dropdown.

## Token Rules

Use semantic tokens, not page-local hardcoded colors, for reusable UI surfaces.

Core tokens currently include:

- Brand and status: `--accent`, `--accent-strong`, `--accent-2`, `--mint`, `--danger`, `--warn`, `--info`
- Surfaces and text: `--bg`, `--bg-elevated`, `--surface`, `--surface-2`, `--border`, `--border-strong`, `--text`, `--text-soft`, `--muted`
- Effects and layout: `--shadow-sm`, `--shadow-md`, `--radius-*`, `--nav-h`, `--sidebar-w`, `--container`
- Theme-tag helpers: `--theme-work`, `--theme-health`, `--theme-study`, `--theme-home`, `--theme-none`

Component CSS should reference these semantic variables instead of embedding separate light/dark values per component.

## Interaction Rules

- Navbar stays sticky; theme controls live in the top shell, not inside page-specific layouts.
- Theme toggle updates only the DOM state and persisted browser preference.
- Enhanced navigation in `src/static/js/ui.js` must preserve the current visual theme across partial content swaps.
- OAuth start links are excluded from enhanced navigation so provider redirects still use normal browser navigation.

## Adding A New Theme

1. Add or adjust semantic tokens in `:root`.
2. Add a full override block for `html[data-ui-theme="<name>"]`.
3. Ensure components still consume semantic tokens rather than branching locally.
4. Extend `getTheme()` / `applyTheme()` in `src/static/js/ui.js`.
5. Update this document and any user-facing docs that mention supported themes.

## Non-Goals

- No per-user server-side theme profile yet.
- No custom theme editor yet.
- No expansion into broader settings/profile pages unless explicitly added to product scope.
