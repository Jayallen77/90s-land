# Phase 1 — Content preservation and migration inventory

Baseline: `a015cd39a15d0f062eac30fe4097a4e97078b651`. This report is generated from frozen source snapshots.

The current presentation remains unchanged. The import is review-only material; it does not claim new historical verification, publish new stories, or feed the public site.

## Preserved material

| Material | Count |
|---|---:|
| Public routes | 26 |
| HTML snapshots including 404 | 27 |
| Existing anchors | 676 |
| Losslessly indexed main-content blocks | 1103 |
| Monthly summaries | 120 |
| Annual chart collections | 10 |
| Annual chart positions | 100 |
| Distinct song/artist-credit combinations | 98 |
| Unique external link candidates | 667 |
| Editorial media files | 34 |
| Existing artifact records | 30 |
| Existing external-resource records | 78 |

Source blocks include page introductions, editorial sections, chart rows, generated catalog mirrors, and supporting-page material. They are not a count of unique articles.

## Year coverage

| Year | Month summaries | Annual chart positions | Newly verified dated events |
|---|---:|---:|---:|
| 1990 | 12 | 10 | 0 |
| 1991 | 12 | 10 | 0 |
| 1992 | 12 | 10 | 0 |
| 1993 | 12 | 10 | 0 |
| 1994 | 12 | 10 | 0 |
| 1995 | 12 | 10 | 0 |
| 1996 | 12 | 10 | 0 |
| 1997 | 12 | 10 | 0 |
| 1998 | 12 | 10 | 0 |
| 1999 | 12 | 10 | 0 |

## Page inventory

Every block has a disposition in `content/migration/inventory.json`, a source range/fingerprint, and an extracted-record destination. The full anchor map is in `content/migration/legacy-links.json`.

| Page | Blocks | Intended use |
|---|---:|---|
| `/` | 14 | Preserve supporting page and existing features |
| `/credits/` | 6 | Preserve supporting page and existing features |
| `/guestbook/` | 2 | Preserve supporting page and existing features |
| `/search/` | 135 | Preserve supporting page and existing features |
| `/sitemap/` | 46 | Preserve supporting page and existing features |
| `/surprise/` | 3 | Preserve supporting page and existing features |
| `/timeline/` | 14 | Preserve supporting page and existing features |
| `/webring/` | 96 | Preserve supporting page and existing features |
| `/timeline/1990/` | 57 | Year context, monthly summaries, annual charts, story candidates |
| `/timeline/1991/` | 60 | Year context, monthly summaries, annual charts, story candidates |
| `/timeline/1992/` | 60 | Year context, monthly summaries, annual charts, story candidates |
| `/timeline/1993/` | 59 | Year context, monthly summaries, annual charts, story candidates |
| `/timeline/1994/` | 55 | Year context, monthly summaries, annual charts, story candidates |
| `/timeline/1995/` | 49 | Year context, monthly summaries, annual charts, story candidates |
| `/timeline/1996/` | 60 | Year context, monthly summaries, annual charts, story candidates |
| `/timeline/1997/` | 48 | Year context, monthly summaries, annual charts, story candidates |
| `/timeline/1998/` | 49 | Year context, monthly summaries, annual charts, story candidates |
| `/timeline/1999/` | 49 | Year context, monthly summaries, annual charts, story candidates |
| `/tours/before-the-feed/` | 21 | Preserve supporting page and existing features |
| `/zones/fashion/` | 26 | Category introductions and story/collection candidates |
| `/zones/games/` | 27 | Category introductions and story/collection candidates |
| `/zones/internet-culture/` | 38 | Category introductions and story/collection candidates |
| `/zones/music/` | 43 | Category introductions and story/collection candidates |
| `/zones/tech-toys/` | 34 | Category introductions and story/collection candidates |
| `/zones/transparent-tech/` | 22 | Category introductions and story/collection candidates |
| `/zones/tv-movies/` | 28 | Category introductions and story/collection candidates |
| `/404.html` | 2 | Preserve supporting page and existing features |

## Review queue

- All 120 monthly summaries and 10 annual charts await fact/source review.
- 25 monthly summaries have no external link inside their source card; their internal navigation is preserved.
- No monthly summary has been converted into an exact-day historical event.
- Song identities preserve original artist-credit strings; collaborations have not been invented as standalone artist entities.
- No imported external URL has been live-checked by this migration.
- 10 media files have no attribution claim in the existing structured artifact catalog. Their page occurrences and original caption/source text remain available in the snapshots and source blocks.
- 4 existing artifact media entries have a non-specific license label:

  - `playstation-hardware` — `See source page`; retain the original source URL for review.
  - `windows-95-start` — `See source page`; retain the original source URL for review.
  - `dreamcast` — `See source page`; retain the original source URL for review.
  - `y2k-office` — `See source page`; retain the original source URL for review.

## Phase boundary

Phase 1 finishes preservation, extraction, schema/relationship validation, and baseline QA. The later editorial launch still requires 30 complete stories and at least 300 sourced dated events, including the agreed 1996 weekly coverage. Imported summaries and chart positions do not count toward those targets.

## Reproduce

```sh
python3 tools/migrate_content.py --check
python3 tools/validate_content.py --baseline-unchanged
python3 tools/report_coverage.py --check
node tools/capture_baseline.mjs --check
```
