#!/usr/bin/env python3
"""Generate complete public pages from authoritative compositions and catalogs."""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import quote

from validate_content import validate_catalogs as validate_existing_catalogs
import editorial
import archive_content as archive
import archive_pages
import hub_pages
import media_variants
import product_pages
import launch_meta
import discovery

ROOT = Path(__file__).resolve().parents[1]
SITE_URL = "https://90s.land"


def load_json(name: str):
    return json.loads((ROOT / "data" / name).read_text())


ARTIFACTS = load_json("artifacts.json")
NAVIGATION = load_json("navigation.json")
RESOURCES = load_json("resources.json")
ROUTES = archive.all_routes()
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


def render_head(route: dict) -> str:
    meta = launch_meta.metadata(route)
    title, description, canonical = (meta[k] for k in ('title','description','canonical'))
    cards = load_json('social-cards.json')['cards']
    card = cards[launch_meta.card_route(route)]
    image_meta = f"""
  <meta property="og:image" content="{SITE_URL}{card['src']}" />
  <meta property="og:image:type" content="image/jpeg" />
  <meta property="og:image:width" content="1200" />
  <meta property="og:image:height" content="630" />
  <meta property="og:image:alt" content="{esc(card['alt'])}" />
  <meta name="twitter:image" content="{SITE_URL}{card['src']}" />
  <meta name="twitter:image:alt" content="{esc(card['alt'])}" />"""
    return f"""  <meta name="description" content="{esc(description)}" />
  <title>{esc(title)}</title>
  <meta name="robots" content="{'index,follow' if meta['indexable'] else 'noindex,follow'}" />
  <link rel="canonical" href="{canonical}" />
  <meta property="og:type" content="website" />
  <meta property="og:site_name" content="90s.land" />
  <meta property="og:title" content="{esc(title)}" />
  <meta property="og:description" content="{esc(description)}" />
  <meta property="og:url" content="{canonical}" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{esc(title)}" />
  <meta name="twitter:description" content="{esc(description)}" />{image_meta}
  <link rel="icon" type="image/png" sizes="32x32" href="/assets/icons/favicon-32.png" />
  <link rel="icon" type="image/svg+xml" href="/assets/editorial/palm-sunset.svg" />
  <link rel="apple-touch-icon" sizes="192x192" href="/assets/icons/icon-192.png" />
  <link rel="manifest" href="/manifest.webmanifest" />
  {launch_meta.structured_navigation(route, editorial.parent_section(route))}"""


