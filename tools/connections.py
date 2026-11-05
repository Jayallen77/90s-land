"""Explicit, reasoned connections for every published story and object."""
import json
from functools import lru_cache
from html import escape
import archive_content as model
RECORDS=json.loads((model.ROOT/'content/editorial/connections.json').read_text())
@lru_cache(maxsize=1)
def routes():return {r['path']:r for r in model.all_routes()}
def sidebar(path):
 rows=[]
 for item in RECORDS[path]:
  target=routes()[item['url'].split('#')[0].split('?')[0]]
  kind={'stories':'STORY','objects':'OBJECT','years':'YEAR','zones':'COLLECTION'}.get(target['type'],'EXPLORE')
  rows.append(f'<a class="ar-related" href="{escape(item["url"],quote=True)}"><span class="ar-meta">{kind}</span><h3>{escape(target["title"])}</h3><p>{escape(item["reason"])}</p></a>')
 return '<aside class="ar-sidebar"><section class="ed-panel ar-panel"><h2>Worth following</h2>'+''.join(rows)+'</section></aside>'
def validate():
 errors=[];expected={model.story_url(s) for s in model.STORIES}|{model.object_url(a) for a in model.ARTIFACTS}
 if set(RECORDS)!=expected:errors.append('Connection review must cover all published stories and objects')
 for path,rows in RECORDS.items():
  targets=[r['url'] for r in rows]
  if not rows or len(targets)!=len(set(targets)):errors.append('Empty or repeated connection: '+path)
  for r in rows:
   if not r.get('reason') or r['url'].split('#')[0].split('?')[0] not in routes() or r['url']==path:errors.append('Invalid editorial connection: '+path)
 return errors
