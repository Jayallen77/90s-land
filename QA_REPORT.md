# 90s.land Share-Ready QA Report

## Verified baseline — July 28, 2026

- Local `main`, GitHub `main`, and the audited source commit matched at
  `c8ce73f78c0d401c559a2dba88b8424f4e7bd585`.
- Production spot checks of the homepage, shared CSS and JavaScript, the 1994
  capsule, and the Webring were byte-for-byte identical to the repository.
- 23 HTML pages and approximately 43,302 visible words.
- 1,395 internal links and 875 external links.
- 0 broken internal page destinations and 13 invalid fragments.
- 90 Webring resources with visible totals still set to 78.
- 64 image elements, all missing explicit intrinsic dimensions.
- No canonical links, Open Graph metadata, XML sitemap, robots file, custom 404,
  or manifest.
- No global skip link, reduced-motion stylesheet, or consistent focus treatment.
- Representative 390-pixel audits found 31 pixels of overflow on the 1994 page
  and 25 pixels on the Internet Culture room.
- Production returned Cloudflare-served dynamic HTML without the requested
  security headers. `/robots.txt`, `/sitemap.xml`, and an unknown route returned
  empty 404 responses.

## Final results

To be completed after implementation and verification.

