#!/usr/bin/env python3
"""Audit a verified package over HTTP; no source checkout or server changes needed."""
import argparse
import gzip
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from build_release import DEFAULT_OUTPUT, ROOT, verify

EXCLUDED = [
    '/does-not-exist/', '/.git/config', '/.git/HEAD', '/.git/index', '/.git/objects/',
    '/%2egit/config', '/.env', '/.env.production', '/.gitignore', '/.codex/config.toml',
    '/.agents/', '/AGENTS.md', '/README.md', '/package.json', '/pnpm-lock.yaml',
    '/requirements-dev.txt', '/playwright.config.mjs', '/node_modules/',
    '/content/pages.json', '/content/deep-links.json', '/content/editorial/catalog.json', '/content/editorial/modules.json',
    '/content/migration/', '/data/artifacts.json', '/data/editorial-index.json',
    '/content/research/notion-2026-10-01.json', '/content/research/expansion/selected-media.json',
    '/data/routes.json', '/data/resources.json', '/data/search-index.json', '/data/social-cards.json',
    '/data/asset-variants.json', '/data/tours.json', '/data/stamps.json', '/data/navigation.json',
    '/tools/build_release.py', '/tools/deploy_release.py', '/tools/product_pages.py', '/tests/test_release.py',
    '/docs/RELEASE.md', '/docs/design/UNIFIED_SITE.md', '/reports/PHASE_5_QA.md', '/reports/baseline/phase-1/',
    '/release-manifest.json', '/90s-land.tar.gz', '/90s-land.tar.gz.sha256',
    '/dist/release/release-manifest.json', '/releases/', '/js/app.js.map',
    '/assets/editorial/home-hero-original.png', '/assets/editorial/movies-hero-source.png',
    '/assets/.git/config', '/assets/runtime/catalog.json', '/assets/runtime/week.json.bak',
    '/data/artifacts.json.gz', '/content/editorial/catalog.json.gz',
    '/%2e%2e/.git/config', '/assets/%2e%2e/%2e%2e/.git/config',
]


def audit(base_url, release):
    manifest = verify(release)
    base_url = base_url.rstrip('/')

    def head(path):
        try:
            with urlopen(Request(base_url + path, method='HEAD'), timeout=15) as response:
                return path, response.status
        except HTTPError as error:
            return path, error.code
        except URLError as error:
            return path, str(error.reason)

    with ThreadPoolExecutor(max_workers=6) as pool:
        status = list(pool.map(head, manifest['routePaths']))
        missing = list(pool.map(head, EXCLUDED))
        cards = list(pool.map(head, ['/'+name for name in manifest['files'] if name.startswith('assets/generated/share/') and name.endswith('.jpg')]))
    errors = [f'{path}: {code}' for path, code in status if code != 200]
    errors.extend(f'Sharing image {path}: {code}' for path, code in cards if code != 200)
    errors.extend(f'Expected 404: {path}: {code}' for path, code in missing if code != 404)
    samples = ['/', '/timeline/1996/', '/js/app.js', '/editorial.css',
               '/assets/runtime/week.json', '/assets/runtime/surprise.json']
    for path in samples:
        name = path.lstrip('/') + ('index.html' if path.endswith('/') else '')
        try:
            for encoding in ('identity', 'gzip'):
                request = Request(base_url + path, headers={'Accept-Encoding': encoding})
                with urlopen(request, timeout=15) as response:
                    body = response.read()
                    actual_encoding = response.headers.get('Content-Encoding')
                    if encoding == 'gzip':
                        if actual_encoding != 'gzip':
                            errors.append('Missing gzip: ' + path)
                        else:
                            body = gzip.decompress(body)
                        if 'accept-encoding' not in response.headers.get('Vary', '').lower():
                            errors.append('Missing Vary: ' + path)
                    elif actual_encoding not in (None, 'identity'):
                        errors.append('Unexpected encoding for identity: ' + path)
                    if hashlib.sha256(body).hexdigest() != manifest['files'][name]['sha256']:
                        errors.append('Served content mismatch: ' + path + ' (' + encoding + ')')
        except (OSError, ValueError, EOFError) as error:
            errors.append(f'{path}: {error}')
    return {'routes': len(status), 'routesPassed': sum(code == 200 for _, code in status),
            'shareCards':len(cards), 'shareCardsPassed':sum(code == 200 for _,code in cards),
            'excludedPaths': dict(missing), 'encodingSamples': len(samples) * 2,
            'contentDigest': manifest['contentDigest'], 'errors': errors}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-url', default='http://127.0.0.1:4174')
    parser.add_argument('--release', type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument('--output', type=Path, default=ROOT / 'dist/deployment-http.json')
    args = parser.parse_args()
    result = audit(args.base_url, args.release)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
    return bool(result['errors'])


if __name__ == '__main__':
    raise SystemExit(main())