def render_shared_ui() -> str:
    stamp_cards = "\n".join(
        f"""          <li class="passport-stamp is-locked" data-passport-stamp="{esc(stamp["id"])}">
            <span class="stamp-mark" aria-hidden="true">{editorial.icon({"first-touch":"star","room-hopper":"folder","random-memory":"bolt","object-collector":"trophy","before-the-feed":"book"}.get(stamp["id"],"star"))}</span>
            <strong>{esc(stamp["title"])}</strong>
            <span>{esc(stamp["description"])}</span>
            <span class="stamp-state" data-passport-stamp-state>Not yet earned</span>
          </li>"""
        for stamp in STAMPS
    )
    return f"""  <p class="sr-only" id="museumStatus" aria-live="polite" aria-atomic="true"></p>

  <dialog class="museum-dialog surprise-dialog" id="surpriseDialog" aria-labelledby="surpriseTitle">
    <div class="dialog-window">
      <div class="dialog-heading"><span id="surpriseTitle">Surprise Me</span><button type="button" class="dialog-close" data-dialog-close="surpriseDialog" aria-label="Close Surprise Me">×</button></div>
      <div class="dialog-body" data-surprise-loading>
        <p class="eyebrow">Loading from CD-ROM…</p>
        <div class="cd-loader" aria-hidden="true"></div>
        <p>Finding a memory you have not just seen.</p>
      </div>
      <div class="dialog-body" data-surprise-ready hidden>
        <p class="eyebrow">Random memory loaded</p>
        <h2 data-surprise-title>Surprise Me</h2>
        <p data-surprise-teaser></p>
        <p class="artifact-meta-line" data-surprise-meta></p>
        <div class="dialog-actions">
          <a class="button primary" href="/surprise/" data-surprise-open>Open memory</a>
          <button class="button" type="button" data-surprise-again>Try another</button>
          <button class="button subtle" type="button" data-dialog-close="surpriseDialog">Not now</button>
        </div>
      </div>
      <div class="dialog-body" data-surprise-error hidden role="status">
        <h2>The disc needs another spin.</h2>
        <p>We couldn’t load a random memory. Try again, or pick an object from the collection.</p>
        <div class="dialog-actions"><button class="button" type="button" data-surprise-retry>Try again</button><a class="button primary" href="/archive/objects/">Browse objects</a></div>
      </div>
    </div>
  </dialog>

  <dialog class="museum-dialog passport-dialog" id="passportDialog" aria-labelledby="passportTitle">
    <div class="dialog-window">
      <div class="dialog-heading"><span>Passport</span><button type="button" class="dialog-close" data-dialog-close="passportDialog" aria-label="Close Museum Passport">×</button></div>
      <div class="dialog-body">
        <p class="eyebrow">YOUR DECADE, COLLECTED</p>
        <h2 id="passportTitle">Your Museum Passport</h2>
        <p class="storage-note" data-storage-note>Saved in this browser on this device. No account needed. Inspect objects, explore years and collections, and complete the tour to earn stamps.</p>
        <div class="passport-stats" aria-label="Museum Passport totals">
          <span><strong data-passport-rooms>0</strong> places explored</span>
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
        <button class="button danger" type="button" data-passport-reset-open>Reset my Passport</button>
      </div>
    </div>
  </dialog>

  <dialog class="museum-dialog reset-dialog" id="passportResetDialog" aria-labelledby="passportResetTitle">
    <div class="dialog-window">
      <div class="dialog-heading"><span>Your local progress</span></div>
      <div class="dialog-body">
        <h2 id="passportResetTitle">Reset this passport?</h2>
        <p>This removes explored years and collections, inspected objects, stamps, and tour progress from this browser. It cannot be undone.</p>
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
          <summary>About this object</summary>
          <p>{esc(artifact["curatorNote"])}</p>
          <p>{esc(artifact["whyItMattered"])}</p>
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
            <a href="{archive.object_url(artifact)}">Object details →</a>
          </div>
        </div>
      </article>"""


def render_artifact_shelf(route: dict) -> str:
    items = [ARTIFACT_BY_ID[item] for item in route.get("artifactIds", []) if item in ARTIFACT_BY_ID]
    if not items:
        return ""
    cards = "\n".join(render_artifact_card(item) for item in items)
    year = int(route['path'].strip('/').split('/')[-1]) if route['type']=='years' else None
    title = f'Objects around {year}' if year else 'Objects of the era'
    context = f'\n        <p>{esc(archive.YEARS[year]["objectNote"])}</p>' if year and archive.YEARS[year].get('objectNote') else ''
    extra_class = ' ed-home-objects' if route['path']=='/' else ''
    return f"""    <section class="panel artifact-shelf{extra_class}" aria-labelledby="artifactShelfTitle-{esc(route["id"])}">
      <div class="section-heading compact-heading">
        <p class="eyebrow">THE OBJECT COLLECTION</p>
        <h2 id="artifactShelfTitle-{esc(route["id"])}">{title}</h2>
        <p>Get closer to the everyday things that made the decade. Collect a stamp as you go.</p>{context}
        <a class="ed-text-link" href="/archive/objects/">Browse all {len(ARTIFACTS)} objects →</a>
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
          <a class="resource-link" href="{esc(item["url"])}" target="_blank" rel="noopener noreferrer">Visit website ↗</a>
        </article>"""


