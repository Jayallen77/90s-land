#!/usr/bin/env python3
"""Check the resource catalog with HEAD and a small GET fallback."""

from __future__ import annotations

import json
import ssl
import urllib.error
import urllib.request
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESOURCES = json.loads((ROOT / "data/resources.json").read_text())
OUTPUT = ROOT / "reports/external-resource-check.json"
USER_AGENT = "90s.land local QA link checker/1.0 (+https://90s.land/)"
BLOCKED_CODES = {401, 403, 406, 418, 429, 451}


def request(url: str, method: str):
    req = urllib.request.Request(
        url,
        method=method,
        headers={"User-Agent": USER_AGENT, "Accept": "text/html,*/*;q=0.8"},
    )
    context = ssl.create_default_context()
    with urllib.request.urlopen(req, timeout=12, context=context) as response:
        if method == "GET":
            response.read(1024)
        return response.status, response.geturl()


def check(item: dict) -> dict:
    attempts = []
    final_url = item["url"]
    status_code = None
    error = None
    for method in ("HEAD", "GET"):
        try:
            status_code, final_url = request(item["url"], method)
            attempts.append({"method": method, "status": status_code})
            if status_code < 400:
                return {
                    "id": item["id"],
                    "title": item["title"],
                    "url": item["url"],
                    "finalUrl": final_url,
                    "classification": "reachable",
                    "attempts": attempts,
                }
        except urllib.error.HTTPError as exc:
            status_code = exc.code
            final_url = exc.geturl()
            error = str(exc.reason)
            attempts.append({"method": method, "status": status_code})
            if method == "HEAD":
                continue
        except Exception as exc:  # network and TLS errors need reporting, not removal
            error = f"{type(exc).__name__}: {exc}"
            attempts.append({"method": method, "error": error})
            if method == "HEAD":
                continue

    if status_code in BLOCKED_CODES:
        classification = "blocked-or-rate-limited"
    elif status_code in {404, 410}:
        classification = "missing"
    else:
        classification = "unresolved"
    return {
        "id": item["id"],
        "title": item["title"],
        "url": item["url"],
        "finalUrl": final_url,
        "classification": classification,
        "attempts": attempts,
        "error": error,
    }


OUTPUT.parent.mkdir(parents=True, exist_ok=True)
results = []
with ThreadPoolExecutor(max_workers=12) as executor:
    futures = {executor.submit(check, item): item for item in RESOURCES}
    for future in as_completed(futures):
        results.append(future.result())
results.sort(key=lambda item: item["id"])

summary = Counter(item["classification"] for item in results)
payload = {
    "checkedAt": datetime.now(timezone.utc).isoformat(),
    "method": "HEAD followed by GET fallback, 12-second timeout",
    "summary": dict(sorted(summary.items())),
    "results": results,
}
OUTPUT.write_text(json.dumps(payload, indent=2) + "\n")
print(json.dumps(payload["summary"], indent=2))
print(f"saved {OUTPUT}")
