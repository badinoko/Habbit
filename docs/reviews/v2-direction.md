# V2 Direction

Status: decision doc for `HF-011` and `HF-014`

Purpose:
- freeze the agreed direction for HabitFlow redesign v2 in one place;
- convert the current research notes into implementation constraints;
- let the next implementation wave move without reopening the same typography/navbar/stats debates.

## Scope

This document covers:

- typography roles;
- navbar density and readability;
- homepage hierarchy;
- statistics page information architecture.

This document does not expand product scope.

HabitFlow remains:

- a personal productivity app;
- a server-rendered web UI;
- a product without task due dates, teams, reminders, or admin dashboards.

## Decision Summary

HabitFlow v2 will follow a balanced two-family system:

- one calm UI sans for the shell and all operational surfaces;
- one display serif for selective emotional hierarchy moments.

The shell should become denser and easier to scan, while the homepage hero can carry more identity.

The statistics page should become easier to navigate structurally, but without introducing new backend view state for this wave.

## Typography Roles

### Role 1. Shell UI

Decision:

- keep `Onest` as the functional UI sans for HabitFlow v2.

Use for:

- navbar;
- page titles;
- forms;
- lists;
- filters;
- cards;
- stats widgets;
- buttons;
- helper and meta copy.

Reason:

- it is already integrated;
- it reads well in Cyrillic;
- it supports a calmer and more operational shell than the current display-heavy treatment.

### Role 2. Display Serif

Decision:

- adopt `Cormorant Garamond` as the display serif for selective hierarchy moments.

Use for:

- homepage hero headline;
- future major landing or section-intro moments where spacing is generous.

Do not use for:

- navbar;
- forms;
- dense lists;
- filters;
- small stats labels;
- operational controls.

Reason:

- it transfers the useful Besedka lesson without importing Besedka tone literally;
- it gives identity to the landing layer without slowing down the application shell.

### Role 3. Meta And Helper Copy

Decision:

- keep meta, support, and secondary copy inside the same `Onest` family;
- separate them through size, weight, color, and spacing rather than through another font family.

Use for:

- eyebrow labels;
- descriptions;
- hints;
- timestamps;
- secondary stats copy.

### Rejected For Current Wave

Decision:

- do not introduce a script accent in v2 implementation wave 1.

Reason:

- the current problem is hierarchy and shell readability, not a lack of decorative personality;
- script would add risk before the system roles are stable.

## Navbar Direction

### Core Rule

The navbar stays calmer than the homepage hero.

### Decisions

- keep navbar typography in `Onest`;
- reduce the feeling of empty vertical space inside nav pills;
- slightly increase text readability through weight and spacing, not through decorative fonts;
- keep icon + label navigation;
- keep the top shell visually compact and operational.

### Explicit Non-Goals

- no serif in the navbar;
- no script in the navbar;
- no loud display styling for the brand wordmark;
- no font chaos across top-level controls.

## Homepage Direction

### Core Rule

The homepage hero is the primary place where typographic identity can become more expressive.

### Decisions

- keep the eyebrow as tracked uppercase sans;
- move the hero headline into the display serif role;
- keep the supporting paragraph and badges in the UI sans;
- increase hierarchy contrast through type roles and spacing instead of through more colors or more fonts.

### Constraint

The hero can feel warmer and more editorial than the shell, but it must still read like a productivity product rather than a community or magazine homepage.

## Statistics IA Direction

### Core Rule

`/stats` remains one page in this wave, but orientation should improve.

### Decisions

- keep one owner-scoped stats route;
- do not add server-side section state for this wave;
- introduce a local section index for faster movement between parts of the page;
- use a sticky left-side section switcher on wider screens;
- collapse to a simpler horizontal or stacked pattern on narrower screens.

### Target Sections

- `Обзор`
- `Задачи`
- `Привычки`
- `Темы`
- `Инсайты`

### Why This Direction

- it preserves the current backend contract;
- it improves orientation without fragmenting the page into separate routes;
- it is a low-risk IA upgrade before heavier stats redesign work.

## Theme-System Constraints

These decisions must remain compatible with `docs/contracts/theme-system.md`.

Keep:

- `light` and `dark` runtime themes;
- client-side theme switching only;
- `localStorage` persistence;
- `data-ui-theme` on `<html>`;
- no full page reload for theme changes.

Typography and layout changes should consume the existing semantic token system rather than bypass it with page-local color logic.

## Implementation Order

### Wave 1

- align shell typography roles with this document;
- tighten navbar density and readability;
- update homepage hero hierarchy;
- add a stats section index with responsive sticky behavior.

### Later, Only If Needed

- broaden serif usage beyond the homepage hero;
- test alternate UI sans candidates;
- reconsider a decorative accent layer after the shell is stable.

## Working Acceptance Criteria

The v2 direction is considered implemented correctly when:

- the shell reads as calmer and more operational than v1;
- the hero has a clearer identity than the navbar;
- the navbar feels denser without looking cramped;
- the stats page is easier to navigate without new backend complexity;
- no forbidden product-scope features are introduced.
