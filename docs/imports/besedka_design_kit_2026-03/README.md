# Besedka Design Kit Import

Imported on: 2026-03-21

Purpose: keep a local design knowledge base from Besedka inside HabitFlow so redesign work can start immediately in a new chat window without re-collecting prompts, artifacts, and visual references.

## Important Notes

- This folder is an imported reference pack, not HabitFlow SSOT.
- Product/domain language inside these files belongs to Besedka and must be adapted before direct implementation.
- Reuse the visual logic, prompt structure, artifact workflow, and layout patterns, not the product-specific nouns.

## Bundle Map

### `core/`

- `BESEDKA_SSOT_COMPONENTS.md` — reusable component mindset and UI decomposition habits.
- `THEME_AND_UI_REFERENCE.md` — the strongest single reference for look-and-feel decisions, tokens, surfaces, spacing, and interaction language.
- `BREAKPOINTS_SSOT.md` — viewport and responsive guardrails.

### `artifacts/redesign_2026-03/`

- Current redesign pack from Besedka.
- Includes `DESIGN_SYSTEM.md`, `DESIGN_DECISIONS.md`, homepage/listing/detail HTML artifacts, and Wave 2 prompts for implementation and external assistants.

### `homepage/homepage_docs/`

- Homepage-specific working context from Besedka:
  - `overview.md`
  - `startup.md`
  - `progress.md`
  - `besedka-homepage.html`
  - screenshots

Useful as a model for how to track one redesign stream from idea to implementation.

### `screenshots/`

- `ARTIFACTS_BRIEF.md` — компактный дизайн-бриф под главную, листинги и detail-поток.
- `current_state/` — before-state screens from Besedka.
- `redesign_wave2/` — desktop/mobile redesign screenshots.

Useful for visual comparison, density decisions, and seeing how the redesign translated into actual screens.

### `archive/redesign_artifacts_wave1/`

- Earlier redesign wave with shell/listing/detail artifacts and prompts.

Useful for tracing iteration history and extracting reusable prompt patterns.

### `archive/research_complete_2025-09-12/`

- Design research summaries and comparisons across UI systems and visual directions.

Useful when we need to justify why a certain design language fits HabitFlow better.

### `archive/reference_packs/`

- `growreports_reference/` — dense reference pack with screens, DOM, metrics, perf, a11y, and flow notes for home/list/detail-like structures.
- `gallery_reference/` — similar reference pack for gallery listing and photo detail behavior.

These are heavier than the rest of the import, but valuable when we need concrete layout evidence rather than abstract inspiration.

### `archive/mobile_redesign_history/`

- Older mobile redesign notes, planning docs, and session files.

Useful when HabitFlow reaches mobile-specific passes.

### `archive/`

- `CURSOR_IMPLEMENTATION_PROMPT.md`
- `design_draft.md`
- `claude_artifacts_prompt_2025-10-04.md`

These are older but still useful prompt/process references.

### `prompt_library/`

- `GLOBAL_CURSOR_PROMPT.md`
- `02_DEEP_RESEARCH_PROMPT.md`

General prompt scaffolds that may help structure design exploration and external assistant tasks.

## Suggested First Reads For HabitFlow

1. `core/THEME_AND_UI_REFERENCE.md`
2. `artifacts/redesign_2026-03/DESIGN_SYSTEM.md`
3. `artifacts/redesign_2026-03/DESIGN_DECISIONS.md`
4. `artifacts/redesign_2026-03/PROMPT_WAVE2_IMPLEMENTATION.md`
5. `artifacts/redesign_2026-03/PROMPT_WAVE2_EXTERNAL_ASSISTANT.md`
6. `screenshots/redesign_wave2/desktop/`
7. `homepage/homepage_docs/besedka-homepage.html`

## HabitFlow Adaptation Heuristic

When reusing this pack for HabitFlow:

1. keep the structural lessons:
   - strong shell
   - confident typography
   - purposeful empty states
   - expressive but controlled surfaces
   - consistent mobile/desktop rhythm
2. preserve HabitFlow product truth:
   - personal productivity app
   - tasks, habits, themes
   - no fake analytics, no invented collaboration layer
3. convert Besedka-specific artifacts into HabitFlow-specific screens:
   - home dashboard
   - auth pages
   - themes list/forms
   - tasks list/forms
   - habits list/forms
   - message/error screens
