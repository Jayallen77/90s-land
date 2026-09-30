"""Visitor-facing copy and generated empty-state regression checks."""
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import archive_content as archive
import archive_pages
import render_site
from content_model import Document, plain_text


class LaunchPhase1Tests(unittest.TestCase):
    def test_public_pages_have_no_development_notes(self):
        pattern = re.compile(
            r'\b(?:this (?:page|room|section|site) (?:should|now)|this rebuild|'
            r'stronger route|stronger year capsule|works better|becomes easier to browse|'
            r'proof that the site|monthly charts can come later|we should|can come later|'
            r'this implementation|this version|the redesign|the rebuild|TODO|FIXME|'
            r'lorem ipsum|coming soon|placeholder|codex prompt)\b', re.I)
        for path, source in render_site.build_outputs().items():
            if path.suffix == '.html':
                with self.subTest(page=str(path.relative_to(ROOT))):
                    self.assertIsNone(pattern.search(plain_text(source)))

    def test_static_month_empty_states_follow_catalog_counts(self):
        for year in range(1990, 2000):
            route = {'path': f'/timeline/{year}/'}
            document = Document(archive_pages.timeline(route))
            for month in range(1, 13):
                with self.subTest(year=year, month=month):
                    panel = next(node for node in document.nodes() if node.attrs.get('data-month-panel') == str(month))
                    empty = next(node for node in panel.walk() if 'data-month-empty' in node.attrs)
                    count = sum(event['date'].startswith(f'{year}-{month:02}') for event in archive.EVENTS)
                    self.assertEqual('hidden' in empty.attrs, count > 0)


if __name__ == '__main__':
    unittest.main()
