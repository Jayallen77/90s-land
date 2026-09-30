# 90s.land v1.0 launch handoff

Phase 3’s committed source is ready for the existing deployment workflow after
the production target and document root have been confirmed. GitHub `main` is
the source delivery destination. A push or pull does not activate the website.

Use the commit containing this handoff and `reports/LAUNCH_PHASE_3_QA.md`.
`git log -1` identifies it without embedding a self-referential commit hash.
The report and `reports/launch-phase3/verification.json` describe its tested
public package; compare the release manifest’s content digest before activation.

1. Pull the reviewed commit into the private checkout with a fast-forward update.
2. Run `python3 -B tools/build_release.py` and
   `python3 -B tools/build_release.py --check`. Packaging needs only Python 3.10+.
   Generated sharing images are committed; production checks their hashes and
   inputs without requiring Pillow or generating media.
3. Serve only `dist/release/public/` or publish it through the managed release
   store described in [RELEASE.md](RELEASE.md). The checkout and manifest stay private.
   New schema-3 runtime data is deliberate; strict schema-2 rollback is supported.
4. Once the actual hosting root is confirmed, follow the atomic publish/rollback
   procedure in that runbook. No hostname, SSH account, or server path is assumed.
5. Run `tools/check_release_http.py --base-url https://90s.land` against the exact
   package. It checks 533 routes, 192 sharing images, gzip samples, and excluded
   private paths. Revalidate HTML/CSS/JS/JSON and retain real 404 behavior.
6. Inspect home, a year, This Week, a story, an object, and the tour on production.
   Verify the deployed head metadata and content-specific sharing images, then
   check actual link previews with each platform’s current tooling. Crawlers may
   retain older cards until their caches refresh.

This Week needs no scheduled server job: the browser derives the equivalent
Monday–Sunday week from the New York civil date, refreshes an open default view,
and preserves explicitly selected dates. The no-JavaScript snapshot is labeled
with its build date. The historical archive remains limited to 1990–1999.

Known external verification limits are documented in the launch report. Avoid
deleting historical citations because of bot blocks, timeouts, or TLS failures.
Recheck the affected destinations independently when practical.
