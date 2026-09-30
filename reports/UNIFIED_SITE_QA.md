# Unified site implementation and verification

Verified locally on 2026-09-30, on `main`. This report covers the complete design
cleanup; it does not claim a GitHub push or VPS deployment.

## Result

Public pages are composed directly from authoritative Python renderers and
catalogs. The former full-page fragments under `content/pages/`, their manifest,
`preserved_content()`, `apply_shell()`, and the raw-page injection/normalization
pipeline are removed. Generated pages have one main, one H1, one shared header,
footer, and discovery navigation. Regression tests reject old reading rooms,
preserved bodies, fake page windows, and title bars throughout the generated site.

The approved Home/Games/Music/1996 identity remains: navy surfaces, palm/sunset
branding, the existing collage heroes, Jersey display type, Barlow text, condensed
labels, and pink/cyan/purple/yellow accents. Specialist and utility pages now use
the same shell, controls, cards, breadcrumbs, and dialogs. Intentional historical
interface exhibits remain inside the modern page composition.

Navigation retains category state and gives existing events a direct `/events/`
collection. Search, resource, and event collections share compact pagination.
Fashion and Internet Culture belong under Culture; Transparent Tech belongs
under Tech. Guestbook links and the form explicitly describe temporary previews.
Every one of the 676 original baseline anchors remains in generated output, with
retired section IDs mapped to corresponding live content and month bookmarks
selecting the requested month.

The 384 existing events, 30 stories, 30 objects, 78 resources, and six-stop tour
remain. There was no historical-library expansion. Blockbuster imagery is labeled
as an interior; Tamagotchi and game entries use clean graphics where no relevant
photograph is available. Small reading images retain their proportions and are
height-limited. Original media attribution remains.

## Verification

| Check | Final result |
| --- | --- |
| Python content/generator/release tests | 37 passed |
| Civil-date tests | 6 passed |
| Browser interactions and accessibility | 65 passed |
| Responsive route sweeps | 32 batches passed: all 475 routes at four widths |
| Visual review | 112 captures: 28 page families at 390, 768, 1280, 1440px |
| Capture health | All HTTP 200; no horizontal overflow or legacy page layouts |
| Internal link audit | 16,299 internal links; 1,599 fragment links; zero errors |
| Migration extraction and coverage | Frozen extraction unchanged; coverage reports current |
| Editorial gate | 384 sourced events, 30 complete stories, 37 reviewed media records, 12 game picks; no errors |
| Assets and media | 103 optimized files current; media dimensions current |
| Clean regeneration | 484 generated files unchanged; renderer check passes |
| Diff whitespace | `git diff --check` passes |
| Production packaging | Schema 2; 475 routes; 619 runtime files; build/check pass |
| Packaged HTTP audit | 475 routes pass; 55 excluded-path probes return 404; 12 identity/gzip samples pass |
| Packaged browser smoke | Home, previously timing-out AOL story, Events, filtered Games, Internet Culture, Search, plus mobile Passport reset/cancel; no errors |

Every major page family was inspected: Home, Timeline, year and month views, the
five hubs, Fashion, Internet Culture, Transparent Tech, story/event/object indexes
and details, Search, Resources, Tour, Surprise Me, Passport, Guestbook, Sitemap,
Credits, 404, and This Week. Inspection also corrected selected-month/filter
styling, hidden skip-link capture artifacts, Passport stamp icons, an Events
heading-order issue, and Credits link differentiation.

The normal browser checks cover timeline filters and history, game genre/platform
filters, search and resource state, pagination, This Week date navigation, the tour,
Surprise Me, local Passport/stamping/reset, guestbook previews, keyboard controls,
old deep links, and no-JavaScript fallbacks. Long route sweeps are split into
bounded batches rather than one timeout-prone site-wide test.

Final logs, HTTP evidence, and screenshots are retained under ignored
`dist/redesign/`. Reproduce screenshots with `node tools/capture_redesign.mjs`;
the full command contract is in `docs/design/UNIFIED_SITE.md`.

## Production boundary and handoff

The intended web root remains **`dist/release/public/`**. Sources, tests, tooling,
reports, docs, `.git`, `content/`, and private `data/` catalogs remain outside the
public package. Only the deliberately limited generated week/surprise payloads
cross the browser data boundary. The release verifier rejects unmanaged paths,
symlinks, and private dependencies. No VPS or Caddy settings were changed.

Verified content digest:
`2cf8dff6e4261e8444e6b69b613371735b5f2ed8b11b434eb98d23817595248d`.

Review the local production preview at `http://127.0.0.1:4174/`. GitHub publication
and VPS deployment are separate steps; the existing publishing and rollback
procedure remains in `docs/RELEASE.md`.
