# Production deployment audit — 2026-09-28

Scope: local repository changes against `6dc11c98606fbeab6f258830687d48029f6e4d8b`.
The initial audit made no GitHub push, VPS connection, Caddy configuration edit,
or live deployment. A subsequent GitHub handoff was authorized after review;
VPS deployment remains a separate task for Hermes. The exact Hermes error and active VPS paths were not supplied, so the
findings below establish repository defects, not a confirmed live-server incident.

## Root cause

1. The checkout contains generated website pages at its root alongside `content/`,
   `data/`, `tools/`, `tests/`, reports, development dependencies, and `.git`.
   Serving or recursively copying that checkout does not establish a public-only
   boundary. `.gitignore` cannot restrict HTTP access.
2. Phase 5 introduced an optional public package, but there was no default `build`
   command or repeatable publisher. `release:build` required an output argument
   and refused any existing nonempty output. The ignored `dist/` output is absent
   after a clean clone/pull, and the runbook did not provide a concrete pull/build/
   publish procedure. Pulling GitHub could update the wrong served tree or leave
   the release missing/stale.
3. The browser fetched `data/artifacts.json` and `data/editorial-index.json` directly,
   so the previous package intentionally exposed those catalog files. Its broad
   dependency policy was not a strict runtime allowlist and did not reject every
   hidden path, route-seed traversal, or symlink. This audit did **not** find evidence
   that the previous package actually included `.git` or credentials.

## Exact repository changes

| Files | Change |
| --- | --- |
| `tools/build_release.py` | Default output `dist/release`; staged repeatable builds; strict route/runtime policy; rejection of internal paths, hidden paths, traversal, and symlinks; schema-2 manifest with routes; hashes, byte counts, gzip-body and inventory verification; serialized builds; failed-build recovery. |
| `tools/deploy_release.py` (new) | Copies only a verified package to an external release store, then atomically switches `current` to its `public/` directory. Reuses identical releases, retains old releases, supports verified rollback, rejects foreign current pointers/directories, and supplies readable file permissions. Does not configure any server. |
| `tools/optimize_assets.py` | Loads Pillow/fonttools only for generation so integrity checking works with the standard library on the VPS. |
| `tools/render_site.py`, `assets/runtime/week.json`, `assets/runtime/surprise.json` | Generates limited public payloads. Original authoring catalogs stay private and intact. |
| `js/archive.js`, `js/surprise.js` | Uses those limited payloads. Same published events, eligible objects, visible text, links, and storage keys. |
| `tools/serve_release.py` | Defaults to the canonical public output and verifies the package before localhost preview. |
| `tools/check_release_http.py` | Audits routes from the release manifest, 52 missing/private paths, identity/gzip bodies, and headers. Reports go to `dist/` by default instead of overwriting Phase 5 evidence. |
| `package.json` | Adds `build`, `build:check`, `release:publish`, and `release:audit`; supplies usable defaults for build/preview. |
| `.gitignore` | Keeps `dist/` ignored; adds local environment files, Python environments/bytecode, and temporary release directories. |
| `playwright.config.mjs` | Binds the development server to localhost. |
| `tests/archive.spec.mjs`, `editorial.spec.mjs`, `hubs.spec.mjs`, `site.spec.mjs` | Uses the configured base URL for every context, including no-JavaScript tests; updates the failed-fetch test endpoint; waits for asynchronous week/tour initialization before interactions. |
| `tests/test_release.py` | Adds boundary, reproducibility, obsolete-file removal, failed-build preservation, promotion, rollback, permission, and foreign-target regression coverage. |
| `README.md`, `docs/RELEASE.md` | Declares the public directory and the private/public contract; documents exact revision-pinned VPS pull/build/publish/check/rollback commands and Caddy preconditions. |
| `reports/PRODUCTION_DEPLOYMENT_AUDIT.md`, `reports/deployment-audit/` | This review record and machine-readable local verification evidence. |

No generated HTML, CSS, page route, media file, source catalog, historical QA
snapshot, or browser storage schema changed. The only browser-code changes are
the two public data consumers above.

## Production directory and deployment contract

