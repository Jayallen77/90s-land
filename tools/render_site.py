#!/usr/bin/env python3
"""Render data-backed static regions without replacing authored long-form copy."""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
SITE_URL = "https://90s.land"


def load_json(name: str):
    return json.loads((ROOT / "data" / name).read_text())


ARTIFACTS = load_json("artifacts.json")
NAVIGATION = load_json("navigation.json")
RESOURCES = load_json("resources.json")
ROUTES = load_json("routes.json")
STAMPS = load_json("stamps.json")
TOURS = load_json("tours.json")

ARTIFACT_BY_ID = {item["id"]: item for item in ARTIFACTS}
ROUTE_BY_PATH = {item["path"]: item for item in ROUTES}
STAMP_BY_ID = {item["id"]: item for item in STAMPS}


def esc(value) -> str:
    return html.escape(str(value), quote=True)


def region(name: str, content: str) -> str:
    return (
        f"<!-- generated:{name}:start -->\n"
        f"{content.rstrip()}\n"
        f"<!-- generated:{name}:end -->"
    )


def replace_region(source: str, name: str, content: str) -> tuple[str, bool]:
    block = region(name, content)
    pattern = re.compile(
        rf"<!-- generated:{re.escape(name)}:start -->.*?"
        rf"<!-- generated:{re.escape(name)}:end -->",
        re.S,
    )
    if pattern.search(source):
        return pattern.sub(block, source, count=1), True
    return source, False


def route_to_file(path: str) -> Path:
    if path == "/":
        return ROOT / "index.html"
    return ROOT / path.strip("/") / "index.html"


def route_room(route: dict) -> str:
    path = route["path"]
    if path.startswith("/zones/"):
        return path.strip("/").split("/")[1]
    if path.startswith("/timeline/") and path != "/timeline/":
        return f'timeline-{path.strip("/").split("/")[1]}'
    if route["type"] == "tours":
        return "tour"
    return route["type"]


def render_navigation() -> str:
    links = "\n".join(
        f'      <a href="{esc(item["href"])}">{esc(item["label"])}</a>'
        for item in NAVIGATION
    )
    return f"""    <nav class="nav" id="siteNav" aria-label="Museum navigation">
{links}
      <div class="museum-toolbelt" aria-label="Museum tools">
        <a class="museum-tool surprise-tool" href="/surprise/" data-surprise-trigger>Surprise me</a>
        <button class="museum-tool passport-tool" type="button" data-passport-trigger hidden>
          Passport <span data-passport-count aria-hidden="true">0</span>
        </button>
      </div>
    </nav>"""


def render_head(route: dict) -> str:
    if route["path"] == "/":
        title = "90s.land — A playable museum of the 1990s"
    else:
        title = f'{route["title"]} — 90s.land'
    description = route["summary"]
    canonical = f'{SITE_URL}{route["path"]}'
    image_meta = ""
    if (ROOT / "assets/generated/og-card.png").exists():
        image_meta = f"""
  <meta property="og:image" content="{SITE_URL}/assets/generated/og-card.png" />
  <meta property="og:image:width" content="1200" />
  <meta property="og:image:height" content="630" />
  <meta property="og:image:alt" content="90s.land playable museum lobby in neon CRT colors." />
  <meta name="twitter:image" content="{SITE_URL}/assets/generated/og-card.png" />"""
    return f"""  <meta name="description" content="{esc(description)}" />
  <title>{esc(title)}</title>
  <link rel="canonical" href="{canonical}" />
  <meta property="og:type" content="website" />
  <meta property="og:site_name" content="90s.land" />
  <meta property="og:title" content="{esc(title)}" />
  <meta property="og:description" content="{esc(description)}" />
  <meta property="og:url" content="{canonical}" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{esc(title)}" />
  <meta name="twitter:description" content="{esc(description)}" />{image_meta}
  <link rel="preload" href="/assets/fonts/space-mono-regular.woff2" as="font" type="font/woff2" crossorigin />
  <link rel="preload" href="/assets/fonts/space-mono-bold.woff2" as="font" type="font/woff2" crossorigin />
  <link rel="preload" href="/assets/fonts/press-start-2p-regular.woff2" as="font" type="font/woff2" crossorigin />
  <link rel="icon" type="image/png" sizes="32x32" href="/assets/icons/favicon-32.png" />
  <link rel="apple-touch-icon" sizes="192x192" href="/assets/icons/icon-192.png" />
  <link rel="manifest" href="/manifest.webmanifest" />"""


