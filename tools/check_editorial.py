#!/usr/bin/env python3
"""Independent Phase 4 publication coverage and source/media completeness gate."""
import argparse
from collections import Counter
from datetime import date,timedelta
import json
from pathlib import Path
import archive_content as archive

ROOT=Path(__file__).resolve().parents[1]

def assess(data):
 errors=[]
 events=data['events'];stories=data['stories'];months=Counter(e['date'][:7] for e in events)
 if len(events)<300:errors.append('At least 300 events required')
 for year in range(1990,2000):
  for month in range(1,13):
   key=f'{year}-{month:02}'
   if not months[key]:errors.append('Missing month: '+key)
 weeks=[]
 for i in range(53):
  start=date(1996,1,1)+timedelta(days=7*i);end=start+timedelta(days=6)
  count=sum(str(start)<=e['date']<=str(end) for e in events)
  weeks.append({'start':str(start),'end':str(end),'events':count})
  if count<3:errors.append(f'Underfilled week: {start} ({count})')
 categories=Counter(s['category'] for s in stories)
 for cat in ['games','music','movies-tv','tech','culture']:
  if categories[cat]<6:errors.append('Fewer than six complete stories: '+cat)
 for s in stories:
  prose=[p for section in s['sections'] for p in section['paragraphs']]
  if len(s['sections'])<3 or len(' '.join(prose).split())<300:errors.append('Incomplete story: '+s['id'])
  if len(prose)!=len(set(prose)):errors.append('Repeated paragraphs: '+s['id'])
 if len({(e['title'],e['date'],e['region']) for e in events})!=len(events):errors.append('Duplicate event identity')
 source_ids={s['id'] for s in data['sources']}
 for e in events:
  if e.get('datePrecision')!='day' or not e.get('sourceIds') or not set(e['sourceIds'])<=source_ids or not e.get('dateNote') or not e.get('verifiedAt'):errors.append('Unreviewed event: '+e['id'])
 return {'events':len(events),'eventsByCategory':dict(Counter(e['category'] for e in events)),'stories':len(stories),'storiesByCategory':dict(categories),'months':dict(sorted(months.items())),'weeks1996':weeks,'errors':errors}

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
 result=assess(archive.CATALOG);result['errors']+=archive.validate()
 media=json.loads((ROOT/'content/editorial/media-review.json').read_text())['items'];reviewed={m['id'] for m in media}
 for a in archive.ARTIFACTS:
  if a['id'] not in reviewed or a['media']['license']=='See source page':result['errors'].append('Unreviewed media: '+a['id'])
 result['reviewedMedia']=len(reviewed)
 modules=json.loads((ROOT/'content/editorial/modules.json').read_text())
 for game in modules['games']:
  if not game.get('sourceUrl') or not game.get('checkedAt') or game['storyId'] not in {s['id'] for s in archive.STORIES}:result['errors'].append('Incomplete game shelf entry: '+game['title'])
 result['gameShelfEntries']=len(modules['games'])
 output=json.dumps(result,ensure_ascii=False,indent=2)+'\n';path=ROOT/'reports/phase-4/editorial-coverage.json'
 if args.check:
  if not path.exists() or path.read_text()!=output:result['errors'].append('Coverage report is stale; run tools/check_editorial.py')
 else:path.parent.mkdir(parents=True,exist_ok=True);path.write_text(output)
 print(json.dumps({k:v for k,v in result.items() if k not in ('months','weeks1996')},indent=2))
 return bool(result['errors'])
if __name__=='__main__':raise SystemExit(main())
