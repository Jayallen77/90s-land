# Phase 3 verification

Reviewed locally September 27, 2026.

## Automated evidence

- **21 Python tests:** catalog integrity, rejection of missing sources/imprecise or
  invalid dates, relationship consistency, complete source-based generation,
  one search result per detail record, baseline anchor preservation, original
  reading-room prose preservation, and the existing import/growth safeguards.
- **6 date tests:** New York versus UTC date, leap-day mapping, invalid dates,
  Monday–Sunday boundaries, DST-safe arithmetic, inclusive events, and decade bounds.
- **43 browser scenarios:** all 81 routes at 390, 768, 1280, and 1440 pixels;
  calendar filters/view/month/history/reload/pagination; weekly default, date/year
  navigation, fallback and empty states; accent/date/region search; detail links;
  no-JavaScript reading; Passport, Surprise Me, tour, guestbook, and old deep links.
  The final complete run passed all 43 scenarios in 51.4 seconds.
- **14 axe checks** are included in those browser scenarios: the eight existing
  representative routes, five new archive surfaces, and the filtered mobile
  calendar. No outstanding violations after repairs.
- **Static link audit:** 81 catalog routes, 3,896 internal links, 1,290 fragment
  links, 30 objects, 78 resources, 12 featured resource references; zero errors.
  The audit inventories 1,067 external links; it does not claim to retest remote
  availability for the entire inherited directory.
- Renderer and media `--check` pass. The immutable migration extraction and
  coverage report remain reproducible; content validation reports zero errors.

## Visual evidence

Six full-page screenshots and machine-readable viewport/error metrics are in
[`phase-3/`](phase-3/), generated with `node tools/capture_phase3.mjs`:

- Desktop June 1996 calendar, historical week, and complete story.
- Mobile June calendar/agenda, historical week, and object profile.

Each captured surface has zero horizontal overflow and no browser exceptions.
The mobile calendar uses compact category labels with full accessible link names
and a readable filtered event list below it. The weekly lead appears before the
day-by-day entries. Sources, credits, related records, and original museum tools
remain reachable.

The review repaired a deep-link scroll shift caused by fonts loading after an
expanded reading room, missing inline-link underlines, a heading-level skip in
the weekly lead, and a CSS specificity conflict in the mobile agenda. Regression
checks cover the affected interactions.

## Scope and limits

Twenty dated events and two complete original stories are starter content for
Phase 3. The Phase 4 coverage and media-review targets are outstanding. This report
does not reuse earlier Lighthouse scores as measurements of the new pages; fresh
performance/release validation belongs to Phase 5. No GitHub push or production
deployment was performed for Phase 3.