def render_shared_ui() -> str:
    stamp_cards = "\n".join(
        f"""          <li class="passport-stamp is-locked" data-passport-stamp="{esc(stamp["id"])}">
            <span class="stamp-mark" aria-hidden="true">{esc(stamp["visual"])}</span>
            <strong>{esc(stamp["title"])}</strong>
            <span>{esc(stamp["description"])}</span>
          </li>"""
        for stamp in STAMPS
    )
    return f"""  <p class="sr-only" id="museumStatus" aria-live="polite" aria-atomic="true"></p>

  <dialog class="museum-dialog surprise-dialog" id="surpriseDialog" aria-labelledby="surpriseTitle">
    <div class="dialog-window">
      <div class="window-bar"><span>RANDOM_MEMORY.EXE</span><button type="button" class="dialog-close" data-dialog-close="surpriseDialog" aria-label="Close Surprise Me">×</button></div>
      <div class="dialog-body" data-surprise-loading>
        <p class="eyebrow">Loading from CD-ROM…</p>
        <div class="cd-loader" aria-hidden="true"></div>
        <p>Finding a memory you have not just seen.</p>
      </div>
      <div class="dialog-body" data-surprise-ready hidden>
        <p class="eyebrow">Random memory loaded</p>
        <h2 id="surpriseTitle" data-surprise-title>Surprise Me</h2>
        <p data-surprise-teaser></p>
        <p class="artifact-meta-line" data-surprise-meta></p>
        <div class="dialog-actions">
          <a class="button primary" href="/surprise/" data-surprise-open>Open memory</a>
          <button class="button" type="button" data-surprise-again>Try another</button>
          <button class="button subtle" type="button" data-dialog-close="surpriseDialog">Not now</button>
        </div>
      </div>
    </div>
  </dialog>

  <dialog class="museum-dialog passport-dialog" id="passportDialog" aria-labelledby="passportTitle">
    <div class="dialog-window">
      <div class="window-bar"><span>MUSEUM_PASSPORT.CARD</span><button type="button" class="dialog-close" data-dialog-close="passportDialog" aria-label="Close Museum Passport">×</button></div>
      <div class="dialog-body">
        <p class="eyebrow">Local museum progress</p>
        <h2 id="passportTitle">Your Museum Passport</h2>
        <p class="storage-note" data-storage-note>Saved only on this device. No account, tracking, or personal data.</p>
        <div class="passport-stats" aria-label="Museum Passport totals">
          <span><strong data-passport-rooms>0</strong> rooms visited</span>
          <span><strong data-passport-artifacts>0</strong> objects inspected</span>
          <span><strong data-passport-stamps>0</strong> stamps earned</span>
        </div>
        <ul class="passport-stamp-grid" aria-label="Passport stamps">
{stamp_cards}
        </ul>
        <div class="passport-resume" data-tour-resume hidden>
          <p><strong>Tour in progress:</strong> <span data-tour-resume-label></span></p>
          <a class="button" data-tour-resume-link href="/tours/before-the-feed/">Resume tour</a>
        </div>
        <button class="button danger" type="button" data-passport-reset-open>Reset local passport</button>
      </div>
    </div>
  </dialog>

  <dialog class="museum-dialog reset-dialog" id="passportResetDialog" aria-labelledby="passportResetTitle">
    <div class="dialog-window">
      <div class="window-bar"><span>RESET_CONFIRM.TXT</span></div>
      <div class="dialog-body">
        <h2 id="passportResetTitle">Reset this passport?</h2>
        <p>This removes visited rooms, inspected objects, stamps, and tour progress from this browser. It cannot be undone.</p>
        <div class="dialog-actions">
          <button class="button" type="button" data-passport-reset-cancel>Keep my passport</button>
          <button class="button danger" type="button" data-passport-reset-confirm>Reset passport</button>
        </div>
      </div>
    </div>
  </dialog>"""


def render_media(artifact: dict, eager: bool = False) -> str:
    media = artifact["media"]
    if media["kind"] == "recreation":
        return (
            f'<div class="artifact-recreation recreation-{esc(artifact["id"])}" '
            f'role="img" aria-label="{esc(media["alt"])}">'
            f'<span>{esc(media["label"])}</span></div>'
        )
    loading = "eager" if eager else "lazy"
    priority = ' fetchpriority="high"' if eager else ""
    responsive_name = {
        "family-pc": "family-pc",
        "hubble-launch": "hubble-launch",
        "bondi-imac": "imac-bondi",
    }.get(artifact["id"])
    if responsive_name:
        widths = [
            width
            for width in (480, 960, 1440)
            if (ROOT / f"assets/generated/{responsive_name}-{width}.webp").exists()
        ]
        if widths:
            avif = ", ".join(
                f"/assets/generated/{responsive_name}-{width}.avif {width}w"
                for width in widths
            )
            webp = ", ".join(
                f"/assets/generated/{responsive_name}-{width}.webp {width}w"
                for width in widths
            )
            return (
                '<picture class="responsive-artifact">'
                f'<source type="image/avif" srcset="{avif}" />'
                f'<source type="image/webp" srcset="{webp}" />'
                f'<img src="{esc(media["src"])}" alt="{esc(media["alt"])}" '
                f'width="{media["width"]}" height="{media["height"]}" '
                f'loading="{loading}" decoding="async"{priority} />'
                "</picture>"
            )
    return (
        f'<img src="{esc(media["src"])}" alt="{esc(media["alt"])}" '
        f'width="{media["width"]}" height="{media["height"]}" '
        f'loading="{loading}" decoding="async"{priority} />'
    )


