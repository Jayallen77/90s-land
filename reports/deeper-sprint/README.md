# Deeper stories and finished exhibits

Approved sprint completed against the 2026-11-05 collection. The visual identity and static architecture are preserved. The reviewable release contains all 35 published stories, 62 object files, 295 timeline records and 101 defining moments.

## Reading and editorial work

All 35 stories received individual edits. The 12 anchor rewrites cover cheat commands, demo editions, memory-card allocation, sampling, breakbeats, R&B, TRL, mixtape running times, FUBU, responsive toys, scheduled television and browser versions. The remaining 23 received substantive subject-specific changes. Formats now include listening guides, comparisons, dated schedules, worked examples and annotated artifacts. There is no minimum word-count gate.

Examples of the new material:

- Classic PC Doom commands include actual effects and the Doom/Doom II no-clipping distinction, with single-player and skill-level conditions.
- The memory-card feature explains a 15-block allocation using the identified Gran Turismo manual and Final Fantasy VII save requirements. It links directly to the memory-card object file.
- Demo-disc material identifies two editions by catalog number and separates playable material from promotional video.
- Sampling connects named source recordings to named later recordings. The photographed MPC2000 is identified as a 1997 instrument, rather than implied to have made earlier records.
- The TRL countdown identifies the September 14, 1998 recap and explicitly explains its fan-archive provenance. It is not represented as MTV's official voting ledger.
- The illustrative six-track mix totals 28:16. Its reference versions and modern remaster/mix labels are disclosed; it is not presented as a surviving period tape.
- SNICK uses an identified US Eastern-feed launch-night schedule, with regional limitations stated.
- Browser comparisons distinguish Navigator 3, Internet Explorer 3 for Windows 95 and the later Windows 3.1 release.

All 62 object descriptions were reviewed and revised. The 18 priority files received deeper model, operation and limitation material. Simple items remain concise. Existing identifiers, Passport keys and tour stop IDs are unchanged.

The catalog adds 38 source records. Source scope and uncertainty remain visible where relevant. Original editorial descriptions and teaching diagrams are distinguished from historical records, photographs and interface recreations.

## Exhibits and discovery

All six existing interface exhibits are now complete: a decoratable invented homepage, simulated six-digit counter, example guestbook with local preview, three-member invented webring, editable AIM-style away-message preview, and browsable directory. Full versions live on object pages; compact versions appear on cards. The tour and collection reuse the same exhibit components. Controls work with keyboard and touch. Script-dependent buttons stay disabled until their handlers are attached. A delayed-module regression checks the fast-tap initialization race exposed by the first GitHub run. Stamp-only buttons say “Collect stamp.” Guestbook and away-message previews do not submit or persist messages.

Search normalizes R&B/rnb/rhythm and blues, N64/Nintendo 64, PS1/PSX/PlayStation, SNES/Super Nintendo, hip-hop and CD-R. Matching uses meaningful tokens and subject weighting. The reviewed R&B query returns 18 relevant results with the R&B feature first, rather than 476 letter-fragment matches.

All 97 story/object pages have curated onward links with brief reasons: 212 relationships in total. There is no irrelevant-link quota. Homepage selections and all eight collections have deliberate, distinct slots. The issue theme is “The little things did the work.”

This Week retains date and year controls. Sparse weeks show explicitly labeled year-level reading, collapse empty days behind an optional control, and identify nearby events as outside the selected week. No dates were assigned to fallback stories or objects. Empty related-story panels are omitted.

## Visuals and attribution

Twelve weak or mismatched story leads were replaced with distinct original explanatory diagrams, including all ten priority leads plus cheats and responsive toys. Existing suitable product photographs and collection heroes remain. All 35 stories have distinct original lead-image identities; renamed files or alternate crops do not count as unique.

Thirteen original SVG/PNG diagrams were created overall: twelve leads and a supporting memory-card allocation figure. Two credited artifact photographs provide supporting context. The figure registry contains 15 records. Captions, subjects, alt text, creator, source, terms and image hashes are recorded. Share cards distinguish explanatory diagrams from photographs. Diagrams are labeled as original interpretation; no generated image is presented as an authentic period photograph. No paid assets were purchased.

