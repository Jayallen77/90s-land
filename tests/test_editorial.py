"""Independent preservation checks for the replacement page compositions."""
import json
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

    def test_core_reading_rooms_retain_all_original_main_text(self):
        manifest = json.loads((ROOT / 'reports/baseline/phase-1/manifest.json').read_text())
        for page in manifest['pages']:
            if page['route'] not in ('/', '/timeline/1996/', '/zones/games/'):
                continue
            with self.subTest(route=page['route']):
                frozen = (ROOT / page['snapshot']).read_text()
                start, end = page['mainRange']
                expected = plain_text(frozen[start:end])
                document = Document((ROOT / page['file']).read_text())
                preserved = document.one(lambda node: node.has_class('ed-preserved'))
                self.assertEqual(document.text(preserved), expected)
                self.assertEqual(len(document.nodes(lambda node: node.tag == 'h1')), 1)


if __name__ == '__main__':
    unittest.main()
