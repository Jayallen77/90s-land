# Reference-driven rebuild: approved decisions and phase handoff

## Approved direction

Rebuild the site as a dense 90s entertainment/editorial archive, following the
three supplied reference designs. Keep static delivery, Python generation,
browser ES modules, existing public URLs, and useful museum features. Replace the
page-authoring and visual systems in subsequent phases.

- Home reference: `docs/design/references/home.jpeg`, 1086×724.
- Timeline reference: `docs/design/references/timeline.jpeg`, 1086×724.
- Games reference: `docs/design/references/games.jpeg`, 1182×665.
- Primary navigation: Home, Timeline, Music, Movies & TV, Games, Tech, Culture,
  This Week.
- US-first historical coverage; label regional releases and include major global
  events. Serious news stays in the timeline; entertainment leads primary heroes.
- This Week defaults to 30 years ago, using America/New_York's date and the
  historical Monday–Sunday week containing the shifted date. Other years/weeks
  remain browsable; clamp invalid leap-day mappings and handle decade boundaries.
- Use free/open suitable editorial media plus original artwork. No paid asset
  purchases. Do not substitute gradient placeholders for collage imagery.
- Full editorial launch: 30 complete stories, at least 300 sourced dated events,
  every month represented, and at least three events per historical week of 1996.
- Existing monthly context, chart rows, and copied source links are not completed
  new stories or verified events.
- Popular modules use labeled editorial selections until genuine measurements
  exist. Historical rankings retain exact source period and region.

## Architecture after Phase 1

Preserve existing category URLs. Add `/zones/culture/`, `/this-week/`,
`/stories/{slug}/`, `/archive/{type}/{slug}/`, and `/events/{slug}/` as their content
and templates become ready. Keep Fashion, Internet Culture, Transparent Tech,
Passport, Surprise Me, the six-stop tour, resource directory, guestbook preview,
credits, and search integrated into the new shell.

Promote reviewed import material into explicit source catalogs and story records;
generate complete HTML using shared Python component functions. Public HTML must
cease being the editorial source of truth. Retain dependency-free static hosting;
no application framework, database, hosted CMS, or tracking service is needed.

Reference desktop proportions: Home middle row approximately 49/24/27%; Timeline
75/25% main/sidebar; Games 29/31/25/15% feature/rankings/platforms/stats. Use 8–12px
panel gaps, thin blue-violet borders, sharp corners, navy surfaces, restrained
pink/cyan/purple/yellow accents, and substantial real imagery. Extend the approved
component system to every page. Mobile reorganizes modules into compact lists,
small grids, and contained horizontal rows.

## Page/module handoff

| Page | Modules in order |
|---|---|
| Home | Collage hero; wide weekly feature + featured story + six-category grid; six-card popular row; compact discovery strip; footer. |
| Timeline/year | Year collage; month selector; heading/filters/view controls; lead and compact event grids; Quick Facts and spotlight sidebar; pagination/context; decade navigation. Calendar must display real days. |
| Games | Collage hero; genre/platform rail; feature + rankings + platform tiles + stats; deep dives/popular row; game archive; hardware/resources. |
| Music | Collage hero; genre rail; feature + annual charts + genre tiles + facts; releases; artists/scenes; deep dives; popular stories. |
| Movies & TV | Cinematic hero; type/genre rail; video-store feature + sourced box office + TV highlights + facts; genre tiles; profiles; deep dives; artifacts/popular. |
| Tech | Computing collage; subcategory rail; family-PC feature + milestones + hardware tiles + facts; product/software archive; deep dives; specialist collections. |
| Culture | Culture collage; topic rail; mall-life feature + touchstones + browse tiles + facts; fashion/collecting; deep dives; people/products/trends; specialist links. |
| This Week | Explicit historical date range; week/year navigation; lead event/roundup; day-grouped events; facts/charts; stories/objects; containing month link. |

The 30-story launch slate is six per category: Games (console wars, LAN parties,
3D, memory cards, cheat codes, couch co-op); Music (mixtapes to MP3, grunge,
hip-hop/R&B crossover, TRL/teen pop, rave culture, Discman/CD listening); Movies &
TV (video store, Saturday cartoons, appointment TV, blockbuster summers, VHS/home
recording, teen/self-aware horror); Tech (family PC, Windows 95, AOL/dial-up, early
browsers, pocket technology, transparent design); Culture (mall life,
grunge/streetwear, teen catalogs, digital pets/toy collecting, sports/pop culture,
screen-name identity). These are planned subjects, not researched publication
claims.

## Implementation checklist

- [x] Phase 1: frozen source/route/anchor/catalog baseline and supplied references.
- [x] Phase 1: deterministic editorial, monthly, chart, media, and link extraction.
- [x] Phase 1: complete block inventory and independent preservation validation.
- [x] Phase 1: remove fixed collection ceilings; test growth and loss detection.
- [x] Phase 2: logo, typography, tokens, shell, shared components, and first three
  hero compositions; compare Home, 1996, and Games against reference canvases.
- [x] Phase 3: complete static generation, event calendar, weekly behavior,
  detail pages, expanded search, preserved discovery tools, legacy links.
- [x] Phase 4: all eight sections; complete stories/events; source/media review;
  coverage and meaningful filter destinations.
- [x] Phase 5: mobile refinement, visual comparison, accessibility, link and
  functional checks, performance measurement, release/rollback preparation.

Read `docs/CONTENT_MIGRATION.md` before reusing or modifying extraction outputs.
Production publication remains outside this implementation phase.

Phase 3 implementation and authoring details: [PHASE_3.md](PHASE_3.md).
Verification: [PHASE_3_QA.md](../reports/PHASE_3_QA.md).

Phase 4 content, modules, and source qualifications: [PHASE_4.md](PHASE_4.md).
Verification: [PHASE_4_QA.md](../reports/PHASE_4_QA.md).

Phase 5 implementation: [PHASE_5.md](PHASE_5.md).
Final verification: [PHASE_5_QA.md](../reports/PHASE_5_QA.md).
Production handoff: [RELEASE.md](RELEASE.md). All five implementation phases are
complete; production publication remains a separate, target-specific task.
