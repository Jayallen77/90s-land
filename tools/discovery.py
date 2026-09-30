"""Published destinations for the museum's lightweight discovery shuffle."""
import archive_content as archive

KINDS = ('story', 'object', 'event', 'year', 'collection', 'tour')


def surprise_pool():
    rows = []
    def add(id, kind, title, teaser, date, room, target):
        rows.append(dict(id=id, kind=kind, title=title, teaser=teaser,
                         dateLabel=date, room=room, target=target))
    for s in archive.STORIES:
        if s['status'] == 'published':
            add('story-'+s['id'], 'story', s['title'], s['summary'], 'The 1990s',
                archive.CATEGORIES[s['category']]+' story', archive.story_url(s))
    for a in archive.ARTIFACTS:
        if a['randomEligible'] and a['status'] != 'needs-source':
            add(a['id'], 'object', a['title'], a['curatorNote'], a['dateRange']['label'],
                'Object archive', archive.object_url(a))
    for e in archive.EVENTS:
        if e['id'] in archive.DEFINING_IDS:
            add('event-'+e['id'], 'event', e['title'], e['summary'], e['date'],
                archive.event_label(e)+' moment', archive.event_url(e))
    for route in archive.all_routes():
        kind = {'years':'year', 'zones':'collection', 'tours':'tour'}.get(route['type'])
        if kind:
            add(route['id'], kind, route['title'], route['summary'],
                route['path'].strip('/').split('/')[-1] if kind=='year' else 'The 1990s',
                {'year':'Year timeline','collection':'Collection','tour':'Guided tour'}[kind], route['path'])
    return rows
