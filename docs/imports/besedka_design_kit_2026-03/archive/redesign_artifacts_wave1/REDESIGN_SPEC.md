# REDESIGN SPEC - Besedka Visual Redesign v2

> **Status:** In progress
> **Start:** 2026-03-11
> **Updated:** 2026-03-12
> **Decision authority:** Claude (full redesign freedom from owner)

---

## 1. PHILOSOPHY

Goal: make Besedka visually modern, lively, elegant but not "AI-looking".
Feel: as if a good designer worked on it.

**Principles:**
- Botanical palette: green (#2d8a56), amber, rose - natural accents
- Typography with character: Cormorant Garamond (headings), Caveat (accents), Inter (body)
- Minimalism with warmth: clean lines + soft shadows + natural colors
- Each section is visually distinct but within a unified system
- Mobile-first thinking: everything designed for 430px first, then scaled up

---

## 2. ACCEPTED DECISIONS

### 2.1 Navbar + Sticky Bar = unified visual stack (ACCEPTED)

On mobile: navbar and sticky bar visually merge into one compact header.
Shared background, single thin divider. Total height ~104px instead of ~127px.

**Navbar (64px, can shrink to 56px on mobile):**
- Left: hamburger (compact, 32px) + logo "Besedka" (Cormorant Garamond)
- Center: section name (mobile), section buttons (desktop)
- Right: bell + avatar/dropdown

**Three center states:**
1. Public/main - section buttons (desktop) / section name (mobile)
2. Admin - dropdown switching between admin panels
3. Chat - dropdown switching between chats (general, VIP)

**Sticky Bar (single-line ALWAYS, even on mobile):**
- Left: back (small circle) + context control (photo/album switcher OR nothing)
- Right: search (icon) + overflow menu (three dots -> dropdown)

**Overflow dropdown contains:**
- Sort (All / Popular / Discussed)
- View (grid / list)
- My photos / My reports
- Mark all read
- Filters

**FAB (Floating Action Button):**
- "Add" / "New report" button - circle, bottom-right on mobile
- On desktop stays in sticky bar as usual
- Color: --bs-accent-green with shadow and micro-animation

### 2.2 Homepage (DONE, accepted)

Hero section + content sections + community CTA.
Three dev containers (announcements, tasks, progress) are temporary, will be removed.

### 2.3 Listings (IN PROGRESS)

**Common principles:**
- Desktop: 3-4 columns
- Mobile: 1 column (news, growreports) or 2 columns (gallery photos)
- Cards with Cormorant Garamond titles
- Hover: translateY(-4px) + shadow enhancement

**News - featured card problem:**
- Large 2x2 featured card doesn't align with cards to the right
- Solution: drop 2x2 featured. Instead - first card full-width horizontal (image left, text right), rest - uniform 3-4 column grid

**Gallery photos:**
- Masonry-like grid with varying aspect-ratios
- Hover overlay: title + likes/comments
- Working well, keeping it

**Gallery albums:**
- Cards with 2x2 cover preview
- Cormorant for title

**GrowReports:**
- Must visually DIFFER from news cards
- Stage icon (seed/veg/flower/harvest) + progress bar
- Horizontal card (icon left, info right) on desktop
- Vertical on mobile

### 2.4 Detail pages

**News / Photo - two-column layout:**
- Left: content
- Right: sticky sidebar (author, tags, related)
- Mobile: sidebar below content

**GrowReport - timeline:**
- Hero with info cards + progress bar + stage dots
- Vertical timeline by weeks
- Each week = collapsible container (toggle)
- Inside: day entries
- Each entry: text + photos + metrics + reactions + comments
- Reaction picker - will be updated (currently "wooden")
- Buttons: report, share - need nice placement

### 2.5 Reactions and sharing

**Reaction picker:**
- Compact, pill-shaped
- On hover/click - expands emoji strip
- Current reaction highlighted in green

**Share button:**
- Generates link with OG-meta (logo, description)
- Share icon + tooltip "Copied!" on click

**Report button:**
- Flag icon, grey, unobtrusive
- Opens modal (already implemented as SSOT)

---

## 3. DO NOT CHANGE

- Backend (views, models, URLs)
- SSOT components (unified_card.html, unified_reactions.html, unified_pagination.html)
- JS logic (AJAX, localStorage, WebSocket)
- Admin panels (separate task)
- Chat (separate task, already has its own design)

---

## 4. CSS ARCHITECTURE

- All new styles in `static/css/redesign_v1.css`
- All colors through CSS variables `--bs-accent-*`
- Fonts: `--bs-font-display`, `--bs-font-handwritten`
- NO !important
- DO NOT edit existing CSS files (only add variables to themes_v2)
- Override styles through more specific selectors

---

## 5. WORK ORDER

### Wave 1 (COMPLETED):
- [x] Prototypes: homepage, listings, details (6 artifacts)
- [x] First implementation in Cursor
- [x] QA: homepage OK, gallery photos OK, news/growreports need another pass

### Wave 2 (CURRENT):
- [ ] New prototype: unified shell (navbar + sticky bar) - desktop + mobile
- [ ] New prototype: news listing with fixed featured composition
- [ ] New prototype: growreports listing with unique hierarchy
- [ ] Update gallery listings (minor improvements)
- [ ] Document in spec

### Wave 3 (NEXT):
- [ ] Wave 2 implementation in Cursor
- [ ] Detail pages: grow entries, reaction picker, share/report buttons
- [ ] Smoke tests, mobile, dark theme

---

## 6. FILE STRUCTURE

```
docs/artifacts/redesign_2026-03/
  INDEX.md
  REDESIGN_SPEC.md              <- THIS SPEC (updated regularly!)
  PROMPT_REDESIGN_IMPLEMENTATION.md
  ADAPTATION_PLAN.md
  home/
    homepage-redesign-v1.html
  listing/
    listing-redesign-v1.html
    gallery-list-redesign-v1.html
  detail/
    news-detail-redesign-v1.html
    photo-detail-redesign-v1.html
    growreport-detail-redesign-v1.html
  shell/                        <- NEW (Wave 2)
    shell-v2.html               <- Navbar + sticky bar all states
```

---

## 7. SCREENSHOTS

Current screenshots: `docs/screenshots/current_state/` (14 files)
After Wave 2 implementation: new screenshots to `docs/screenshots/redesign_wave2/`