def search_records():
    records = []
    excluded_paths = {"/", "/search/", "/sitemap/", "/credits/"}
    for route in ROUTES:
        if route["path"] in excluded_paths or route["type"] in {"events", "stories", "objects"}:
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
                "href": archive.object_url(artifact),
                "tags": artifact["tags"] + [artifact["room"], artifact["dateRange"]["label"]],
                "external": False,
            }
        )
    for event in archive.EVENTS:
        object_tags=[tag for id in event['objectIds'] for tag in [id,ARTIFACT_BY_ID[id]['title'],*ARTIFACT_BY_ID[id]['tags']]]
        records.append({"id":"event-"+event["id"], "type":"events", "recordType":"event", "title":event["title"], "summary":event["date"]+" · "+event["region"]+" · "+event["summary"], "href":archive.event_url(event), "tags":[event["date"], event["date"][:4], event["region"], archive.CATEGORIES[event["category"]], archive.event_label(event), *object_tags, *event["paragraphs"]], "external":False})
    for story in archive.STORIES:
        records.append({"id":"story-"+story["id"], "type":"stories", "recordType":"story", "title":story["title"], "summary":story["summary"], "href":archive.story_url(story), "tags":[archive.CATEGORIES[story["category"]], *story.get('topics',[]), *[str(y['year']) for y in archive.YEARS.values() if story['id'] in y['storyIds']], *[p for section in story["sections"] for p in section["paragraphs"]]], "external":False})
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
        ("all", "Everything"),
        ("events", "Events"),
        ("stories", "Stories"),
        ("objects", "Objects"),
        ("zones", "Collections"),
        ("years", "Years"),
        ("tours", "Tours"),
        ("explore", "Resources"),
        ("highlights", "Guides"),
        ("community", "Community"),
    ]
    buttons = "\n".join(
        f'        <button class="resource-filter{" active" if key == "all" else ""}" '
        f'type="button" data-site-filter="{key}" aria-pressed="{"true" if key == "all" else "false"}">'
        f'{label} <span>{len(records) if key == "all" else counts.get(key, 0)}</span></button>'
        for key, label in categories
    )
    controls = f"""    <section class="panel resource-console" id="finder" aria-label="Search controls">
      <div class="resource-console-grid">
        <div><p class="eyebrow">SEARCH THE 90s</p><h2>Find your next memory</h2><p>Try a name, a year, or an object. Results update as you type; choose a collection below to narrow them.</p></div>
        <div class="resource-search-wrap">
          <label for="siteSearchInput">Search the archive</label>
          <input id="siteSearchInput" type="search" placeholder="try: Mosaic, cassette, Blockbuster, GeoCities…" autocomplete="off" />
        </div>
      </div>
      <div class="site-filter-row" aria-label="Filter results">
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
          <span>{esc(dict(categories).get(item['type'],item['recordType'])).upper()}{' · EXTERNAL ↗' if item['external'] else ''}</span>
          <h3>{esc(item["title"])}</h3>
          <p>{esc(item["summary"])}</p>
        </a>"""
        )
    results = f"""    <section class="panel resource-directory" aria-labelledby="searchResultsTitle">
      <p class="eyebrow">Results</p>
      <h2 id="searchResultsTitle">Events, stories, objects, and places to explore</h2>
      <p class="resource-count" id="siteSearchCount" aria-live="polite" aria-atomic="true">Showing {len(records)} matches.</p>
      <div class="chart-year-grid site-search-grid" id="siteSearchGrid">
{chr(10).join(cards)}
      </div>
      <div class="ar-empty resource-notes" id="siteSearchNoResults" hidden>
        <h3>No memory found under that label.</h3>
        <p>Try a shorter word, clear the filters, or let the museum choose.</p>
        <div class="hero-actions"><button class="button" type="button" data-search-clear>Clear search</button><a class="button" href="/surprise/" data-surprise-trigger>Surprise me</a><a class="button" href="/sitemap/">Open site map</a></div>
      </div>
    </section>"""
    return controls, results


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
        connections=''
        if stop.get('storyId'):
            story=next(s for s in archive.STORIES if s['id']==stop['storyId'])
            connections+=f'<a href="{archive.story_url(story)}">Read: {esc(story["title"])} →</a>'
        if stop.get('eventId'):
            event=archive.EVENT_BY_ID[stop['eventId']]
            connections+=f'<a href="{archive.event_url(event)}">On the calendar: {esc(event["title"])} →</a>'
        stops.append(
            f"""      <article class="tour-stop" id="{esc(stop["id"])}" data-tour-stop="{esc(stop["id"])}" data-tour-number="{stop["number"]}">
        <p class="tour-step-label">Stop {stop["number"]} of {total}</p>
        <h2>{esc(stop["title"])}</h2>
        <p class="tour-curator-text">{esc(stop["curatorText"])}</p>
        <p>{esc(stop["detail"])}</p>
        <div class="tour-artifact-row">{artifacts}</div>
{interaction}
        <p><a href="{esc(stop["exhibitHref"])}">{esc(stop["exhibitLabel"])} →</a></p>
        <nav class="ar-detail-links" aria-label="More from this stop">{connections}</nav>
        <div class="tour-controls">
          {back}
          <button class="button primary" type="button" data-tour-next>{next_label}</button>
          <a class="button subtle" href="/">Exit tour</a>
        </div>
      </article>"""
        )
    return f"""  <main id="main-content" class="ed-main tour-main" data-tour-id="{esc(tour["id"])}">
    <section class="ar-heading tour-hero">
      <div class="page-pad">

        <p class="eyebrow">A guided tour · about {tour["durationMinutes"]} minutes</p>
        <h1>{esc(tour["title"])}</h1>
        <p class="lede">{esc(tour["description"])}</p>
        <div class="tour-progress" role="progressbar" aria-label="Tour progress" aria-valuemin="1" aria-valuemax="{total}" aria-valuenow="1"><span data-tour-progress-bar></span></div>
        <p class="tour-progress-copy" aria-live="polite" data-tour-progress-copy>Ready for stop 1 of {total}.</p>
      </div>
    </section>
    <section class="tour-deck" data-tour-deck>
{chr(10).join(stops)}
    </section>
    <section class="panel" data-tour-finish hidden><h2>You made it through Before the Feed.</h2><p>Your stamp is in your Museum Passport. Keep following the connections.</p><div class="dialog-actions"><button type="button" class="button primary" data-tour-passport>See my Passport</button><a class="button" href="/zones/internet-culture/">Explore Internet Culture</a><a class="button" href="/surprise/">Find a surprise</a></div></section>
  </main>"""