def render_artifact_card(
    artifact: dict, compact: bool = False, dom_id: str | None = None
) -> str:
    media = artifact["media"]
    credit = esc(media["credit"])
    if media.get("sourceUrl"):
        credit_markup = (
            f'<a href="{esc(media["sourceUrl"])}" target="_blank" '
            f'rel="noopener noreferrer">{credit} ↗</a>'
        )
    else:
        credit_markup = credit
    details = "" if compact else f"""        <details>
          <summary>Open curator label</summary>
          <p>{esc(artifact["curatorNote"])}</p>
          <p><strong>Why it mattered:</strong> {esc(artifact["whyItMattered"])}</p>
          <p class="artifact-credit">{credit_markup} · {esc(media["license"])}</p>
        </details>"""
    card_id = dom_id or f'artifact-{artifact["slug"]}'
    return f"""      <article class="artifact-ticket" id="{esc(card_id)}" data-artifact-id="{esc(artifact["id"])}">
        <div class="artifact-ticket-media">{render_media(artifact)}</div>
        <div class="artifact-ticket-copy">
          <p class="artifact-label">{esc(artifact["label"])} · {esc(artifact["dateRange"]["label"])}</p>
          <h3>{esc(artifact["title"])}</h3>
{details}
          <div class="artifact-actions">
            <button class="button inspect-button" type="button" data-artifact-inspect="{esc(artifact["id"])}">Inspect + stamp</button>
            <a href="{esc(artifact["target"])}">Open exhibit</a>
          </div>
        </div>
      </article>"""


def render_artifact_shelf(route: dict) -> str:
    items = [ARTIFACT_BY_ID[item] for item in route.get("artifactIds", []) if item in ARTIFACT_BY_ID]
    if not items:
        return ""
    cards = "\n".join(render_artifact_card(item) for item in items)
    return f"""    <section class="panel artifact-shelf" aria-labelledby="artifactShelfTitle-{esc(route["id"])}">
      <div class="section-heading compact-heading">
        <p class="eyebrow">Passport exhibit tray</p>
        <h2 id="artifactShelfTitle-{esc(route["id"])}">Objects you can inspect here.</h2>
        <p>Open a curator label, stamp the object, then follow its next connection.</p>
      </div>
      <div class="artifact-ticket-grid">
{cards}
      </div>
    </section>"""


def render_resource_card(item: dict, featured: bool = False) -> str:
    classes = "resource-card featured-resource" if featured else "resource-card"
    warning = (
        f'<p class="resource-usage"><b>Heads up:</b> {esc(item["contentWarning"])}</p>'
        if item.get("contentWarning")
        else ""
    )
    availability = (
        f'<p class="resource-availability"><b>Availability:</b> {esc(item["availabilityWarning"])}</p>'
        if item.get("availabilityWarning")
        else ""
    )
    notices = "\n".join(
        f"          {notice}" for notice in (warning, availability) if notice
    )
    return f"""        <article class="{classes}" data-category="{esc(item["categoryId"])}" data-title="{esc(item["title"].lower())}" data-tag="{esc(item["tag"])}">
          <div class="resource-card-top"><span class="resource-category">{esc(item["category"])}</span><span class="resource-tag">{esc(item["destinationType"])}</span></div>
          <h3>{esc(item["title"])}</h3>
          <p>{esc(item["description"])}</p>
{notices}
          <a class="resource-link" href="{esc(item["url"])}" target="_blank" rel="noopener noreferrer">Launch external portal ↗</a>
        </article>"""


def render_webring_sections() -> tuple[str, str]:
    featured = [item for item in RESOURCES if item["featured"]]
    featured_cards = "\n".join(render_resource_card(item, True) for item in featured)
    directory_cards = "\n".join(render_resource_card(item) for item in RESOURCES)
    featured_section = f"""    <section class="panel featured-resource-section" aria-labelledby="featuredResourcesTitle">
      <div class="section-heading inline-heading">
        <p class="eyebrow">Curator shortcuts</p>
        <h2 id="featuredResourcesTitle">Twelve strong exits from the museum.</h2>
        <p>Featured selections are references into the same {len(RESOURCES)}-destination catalog, not extra resources.</p>
      </div>
      <div class="featured-resource-grid">
{featured_cards}
      </div>
    </section>"""
    directory_section = f"""    <section class="panel resource-directory" id="directory">
      <p class="eyebrow">Full directory</p>
      <h2>Curated exit hall</h2>
      <p class="resource-count" id="resourceCount" aria-live="polite" aria-atomic="true">Showing {len(RESOURCES)} external destinations.</p>
      <div class="resource-grid" id="resourceGrid">
{directory_cards}
      </div>
      <p class="no-results" id="resourceNoResults" hidden>No portals found. Try a looser search, like “web”, “games”, or “music”.</p>
    </section>"""
    return featured_section, directory_section


def search_records():
    records = []
    excluded_paths = {"/", "/search/", "/sitemap/", "/credits/"}
    for route in ROUTES:
        if route["path"] in excluded_paths:
            continue
        records.append(
            {
                "id": f'route-{route["id"]}',
                "type": route["type"],
                "recordType": "route" if route["type"] != "tours" else "tour",
                "title": route["title"],
                "summary": route["summary"],
                "href": route["path"],
                "tags": route["tags"],
                "external": False,
            }
        )
    for artifact in ARTIFACTS:
        records.append(
            {
                "id": f'artifact-{artifact["id"]}',
                "type": "objects",
                "recordType": "artifact",
                "title": artifact["title"],
                "summary": artifact["curatorNote"],
                "href": artifact["target"],
                "tags": artifact["tags"] + [artifact["room"], artifact["dateRange"]["label"]],
                "external": False,
            }
        )
    for item in RESOURCES:
        records.append(
            {
                "id": f'resource-{item["id"]}',
                "type": "explore",
                "recordType": item["destinationType"],
                "title": item["title"],
                "summary": item["description"],
                "href": item["url"],
                "tags": [item["category"], item["tag"], item["destinationType"]],
                "external": True,
            }
        )
    return records


