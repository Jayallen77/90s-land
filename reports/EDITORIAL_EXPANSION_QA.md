# Editorial expansion — October 1, 2026

The approved 90s.land composition now contains a substantially larger connected
editorial library. New content is implemented in the current route, story, object,
search, calendar, category, Passport and Surprise Me systems.

## Content inventory

| Collection | Before this pass | Final library | Added |
| --- | ---: | ---: | ---: |
| Timeline events | 442 | 635 | 193 |
| Complete stories/features | 30 | 51 | 21 |
| Objects | 30 | 62 | 32 |
| Public routes | 533 | 779 | 246 |

The 21 new features contain 446–552 words of original prose each, divided into
sections with sources, related articles, objects and timeline connections.
Topics include AOL pricing, browser competition, MiniDisc, removable storage,
WebTV, demo discs, shareware, handhelds, Bristol music, breakbeats, sampling,
R&B, record shops, grunge, streetwear, skate/rave clothing, landlines, photo labs,
school computer labs/book fairs, holiday toys and SNICK.

Music now has 146 events (previously 18), technology 54 (25), games 42 (17),
and culture 31 (20). All 356 existing Movie/TV events remain. Story totals are
11 Music, 11 Tech, 9 Games, 13 Culture and 7 Movie/TV. Fashion receives three
new features, two sourced milestones, object photographs and editorial groups.
The Music hub links to 120 album selections spread across all ten years.
Nintendo entries distinguish original Japanese releases from other territories;
PC additions include Diablo, StarCraft and month-precision Warcraft.

| Year | Events | Year | Events |
| --- | ---: | --- | ---: |
| 1990 | 48 | 1995 | 52 |
| 1991 | 51 | 1996 | 188 |
| 1992 | 52 | 1997 | 43 |
| 1993 | 54 | 1998 | 48 |
| 1994 | 49 | 1999 | 50 |

## Research and factual scope

The connected Notion workspace contained 288 Daily Events records and 19
pipeline ideas. These were reviewed as research leads, not publication-ready
copy. Useful music leads were independently verified and rewritten. Incorrect
or unsupported dates were not imported, including the Tool CD/vinyl confusion,
the Macarena chart-week claim and the Red Alert date.

New source records include the Computer History Museum, Nintendo, Sony,
Blizzard, Casio, Fujifilm, FUBU, Marc Jacobs, Scholastic, contemporary reporting,
Universal Music Group's annual album guides and qualified historical discographies.
The catalog contains 217 source records. Existing event identities and source
assignments pass the preservation gate; sources were supplemented rather than
rewritten to accommodate the expansion.

The archive stores 470 day-precision, 8 month-precision and 157 year-precision
events. A month or year is displayed as such. No first-of-month/January-1 date is
invented for ordering, search, calendar cells or anniversary weeks. Year-only
entries have a distinct contextual shelf that follows category/region filters;
month-only entries remain visible in calendar view outside dated cells.

Thirty-two locally stored Commons photographs were selected by visual review,
with model/era notes, credit and license metadata. Responsive WebPs use the
existing image pipeline. These are authentic object photographs, often taken
later; they are not presented as period scenes. Existing labeled interface
recreations and original hero collages remain. Album cards use original
typography rather than pretending an unrelated photograph is an album cover.

The Resources section now opens with four guided collections. HEAD checks found
67 reachable links and 11 inconclusive outcomes (five denied, one method denied,
and five transport/time-out failures). No confirmed 404/410 resource was found;
blocked or inconclusive checks were not silently labeled dead.

## This Week and saved HTML

The publication clock uses America/Denver in Python and the browser. The current
civil date maps to 30 years earlier with leap-day clamping and the existing
1990–1999 boundary. Browser date rollover and adjacent/custom week navigation
remain supported. Only exact-day events enter a week. Weeks with fewer than
three entries receive explicitly labeled nearby dates in both saved HTML and
the enhanced interface.

Every release build refreshes Home and This Week for its Denver date without
editing the authoring catalog. The private release manifest records
`editorialAsOf`; `--as-of YYYY-MM-DD` allows reproduction. Tests also build the
January 2027 boundary, check both saved pages, and verify that catalog state is
restored. Populated calendar/week empty-state nodes contain no misleading copy.

Static hosting must run build/publish daily to keep stored HTML current for
crawlers. Browser refresh alone cannot rewrite a stored page. This checkout
has no confirmed VPS connection, release-store path or remote scheduler.
Production deployment and its daily schedule therefore remain dependent on
those operator details; GitHub publication alone does not deploy 90s.land.

## Verification

- 54 Python tests passed, including precision validation, future build dates,
  sparse saved weeks, content completeness, relationships and release boundaries.
- 9 date/discovery tests passed, including all 522 historical week selections.
- 198/198 Playwright browser tests passed against the final packaged release.
- Static audit: 779 routes, 44,170 internal links and 3,175 fragment links;
  zero errors.
- Publication audit: 777 indexable routes, 51 Article schemas and 245 sharing
  cards; zero errors. Search retains its intentional `noindex,follow` policy.
- HTTP audit: 779/779 routes and 245/245 sharing images passed; all 58 private
  path probes returned 404; 12 identity/gzip samples passed.
- Responsive capture: 56 views at 390 and 1440 pixels, covering all ten years,
  main sections and representative new articles/objects; no horizontal overflow,
  broken images or page errors.
- Migration extraction, catalog/curation checks, asset hashes, generated-file
  checks, media dimensions and the release verifier passed. No separate lint or
  typecheck command is configured for this Python/ES-module project.
- Lighthouse: eight mobile/desktop views across Home, Music, Games and Tech;
  performance 96–100, accessibility/best practices/SEO 100, maximum CLS 0.001705.
  No threshold failures or runtime warnings.

The full browser suite includes navigation and keyboard interaction, calendars,
filters, Search, no-JavaScript pages, accessibility scans, all runtime routes,
Surprise Me, saved Passport and tour state. New coverage opens all 21 new
features and all 32 new objects at both sizes, plus all 120 new album records.

## Review and deployable artifact

The verified package is `dist/release/public/`, served locally at
`http://127.0.0.1:4176/`. Its manifest, transport archive and checksum stay
outside that public directory. Raw Notion/reference captures are ignored under
`content/research/`; authoring catalogs, tests, reports, dependencies and Git
metadata do not enter the public package. The existing 676 legacy section
anchors and live discovery systems remain covered by preservation tests.

Final digest: 016f3c11524d9f1c32947da45d14d1673197eea8dac75bd3d9f8f4929f9ebef1.
See `reports/editorial-expansion/` for compact machine-readable results and
`docs/RELEASE.md` for the confirmed-path deployment/rollback procedure.
