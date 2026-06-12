# 90s.land Next

Experimental rebuild for **90s.land**.

Safety boundary: this project lives at `/home/hermes/projects/90s-land-next` and must not modify or deploy `/home/justin/sites/90s-land` without explicit Justin approval.

## Stack

Simple static site:

- `index.html`
- `styles.css`
- `script.js`

No build step. This keeps iteration fast, cheap, and easy to publish to here.now.

## Local preview

```bash
cd /home/hermes/projects/90s-land-next
python3 -m http.server 4173
```

Open `http://localhost:4173`.

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

Published with here.now from this project directory. Do not deploy to the real 90s.land domain until Justin explicitly approves.