def render_surprise_main() -> str:
    pool = discovery.surprise_pool()
    eligible = [item for kind in discovery.KINDS for item in [i for i in pool if i['kind']==kind][:2]]
    envelopes = []
    for index, item in enumerate(eligible, 1):
        envelopes.append(
            f"""      <a class="mystery-envelope" href="{esc(item["target"])}" data-fallback-artifact="{esc(item["id"])}">
        <span aria-hidden="true">✉ {index:02d}</span>
        <strong>Mystery envelope</strong>
        <small>{esc(item["dateLabel"])} · {esc(item["room"])}</small>
      </a>"""
        )
    return f"""  <main id="main-content" class="ed-main surprise-page">
    <section class="ar-heading">
      <div class="page-pad">

        <p class="eyebrow">TAKE A DETOUR</p>
        <h1>Open a mystery memory.</h1>
        <p class="lede">One click, one unexpected connection. Find a story, an object, a defining moment, a year, a collection, or a tour. The last three picks stay out of the shuffle.</p>
        <button class="button primary" type="button" data-surprise-trigger-button>Load a random memory</button>
      </div>
    </section>
    <section class="panel">
      <div class="section-heading compact-heading"><p class="eyebrow">PICK A MEMORY</p><h2>Choose one without reading the label.</h2></div>
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
        license_label = esc(media['license'])
        if media.get('licenseUrl'):
            license_label = f'<a href="{esc(media["licenseUrl"])}">{license_label}</a>'
        credits.append(
            f"<li><strong>{esc(item['title'])}</strong> — {esc(media['credit'])}; "
            f"{license_label}; {source}</li>"
        )
    return f"""  <main id="main-content" class="ed-main">
    <section class="ar-heading">
      <div class="page-pad"><p class="eyebrow">Source labels</p><h1>Credits, licenses, and recreations.</h1><p class="lede">90s.land distinguishes sourced media, editorial interpretation, and original interface recreations.</p></div>
    </section>
    <section class="panel credits-panel">
      <h2>Artifact media</h2>
      <ul class="credits-list">{''.join(credits)}</ul>
      <h2>Type</h2>
      <p>The editorial interface uses locally hosted Jersey 10, Barlow, and Barlow Condensed from the <a href="https://github.com/google/fonts">Google Fonts repository</a>. Their SIL Open Font Licenses are included: <a href="/assets/fonts/OFL-jersey10.txt">Jersey 10</a>, <a href="/assets/fonts/OFL-barlow.txt">Barlow</a>, and <a href="/assets/fonts/OFL-barlowcondensed.txt">Barlow Condensed</a>.</p>
      <p>The content-specific sharing cards use the same Jersey 10 and Barlow family as the museum. The earlier museum-case graphic uses Press Start 2P and Space Mono under their <a href="/assets/fonts/OFL-Press-Start-2P.txt">Press Start 2P</a> and <a href="/assets/fonts/OFL-Space-Mono.txt">Space Mono</a> licenses. Those earlier fonts are part of that image, not the page interface.</p>
      <h2>Editorial status</h2>
      <p><strong>Verified</strong> artifacts use a source trail. <strong>Editorial</strong> objects are clearly labeled original recreations. Items marked <strong>needs source</strong> are excluded from Surprise Me and guided tours.</p>
      <h2>Image adaptations</h2><p>Photographs are locally resized and may be cropped by the page layout. Sharing cards combine reviewed collection imagery or labeled editorial illustrations with original museum typography; each card names the creator and license. Credits above link to the original file records; Creative Commons ShareAlike terms continue to apply to adapted images. Original interface recreations are labeled separately. The Y2K office photograph is credited to the Government of Japan, Prime Minister’s Office website, under its Standard Terms of Use 2.0, compatible with CC BY 4.0.</p>
      <h2>Sharing artwork</h2>
      <p>The Home, 1996 Timeline, Games, Music, Movies &amp; TV, Tech, and Culture hero collages are original AI-generated editorial illustrations created with OpenAI on September 26–27, 2026. They evoke the decade and are not documentary photographs or evidence of release dates. Brands and illustrated products belong to their respective owners. The palm/sunset brand mark and interface icons are original SVG artwork.</p>
      <p>Content-specific sharing cards use reviewed object imagery, clearly labeled editorial illustrations, or original graphic compositions. The earlier museum-case sharing graphic combines an original AI-generated illustration created with OpenAI and lettering in Press Start 2P and Space Mono.</p>
    </section>
  </main>"""


def page_document(route: dict, main: str, body_class: str = "") -> str:
    main = product_pages.finish_main(route, main, render_artifact_shelf)
    body_class = 'editorial-body ' + body_class
    body_attr = f' class="{esc(body_class)}"' if body_class else ""
    search_font = ('  <link rel="preload" href="/assets/fonts/BarlowCondensed-SemiBold.woff2" as="font" type="font/woff2" crossorigin />\n'
                   if route['path'] == '/search/' else '')
    return f"""<!doctype html>
