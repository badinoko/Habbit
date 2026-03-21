# V2 Navbar And Stats Notes

Status: working note for `HF-014`

Purpose:
- capture direct user feedback on navbar readability and stats-page structure;
- keep these notes separate from code until the next implementation wave starts.

## Clarifications

### What is `Inter`

`Inter` is the clean working sans font currently observed on Besedka.

In practical terms, this is the font role for:

- navbar links
- buttons
- form labels
- card text
- helper copy
- numbers and metrics in ordinary UI

It is not the expressive display font. It is the stable operational font.

### What is `script accent`

`Script accent` means a handwritten or calligraphic decorative font.

In the Besedka context this role is handled by `Caveat`.

This is not a base UI font. It is only suitable for:

- a small emotional note
- a signature-like phrase
- a tiny decorative accent on the homepage

It should not be used for:

- navbar
- forms
- stats widgets
- filters
- lists
- dense operational screens

## User Feedback On Current HabitFlow Navbar

Observed issue:

- the three main nav items, `Задачи`, `Привычки`, `Статистика`, feel too airy vertically
- even the active pill still has too much empty height inside it
- the text does not feel readable or alive enough

Interpretation:

- the navbar is not visually dense enough
- the text size and the height of the tap target are not working together
- the typeface does not currently create identity

Important nuance:

- the request is not to create font chaos
- the request is to build a stable role system and then give some roles more personality

## Working Navbar Direction

### Keep calm

The navbar should stay calmer than the homepage hero.

### Improve readability

Potential adjustments to test in v2:

- slightly larger nav text
- reduced vertical padding
- stronger weight contrast
- a less squat feeling in the active pill
- possibly a more vertically open UI sans if the current one keeps feeling too compressed

### Avoid overcorrection

Probably not desirable:

- display serif directly in the navbar
- handwritten/script font in the navbar
- excessive font mixing at the top shell level

## User Feedback On Page-System Roles

The user feedback points to a valid systems problem:

- discussing every screen one by one is inefficient
- HabitFlow has many templates and dense pages
- a base role system should reduce future debate and make the next wave more coherent

## Baseline Type Roles For HabitFlow V2

### Role 1. Shell UI

Used for:

- navbar
- sidebar
- buttons
- tabs
- form labels
- control text

Candidate direction:

- one clean UI sans

### Role 2. Display Headline

Used for:

- homepage hero
- major section intros
- selected large headings

Candidate direction:

- one serif display family

### Role 3. Section Heading

Used for:

- page titles
- card section titles
- form section labels
- stats subsection headings

Candidate direction:

- probably still the UI sans, but with stronger size/weight tuning than v1

### Role 4. Meta And Helper Copy

Used for:

- descriptions
- hints
- dates
- minor labels
- secondary stats text

Candidate direction:

- same UI sans, quieter color and lower emphasis

## User Feedback On Stats Page Structure

Current pain:

- the page starts well with the top summary and cards
- then the user scrolls into `Задачи`
- then scrolls again into `Привычки`
- the long vertical flow works, but it feels like the page is asking to be segmented more clearly

Analogy proposed by the user:

- a sticky left-side section switcher similar to the settings screen in another project
- only the selected right-side section is shown prominently

## Candidate Stats IA Direction

Potential left-side sticky switcher for:

- `Обзор`
- `Задачи`
- `Привычки`
- `Темы`
- `Инсайты`

Benefits:

- clearer section boundaries
- easier orientation in a dense stats page
- less blind scrolling
- more dashboard-like feeling

Open tradeoff:

- if each section becomes its own view-state, we should keep transitions partial and avoid full reloads
- the page must still work on narrower screens without becoming over-fragmented

## Current Recommendation

For the next v2 discussion round:

1. lock the role system first;
2. tune navbar density and readability second;
3. prototype the stats-page sticky switcher as an information-architecture option before implementation.
