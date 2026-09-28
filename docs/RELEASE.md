# 90s.land release and rollback

This is an operator handoff for the Phase 5 static build. It does not deploy or
change DNS. A production task must first identify the actual host, service
account, web server, document root, and existing deployment method; do not reuse
an unverified path from an earlier prototype.

## Prepare an exact release

Use a clean checkout of the intended GitHub commit. Install the pinned development
dependencies (`requirements-dev.txt` and `pnpm-lock.yaml`) only on the build
machine. The public server needs no Python, Node, database, or package install.

```sh
pnpm author:check
pnpm editorial:check
pnpm content:check
pnpm test:content
pnpm test:dates
pnpm test
python3 tools/audit_site.py
python3 tools/build_release.py --output /tmp/90s-land-release
python3 tools/build_release.py --check --output /tmp/90s-land-release
```

The output directory must be new or empty. The builder never overwrites an
existing release. It produces `public/`, `release-manifest.json`, and a
deterministic `90s-land.tar.gz` with a companion SHA-256 checksum. Only
`public/` is eligible for the web root; keep the manifest with the release record.
Record the full Git commit beside its manifest before transfer.

The builder starts with all catalog routes, the 404 page, sitemap, robots file,
web manifest, and social image, then follows local HTML/CSS/JS/JSON dependencies.
The manifest lists SHA-256 hashes and sizes for every shipped file and a digest
for the complete inventory. It includes deterministic gzip variants for text.
Source fragments, catalogs used only by the generator, tests, QA reports, frozen
snapshots, node_modules, Git metadata, and original hero PNGs are excluded.

## Preview the actual package

```sh
python3 tools/serve_release.py --root /tmp/90s-land-release/public --port 4174
```

In another terminal:

```sh
python3 tools/check_release_http.py --release /tmp/90s-land-release
PLAYWRIGHT_BASE_URL=http://127.0.0.1:4174 pnpm exec playwright test tests/release.spec.mjs
LIGHTHOUSE_BASE_URL=http://127.0.0.1:4174 LIGHTHOUSE_OUTPUT=reports/phase-5/performance-final pnpm lighthouse
```

This server binds only to localhost. It negotiates gzip, sends `Vary:
Accept-Encoding`, revalidates content, and returns the custom 404 page with
status 404. It is a review tool, not a production service.

The release performance measurements depend on compression being enabled.
Configure the actual host to serve the supplied `.gz` files, or apply equivalent
dynamic gzip/Brotli compression to HTML, CSS, JS, JSON, SVG, and XML. Check those
response headers after deployment. Keep the uncompressed originals for clients
that do not negotiate compression.

Required serving behavior:

- Resolve `/section/` to its `index.html`, retaining query strings and anchors.
- Serve `/404.html` with an actual 404 status for unknown URLs, not a homepage
  rewrite. Do not expose directory listings or files outside `public/`.
- Revalidate HTML, JSON, CSS, and JS (`Cache-Control: no-cache` is a safe initial
  policy). The runtime filenames are not universally content-addressed, so do
  not apply a blanket year-long immutable policy. Long-lived caching requires
  an explicit filename/version strategy.
- Preserve HTTPS, canonical 90s.land URLs, correct MIME types, and query strings.
  No SPA fallback, service worker, cross-origin API, font service, or tracker is
  required.
- If the host enforces a Content Security Policy, account for the small inline
  script that sets the enhancement class before first paint. Compute its hash
  from the final HTML; do not silently remove it or weaken unrelated policy.

## Production promotion after target confirmation

1. Read the current host configuration and identify the exact existing release.
   Keep a verified copy of its files and configuration. Record its commit or
   checksum and the active document-root/symlink target.
2. Transfer the new package into a **new release directory** owned by the existing
   site service account. Verify its manifest on the destination before promotion.
   Keep source repositories and manifests outside the public root.
3. Preview that directory through the real serving configuration. Check homepage,
   June 1996 calendar filters, This Week date navigation, a story, Culture, search,
   an original deep link, source credits, and a nonexistent URL. Inspect gzip,
   cache, content-type, and 404 headers.
4. Promote atomically using the host's existing release mechanism. For a symlink
   deployment, switch the symlink rather than copying over live files. Do not
   invent a service restart or change DNS as part of a static content update.
5. Repeat the smoke checks on the public HTTPS domain, including a fresh private
   browser window and an existing session. Check console/network failures and
   mobile navigation. Retain the previous release through acceptance.

## Rollback

Roll back if routes fail, core navigation/search/calendar behavior breaks, source
files are exposed, or response/asset errors affect the public experience. Switch
the active release pointer back to the recorded previous directory using the
same atomic mechanism. Restore changed serving configuration only if it was
part of this deployment, then verify homepage, legacy deep links, 404 behavior,
and the previous manifest. Retain the failed release for diagnosis.

There is no database migration. Passport and tour progress stay in each browser;
this release retains their storage keys and schema. Rollback must not clear local
storage, erase visitor progress, delete the prior release, or rely on guessed
server paths. Git rollback and deployed-file rollback are separate operations;
the release pointer can be restored without rewriting GitHub history.
