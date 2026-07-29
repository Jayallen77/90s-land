# 90s.land Next

Experimental rebuild for **90s.land**.

Safety boundary: this project lives at `/home/hermes/projects/90s-land-next` and must not modify or deploy `/home/justin/sites/90s-land` without explicit Justin approval.

## Stack

Simple static site:

- `index.html`
- `styles.css`
- `js/` contains small page-aware ES modules.
- `data/` contains the route, artifact, resource, tour, navigation, and stamp
  catalogs.
- `tools/render_site.py` rewrites only marked generated regions.

Generated HTML is committed. The deployed site remains dependency-free.

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
