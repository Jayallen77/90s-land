# Phase 2: editorial visual system

Implemented September 26, 2026. The three supplied canvases remain the design
references; the new artwork is original illustration, not a copy of the reference
screenshots or documentary evidence.

## What shipped locally

- Palm/sunset SVG mark and a Jersey 10 wordmark; matching SVG favicon.
- Locally hosted Jersey 10 display, Barlow body, Barlow Condensed labels, and the
  existing Space Mono archive/date text. SIL licenses are in `assets/fonts/`.
- Eight primary destinations, active-page state, responsive keyboard-accessible
  menu, search entry, shared footer, and a separate discovery strip for Passport,
  Surprise Me, the tour, resources, and guestbook.
- Three original cinematic hero compositions and responsive WebP derivatives.
- Home weekly/featured/category row and six editorial picks; Games topic links,
  feature, five curator picks, platform tiles, era notes and deep dives; a June
  1996 composition with three sourced releases, four archive connections, sidebar
  modules, grid/list controls, month links, and decade navigation.
- Three compact, expandable reading rooms containing complete original main-page
  text and anchors. Direct fragment URLs open their containing room automatically;
  native details controls also work without JavaScript.

## Tokens and components

The authoritative styles are in `editorial.css`. The existing `styles.css` remains
for the preserved rooms and sections awaiting their full visual rebuild.

| Token | Value |
|---|---|
| Background | `#040817` |
| Panel / raised panel | `#080E20` / `#10172C` |
| Border | `#34375D` |
| Text / muted | `#F7F5FF` / `#BBC3D7` |
| Pink / cyan / purple / yellow | `#FF149F` / `#39D9DD` / `#9453F4` / `#FFD24A` |
| Maximum width | 1440px |
| Desktop / phone gutters | 24px / 16px |
| Panel gap / radius | 8px / 4px |

`tools/editorial.py` owns the shared header/footer, discovery strip, icons, hero,
panel heading, image card, page compositions, and reading-room wrapper. Primary
navigation is sourced from `data/navigation.json`. `tools/render_site.py` assembles
the pages; generated HTML is committed so hosting needs no Python or Node runtime.

## Artwork and fonts

The built-in OpenAI image generation tool produced the selected hero artwork. All
selected originals and runtime versions are saved inside the project:

- `assets/editorial/home-hero-original.png`
- `assets/editorial/timeline-hero-original.png`
- `assets/editorial/games-hero-original.png`
- Corresponding `*-hero-768.webp`, `*-hero-1440.webp`, and `*-hero-2172.webp` files.

The final prompts are in `docs/design/hero-prompts.json`. The raw PNGs are source
assets; pages request WebP derivatives. Native SVG artwork is in
`assets/editorial/palm-sunset.svg`. Existing object photographs retain their
catalog attribution and links on the public Credits page. Collage uses are
explicitly identified there as AI-generated editorial illustrations.

Font distributions were downloaded from the official Google Fonts repository:
[Jersey 10](https://github.com/google/fonts/tree/main/ofl/jersey10),
[Barlow](https://github.com/google/fonts/tree/main/ofl/barlow), and
[Barlow Condensed](https://github.com/google/fonts/tree/main/ofl/barlowcondensed).
No font service or third-party script is required at runtime.

## Phase boundary and intentional differences from the references

This phase establishes the reusable presentation system. It does not claim the
complete event calendar, 30 stories, 300 events, game catalog, or measured popularity.

- The home feature currently represents **September 23–29, 1996**. Its Nintendo
  launch claim links to Nintendo’s U.S. history. Automatic “30 years ago” date
  selection and browsing other weeks remain Phase 3 work.
- The Timeline composition starts at **June 1996** with three individually sourced
  releases in `content/editorial/timeline-1996.json`. The other four cards are
  explicitly archive connections. They are not four additional dated events.
- Month links reveal the corresponding preserved monthly context; they do not
  filter a complete event database. Grid/list controls switch the three highlights.
  A real daily calendar and URL-persistent filters remain Phase 3.
- “Culture” currently opens the existing Internet Culture collection. “This Week”
  opens the populated home module. Dedicated Culture and This Week pages arrive
  with their complete content/templates; no empty destination was added.
- Home selections are labeled **Editor picks**, and Games has a **curator’s
  starting five**. Neither is presented as measured popularity or historical sales.
- Games topic links lead to existing relevant exhibits/reading-room sections;
  they are not pretend genre filters over an unpublished game catalog.
- The reference’s imagery and some sample dates are illustrative, so its exact
  story subjects/rankings were not copied as historical fact.

The Phase 2 implementation was validated with a local preview before the requested
GitHub publication. Production deployment should publish an explicit runtime allowlist,
excluding frozen snapshots, raw artwork, tests, source prompts, and reports.

## Continue with Phase 3

Keep the frozen baseline and `content/migration/` intact. Promote reviewed material
to explicit source/story/event records, replace the reading-room bridge with full
static generation, add the daily calendar and historical-week behavior, expand
search/detail pages, and retain all current legacy-link and interaction checks.
