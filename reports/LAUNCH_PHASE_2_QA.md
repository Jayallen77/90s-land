# 90s.land — launch Phase 2

Phase 2: editorial quality, content balance, and information architecture.
Reviewed September 30, 2026. Baseline: `38e931898fcfe120bad74699904fbf848dfe5933`.

## Content architecture

All ten year pages now open with a distinct caption and short introduction,
followed by 10–11 defining moments. The full monthly archive remains below,
with its filters, pagination, regional labels, real calendar dates, and legacy
month bookmarks. Each year has five stories spanning Music, Movies & TV,
Games, Tech, and Culture; four object exhibits; collection links; and the
existing decade and experience navigation. The approved 1996 hero, object
photography, fonts, colors, and shared components remain in use.

`content/editorial/curation.json` is the authoritative introduction layer.
Publication checks require 10–20 distinct moments from the correct year, at
least five themes, no more than three films, valid stories and objects, and
visible context for objects whose recorded dates differ from the year.
The 1991 six-button Genesis controller and 1992 Windows 3.0 display retain
their exhibits and source dates, with clear earlier/later object notes.

The homepage places the 1990–1999 selector immediately after the hero. It
also exposes collections, a search form, the original six featured stories,
four selected objects, and three experience cards for Tour, Surprise Me, and
Passport. The object shelf uses four columns on wide screens and two on
mobile to keep the page compact. This Week remains a prominent existing
feature. The homepage Passport button restores focus when the dialog closes.

## Balance and coverage

58 individually researched dated events were added. Every original event
remains: the preservation check protects all 384 IDs, slugs, dates, precision,
categories, regions, source IDs, and publication statuses. All 345 film entries
are retained. There are now 442 events and 533 public routes.

| Theme | Before: complete archive | After: complete archive | Defining moments |
| --- | ---: | ---: | ---: |
| Music | 8 | 18 | 13 |
| Movies | 345 | 345 | 20 |
| Television | 0 | 11 | 11 |
| Games | 7 | 17 | 17 |
| Technology | 10 | 19 | 15 |
| Internet | 2 | 6 | 6 |
| Culture | 3 | 4 | 3 |
| Fashion | 0 | 0 | 0 |
| Major news | 1 | 6 | 6 |
| Sports | 7 | 15 | 9 |
| Toys / products | 1 | 1 | 1 |
| **Total** | **384** | **442** | **101** |

Films constituted 89.8% of the original dated archive and remain 78.1% of the
complete archive. They account for 19.8% of the defining moments, exactly two
in each year. The change addresses what visitors encounter first while
preserving the deeper film-release collection. It does not claim equal
historical coverage across categories or regions.

Fashion is represented through the sourced lookbook and the stories
“Clothes with a soundtrack” and “The catalog on your bedroom floor.” No exact
day was invented for an era-wide style. The existing Tamagotchi entry is the
day-specific toy milestone.

| Year | Before: all events | After: all events | Defining moments |
| --- | ---: | ---: | ---: |
| 1990 | 24 | 31 | 10 |
| 1991 | 26 | 32 | 10 |
| 1992 | 27 | 33 | 10 |
| 1993 | 27 | 33 | 10 |
| 1994 | 23 | 29 | 10 |
| 1995 | 26 | 32 | 10 |
| 1996 | 157 | 159 | 11 |
| 1997 | 22 | 27 | 10 |
| 1998 | 26 | 33 | 10 |
| 1999 | 26 | 33 | 10 |

All 120 months retain dated entries. The original 1996 concentration remains
visible in the complete archive: May, August, and November each contain 15
entries. May and August are entirely film releases. Curation, rather than
removing those records or filling every month with generic material, provides
the broader introduction.

The [before distribution](launch-phase2/distribution-before.json) and
[after distribution](launch-phase2/distribution-after.json) contain category
and theme counts for every year and every month. Both use the same Phase 2
theme classification. The six existing collection categories remain stable;
separate thematic labels distinguish film/television, technology/Internet,
and culture/sports/toys.

## Editorial changes

