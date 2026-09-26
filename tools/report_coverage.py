#!/usr/bin/env python3
"""Report preserved material separately from publishable, verified archive depth."""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path

from content_model import BASELINE, MIGRATION, ROOT, json_text, read_json


def build_report(root: Path = ROOT):
    baseline = read_json(root / BASELINE / "manifest.json")
    names = ("pages", "years", "months", "charts", "entities", "sources", "media", "inventory", "legacy-links")
    data = {name: read_json(root / MIGRATION / f"{name}.json")["records"] for name in names}
    missing_attribution = [item["src"] for item in data["media"] if not item["attributionClaims"]]
    vague_licenses = [claim for item in data["media"] for claim in item["attributionClaims"] if claim["license"] == "See source page"]
    no_links = [item["id"] for item in data["months"] if not item["sourceIds"]]
    years = [{"year": year["year"], "monthlySummaries": sum(item["year"] == year["year"] for item in data["months"]), "annualChartPositions": sum(len(chart["entries"]) for chart in data["charts"] if chart["year"] == year["year"]), "verifiedDatedEvents": 0} for year in data["years"]]
    report = {
        "schemaVersion": 1, "baselineRevision": baseline["revision"],
        "scope": "Phase 1 preservation and extraction; no historical verification or new articles",
        "counts": {
            "publicRoutes": sum(page["id"] != "not-found" for page in data["pages"]),
            "snapshottedDocuments": len(data["pages"]),
            "preservedAnchors": len(data["legacy-links"]),
            "sourceBlocks": len(data["inventory"]),
            "monthlySummaries": len(data["months"]),
            "annualCharts": len(data["charts"]),
            "annualChartPositions": sum(len(chart["entries"]) for chart in data["charts"]),
            "distinctSongCredits": len(data["entities"]),
            "uniqueExternalLinks": len(data["sources"]),
            "mediaFiles": len(data["media"]),
            "preservedArtifacts": baseline["catalogs"]["artifacts"]["count"],
            "preservedResources": baseline["catalogs"]["resources"]["count"],
        },
        "blockKinds": dict(sorted(Counter(row["kind"] for row in data["inventory"]).items())),
        "years": years,
        "reviewQueue": {
            "unreviewedMonthlySummaries": [item["id"] for item in data["months"]],
            "monthlySummariesWithoutExternalLinks": no_links,
            "unverifiedAnnualCharts": [item["id"] for item in data["charts"]],
            "ambiguousArtifactLicenses": vague_licenses,
            "mediaWithoutStructuredArtifactAttribution": missing_attribution,
            "note": "An external link is a source candidate, not evidence that a claim or image license has been verified. Image references and search/discovery links are separately labeled.",
        },
        "futureLaunchTargets": {"completeStories": 30, "verifiedDatedEvents": 300, "weeklyFocusYear": 1996},
        "publishedByThisPhase": {"completeStories": 0, "verifiedDatedEvents": 0},
    }
    lines = [
        "# Phase 1 — Content preservation and migration inventory", "",
        f"Baseline: `{baseline['revision']}`. This report is generated from frozen source snapshots.", "",
        "The current presentation remains unchanged. The import is review-only material; it does not claim new historical verification, publish new stories, or feed the public site.", "",
        "## Preserved material", "", "| Material | Count |", "|---|---:|",
    ]
    labels = {"publicRoutes": "Public routes", "snapshottedDocuments": "HTML snapshots including 404", "preservedAnchors": "Existing anchors", "sourceBlocks": "Losslessly indexed main-content blocks", "monthlySummaries": "Monthly summaries", "annualCharts": "Annual chart collections", "annualChartPositions": "Annual chart positions", "distinctSongCredits": "Distinct song/artist-credit combinations", "uniqueExternalLinks": "Unique external link candidates", "mediaFiles": "Editorial media files", "preservedArtifacts": "Existing artifact records", "preservedResources": "Existing external-resource records"}
    lines.extend(f"| {labels[key]} | {value} |" for key, value in report["counts"].items())
    lines += ["", "Source blocks include page introductions, editorial sections, chart rows, generated catalog mirrors, and supporting-page material. They are not a count of unique articles.", "", "## Year coverage", "", "| Year | Month summaries | Annual chart positions | Newly verified dated events |", "|---|---:|---:|---:|"]
    lines.extend(f"| {item['year']} | {item['monthlySummaries']} | {item['annualChartPositions']} | 0 |" for item in years)
    lines += ["", "## Page inventory", "", "Every block has a disposition in `content/migration/inventory.json`, a source range/fingerprint, and an extracted-record destination. The full anchor map is in `content/migration/legacy-links.json`.", "", "| Page | Blocks | Intended use |", "|---|---:|---|"]
    for page in data["pages"]:
        purpose = "Year context, monthly summaries, annual charts, story candidates" if page["type"] == "years" else "Category introductions and story/collection candidates" if page["type"] == "zones" else "Preserve supporting page and existing features"
        lines.append(f"| `{page['route']}` | {len(page['blocks'])} | {purpose} |")
    lines += ["", "## Review queue", "",
        f"- All {len(data['months'])} monthly summaries and {len(data['charts'])} annual charts await fact/source review.",
        f"- {len(no_links)} monthly summaries have no external link inside their source card; their internal navigation is preserved.",
        "- No monthly summary has been converted into an exact-day historical event.",
        "- Song identities preserve original artist-credit strings; collaborations have not been invented as standalone artist entities.",
        "- No imported external URL has been live-checked by this migration.",
        f"- {len(missing_attribution)} media files have no attribution claim in the existing structured artifact catalog. Their page occurrences and original caption/source text remain available in the snapshots and source blocks.",
        f"- {len(vague_licenses)} existing artifact media entries have a non-specific license label:", ""]
    lines.extend(f"  - `{claim['artifactId']}` — `{claim['license']}`; retain the original source URL for review." for claim in vague_licenses)
    lines += ["", "## Phase boundary", "",
        "Phase 1 finishes preservation, extraction, schema/relationship validation, and baseline QA. The later editorial launch still requires 30 complete stories and at least 300 sourced dated events, including the agreed 1996 weekly coverage. Imported summaries and chart positions do not count toward those targets.", "",
        "## Reproduce", "", "```sh", "python3 tools/migrate_content.py --check", "python3 tools/validate_content.py --baseline-unchanged", "python3 tools/report_coverage.py --check", "node tools/capture_baseline.mjs --check", "```", "",
    ]
    return {Path("reports/phase-1-coverage.json"): json_text(report), Path("reports/PHASE_1_MIGRATION.md"): "\n".join(lines)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    changed = []
    for relative, text in build_report().items():
        path = ROOT / relative
        if not path.exists() or path.read_text(encoding="utf-8") != text:
            changed.append(str(relative))
            if not args.check:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text, encoding="utf-8")
    if args.check and changed:
        print("Coverage report drift:\n" + "\n".join(changed))
        return 1
    print("Coverage report is current" if args.check else "Wrote Phase 1 migration report and review queue")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