<html lang="en" class="no-js">
<head>
  <meta charset="utf-8" />
  <script>document.documentElement.classList.replace('no-js','js');</script>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <link rel="preload" href="/assets/fonts/Jersey10-Regular.woff2" as="font" type="font/woff2" crossorigin />
  <link rel="preload" href="/assets/fonts/Barlow-Regular.woff2" as="font" type="font/woff2" crossorigin />
  <link rel="preload" href="/assets/fonts/BarlowCondensed-Bold.woff2" as="font" type="font/woff2" crossorigin />
{search_font}{region("head", render_head(route))}
  <link rel="stylesheet" href="/styles.css?v=launch-phase3" />
  <link rel="stylesheet" href="/editorial.css?v=launch-phase3" />
  <link rel="stylesheet" href="/archive.css?v=launch-phase3" />
  <link rel="stylesheet" href="/hub.css?v=launch-phase3" />
</head>
<body{body_attr} data-route="{esc(route["path"])}" data-room="{esc(route_room(route))}">
  <a class="skip-link" href="#main-content">Skip to museum content</a>
{editorial.shell_header(route)}
{main}
{editorial.discovery()}
{editorial.shell_footer()}
{editorial.directory()}
{region("shared-ui", render_shared_ui())}
  <script type="module" src="/js/app.js?v=launch-phase3"></script>
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
    main = """  <main id="main-content" class="ed-main error-page">
    <section class="ar-heading">
      <div class="page-pad">
        <p class="eyebrow">Missing exhibit</p>
        <h1>This memory fell behind the filing cabinet.</h1>
        <p class="lede">The route does not exist, but the museum is still open.</p>
        <div class="hero-actions"><a class="button primary" href="/">Return home</a><a class="button" href="/surprise/">Surprise me</a><a class="button" href="/sitemap/">Open the map</a></div>
      </div>
    </section>
  </main>"""
    return page_document(route, main, "error-body")


