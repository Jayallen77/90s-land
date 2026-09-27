# Phase 4 verification

Reviewed locally September 27, 2026. The content and section expansion is
complete. These are implementation checks, not a production deployment report.

## Automated evidence

- **24 Python tests:** source-based static generation, schema and relationship
  integrity, preservation of original prose and anchors, search records, growth
  safeguards, all 120 months, every 1996 week including the year boundary,
  complete stories, and rejection of unreviewed events.
- **6 date tests:** New York date handling, leap-day mapping, civil-date arithmetic,
  DST boundaries, inclusive weeks, and decade limits.
- **52 browser scenarios:** all 474 catalog routes at 390, 768, 1280, and 1440
  pixels; real calendars, pagination, filters, date navigation, reload/history,
  empty states, source links, search, Passport, Surprise Me, tour, guestbook,
  legacy anchors, and no-JavaScript reading. The new scenarios cover all five
  category hubs, every advertised topic, combined game genre/platform filters,
  invalid selections, the new Culture route, and story-library categories.
- **20 axe checks** are included in the browser scenarios: eight existing
  representative pages, five archive surfaces, the filtered mobile calendar,
  five category hubs, and the story library. Zero outstanding violations.
- **Static link audit:** 474 catalog routes, 17,048 internal links, 2,471 fragment
  links, 30 objects, 78 resources, and 12 featured resource references; zero
  errors. The audit inventories 1,524 external links but does not certify every
  inherited remote destination's availability.
- Renderer and media `--check` pass. Nine frozen-source migration catalogs remain
  reproducible with zero changed extraction outputs. The original coverage report
  is current and content validation reports zero errors.
- The independent [editorial coverage report](phase-4/editorial-coverage.json)
  confirms 384 events, 30 stories, all 120 months, at least three entries in each
  of 53 weeks starting in 1996, 37 reviewed media items, and 12 sourced game picks.

## Content and media review

All 30 original stories have four sections and 316–407 words of body prose.
There are six stories each for Games, Music, Movies & TV, Tech, and Culture.
Short event entries remain separately labeled dates rather than being counted
as full stories. Catalog sources contain 67 records; charts and game picks have
their own explicit source fields.

The 384-event catalog is film-heavy: 345 North American theatrical entries,
12 Tech, 11 Culture, eight Music, seven Games, and one News. Movie dates carry
regional and limited/preview/expansion qualifications. The public coverage note
identifies the uneven coverage and treats blank days as archive gaps.

The media review covers 24 existing photographs/screenshots, six original
interface recreations, and seven original AI hero illustrations. Credits disclose
resizing/cropping, link source records and license terms, and distinguish
illustration from documentary material. Dreamcast and Y2K office attribution
and source identities were corrected. The Phase 1 frozen material was not edited.

Historical rankings state the measurement: the music panel is the US 1996
Billboard year-end chart transcribed via Wikipedia; the movie panel measures
US/Canada receipts earned during calendar 1996, not lifetime box office. Game
and story picks are editorial, without invented popularity measurements.

## Visual evidence

[`phase-4/`](phase-4/) contains 16 full-page captures: Home, Timeline, Games,
Music, Movies & TV, Tech, Culture, and This Week, each at 1440×1000 and 390×844.
`layout-metrics.json` records zero horizontal overflow and no browser exceptions
for every capture. Generate them with `node tools/capture_phase4.mjs` while the
local server is running on port 4173.

The review repaired a mobile event-card grid conflict, added the missing story
library heading level, made weekly feature artwork follow its selected event,
and broadened Culture's featured dates beyond the year-boundary sports entries.
The new four section collages have local responsive WebP sizes. Original reading
rooms and discovery tools remain reachable below the editorial sections.

## Remaining phase boundary

Phase 5 remains open for further mobile refinement, final reference comparison,
fresh performance measurements, and production release/rollback preparation.
No older Lighthouse score is presented as a measurement of these expanded pages.
The 52 browser scenarios and screenshots are local verification; GitHub
publication does not establish that 90s.land production has deployed this commit.
