"""Publication integrity and clean-build checks for the dated archive."""
import copy
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import archive_content as archive
import render_site
from content_model import Document


class ArchiveTests(unittest.TestCase):
    def test_reviewed_catalog_is_valid(self):
        self.assertEqual(archive.validate(),[])

    def test_unknown_sources_and_mismatched_date_precision_cannot_publish(self):
        for field,value,message in [('sourceIds',['missing'],'Unknown source'),('datePrecision','month','Invalid event date'),('date','1996-02-30','Invalid event date'),('date','2000-01-01','outside decade'),('storyIds',['missing'],'Unknown story')]:
            with self.subTest(field=field):
                data=copy.deepcopy(archive.CATALOG)
                data['events'][0][field]=value
                self.assertTrue(any(message in error for error in archive.validate(data)))

    def test_build_never_reads_public_html_or_frozen_snapshots(self):
        original = Path.read_text
        def read(path,*args,**kwargs):
            self.assertFalse(str(path).endswith('.html'), f'Render read generated HTML: {path}')
            self.assertNotIn('/reports/baseline/',str(path),f'Render read frozen import: {path}')
            return original(path,*args,**kwargs)
        with patch.object(Path,'read_text',read):
            outputs=render_site.build_outputs()
        for route in archive.all_routes():
            document=Document(outputs[render_site.route_to_file(route['path'])])
            self.assertEqual(len(document.nodes(lambda n:n.tag=='main')),1,route['path'])
            self.assertEqual(len(document.nodes(lambda n:n.tag=='h1')),1,route['path'])

    def test_search_has_one_entry_per_event_story_and_object(self):
        records=render_site.search_records()
        for type,source in [('events',archive.EVENTS),('stories',archive.STORIES),('objects',archive.ARTIFACTS)]:
            self.assertEqual(len([r for r in records if r['type']==type]),len(source))
        self.assertEqual(len({r['id'] for r in records}),len(records))
        self.assertEqual(len({r['href'] for r in records if not r['external']}),len([r for r in records if not r['external']]))

    def test_calendar_encodes_real_leap_days_and_weekday_columns(self):
        import archive_pages
        doc=Document(archive_pages.calendar_table(1996,2,archive.EVENTS))
        dates=[n.attrs['datetime'] for n in doc.nodes(lambda n:n.tag=='time')]
        self.assertEqual(len(dates),29)
        self.assertEqual(dates[-1],'1996-02-29')
        doc=Document(archive_pages.calendar_table(1995,2,[]))
        self.assertEqual(len(doc.nodes(lambda n:n.tag=='time')),28)


if __name__=='__main__': unittest.main()
