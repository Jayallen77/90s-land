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
 if [a['id'] for a in m.ARTIFACTS]!=baseline['originalArtifactIds']:errors.append('Artifact and Passport identifiers changed')
 if [s['id'] for t in json.loads((m.ROOT/'data/tours.json').read_text()) for s in t['stops']]!=baseline['originalTourStopIds']:errors.append('Tour progress identifiers changed')
 # Event story links are authoring data; the approved timeline identity itself is frozen.
 current=json.loads((m.ROOT/'content/editorial/catalog.json').read_text())
 if preservation(current,m.PUBLICATION,m.CURATION)!=baseline['fingerprints']:errors.append('Approved timeline, defining moments or retirement map changed')
 if len(m.STORIES)!=35 or len(m.ARTIFACTS)!=62 or len(m.EVENTS)!=295 or len(m.DEFINING_IDS)!=101:errors.append('Approved collection inventory changed')
 for s in m.STORIES:
  if s.get('updatedAt','')<'2026-11-05':errors.append('Story missed editorial pass: '+s['id'])
  if any('{{figure:' in p and not re.fullmatch(r'\{\{figure:[a-z0-9-]+\}\}',p) for sec in s['sections'] for p in sec['paragraphs']):errors.append('Malformed figure: '+s['id'])
 for a in m.ARTIFACTS:
  if a.get('reviewedAt','')<'2026-11-05':errors.append('Object missed review: '+a['id'])
 for id in IDS:
  html=render(id,True)
  if 'ORIGINAL RECREATION' not in html or 'GEOCITIES_HOME.HTML' in html:errors.append('Unfinished exhibit: '+id)
 figures=json.loads((m.ROOT/'content/editorial/figures.json').read_text())
 for id,f in figures.items():
  if not set(f.get('sourceIds',[]))<=m.SOURCES.keys() or not f.get('sourceIds'):errors.append('Unsupported figure: '+id)
  file=m.ROOT/f['src'].lstrip('/')
  if not file.is_file() or hashlib.sha256(file.read_bytes()).hexdigest()!=f['sha256']:errors.append('Unreviewed figure bytes: '+id)
  if f.get('visualType')=='explanatory-diagram' and not f['caption'].startswith('Original'):errors.append('Unlabeled original diagram: '+id)
 from reading import year_reading
 for year in range(1990,2000):
  rows=year_reading(year)
  if len(rows)!=4 or len({r['url'] for r in rows})!=4 or any(r['url'] not in connections.routes() for r in rows):errors.append('Invalid weekly fallback: '+str(year))
 return {'stories':35,'objects':62,'activePages':128,'timelineRecords':295,'definingMoments':101,'reviewedRelationshipPages':len(connections.RECORDS),'reasonedLinks':sum(map(len,connections.RECORDS.values())),'exhibits':len(IDS),'supportingFigureRecords':len(figures),'errors':errors}
if __name__=='__main__':
 result=check();print(json.dumps(result,indent=2));raise SystemExit(bool(result['errors']))