def render_search_sections() -> tuple[str, str]:
    records = search_records()
    counts = Counter(item["type"] for item in records)
    categories = [
        ("all", "All"),
        ("highlights", "Highlights"),
        ("years", "Years"),
        ("zones", "Rooms"),
        ("objects", "Objects"),
        ("tours", "Tours"),
        ("community", "Community"),
        ("explore", "Explore tools"),
    ]
    buttons = "\n".join(
        f'        <button class="resource-filter{" active" if key == "all" else ""}" '
        f'type="button" data-site-filter="{key}" aria-pressed="{"true" if key == "all" else "false"}">'
        f'{label} <span>{len(records) if key == "all" else counts.get(key, 0)}</span></button>'
        for key, label in categories
    )
    controls = f"""    <section class="panel resource-console" id="finder" aria-label="Portal search controls">
      <div class="resource-console-grid">
        <div><p class="eyebrow">Search the museum</p><h2>Portal finder + artifact atlas</h2><p>Type a year, room, object, tour stop, or external resource.</p></div>
        <div class="resource-search-wrap">
          <label for="siteSearchInput">Search routes + objects</label>
          <input id="siteSearchInput" type="search" placeholder="try: Mosaic, cassette, Blockbuster, GeoCities…" autocomplete="off" />
        </div>
      </div>
      <div class="site-filter-row" aria-label="Filter portal routes">
{buttons}
      </div>
    </section>"""
    cards = []
    for item in records:
        attrs = (
            ' target="_blank" rel="noopener noreferrer"'
            if item["external"]
            else ""
        )
        tags = " ".join(str(tag) for tag in item["tags"])
        cards.append(
            f"""        <a class="chart-year-card ready site-search-card" href="{esc(item["href"])}"{attrs}
          data-search-category="{esc(item["type"])}" data-record-type="{esc(item["recordType"])}"
          data-title="{esc(item["title"].lower())}" data-tags="{esc(tags.lower())}">
          <span>{esc(item["recordType"]).upper()}</span>
          <h3>{esc(item["title"])}</h3>
          <p>{esc(item["summary"])}</p>
        </a>"""
        )
    results = f"""    <section class="panel resource-directory" aria-labelledby="searchResultsTitle">
      <p class="eyebrow">Results</p>
      <h2 id="searchResultsTitle">Routes, objects, tours, and exit-hall resources</h2>
      <p class="resource-count" id="siteSearchCount" aria-live="polite" aria-atomic="true">Showing {len(records)} matches.</p>
      <div class="chart-year-grid site-search-grid" id="siteSearchGrid">
{chr(10).join(cards)}
      </div>
      <div class="portal-box resource-notes" id="siteSearchNoResults" hidden>
        <h3>No memory found under that label.</h3>
        <p>Try a shorter word, clear the filters, or let the museum choose.</p>
        <div class="hero-actions"><button class="button" type="button" data-search-clear>Clear search</button><a class="button" href="/surprise/" data-surprise-trigger>Surprise me</a><a class="button" href="/sitemap/">Open museum map</a></div>
      </div>
    </section>"""
    return controls, results


def render_timeline_doors() -> str:
    year_routes = sorted(
        (route for route in ROUTES if route["type"] == "years"),
        key=lambda route: route["path"],
    )
    cards = []
    for route in year_routes:
        year = route["path"].strip("/").split("/")[1]
        artifacts = [
            ARTIFACT_BY_ID[artifact_id]
            for artifact_id in route.get("artifactIds", [])
            if artifact_id in ARTIFACT_BY_ID
        ][:3]
        object_labels = "".join(
            f"<em>{esc(artifact['title'])}</em>" for artifact in artifacts
        )
        cards.append(
            f"""        <a class="timeline-card museum-year-door" href="{esc(route["path"])}" data-timeline-room="timeline-{year}">
          <span class="timeline-year">{year}</span>
          <div>
            <p class="artifact-label">Door {int(year) - 1989:02d} · catalog case</p>
            <h3>{esc(route["title"])}</h3>
            <p>{esc(route["summary"])}</p>
            <div class="mini-tags year-object-labels">{object_labels}</div>
            <strong>Open {year} →</strong>
            <small class="visited-door-label" data-visited-door-label>Not visited</small>
          </div>
        </a>"""
        )
    return f"""    <section class="timeline-product-panel" aria-labelledby="timelineDoorsTitle">
      <div class="section-heading inline-heading">
        <p class="eyebrow">Ten chronological doors</p>
        <h2 id="timelineDoorsTitle">Choose a year. Carry the objects forward.</h2>
        <p>Each door previews three catalog objects. Your local passport marks a door after you enter it.</p>
      </div>
      <div class="timeline-card-grid">
{chr(10).join(cards)}
      </div>
    </section>"""


