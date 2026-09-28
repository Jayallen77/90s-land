# Phase 5: refinement, performance, and release preparation

Implemented September 27, 2026. The five-phase rebuild is ready for a separately
authorized production handoff. The site retains its 474 routes, 384 sourced dates,
30 complete stories, original reading rooms, and local museum tools.

## Final refinements

- Font delivery now uses local WOFF2 variants of the five editorial fonts,
  retaining their glyphs, original TTFs, and OFL licenses. Preloads match the
  files actually used; obsolete TTF preloads no longer consume bandwidth.
- All 24 catalog photos/screenshots have responsive WebP variants with useful
  card sizes. Static pages and the live historical-week image share those
  variants. Original images, source credits, and media review records remain.
- The enhancement class is applied before first paint. Mobile navigation no
  longer flashes its expanded no-script layout and then moves the whole page.
  Calendar months wait for the selected month rather than briefly displaying
  the entire year. If an enhancement import fails, the readable static archive
  and navigation are restored.
- Phone controls and game source/story links have more comfortable hit areas.
  The mobile timeline story module becomes a readable list instead of three
  cramped columns. The brand link derives its accessible name from its visible
  wording and a hidden home label, avoiding an overriding label mismatch.
- Ten dead inherited source URLs were repaired without changing the preserved
  prose. Unicode URLs are correctly encoded by the link checker. Bot blocks,
  timeouts, and TLS failures remain qualified in the outbound-link report.

No content counts were padded, date claims changed, public routes removed,
framework added, storage keys changed, or production configuration altered.

## Visual review

Home, June 1996, and Games were captured at the supplied reference sizes. The
navy surfaces, collage heroes, pixel headings, narrow panel gaps, category colors,
and dense desktop module grids remain. Home preserves the roughly 49/24/27
middle row; the Games lead row stays close to the approved four-column balance.
The timeline uses a main archive column and a narrow sidebar.

The references remain visual direction rather than historical source material.
Original collages, real titles/dates, source qualifiers, filter controls, and
reading-room links account for intentional content and height differences.
The implementation does not claim to be a literal screenshot reproduction.

Nine surfaces were reviewed at 320 and 390 pixels, with desktop captures at the
reference dimensions. The archive keeps its imagery, readable cards, and working
controls at narrow widths. See the
[side-by-side comparison](../reports/phase-5/reference-comparison.html) and
[final screenshots](../reports/phase-5/screenshots/).

## Performance and serving

The initial mobile baseline exposed large original images, uncompressed font
downloads, and visible layout shifts. The optimized release adds those asset
fixes, stable startup, and deterministic gzip variants for text. The final
Lighthouse sample covers 15 page types in mobile and desktop modes.

These are local lab measurements with compression enabled, not production field
data. See [the QA report](../reports/PHASE_5_QA.md) for scores, transfer sizes,
methodology, and limits. The actual host must negotiate gzip or equivalent
compression; merely copying `.gz` files without serving them is insufficient.

## Reproducible package and rollback

`tools/build_release.py` follows runtime dependencies from the public route
inventory and writes a new release directory. It includes the public tree,
deterministic tar.gz, companion checksum, and per-file SHA-256 manifest. It
rejects missing dependencies, private-source dependencies, changed checksums,
and accidental overwriting of an existing release. The package contains 660
runtime files before generated gzip companions.

`tools/serve_release.py` previews only that public tree on localhost, with gzip
negotiation and real 404 responses. `tools/check_release_http.py` verifies every
route, representative compressed responses, checksums, and exclusion of source
files. `tests/test_release.py` covers tamper rejection and package boundaries;
`tests/release.spec.mjs` covers narrow layouts, keyboard use, touch targets,
enhancement failure, and optimized requests.

The [release runbook](RELEASE.md) describes transfer verification, required host
behavior, atomic promotion, smoke checks, and restoring the previous release.
It deliberately does not assume a VPS path or hosting account. Rollback requires
no database migration and preserves browser-local Passport/tour state.
