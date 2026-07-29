# 90s.land Share-Ready QA Report

## Verified baseline — July 28, 2026

- Local `main`, GitHub `main`, and the audited source commit matched at
  `c8ce73f78c0d401c559a2dba88b8424f4e7bd585`.
- Production spot checks of the homepage, shared CSS and JavaScript, the 1994
  capsule, and the Webring were byte-for-byte identical to the repository.
- 23 HTML pages and approximately 43,302 visible words.
- 1,395 internal links and 875 external links.
- 0 broken internal page destinations and 13 invalid fragments.
- 78 unique Webring resources rendered as 90 card instances because the
  12 featured entries were duplicated in the directory below.
- 64 image elements, all missing explicit intrinsic dimensions.
- No canonical links, Open Graph metadata, XML sitemap, robots file, custom 404,
  or manifest.
- No global skip link, reduced-motion stylesheet, or consistent focus treatment.
- Representative 390-pixel audits found 31 pixels of overflow on the 1994 page
  and 25 pixels on the Internet Culture room.
- Production returned Cloudflare-served dynamic HTML without the requested
  security headers. `/robots.txt`, `/sitemap.xml`, and an unknown route returned
  empty 404 responses.

## Final results

Verified locally on July 28, 2026 from
`codex/playable-museum-overhaul`. Production was not changed.

### Catalog and static integrity

- 26 cataloged public routes plus the branded `404.html`.
- Approximately 52,200 visible words across cataloged routes; all existing
  year and room writing remains available.
- 1,575 internal-link instances, 1,017 external-link instances, and 870
  fragment-link instances.
- 0 broken internal routes, fragments, catalog targets, or local image assets.
- The 13 known invalid fragments were repaired: January–December anchors on
  1994 and `#genre-shelves` in the Music room.
- 30 structured artifacts, 78 unique resources, 12 featured resource
  references, six tour stops, and five passport stamps.
- 104 image elements across cataloged routes; 0 missing intrinsic dimensions.
- 0 undocumented `!important` declarations.
- Generated HTML and media checks pass with no drift.

The baseline phrasing “90 Webring resources displayed as 78” was clarified
during migration: the legacy file contained 78 unique destinations and rendered
12 of them twice as featured cards, for 90 card instances. The new catalog keeps
78 unique records and labels the featured cards as references.

### Browser, keyboard, and accessibility

- Playwright: 19 tests pass. The suite covers all 26 routes at 390×844,
  768×1024, 1280×800, and 1440×900; no horizontal overflow or clipped controls
  remain.
- Lobby requirements pass at 390×844 and 1280×800: all three primary actions
  are visible and the family-PC case begins on mobile and fully fits on desktop.
- axe: 0 violations on the lobby, timeline, 1994 capsule, Internet Culture,
  guided tour, and search.
- Agent-operated keyboard walkthrough passed for mobile navigation,
  Surprise Me, Passport, tour progression, and search, including Escape and
  focus restoration.
- JavaScript-disabled checks pass: core navigation, all six tour stops, all
  30 mystery-envelope links, search/resource cards, and exhibit copy remain
  available; the Passport control stays hidden until initialized.

### Lighthouse

Twelve local Lighthouse runs covered the lobby, timeline, 1994, Internet
Culture, the tour, and search:

- Performance: 97–99 mobile; 100 desktop.
- Accessibility: 100 for every run.
- Best Practices: 100 for every run.
- SEO: 100 for every run.

### External resources

The 78 resource-catalog destinations were checked with HEAD followed by GET
fallback and a 12-second timeout:

- 69 reachable.
- 5 returned HTTP 403 and are labeled as automated-check blocks.
- 3 timed out and 1 returned a certificate error; all four are labeled
  unresolved rather than removed.

The complete result is checked in at
`reports/external-resource-check.json`.

### Review artifacts and limitations

- Ten screenshots cover the lobby at four required viewports and mobile/desktop
  Surprise Me, Passport, and tour states.
- The original 1200×630 social card was generated once after visual
  stabilization; its visible text was applied deterministically and verified.
- Security, caching, HSTS, custom-404, CSP, referrer, MIME, permissions, and
  framing recommendations are documentation only in
  `ops/HEADER_RECOMMENDATIONS.md`.
- External availability remains time-sensitive. A final human screen-reader
  spot check and production-server header validation are still recommended
  before any separately approved deployment.

### Phase 2 backlog

- Additional guided tours.
- Full artifact migration beyond the initial 30 objects.
- Quiz Arcade.
- Mixtape Maker.
- Optional audio with explicit controls.
- Moderated community features.
- A later Astro evaluation after the static system has real usage evidence.
