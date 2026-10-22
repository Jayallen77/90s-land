# Deployment standardization verification

Verified locally on October 22, 2026. Production deployment is a separate Hermes
operation. No SSH connection, VPS file change, Caddy change or release-system
migration was performed.

## Repository audit and preservation

- Repository: `https://github.com/Jayallen77/90s-land.git`.
- GitHub default branch and local branch/upstream: `main` / `origin/main`.
- After fetching, both started at
  `485f5b4e634f796fc8656d6cb68e680fc2a61a79`; divergence was `0 0`.
- No tracked local modifications were present at the start. No submodules,
  tracked symlinks, tracked environment files, assume-unchanged files or
  skip-worktree entries were found.
- The old `codex/playable-museum-overhaul` branch remains untouched. Its final
  tree matches the museum-overhaul publication already on main at `b80b0a9`;
  merging its old history is unnecessary.
- Five existing untracked files remain unchanged: the four
  `content/editorial/*-expansion.tsv` research tables and
  `assets/generated/share/object-memory-card-caf5a48fc97c.jpg`. They are not
  public dependencies. SHA-256-verified copies are under ignored
  `dist/deployment-audit/local-work-backup/`.
- The previous local `dist/release/` contained an extra unmanifested sharing
  image. The builder correctly refused to replace it. That complete bundle was
  preserved under `dist/deployment-audit/preexisting-release/` before a fresh
  candidate was built.

## Changes

`DEPLOYMENT.md` is the current deployment authority. It describes the local →
GitHub main → Hermes workflow, the supplied Caddy path, production reconciliation,
automatic commit capture, build/check commands, live verification, the existing
publisher and rollback. README and the package-format documentation link there;
the earlier launch handoff is explicitly historical.

`build:production` invokes `tools/build_release.py --require-clean`. That option
rejects dirty/staged/untracked work and public dependencies absent from the Git
index, then checks source cleanliness and HEAD again after packaging. It reports
the source SHA without changing the release manifest format or release naming.
Unsupported Python versions now produce a clear Python 3.10+ requirement.

The production preview now uses persistent HTTP/1.1 connections and a larger
connection backlog. The initial full-route run encountered connection resets,
failed module fetches and intermittent image decode failures with the former
HTTP/1.0 preview. After this change, connection reuse across HTML, JavaScript,
404 and image responses was verified, and the complete browser suite passed.
The Caddy serving configuration and website runtime were not changed.

`pnpm launch:audit` now writes to ignored `dist/publication.json`, preserving the
historical Phase 3 report. Browser screenshots are similarly routed under
ignored `dist/` during verification.

The new `Verify production build` GitHub Actions workflow checks pushes to main
and pull requests targeting main. It runs source/content checks, Python/date
tests, strict packaging, the HTTP audit and the browser suite. It has read-only
repository permissions and no production credentials or deployment operation.
Hosted execution is separate from the local results below.

The first hosted run passed source checks, packaging and HTTP delivery, then
found nine browser-test startup races on the slower Linux runner (189 passed).
The shared browser fixture now waits for existing Passport, timeline, hub and
Search readiness signals after navigation before tests interact or leave the
page. No website code or assertions were changed. All twelve affected cases,
including the directory's five widths, passed locally with that fixture.
The hosted suite is split across four isolated runners, with one browser worker
per runner, so the complete route matrix remains covered without serializing
every route sweep onto one hosted machine.

## Verification results

| Check | Result |
| --- | --- |
| Python generator/content/release tests | 57 passed, including three new deployment-source regressions |
| Date and discovery tests | 9 passed |
| Complete packaged browser suite | 198 passed in 8.2 minutes with the final readiness fixture |
| Authoring/media checks | Generated HTML, asset integrity, sharing cards and dimensions current |
| Content extraction, validation and coverage | Passed; frozen historical sources preserved |
| Editorial and curation checks | No errors |
| Static link audit | 779 routes, 44,170 internal links, 3,175 fragment links; zero errors |
| Publication/metadata audit | 779 routes, 777 indexable routes, 245 sharing cards; no errors |
| Public dependency tracking | All 1,265 runtime files are tracked; no missing dependencies |
| Package build and integrity check | Passed; schema 3 |
| Clean isolated Git snapshot | Strict build passed using Python 3.13 without third-party build dependencies |
| HTTP delivery | 779/779 routes and 245/245 sharing images passed |
| Public boundary and compression | 58 private-path probes returned 404; all 12 identity/gzip samples passed |
| Representative visual check | Eight mobile/desktop captures; no horizontal overflow; Home and Games inspected |
| Documentation/workflow syntax | Workflow YAML and all nine shell command blocks parsed successfully |
| Whitespace | `git diff --check` passed |
| Original untracked work | All five original SHA-256 hashes still match |

The public-file inventory and every file hash match the pre-change baseline
for editorial date `2026-10-22`. No website content, styling, browser modules,
catalogs or assets were changed. Both packages have content digest:

`d92700b74296b42e251afab013f5fbe2626f3176bebffcb86994795d7aa495e0`

The public output is `dist/release/public/`; packaging needs Git and Python
3.10+ with America/Denver time-zone data. Local build validation used Python 3.13;
the Python test suite used the bundled Python 3.12 environment. Development
dependencies remain pinned in the existing dependency files.

Detailed logs, public-only HTTP results, screenshots and local backups are under
ignored `dist/deployment-audit/`. The final committed snapshot is additionally
built from a clean local clone before the normal main push.

## Production boundary

The supplied production root is
`/home/justin/sites/90s-land-releases/current`, pointing to a versioned release.
The active production commit, exact release layout and production-only changes
have not been verified. Public HTTPS file sampling returned 403 responses.
This uncertainty was flagged before publication; Justin reaffirmed that the
local website should be pushed to GitHub main for Hermes to pull and deploy.

Hermes must preserve the current release, inspect for production-only work and
use the established release mechanism. The new runbook does not authorize a
Caddy change or require migration to a different release layout. Previous
releases remain available for rollback, with no manual version-number scheme.
