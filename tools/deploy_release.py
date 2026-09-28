#!/usr/bin/env python3
"""Publish a verified release and atomically switch current; never configure Caddy."""
import argparse
import json
import os
from pathlib import Path
import shutil
import tempfile

from build_release import DEFAULT_OUTPUT, ROOT, locked, verify


def managed_current(site_root):
    current = site_root / 'current'
    if not current.is_symlink():
        if current.exists():
            raise ValueError('current already exists and is not a managed symlink; no files were replaced')
        return None
    target = current.resolve(strict=True)
    if target.parent.parent != site_root / 'releases' or target.name != 'public':
        raise ValueError('current points outside managed releases; no files were replaced')
    manifest = verify(target.parent)
    if target.parent.name != manifest['contentDigest']:
        raise ValueError('Current release directory does not match its digest')
    return str(target.parent)


def publish(release, site_root):
    release = Path(release).resolve()
    requested_root = Path(site_root).absolute()
    if requested_root.is_symlink():
        raise ValueError('Site root must not itself be a symlink')
    site_root = requested_root.resolve()
    if site_root.is_relative_to(ROOT.resolve()) or ROOT.resolve().is_relative_to(site_root):
        raise ValueError('Site root must be separate from the Git checkout')
    if site_root.is_relative_to(release) or release.is_relative_to(site_root / 'current'):
        raise ValueError('Source release must not contain the site root or use current')
    manifest = verify(release)
    created_root = not site_root.exists()
    site_root.mkdir(parents=True, exist_ok=True)
    if created_root:
        site_root.chmod(0o755)
    with locked(site_root / '.deploy.lock'):
        releases = site_root / 'releases'
        if releases.is_symlink():
            raise ValueError('releases must not be a symlink')
        previous = managed_current(site_root)
        releases.mkdir(exist_ok=True)
        releases.chmod(0o755)
        target = releases / manifest['contentDigest']
        if target.is_symlink():
            raise ValueError('Release directory must not be a symlink')
        if target.exists():
            if verify(target)['contentDigest'] != manifest['contentDigest']:
                raise ValueError('Existing release digest mismatch')
        else:
            with tempfile.TemporaryDirectory(prefix='.90s-publish-', dir=site_root) as work:
                staged = Path(work) / 'release'
                staged.mkdir()
                # Copy only the verified package, never surrounding source/deploy files.
                shutil.copytree(release / 'public', staged / 'public')
                for name in ('release-manifest.json', '90s-land.tar.gz', '90s-land.tar.gz.sha256'):
                    shutil.copyfile(release / name, staged / name)
                verify(staged)
                # Caddy needs traversal/read access even with a restrictive deploy-user umask.
                staged.chmod(0o755)
                for path in staged.rglob('*'):
                    path.chmod(0o755 if path.is_dir() else 0o644)
                staged.rename(target)
        # Same-filesystem rename of a symlink is atomic on the supported Linux/macOS hosts.
        with tempfile.TemporaryDirectory(prefix='.90s-publish-', dir=site_root) as work:
            pointer = Path(work) / 'current'
            pointer.symlink_to(Path('releases') / target.name / 'public')
            os.replace(pointer, site_root / 'current')
        return {'contentDigest': manifest['contentDigest'], 'current': str(site_root / 'current'),
                'release': str(target), 'previousRelease': previous}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--release', type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument('--site-root', type=Path, required=True,
                        help='Dedicated release store outside the checkout; Caddy must already serve its current/ path')
    args = parser.parse_args()
    print(json.dumps(publish(args.release, args.site_root), indent=2))


if __name__ == '__main__':
    main()
