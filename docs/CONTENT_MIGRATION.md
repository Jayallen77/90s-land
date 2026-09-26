# Phase 1 content contract

Phase 1 preserves and extracts the existing site. It does not change the public
presentation or publish researched stories/events. Read the generated
[migration report](../reports/PHASE_1_MIGRATION.md) for the inventory and review queue.

## Ownership

| Location | Authority and editing rule |
|---|---|
| `reports/baseline/phase-1/manifest.json` | Frozen page/catalog identities, served-file hashes, original anchors, revision, and reference hashes. Never regenerate to make a failing check pass. |
| `reports/baseline/phase-1/pages/*.html.txt` | Exact UTF-8 page snapshots, including 404. The `.html.txt` suffix prevents the current recursive HTML tools from rewriting them. |
| `reports/baseline/phase-1/catalogs/*.json` | Exact copies of all six existing catalogs. Preserve these independently of future additions to live catalogs. |
| `reports/baseline/phase-1/screenshots/` | Six immutable first-viewport screenshots. Desktop uses the supplied reference dimensions; phone uses 390×844. |
| `docs/design/references/` | The three supplied JPEGs, copied without transformation. Development fixtures, not page assets. |
| `content/migration/*.json` | Deterministic, review-only extraction from the frozen snapshots. Do not hand-edit; promote reviewed records into the new authoritative catalogs during the later rebuild. |
| Existing `data/*.json` and public HTML | Continue driving the current site during Phase 1. Their content is unchanged. |

The staging location is deliberate: source preservation must stay reproducible
while future edited stories and verified events evolve independently. No second
runtime data source has been introduced.

## Version 1 import schemas

Every import file is an object with `schemaVersion: 1`, a `kind` matching its
filename, and an array of `records` with unique string IDs. The executable schema
and relationship checks live in `tools/validate_content.py`; they use the Python
standard library.

| Catalog | Main fields and relationships |
|---|---|
| `pages` | Stable page ID, route, title, type, `mainRange`, and ordered `blocks`. Blocks contain heading/level, text, paragraphs, links, images, source IDs, and provenance. |
| `years` | Historical year, original route/page ID, ordered `monthIds`, and `chartIds`. |
| `months` | Stable ID, `year`, `month`, `kind: monthly-context`, `datePrecision: month`, title, paragraphs, links, source IDs, legacy URL, and provenance. No invented day/date field. |
| `charts` | Stable ID, year, `scope: year-end`, region, source IDs, legacy URL, and ordered ranked entries. Each entry references a song entity and preserves its original title, credit, notes, links, and source slice. |
| `entities` | Imported song entities with title, original artist-credit string, source IDs, and chart/rank appearances. Deduplication uses normalized title plus credit; it does not split collaborations into invented artists. |
| `sources` | Stable URL hash ID, exact URL, original labels, roles, and page/line occurrences. `verifiedAt` stays null. |
| `media` | File identity/hash/size, page/alt occurrences, and attribution claims copied from existing artifacts. Rights status is `recorded-unverified` or `needs-review`. |
| `inventory` | One disposition per source block: originating page, kind, current URL, extracted-record destination, planned use, and `preserved-awaiting-curation` status. |
| `legacy-links` | One mapping per original anchor, initially mapping each URL to itself, with page/block ownership. Future redirect/anchor decisions must retain this frozen input. |

All imported content keeps `verificationStatus: unreviewed`; month summaries,
charts, and song entities also keep `publicationStatus: imported-draft`. Existing
artifact status values are preserved in their original catalog, but do not confer
verification on extracted claims or settle image rights.

### Lossless extraction

Main content is partitioned at heading boundaries. Each source character inside
the original `<main>` belongs to exactly one block, including text before the
first heading. A block is an indexing unit, not necessarily a balanced HTML
fragment or a complete article. Never render the raw source slice directly as a
new article.

Every source range stores the snapshot path, Unicode-character start/end offsets
(end exclusive), line range, and SHA-256 of the exact UTF-8-encoded slice.
Validation rejects coverage gaps, overlaps, altered source text, missing
dispositions, and changed snapshots. Complete original page bytes remain available
even when a block contains old layout chrome or generated catalog material.

Monthly summaries are kept as context even if their prose mentions a precise
date. Some describe broad cultural moods or discuss an event from another month.
Dates must be researched before creating event records. Annual chart rank is not
a release date or a weekly chart position.

Source roles are conservative: reference candidate, media reference, discovery
search, or listening search. Link presence is not proof of a fact. No live URL
availability or historical accuracy is claimed by this import.

## Preservation and growth

The shared live-catalog validator checks required types, unique IDs/route paths,
artifact/media relationships, tour stops/stamps, and missing baseline identities.
It is used by both the existing renderer and static audit.

It accepts additions to the artifact/resource catalogs and changes in featured
selection size. It rejects replacing a baseline record with a different ID even
when the total count stays unchanged. Baseline route paths and tour stop IDs are
also protected. The static audit remains responsible for rendered link/fragment
validity.

The former exact ceilings of 30 artifacts, 78 resources, and 12 featured records
are gone. Browser tests derive collection counts from the current catalogs.

## Commands

```sh
# Read-only: check reproducibility, relationships, reports, and visual evidence.
python3 tools/migrate_content.py --check
python3 tools/validate_content.py
python3 tools/report_coverage.py --check
node tools/capture_baseline.mjs --check

# Phase 1 only: all original served files must still match the baseline bytes.
python3 tools/validate_content.py --baseline-unchanged

# Regenerate disposable import/report outputs from the frozen baseline.
python3 tools/migrate_content.py
python3 tools/report_coverage.py

# Test loss/corruption detection, allowed growth, and current browser behavior.
python3 -m unittest discover -s tests -p 'test_*.py'
pnpm test
```

The same workflows are available through `content:check`, `content:baseline`,
`content:visual-check`, `content:extract`, `content:report`, and `test:content`.
The first baseline capture is intentionally one-shot. The capture command rejects
an existing baseline; the screenshot command rejects existing captures.

After presentation work begins, retire the **Phase 1 unchanged-site check** from
that phase's acceptance gate. Keep source-extraction reproducibility, frozen
fixture integrity, catalog preservation, and link validation. Do not change the
baseline hashes to accommodate the redesign.

## Deployment boundary

The baseline, references, tools, reports, tests, and migration staging records are
development material. A later deployment should publish an explicit allowlist of
generated public HTML, required runtime data, scripts, styles, and media. Do not
copy the entire repository to the public document root. This phase makes no
deployment, hosting, DNS, or external-account changes.