Build output: **`dist/release/public/`**. The adjacent manifest, archive, and checksum
must remain outside the document root.

Published layout: **`SITE_ROOT/current`**, a symlink to
`SITE_ROOT/releases/CONTENT_DIGEST/public`. `SITE_ROOT` is a dedicated directory
outside the Git checkout. Only the files in `public/` are served.

The exact deployment procedure is in [the runbook](../docs/RELEASE.md#exact-vps-procedure-after-the-reviewed-change-is-merged).
It uses the confirmed VPS paths and a full approved GitHub revision, then runs:

```sh
git pull --ff-only origin main
python3 -B tools/build_release.py
python3 -B tools/build_release.py --check
python3 -B tools/deploy_release.py --site-root "$SITE_ROOT"
python3 -B tools/check_release_http.py --base-url https://90s.land
```

Use the complete runbook for the clean-tree/branch/revision checks, previous-release
record, prerequisites, and rollback commands. Do not execute the abbreviated
sequence without those preconditions.

**If Caddy currently serves the repository root, a separate hosting correction is
still required.** No repo script can override that configuration. The runbook stops
when the existing root is not `SITE_ROOT/current`; no Caddy modification is included
or authorized here. Caddy itself was not installed/run locally; HTTP checks use the
verified package preview and do not certify the unknown live configuration.

## Local validation

See [build evidence](deployment-audit/build-and-http.json) and
[HTTP probe results](deployment-audit/http.json).

- 474 routes, 636 runtime files before gzip sidecars; strict manifest verification passes.
- Clean source export without `.git`, `node_modules`, or previous `dist/`: identical
  production manifest and archive.
- A fresh Python virtual environment without pip, Pillow, or fonttools: identical archive.
- Rebuilding the same inputs produces identical output. Regression tests confirm
  removed assets disappear and a failed next build preserves the verified package.
- 475 HTML files (474 routes plus the 404 page) and all four stylesheets are
  byte-for-byte identical to the previous Phase 5 release.
- All 474 routes return HTTP 200 from the production preview. All 52 missing/private
  URL probes return HTTP 404. Twelve identity/gzip responses match manifest hashes.
- Actual full-package local publication under umask `077`: verification passes,
  public files remain readable, source/catalog/manifest paths stay outside the root.
- Python suite: 35 passing tests. Date arithmetic suite: 6 passing tests.
- Authoring, media integrity, migration, content, coverage, and editorial checks pass.
  Static link audit: 17,048 internal links and 2,471 fragments, zero errors.
- `.gitignore` verification covers `dist/`, environment files, Python environments,
  dependencies, and bytecode. No tracked `.env`, PEM, private-key, or PKCS#12 files
  were found by filename inventory; this is not a historical secret scan.

The first browser run exposed two test timing races: interaction occurred before
weekly data or tour enhancement initialization. Tests now wait for observable
ready state. An earlier complete run passed **57/57 browser tests** against the
production package in 2.8 minutes, including all 474 routes at four viewport
sizes, accessibility, no-JavaScript fallbacks, and museum interactions. The weekly
navigation test also passed three consecutive focused repetitions.

Final targeted handoff: the subsequent full-suite gate passed 56 tests but the
wide-screen sweep exceeded its cumulative 180-second limit while navigating to
`/stories/the-internet-came-in-the-mail/`. At Justin's direction, only that page
was repeated three times in fresh wide-screen browser contexts: all passed
(242 ms, 97 ms, 81 ms), with no layout or JavaScript errors. This is treated as
a test flake; no site-code fix or unrelated refactor was made.

The production build/check then passed again. The requested five-page smoke
check passed for Home, the story, June 1996 timeline, Games, and This Week,
including Surprise Me, a game filter, and weekly date state. All 474 HTTP routes,
52 missing/private path probes, and 12 identity/gzip samples passed again.
The expensive full browser suite was not repeated for this final handoff.

Release content digest:
`d3914fb0be3713717344e946cf02d15de8d359a48729d786b216d5832ec5780c`

Archive SHA-256:
`4cad0c321805e4e180a5ca046d0ce8771df5c10b59bb2fee7419381fa2d74b63`
