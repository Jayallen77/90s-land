#!/usr/bin/env python3
"""Reproducible editorial balance report and year-selection publication gate."""
import argparse
from collections import Counter
import json
import archive_content as archive


def distribution(events):
    def counts(items):
        categories=Counter(e['category'] for e in items);themes=Counter(e['theme'] for e in items)
        return {'total':len(items),'categories':{k:categories[k] for k in archive.CATEGORIES},'themes':{k:themes[k] for k in archive.THEMES}}
    result=counts(events)
    result['years']={str(y):counts([e for e in events if e['date'].startswith(str(y))]) for y in range(1990,2000)}
    result['months']={f'{y}-{m:02}':counts([e for e in events if e['date'].startswith(f'{y}-{m:02}')]) for y in range(1990,2000) for m in range(1,13)}
    return result


def report():
    errors=archive.validate_curation()
    preservation=json.loads((archive.ROOT/'reports/launch-phase2/event-preservation.json').read_text())
    for old in preservation['events']:
        event=archive.EVENT_BY_ID.get(old['id'])
        if not event or any(event.get(k)!=value for k,value in old.items()):errors.append('Original event identity or source changed: '+old['id'])
    highlights=[e for y in range(1990,2000) for e in archive.defining_events(y)]
    return {'baselineCommit':preservation['commit'],'after':distribution(archive.EVENTS),'definingMoments':distribution(highlights),'yearSelections':archive.CURATION['years'],'fashionContext':{'datedEvents':sum(e['theme']=='fashion' for e in archive.EVENTS),'storyIds':[s['id'] for s in archive.STORIES if 'fashion' in s.get('topics',[])],'note':'Fashion is explored through sourced stories and the lookbook. No exact launch day was invented for an era-wide style.'},'errors':errors}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
    result=report();path=archive.ROOT/'reports/launch-phase2/distribution-after.json';output=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
    errors=list(result['errors'])
    if args.check:
        if not path.exists() or path.read_text()!=output:errors.append('Curation report is stale; run tools/check_curation.py')
    else:path.parent.mkdir(parents=True,exist_ok=True);path.write_text(output)
    print(json.dumps({'events':len(archive.EVENTS),'definingMoments':result['definingMoments']['total'],'years':len(archive.YEARS),'errors':errors},indent=2))
    return bool(errors)


if __name__=='__main__':raise SystemExit(main())
