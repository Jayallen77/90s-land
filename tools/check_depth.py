#!/usr/bin/env python3
"""Depth-sprint editorial, media, relationship and preservation checks."""
import hashlib,json,re
from pathlib import Path
import archive_content as m
import connections
from exhibits import IDS,render
from check_polish import assess

def fingerprint(value):return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
def preservation(catalog,publication,curation):
 return {'events':fingerprint(catalog['events']),'publication':fingerprint(publication),'defining':fingerprint([y['eventIds'] for y in curation['years']])}
def check():
 errors=connections.validate()+assess()['errors']
 baseline=json.loads((m.ROOT/'reports/deeper-sprint/preservation.json').read_text())
 old=json.loads((m.ROOT/'reports/connected-sprint/baseline.json').read_text())
 if [a['id'] for a in m.ARTIFACTS]!=baseline['originalArtifactIds']+m.introduced_ids('object'):errors.append('Artifact and Passport identifiers changed')
 if {s['id'] for s in m.STORIES}!=set(old['storyIds']+m.introduced_ids('story')):errors.append('Story identity changed without a publication decision')
 for kind in ('story','object'):
  added=m.introduced_ids(kind)
  if len(added)!=len(set(added)) or set(added)&set(old[kind+'Ids']):errors.append('Duplicate introduced '+kind+' identity')
 if [s['id'] for t in json.loads((m.ROOT/'data/tours.json').read_text()) for s in t['stops']]!=baseline['originalTourStopIds']:errors.append('Tour progress identifiers changed')
 # Event story links are authoring data; the approved timeline identity itself is frozen.
 current=json.loads((m.ROOT/'content/editorial/catalog.json').read_text())
 if preservation(current,m.PUBLICATION,m.CURATION)!=baseline['fingerprints']:errors.append('Approved timeline, defining moments or retirement map changed')
 if len(m.EVENTS)!=295 or len(m.DEFINING_IDS)!=101:errors.append('Approved timeline inventory changed')
 for s in m.STORIES:
  if s.get('updatedAt','')<'2026-11-05':errors.append('Story missed editorial pass: '+s['id'])
  if any(re.search(r'\{\{(?:figure|tool):',p) and not re.fullmatch(r'\{\{(?:figure|tool):[a-z0-9-]+\}\}',p) for sec in s['sections'] for p in sec['paragraphs']):errors.append('Malformed article block: '+s['id'])
 imports={}
 for file in (m.ROOT/'js').glob('*.js'):
  for spec in re.findall(r'''(?:from\s*|import\s*\(\s*)["'](\./[^"']+)["']''',file.read_text()):
   imports.setdefault(spec.split('?')[0],set()).add(spec)
 for module,versions in imports.items():
  if len(versions)>1:errors.append('Multiple runtime identities for '+module)
 for a in m.ARTIFACTS:
  if a.get('reviewedAt','')<'2026-11-05':errors.append('Object missed review: '+a['id'])
 for id in IDS:
  html=render(id,True)
  if 'ORIGINAL RECREATION' not in html or 'GEOCITIES_HOME.HTML' in html:errors.append('Unfinished exhibit: '+id)
 figures=json.loads((m.ROOT/'content/editorial/figures.json').read_text())
 edition=json.loads((m.ROOT/'content/editorial/edition.json').read_text())
 if not set(edition.get('objectIds',[]))<={a['id'] for a in m.ARTIFACTS} or len(edition.get('objectIds',[]))!=len(set(edition.get('objectIds',[]))) or not edition.get('objectIds'):errors.append('Invalid edition object selection')
 for id,f in figures.items():
  if not set(f.get('sourceIds',[]))<=m.SOURCES.keys() or not f.get('sourceIds'):errors.append('Unsupported figure: '+id)
  file=m.ROOT/f['src'].lstrip('/')
  if not file.is_file() or hashlib.sha256(file.read_bytes()).hexdigest()!=f['sha256']:errors.append('Unreviewed figure bytes: '+id)
  if f.get('visualType')=='explanatory-diagram' and not f['caption'].startswith('Original'):errors.append('Unlabeled original diagram: '+id)
 from reading import year_reading
 for year in range(1990,2000):
  rows=year_reading(year)
  if len(rows)!=4 or len({r['url'] for r in rows})!=4 or any(r['url'] not in connections.routes() for r in rows):errors.append('Invalid weekly fallback: '+str(year))
 return {'stories':len(m.STORIES),'objects':len(m.ARTIFACTS),'activePages':sum(r['type']!='redirects' for r in m.all_routes()),'timelineRecords':len(m.EVENTS),'definingMoments':len(m.DEFINING_IDS),'reviewedRelationshipPages':len(connections.RECORDS),'reasonedLinks':sum(map(len,connections.RECORDS.values())),'exhibits':len(IDS),'supportingFigureRecords':len(figures),'errors':errors}
if __name__=='__main__':
 result=check();print(json.dumps(result,indent=2));raise SystemExit(bool(result['errors']))