def render_homepage_builder() -> str:
    return """        <div class="homepage-builder" data-homepage-builder>
          <div class="homepage-preview" aria-live="polite" data-homepage-preview>
            <p class="homepage-title">WELCOME TO MY PAGE!!!</p>
            <p>Music, games, aliens, and links I think are cool.</p>
            <p class="homepage-under-construction" hidden data-builder-layer="construction">UNDER CONSTRUCTION</p>
            <p class="homepage-counter" hidden data-builder-layer="counter">visitor no. 000247</p>
          </div>
          <div class="builder-controls" aria-label="Homepage recreation controls">
            <button type="button" aria-pressed="false" data-homepage-toggle="stars">Add tiled stars</button>
            <button type="button" aria-pressed="false" data-homepage-toggle="construction">Add construction badge</button>
            <button type="button" aria-pressed="false" data-homepage-toggle="counter">Add visitor counter</button>
            <button type="button" data-homepage-reset>Reset page</button>
          </div>
        </div>"""


def render_tour_main(tour: dict) -> str:
    stops = []
    total = len(tour["stops"])
    for stop in tour["stops"]:
        artifacts = "\n".join(
            render_artifact_card(
                ARTIFACT_BY_ID[item],
                compact=True,
                dom_id=f'tour-{stop["id"]}-{ARTIFACT_BY_ID[item]["slug"]}',
            )
            for item in stop["artifactIds"]
            if item in ARTIFACT_BY_ID
        )
        interaction = (
            render_homepage_builder()
            if stop.get("interaction") == "homepage-builder"
            else ""
        )
        back = (
            '<button class="button" type="button" data-tour-back>Back</button>'
            if stop["number"] > 1
            else ""
        )
        next_label = "Complete tour" if stop["number"] == total else "Next stop"
        stops.append(
            f"""      <article class="tour-stop" id="{esc(stop["id"])}" data-tour-stop="{esc(stop["id"])}" data-tour-number="{stop["number"]}">
        <p class="tour-step-label">Stop {stop["number"]} of {total}</p>
        <h2>{esc(stop["title"])}</h2>
        <p class="tour-curator-text">{esc(stop["curatorText"])}</p>
        <p>{esc(stop["detail"])}</p>
        <div class="tour-artifact-row">{artifacts}</div>
{interaction}
        <p><a href="{esc(stop["exhibitHref"])}">{esc(stop["exhibitLabel"])} →</a></p>
        <div class="tour-controls">
          {back}
          <button class="button primary" type="button" data-tour-next>{next_label}</button>
          <a class="button subtle" href="/">Exit tour</a>
        </div>
      </article>"""
        )
    return f"""  <main id="main-content" class="tour-main" data-tour-id="{esc(tour["id"])}">
    <section class="window tour-hero">
      <div class="window-bar"><span>BEFORE_THE_FEED.TOUR</span><span class="window-buttons" aria-hidden="true">_ □ ×</span></div>
      <div class="page-pad">
        <nav class="breadcrumbs"><a href="/">Museum Desk</a> / Guided Tour</nav>
        <p class="eyebrow">One excellent guided tour · about {tour["durationMinutes"]} minutes</p>
        <h1>{esc(tour["title"])}</h1>
        <p class="lede">{esc(tour["description"])}</p>
        <div class="tour-progress" role="progressbar" aria-label="Tour progress" aria-valuemin="1" aria-valuemax="{total}" aria-valuenow="1"><span data-tour-progress-bar></span></div>
        <p class="tour-progress-copy" aria-live="polite" data-tour-progress-copy>Ready for stop 1 of {total}.</p>
      </div>
    </section>
    <section class="tour-deck" data-tour-deck>
{chr(10).join(stops)}
    </section>
  </main>"""


def render_surprise_main() -> str:
    eligible = [item for item in ARTIFACTS if item["randomEligible"] and item["status"] != "needs-source"]
    envelopes = []
    for index, item in enumerate(eligible, 1):
        envelopes.append(
            f"""      <a class="mystery-envelope" href="{esc(item["target"])}" data-fallback-artifact="{esc(item["id"])}">
        <span aria-hidden="true">✉ {index:02d}</span>
        <strong>Mystery envelope</strong>
        <small>{esc(item["dateRange"]["label"])} · {esc(item["room"].replace("-", " "))}</small>
      </a>"""
        )
    return f"""  <main id="main-content" class="surprise-page">
    <section class="window page-hero">
      <div class="window-bar"><span>RANDOM_MEMORY.EXE</span><span class="window-buttons" aria-hidden="true">_ □ ×</span></div>
      <div class="page-pad">
        <nav class="breadcrumbs"><a href="/">Museum Desk</a> / Surprise Me</nav>
        <p class="eyebrow">Serendipity desk</p>
        <h1>Open a mystery memory.</h1>
        <p class="lede">With JavaScript, the desk avoids your three most recent choices and reveals a teaser first. Without it, every envelope below still opens a real, validated museum exhibit.</p>
        <button class="button primary" type="button" data-surprise-trigger-button>Load a random memory</button>
      </div>
    </section>
    <section class="panel">
      <div class="section-heading compact-heading"><p class="eyebrow">No-script envelope wall</p><h2>Choose one without reading the label.</h2></div>
      <div class="mystery-envelope-grid">
{chr(10).join(envelopes)}
      </div>
    </section>
  </main>"""


