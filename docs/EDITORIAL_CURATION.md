# Editorial curation

The dated archive lives in `content/editorial/catalog.json`. Phase 2 adds a
small, reviewed layer in `content/editorial/curation.json`; it does not replace
the complete calendar. Edit these sources and regenerate the public pages.

## Year introductions

Each 1990–1999 record contains a caption, introduction, 10–20 defining event
IDs, five story IDs spanning the principal collections, and object IDs. The
publication gate requires at least five event themes and no more than three
film selections per year. A selection must reference an event from that year.

The 1991 and 1992 object shelves preserve existing exhibits whose recorded
dates differ from the year being explored. Their visible `objectNote` explains
the distinction. Other earlier/later objects also require an explicit note;
do not alter an object's dates to make it fit a year.

Events retain their original six collection categories. The `theme` field
allows the editorial audit to distinguish movies from television, technology
from Internet history, and sports or toys from other culture. Fashion remains
an era-wide collection and sourced stories; it has no day-specific event in
this catalog. Add one only when a credible source supports the precise day.

## Connections and search

Year pages show the selected moments before the monthly archive. Calendar
filters apply to the chronological section, leaving the introduction visible.
Collection calendar picks are intentional selections in `tools/hub_pages.py`.
Related panels prefer defining moments and varied themes, with a short list
of stories, objects, and events. Object pages link to search for the complete
set of related dates.

Tour stops may reference a `storyId` and an `eventId` in `data/tours.json`.
These references are validated alongside the existing object and stop IDs.
Search derives its records from the public route, event, story, object, and
resource catalogs. Add useful aliases to object tags (for example `n64`) so
connected events can be found by the same familiar name.

## Regeneration and validation

Run the authoring pipeline, then `tools/check_curation.py` to refresh the
distribution report. `--check` rejects stale reports or invalid selections.
The Phase 1 event identity snapshot is in
`reports/launch-phase2/event-preservation.json`; the check protects original
IDs, URLs, dates, date precision, categories, regions, source references, and
publication status. Edited titles and descriptive copy are allowed.

Run the content, editorial, Python, date, and browser checks before packaging.
`tests/launch-phase2.spec.mjs` covers the new navigation, year selections,
search, object links, Passport focus, responsive layouts, and accessibility.
The broader suite still checks every public route and calendar combination.

`reports/launch-phase2/distribution-before.json` records the Phase 1 baseline
classified with the same thematic labels. `distribution-after.json` includes
all years and all 120 months, both for the complete archive and the curated
moments. These reports describe coverage, not a claim of historical
completeness or equal representation.

The production build remains the public-only package described in
`docs/RELEASE.md`. A Git push does not publish that package to the web server.
