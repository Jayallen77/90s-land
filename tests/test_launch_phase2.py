"""Protect the curated year experience and existing historical evidence."""
import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import archive_content as archive
import check_curation


class PhaseTwoTests(unittest.TestCase):
    def test_original_dates_regions_and_source_links_are_preserved(self):
        original = json.loads((ROOT / 'reports/launch-phase2/event-preservation.json').read_text())
        self.assertEqual(len(original['events']), 384)
        for record in original['events']:
            with self.subTest(event=record['id']):
                current = archive.EVENT_BY_ID[record['id']]
                self.assertEqual({key: current[key] for key in record}, record)
        self.assertEqual(check_curation.report()['errors'], [])

    def test_each_year_has_a_varied_introduction_and_connections(self):
        self.assertEqual(set(archive.YEARS), set(range(1990, 2000)))
        for year, capsule in archive.YEARS.items():
            with self.subTest(year=year):
                picks = archive.defining_events(year)
                self.assertTrue(10 <= len(picks) <= 20)
                self.assertGreaterEqual(len({e['theme'] for e in picks}), 5)
                self.assertLessEqual(sum(e['theme'] == 'movies' for e in picks), 3)
                self.assertTrue(all(e['date'].startswith(str(year)) for e in picks))
                self.assertEqual(len(set(capsule['objectIds'])), 4)
                objects = [o for o in archive.ARTIFACTS if o['id'] in capsule['objectIds']]
                if any(not o['dateRange']['startYear'] <= year <= o['dateRange']['endYear'] for o in objects):
                    self.assertTrue(capsule.get('objectNote'), 'Earlier/later objects need visible context')
        self.assertEqual(len({y['intro'] for y in archive.YEARS.values()}), 10)

    def test_invalid_or_narrow_selections_cannot_publish(self):
        for alteration, message in [
            (lambda y: y['eventIds'].__setitem__(0, 'missing'), 'unknown event'),
            (lambda y: y['eventIds'].__setitem__(0, archive.YEARS[1999]['eventIds'][0]), 'another year'),
            (lambda y: y['eventIds'].__setitem__(0, y['eventIds'][1]), 'distinct moments'),
            (lambda y: y.update(eventIds=[e['id'] for e in archive.EVENTS if e['date'].startswith('1990') and e['theme'] == 'movies'][:10]), 'narrow cultural coverage'),
            (lambda y: y.update(storyIds=['missing'] * 5), 'unknown or missing story'),
            (lambda y: y.update(objectIds=['missing'] * 4), 'unknown or missing object'),
        ]:
            with self.subTest(message=message):
                curation = copy.deepcopy(archive.CURATION)
                alteration(curation['years'][0])
                self.assertTrue(any(message in error for error in archive.validate_curation(curation)))

    def test_short_object_connections_do_not_become_film_lists(self):
        picks = archive.selected_events(archive.EVENTS, limit=3)
        self.assertEqual(len(picks), 3)
        self.assertEqual(len({e['theme'] for e in picks}), 3)
        self.assertTrue(all(e['id'] in archive.DEFINING_IDS for e in picks))

    def test_earlier_or_later_objects_require_a_visible_explanation(self):
        curation = copy.deepcopy(archive.CURATION)
        del curation['years'][1]['objectNote']
        self.assertTrue(any('earlier or later object needs context' in error for error in archive.validate_curation(curation)))


if __name__ == '__main__':
    unittest.main()
