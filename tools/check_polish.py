#!/usr/bin/env python3
"""Publication lifecycle and original-image checks for the curated editorial library."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit
import archive_content as model

ROOT=model.ROOT


def assess(media=None, publication=None):
    media=model.STORY_MEDIA if media is None else media
    publication=model.PUBLICATION if publication is None else publication
    errors=[]
    stories={s['id'] for s in model.STORIES}
    if set(media)!=stories: errors.append('Story media must match the published story inventory')
    identities=[];hashes=[]
    required=('src','width','height','alt','caption','credit','sourceUrl','sourceIdentity','license','licenseUrl','reviewedAt','depictedSubject','eraNote','sha256')
    for id,record in media.items():
        for field in required:
            if not record.get(field):errors.append(f'Incomplete story media: {id}: {field}')
        path=ROOT/record.get('src','').lstrip('/')
        if not path.is_file():errors.append('Missing story image: '+id);continue
        actual=hashlib.sha256(path.read_bytes()).hexdigest()
        if actual!=record.get('sha256'):errors.append('Story image changed without review: '+id)
        hashes.append(actual);identities.append(record.get('sourceIdentity'))
        if 'illustration' in record.get('license','').lower() or '/assets/editorial/' in record.get('src',''):errors.append('Generic illustration used as story lead: '+id)
    if len(set(hashes))!=len(hashes):errors.append('Lead image bytes reused between stories')
    if len(set(identities))!=len(identities):errors.append('Original lead image reused between stories')
    paragraphs=[]
    for s in model.STORIES:
        paragraphs.extend(p for sec in s['sections'] for p in sec['paragraphs'])
    if len(paragraphs)!=len(set(paragraphs)):errors.append('Repeated story prose')
    for obj in model.ARTIFACTS:
        if not obj.get('sourceIds'):errors.append('Missing object evidence: '+obj['id'])
        if not obj.get('reviewedAt'):errors.append('Unreviewed object prose: '+obj['id'])
    redirects=publication['redirects'];retired=set(publication['retiredRoutes']);original=set(publication['originalRoutes'])
    routes=model.all_routes();active={r['path'] for r in routes if r['type']!='redirects'}
    if active & (retired | redirects.keys()):errors.append('Publication lifecycle overlaps')
    if retired & redirects.keys():errors.append('Retired route is also a redirect')
    if original != active | set(redirects) | retired:errors.append('Original URLs are not completely accounted for')
    for path,target in redirects.items():
        parts=urlsplit(target)
        if parts.scheme or parts.netloc or parts.path not in active:errors.append('Invalid redirect destination: '+path)
        if parts.path in redirects:errors.append('Redirect chain: '+path)
    for event in model.EVENTS:
        if event['status']!='timeline-only' or event.get('art') is not None:errors.append('Event is not a text-only timeline record: '+event['id'])
    return {'stories':len(stories),'storiesByCategory':dict(Counter(s['category'] for s in model.STORIES)),
            'timelineEntries':len(model.EVENTS),'objects':len(model.ARTIFACTS),'activePages':len(active),
            'compatibilityPages':len(redirects),'retiredPages':len(retired),'uniqueLeadImages':len(set(identities)),
            'errors':errors}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output');args=parser.parse_args()
    result=assess()
    if args.output:
        path=ROOT/args.output;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2));return bool(result['errors'])

if __name__=='__main__':raise SystemExit(main())