def render_credits_main() -> str:
    credits = []
    seen = set()
    for item in ARTIFACTS:
        media = item["media"]
        key = (media.get("src"), media.get("sourceUrl"), media["credit"])
        if key in seen:
            continue
        seen.add(key)
        if media.get("sourceUrl"):
            source = f'<a href="{esc(media["sourceUrl"])}" target="_blank" rel="noopener noreferrer">source ↗</a>'
        else:
            source = "original recreation"
        credits.append(
            f"<li><strong>{esc(item['title'])}</strong> — {esc(media['credit'])}; "
            f"{esc(media['license'])}; {source}</li>"
        )
    return f"""  <main id="main-content">
    <section class="window page-hero">
      <div class="window-bar"><span>CREDITS_AND_PROVENANCE.TXT</span><span class="window-buttons" aria-hidden="true">_ □ ×</span></div>
      <div class="page-pad"><nav class="breadcrumbs"><a href="/">Museum Desk</a> / Credits</nav><p class="eyebrow">Source labels</p><h1>Credits, licenses, and recreations.</h1><p class="lede">90s.land distinguishes sourced media, editorial interpretation, and original interface recreations.</p></div>
    </section>
    <section class="panel credits-panel">
      <h2>Artifact media</h2>
      <ul class="credits-list">{''.join(credits)}</ul>
      <h2>Type</h2>
      <p>Press Start 2P and Space Mono are self-hosted from the Google Fonts distribution under the SIL Open Font License. Read the local <a href="/assets/fonts/OFL-Press-Start-2P.txt">Press Start 2P license</a> and <a href="/assets/fonts/OFL-Space-Mono.txt">Space Mono license</a>.</p>
      <h2>Editorial status</h2>
      <p><strong>Verified</strong> artifacts use a source trail. <strong>Editorial</strong> objects are clearly labeled original recreations. Items marked <strong>needs source</strong> are excluded from Surprise Me and guided tours.</p>
      <h2>Sharing artwork</h2>
      <p>The 1200×630 social card uses one original OpenAI-generated museum-case background, based on the completed local lobby as a style reference, with all visible type applied deterministically from the self-hosted fonts.</p>
    </section>
  </main>"""


def page_document(route: dict, main: str, body_class: str = "") -> str:
    body_attr = f' class="{esc(body_class)}"' if body_class else ""
    return f"""<!doctype html>
<html lang="en" class="no-js">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
{region("head", render_head(route))}
  <link rel="stylesheet" href="/styles.css?v=playable-museum-1" />
</head>
<body{body_attr} data-route="{esc(route["path"])}" data-room="{esc(route_room(route))}">
  <a class="skip-link" href="#main-content">Skip to museum content</a>
  <div class="crt" aria-hidden="true"></div>
  <div class="starfield" aria-hidden="true"></div>
  <header class="topbar" id="top">
    <a class="brand" href="/" aria-label="90s.land home"><span class="logo-box">90s</span><span>.land</span></a>
    <button class="menu-toggle" type="button" aria-expanded="false" aria-controls="siteNav">
      <span aria-hidden="true">☰</span><span>Menu</span>
    </button>
{region("navigation", render_navigation())}
  </header>
{main}
  <footer class="footer"><p>© 1999–forever 90s.land // handmade for curious people // <a href="/credits/">credits</a> // <a href="#top">back to top</a></p></footer>
{region("shared-ui", render_shared_ui())}
  <script type="module" src="/js/app.js?v=playable-museum-1"></script>
</body>
</html>
"""


def render_404() -> str:
    route = {
        "path": "/404.html",
        "title": "404 — Exhibit not found",
        "summary": "The requested 90s.land exhibit could not be found.",
        "type": "highlights",
    }
    main = """  <main id="main-content" class="error-page">
    <section class="window page-hero">
      <div class="window-bar"><span>404_NOT_FOUND.EXE</span><span class="window-buttons" aria-hidden="true">_ □ ×</span></div>
      <div class="page-pad">
        <p class="eyebrow">Missing exhibit</p>
        <h1>This memory fell behind the filing cabinet.</h1>
        <p class="lede">The route does not exist, but the museum is still open.</p>
        <div class="hero-actions"><a class="button primary" href="/">Return to the Museum Desk</a><a class="button" href="/surprise/">Surprise me</a><a class="button" href="/sitemap/">Open the map</a></div>
      </div>
    </section>
  </main>"""
    return page_document(route, main, "error-body")


def inject_head(source: str, route: dict) -> str:
    content = render_head(route)
    source, found = replace_region(source, "head", content)
    if found:
        return source
    source = re.sub(r"\s*<meta\s+name=\"description\"[^>]*?/?>", "", source, count=1, flags=re.I)
    source = re.sub(r"\s*<title>.*?</title>", "", source, count=1, flags=re.S | re.I)
    viewport = re.search(r"<meta\s+name=\"viewport\"[^>]*?/?>", source, flags=re.I)
    if not viewport:
        raise ValueError(f"Missing viewport meta for {route['path']}")
    return source[: viewport.end()] + "\n" + region("head", content) + source[viewport.end() :]


