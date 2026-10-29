# Editorial polish — October 29, 2026

The approved collection contains 35 rewritten features (nine music, eight games,
eight technology, six culture, and four movies/TV), 295 timeline records, and 62
expanded object entries. The existing visual system and collection heroes remain.

`page-by-page-review.csv` records both the approved action and implemented outcome
for all 779 original URLs. There are 128 active pages, 311 compatibility pages,
and 340 retired pages. Compatibility pages contain canonical destinations,
noindex metadata, a visible destination link, and a meta refresh that works
without JavaScript. Retired pages are absent from the release and return 404.
All 101 defining moments remain in their year collections.

Each feature has a separate lead-image record in
`content/editorial/story-media.json`, including its original source identity,
file hash, depicted subject, era note, creator, usage terms, caption, and alt text.
Photographs taken outside the decade are identified in their captions. They are
reference images of the actual subject, rather than claims of contemporary
documentation. No assets were purchased. Collection hero artwork remains intact.

The checks reject reused original story photographs, disguised filename reuse,
changed unreviewed image files, missing attribution, copied paragraphs, invalid
relationships, missing URL outcomes, and redirect chains. The static audit also
rejects repeated photographs within a page, including responsive variants of
the same original. Sparse calendar periods do not require filler entries.

The desktop and mobile contact sheets cover all 128 active pages at 1440 and
390 pixels. Full-size page captures remain in the local QA directory at
`/tmp/90s-land-polish-research/screenshots/`. The runnable preview includes the
entire collection. `preview-desktop.png` provides a quick view of the home page.

The source HTTP snapshot under `content/research/polish/` is a research aid,
not a claim that every publisher accepts automated requests. Some publishers
block automated retrieval. Sources are selected for their actual subject and
claim; exact days are not inferred from year-only museum records or photographs.

Publishing to GitHub main runs CI. Hermes remains responsible for production
deployment using `DEPLOYMENT.md`; this implementation makes no VPS changes.

Validation passed: 63 Python tests, nine date/discovery tests, and all 154 browser
tests. Authoring, content, editorial, curation, asset integrity, static links,
sharing metadata, and packaged HTTP checks pass. See the JSON audit evidence
in this directory for counts and results.
