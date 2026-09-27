# Phase 3: connected archive and complete static generation

Implemented September 27, 2026. This phase connects the visual system to dated
content and reproducible source files. The broader editorial expansion remains
Phase 4; production publication is separate.

## Source ownership

| Source | Purpose |
|---|---|
| `content/pages.json` and `content/pages/*.html.inc` | 23 balanced, editable preserved main fragments with original snapshot provenance. |
| `content/routes.json` | Metadata for the original 26 catalog routes. |
| `content/editorial/catalog.json` | 20 reviewed day-specific events, two original stories, 17 source records, explicit relationships, and static fallback build date. |
| Existing artifact/resource/tour/stamp/navigation catalogs | Collection identity, media credits, museum tools, and shared navigation. |
| Python component modules | Complete shell, archive compositions, detail pages, utility pages, metadata, sitemap, and shared UI. |

Run `python3 tools/render_site.py` after source edits. Public HTML and
`data/routes.json`, `data/editorial-index.json`, and `data/search-index.json` are
outputs. No renderer reads a public HTML file or frozen snapshot. A unit test
rejects those reads while generating every page.

Preserved prose is still existing editorial material, not newly verified events.
The immutable migration catalogs and baseline are unchanged. Old monthly summaries
remain behind their original anchors in the year reading rooms. Their former
Grid/List/Calendar controls have been retired: those controls rearranged summaries,
not real calendar days. No authored prose or legacy anchor was removed.

## Browsing behavior

All ten years have true Monday-first calendars for every month, including February
29, 1996. Grid, list, calendar, category, region, month, and page selections are
encoded in URLs. Back, forward, reload, cross-year month navigation, and empty
filters remain usable. Card views paginate at 12 records; calendars retain all
matching dates. On mobile, compact calendar links accompany a readable agenda.

Without JavaScript, every monthly section, event, story, object, source link, and
reading room remains accessible. Interactive filters are hidden. The weekly page
shows an explicitly dated build-time fallback and links to the complete timeline.
If the weekly catalog fetch fails, that fallback remains visible with an explanation.

“This Week” uses the current **America/New_York** civil date on page load, subtracts
30 from the year, clamps a leap-day mapping to the last valid February day, then
finds the historical Monday–Sunday week containing that date. Date arithmetic uses
UTC civil days, avoiding daylight-saving shifts. Dates outside the archive clamp
to January 1, 1990 or December 31, 1999. A final week can naturally include the first
two days of 2000, but no out-of-decade event is published or selectable.

The homepage uses the same calculation and event catalog, choosing entertainment
or technology for its weekly feature. The full timeline and weekly archive may
include world news. Empty weeks offer separately labeled nearby dates; they never
present those dates as events inside the selected week.

## Detail records and discovery

- `/events/{slug}/`: exact regional date, context, date qualification, source
  citations, containing month/week, and related stories/objects.
- `/stories/{slug}/`: complete original prose, cited historical claims, related
  events/objects, canonical metadata, and Article structured data.
- `/archive/objects/{slug}/`: existing curator notes, media attribution/license
  labels, related records, original exhibit links, and Inspect + stamp.
- `/stories/` and `/archive/objects/`: browsable indexes.
- `/this-week/`: weekly lead, day-grouped events, date/year navigation, nearby
  recovery paths, and story discovery.

Search has one result per event, story, or object (no duplicate detail-route
results). It searches date, region, category, and body terms, accepts multiple
query words, and normalizes accents. Existing routes, resources, and tools remain
searchable. Counts are derived from records. The HTML and XML site maps include
the new destinations. The site has 81 catalog routes plus its 404 page.

## Remaining editorial work

The starter catalog exercises every year and the new relationships. It does not
meet the launch targets of 300 events, every month represented, three events per
1996 week, and 30 stories. Blank dates are explicitly labeled as archive gaps.
Existing broad/vague media license labels have not been upgraded into new rights
claims; the full source/media review remains Phase 4. The 30 object detail pages
reuse existing collection records and are not counted as 30 new stories.

The remaining Music, Movies & TV, Tech, and Culture compositions and substantive
genre/platform destinations belong to Phase 4. Phase 5 retains the full performance,
release, and final visual review gates. No production deployment occurred.
