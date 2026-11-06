# Bring a friend — November 6, 2026

This sprint adds six researched features and five photographed objects, substantively improves six retained features, and connects the resulting collection through a new magazine edition. The existing visual identity, static architecture, six web exhibits and all prior story URLs remain intact.

The complete reviewable package contains **41 stories, 67 objects and 139 active pages**. It preserves **295 timeline records, 101 defining moments, 311 compatibility pages and 340 retired routes**. All 779 original URL decisions remain accounted for; eleven deliberately introduced URLs live in `content/editorial/additions.json` instead of changing that historical ledger. Existing Passport object identifiers and tour stop identifiers are preserved.

## What to read and try

| Feature | Delivered depth |
| --- | --- |
| [Pokémon needed a friend and a cable](../../stories/pokemon-needed-a-friend/index.html) | Original Red/Blue Cable Club workflow, compatible equipment, trade versus battle and consequences for saved collections. |
| [One more challenger at the arcade](../../stories/one-more-challenger/index.html) | Six attack strengths, facing-specific Ryu fireball input and the controller changes between cabinet and home. The photographed screen is identified as Champion Edition. |
| [French house: let the loop change around you](../../stories/french-house-in-the-filter/index.html) | Three named recordings, listening prompts, and Alan Braxe’s own sample/drums/bass/vocal account of the Stardust production. |
| [Thirty-two megabytes for the bus ride](../../stories/thirty-two-megabytes/index.html) | Rio PMP300 transfer hardware, explicit encoding assumptions and a working storage/bitrate/track-length calculator. |
| [When texting meant learning the keypad](../../stories/texting-on-twelve-keys/index.html) | The original Nokia 3210 guide, 13 versus five letter presses for HELLO, dictionary ambiguity and a working key-mapping comparison. |
| [The team behind the 1999 World Cup final](../../stories/the-team-behind-the-1999-final/index.html) | Lilly’s clearance, Scurry’s save, Chastain’s kick and a clear distinction between the 0–0 match and 5–4 shootout. The actual 1999 team photograph is dated to the reception afterward. |

The new object files identify a 1997 museum Tamagotchi, early silver Game Boy Pocket, dual-connector Game Boy link cable, Rio PMP300 and Roland TR-909. Each explains operation, limitations and a concrete connection to a story. Era-of-use labels avoid treating 1999 as a manufacturing end date.

Retained features improved: `holiday-toys-that-answered-back`, `handhelds-and-batteries`, `from-mixtape-to-file`, `the-landline-negotiation`, `the-console-war-couch` and `sampling-a-record-collection`. Their additions cover the actual toy, Pocket hardware and power, file-size arithmetic, handset replies, arcade/home controls and listening to a loop’s arrangement.

## Imagery and editorial curation

Seven new source photographs total about 1 MB before responsive derivatives. Original source identities, creators, usage terms, hashes, captions, alt text and era/model limitations are recorded in [image-review.json](image-review.json). Six new stories have distinct lead identities; the existing Nokia photograph becomes one new story lead without being reused by another story. The toy feature gains an actual 1997 photograph and keeps its original functional comparison as a supporting figure. The Pocket photograph supports the portable-play comparison. All **41 story lead identities are distinct**.

The TR-909 image preserves the source’s Emhoo/Metoc attribution and editing note. The White House image is US federal public-domain material, dated July 19, 1999. Museum Rotterdam’s catalog date belongs to the Tamagotchi object, not the photograph. A restricted Smithsonian jersey image and a modern Furby shop photograph were rejected. No paid or newly generated illustrative assets were used.

The homepage issue, all eight collection introductions, relevant year selections and sparse-week reading were refreshed. The homepage object shelf is now edition data. There are **251 reasoned connections across all 108 story/object pages**. Game-shelf entries now link directly to the Pokémon and arcade features. SMS/text-message aliases find the keypad subject; TR-909/TR909 aliases identify the drum machine. The title-first R&B behavior remains covered.

## Verification and evidence

- [Live review](live-review.json): all 128 pre-sprint active pages returned HTTP 200 with one h1. This was a read-only crawl. Raw HTML hash differences were not treated as proof of a deployment defect.
- [Page QA](page-qa.json): all 139 final active pages reviewed at 390 and 1440 px, **278 renders, zero issue pages**. Checks include h1, image decoding, horizontal overflow, uncaught page errors, unrendered content markers and Axe. Full-page captures remain in `/private/tmp/90s-land-review-20261106/final-page-captures`; paired contact sheets were visually inspected across the collection. Additional direct browser review covered the homepage, thumbnail subjects and the two tools, including a real keyboard-driven bitrate change and mobile keypad input.
- [HTTP QA](http-qa.json): all 450 served routes and 139 sharing cards return successfully. Identity/gzip samples match the package manifest; authoring, repository and private paths return real 404s.
- Python content/preservation/release tests, JavaScript date/search/discovery/math tests, browser interaction tests, content checks, static link/fragment audits and clean-snapshot production packaging are required before delivery. Exact final results are recorded in [validation.json](validation.json).

The first interaction run exposed two copies of a shared stateful module after asset-version changes. All transitive imports now use the same version, and the content gate rejects multiple runtime identities for one local module. The affected seven menu/Passport flows passed after correction; the final full suite is required as well. The feature-selection test now reads the active edition rather than a historical hardcoded story.

## Research scope and delivery

New and edited historical claims were checked against manufacturer/publisher records, period manuals, the instrument designer and producer interviews, museum records, US Soccer and FIFA. Original manual scans are cited as such even when hosted by preservation sites. The Capcom-hosted original booklet was search-index readable but returned 403 to the direct research client; that retrieval limitation is visible in its source note. The Rio manual is explicitly the 64 MB edition, while standard 32 MB capacity is sourced separately. No exact timeline dates were invented or changed.

This is a focused editorial sprint, not a fresh verification of every unchanged sentence or every external destination linked by the museum. Automated accessibility checks supplement visual and interaction review; they do not constitute a complete assistive-technology audit.

Delivery uses the existing GitHub `main` → Hermes workflow. Codex prepares and validates the source and public-only build. Production deployment remains with Hermes; no SSH, VPS or Caddy changes are part of this sprint.
