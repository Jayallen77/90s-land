# Phase 5 final verification

Reviewed September 27, 2026. This report covers the local site and packaged release;
it does not certify an unperformed production deployment.

## Performance

Thirty Lighthouse 13.4.1 runs cover 15 page types in mobile and desktop modes:
Home, Timeline, June 1996, Games, Music, Movies & TV, Tech, Culture, This Week,
story detail, object detail, 1994, Internet Culture, the tour, and search.

- **Mobile Performance: 91–96. Desktop Performance: 99–100.**
- **Accessibility, Best Practices, and SEO: 100 in every sampled run.**
- No runtime errors or Lighthouse run warnings were reported.

| Mobile page | Initial score | Release score | Initial LCP | Release LCP | Initial transfer | Release transfer |
|---|---:|---:|---:|---:|---:|---:|
| Home | 75 | 93 | 4.50 s | 3.08 s | 2.20 MB | 0.49 MB |
| June 1996 | 55 | 93 | 6.90 s | 3.00 s | 3.68 MB | 0.44 MB |
| Games | 70 | 94 | 6.31 s | 2.93 s | 1.69 MB | 0.40 MB |
| Search | 62 | 93 | 7.36 s | 2.85 s | 1.17 MB | 0.31 MB |

Home layout shift fell from 0.168 to 0.001; June 1996 fell from 0.216 to 0.052.
Scores are single-run local lab samples, not medians or measured visitor
experience. The initial baseline used the existing uncompressed Python preview;
the release uses optimized assets **and negotiated gzip**. Improvements must not
be attributed to image conversion alone. Production needs equivalent compression
and a separate HTTPS smoke check. No Safari/device-lab or production-field result
is implied by the Chromium desktop/mobile emulation.

Machine-readable evidence:
[initial](phase-5/performance-before/summary.json),
[intermediate](phase-5/performance-after/summary.json), and
[release](phase-5/performance-final/summary.json). Full Lighthouse diagnostics are
generated locally but ignored by Git; the checked-in summaries retain per-page
metrics, version, measurement time, warnings, and errors.

## Functional and accessibility checks

- 28 Python tests cover source-based generation, content preservation, catalog
  integrity, coverage, release dependency boundaries, checksum tampering, and
  gzip negotiation. Six civil-date tests cover historical week/date behavior.
- 57 browser scenarios cover all 474 routes at 390, 768, 1280, and 1440 pixels,
  museum interactions, search, calendar/week/history/pagination, every hub topic,
  game intersections and reset, no-script reading, and original deep links.
  Phase 5 adds 320-pixel checks across 17 surfaces, keyboard menu/filter/Passport
  use, touch-target and visible-label checks, import-failure recovery, and
  responsive-image/WOFF2 request checks.
- The five Phase 5 scenarios also run against the isolated release package.
- The existing 20 axe checks remain in the browser suite, supplemented by the
  explicit target-size/label rules and the 30 Lighthouse accessibility samples.
  The stricter label check found and prompted a repair to the logo link.
- Static audit: 474 routes, 17,048 internal links, 2,471 fragments, zero errors.
  Renderer, image dimensions, optimized asset hashes, editorial coverage, frozen
  extraction, and preservation validation pass. Phase 1 snapshots stay unchanged.

## Outbound links

The initial scan checked 745 unique URLs using HEAD with a small GET fallback,
12-second timeouts, and at most two concurrent requests per host. Ten 404 URLs
were replaced with reachable equivalents; two Unicode URL checks were repaired
in the checker. The current published set deduplicates to 742 destinations:

- **715 reachable** by the automated checker.
- **20 blocked or rate-limited**; that does not establish a broken destination.
- **Seven unresolved** due to timeout, TLS validation, or an inconclusive response.
- **Zero confirmed missing destinations remain** after the targeted repairs.

The unresolved destinations are the three TEXTFILES services, Macintosh Garden,
Software Heritage, a Paramount press release, and the dELiA's company-history
reference. They remain visible and qualified in the evidence; no content or
useful resource was silently removed to obtain a clean count.

See [initial scan](phase-5/external-links.json),
[replacement checks](phase-5/link-repairs.json), and
[current inventory](phase-5/external-links-final.json). Current results combine
the initial scan and targeted rechecks rather than pretending every URL was
scanned twice. Automated reachability is not a new review of every historical
claim in the inherited reading rooms.

## Visual and release evidence

Twenty-seven screenshots cover nine surfaces at 320 and 390 pixels plus matching
reference-sized desktop canvases. There are no clipped headings, horizontal
overflow, or browser exceptions in the captured surfaces.
[Layout metrics](phase-5/screenshots/layout-metrics.json) and the
[reference comparison](phase-5/reference-comparison.html) are retained.

The release contains 660 runtime files plus compressed companions. Its manifest
records every checksum. HTTP checks return 200 for all 474 routes; missing paths,
Git metadata, authoring catalogs, reports, docs, and original hero PNGs return
404. Five gzip samples decode to their exact manifested content. See
[release HTTP results](phase-5/release-http.json).

The durable local package is built under ignored `dist/phase-5/`. Its public tree,
tar.gz, SHA-256 file, and manifest can be rebuilt from the checked-in sources.
The [release/rollback runbook](../docs/RELEASE.md) requires confirming the actual
host and prior release, verifying transfer, promoting atomically, and retaining
the previous release. Production deployment, DNS changes, and server operations
remain outside this completed implementation phase.
