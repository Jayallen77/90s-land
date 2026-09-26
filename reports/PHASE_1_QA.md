# Phase 1 verification — September 26, 2026

Baseline commit: `a015cd39a15d0f062eac30fe4097a4e97078b651`.

## Result

Phase 1 preserves the existing presentation and establishes a reproducible,
review-only content import. No public HTML, CSS, JavaScript, media, or original
catalog contents were changed. No deployment or external publication occurred.

| Check | Result |
|---|---|
| Extraction from frozen source | Nine catalogs reproduce without drift |
| Catalog/migration validation | Zero errors |
| Original served-file fingerprints | All match the baseline |
| Coverage-report reproducibility | Pass |
| Reference and snapshot fingerprints | Pass |
| Desktop/mobile visual baseline | Six frozen captures verified |
| Existing page generation | Current; no changed output |
| Media derivatives/dimensions | Current |
| Static audit | 26 routes; 1,711 internal links; 1,017 external links; 1,003 fragment links; zero errors |
| Python migration acceptance tests | 14 passed |
| Playwright/browser and axe regression tests | 22 passed |
| Tracked diff whitespace check | Pass |

## What the migration tests protect

Tests exercise deterministic extraction, Unicode/entity offsets, snapshot
integrity, complete source coverage, missing month/anchor/disposition detection,
chart/artist-credit relationships, annual scope, source references, and draft
status. They also prove that new artifacts/resources/featured selections are
allowed while same-count replacement cannot hide deletion of baseline IDs.

Browser checks preserve responsive bounds across four viewport sizes, menu and
dialog behavior, Passport persistence/fallback/reset, Surprise Me repeat
avoidance, tour navigation/resume/completion, search URL state/counts, the
guestbook preview, no-JavaScript fallbacks, timeline controls, and axe checks on
representative routes.

## Visual evidence

`reports/baseline/phase-1/screenshots.json` records image hashes, browser version,
viewport dimensions, document geometry, and the baseline revision. Home and
Timeline use 1086×724, Games uses 1182×665, and all three also use 390×844. Captures
use reduced motion and fresh browser contexts. These are screenshots of the
current site, not redesign previews.

## Limits and next phase

- All imported editorial claims remain unreviewed. External-link availability
  and historical accuracy were not researched in this phase.
- The review queue identifies 25 monthly cards without an external link, four
  vague artifact-license labels, and ten media files without structured artifact
  attribution. Original caption and source context remains preserved.
- This phase does not add the planned 30 new stories or 300 verified events.
- Lighthouse was not rerun because public delivery is unchanged. Measure the new
  design after implementation; do not reuse historical scores as current proof.
- Validation was completed on the local working tree before GitHub publication.
  No production deployment was made as part of Phase 1.

Use `docs/REBUILD_HANDOFF.md` for the Phase 2 checklist and
`docs/CONTENT_MIGRATION.md` for source ownership and validation commands.
