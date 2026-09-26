#!/usr/bin/env python3
"""Capture an immutable baseline, then extract review-only content from it.

This command never edits public HTML, CSS, JavaScript, or existing catalogs.
Normal/check runs read the frozen snapshots, not changing rendered pages.
"""

from __future__ import annotations

import argparse
import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

from content_model import (
    BASELINE, HEADINGS, MIGRATION, ROOT, Document, digest, json_text,
    plain_text, provenance, read_json, route_file, source_id,
)

CATALOGS = ("routes", "artifacts", "resources", "tours", "stamps", "navigation")
REVIEW = "unreviewed"


def envelope(kind, records):
    return {"schemaVersion": 1, "kind": kind, "records": records}


def capture_baseline(root: Path, revision: str, references: list[str]) -> None:
    destination = root / BASELINE
    if destination.exists():
        raise ValueError(f"Baseline already exists; refusing to replace {BASELINE}")
    if not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise ValueError("--revision must be the full baseline commit SHA")
    if len(references) != 3 or not all(Path(value).is_file() for value in references):
        raise ValueError("Provide the three existing Home, Timeline, Games reference files")
    catalogs = {name: read_json(root / "data" / f"{name}.json") for name in CATALOGS}
    routes = catalogs["routes"] + [{"id": "not-found", "path": "/404.html", "title": "404", "type": "utility"}]
    manifest = {
        "schemaVersion": 1,
        "revision": revision,
        "capturedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "offsetUnit": "unicode-code-points",
        "pages": [], "catalogs": {}, "servedFileHashes": {}, "assetSizes": {}, "references": [],
    }
    outputs = {}
    for route in routes:
        relative = Path("404.html") if route["id"] == "not-found" else route_file(route["path"])
        raw = (root / relative).read_bytes()
        source = raw.decode("utf-8")
        doc = Document(source)
        main = doc.one(lambda node: node.tag == "main")
        snapshot = BASELINE / "pages" / f"{route['id']}.html.txt"
        outputs[snapshot] = raw
        manifest["pages"].append({
            "id": route["id"], "route": route["path"], "title": route["title"],
            "type": route["type"], "file": str(relative), "snapshot": str(snapshot),
            "sha256": digest(raw), "mainRange": [main.inner_start, main.inner_end],
            "anchors": [node.attrs["id"] for node in doc.nodes(lambda node: bool(node.attrs.get("id")))],
            "headings": [{"level": int(node.tag[1]), "text": doc.text(node)} for node in doc.nodes(lambda node: node.tag in HEADINGS)],
            "links": [node.attrs["href"] for node in doc.nodes(lambda node: node.tag in {"a", "area"} and bool(node.attrs.get("href")))],
        })
        manifest["servedFileHashes"][str(relative)] = digest(raw)
    for name, records in catalogs.items():
        relative = Path("data") / f"{name}.json"
        raw = (root / relative).read_bytes()
        snapshot = BASELINE / "catalogs" / f"{name}.json"
        outputs[snapshot] = raw
        manifest["catalogs"][name] = {"snapshot": str(snapshot), "sha256": digest(raw), "count": len(records)}
        manifest["servedFileHashes"][str(relative)] = digest(raw)
    served_files = [root / name for name in ("styles.css", "sitemap.xml", "robots.txt", "manifest.webmanifest")]
    served_files += [path for folder in ("assets", "js") for path in (root / folder).rglob("*") if path.is_file()]
    for path in sorted(served_files):
        manifest["servedFileHashes"][str(path.relative_to(root))] = digest(path.read_bytes())
        if path.is_relative_to(root / "assets"):
            manifest["assetSizes"][str(path.relative_to(root))] = path.stat().st_size
    for name, original in zip(("home", "timeline", "games"), references):
        target = Path("docs/design/references") / f"{name}.jpeg"
        raw = Path(original).read_bytes()
        if (root / target).exists() and (root / target).read_bytes() != raw:
            raise ValueError(f"Refusing to overwrite existing reference {target}")
        outputs[target] = raw
        manifest["references"].append({"id": name, "file": str(target), "sha256": digest(raw)})
    outputs[BASELINE / "manifest.json"] = json_text(manifest).encode()
    for relative, raw in outputs.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)


