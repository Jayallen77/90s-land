"""Authoritative dated archive and route model; never reads generated HTML."""
from __future__ import annotations
import calendar
import json
import re
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATEGORIES = {'music':'Music', 'movies-tv':'Movies & TV', 'games':'Games', 'tech':'Tech', 'culture':'Culture', 'news':'World news'}
HEROES = {'home', 'timeline', 'games', 'music', 'movies', 'tech', 'culture'}
CATALOG = json.loads((ROOT/'content/editorial/catalog.json').read_text())
ARTIFACTS = json.loads((ROOT/'data/artifacts.json').read_text())
EVENTS = sorted(CATALOG['events'], key=lambda e: (e['date'], e['id']))
STORIES = CATALOG['stories']
SOURCES = {s['id']: s for s in CATALOG['sources']}


def event_url(item): return f'/events/{item["slug"]}/'
def story_url(item): return f'/stories/{item["slug"]}/'
def object_url(item): return f'/archive/objects/{item["slug"]}/'


def historical_date(today):
    year = today.year - 30
    shifted = date(year, today.month, min(today.day, calendar.monthrange(year, today.month)[1]))
    return min(date(1999,12,31), max(date(1990,1,1), shifted))


def week_bounds(day):
    start = day - timedelta(days=day.weekday())
    return start, start + timedelta(days=6)


def all_routes():
    routes = json.loads((ROOT/'content/routes.json').read_text())
    def add(id, type, path, title, summary, tags, objects=()):
        routes.append(dict(id=id, type=type, path=path, title=title, summary=summary,
                           tags=tags, artifactIds=list(objects), randomEligible=False))
    add('this-week','highlights','/this-week/','This week, 30 years ago','Step back into a historical Monday–Sunday week. Browse dated releases and moments from the 1990s.',['week','calendar'])
    add('events','highlights','/events/','Events from the 90s','Browse dated releases and milestones across the decade. Filter by category, then follow the source notes.',['events','calendar'])
    add('stories','highlights','/stories/','Stories from the 90s','Read the stories behind the dates, objects, and everyday rituals.',['stories'])
    add('object-archive','highlights','/archive/objects/','The object archive',f'{len(ARTIFACTS)} objects, interfaces, and recreations from the 1990s.',['objects','archive'])
    add('zones-culture','zones','/zones/culture/','Culture: meet you at the mall','Style, toys, sports, screen names, and the everyday rituals that made the decade yours.',['culture','fashion','toys','sports','internet'])
    for e in EVENTS:
        add('event-'+e['id'],'events',event_url(e),e['title'],e['summary'],[e['date'], e['category'], e['region']],e['objectIds'])
    for s in STORIES:
        add('story-'+s['id'],'stories',story_url(s),s['title'],s['summary'],[s['category']],s['objectIds'])
    for a in ARTIFACTS:
        add('object-'+a['id'],'objects',object_url(a),a['title'],a['curatorNote'],a['tags'],[a['id']])
    return routes


def validate(catalog=None):
    data = catalog or CATALOG
    errors = []
    def require(condition, message):
        if not condition: errors.append(message)
    ids = {}
    for group in ('sources','events','stories'):
        ids[group] = {i['id'] for i in data[group]}
        require(len(ids[group]) == len(data[group]), f'Duplicate {group} id')
        if group != 'sources':
            require(len({i['slug'] for i in data[group]}) == len(data[group]), f'Duplicate {group} slug')
    objects = {a['id'] for a in ARTIFACTS}
    for s in data['sources']:
        require(s['url'].startswith('https://') and bool(s.get('scope')) and bool(s.get('checkedAt')), f'Incomplete source: {s["id"]}')
    for group in ('events','stories'):
        for item in data[group]:
            prefix = item['id']
            require(bool(re.fullmatch('[a-z0-9]+(?:-[a-z0-9]+)*', item['slug'])), f'Invalid slug: {prefix}')
            require(item['category'] in CATEGORIES, f'Unknown category: {prefix}')
            require(item.get('status') == 'published', f'Unpublished item in public catalog: {prefix}')
            require(bool(item.get('sourceIds')), f'Missing source: {prefix}')
            require(set(item.get('sourceIds', [])) <= ids['sources'], f'Unknown source: {prefix}')
            require(set(item.get('objectIds', [])) <= objects, f'Unknown object: {prefix}')
            require(item.get('art') is None or item['art'] in objects | HEROES, f'Unknown artwork: {prefix}')
            if group == 'events':
                try:
                    day = date.fromisoformat(item['date'])
                    require(1990 <= day.year <= 1999, f'Date outside decade: {prefix}')
                except (ValueError, KeyError): errors.append(f'Invalid event date: {prefix}')
                require(item.get('datePrecision') == 'day' and bool(item.get('dateNote')) and bool(item.get('verifiedAt')), f'Event needs verified day precision: {prefix}')
                require(bool(item.get('region')), f'Missing region: {prefix}')
                require(set(item.get('storyIds', [])) <= ids['stories'], f'Unknown story: {prefix}')
            else:
                require(bool(item.get('sections')), f'Empty story: {prefix}')
                require(set(item.get('eventIds', [])) <= ids['events'], f'Unknown event: {prefix}')
    for story in data['stories']:
        for event in data['events']:
            require((event['id'] in story['eventIds']) == (story['id'] in event['storyIds']), f'Asymmetric event/story relation: {event["id"]}, {story["id"]}')
    routes = all_routes()
    require(len({r['path'] for r in routes}) == len(routes), 'Duplicate route path')
    return errors


def browser_index():
    return {'buildAsOf': CATALOG['buildAsOf'], 'coverageNote': CATALOG['coverageNote'],
            'events': [{**{k:e[k] for k in ('id','title','date','category','region','summary')},'url':event_url(e), 'image': event_image(e)} for e in EVENTS]}


def event_image(event):
    from media_variants import image_record
    key = event.get('art')
    if key in HEROES:
        return {'src':f'/assets/editorial/{key}-hero-768.webp', 'alt':'Original illustrated collage of 90s objects.', 'width':768, 'height':256}
    artifact = next((a for a in ARTIFACTS if a['id']==key),None)
    if artifact and artifact['media']['kind']=='image':
        return image_record({k:artifact['media'][k] for k in ('src','alt','width','height')})
    return None