## Validation

| Check | Result |
| --- | --- |
| Entire active collection, 390 px and 1440 px | 128 pages / 256 renders; zero recorded issues |
| Accessibility scan across those renders | Zero Axe violations |
| Original URL reconciliation | 779 checked: 128 retained, 311 compatibility, 340 retired; zero unexpected statuses |
| Packaged route HTTP audit | 439/439 passed |
| Sharing-preview HTTP audit | 128/128 passed |
| Static internal-link audit | 23,351 links and 2,994 fragments; zero errors |
| Full browser suite | 159 passed |
| Final search, exhibit and sparse-week regression | 5 passed, including delayed-module initialization |
| Python content/renderer/release tests | 67 passed |
| Node date/discovery/search tests | 12 passed |
| Authoring, content, curation, preservation, media and metadata checks | Passed |
| Production release build and package integrity | Passed; delivery uses a clean committed snapshot |

The complete page review scrolls every page to load images, checks HTTP responses, image decoding, horizontal overflow, script errors, heading structure, unrendered figure markers and accessibility, then saves full-page screenshots. Screenshot contact sheets were visually reviewed in addition to interactive desktop/mobile spot checks. All six exhibits also have keyboard/touch behavior tests. Existing search history, filters, date navigation, no-JavaScript content, Passport persistence/reset, Surprise Me and tour progress are covered by the browser suite.

The 779-URL and collection-wide audits preserve the existing retirement/compatibility decisions. Compatibility pages remain excluded from discovery and the XML sitemap. Fingerprints also verify that timeline records, defining moments and publication decisions did not change.

### Evidence files

- `approved-ledger.csv`: all 128 approved page briefs.
- `editorial-review.json`: story structure/length review and added source inventory.
- `media-review.json`: lead replacements, original identities, captions and rationale.
- `preservation.json`: baseline fingerprints and original artifact/tour identifiers.
- `page-qa.json`: every desktop/mobile page result and screenshot filename.
- `original-url-qa.csv` and `original-url-qa.json`: every original URL and expected result.
- `http-qa.json`: packaged HTTP, sharing cards, private-file exclusion and encoding checks.
- `preview-desktop.png`: finished homepage preview.

Full-page screenshots and contact sheets from this run are in `/private/tmp/90s-land-sprint-qa-20261105/`. They are local QA artifacts, not public runtime files. Historical launch screenshots in the repository were preserved rather than overwritten by this sprint's test captures.

## Review and delivery

The complete local production preview is available at http://127.0.0.1:4175/ while the preview process is running. Useful entry points are `/stories/the-secret-button-sequence/`, `/stories/fifteen-blocks-of-memory/`, `/archive/objects/geocities-homepage/`, `/search/?q=R%26B` and `/this-week/?date=1996-11-05`.

This sprint was finished in the isolated checkout `/private/tmp/90s-land-sprint-20261105` after the original Desktop checkout became unavailable. Original local-only files were not copied, replaced or discarded. GitHub `main` is the delivery source. Hermes remains responsible for production deployment; this work makes no SSH, VPS or Caddy changes.

To reproduce the source and release checks:

```sh
pnpm install --frozen-lockfile
pnpm author:check
pnpm editorial:check
pnpm content:check
pnpm test:content
pnpm test:dates
pnpm run audit
pnpm launch:audit
pnpm build:production
pnpm build:check
python3 -B tools/serve_release.py --port 4175
# In another shell:
pnpm release:audit --base-url http://127.0.0.1:4175
PLAYWRIGHT_BASE_URL=http://127.0.0.1:4175 LAUNCH_QA_DIR=dist/ci/screenshots pnpm test
```

`build:production` requires a clean committed checkout. Review reports, raw authoring catalogs and tools are excluded from the public release. The GitHub workflow repeats content checks, clean builds, HTTP audits and the browser suite in four shards before the Hermes handoff.
