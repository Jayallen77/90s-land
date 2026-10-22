# Deploying 90s.land from GitHub main

This is the authoritative Hermes deployment runbook. Production source is
`https://github.com/Jayallen77/90s-land.git`, branch **`main`**. Justin makes and
tests changes locally with Codex, commits and pushes to `main`, then asks Hermes
VPS Deployment Manager to deploy. A GitHub push runs verification; it does not
deploy. Other branches and files edited directly on the VPS are not deployment
sources.

The existing Caddy document root is
**`/home/justin/sites/90s-land-releases/current`**, a symlink to a versioned release.
Keep that root, the release layout, Caddy configuration, and existing deployment
user unchanged. Hermes performs the VPS operations; this repository audit did
not connect to or change the VPS.

## First deployment: reconcile production before replacing it

**The active production revision has not been verified against GitHub `main`.**
The October 22, 2026 local audit found local and GitHub `main` at
`485f5b4e634f796fc8656d6cb68e680fc2a61a79`. Public HTTPS sampling was blocked with
403 responses. A similar-looking homepage is not evidence of identical source.
Do not interpret publication of this runbook as approval to overwrite unknown
production changes.

Before the first deployment under this workflow, Hermes must:

1. Resolve the existing `current` symlink, record its exact target, inspect the
   private release manifest and existing deployment records, and preserve that
   complete release using the existing backup procedure. Do not edit live files.
2. Inspect the actual VPS source checkout, its remote, branch, status and commit.
   Stop for uncommitted changes, local commits outside `origin/main`, an unknown
   release origin, or content/assets absent from GitHub. Preserve those files and
   report the differences to Justin for reconciliation into `main` locally.
3. Verify the active release's actual files against its manifest. A recorded Git
   SHA alone does not rule out later manual edits. If provenance is missing, build
   a comparison package from `main` with `--as-of` set to the active manifest's
   `editorialAsOf`, into a separate staging directory. Compare the complete public
   inventory and uncompressed file hashes, including images/fonts. Compression
   differences across Python/zlib versions are not website changes. Missing,
   additional, or different website files require investigation before switching.
4. Confirm the existing release layout and publisher. The included helper only
   supports `releases/CONTENT_DIGEST/public`, schema-2/3 manifests and complete
   verified packages. If the current versioned release uses another layout, keep
   using the established publisher with its existing atomic switch/rollback
   procedure. Do not migrate the release system to make the helper work.

Keep the reconciliation evidence in Hermes's private deployment records. On later
deployments, verify that the active target and manifest still match the last
recorded successful deployment; unexplained drift requires the same investigation.
GitHub synchronization alone never proves production parity.

## Build and tracking contract

| Item | Contract |
| --- | --- |
| Production source | GitHub `main` at the SHA fetched when deployment begins |
| Build | `python3 -B tools/build_release.py --require-clean` |
| Equivalent package script | `pnpm build:production` |
| Verify existing package | `python3 -B tools/build_release.py --check` |
| Public output | **`dist/release/public/`** |
| Private metadata/transport | `dist/release/release-manifest.json`, `90s-land.tar.gz`, `90s-land.tar.gz.sha256` |
| VPS build dependencies | Git, Python 3.10+, system time-zone data including `America/Denver`; Linux or macOS |
| Runtime | Static HTML/CSS/JS, local images/fonts; Caddy serves the existing `current` pointer |

Production packaging uses Python's standard library. It needs no Node, pnpm,
Pillow, npm install, credentials, image generation, or application server. Use a
Python 3.10+ executable on PATH; stock macOS `python3` may be older. The strict
build refuses staged/unstaged/untracked work and ignored public dependencies
that are missing from Git. It checks again after building and reports
`sourceCommit`. It does not commit, stash, clean, reset or pull anything.

Authoring sources, generated public HTML, responsive media, sharing cards and
runtime payloads are committed. `dist/`, dependency folders, environments and
private research exports are ignored. The public package follows dependencies
from every catalog route and refuses missing files, private paths and symlinks.
Never serve or copy the entire Git checkout. Never publish the private manifest
or transport archive inside `current`.

