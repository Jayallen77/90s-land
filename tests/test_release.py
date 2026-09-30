import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from build_release import build, collect_files, dependencies, sha, verify
from deploy_release import publish
from serve_release import gzip_accepted
from discovery import surprise_pool


def fixture(root):
    """A tiny standalone checkout to test deployment failure modes cheaply."""
    (root / 'data').mkdir(parents=True)
    (root / 'data/routes.json').write_text('[{"path":"/"}]')
    (root / 'assets/generated').mkdir(parents=True)
    (root / 'assets/generated/og-card.png').write_bytes(b'image fixture')
    for name in ('index.html', '404.html', 'robots.txt', 'sitemap.xml', 'manifest.webmanifest'):
        (root / name).write_text('{}' if name.endswith('webmanifest') else '<p>Fixture</p>')


class ReleaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.path = Path(cls.temp.name) / 'release'
        cls.manifest = build(ROOT, cls.path)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_release_contains_every_route_and_no_source_material(self):
        files = self.manifest['files']
        for route in json.loads((ROOT / 'data/routes.json').read_text()):
            self.assertIn(str(Path(route['path'].strip('/')) / 'index.html'), files)
        for name in files:
            self.assertNotIn(name.split('/')[0], {'data', 'content', 'reports', 'tests', 'tools', 'docs', 'node_modules', '.git'})
            self.assertFalse(any(part.startswith('.') for part in Path(name).parts))
            self.assertFalse(name.endswith(('-source.png', '-original.png', '.map')))
        self.assertIn('assets/runtime/week.json', files)
        self.assertIn('assets/runtime/surprise.json', files)
        self.assertIn('index.html.gz', files)
        verify(self.path)

    def test_browser_data_contains_only_published_interaction_fields(self):
        data = json.loads((self.path / 'public/assets/runtime/surprise.json').read_text())
        source = json.loads((ROOT / 'data/artifacts.json').read_text())
        eligible = [item for item in source if item['randomEligible'] and item['status'] != 'needs-source']
        self.assertEqual(data, surprise_pool())
        objects = [row for row in data if row['kind']=='object']
        self.assertEqual([a['id'] for a in objects], [a['id'] for a in eligible])
        for row, original in zip(objects, eligible):
            self.assertEqual(set(row), {'id', 'kind', 'title', 'teaser', 'dateLabel', 'room', 'target'})
            self.assertEqual(row['teaser'], original['curatorNote'])
            self.assertEqual(row['target'], '/archive/objects/'+original['slug']+'/')
        week = json.loads((self.path / 'public/assets/runtime/week.json').read_text())
        self.assertEqual(set(week), {'events'})
        self.assertEqual(week['events'], json.loads((ROOT / 'data/editorial-index.json').read_text())['events'])

    def test_modified_release_asset_is_rejected(self):
        p = self.path / 'public/js/app.js'
        original = p.read_bytes()
        try:
            p.write_bytes(original + b'\n// changed\n')
            with self.assertRaisesRegex(ValueError, 'Checksum mismatch'):
                verify(self.path)
        finally:
            p.write_bytes(original)

    def test_private_links_hidden_files_and_traversal_fail_closed(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            fixture(root)
            for url in ('/data/artifacts.json', '/docs/private.html', '/.git/config',
                        '/assets/.env', '/assets/.private/leak.svg', '/js/app.js.map',
                        '/assets/runtime/catalog.json', '/assets/editorial/home-hero-original.png',
                        '/%2egit/config', '/%2e%2e/secret.html', '/assets/../data/artifacts.json'):
                with self.subTest(url=url):
                    (root / 'index.html').write_text(f'<a href="{url}">bad</a>')
                    with self.assertRaises(ValueError):
                        collect_files(root)
            (root / 'index.html').write_text('<img src="/assets/generated/missing.webp">')
            with self.assertRaisesRegex(ValueError, 'Missing dependency'):
                dependencies(root, Path('index.html'))

    def test_routes_cannot_seed_private_or_outside_files(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            fixture(root)
            for route in ('/../', '/.git/', '/docs/', '/assets/', '//', '/zones/../docs/', '/%2e%2e/'):
                with self.subTest(route=route):
                    (root / 'data/routes.json').write_text(json.dumps([{'path': '/'}, {'path': route}]))
                    with self.assertRaises(ValueError):
                        collect_files(root)

    def test_file_and_directory_symlinks_are_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            fixture(root)
            (root / 'assets/generated/leak.svg').symlink_to(root / 'index.html')
            (root / 'index.html').write_text('<img src="/assets/generated/leak.svg">')
            with self.assertRaisesRegex(ValueError, 'Symlink'):
                collect_files(root)
            (root / 'assets/media').symlink_to(root / 'assets/generated', target_is_directory=True)
            (root / 'index.html').write_text('<img src="/assets/media/og-card.png">')
            with self.assertRaisesRegex(ValueError, 'Symlink'):
                collect_files(root)

    def test_rebuild_is_identical_and_removes_obsolete_assets(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            root, output = base / 'source', base / 'release'
            fixture(root)
            (root / 'index.html').write_text('<img src="/assets/generated/old.svg">')
            (root / 'assets/generated/old.svg').write_text('<svg/>')
            first = build(root, output)
            checksum = sha(output / '90s-land.tar.gz')
            self.assertEqual(first, build(root, output))
            self.assertEqual(checksum, sha(output / '90s-land.tar.gz'))
            (root / 'index.html').write_text('<p>new page</p>')
            second = build(root, output)
            self.assertNotEqual(first['contentDigest'], second['contentDigest'])
            self.assertFalse((output / 'public/assets/generated/old.svg').exists())
            # A failed next build cannot damage the last verified package.
            (root / 'index.html').write_text('<a href="/data/secret.json">bad</a>')
            with self.assertRaises(ValueError):
                build(root, output)
            self.assertEqual(verify(output), second)
            with self.assertRaisesRegex(ValueError, 'Output must be'):
                build(root, root / 'assets/release')

    def test_extra_files_directories_or_symlinks_in_package_are_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            root, output = base / 'source', base / 'release'
            fixture(root)
            build(root, output)
            extra = output / 'public/.git'
            extra.mkdir()
            with self.assertRaisesRegex(ValueError, 'Unexpected public directory'):
                verify(output)
            extra.rmdir()
            extra = output / 'public/.env'
            extra.write_text('PRIVATE=fixture')
            with self.assertRaisesRegex(ValueError, 'inventory'):
                verify(output)
            extra.unlink()
            (output / 'public/index.html').unlink()
            (output / 'public/index.html').symlink_to(root / 'index.html')
            with self.assertRaisesRegex(ValueError, 'Non-regular'):
                verify(output)

    def test_encoding_negotiation_respects_disabled_and_weighted_gzip(self):
        self.assertTrue(gzip_accepted('gzip;q=0.5, br'))
        self.assertTrue(gzip_accepted('br, gzip'))
        self.assertFalse(gzip_accepted('gzip;q=0, *;q=1'))
        self.assertFalse(gzip_accepted('br'))


class PublishTests(unittest.TestCase):
    def use_fixture_checkout(self, root):
        # Model the disposable checkout, so TMPDIR can safely live inside dist/.
        # The production publisher still rejects publishing inside its real checkout.
        boundary = patch('deploy_release.ROOT', root)
        boundary.start()
        self.addCleanup(boundary.stop)

    def test_promotion_repeat_rollback_and_failed_switch(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder).resolve()
            root, output, site = base / 'source', base / 'release', base / 'site'
            fixture(root)
            self.use_fixture_checkout(root)
            first = build(root, output)
            with self.assertRaisesRegex(ValueError, 'separate from the Git checkout'):
                publish(output, root / 'public')
            one = publish(output, site)
            self.assertIsNone(one['previousRelease'])
            self.assertEqual((site / 'current').resolve(), Path(one['release']) / 'public')
            self.assertFalse((site / 'current/release-manifest.json').exists())
            self.assertEqual(publish(output, site)['contentDigest'], first['contentDigest'])
            (root / 'index.html').write_text('<p>second release</p>')
            build(root, output)
            with patch('deploy_release.os.replace', side_effect=OSError('simulated failure')):
                with self.assertRaises(OSError):
                    publish(output, site)
            self.assertEqual((site / 'current').resolve(), Path(one['release']) / 'public')
            two = publish(output, site)
            self.assertEqual(two['previousRelease'], one['release'])
            self.assertEqual((site / 'current/index.html').read_text(), '<p>second release</p>')
            rollback = publish(Path(one['release']), site)
            self.assertEqual(rollback['contentDigest'], first['contentDigest'])
            self.assertTrue(Path(two['release']).exists())
            self.assertEqual((site / 'current/index.html').stat().st_mode & 0o777, 0o644)
            # An invalid candidate never replaces the active pointer.
            (output / 'public/.env').write_text('PRIVATE=fixture')
            with self.assertRaises(ValueError):
                publish(output, site)
            self.assertEqual((site / 'current').resolve(), Path(one['release']) / 'public')

    def test_existing_web_directory_or_foreign_symlink_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            root, output, site = base / 'source', base / 'release', base / 'site'
            fixture(root)
            self.use_fixture_checkout(root)
            build(root, output)
            current = site / 'current'
            current.mkdir(parents=True)
            with self.assertRaisesRegex(ValueError, 'not a managed symlink'):
                publish(output, site)
            current.rmdir()
            current.symlink_to(root)
            with self.assertRaisesRegex(ValueError, 'outside managed releases'):
                publish(output, site)


if __name__ == '__main__':
    unittest.main()
