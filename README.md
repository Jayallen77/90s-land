# 90s.land

Static nostalgia site, with a reference-driven editorial rebuild in progress.
Phase 2 replaces Home, the 1996 Timeline, and Games with the approved editorial
visual system. The shared header/footer span the site; original reading rooms,
objects, tools, and deep links remain available. Hosting paths from earlier
prototype notes are not a verified deployment target for this checkout.

## Stack

Simple static site:

- `index.html`
- `styles.css`
- `editorial.css` contains the shared design tokens, components, and responsive layouts.
- `js/` contains small page-aware ES modules.
- `data/` contains the route, artifact, resource, tour, navigation, and stamp
  catalogs.
- `tools/editorial.py` generates the three new compositions and shared shell.
- `tools/render_site.py` assembles these pages and maintains generated regions in
  the remaining legacy pages.

Generated HTML is committed. The deployed site remains dependency-free.

## Rebuild preparation

- [Phase 1 report and review queue](reports/PHASE_1_MIGRATION.md)
- [Import schemas, source ownership, and preservation checks](docs/CONTENT_MIGRATION.md)
- [Approved rebuild decisions and remaining phases](docs/REBUILD_HANDOFF.md)
- [Phase 2 design system and scope](docs/design/PHASE_2.md)
- [Phase 2 verification and visual review](reports/PHASE_2_QA.md)

`content/migration/` contains reproducible, unreviewed import records. They do not
feed the current site. Frozen HTML/catalog snapshots and six visual baselines
live under `reports/baseline/phase-1/`; the three supplied designs are development
fixtures under `docs/design/references/`.
The three new pages include balanced copies of their original main content from
those frozen snapshots inside expandable reading rooms. New editorial highlights
live separately in `content/editorial/`; complete content promotion is Phase 3.

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
pnpm content:visual-check
pnpm test:content
pnpm test
node tools/capture_phase2.mjs
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

Do not deploy, push, or alter 90s.land production until Justin explicitly
approves a separate production task.
