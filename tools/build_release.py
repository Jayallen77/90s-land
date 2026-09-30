#!/usr/bin/env python3
"""Build a verified public-only package using Python 3.10+ and no third-party tools."""
import argparse
from contextlib import contextmanager
import fcntl
import gzip
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / 'dist/release'
TEXT_TYPES = {'.html', '.css', '.js', '.json', '.xml', '.txt', '.svg', '.webmanifest'}
ROOT_FILES = {'404.html', 'robots.txt', 'sitemap.xml', 'manifest.webmanifest',
              'styles.css', 'editorial.css', 'archive.css', 'hub.css'}
ROUTE_PREFIXES = {'archive', 'credits', 'events', 'guestbook', 'search', 'sitemap',
                  'stories', 'surprise', 'this-week', 'timeline', 'tours', 'webring', 'zones'}
JS_FILES = {f'js/{name}.js' for name in (
    'announce', 'app', 'archive', 'date-utils', 'editorial', 'guestbook', 'hubs',
    'navigation', 'pagination', 'passport', 'resources', 'search', 'storage', 'surprise', 'tour')}
RUNTIME_FILES = {'assets/runtime/week.json', 'assets/runtime/surprise.json'}
MEDIA_TYPES = {'.png', '.jpg', '.jpeg', '.webp', '.avif', '.svg', '.gif', '.ico'}
FONT_LICENSES = {'OFL-Press-Start-2P.txt', 'OFL-Space-Mono.txt', 'OFL-barlow.txt',
                 'OFL-barlowcondensed.txt', 'OFL-jersey10.txt'}


def safe_relative(name):
    """Validate the lexical path BEFORE resolving it (including encoded URLs)."""
    if not isinstance(name, str) or not name or '\\' in name:
        raise ValueError(f'Unsafe public path: {name}')
    path = Path(name)
    if path.is_absolute() or any(part in ('', '.', '..') or part.startswith('.')
                                 for part in name.split('/')):
        raise ValueError(f'Unsafe public path: {name}')
    return path


def route_files(routes):
    files = set()
    for route in routes:
        if not isinstance(route, str) or not re.fullmatch(r'/(?:[a-z0-9-]+/)*', route):
            raise ValueError(f'Invalid route: {route}')
        path = Path(route.lstrip('/')) / 'index.html'
        if route != '/' and path.parts[0] not in ROUTE_PREFIXES:
            raise ValueError(f'Private source route: {route}')
        if path in files:
            raise ValueError(f'Duplicate route: {route}')
        files.add(path)
    if Path('index.html') not in files:
        raise ValueError('Missing home route')
    return files


def public_path(name, html_files):
    path = safe_relative(name)
    if path in html_files or name in ROOT_FILES | JS_FILES | RUNTIME_FILES:
        return path
    if len(path.parts) >= 3 and path.parts[0] == 'assets':
        if path.name.endswith(('-source.png', '-original.png')):
            raise ValueError(f'Private source linked as runtime: {name}')
        if path.parts[1] in {'editorial', 'generated', 'media', 'gifs', 'icons'} and path.suffix in MEDIA_TYPES:
            return path
        if path.parts[1] == 'fonts' and len(path.parts) == 3:
            if path.suffix in {'.woff2', '.ttf'} or path.name in FONT_LICENSES:
                return path
    raise ValueError(f'Private source or unapproved public dependency: {name}')


def regular_file(root, relative):
    """Never follow symlinks, even when their resolved target is inside the root."""
    relative = safe_relative(str(relative))
    current = root
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError(f'Symlink in public input: {relative}')
    if not current.is_file():
        raise ValueError(f'Missing dependency: {relative}')
    return current


