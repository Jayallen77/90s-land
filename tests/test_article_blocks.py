import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import article_blocks as blocks
class ArticleBlocksTests(unittest.TestCase):
 def test_legacy_paragraphs_and_editorial_blocks_coexist(self):
  data=blocks.parse('A plain paragraph.\n\n- First\n- Second\n\n| Game | Blocks |\n| --- | --- |\n| GT | 5 |\n\n> A contextual note.')
  self.assertEqual([x['type'] for x in data],['paragraph','list','table','note'])
  html=blocks.render(data,'Save space');self.assertIn('scope="col"',html);self.assertIn('<caption>Save space</caption>',html);self.assertIn('<p>A plain paragraph.</p>',html)
 def test_inline_markup_cannot_inject_html_or_script_links(self):
  html=blocks.inline('<img src=x onerror=alert(1)> [x](javascript:alert) **bold** `IDDQD` [card](/archive/objects/memory-card/)')
  self.assertNotIn('<img',html);self.assertNotIn('href="javascript:',html);self.assertIn('<code>IDDQD</code>',html);self.assertIn('href="/archive/objects/memory-card/"',html)
 def test_figure_has_accessible_caption_and_large_view(self):
  html=blocks.render(blocks.parse('{{figure:memory-blocks}}'),'Read this card')
  self.assertIn('<figure',html);self.assertIn('<figcaption>',html);self.assertIn('alt="',html);self.assertIn('View large',html);self.assertNotIn('{{figure:',html)
 def test_unknown_figure_fails_authoring(self):
  with self.assertRaises(KeyError):blocks.render([{'type':'figure','id':'missing-proof'}],'Figure')
