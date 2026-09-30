# Unified public site

This is the current presentation and authoring contract. Earlier phase documents
and frozen migration snapshots describe historical work; they do not require
retaining old public layouts or copying their prose beneath a redesigned page.

## Composition

`tools/render_site.py` assembles each complete document once, including the
shared header, footer, discovery navigation, and dialogs from `editorial.py`.
`archive_pages.py` renders calendars, This Week, stories, events, and objects;
`hub_pages.py` renders the five primary collection hubs and timeline overview;
`product_pages.py` renders the specialist collections and utility pages.

The old `content/pages/` fragments, `content/pages.json`, `preserved_content()`,
and `apply_shell()` rendering paths are removed. No public composition may
include `.ed-preserved`, `.ed-reading-room`, fake page windows, or title bars.
Intentional interface recreations are contained within labeled exhibits, such
as the homepage builder and individual GeoCities, guestbook, and AIM objects.

## Design

Keep the navy surfaces, palm/sunset branding, existing cinematic hero artwork,
Jersey display type, Barlow body type, condensed labels, and pink/cyan/purple/
yellow accents. `styles.css` owns foundations, buttons, utility cards, dialogs,
object sections, and intentional exhibits. `editorial.css` owns the brand,
header, homepage, and shared editorial layouts. `archive.css` owns reading and
calendar surfaces; `hub.css` owns collection grids and responsive hub layouts.
The three retired runtime font files and unused timeline script are removed.
Legacy TTF sources remain solely for the existing social-card authoring tool;
they are not website runtime dependencies.

## Navigation and state

The primary navigation is Home, Timeline, Music, Movies & TV, Games, Tech,
Culture, and This Week. Fashion and Internet Culture belong under Culture;
Transparent Tech belongs under Tech. The existing URLs are retained.

Hub story links retain their category in `/stories/?category=...`. Dated-event
links open `/events/?category=...`, a collection of the existing catalog rather
than a keyword search. Search, resource, and event collections use the shared
paginator. Their filters, queries, and result page survive reload and browser
history. Timeline category/region/month/display state and game genre/platform
state retain their existing URL contracts.

`content/deep-links.json` contains compatibility IDs attached to corresponding
live sections. Every baseline anchor remains available; original artifact
anchors attach to modern object cards, and `#month-jan` through `#month-dec`
select the corresponding timeline month. Other retired section bookmarks lead
to their nearest live content section. No old page body is loaded or published.
Object details and tour cards link to canonical object pages or live collections.

Guestbook links say "Guestbook preview". Entries are temporary browser previews:
nothing is sent, stored, published, or shared. Passport and tour progress retain
their existing local storage behavior and keyboard-accessible dialogs.

## Media and content

Keep the existing sourced library and attribution. The Blockbuster photograph
is labeled as a store interior. Tamagotchi entries use a graphic treatment
because the catalog has no suitable photograph. Individual game cards use title
and genre graphics rather than hardware photographs implying game screenshots.
Atmospheric collage artwork belongs in collection heroes; story cards without
relevant documentary imagery use graphics. Small images retain their natural
proportions on reading pages rather than being stretched into large heroes.

This phase does not expand the historical library: the 384 events, 30 stories,
and 30 objects remain. The new Events index only provides a direct home for
existing records. Repetitive promotion strips and development-oriented route
metadata are removed.

## Verification and publishing

Regenerate from sources; never permanently patch generated HTML by hand:

```sh
python3 tools/optimize_assets.py --check
python3 tools/render_site.py
python3 tools/render_site.py --check
python3 tools/process_media.py --check
python3 -m unittest discover -s tests -p 'test_*.py'
node --test tests/date-utils.test.mjs
pnpm test
python3 tools/audit_site.py
python3 -B tools/build_release.py
python3 -B tools/build_release.py --check
```

`tests/test_editorial.py` verifies baseline anchors and rejects complete legacy
compositions across every generated public HTML document. Browser checks cover
filters, history, pagination, keyboard navigation, static fallbacks, and
accessibility. Responsive route sweeps are divided into bounded batches to avoid
one long timeout covering the entire site. `tools/capture_redesign.mjs` captures
all major families at 390, 768, 1280, and 1440 pixels under ignored `dist/redesign/`.

The production root remains `dist/release/public/`. Build metadata, catalogs,
source, tests, reports, tooling, and Git data remain outside that directory. See
`docs/RELEASE.md` for packaging, publishing, and rollback. This redesign does not
change VPS or Caddy configuration.