Rewrote all 30 story summaries, 11 story openings, context for 18 objects,
and all six tour-stop descriptions. Refined homepage and collection copy,
year introductions, and the titles and summaries of 20 selected film entries.
Object cards no longer repeat “Why it mattered”; detail pages use “The
object’s story.” The pass focuses on familiar actions, specific objects, and
plain descriptions while retaining the longer sourced stories.

Examples include the family PC as a shared chair and phone line, choosing a
screen name, seeing circuitry through a purple shell, and rewinding a tape.
The full release collection still uses concise date-led archival descriptions.

## Search and intentional links

Search covers events, stories, objects, collections, years, tours, resources,
guides, and community routes. It normalizes accents and punctuation, ranks
exact and partial title matches ahead of body matches, and updates filter
counts for the current query. Pagination and browser history use the same
ranked results. Object metadata improves event discovery, including the
familiar “N64” alias for the gray controller. External resource results are
clearly labeled.

Related panels show up to three objects, two stories, and three varied events.
Object pages offer a search link to their complete set of connected dates.
Event and story pages link to the relevant collection and year introduction;
matching objects connect into existing tour stops. Each tour stop now links
to a relevant story, and three also link to dated events. Collection calendar
picks span the decade; Movies & TV includes television alongside films.

## Sourcing and media

The new entries link to primary sources including Nintendo, Sega, Microsoft,
W3C, NASA, the Television Academy, artist/label archives, the Library of
Congress, sports organizations, and public institutions. Regional release
distinctions and specific date notes remain visible. The Google entry uses
incorporation rather than a later birthday celebration; the Jordan entry
uses his return game rather than the earlier announcement.

All 67 original factual source records and all 30 object media records remain
unchanged. There are now 125 factual source records. The 37 reviewed media
items, attribution, licenses, and original/generated artwork disclosures
remain intact. The additions use existing typography and object connections;
no new historical-looking imagery was introduced.

## Validation

All 168 distinct browser checks are validated. The first full regression
run passed 164 checks. After the final compact shelf and context notes,
167 of 168 passed; the remaining test clicked before the tour finished
selecting its active stop. The test now waits for the requested stop, and
passed **20 consecutive repetitions**. This was a test synchronization fix;
no product-code change was required for the reset behavior.

| Check | Result |
| --- | --- |
| Python publication/build/content tests | 44 passed |
| Civil-date tests | 6 passed |
| Browser regression checks | 168 distinct checks validated; reset check passed 20 repetitions |
| Public route layouts | 533 routes × 390, 768, 1280, 1440px; no overflow/clipped controls |
| Minimum-width reflow | 17 principal surfaces at 320px |
| Runtime, console, HTTP errors and image decoding | All 533 routes passed |
| Calendar filters and empty states | 85,680 month/category/region/view/width combinations passed |
| Historical weeks | All 522 weeks at two widths; 1,044 states passed |
| Accessibility | No axe violations on tested pages, menus, and responsive Phase 2 surfaces |
| Static link audit | 30,467 internal, 799 external, 2,287 fragment links; 0 errors |
| HTTP release audit | 533 routes passed, 55 excluded paths returned 404, 12 encoding samples passed |
| Generated sources, assets, media, coverage, editorial and curation checks | Passed |
| Public-only build and integrity check | Passed; 677 runtime files |
| Git diff whitespace check | Passed |

Final package digest:
`0bc0599cb9aafb642eb410c815bd127f95bd7f3985140e7f2fd1060bf6b94521`.

Machine-readable evidence: [QA results](launch-phase2/qa-results.json) and
[HTTP results](launch-phase2/http-results.json). Screenshots include
[desktop homepage](launch-phase2/home-1440-top.png),
[mobile homepage](launch-phase2/home-390.png),
[1994 defining moments](launch-phase2/year-1994-1440-top.png), and the 1991/1992
object context at both mobile and desktop sizes. A final regeneration removed
empty indented lines; it did not alter the tested DOM or styles.

## Delivery

Sources, generated routes, search/runtime indexes, sitemap, tests, and QA
evidence are included in the Phase 2 revision. The public-only release is
built at `dist/release/public/`. Commit/push is a source handoff; activation
on the production web server is a separate deployment operation described
in `docs/RELEASE.md`. Phase 3 remains a separate sprint.

Maintenance instructions: [editorial curation](../docs/EDITORIAL_CURATION.md).
