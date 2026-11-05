"""Date precision, crawlable week output and new editorial source contracts."""
import copy
from datetime import date, datetime, timezone
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import archive_content as model
import archive_pages
from build_release import current_week_pages

class ExpansionTests(unittest.TestCase):
    def test_month_and_year_events_do_not_invent_calendar_days(self):
        events=model.browser_index()['events']
        self.assertNotIn('fubu-begins',{e['id'] for e in events})
        self.assertNotIn('casio-qv10',{e['id'] for e in events})
        self.assertIn('release-wishkah',{e['id'] for e in events})
        self.assertEqual(model.date_label('1992'),'1992')
        self.assertEqual(model.date_label('1995-03'),'March 1995')
        data=copy.deepcopy(model.CATALOG)
        entry=next(e for e in data['events'] if e['id']=='casio-qv10')
        entry['date']='1995-03-01'
        self.assertTrue(any('Invalid event date: casio-qv10'==e for e in model.validate(data)))

    def test_release_refreshes_both_time_based_pages_without_changing_catalog(self):
        original=model.CATALOG['buildAsOf']
        pages=current_week_pages(ROOT,date(2027,1,1))
        week=pages[Path('this-week/index.html')]
        self.assertIn('Dec 30, 1996',week)
        self.assertIn('Jan 5, 1997',week)
        self.assertIn('THIS WEEK IN<strong>1997',pages[Path('index.html')])
        self.assertEqual(model.CATALOG['buildAsOf'],original)

    def test_sparse_week_has_server_rendered_nearby_entries(self):
        output=archive_pages.weekly(date(1990,1,1))
        self.assertIn('<section data-week-nearby>',output)
        self.assertIn('Outside the selected week.',output)
        self.assertIn('/timeline/',output.split('data-nearby-events>')[1].split('</section>')[0])

    def test_populated_week_contains_no_false_empty_copy(self):
        self.assertNotIn('No events in the archive for this week.',archive_pages.weekly(date(1996,10,1)))
        self.assertIn('From the Muddy Banks',archive_pages.weekly(date(1996,10,1)))

    def test_published_library_has_complete_prose_and_reviewed_images(self):
        features=model.load_features(ROOT/'content/editorial/features.md')
        self.assertEqual({s['id'] for s in features},{s['id'] for s in model.STORIES})
        for story in features:
            with self.subTest(story=story['id']):
                self.assertTrue(story['sections'])
                self.assertTrue(all(sec['paragraphs'] and sec['heading'] for sec in story['sections']))
                self.assertTrue(story['sourceIds'])
                self.assertIn(story['id'],model.STORY_MEDIA)
        for obj in model.ARTIFACTS:
            self.assertTrue(obj['whyItMattered'] and obj['sections'])
            self.assertTrue(obj['sourceIds'])
            self.assertGreaterEqual(obj['reviewedAt'],'2026-11-05')
            if obj['media']['kind']=='image':
                self.assertTrue((ROOT/obj['media']['src'].lstrip('/')).is_file())

    def test_denver_civil_day_matches_browser_boundary(self):
        self.assertEqual(model.civil_today(datetime(2026,9,28,5,tzinfo=timezone.utc)),date(2026,9,27))

if __name__=='__main__':unittest.main()
