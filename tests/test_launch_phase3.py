import json
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import archive_content as archive
import discovery
from check_launch import assess
from build_release import dependencies, route_files

class LaunchPolishTests(unittest.TestCase):
    def test_publication_metadata_and_copy_are_complete(self):
        self.assertEqual(assess()['errors'],[])
    def test_shuffle_only_contains_rich_published_destinations(self):
        rows=discovery.surprise_pool();paths={r['path'] for r in archive.all_routes()}
        self.assertEqual(len(rows),180)
        self.assertEqual(len({r['id'] for r in rows}),len(rows))
        self.assertEqual({r['kind'] for r in rows},set(discovery.KINDS))
        self.assertTrue(all(r['target'] in paths and r['teaser'] for r in rows))
        self.assertEqual({r['id'].removeprefix('event-') for r in rows if r['kind']=='event'},archive.DEFINING_IDS)
        self.assertTrue(all(r['target'] not in {'/credits/','/search/','/guestbook/','/sitemap/','/surprise/'} for r in rows))
    def test_absolute_share_assets_cross_the_public_boundary(self):
        deps=dependencies(ROOT,Path('index.html'),route_files([r['path'] for r in archive.all_routes()]))
        card=json.loads((ROOT/'data/social-cards.json').read_text())['cards']['/']['src']
        self.assertIn(Path(card.lstrip('/')),deps)
    def test_short_weekly_selections_never_hide_the_calendar(self):
        for y in range(1990,2000):
            events=[e for e in archive.EVENTS if e['date'].startswith(str(y))]
            picks=archive.selected_events(events)
            self.assertLessEqual(len(picks),4)
            self.assertLessEqual(sum(e['theme']=='movies' for e in picks),2)
            self.assertEqual(len(set(e['id'] for e in picks)),len(picks))
            self.assertTrue(all(e in events for e in picks))