class References(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.urls = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        for key in ('href', 'src', 'poster'):
            if values.get(key):
                self.urls.append(values[key])
        for key in ('srcset', 'imagesrcset'):
            self.urls.extend(value.strip().split()[0] for value in values.get(key, '').split(',') if value.strip())


def dependencies(root, relative, html_files=None):
    html_files = html_files if html_files is not None else {Path('index.html')}
    path = regular_file(root, relative)
    if path.suffix not in TEXT_TYPES:
        return set()
    source = path.read_text(encoding='utf-8')
    urls = []
    if path.suffix == '.html':
        parser = References()
        parser.feed(source)
        urls = parser.urls
    elif path.suffix == '.css':
        urls = re.findall(r'url\([\s\"\']*([^\)\"\']+)', source)
    elif path.suffix == '.js':
        urls = re.findall(r'(?:from\s*|import\s*\(\s*|fetch\s*\(\s*)[\"\']([^\"\']+)', source)
    elif path.suffix in ('.json', '.webmanifest'):
        urls = re.findall(r'/(?:assets|data|js)/[^\s\"\',]+', source)
    found = set()
    for url in urls:
        parts = urlsplit(url)
        if parts.scheme or parts.netloc or not parts.path:
            continue
        raw = unquote(parts.path)
        # Ordinary ./module.js imports are valid; parent traversal is not needed here.
        if raw.startswith('./'):
            raw = raw[2:]
        raw_parts = raw.lstrip('/').rstrip('/')
        if raw_parts:
            safe_relative(raw_parts)
        rel = Path(raw_parts) if raw.startswith('/') else relative.parent / raw_parts
        candidate = root / rel
        if candidate.is_dir() or raw.endswith('/'):
            rel = rel / 'index.html'
        public_path(str(rel), html_files)
        regular_file(root, rel)
        found.add(rel)
    return found


def collect_files(root):
    routes = [r['path'] for r in json.loads((root / 'data/routes.json').read_text())]
    html_files = route_files(routes)
    seeds = html_files | {Path(p) for p in ('404.html', 'robots.txt', 'sitemap.xml',
                                           'manifest.webmanifest', 'assets/generated/og-card.png')}
    included = set()
    pending = list(seeds)
    while pending:
        path = pending.pop()
        if path in included:
            continue
        public_path(str(path), html_files)
        regular_file(root, path)
        included.add(path)
        pending.extend(dependencies(root, path, html_files) - included)
    return included


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(files):
    return hashlib.sha256(json.dumps(files, sort_keys=True).encode()).hexdigest()


def verify_runtime_data(web):
    surprise = web / 'assets/runtime/surprise.json'
    if surprise.exists():
        rows = json.loads(surprise.read_text())
        if not isinstance(rows, list) or any(set(row) != {'id', 'title', 'teaser', 'dateLabel', 'room', 'target'} for row in rows):
            raise ValueError('Unexpected fields in public Surprise data')
    week = web / 'assets/runtime/week.json'
    if week.exists():
        data = json.loads(week.read_text())
        fields = {'id', 'title', 'date', 'category', 'region', 'summary', 'url', 'image'}
        image_fields = {'src', 'alt', 'width', 'height', 'srcset', 'sizes'}
        if set(data) != {'events'} or any(set(event) != fields or
                (event['image'] is not None and not set(event['image']).issubset(image_fields))
                for event in data['events']):
            raise ValueError('Unexpected fields in public week data')


def verify(directory):
    directory = Path(directory)
    manifest = json.loads(regular_file(directory, Path('release-manifest.json')).read_text())
    if manifest.get('schemaVersion') != 2:
        raise ValueError('Unsupported release manifest; rebuild with the current builder')
    web = directory / 'public'
    if web.is_symlink() or not web.is_dir():
        raise ValueError('Public directory must be a real directory')
    expected = manifest['files']
    html_files = route_files(manifest['routePaths'])
    if manifest['contentDigest'] != digest(expected):
        raise ValueError('Manifest content digest mismatch')
    if manifest['routes'] != len(html_files):
        raise ValueError('Manifest route count mismatch')
    actual = set()
    expected_dirs = {parent.as_posix() for name in expected for parent in Path(name).parents}
    for p in web.rglob('*'):
        if p.is_symlink() or not (p.is_dir() or p.is_file()):
            raise ValueError(f'Non-regular public entry: {p.relative_to(web)}')
        if p.is_dir() and p.relative_to(web).as_posix() not in expected_dirs:
            raise ValueError(f'Unexpected public directory: {p.relative_to(web)}')
        if p.is_file():
            actual.add(p.relative_to(web).as_posix())
    if actual != set(expected):
        raise ValueError('Public file inventory differs from manifest')
    if not {str(p) for p in html_files}.issubset(expected):
        raise ValueError('Missing route from release')
    if manifest['runtimeFiles'] != sum(not p.endswith('.gz') for p in expected):
        raise ValueError('Manifest runtime count mismatch')
    verify_runtime_data(web)
    for name, record in expected.items():
        safe_relative(name)
        original = name[:-3] if name.endswith('.gz') else name
        public_path(original, html_files)
        p = regular_file(web, Path(name))
        if sha(p) != record['sha256'] or p.stat().st_size != record['bytes']:
            raise ValueError('Checksum mismatch: ' + name)
        if name.endswith('.gz'):
            if original not in expected or Path(original).suffix not in TEXT_TYPES:
                raise ValueError('Unexpected compressed file: ' + name)
            if gzip.decompress(p.read_bytes()) != regular_file(web, Path(original)).read_bytes():
                raise ValueError('Compressed content mismatch: ' + name)
        else:
            for dep in dependencies(web, Path(name), html_files):
                if str(dep) not in expected:
                    raise ValueError('Unpackaged dependency: ' + str(dep))
    archive = regular_file(directory, Path('90s-land.tar.gz'))
    checksum = regular_file(directory, Path('90s-land.tar.gz.sha256'))
    if sha(archive) != checksum.read_text().split()[0]:
        raise ValueError('Release archive checksum mismatch')
    return manifest


@contextmanager
def locked(path):
    """Serialize cooperating builders/publishers without stale PID lock files."""
    if path.is_symlink():
        raise ValueError(f'Lock must not be a symlink: {path}')
    with path.open('a') as handle:
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise ValueError(f'Another release operation holds {path}') from error
        try:
            yield
        finally:
            fcntl.flock(handle, fcntl.LOCK_UN)


def write_package(root, directory):
    web = directory / 'public'
    web.mkdir()
    paths = collect_files(root)
    for relative in sorted(paths):
        target = web / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(regular_file(root, relative), target)
        if target.suffix in TEXT_TYPES and target.stat().st_size > 1024:
            # GzipFile fixes the OS header byte across Python versions/platforms.
            with target.with_name(target.name + '.gz').open('wb') as output:
                with gzip.GzipFile(filename='', mode='wb', fileobj=output, mtime=0, compresslevel=9) as compressed:
                    compressed.write(target.read_bytes())
    files = {p.relative_to(web).as_posix(): {'sha256': sha(p), 'bytes': p.stat().st_size}
             for p in sorted(web.rglob('*')) if p.is_file()}
    routes = [r['path'] for r in json.loads((root / 'data/routes.json').read_text())]
    manifest = {'schemaVersion': 2, 'contentDigest': digest(files), 'routes': len(routes),
                'routePaths': sorted(routes), 'runtimeFiles': len(paths), 'files': files}
    (directory / 'release-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    archive = directory / '90s-land.tar.gz'
    with archive.open('wb') as output:
        with gzip.GzipFile(filename='', mode='wb', fileobj=output, mtime=0) as compressed:
            with tarfile.open(fileobj=compressed, mode='w') as tar:
                for path in [directory / 'release-manifest.json'] + sorted(p for p in web.rglob('*') if p.is_file()):
                    entry = tar.gettarinfo(str(path), str(path.relative_to(directory)))
                    entry.uid = entry.gid = entry.mtime = 0
                    entry.uname = entry.gname = ''
                    entry.mode = 0o644
                    with path.open('rb') as stream:
                        tar.addfile(entry, stream)
    (directory / '90s-land.tar.gz.sha256').write_text(sha(archive) + '  90s-land.tar.gz\n')
    verify(directory)
    return manifest


def build(root, directory):
    root = Path(root).resolve()
    directory = Path(os.path.abspath(directory))
    if directory.is_symlink():
        raise ValueError('Output path must not be a symlink')
    directory = directory.resolve()
    if root.is_relative_to(directory) or (directory.is_relative_to(root) and not directory.is_relative_to(root / 'dist')):
        raise ValueError('Output must be under dist/ or outside the source checkout')
    directory.parent.mkdir(parents=True, exist_ok=True)
    with locked(directory.parent / f'.{directory.name}.lock'):
        if directory.exists() and any(directory.iterdir()):
            # Only replace our own verified build output, never an unrelated directory.
            verify(directory)
        with tempfile.TemporaryDirectory(prefix='.90s-build-', dir=directory.parent) as work:
            staging = Path(work) / 'next'
            staging.mkdir()
            manifest = write_package(root, staging)
            previous = Path(work) / 'previous'
            try:
                if directory.exists():
                    directory.rename(previous)
                staging.rename(directory)
            except BaseException:
                if previous.exists() and not directory.exists():
                    previous.rename(directory)
                raise
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument('--check', action='store_true', help='Verify an existing package without rebuilding')
    args = parser.parse_args()
    if args.check:
        manifest = verify(args.output)
    else:
        # Generated HTML/media are committed; VPS builds need only the standard library.
        # Fail on stale authoring outputs rather than silently publishing a mixed revision.
        for script in ('optimize_assets.py', 'render_site.py'):
            subprocess.run([sys.executable, '-B', str(ROOT / 'tools' / script), '--check'], check=True)
        manifest = build(ROOT, args.output)
    print(json.dumps({'output': str(args.output.absolute() / 'public'),
                      **{k: v for k, v in manifest.items() if k not in ('files', 'routePaths')}}, indent=2))


if __name__ == '__main__':
    main()