def link_role(url: str, node) -> str:
    if any(part in url for part in ("/results?search_query=", "open.spotify.com/search/")):
        return "listen-search"
    if "Special:Search" in url or "search_query=" in url or "google.com/search" in url:
        return "discovery-search"
    if node.closest(lambda parent: parent.tag == "figure") or "commons.wikimedia.org/wiki/File:" in url:
        return "media-reference"
    return "reference-candidate"


def normalized_song_key(title: str, artist: str) -> str:
    value = unicodedata.normalize("NFKD", title + "\n" + artist).casefold()
    return "".join(char for char in value if not unicodedata.combining(char))


def extract(root: Path) -> dict[Path, str]:
    baseline = read_json(root / BASELINE / "manifest.json")
    source_records, page_records, inventory, months, charts, years, songs = {}, [], [], [], [], [], {}
    documents = {}
    snapshots = {}
    blocks_by_page = {}
    legacy_links = []

    for page in baseline["pages"]:
        source = (root / page["snapshot"]).read_text(encoding="utf-8")
        if digest(source) != page["sha256"]:
            raise ValueError(f"Snapshot changed: {page['snapshot']}")
        snapshots[page["id"]] = source
        doc = documents[page["id"]] = Document(source)
        main = doc.one(lambda node: node.tag == "main")
        all_nodes = doc.nodes()
        for node in all_nodes:
            url = node.attrs.get("href", "")
            if node.tag != "a" or urlsplit(url).scheme not in {"http", "https"}:
                continue
            sid = source_id(url)
            item = source_records.setdefault(sid, {"id": sid, "url": url, "labels": [], "roles": [], "verificationStatus": REVIEW, "verifiedAt": None, "occurrences": []})
            label = doc.text(node)
            role = link_role(url, node)
            if label and label not in item["labels"]:
                item["labels"].append(label)
            if role not in item["roles"]:
                item["roles"].append(role)
            item["occurrences"].append({"pageId": page["id"], "line": source.count("\n", 0, node.start) + 1, "role": role})

        headings = [node for node in main.walk() if node.tag in HEADINGS]
        boundaries = sorted(set([main.inner_start, *(node.start for node in headings), main.inner_end]))
        heading_by_start = {node.start: node for node in headings}
        blocks = []
        for index, (start, end) in enumerate(zip(boundaries, boundaries[1:]), 1):
            heading = heading_by_start.get(start)
            owner = heading.closest(lambda node: bool(node.attrs.get("id"))) if heading else main
            anchor = owner.attrs.get("id") if owner else None
            nodes = [node for node in all_nodes if start <= node.start < end]
            links = [{"label": doc.text(node), "href": node.attrs["href"]} for node in nodes if node.tag == "a" and node.attrs.get("href")]
            kind = "editorial"
            if heading and heading.closest(lambda node: node.has_class("month-card")):
                kind = "month-summary"
            elif heading and heading.closest(lambda node: node.has_class("song-card")):
                kind = "chart-entry"
            elif heading and heading.closest(lambda node: bool(node.attrs.get("data-artifact-id"))):
                kind = "artifact-mirror"
            elif page["type"] not in {"years", "zones"}:
                kind = "supporting-page"
            block_id = f"legacy-{page['id']}-{index:04d}"
            block = {
                "id": block_id, "kind": kind,
                "heading": doc.text(heading) if heading else None,
                "headingLevel": int(heading.tag[1]) if heading else None,
                "text": plain_text(source[start:end]),
                "paragraphs": [doc.text(node) for node in nodes if node.tag == "p" and node.end <= end],
                "links": links,
                "images": [{key: node.attrs[key] for key in ("src", "alt", "width", "height") if key in node.attrs} for node in nodes if node.tag == "img"],
                "sourceIds": sorted({source_id(link["href"]) for link in links if urlsplit(link["href"]).scheme in {"http", "https"}}),
                "provenance": provenance(page["snapshot"], source, start, end),
            }
            blocks.append(block)
            inventory.append({
                "id": block_id, "pageId": page["id"], "heading": block["heading"],
                "kind": kind, "status": "preserved-awaiting-curation",
                "currentDestination": page["route"] + (f"#{anchor}" if anchor else ""),
                "extractedRecord": {"catalog": "pages", "id": page["id"], "blockId": block_id},
                "plannedUse": "year-context" if page["type"] == "years" else "category-editorial" if page["type"] == "zones" else "preserve-supporting-page",
            })
        blocks_by_page[page["id"]] = blocks
        page_records.append({"id": page["id"], "route": page["route"], "type": page["type"], "title": page["title"], "verificationStatus": REVIEW, "mainRange": page["mainRange"], "blocks": blocks})
        for node in all_nodes:
            if not node.attrs.get("id"):
                continue
            block = next((block for block in blocks if block["provenance"]["start"] <= node.start < block["provenance"]["end"]), None)
            legacy_links.append({"id": f"anchor-{page['id']}-{node.attrs['id']}", "from": page["route"] + "#" + node.attrs["id"], "to": page["route"] + "#" + node.attrs["id"], "pageId": page["id"], "blockId": block["id"] if block else None, "owner": "main-content" if main.start <= node.start < main.end else "shared-ui", "status": "preserve"})

    def source_ids(node):
        return sorted({source_id(child.attrs["href"]) for child in node.walk() if child.tag == "a" and urlsplit(child.attrs.get("href", "")).scheme in {"http", "https"}})

    def link_data(doc, node):
        return [{"label": doc.text(child), "href": child.attrs["href"]} for child in node.walk() if child.tag == "a" and child.attrs.get("href")]

    def locate(page, node):
        return provenance(page["snapshot"], snapshots[page["id"]], node.start, node.end)

    def associate(page, node, catalog, record_id):
        for row in inventory:
            if row["pageId"] != page["id"]:
                continue
            block = next(block for block in blocks_by_page[page["id"]] if block["id"] == row["id"])
            if node.start <= block["provenance"]["start"] < node.end:
                row["extractedRecord"] = {"catalog": catalog, "id": record_id}
                row["plannedUse"] = catalog

    for page in baseline["pages"]:
        if page["type"] != "years":
            continue
        year = int(page["route"].strip("/").split("/")[-1])
        doc = documents[page["id"]]
        year_months = []
        for month, card in enumerate(doc.nodes(lambda node: node.has_class("month-card")), 1):
            title = next(node for node in card.walk() if node.tag in HEADINGS)
            record_id = f"month-{year}-{month:02d}"
            months.append({
                "id": record_id, "kind": "monthly-context", "year": year, "month": month,
                "datePrecision": "month", "title": doc.text(title),
                "paragraphs": [doc.text(node) for node in card.walk() if node.tag == "p"],
                "links": link_data(doc, card), "sourceIds": source_ids(card),
                "verificationStatus": REVIEW, "publicationStatus": "imported-draft",
                "legacyHref": page["route"] + "#" + card.attrs["id"],
                "provenance": locate(page, card),
            })
            year_months.append(record_id)
            associate(page, card, "months", record_id)
        chart_node = doc.one(lambda node: node.attrs.get("id") == "top-songs")
        chart_id = f"billboard-year-end-hot-100-{year}-top-10"
        chart_sources = [source_id(link["href"]) for link in link_data(doc, chart_node) if "Billboard_Year-End_Hot_100" in link["href"]]
        entries = []
        for card in (node for node in chart_node.walk() if node.has_class("song-card")):
            title_node = next(node for node in card.walk() if node.tag == "h3")
            rank_node = next(node for node in card.walk() if node.has_class("chart-rank"))
            paragraphs = [node for node in card.walk() if node.tag == "p"]
            title, artist = doc.text(title_node), doc.text(paragraphs[0])
            rank = int(re.search(r"\d+", doc.text(rank_node)).group())
            key = normalized_song_key(title, artist)
            song_id = "song-" + digest(key)[:16]
            song = songs.setdefault(song_id, {"id": song_id, "type": "song", "title": title, "artistCredit": artist, "verificationStatus": REVIEW, "publicationStatus": "imported-draft", "sourceIds": [], "appearances": []})
            song["appearances"].append({"chartId": chart_id, "rank": rank})
            song["sourceIds"] = sorted(set(song["sourceIds"] + chart_sources))
            entries.append({"rank": rank, "entityId": song_id, "titleAsPublished": title, "artistCreditAsPublished": artist, "editorialNote": " ".join(doc.text(node) for node in paragraphs[1:]), "links": link_data(doc, card), "provenance": locate(page, card)})
            associate(page, card, "charts", chart_id)
        charts.append({"id": chart_id, "title": f"Billboard Year-End Hot 100: Top 10 of {year}", "year": year, "scope": "year-end", "region": "US", "sourceIds": sorted(set(chart_sources)), "verificationStatus": REVIEW, "publicationStatus": "imported-draft", "legacyHref": page["route"] + "#top-songs", "entries": entries})
        years.append({"id": f"year-{year}", "year": year, "title": page["title"], "route": page["route"], "pageId": page["id"], "monthIds": year_months, "chartIds": [chart_id], "verificationStatus": REVIEW})

    # Preserve image attribution claims as claims, including unresolved labels.
    artifacts = read_json(root / baseline["catalogs"]["artifacts"]["snapshot"])
    media = []
    for relative in sorted(key for key in baseline["assetSizes"] if key.startswith("assets/media/")):
        src = "/" + relative
        claims = [{"artifactId": item["id"], "credit": item["media"].get("credit"), "sourceUrl": item["media"].get("sourceUrl"), "license": item["media"].get("license")} for item in artifacts if item["media"].get("src") == src]
        occurrences = [{"pageId": page["id"], "alt": node.attrs.get("alt", ""), "line": snapshots[page["id"]].count("\n", 0, node.start) + 1} for page in baseline["pages"] for node in documents[page["id"]].nodes(lambda node: node.tag == "img" and node.attrs.get("src") == src)]
        unresolved = not claims or any(not claim["license"] or claim["license"] == "See source page" for claim in claims)
        media.append({"id": "media-" + digest(src)[:16], "src": src, "sha256": baseline["servedFileHashes"][relative], "bytes": baseline["assetSizes"][relative], "attributionClaims": claims, "occurrences": occurrences, "rightsStatus": "needs-review" if unresolved else "recorded-unverified"})
    datasets = {"pages": page_records, "years": years, "months": months, "charts": charts, "entities": sorted(songs.values(), key=lambda song: song["id"]), "sources": sorted(source_records.values(), key=lambda source: source["id"]), "media": media, "inventory": inventory, "legacy-links": legacy_links}
    return {MIGRATION / f"{name}.json": json_text(envelope(name, records)) for name, records in datasets.items()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capture-baseline", action="store_true")
    parser.add_argument("--revision")
    parser.add_argument("--references", nargs=3, metavar=("HOME", "TIMELINE", "GAMES"))
    parser.add_argument("--check", action="store_true", help="compare extraction without writing")
    args = parser.parse_args()
    try:
        if args.capture_baseline:
            if args.check:
                parser.error("--check cannot capture a baseline")
            capture_baseline(ROOT, args.revision or "", args.references or [])
        outputs = extract(ROOT)
        changed = []
        for relative, expected in outputs.items():
            path = ROOT / relative
            if not path.exists() or path.read_text(encoding="utf-8") != expected:
                changed.append(str(relative))
                if not args.check:
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text(expected, encoding="utf-8")
        if args.check and changed:
            print("Migration extraction drift:\n" + "\n".join(changed))
            return 1
        print(f"Migration extraction {'matches frozen source' if args.check else 'complete'}: {len(outputs)} catalogs; {len(changed)} changed")
        return 0
    except (ValueError, OSError, KeyError) as error:
        print(f"ERROR: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
