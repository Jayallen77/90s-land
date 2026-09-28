# 90s.land

Static nostalgia site with the five-phase editorial rebuild completed locally.
Phase 5 adds smaller media and fonts, mobile polish, release verification, and
a reproducible deployment package. All eight primary sections include 384 sourced dated events,
30 original stories, and working topic, genre, and platform filters. The shared editorial shell, original
reading rooms, museum tools, and old deep links remain available. Hosting paths
from earlier prototype notes are not a verified deployment target.

## Stack and authoring

Python generates dependency-free HTML, CSS, JSON, and browser ES modules.
Generated public HTML is committed; edit its sources and run the renderer.

- `content/pages.json` maps the 23 preserved main fragments in `content/pages/`.
  These balanced fragments are authoritative editable prose, separate from the
  immutable import. Generated regions inside them still come from catalogs.
- `content/routes.json` owns the original route metadata. The renderer appends
  event, story, object, and index routes and writes `data/routes.json`.
- `content/editorial/catalog.json` owns reviewed events, original stories, source
  records, relationships, and the explicit build date for static week fallbacks.
- `content/editorial/modules.json` owns sourced chart snapshots and the curated
  game shelf. `content/editorial/media-review.json` records the media review.
- Existing `data/artifacts.json`, `resources.json`, `tours.json`, `stamps.json`, and
  `navigation.json` remain authoritative for their collections and tools.
- `data/routes.json`, `editorial-index.json`, and `search-index.json` are generated.
- `tools/optimize_assets.py` creates responsive object WebPs and local WOFF2 fonts;
  `data/asset-variants.json` records their integrity hashes. Originals are retained.
- `assets/runtime/week.json` and `surprise.json` are generated, limited browser
  payloads. Authoring catalogs under `data/` and `content/` are never published.
- `tools/render_site.py` generates every public document; `tools/editorial.py`
  supplies the shared shell and Home composition. `archive_content.py`
  validates the dated archive; `archive_pages.py` renders its pages and
  `hub_pages.py` supplies the section hubs and timeline overview.
- `styles.css` supports preserved museum content; `editorial.css` supplies the
  visual system; `archive.css` adds calendars and reading surfaces, and `hub.css`
  supplies the dense section layouts.
- `js/date-utils.js` provides civil-date arithmetic. `js/archive.js` progressively
  enhances the static calendar and weekly page. `js/hubs.js` provides URL-based
  category, topic, game genre, and platform filters.

```sh
python3 tools/render_site.py
```

The renderer does not read generated public HTML or frozen snapshots. The
source-independence test rejects either dependency. Do not edit generated HTML
to change content. Production packaging verifies and copies the committed output.

## Rebuild documentation

- [Phase 1 report and review queue](reports/PHASE_1_MIGRATION.md)
- [Import schemas and preservation contract](docs/CONTENT_MIGRATION.md)
- [Approved decisions and remaining phases](docs/REBUILD_HANDOFF.md)
- [Phase 2 design system](docs/design/PHASE_2.md)
- [Phase 2 verification](reports/PHASE_2_QA.md)
- [Phase 3 authoring and behavior](docs/PHASE_3.md)
- [Phase 3 verification](reports/PHASE_3_QA.md)
- [Phase 4 content and sections](docs/PHASE_4.md)
- [Phase 4 verification](reports/PHASE_4_QA.md)
- [Phase 5 implementation](docs/PHASE_5.md)
- [Phase 5 final verification and performance](reports/PHASE_5_QA.md)
- [Release and rollback runbook](docs/RELEASE.md)

`content/migration/` remains an unreviewed reproducible extraction, not a source
of published events. Frozen snapshots under `reports/baseline/phase-1/` and supplied
JPEG references under `docs/design/references/` remain intact. Promoted fragments
preserve the old prose without certifying old historical claims; day-specific
entries require separate sources and date notes.

## Local preview

```sh
python3 -B tools/build_release.py
python3 -B tools/serve_release.py --port 4174
```

Open `http://127.0.0.1:4174/`. This verifies and serves only the production bundle.
For source authoring only, bind `python3 -m http.server 4173 --bind 127.0.0.1`
to localhost; never expose the checkout as a production document root.

Before review, run:

```sh
python3 tools/render_site.py --check
python3 tools/optimize_assets.py --check
python3 tools/process_media.py --check
python3 tools/audit_site.py
python3 tools/check_editorial.py --check
pnpm content:check
pnpm content:visual-check
pnpm test:content
pnpm test:dates
pnpm test
node tools/capture_phase5.mjs
```

`content:baseline` is the retired Phase 1 unchanged-presentation gate. It is
expected to fail after the visual rebuild; keep the frozen baseline intact.

## Current concept

A nostalgic interactive portal/museum/playground for the 90s and pre-algorithm internet:

- Retro homepage / enter experience
- Fake desktop/window UI
- History of the 90s by year
- Portal zones for music, movies, games, TV, tech, toys, internet culture, fashion, and major events
- Webring/resources section
- Guestbook preview
- Mobile-friendly responsive layout

## Deployment

**The public production output is `dist/release/public/`. Never serve the Git
checkout.** After pulling a reviewed commit, run `python3 -B tools/build_release.py`
(or `pnpm build`). Packaging requires only Python 3.10+; it verifies committed
generated output and creates a repeatable, public-only package. `dist/` is ignored,
so a Git pull alone is not a deployment.

`python3 -B tools/deploy_release.py --site-root /CONFIRMED/RELEASE/STORE` publishes
verified files outside the checkout and atomically switches `current` to the
release's `public/` directory. Caddy must already serve that `current` path.
The helper preserves prior releases and does not change server configuration.

See [the deployment and rollback runbook](docs/RELEASE.md) for exact VPS commands,
required serving behavior, verification, and rollback. Manifests and archives stay
outside the public root. GitHub publication and VPS deployment are separate
operations; perform each only when Justin authorizes it. The deployment scripts
never change Caddy configuration.