The October 22 audit verified 779 public routes and 1,265 runtime files, all
tracked. Five pre-existing untracked research/intermediate files were preserved
locally; none is a public runtime dependency. They are not required on the VPS.

## Local changes and GitHub verification

Use Python 3.10+ and the pinned development dependencies for authoring and tests:

```sh
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements-dev.txt
# Use the pnpm version declared in package.json (11.9.0).
pnpm install --frozen-lockfile
pnpm exec playwright install chromium

git switch main
git fetch origin
git merge --ff-only origin/main
# Edit authoritative sources, then regenerate when required:
pnpm author
pnpm author:check
pnpm editorial:check
pnpm content:check
pnpm test:content
pnpm test:dates
pnpm run audit
pnpm launch:audit
pnpm build
pnpm build:check
```

Review each changed path and stage the intended files explicitly. Preserve
unrelated work separately rather than adding it blindly. Commit the verified
changes, then test the committed snapshot with `pnpm build:production` in a clean
checkout. A fresh clone is useful when the authoring checkout contains unrelated
untracked work. To check packaged behavior, run `pnpm release:preview` in one
terminal and, in another:

```sh
pnpm release:audit
LAUNCH_QA_DIR=dist/local-qa PLAYWRIGHT_BASE_URL=http://127.0.0.1:4174 pnpm test
git diff --check
git fetch origin
# If main advanced, integrate without rewriting history and repeat affected checks.
git push origin main
git ls-remote origin refs/heads/main
```

The `Verify production build` GitHub Actions workflow runs source/media/content
checks, Python/date tests, a strict build, the package HTTP audit and the complete
browser suite on pushes to `main` and pull requests targeting `main`. It has no
VPS credentials or deployment step. Hermes must confirm a successful workflow
for the exact fetched SHA before deployment; pending, missing or failed checks
are a stop condition. Branch rules were not changed by this audit.

## Hermes deployment procedure

Serialize deployments through the existing Deployment Manager. Complete the
production reconciliation above before the first switch. Start in the **actual
existing private VPS checkout**, whose location Hermes must inspect; the known
Caddy release path is not the source checkout path.

```sh
set -eu
SITE_REPO=$(git rev-parse --show-toplevel)
SITE_ROOT='/home/justin/sites/90s-land-releases'
SITE_ORIGIN='https://90s.land'
cd "$SITE_REPO"

test "$(git remote get-url origin)" = 'https://github.com/Jayallen77/90s-land.git'
test "$(git branch --show-current)" = main
test -z "$(git status --porcelain --untracked-files=all)"
git fetch origin
SITE_REVISION=$(git rev-parse --verify refs/remotes/origin/main)
git merge --ff-only "$SITE_REVISION"
test "$(git rev-parse HEAD)" = "$SITE_REVISION"
test -z "$(git status --porcelain --untracked-files=all)"
python3 -c 'import sys; from zoneinfo import ZoneInfo; assert sys.version_info >= (3, 10), "Python 3.10+ required"; ZoneInfo("America/Denver")'

# Hermes: confirm the GitHub verification workflow passed for SITE_REVISION now.
# Do not proceed to publication without that result and production reconciliation.

SITE_LOG="dist/hermes/$(date -u +%Y%m%dT%H%M%SZ)-$SITE_REVISION"
mkdir -p "$SITE_LOG"
git rev-parse HEAD > "$SITE_LOG/source-commit.txt"
python3 -B tools/build_release.py --require-clean > "$SITE_LOG/build.log" 2>&1
cat "$SITE_LOG/build.log"
python3 -B tools/build_release.py --check
```

Always build after synchronizing. A pull alone is insufficient because `dist/`
is not tracked. Packaging also refreshes Home and This Week for the current
America/Denver date without modifying committed sources. Use the existing Hermes
scheduling facility for date refreshes if already configured; this change does
not install a scheduler. Explicit `--as-of YYYY-MM-DD` is for reproduction and
comparison, not routine production deployment.

