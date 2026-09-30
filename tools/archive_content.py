"""Authoritative dated archive and route model; never reads generated HTML."""
from __future__ import annotations
import calendar
import json
import re
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATEGORIES = {'music':'Music', 'movies-tv':'Movies & TV', 'games':'Games', 'tech':'Tech', 'culture':'Culture', 'news':'World news'}
THEMES = {'music':'Music', 'movies':'Movies', 'television':'Television', 'games':'Games', 'technology':'Technology', 'internet':'Internet', 'culture':'Culture', 'fashion':'Fashion', 'news':'World news', 'sports':'Sports', 'toys':'Toys & products'}
HEROES = {'home', 'timeline', 'games', 'music', 'movies', 'tech', 'culture'}
CATALOG = json.loads((ROOT/'content/editorial/catalog.json').read_text())
ARTIFACTS = json.loads((ROOT/'data/artifacts.json').read_text())
EVENTS = sorted(CATALOG['events'], key=lambda e: (e['date'], e['id']))
STORIES = CATALOG['stories']
SOURCES = {s['id']: s for s in CATALOG['sources']}
CURATION = json.loads((ROOT/'content/editorial/curation.json').read_text())
YEARS = {y['year']: y for y in CURATION['years']}
EVENT_BY_ID = {e['id']:e for e in EVENTS}
DEFINING_IDS = {id for y in YEARS.values() for id in y['eventIds']}


def defining_events(year):
    return [EVENT_BY_ID[id] for id in YEARS[year]['eventIds']]


def event_label(event):
    return THEMES[event['theme']]


def selected_events(events, limit=4, movie_limit=None):
    """Prefer curated connections and spread a short selection across themes."""
    ranked = sorted(events, key=lambda e: (e['id'] not in DEFINING_IDS, e['date'], e['id']))
    selected=[];themes=set()
    for event in ranked:
        if event['theme'] not in themes:
            selected.append(event);themes.add(event['theme'])
        if len(selected)==limit:return selected
    for event in ranked:
        if len(selected)>=limit: break
        if event not in selected and (movie_limit is None or event['theme']!='movies' or sum(e['theme']=='movies' for e in selected)<movie_limit): selected.append(event)
    return selected


def validate_curation(curation=None, catalog=None):
    data=curation or CURATION;catalog=catalog or CATALOG;errors=[]
    events={e['id']:e for e in catalog['events']};stories={s['id']:s for s in catalog['stories']};objects={a['id']:a for a in ARTIFACTS}
    if data.get('schemaVersion')!=1:errors.append('Unsupported year curation schema')
    years=data.get('years',[])
    if sorted(y['year'] for y in years)!=list(range(1990,2000)):errors.append('Curation needs exactly ten unique years')
    for y in years:
        ids=y.get('eventIds',[]);prefix=f'Curation {y["year"]}'
        if not 10<=len(ids)<=20 or len(ids)!=len(set(ids)):errors.append(prefix+': needs 10–20 distinct moments')
        picks=[events[id] for id in ids if id in events]
        if len(picks)!=len(ids):errors.append(prefix+': unknown event')
        if any(int(e['date'][:4])!=y['year'] for e in picks):errors.append(prefix+': event from another year')
        if len({e['theme'] for e in picks})<5 or sum(e['theme']=='movies' for e in picks)>3:errors.append(prefix+': narrow cultural coverage')
        if not y.get('caption') or not y.get('intro'):errors.append(prefix+': missing introduction')
        if len(y.get('storyIds',[]))!=5 or not set(y['storyIds'])<=stories.keys():errors.append(prefix+': unknown or missing story')
        elif {stories[id]['category'] for id in y['storyIds']}!={'music','movies-tv','games','tech','culture'}:errors.append(prefix+': story collections incomplete')
        if not set(y.get('objectIds',[]))<=objects.keys() or len(y.get('objectIds',[]))<3:errors.append(prefix+': unknown or missing object')
        if any(not objects[id]['dateRange']['startYear']<=y['year']<=objects[id]['dateRange']['endYear'] for id in y.get('objectIds',[]) if id in objects) and not y.get('objectNote'):
            errors.append(prefix+': earlier or later object needs context')
    return errors


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
                require(item.get('theme') in THEMES, f'Unknown event theme: {prefix}')
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
    for tour in json.loads((ROOT/'data/tours.json').read_text()):
        for stop in tour['stops']:
            require(not stop.get('storyId') or stop['storyId'] in ids['stories'], f'Unknown tour story: {stop["id"]}')
            require(not stop.get('eventId') or stop['eventId'] in ids['events'], f'Unknown tour event: {stop["id"]}')
    routes = all_routes()
    require(len({r['path'] for r in routes}) == len(routes), 'Duplicate route path')
    return errors+validate_curation(catalog=data)


def browser_index():
    return {'buildAsOf': CATALOG['buildAsOf'], 'coverageNote': CATALOG['coverageNote'],
            'events': [{**{k:e[k] for k in ('id','title','date','category','theme','region','summary')},'defining':e['id'] in DEFINING_IDS,'url':event_url(e), 'image': event_image(e)} for e in EVENTS]}


def event_image(event):
    from media_variants import image_record
    key = event.get('art')
    if key in HEROES:
        return {'src':f'/assets/editorial/{key}-hero-768.webp', 'alt':'Original illustrated collage of 90s objects.', 'width':768, 'height':256}
    artifact = next((a for a in ARTIFACTS if a['id']==key),None)
    if artifact and artifact['media']['kind']=='image':
        return image_record({k:artifact['media'][k] for k in ('src','alt','width','height')})
    return None
