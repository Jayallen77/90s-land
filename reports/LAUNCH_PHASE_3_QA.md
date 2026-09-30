# 90s.land — launch Phase 3

Completed September 30, 2026. This sprint preserves the approved visual system,
existing URLs, historical dates, source records, object media, and six-stop tour.
It finishes discovery, sharing, metadata, and launch verification.

## Major changes

- Added **192 content-specific sharing cards** at 1200 × 630. Every principal
  route and each of the 101 defining events gets its own card. Other event
  pages use their year’s card. Cards use reviewed object imagery, labeled
  editorial illustrations, or an original graphic, with creator/license credits.
  JPEG filenames reflect their inputs; the manifest and build gate detect drift.
- Broadened **Surprise Me to 180 destinations**: 30 stories, 30 objects,
  101 defining events, 10 years, eight collections, and the existing tour.
  Type weights favor stories and objects without letting the large event pool
  dominate. The last three picks stay excluded. Objects open their detail pages.
  Removed the artificial 650 ms wait and guarded overlapping requests.
- **This Week** selects up to four actual entries, prioritizes defining moments,
  spreads themes, and limits its short selection to two films. The seven-day
  calendar keeps every entry. Year and collection links follow the selected
  week. Nearby dates remain explicitly outside empty weeks. The New York date
  refreshes on visibility changes and once per minute; custom selections stay put.
  The saved no-JavaScript week remains explicitly dated September 27, 2026.
- **Passport** now counts “places explored,” including years and collections,
  explains local browser storage, and visibly distinguishes earned/unearned stamps.
  Existing state keys, IDs, progress, and milestones remain compatible.
- **Before the Feed** retains all six stops, back/next, deep links, browser history,
  interactive recreations, inspection, resume, and completion. Its finish panel
  offers Passport, Internet Culture, and Surprise Me. Reset clears completion.

## SEO and crawlability

All 533 routes have unique titles and descriptions, self-canonicals, Open Graph
and Twitter metadata, image dimensions, and sharing-image alt text. Titles
specifically describe year timelines, Internet Culture, transparent electronics,
video-store nights, AIM, and Y2K. The ten-year structure retains paths to 1998
technology and other long-tail content.

The sitemap contains **531 indexable routes**. Search results and the unsaved
Guestbook preview use `noindex,follow`; the real 404 page is also noindex. Robots
allows crawling and points to the sitemap. Added WebSite and BreadcrumbList
schema while retaining 30 Article and 472 WebPage records. Historical event
dates are not presented as website publication dates.

