"""Publication gates, including calendar boundaries and coverage-loss checks."""
import copy
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import archive_content as archive
from check_editorial import assess

class PublicationCoverageTests(unittest.TestCase):
 def test_complete_launch(self):
  self.assertEqual(assess(archive.CATALOG)['errors'],[])
 def test_missing_month_and_boundary_week_are_detected(self):
  data=copy.deepcopy(archive.CATALOG)
  data['events']=[e for e in data['events'] if not e['date'].startswith('1993-02') and not '1996-12-30'<=e['date']<='1997-01-05']
  errors=assess(data)['errors']
  self.assertIn('Missing month: 1993-02',errors)
  self.assertTrue(any('Underfilled week: 1996-12-30' in e for e in errors))
 def test_stubs_and_uncited_events_do_not_qualify(self):
  data=copy.deepcopy(archive.CATALOG);data['stories'][0]['sections']=[];data['events'][0]['sourceIds']=[]
  errors=assess(data)['errors']
  self.assertTrue(any(e.startswith('Incomplete story:') for e in errors))
  self.assertTrue(any(e.startswith('Unreviewed event:') for e in errors))
