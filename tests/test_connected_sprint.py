"""Content-growth and static-worked-example contracts."""
import json,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import archive_content as model
import article_blocks
from check_depth import check
from check_polish import assess

class ConnectedSprintTests(unittest.TestCase):
 def test_growth_is_explicit_and_original_decisions_survive(self):
  self.assertEqual(check()['errors'],[])
  self.assertEqual(len(model.introduced_routes()),11)
  self.assertFalse(model.introduced_routes() & set(model.PUBLICATION['originalRoutes']))
  self.assertEqual(len(model.PUBLICATION['originalRoutes']),779)
  self.assertEqual(len(model.PUBLICATION['redirects']),311)
  self.assertEqual(len(model.PUBLICATION['retiredRoutes']),340)

 def test_undeclared_active_page_cannot_hide_in_the_historical_ledger(self):
  old=model.introduced_routes
  try:
   model.introduced_routes=lambda:set()
   self.assertIn('Original URLs are not completely accounted for',assess()['errors'])
  finally:model.introduced_routes=old

 def test_worked_examples_have_readable_fallbacks_and_bound_controls(self):
  for id,answer in [('mp3-budget','33:20'),('keypad','13 letter presses')]:
   rendered=article_blocks.render(article_blocks.parse('{{tool:'+id+'}}'),'Example')
   self.assertIn(answer,rendered);self.assertIn(' disabled',rendered);self.assertIn('<noscript>',rendered)
  with self.assertRaises(ValueError):article_blocks.parse('{{tool:unreviewed}}')

 def test_toy_photo_survives_the_diagram_authoring_pass(self):
  from build_editorial_diagrams import LEADS
  self.assertNotIn('holiday-toys-that-answered-back',LEADS)
  self.assertIn('/connected/tamagotchi-1997.webp',model.STORY_MEDIA['holiday-toys-that-answered-back']['src'])

if __name__=='__main__':unittest.main()