The implementation follows [Open Graph metadata](https://ogp.me/),
[Google canonical guidance](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls),
[noindex guidance](https://developers.google.com/search/docs/crawling-indexing/block-indexing),
and [breadcrumb guidance](https://developers.google.com/search/docs/appearance/structured-data/breadcrumb).
Local verification covers metadata and image delivery. Platform caches and actual
shared-link appearance still require the new release to be deployed.

## Bugs and accessibility

Fixed Search count badges changing width and wrapping filter rows during query
initialization. Preloaded its existing semibold filter font, reserved the results
region, and withheld the enhanced grid until filtering finishes. This removes
the measured initial layout shift while retaining the full static fallback.
Removed stale count updates that wrote overlapping numbers into
retired bookmark anchors; the anchors remain valid and empty. Increased the
homepage Internet Culture link’s tap target to 44 px. Weekly curation’s film
limit is scoped to weekly highlights, preserving three related events on object
pages. The tour completion Passport action has its own hook, preserving the
standard footer trigger.
Corrected doubled periods in three year summaries shown in Search.

Keyboard focus, modal Escape/focus return, directory navigation, controls,
reduced motion, storage failure, JavaScript/fetch failure, and readable static
fallbacks are covered by browser regressions. The suite includes axe checks.
Public-copy and metadata checks found no missing h1s, image alt attributes,
duplicate titles/descriptions, unfinished public copy, or invalid structured data.

## Verification and performance

Final measured results are recorded in [verification.json](launch-phase3/verification.json)
and [the Lighthouse summary](launch-phase3/lighthouse-after/summary.json).
The baseline and final performance comparison is in
[performance-comparison.json](launch-phase3/performance-comparison.json).

The final suite passed **174/174 browser checks**, **48/48 Python tests**, and
**9/9 date/discovery tests**. The tour's earlier stability check passed 20 consecutive
runs. HTTP delivery passed **533/533 routes**, **192/192 sharing images**, 12 gzip
samples, and all 56 private-path exclusions. Publication and static audits reported
zero errors. The capture set contains 60 route views and two Passport views.

Across 30 Lighthouse audits (15 pages × two modes), mobile performance was
**93–99**, desktop performance **99–100**, accessibility **100**,
and best practices **100**. All 28 audits of indexable content pages scored **100 SEO**.
Search's raw SEO score is **69** because its deliberate `noindex,follow` fails
Lighthouse's indexing audit. That policy is checked explicitly; every other
applicable SEO audit passes. Raw scores remain in the evidence. The runner also
requires CLS ≤ 0.1, mobile performance ≥ 85, and desktop performance ≥ 90.

| Page | Mobile performance, before → after | Desktop performance, before → after |
| --- | ---: | ---: |
| home | 97 → 97 | 99 → 100 |
| year-1996 | 95 → 95 | 100 → 100 |
| week | 96 → 96 | 100 → 100 |
| search | 92 → 95 | 100 → 100 |

Homepage accessibility improved from 96 to 100. Search CLS decreased from
0.111 to 0.000 on mobile and 0.046 to
0.000 on desktop. Small performance-score
differences on the other pages are within the limits of single-run lab comparisons.

The route suite checks all 533 routes at four viewport widths, all calendar
filter combinations, and 522 historical weeks at two widths. It also checks
the new shuffle kinds, rapid requests, New York midnight rollover, custom-week
preservation, Passport states, and tour finish/reset behavior. Python tests cover
publication, content preservation, release boundaries, deterministic packaging,
and deployment/rollback failure modes. Date/discovery tests exercise selection
weights, recency, date boundaries, and honest weekly picks.

Manually reviewed home, all ten years, Music, Movies & TV, Games, Tech, Culture,
Fashion, Internet Culture, Transparent Tech, This Week, Search, Objects, Stories,
Surprise Me, the tour, Passport, Credits, Resources, and Sitemap. Reviewed
representative story/object pages too. Desktop/mobile captures and review sheets
are under [screenshots](launch-phase3/screenshots/inventory.json); the required
surfaces have no detected horizontal overflow or uncaught browser errors.

Performance work preserves image quality and local optimized fonts. The site
still uses responsive AVIF/WebP derivatives, intrinsic image dimensions, gzip,
and conditional browser modules. Sharing JPEGs are crawler assets, not added
page-image downloads. Search layout stability and immediate Surprise Me loading
are the main visitor-facing performance fixes. Lighthouse measurements are
throttled localhost lab results, not production field measurements.

## External links and remaining limits

The final source/resource crawl checked **240 unique URLs** from 799 published
links: 218 reachable, 12 access-blocked/rate-limited, and 10 unresolved through
the HTTP checker. It found no confirmed 404/410 destinations. Six unresolved
URLs yielded publisher content through a separate web reader, which may use
cached responses; their HTTP classifications remain unchanged. Four still
failed both approaches. No historical source or resource was silently removed.
Full destinations, affected routes, and failure details are in
[external-links.json](launch-phase3/external-links.json) and
[external-followup.json](launch-phase3/external-followup.json).

## Material files and delivery

Authoritative implementation: `tools/launch_meta.py`, `tools/build_share_cards.py`,
`tools/discovery.py`, `tools/render_site.py`, `tools/archive_content.py`,
`tools/archive_pages.py`, `tools/editorial.py`, and `js/discovery.js`.
Interaction polish: `js/archive.js`, `js/search.js`, `js/surprise.js`,
`js/passport.js`, `js/tour.js`, `editorial.css`, `archive.css`, and `data/stamps.json`.
Build/QA: `tools/build_release.py`, `tools/check_release_http.py`, `tools/run_lighthouse.mjs`,
`tools/check_launch.py`, `tools/process_media.py`, `tools/capture_launch.mjs`,
the Phase 3 tests, and `package.json`. Generated route HTML, runtime JSON,
the sharing manifest/images, and sitemap are committed.

`process_media.py` now checks catalog pages rather than crawling temporary
Playwright traces. QA screenshot output respects the current sprint directory;
historical Phase 2 captures remain intact. Production packages use schema 3;
the verifier strictly supports previous schema-2 packages for replacement/rollback.

Source delivery targets the existing GitHub `main`. Build and deployment details
are in [LAUNCH_HANDOFF.md](../docs/LAUNCH_HANDOFF.md) and
[RELEASE.md](../docs/RELEASE.md). The verified package is local; no production
server configuration, restart, or live switch was performed.
