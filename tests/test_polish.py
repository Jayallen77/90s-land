"""Behavioral contracts for curated publication and independent story photography."""
import copy
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import archive_content as model
from check_polish import assess
from check_editorial import assess as editorial_assess

class CuratedPublicationTests(unittest.TestCase):
    def test_every_original_url_has_exactly_one_outcome(self):
        self.assertEqual(assess()['errors'],[])
        self.assertEqual(len(model.DEFINING_IDS),101)
        self.assertTrue(model.DEFINING_IDS <= model.EVENT_BY_ID.keys())

    def test_duplicate_photo_cannot_be_disguised_by_another_filename(self):
        media=copy.deepcopy(model.STORY_MEDIA);first,second=list(media)[:2]
        media[second]['sourceIdentity']=media[first]['sourceIdentity']
        self.assertIn('Original lead image reused between stories',assess(media)['errors'])

    def test_unreviewed_image_changes_and_missing_captions_fail(self):
        media=copy.deepcopy(model.STORY_MEDIA);first=next(iter(media))
        media[first]['sha256']='0'*64;media[first]['caption']=''
        errors=assess(media)['errors']
        self.assertIn('Story image changed without review: '+first,errors)
        self.assertIn('Incomplete story media: '+first+': caption',errors)

    def test_unknown_redirects_and_chains_cannot_publish(self):
        publication=copy.deepcopy(model.PUBLICATION);first,second=list(publication['redirects'])[:2]
        publication['redirects'][first]=second
        self.assertIn('Redirect chain: '+first,assess(publication=publication)['errors'])
        publication['redirects'][first]='/not-a-page/'
        self.assertIn('Invalid redirect destination: '+first,assess(publication=publication)['errors'])

    def test_sparse_calendar_does_not_encourage_filler(self):
        data=copy.deepcopy(model.CATALOG);data['events']=[e for e in data['events'] if not e['date'].startswith('1993-02')]
        self.assertEqual(editorial_assess(data)['errors'],[])

    def test_timeline_urls_keep_event_identity_and_date_precision(self):
        for event in model.EVENTS:
            url=model.event_url(event)
            self.assertTrue(url.startswith('/timeline/'+event['date'][:4]+'/'))
            self.assertTrue(url.endswith('#event-'+event['id']))
            self.assertEqual('?month=' in url,event['datePrecision']!='year')
        self.assertTrue(all(r['type']!='events' for r in model.all_routes()))

if __name__=='__main__':unittest.main()