def inject_navigation(source: str) -> str:
    content = render_navigation()
    source, found = replace_region(source, "navigation", content)
    if found:
        return source
    pattern = re.compile(
        r"<nav\s+class=\"nav\"\s+id=\"siteNav\"[^>]*>.*?</nav>",
        re.S | re.I,
    )
    if not pattern.search(source):
        raise ValueError("Missing site navigation")
    return pattern.sub(region("navigation", content), source, count=1)


def inject_shared_ui(source: str) -> str:
    content = render_shared_ui()
    source, found = replace_region(source, "shared-ui", content)
    if found:
        return source
    script = re.search(r'<script[^>]+src="/(?:script\.js|js/app\.js)[^"]*"[^>]*></script>', source, re.I)
    if not script:
        return source.replace("</body>", region("shared-ui", content) + "\n</body>")
    return source[: script.start()] + region("shared-ui", content) + "\n  " + source[script.start() :]


def inject_artifact_shelf(source: str, route: dict) -> str:
    content = render_artifact_shelf(route)
    source, found = replace_region(source, "artifact-shelf", content)
    if found:
        return source
    if not content:
        return source
    return source.replace("</main>", region("artifact-shelf", content) + "\n  </main>", 1)


def inject_museum_tools_map(source: str) -> str:
    content = """    <section class="panel museum-map-tools" id="museum-tools">
      <p class="eyebrow">Playable museum tools</p>
      <h2>Start with an action.</h2>
      <div class="zone-grid">
        <a class="zone-card" href="/tours/before-the-feed/"><span class="pixel-icon">TOUR</span><h3>Before the Feed</h3><p>Six stops through the personal web.</p></a>
        <a class="zone-card" href="/surprise/"><span class="pixel-icon">RND</span><h3>Surprise Me</h3><p>Let the museum choose a valid artifact.</p></a>
        <a class="zone-card" href="/credits/"><span class="pixel-icon">SRC</span><h3>Credits</h3><p>See source, license, and recreation labels.</p></a>
      </div>
    </section>"""
    source, found = replace_region(source, "museum-tools-map", content)
    if found:
        return source
    return source.replace("</main>", region("museum-tools-map", content) + "\n  </main>", 1)


def normalize_existing_page(source: str, route: dict) -> str:
    source = inject_head(source, route)
    source = inject_navigation(source)
    source = inject_shared_ui(source)
    source = inject_artifact_shelf(source, route)
    if route["path"] == "/sitemap/":
        source = inject_museum_tools_map(source)

    if "class=\"no-js\"" not in source:
        source = re.sub(r"<html([^>]*)>", r'<html\1 class="no-js">', source, count=1)

    def body_repl(match):
        attrs = match.group(1)
        attrs = re.sub(r'\s+data-(?:route|room)="[^"]*"', "", attrs)
        return (
            f'<body{attrs} data-route="{esc(route["path"])}" '
            f'data-room="{esc(route_room(route))}">'
        )

    source = re.sub(r"<body([^>]*)>", body_repl, source, count=1, flags=re.I)
    if "class=\"skip-link\"" not in source:
        source = re.sub(
            r"(<body[^>]*>)",
            r'\1\n  <a class="skip-link" href="#main-content">Skip to museum content</a>',
            source,
            count=1,
        )
    source = re.sub(
        r"<main(?![^>]*\sid=)([^>]*)>",
        r'<main id="main-content"\1>',
        source,
        count=1,
        flags=re.I,
    )
    source = re.sub(
        r'class="window-buttons"(?!\s+aria-hidden)',
        'class="window-buttons" aria-hidden="true"',
        source,
    )
    source = source.replace('rel="noreferrer"', 'rel="noopener noreferrer"')
    source = re.sub(
        r'<script\s+src="/script\.js[^"]*"></script>',
        '<script type="module" src="/js/app.js?v=playable-museum-1"></script>',
        source,
        flags=re.I,
    )
    source = re.sub(
        r'<link\s+href="https://fonts\.googleapis\.com[^>]+>\s*',
        "",
        source,
        flags=re.I,
    )
    source = re.sub(
        r'<link\s+rel="preconnect"\s+href="https://fonts\.(?:googleapis|gstatic)\.com"[^>]*>\s*',
        "",
        source,
        flags=re.I,
    )
    source = re.sub(
        r'<link\s+rel="stylesheet"\s+href="/styles\.css[^"]*"\s*/?>',
        '<link rel="stylesheet" href="/styles.css?v=playable-museum-1" />',
        source,
        count=1,
        flags=re.I,
    )
    source = re.sub(
        r'<footer class="footer">.*?</footer>',
        '<footer class="footer"><p>© 1999–forever 90s.land // handmade for curious people // <a href="/credits/">credits</a> // <a href="#top">back to top</a></p></footer>',
        source,
        count=1,
        flags=re.I | re.S,
    )
    return source


def replace_full_section(source: str, selector_pattern: str, name: str, content: str) -> str:
    source, found = replace_region(source, name, content)
    if found:
        return source
    match = re.search(selector_pattern, source, re.S | re.I)
    if not match:
        raise ValueError(f"Could not locate section for {name}")
    return source[: match.start()] + region(name, content) + source[match.end() :]


