# 90s.land

Static nostalgia site, with a reference-driven editorial rebuild in progress.
The current presentation remains in place while Phase 1 preserves and extracts
the archive. Hosting paths from earlier prototype notes are not a verified
deployment target for this checkout.

## Stack

Simple static site:

- `index.html`
- `styles.css`
- `js/` contains small page-aware ES modules.
- `data/` contains the route, artifact, resource, tour, navigation, and stamp
  catalogs.
- `tools/render_site.py` rewrites only marked generated regions.

Generated HTML is committed. The deployed site remains dependency-free.

## Rebuild preparation

- [Phase 1 report and review queue](reports/PHASE_1_MIGRATION.md)
- [Import schemas, source ownership, and preservation checks](docs/CONTENT_MIGRATION.md)
- [Approved rebuild decisions and remaining phases](docs/REBUILD_HANDOFF.md)

`content/migration/` contains reproducible, unreviewed import records. They do not
feed the current site. Frozen HTML/catalog snapshots and six visual baselines
live under `reports/baseline/phase-1/`; the three supplied designs are development
fixtures under `docs/design/references/`.

## Local preview

```sh
python3 -m http.server 4173
```

Open `http://127.0.0.1:4173/`.

Before review, run:

```sh
python3 tools/render_site.py --check
python3 tools/process_media.py --check
python3 tools/audit_site.py
pnpm content:check
pnpm content:baseline
pnpm content:visual-check
pnpm test:content
pnpm test
```

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

Do not deploy, push, or alter 90s.land production until Justin explicitly
approves a separate production task.
