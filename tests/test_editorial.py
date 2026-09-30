"""Regression contract: one modern composition and working historical bookmarks."""
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from content_model import Document, plain_text


class EditorialPreservationTests(unittest.TestCase):
    def test_every_baseline_fragment_survives(self):
        manifest = json.loads((ROOT / 'reports/baseline/phase-1/manifest.json').read_text())
        for page in manifest['pages']:
            with self.subTest(route=page['route']):
                document = Document((ROOT / page['file']).read_text())
                current_ids = {node.attrs['id'] for node in document.nodes() if 'id' in node.attrs}
                self.assertEqual(set(page['anchors']) - current_ids, set())

    def test_every_page_has_one_modern_composition(self):
        import render_site
        forbidden = ('ed-reading-room', 'ed-preserved', 'window-bar', 'window-buttons', 'portal-box', 'Open Archive')
        outputs = render_site.build_outputs()
        for path, source in outputs.items():
            if path.suffix != '.html': continue
            with self.subTest(page=str(path.relative_to(ROOT))):
                for token in forbidden: self.assertNotIn(token, source)
                doc = Document(source)
                for tag in ('main','h1'):
                    self.assertEqual(len(doc.nodes(lambda n:n.tag==tag)),1)
                self.assertEqual(len(doc.nodes(lambda n:n.has_class('ed-header'))),1)
                self.assertEqual(len(doc.nodes(lambda n:n.has_class('ed-footer'))),1)
                self.assertEqual(len(doc.nodes(lambda n:n.has_class('ed-discovery'))),1)
                self.assertEqual(len(doc.nodes(lambda n:n.has_class('window'))),0)

    def test_legacy_renderers_cannot_be_called(self):
        import editorial, archive_content
        self.assertFalse(hasattr(editorial,'preserved_content'))
        self.assertFalse(hasattr(editorial,'apply_shell'))
        self.assertFalse(hasattr(archive_content,'page_source'))

    def test_game_and_tamagotchi_images_do_not_misrepresent_subject(self):
        import archive_content, hub_pages
        self.assertIsNone(next(s for s in archive_content.STORIES if s['id']=='the-toy-that-needed-you')['art'])
        doc = Document(hub_pages.game_archive())
        self.assertEqual(len(doc.nodes(lambda n:n.tag=='img')),0)

if __name__ == '__main__': unittest.main()