def build_outputs() -> dict[Path, str]:
    outputs = {}
    for route in ROUTES:
        if route["type"] == "years":
            outputs[route_to_file(route["path"])] = page_document(route, archive_pages.timeline(route), "editorial-body editorial-timeline")
        elif route["path"] == "/this-week/":
            outputs[route_to_file(route["path"])] = page_document(route, archive_pages.weekly(), "editorial-body")
        elif route["path"] in {"/stories/", "/events/", "/archive/objects/"}:
            outputs[route_to_file(route["path"])] = page_document(route, archive_pages.archive_index(route, render_media), "editorial-body")
        elif route["type"] in {"events", "stories", "objects"}:
            outputs[route_to_file(route["path"])] = page_document(route, archive_pages.detail(route, render_media), "editorial-body")
        elif route["path"] in hub_pages.HUBS:
            outputs[route_to_file(route["path"])] = page_document(route, hub_pages.hub(route), "editorial-body")
        elif route["path"] == "/timeline/":
            outputs[route_to_file(route["path"])] = page_document(route, hub_pages.timeline_index(route), "editorial-body")
        elif route["path"] in editorial.CORE:
            outputs[route_to_file(route["path"])] = page_document(
                route, editorial.main(route), f'editorial-body editorial-{editorial.CORE[route["path"]]}'
            )
        elif route["path"] == "/surprise/":
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
            outputs[route_to_file(route["path"])] = page_document(route, product_pages.page(route, render_search_sections, render_resource_card, render_homepage_builder))

        path = route_to_file(route["path"])
        outputs[path] = media_variants.optimize_html(outputs[path])

    outputs[ROOT / "404.html"] = media_variants.optimize_html(render_404())
    sitemap_urls = "\n".join(
        f"  <url><loc>{SITE_URL}{esc(route['path'])}</loc></url>" for route in ROUTES if launch_meta.metadata(route)['indexable']
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
    outputs[ROOT / "data/routes.json"] = json.dumps(ROUTES, ensure_ascii=False, indent=2) + "\n"
    outputs[ROOT / "data/editorial-index.json"] = json.dumps(archive.browser_index(), ensure_ascii=False, indent=2) + "\n"
    # Only the fields needed by browser interactions cross the public boundary.
    # Authoring catalogs (including review/source metadata) remain in data/.
    outputs[ROOT / "assets/runtime/week.json"] = json.dumps(
        {"events": archive.browser_index()["events"]}, ensure_ascii=False, indent=2
    ) + "\n"
    outputs[ROOT / "assets/runtime/surprise.json"] = json.dumps(discovery.surprise_pool(), ensure_ascii=False, indent=2) + "\n"
    outputs[ROOT / "data/search-index.json"] = json.dumps(search_records(), ensure_ascii=False, indent=2) + "\n"
    outputs[ROOT / "manifest.webmanifest"] = json.dumps(manifest, indent=2) + "\n"
    return outputs


def validate_catalogs() -> list[str]:
    return validate_existing_catalogs(ROOT, routes=ROUTES) + archive.validate()


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