Continue through the **existing** publisher only after staging verification. If
the existing layout is confirmed compatible with the repository's helper, these
are the exact commands. The read-only preflight below refuses an incompatible
current pointer before the publisher writes anything:

```sh
SITE_PREVIOUS=$(python3 -B - "$SITE_ROOT" <<'PY'
import sys
from pathlib import Path
sys.path.insert(0, 'tools')
from deploy_release import managed_current
previous = managed_current(Path(sys.argv[1]).resolve())
if previous is None:
    raise SystemExit('Expected an existing production release; stop and inspect')
print(previous)
PY
)
printf '%s\n' "$SITE_PREVIOUS" > "$SITE_LOG/previous-release.txt"
cp dist/release/release-manifest.json "$SITE_LOG/release-manifest.json"

# Stop if main advanced while this candidate was being built/verified.
test "$(git ls-remote origin refs/heads/main | cut -f1)" = "$SITE_REVISION"
test "$(git rev-parse HEAD)" = "$SITE_REVISION"
test -z "$(git status --porcelain --untracked-files=all)"

# Copies only the verified package and atomically replaces the current symlink.
python3 -B tools/deploy_release.py --site-root "$SITE_ROOT" > "$SITE_LOG/publish.json"
cat "$SITE_LOG/publish.json"

if ! python3 -B tools/check_release_http.py --base-url "$SITE_ORIGIN" \
    --output "$SITE_LOG/http.json"; then
    # Restore the prior complete release without rebuilding it.
    python3 -B tools/deploy_release.py --site-root "$SITE_ROOT" --release "$SITE_PREVIOUS"
    python3 -B tools/check_release_http.py --base-url "$SITE_ORIGIN" \
        --release "$SITE_PREVIOUS" --output "$SITE_LOG/rollback-http.json"
    exit 1
fi
```

For a different existing publisher, supply the same verified `public/` output,
retain manifests and archives privately, preserve the exact previous target,
switch atomically using that publisher, and use its established rollback. Do
not run the helper against an incompatible layout or change Caddy to accommodate
it. Carry out the same complete live HTTP audit against the candidate package.

The HTTP audit checks all routes and sharing cards, private-path exclusions,
404 behavior and identity/gzip response hashes. It expects compression and
`Vary: Accept-Encoding` from the existing serving configuration. If those checks
fail, roll back and report; changing Caddy is outside this procedure.

Then smoke-test Home, Timeline, Music/Games filters, This Week navigation,
Search, a story, object images, Surprise Me, the tour, Passport and mobile menus.
Retain existing browser storage while testing. Save the automatically captured
source SHA, manifest/digest, previous/current targets, build/HTTP/browser results
and outcome in Hermes's private persistent deployment log. Report the deployed
SHA and verification result to Justin. No manual version numbers or release
tags are required; the existing helper names immutable releases by content digest
and retains previous releases.

## Rollback after a later failure

Use the recorded previous release with the established publisher. For the
compatible included helper, in the same deployment shell:

```sh
test -n "$SITE_PREVIOUS"
python3 -B tools/deploy_release.py --site-root "$SITE_ROOT" --release "$SITE_PREVIOUS"
python3 -B tools/check_release_http.py --base-url "$SITE_ORIGIN" \
    --release "$SITE_PREVIOUS" --output "$SITE_LOG/rollback-http.json"
```

In a new shell, load the previous path from that deployment's private record;
do not guess it or select a directory by name ordering. Keep failed and previous
releases for diagnosis. Do not delete releases, reset Git, force-push, overwrite
live files, rebuild old content from the latest checkout, clear visitor storage,
change permissions recursively, or restart/reconfigure Caddy to perform rollback.

Detailed package internals and the serving contract remain in
[docs/RELEASE.md](docs/RELEASE.md).
