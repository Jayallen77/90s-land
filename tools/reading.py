"""Year-level editorial reading, kept separate from exact-date calendar facts."""
from html import escape
import json
import archive_content as model

def year_reading(year):
    ids=json.loads((model.ROOT/'content/editorial/weekly-reading.json').read_text())[str(year)]
    stories=[next(s for s in model.STORIES if s['id']==id) for id in ids[:2]]
    objects=[next(a for a in model.ARTIFACTS if a['id']==id) for id in ids[2:]]
    return [{'title':s['title'],'url':model.story_url(s),'summary':s['summary'],'kind':'Story'} for s in stories]+[{'title':a['title'],'url':model.object_url(a),'summary':a['curatorNote'],'kind':'Object'} for a in objects]

def markup(year, sparse=True):
    rows=''.join(f'<a class="ar-related" href="{escape(r["url"],quote=True)}"><span class="ar-meta">{r["kind"]}</span><h3>{escape(r["title"])}</h3><p>{escape(r["summary"])}</p></a>' for r in year_reading(year))
    return f'<section class="ed-panel ar-year-reading" data-week-reading'+('' if sparse else ' hidden')+f'><p class="ar-kicker">YEAR-LEVEL READING</p><h2 data-reading-title>From the {year} collection</h2><p>Stories and objects connected to the year. Exact dates for the selected week appear separately below.</p><div class="ed-two-up" data-reading-links>{rows}</div></section>'
