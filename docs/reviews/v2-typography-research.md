# V2 Typography Research

Status: working note for `HF-014`

Purpose:
- capture the actual typography signals from Besedka before touching HabitFlow v2;
- separate confirmed findings from hypotheses;
- define what is transferable into HabitFlow and what should stay Besedka-specific.

## Sources

- Besedka live homepage at `http://127.0.0.1:8001/`
- Besedka public site at `https://besedka.org/`
- User-provided Besedka homepage screenshots from the current chat
- Saved local HTML snapshot: `tmp_besedka_home.html`

## Confirmed Font Stack In Besedka

From the live homepage HTML:

- UI sans: `Inter`
- Display serif: `Cormorant Garamond`
- Accent handwritten script: `Caveat`

Loaded resources visible in the homepage HTML:

- `https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap`
- `https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600;700&family=Caveat:wght@500;700&display=swap`

The critical inline CSS also confirms:

- `body` uses `Inter`
- default heading rules initially inherit `Inter`
- the more expressive serif/script usage is likely introduced later by page-level CSS such as:
  - `/static/css/redesign_v1.css`
  - `/static/css/unified_styles.css`
  - `/static/css/navbar_v2.css`
  - `/static/css/besedka_themes_v2.css`

## Typography Roles Observed In Besedka

### 1. Functional UI layer

Used for:

- navbar links
- supporting paragraphs
- cards and metrics
- labels and utility copy
- buttons in most practical contexts

Characteristics:

- neutral grotesk
- compact and readable
- medium-to-strong weight hierarchy
- no decorative pressure

This role is clearly handled by `Inter`.

### 2. Display layer

Used for:

- hero headlines
- large section headlines
- expressive statement blocks

Characteristics:

- strong contrast with the UI layer
- large optical size
- editorial tone
- creates identity without polluting controls

This role is clearly handled by `Cormorant Garamond`.

### 3. Accent layer

Used for:

- small emotional or handwritten notes
- rare emphasis moments

Characteristics:

- informal
- warm
- decorative
- should be used very sparingly

This role is handled by `Caveat`.

## Structural Lessons From Besedka

### What works well

- Typography is role-based, not random.
- The serif layer appears only where it can dominate safely.
- The sans layer keeps the system usable and stable.
- The handwritten layer is rare enough to feel intentional.
- Eyebrow labels use uppercase sans with tracking, which creates rhythm before the headline.

### Why it feels richer than HabitFlow v1

- Besedka has much stronger scale contrast between eyebrow, headline, body, and CTA.
- Hero blocks are allowed to breathe.
- Headline font is visibly different from UI font, not just a heavier version of the same family.
- Utility copy stays disciplined, so decorative type has room to matter.

## Transferability To HabitFlow

### Safe to transfer

- two-tier system: `display serif + functional sans`
- uppercase tracked eyebrow pattern
- stronger separation between hero copy and operational UI copy
- larger headline scale than in the current HabitFlow v1 shell

### Transfer with caution

- handwritten accent layer

Reason:

- HabitFlow is a productivity product, not an editorial/community surface
- too much script typography will quickly look sentimental or noisy
- if used at all, it should stay on the homepage only and never enter forms, filters, stats, navbar, or list views

### Should not be copied literally

- Besedka content density and hero drama
- botanical/community semantics
- homepage-first editorial tone across the whole product

HabitFlow still needs:

- stronger operational clarity
- faster scanning in lists and forms
- calmer shell behavior

## Preliminary Direction For HabitFlow V2

### Recommended role split

- `UI sans` for navbar, forms, lists, filters, metrics, cards, buttons, helper text
- `Display serif` for homepage hero, major section leads, possibly select stats headlines
- optional `Accent script` only if a single narrow use-case survives review

### Recommended constraints

- no script font in navbar
- no script font in auth
- no script font in forms
- no serif in dense data tables or interactive filters
- serif should appear where line length and spacing can support it

## Open Questions Before Implementation

- Keep `Inter` as the functional base, or switch to another Cyrillic-friendly UI sans?
- Keep `Cormorant Garamond` as the display reference, or choose a sturdier serif for HabitFlow?
- Do we want any accent-script layer at all?
- How much of the serif layer should appear outside the homepage?
- Can navbar typography become more expressive without hurting scan speed?

## Working Recommendation

For v2 planning, the safest starting position is:

- keep a clean UI sans for the whole shell;
- introduce one expressive serif only for major homepage and section headings;
- postpone any script accent until after navbar and hierarchy problems are solved.