def render_existing_page(route: dict) -> str:
    path = route_to_file(route["path"])
    source = path.read_text()
    if route["path"] == "/webring/":
        featured, directory = render_webring_sections()
        source = replace_full_section(
            source,
            r'<section class="panel starter-pack".*?</section>',
            "webring-featured",
            featured,
        )
        source = replace_full_section(
            source,
            r'<section class="panel resource-directory" id="directory">.*?</section>',
            "webring-directory",
            directory,
        )
        source = re.sub(
            r"<span>78 portals indexed</span>",
            f"<span>{len(RESOURCES)} unique portals indexed</span>",
            source,
        )
        source = re.sub(
            r'(data-resource-filter="all">All <span>)\d+(</span>)',
            rf"\g<1>{len(RESOURCES)}\g<2>",
            source,
        )
    if route["path"] == "/search/":
        controls, results = render_search_sections()
        source = replace_full_section(
            source,
            r'<section class="panel resource-console" id="finder".*?</section>',
            "search-controls",
            controls,
        )
        source = replace_full_section(
            source,
            r'<section class="panel resource-directory">.*?</section>',
            "search-results",
            results,
        )
    if route["path"] == "/timeline/":
        source = replace_full_section(
            source,
            r'<section class="timeline-product-panel">.*?</section>',
            "timeline-doors",
            render_timeline_doors(),
        )
    return normalize_existing_page(source, route)


def build_outputs() -> dict[Path, str]:
    outputs = {}
    for route in ROUTES:
        if route["path"] == "/surprise/":
            outputs[route_to_file(route["path"])] = page_document(
                route, render_surprise_main(), "surprise-body"
            )
        elif route["path"] == "/tours/before-the-feed/":
            outputs[route_to_file(route["path"])] = page_document(
                route, render_tour_main(TOURS[0]), "tour-body"
            )
        elif route["path"] == "/credits/":
            outputs[route_to_file(route["path"])] = page_document(
                route, render_credits_main(), "credits-body"
            )
        else:
            outputs[route_to_file(route["path"])] = render_existing_page(route)

    outputs[ROOT / "404.html"] = render_404()
    sitemap_urls = "\n".join(
        f"  <url><loc>{SITE_URL}{esc(route['path'])}</loc></url>" for route in ROUTES
    )
    outputs[ROOT / "sitemap.xml"] = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{sitemap_urls}\n</urlset>\n"
    )
    outputs[ROOT / "robots.txt"] = (
        "User-agent: *\nAllow: /\n\nSitemap: https://90s.land/sitemap.xml\n"
    )
    manifest = {
        "name": "90s.land — A playable museum of the 1990s",
        "short_name": "90s.land",
        "start_url": "/",
        "display": "browser",
        "background_color": "#070018",
        "theme_color": "#0b001c",
        "description": "Browse the decade. Open its objects. Get lost on purpose.",
        "icons": [
            {"src": "/assets/icons/icon-192.png", "sizes": "192x192", "type": "image/png"},
            {"src": "/assets/icons/icon-512.png", "sizes": "512x512", "type": "image/png"},
        ],
    }
    outputs[ROOT / "manifest.webmanifest"] = json.dumps(manifest, indent=2) + "\n"
    return outputs


def validate_catalogs() -> list[str]:
    errors = []
    artifact_ids = [item["id"] for item in ARTIFACTS]
    if len(artifact_ids) != 30:
        errors.append(f"Expected 30 artifacts, found {len(artifact_ids)}")
    if len(set(artifact_ids)) != len(artifact_ids):
        errors.append("Artifact IDs are not unique")
    if len({item["id"] for item in RESOURCES}) != len(RESOURCES):
        errors.append("Resource IDs are not unique")
    if len(RESOURCES) != 78:
        errors.append(f"Expected 78 unique resources, found {len(RESOURCES)}")
    if sum(bool(item["featured"]) for item in RESOURCES) != 12:
        errors.append("Expected 12 featured resource references")
    for artifact in ARTIFACTS:
        if artifact["status"] == "needs-source" and artifact["randomEligible"]:
            errors.append(f'{artifact["id"]} is unsourced but random eligible')
        if artifact["media"]["kind"] == "image":
            media_path = ROOT / artifact["media"]["src"].lstrip("/")
            if not media_path.exists():
                errors.append(f"Missing artifact media: {media_path}")
    for tour in TOURS:
        if not 5 <= len(tour["stops"]) <= 7:
            errors.append(f'{tour["id"]} must have 5–7 stops')
        for stop in tour["stops"]:
            for artifact_id in stop["artifactIds"]:
                if artifact_id not in ARTIFACT_BY_ID:
                    errors.append(f"Unknown tour artifact: {artifact_id}")
        if tour["completionStampId"] not in STAMP_BY_ID:
            errors.append(f'Unknown completion stamp: {tour["completionStampId"]}')
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Fail instead of writing")
    args = parser.parse_args()

    errors = validate_catalogs()
    if errors:
        print("\n".join(f"ERROR: {item}" for item in errors), file=sys.stderr)
        return 1

    outputs = build_outputs()
    changed = []
    for path, expected in outputs.items():
        current = path.read_text() if path.exists() else None
        if current != expected:
            changed.append(path)
            if not args.check:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(expected)

    if changed:
        for path in changed:
            print(path.relative_to(ROOT))
        if args.check:
            print(f"{len(changed)} generated files are stale", file=sys.stderr)
            return 1
        print(f"rendered {len(changed)} files")
    else:
        print("generated files are current")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
