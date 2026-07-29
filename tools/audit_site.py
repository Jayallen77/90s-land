#!/usr/bin/env python3
"""Static route, fragment, catalog, metadata, and media audit for 90s.land."""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]


class Document(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = []
        self.links = []
        self.images = []
        self.metas = []
        self.canonicals = []
        self.target_blank = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if values.get("id"):
            self.ids.append(values["id"])
        if tag in ("a", "area") and values.get("href"):
            self.links.append(values["href"])
            if values.get("target") == "_blank":
                self.target_blank.append(values)
        if tag == "img":
            self.images.append(values)
        if tag == "meta":
            self.metas.append(values)
        if tag == "link" and values.get("rel") == "canonical":
            self.canonicals.append(values.get("href"))


def route_file(path: str) -> Path:
    if path == "/":
        return ROOT / "index.html"
    return ROOT / path.strip("/") / "index.html"


def document(path: Path) -> Document:
    parsed = Document()
    parsed.feed(path.read_text(errors="replace"))
    return parsed


def target_file(url_path: str) -> Path:
    if url_path == "/":
        return ROOT / "index.html"
    candidate = ROOT / url_path.lstrip("/")
    if candidate.is_dir() or url_path.endswith("/"):
        candidate = candidate / "index.html"
    return candidate


def main() -> int:
    routes = json.loads((ROOT / "data/routes.json").read_text())
    artifacts = json.loads((ROOT / "data/artifacts.json").read_text())
    resources = json.loads((ROOT / "data/resources.json").read_text())
    tours = json.loads((ROOT / "data/tours.json").read_text())
    stamps = json.loads((ROOT / "data/stamps.json").read_text())
    errors = []
    docs = {}

    for route in routes:
        path = route_file(route["path"])
        if not path.is_file():
            errors.append(f"missing route: {route['path']}")
            continue
        docs[route["path"]] = document(path)

    internal_links = 0
    external_links = 0
    fragments = 0
    for route_path, parsed in docs.items():
        duplicates = [item for item, count in Counter(parsed.ids).items() if count > 1]
        if duplicates:
            errors.append(f"duplicate ids in {route_path}: {', '.join(duplicates)}")
        if len(parsed.canonicals) != 1:
            errors.append(f"canonical count in {route_path}: {len(parsed.canonicals)}")
        meta_keys = {item.get("property") or item.get("name") for item in parsed.metas}
        for required in (
            "description", "og:title", "og:description", "og:url",
            "twitter:title", "twitter:description"
        ):
            if required not in meta_keys:
                errors.append(f"missing {required} in {route_path}")
        for image in parsed.images:
            if not image.get("width") or not image.get("height"):
                errors.append(f"image lacks dimensions in {route_path}: {image.get('src')}")
            if image.get("src", "").startswith("/"):
                asset = ROOT / image["src"].lstrip("/")
                if not asset.is_file():
                    errors.append(f"missing image in {route_path}: {image['src']}")
        for link in parsed.target_blank:
            rel = set((link.get("rel") or "").split())
            if not {"noopener", "noreferrer"}.issubset(rel):
                errors.append(f"unsafe target=_blank in {route_path}: {link.get('href')}")

        for href in parsed.links:
            parts = urlsplit(href)
            if parts.scheme in ("http", "https"):
                external_links += 1
                continue
            if parts.scheme or href.startswith(("mailto:", "tel:", "javascript:")):
                continue
            internal_links += 1
            raw_path = unquote(parts.path)
            destination_path = raw_path or route_path
            if not destination_path.startswith("/"):
                destination_path = "/" + destination_path
            target = target_file(destination_path)
            if not target.is_file():
                errors.append(f"broken target from {route_path}: {href}")
                continue
            if parts.fragment:
                fragments += 1
                target_doc = docs.get(destination_path) or document(target)
                if unquote(parts.fragment) not in target_doc.ids:
                    errors.append(f"broken fragment from {route_path}: {href}")

    artifact_ids = {item["id"] for item in artifacts}
    route_paths = {item["path"] for item in routes}
    stamp_ids = {item["id"] for item in stamps}
    if len(artifacts) != 30 or len(artifact_ids) != 30:
        errors.append(f"artifact catalog expected 30 unique records, found {len(artifact_ids)}")
    if len(resources) != 78 or len({item["id"] for item in resources}) != 78:
        errors.append(f"resource catalog expected 78 unique records, found {len(resources)}")
    if sum(bool(item["featured"]) for item in resources) != 12:
        errors.append("resource catalog expected 12 featured references")
    required_artifact_fields = {
        "id", "slug", "dateRange", "room", "label", "curatorNote",
        "whyItMattered", "media", "relatedYears", "relatedArtifacts",
        "relatedRoutes", "target", "status", "randomEligible"
    }
    for item in artifacts:
        missing = required_artifact_fields - item.keys()
        if missing:
            errors.append(f"artifact {item.get('id')} missing {sorted(missing)}")
        target = urlsplit(item["target"])
        target_path = target.path
        if target_path not in route_paths:
            errors.append(f"artifact {item['id']} target route is uncataloged: {target_path}")
        elif target.fragment and target.fragment not in docs[target_path].ids:
            errors.append(f"artifact {item['id']} target fragment missing: {item['target']}")
        if item["status"] == "needs-source" and item["randomEligible"]:
            errors.append(f"needs-source artifact is Surprise eligible: {item['id']}")

    for tour in tours:
        if tour["completionStampId"] not in stamp_ids:
            errors.append(f"unknown completion stamp in {tour['id']}")
        for stop in tour["stops"]:
            unknown = set(stop["artifactIds"]) - artifact_ids
            if unknown:
                errors.append(f"unknown tour artifacts in {stop['id']}: {sorted(unknown)}")
            tour_doc = docs[f"/tours/{tour['slug']}/"]
            if stop["id"] not in tour_doc.ids:
                errors.append(f"tour stop fragment missing: {stop['id']}")

    webring = (ROOT / "webring/index.html").read_text()
    directory_match = re.search(
        r"<!-- generated:webring-directory:start -->(.*?)<!-- generated:webring-directory:end -->",
        webring,
        re.S,
    )
    directory_cards = (
        len(re.findall(r'class="resource-card"', directory_match.group(1)))
        if directory_match
        else 0
    )
    if directory_cards != len(resources):
        errors.append(f"Webring directory rendered {directory_cards}, expected {len(resources)}")

    guestbook = (ROOT / "guestbook/index.html").read_text()
    if "Preview my entry — not saved" not in guestbook or re.search(r"<form[^>]*\saction=", guestbook):
        errors.append("guestbook sandbox contract is missing")

    print(
        json.dumps(
            {
                "routes": len(routes),
                "internalLinks": internal_links,
                "externalLinks": external_links,
                "fragmentLinks": fragments,
                "artifacts": len(artifacts),
                "resources": len(resources),
                "featuredResourceReferences": sum(bool(item["featured"]) for item in resources),
                "errors": len(errors),
            },
            indent=2,
        )
    )
    if errors:
        print("\n".join(f"ERROR: {error}" for error in errors), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
