# Phase 4: complete sections and editorial archive

Implemented September 27, 2026. The eight primary sections now lead into a
connected, statically generated archive. Production deployment remains a
separate task; Phase 5 retains performance measurement and release preparation.

## Content delivered

- **384 sourced events**, each with a full civil date, region, date qualification,
  review date, and source references. All 120 months of 1990–1999 are represented.
- **At least three events in each of the 53 Monday–Sunday weeks beginning in
  1996**, including December 30, 1996–January 5, 1997. Boundary-week entries are
  actual bowl games on their published dates, not copied monthly summaries.
- **30 original stories, six per section category.** Every story has four
  sections, complete prose, source notes, and related objects or events. The
  launch slate covers all 30 subjects in the approved handoff.
- **67 shared source records**, plus per-entry publisher/museum references in the
  game shelf and separately documented chart sources.
- **12 curated games** with six genre choices and four platform choices. These
  are editorial selections, not a claim about sales or current popularity.
- **474 catalog routes**, plus the 404 page, from a single reproducible renderer.

Events are intentionally strongest in North American theatrical releases:
345 Movies & TV, 12 Tech, eight Music, seven Games, 11 Culture, and one News.
This is coverage of selected dates, not a complete day-by-day history or an
evenly balanced event encyclopedia. The public coverage note makes this clear.
Thirty objects, inherited monthly prose, annual chart rows, and original
interface recreations are not counted as new stories or events.

## Section design and interactions

Home, Timeline, Music, Movies & TV, Games, Tech, Culture, and This Week use the
shared navy/pink/cyan editorial system. New original hero collages cover Music,
Movies & TV, Tech, and Culture. The five section hubs combine a feature, sourced
chart or story list, object tiles, facts, six deep dives, and relevant collections.
The timeline overview offers ten year doors with counts from the live catalog.

Games combines genre and platform filters, including intersection empty states
and a reset path. Other hubs offer topic filters with real story destinations.
The story library filters all 30 stories by category. Selection survives reload,
back, and forward; invalid values recover to the full collection. All articles,
game entries, and links remain available without JavaScript.

Music includes the 1996 Billboard year-end Hot 100 top five, explicitly labeled
as a US annual chart transcribed via Wikipedia. Movies & TV shows The Numbers'
top five for **earnings during calendar 1996 in the US/Canada**, in nominal
dollars, not lifetime grosses. Neither module masquerades as a weekly chart.
Music scene and home-viewing modules link to original essays. Tech and Culture
connect the older Fashion, Internet Culture, and Transparent Tech collections.

Original reading-room prose and anchors remain available at their old routes.
The new Culture navigation target is `/zones/culture/`; the previous Internet
Culture URL is still intact. Passport, Surprise Me, the guided tour, search,
resource directory, and guestbook preview remain functional.

## Source and date policy

Movie entries use reviewed annual release calendars and, where needed,
individual film pages from The Numbers. Dates are labeled **North America
(US/Canada)**. A calendar date is not promoted into a claim about a world
premiere or nationwide wide release: limited openings, previews, and later
expansions may differ. Each entry carries that qualification.

Other entries use relevant primary records: Nintendo and Sony histories,
official Nirvana and Metallica discographies, NASA mission and Hubble releases,
original Hotmail announcement archives, and official bowl/university histories.
Story references also include CERN, the Computer History Museum, Smithsonian,
The Strong, the V&A, and The Henry Ford. Essays distinguish historical anchors
from original interpretation. A year-only source never supplies an invented day.

The independent gate `python3 tools/check_editorial.py --check` validates month
and week coverage, story completeness, record identities, review/source fields,
media coverage, and game destinations. Source URLs still need human review when
claims change; passing a schema check is not a substitute for that review.

## Media provenance

`content/editorial/media-review.json` records **37 reviewed media items**:
24 existing photographs/screenshots, six original interface recreations, and
seven original AI hero illustrations. Commons file records were reviewed for
creator and license metadata. Resizing and CSS cropping are disclosed; direct
license links appear on credits and object detail pages.

The review corrected the Dreamcast file identity and its CC BY-SA 3.0 license,
and the Y2K office file identity, government attribution, and terms. The existing
Y2K photograph depicts Japan's December 31, 1999 response office. Frozen imports
remain untouched; published catalogs carry the reviewed information.

Collages are labeled original AI illustrations, not documentary evidence.
Artifact photos illustrate listening, viewing, and playing hardware; the game
shelf explicitly distinguishes platform imagery from game screenshots. No paid
assets, new trackers, backend, or framework were introduced.

## Authoring and follow-up

Edit `content/editorial/catalog.json` for events/stories/sources and
`content/editorial/modules.json` for the chart/game modules. New section
compositions live in `tools/hub_pages.py`, their styles in `hub.css`, and filter
behavior in `js/hubs.js`. After changes run:

```sh
python3 tools/render_site.py
python3 tools/check_editorial.py
python3 tools/render_site.py --check
python3 tools/check_editorial.py --check
python3 tools/audit_site.py
pnpm test:content
pnpm test:dates
pnpm test
node tools/capture_phase4.mjs
```

The coverage report and 16 desktop/mobile captures live in `reports/phase-4/`.
See [Phase 4 verification](../reports/PHASE_4_QA.md) for results. Phase 5 remains
open for further mobile refinement, measured performance, and a release/rollback
plan. This phase does not activate a production deployment.
