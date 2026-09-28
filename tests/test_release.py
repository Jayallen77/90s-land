import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from build_release import build, verify, dependencies
from serve_release import gzip_accepted

class ReleaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory()
        cls.path=Path(cls.temp.name)/'release'
        cls.manifest=build(ROOT,cls.path)
    @classmethod
    def tearDownClass(cls):cls.temp.cleanup()

    def test_release_contains_every_route_and_no_source_material(self):
        files=self.manifest['files']
        for route in json.loads((ROOT/'data/routes.json').read_text()):
            self.assertIn(str(Path(route['path'].strip('/'))/'index.html'),files)
        for name in files:
            self.assertNotIn(name.split('/')[0],{'content','reports','tests','tools','docs','node_modules','.git'})
            self.assertFalse(name.endswith(('-source.png','-original.png')))
        self.assertIn('index.html.gz',files)
        self.assertTrue((self.path/'90s-land.tar.gz').is_file())
        verify(self.path)

    def test_modified_release_asset_is_rejected(self):
        p=self.path/'public/js/app.js';original=p.read_bytes()
        try:
            p.write_bytes(original+b'\n// changed\n')
            with self.assertRaisesRegex(ValueError,'Checksum mismatch'):verify(self.path)
        finally:p.write_bytes(original)

    def test_missing_dependency_and_private_source_link_are_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);page=root/'index.html'
            page.write_text('<img src="/missing.webp" />')
            with self.assertRaisesRegex(ValueError,'Missing dependency'):dependencies(root,Path('index.html'))
            (root/'docs').mkdir();(root/'docs/private.html').write_text('source')
            page.write_text('<a href="/docs/private.html">source</a>')
            with self.assertRaisesRegex(ValueError,'Private source'):dependencies(root,Path('index.html'))

    def test_encoding_negotiation_respects_disabled_and_weighted_gzip(self):
        self.assertTrue(gzip_accepted('gzip;q=0.5, br'))
        self.assertTrue(gzip_accepted('br, gzip'))
        self.assertFalse(gzip_accepted('gzip;q=0, *;q=1'))
        self.assertFalse(gzip_accepted('br'))

if __name__=='__main__':unittest.main()
