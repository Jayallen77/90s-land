# Phase 2 verification

Validated locally on September 26, 2026, before GitHub publication. Production
deployment remains a separate task.

## Results

- **16 Python acceptance tests pass.** This includes all Phase 1 preservation,
  corruption/loss detection and growth tests, plus independent checks that every
  baseline anchor survives and the three new reading rooms retain all original
  main-page text. Each replacement page has exactly one H1.
- **28 Playwright tests pass.** All 26 routes fit 390, 768, 1280 and 1440px viewports;
  the mobile menu, Passport persistence/reset/storage fallback, Surprise Me,
  guided tour, search, guestbook preview, no-script access and old month controls
  remain functional. New tests cover highlight grid/list modes, automatic reading
  room opening from old deep links, loaded hero/fonts, and no-script reading rooms.
- **Axe reports no violations** on Home, Timeline index, 1994, the new 1996 page,
  Games, Internet Culture, Tour, and Search.
- Frozen migration extraction: **9 catalogs, zero drift**. Catalog/relationship
  validation and the Phase 1 coverage report remain current.
- Generated HTML and media checks are current. The static link audit reports
  **zero errors**; external historical claims are not inferred from this check.

## Visual inspection

Six screenshots were inspected at the exact three reference canvas sizes and at
390×844. Open [the comparison sheet](phase-2/comparison.html), or inspect
`reports/phase-2/screenshots/`. `tools/capture_phase2.mjs` waits for fonts and all
visible images before saving the captures; metrics are saved alongside them.

The Home hero ends at y=354, matching the supplied composition’s main transition.
Timeline retains the shallow year banner and full-width month rail. Games retains
the shallow collage, nine-topic rail, four distinct upper panels, and compact
lower rows. Mobile reorganizes these into readable lists/grids with no page-wide
horizontal scroll. The resulting copy, object photography, and original hero
artwork intentionally differ from the reference’s illustrative content.

Original anchors are preserved inside accessible disclosure sections. Direct
hash navigation opens them. The native summaries remain usable without JavaScript.
This is a migration bridge until full content generation replaces the old markup.

## Scope limits

The new weekly panel is a fixed September 23–29, 1996 selection; the new Timeline
grid is a June composition containing three sourced releases. Month links reach
the original monthly context. Full date/region filtering, day calendars, historical
week navigation, the complete story/event catalog, and the remaining category
compositions are not claimed complete. See [the detailed design handoff](../docs/design/PHASE_2.md).

No new Lighthouse score is claimed in this phase. Hero images have intrinsic
dimensions, responsive WebP sources, and high-priority loading; supporting images
are lazy loaded. Final performance profiling is still a Phase 5 task.

## Commands

```sh
python3 tools/render_site.py --check
python3 tools/process_media.py --check
python3 tools/audit_site.py
python3 tools/migrate_content.py --check
python3 tools/validate_content.py
python3 tools/report_coverage.py --check
python3 -m unittest discover -s tests -p 'test_*.py'
pnpm test
node tools/capture_phase2.mjs
```

The Phase 1 `--baseline-unchanged` flag is intentionally retired as an acceptance
gate now that presentation changes are authorized. Baseline files and hashes were
not changed to accommodate the redesign.
