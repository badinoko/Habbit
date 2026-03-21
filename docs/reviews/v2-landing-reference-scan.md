# V2 Landing Reference Scan

Status: working note for `HF-011` and `HF-014`

Purpose:
- collect modern landing-page reference patterns before HabitFlow v2 visual tuning;
- avoid copying one site blindly;
- extract reusable rules for typography, hierarchy, CTA framing, and navbar behavior.

## Sources

- Linear: `https://linear.app/`
- Raycast: `https://raycast.com/`
- Stripe: `https://stripe.com/`
- Besedka homepage: `http://127.0.0.1:8001/`

## Confirmed Technical Signals

### Linear

Observed from homepage HTML:

- preloads `InterVariable.woff2`
- uses a system built around variable `Inter`
- dark landing with very controlled type scales

Implication:

- modern product feel through spacing, polish, and rhythm rather than display-font theatrics

### Raycast

Observed from homepage HTML:

- self-hosted font files are preloaded from `_next/static/media/*.woff2`
- exact family names are not visible from the top-level HTML
- typography reads as modern sans with strong product-marketing polish

Implication:

- Raycast relies on strong type scale, compact spacing discipline, and highly polished CTA/card composition more than on obvious decorative font contrast

### Stripe

Observed from homepage HTML:

- preloads `Sohne`
- preloads `Source Code Pro`
- uses a premium product-marketing type system with a strong sans base and code/mono support

Implication:

- Stripe gets richness from contrast in scale, spacing, and layout orchestration, not from mixing many font personalities

### Besedka

Observed from homepage HTML:

- `Inter`
- `Cormorant Garamond`
- `Caveat`

Implication:

- Besedka is the only current reference in this set that clearly uses a three-role type system with a visible serif display layer and optional script accent

## Cross-Reference Patterns

### Pattern A: one strong functional sans

Seen in:

- Linear
- likely Raycast
- Stripe

Why it works:

- faster scan speed
- easier responsive behavior
- consistent UI tone
- less risk in dense product surfaces

### Pattern B: richness through scale, not font count

Seen in:

- Linear
- Stripe
- Raycast

Why it matters:

- a landing can feel premium even with one main family if hierarchy is strong enough
- many weaker redesigns fail because all text sizes are too similar, not because the font itself is wrong

### Pattern C: expressive serif reserved for editorial impact

Seen most clearly in:

- Besedka

Why it matters:

- serif can give identity fast
- but only if it stays out of utility-heavy surfaces

## What This Means For HabitFlow

HabitFlow is not:

- a pure SaaS marketing landing like Linear
- a developer-product launch page like Raycast
- a financial enterprise landing like Stripe
- a community/editorial homepage like Besedka

So the v2 target should be hybrid:

- product UI should stay operationally clear;
- homepage and selected headings can become more expressive;
- the shell must remain easier to scan than Besedka;
- typography should gain identity without slowing task management flows.

## Preliminary V2 Rules

### Likely good direction

- one strong Cyrillic-friendly UI sans across the shell
- one serif display family for homepage and major section leads
- stronger difference between headline scale and body scale
- better eyebrow/section-label system

### Likely bad direction

- multiple decorative fonts across all screens
- serif inside navbar and filters
- script font inside operational UI
- overly editorial homepage that fights the productivity purpose

## Navbar-Specific Relevance

From these references, one thing is consistent:

- navbars stay typographically calm even when the hero is expressive

That matters for HabitFlow v2:

- if we make the homepage more typographic, navbar should probably become cleaner, not louder
- strong identity should live below the navbar, not inside every top-level control

## Candidate Decision Paths For HabitFlow V2

### Path 1. Conservative

- keep current sans base
- increase scale contrast
- improve weights, spacing, and navbar density

### Path 2. Balanced

- keep clean UI sans
- add one serif display family for homepage and select section leads
- no script layer for now

### Path 3. Expressive

- UI sans + display serif + tiny script accent
- only acceptable if the script remains rare and homepage-only

## Current Recommendation

The best next experiment for HabitFlow looks like `Path 2`:

- one UI sans for everything functional
- one serif for major emotional or directional headings
- no script until navbar and overall hierarchy are settled
