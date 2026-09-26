#!/usr/bin/env python3
"""Validate catalog relationships and the lossless, unverified Phase 1 import."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit

from content_model import BASELINE, MIGRATION, ROOT, Document, digest, plain_text, read_json, route_file


def load_array(path: Path, errors: list[str]):
    try:
        result = read_json(path)
        if not isinstance(result, list) or not all(isinstance(item, dict) for item in result):
            raise ValueError("expected an array of objects")
        return result
    except (OSError, ValueError) as error:
        errors.append(f"{path.name}: {error}")
        return []


def unique(records, label, errors, key="id"):
    values = [item.get(key) for item in records]
    if any(not isinstance(value, str) or not value.strip() for value in values):
        errors.append(f"{label}: {key} must be a nonempty string")
    valid = [value for value in values if isinstance(value, str)]
    repeated = [value for value, count in Counter(valid).items() if count > 1]
    if repeated:
        errors.append(f"{label}: duplicate {key}: {', '.join(repeated)}")
    return set(valid)


def required(record, fields, label, errors):
    for key, expected in fields.items():
        value = record.get(key)
        if not isinstance(value, expected) or (expected is int and isinstance(value, bool)):
            errors.append(f"{label}: {key} must be {expected.__name__}")


def validate_catalogs(root: Path = ROOT) -> list[str]:
    """Growth is allowed; baseline identities and existing relationships survive."""
    errors = []
    catalogs = {name: load_array(root / "data" / f"{name}.json", errors) for name in ("routes", "artifacts", "resources", "tours", "stamps")}
    ids = {name: unique(records, name, errors) for name, records in catalogs.items()}
    route_paths = unique(catalogs["routes"], "routes", errors, "path")
    schemas = {
        "routes": {"id": str, "path": str, "type": str, "title": str, "summary": str, "tags": list, "artifactIds": list, "randomEligible": bool},
        "artifacts": {"id": str, "slug": str, "title": str, "dateRange": dict, "room": str, "label": str, "curatorNote": str, "whyItMattered": str, "media": dict, "relatedYears": list, "relatedArtifacts": list, "relatedRoutes": list, "target": str, "status": str, "randomEligible": bool, "tags": list},
        "resources": {"id": str, "title": str, "url": str, "categoryId": str, "category": str, "tag": str, "description": str, "destinationType": str, "featured": bool},
        "tours": {"id": str, "slug": str, "title": str, "completionStampId": str, "stops": list},
        "stamps": {"id": str, "title": str, "description": str, "visual": str},
    }
    for name, records in catalogs.items():
        for record in records:
            required(record, schemas[name], f"{name}/{record.get('id', '?')}", errors)
    if errors:
        return errors
    for route in catalogs["routes"]:
        path = route["path"]
        if not path.startswith("/") or ".." in Path(path).parts or not path.endswith("/"):
            errors.append(f"route {route['id']}: expected an absolute directory URL")
        unknown = set(route["artifactIds"]) - ids["artifacts"]
        if unknown:
            errors.append(f"route {route['id']}: unknown artifacts {sorted(unknown)}")
    for item in catalogs["artifacts"]:
        label = f"artifact {item['id']}"
        if item["status"] not in {"verified", "editorial", "needs-source"}:
            errors.append(f"{label}: unsupported status")
        if item["status"] == "needs-source" and item["randomEligible"]:
            errors.append(f"{label}: needs-source artifact cannot be random eligible")
        date = item["dateRange"]
        required(date, {"startYear": int, "endYear": int, "label": str}, label + " dateRange", errors)
        if isinstance(date.get("startYear"), int) and isinstance(date.get("endYear"), int) and date["startYear"] > date["endYear"]:
            errors.append(f"{label}: date range is reversed")
        media = item["media"]
        required(media, {"kind": str, "alt": str, "credit": str, "license": str}, label + " media", errors)
        if media.get("kind") == "image":
            required(media, {"src": str, "width": int, "height": int, "sourceUrl": str}, label + " image", errors)
            src = media.get("src", "")
            if not isinstance(src, str) or not src.startswith("/") or ".." in Path(src).parts or not (root / src.lstrip("/")).is_file():
                errors.append(f"{label}: missing or invalid local image")
        elif media.get("kind") != "recreation":
            errors.append(f"{label}: unsupported media kind")
        if set(item["relatedArtifacts"]) - ids["artifacts"]:
            errors.append(f"{label}: unknown related artifact")
        if set(item["relatedRoutes"]) - route_paths:
            errors.append(f"{label}: unknown related route")
        if urlsplit(item["target"]).path not in route_paths:
            errors.append(f"{label}: unknown target route")
    for item in catalogs["resources"]:
        if urlsplit(item["url"]).scheme not in {"https", "http"}:
            errors.append(f"resource {item['id']}: expected an HTTP(S) URL")
    for tour in catalogs["tours"]:
        if tour["completionStampId"] not in ids["stamps"]:
            errors.append(f"tour {tour['id']}: unknown completion stamp")
        if not tour["stops"] or not all(isinstance(stop, dict) for stop in tour["stops"]):
            errors.append(f"tour {tour['id']}: expected nonempty stop records")
            continue
        unique(tour["stops"], f"tour {tour['id']} stops", errors)
        for stop in tour["stops"]:
            required(stop, {"id": str, "number": int, "title": str, "artifactIds": list, "exhibitHref": str}, f"tour {tour['id']} stop", errors)
            if isinstance(stop.get("artifactIds"), list) and set(stop["artifactIds"]) - ids["artifacts"]:
                errors.append(f"tour {tour['id']}: unknown stop artifact")
    try:
        baseline = read_json(root / BASELINE / "manifest.json")
        for name, current in catalogs.items():
            snapshot = root / baseline["catalogs"][name]["snapshot"]
            if digest(snapshot.read_bytes()) != baseline["catalogs"][name]["sha256"]:
                errors.append(f"{name}: preservation snapshot changed")
            original = read_json(snapshot)
            missing = {item["id"] for item in original} - ids[name]
            if missing:
                errors.append(f"{name}: baseline IDs removed: {', '.join(sorted(missing))}")
        missing_paths = {page["route"] for page in baseline["pages"] if page["id"] != "not-found"} - route_paths
        if missing_paths:
            errors.append(f"routes: baseline paths removed: {sorted(missing_paths)}")
        original_tours = read_json(root / baseline["catalogs"]["tours"]["snapshot"])
        current_tours = {tour["id"]: tour for tour in catalogs["tours"]}
        for tour in original_tours:
            current = current_tours.get(tour["id"])
            if current and {stop["id"] for stop in tour["stops"]} - {stop.get("id") for stop in current["stops"]}:
                errors.append(f"tour {tour['id']}: baseline stop IDs removed")
    except (OSError, ValueError, KeyError) as error:
        errors.append(f"Cannot validate preservation baseline: {error}")
    return errors


def load_migration(root: Path, errors: list[str]):
    datasets = {}
    for name in ("pages", "years", "months", "charts", "entities", "sources", "media", "inventory", "legacy-links"):
        try:
            data = read_json(root / MIGRATION / f"{name}.json")
            if not isinstance(data, dict) or data.get("schemaVersion") != 1 or data.get("kind") != name:
                raise ValueError("unsupported schemaVersion or catalog kind")
            records = data.get("records")
            if not isinstance(records, list) or not all(isinstance(record, dict) for record in records):
                raise ValueError("records must be an array of objects")
            unique(records, name, errors)
            datasets[name] = records
        except (OSError, ValueError) as error:
            errors.append(f"migration/{name}: {error}")
    return datasets


def validate_migration(root: Path = ROOT, *, baseline_unchanged=False) -> list[str]:
    errors = []
    data = load_migration(root, errors)
    if errors:
        return errors
    baseline = read_json(root / BASELINE / "manifest.json")
    original_pages = {page["id"]: page for page in baseline["pages"]}
    snapshots = {}
    for page in baseline["pages"]:
        path = root / page["snapshot"]
        if not path.is_file() or digest(path.read_bytes()) != page["sha256"]:
            errors.append(f"Snapshot changed or missing: {page['snapshot']}")
        else:
            snapshots[page["snapshot"]] = path.read_text(encoding="utf-8")
    for item in [*baseline["catalogs"].values(), *baseline["references"]]:
        relative = item.get("snapshot", item.get("file"))
        path = root / relative
        if not path.is_file() or digest(path.read_bytes()) != item["sha256"]:
            errors.append(f"Baseline fixture changed or missing: {relative}")
    if baseline_unchanged:
        for relative, expected in baseline["servedFileHashes"].items():
            path = root / relative
            if not path.is_file() or digest(path.read_bytes()) != expected:
                errors.append(f"Public baseline changed: {relative}")
    if errors:
        return errors

    schemas = {
        "pages": {"id": str, "route": str, "blocks": list, "mainRange": list, "verificationStatus": str},
        "years": {"id": str, "year": int, "route": str, "monthIds": list, "chartIds": list, "verificationStatus": str},
        "months": {"id": str, "kind": str, "year": int, "month": int, "datePrecision": str, "title": str, "paragraphs": list, "sourceIds": list, "provenance": dict, "verificationStatus": str},
        "charts": {"id": str, "year": int, "scope": str, "region": str, "entries": list, "sourceIds": list, "verificationStatus": str},
        "entities": {"id": str, "type": str, "title": str, "artistCredit": str, "sourceIds": list, "appearances": list, "verificationStatus": str},
        "sources": {"id": str, "url": str, "labels": list, "roles": list, "occurrences": list, "verificationStatus": str},
        "media": {"id": str, "src": str, "sha256": str, "bytes": int, "attributionClaims": list, "rightsStatus": str},
        "inventory": {"id": str, "pageId": str, "kind": str, "status": str, "currentDestination": str, "extractedRecord": dict},
        "legacy-links": {"id": str, "from": str, "to": str, "pageId": str, "owner": str, "status": str},
    }
    for name, records in data.items():
        for record in records:
            required(record, schemas[name], f"{name}/{record.get('id', '?')}", errors)
    if errors:
        return errors

    ids = {name: {item["id"] for item in records} for name, records in data.items()}

    def check_provenance(value, label):
        required(value, {"snapshot": str, "start": int, "end": int, "sha256": str, "lineStart": int, "lineEnd": int}, label, errors)
        source = snapshots.get(value.get("snapshot"))
        start, end = value.get("start"), value.get("end")
        if source is None or type(start) is not int or type(end) is not int or not 0 <= start < end <= len(source):
            errors.append(f"{label}: invalid source range")
            return ""
        raw = source[start:end]
        if digest(raw) != value.get("sha256"):
            errors.append(f"{label}: source slice fingerprint differs")
        if value.get("lineStart") != source.count("\n", 0, start) + 1 or value.get("lineEnd") != source.count("\n", 0, end - 1) + 1:
            errors.append(f"{label}: incorrect source line range")
        return raw

    block_ids = []
    if ids["pages"] != set(original_pages):
        errors.append("pages: extracted page inventory differs from baseline")
    for page in data["pages"]:
        original = original_pages.get(page["id"])
        if not original:
            continue
        cursor, expected_end = original["mainRange"]
        if page["mainRange"] != original["mainRange"]:
            errors.append(f"{page['id']}: main range changed")
        for block in page["blocks"]:
            required(block, {"id": str, "text": str, "paragraphs": list, "links": list, "images": list, "sourceIds": list, "provenance": dict}, page["id"] + " block", errors)
            if not isinstance(block.get("provenance"), dict):
                continue
            location = block["provenance"]
            raw = check_provenance(location, block.get("id", "block"))
            if location.get("start") != cursor:
                errors.append(f"{page['id']}: gap or overlap in main-content coverage")
            cursor = location.get("end")
            if block.get("text") != plain_text(raw):
                errors.append(f"{block.get('id')}: extracted text differs from frozen source")
            block_ids.append(block.get("id"))
            if set(block.get("sourceIds", [])) - ids["sources"]:
                errors.append(f"{block.get('id')}: unknown source reference")
        if cursor != expected_end:
            errors.append(f"{page['id']}: incomplete main-content coverage")
    if len(set(block_ids)) != len(block_ids) or set(block_ids) != ids["inventory"]:
        errors.append("inventory: every source block must have exactly one disposition")
    for item in data["inventory"]:
        target = item["extractedRecord"]
        if item["pageId"] not in ids["pages"] or target.get("id") not in ids.get(target.get("catalog"), set()):
            errors.append(f"inventory {item['id']}: unresolved extracted destination")
        if item["status"] != "preserved-awaiting-curation":
            errors.append(f"inventory {item['id']}: import cannot claim completed curation")

    expected_anchors = {page["route"] + "#" + anchor for page in baseline["pages"] for anchor in page["anchors"]}
    actual_anchors = [item["from"] for item in data["legacy-links"]]
    if set(actual_anchors) != expected_anchors or len(actual_anchors) != len(expected_anchors):
        errors.append("legacy-links: missing or duplicate baseline anchors")
    for item in data["legacy-links"]:
        if item["to"] != item["from"] or item["pageId"] not in ids["pages"] or item.get("blockId") not in {None, *block_ids}:
            errors.append(f"legacy-links {item['id']}: invalid initial preservation mapping")

    expected_periods = set()
    for page in baseline["pages"]:
        if page["type"] == "years":
            year = int(page["route"].strip("/").split("/")[-1])
            doc = Document(snapshots[page["snapshot"]])
            expected_periods.update((year, month) for month, _ in enumerate(doc.nodes(lambda node: node.has_class("month-card")), 1))
    actual_periods = [(item["year"], item["month"]) for item in data["months"]]
    if set(actual_periods) != expected_periods or len(set(actual_periods)) != len(actual_periods):
        errors.append("months: baseline month coverage differs")
    for item in data["months"]:
        if item["kind"] != "monthly-context" or item["datePrecision"] != "month" or "date" in item:
            errors.append(f"{item['id']}: monthly context must not invent an exact event date")
        raw = check_provenance(item["provenance"], item["id"])
        source_card = Document(raw)
        headings = source_card.nodes(lambda node: node.tag in {"h1", "h2", "h3", "h4", "h5", "h6"})
        paragraphs = [source_card.text(node) for node in source_card.nodes(lambda node: node.tag == "p")]
        if not headings or item["title"] != source_card.text(headings[0]) or item["paragraphs"] != paragraphs:
            errors.append(f"{item['id']}: imported text differs from source")
    expected_years = {year for year, _ in expected_periods}
    if {item["year"] for item in data["years"]} != expected_years or len(data["years"]) != len(expected_years):
        errors.append("years: baseline year coverage differs")
    if {item["year"] for item in data["charts"]} != expected_years or len(data["charts"]) != len(expected_years):
        errors.append("charts: baseline year coverage differs")
    for item in data["years"]:
        if set(item["monthIds"]) - ids["months"] or set(item["chartIds"]) - ids["charts"]:
            errors.append(f"{item['id']}: broken month/chart relationship")
        if item["monthIds"] != [month["id"] for month in data["months"] if month["year"] == item["year"]]:
            errors.append(f"{item['id']}: month sequence differs")
    for chart in data["charts"]:
        if chart["scope"] != "year-end" or not chart["sourceIds"]:
            errors.append(f"{chart['id']}: preserve annual scope and source trail")
        ranks = [entry.get("rank") for entry in chart["entries"]]
        if ranks != list(range(1, len(ranks) + 1)):
            errors.append(f"{chart['id']}: ranks must be ordered and unique")
        page = original_pages.get(f"timeline-{chart['year']}")
        if page:
            doc = Document(snapshots[page["snapshot"]])
            expected_count = len(doc.nodes(lambda node: node.has_class("song-card")))
            if len(chart["entries"]) != expected_count:
                errors.append(f"{chart['id']}: baseline chart positions lost")
        for entry in chart["entries"]:
            if entry.get("entityId") not in ids["entities"]:
                errors.append(f"{chart['id']}: unknown song entity")
            if isinstance(entry.get("provenance"), dict):
                raw = check_provenance(entry["provenance"], chart["id"])
                card = Document(raw)
                title = card.nodes(lambda node: node.tag == "h3")
                credit = card.nodes(lambda node: node.tag == "p")
                if not title or not credit or entry.get("titleAsPublished") != card.text(title[0]) or entry.get("artistCreditAsPublished") != card.text(credit[0]):
                    errors.append(f"{chart['id']}: original song credit changed")
            else:
                errors.append(f"{chart['id']}: missing entry provenance")
    for name in ("years", "months", "charts", "entities", "sources", "pages"):
        for item in data[name]:
            if item["verificationStatus"] != "unreviewed":
                errors.append(f"{name}/{item['id']}: imported claims must remain unreviewed")
            if name in {"months", "charts", "entities"} and item.get("publicationStatus") != "imported-draft":
                errors.append(f"{name}/{item['id']}: imported material must remain a draft")
            if set(item.get("sourceIds", [])) - ids["sources"]:
                errors.append(f"{name}/{item['id']}: unknown source")
    for source in data["sources"]:
        if urlsplit(source["url"]).scheme not in {"http", "https"} or source.get("verifiedAt") is not None:
            errors.append(f"{source['id']}: invalid imported source")
    appearances = {(entry["entityId"], chart["id"], entry["rank"]) for chart in data["charts"] for entry in chart["entries"]}
    entity_appearances = {(entity["id"], appearance.get("chartId"), appearance.get("rank")) for entity in data["entities"] for appearance in entity["appearances"]}
    if appearances != entity_appearances:
        errors.append("entities: song/chart appearance relationships differ")
    if {item["src"].lstrip("/") for item in data["media"]} != {path for path in baseline["assetSizes"] if path.startswith("assets/media/")}:
        errors.append("media: baseline editorial asset inventory differs")
    for media in data["media"]:
        relative = media["src"].lstrip("/")
        if baseline["servedFileHashes"].get(relative) != media["sha256"]:
            errors.append(f"{media['id']}: media fingerprint differs")
        if media["rightsStatus"] not in {"recorded-unverified", "needs-review"}:
            errors.append(f"{media['id']}: import cannot establish image rights")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-unchanged", action="store_true", help="Phase 1 only: compare every original served file byte for byte")
    args = parser.parse_args()
    try:
        errors = validate_catalogs() + validate_migration(baseline_unchanged=args.baseline_unchanged)
    except (OSError, ValueError, KeyError, TypeError) as error:
        errors = [f"Invalid content structure: {error}"]
    print(json.dumps({"errors": len(errors), "baselineUnchangedChecked": args.baseline_unchanged}, indent=2))
    for error in errors:
        print("ERROR:", error)
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
