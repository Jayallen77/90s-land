"""Search and sharing metadata for the existing public catalog."""
import json
import archive_content as archive

SITE_URL = 'https://90s.land'
NOINDEX = {'/search/', '/guestbook/', '/404.html'}
COLLECTION_TITLES = {
    '/zones/music/': '90s Music: Albums, Mixtapes & Stories',
    '/zones/tv-movies/': '90s Movies & TV: Releases and Stories',
    '/zones/games/': '90s Gaming: Consoles, Games & Stories',
    '/zones/tech-toys/': '90s Technology: Computers, Gadgets & the Web',
    '/zones/culture/': '90s Culture: Toys, Sports & Everyday Life',
    '/zones/fashion/': '90s Fashion: Grunge, Streetwear & Mall Style',
    '/zones/internet-culture/': '90s Internet Culture: Homepages, AIM & Webrings',
    '/zones/transparent-tech/': '90s Transparent Electronics: iMac, Game Boy & N64',
}
FOCUSED_TITLES = {
    '/': 'A playable museum of the 1990s',
    '/timeline/': '1990s Timeline: Explore 1990–1999',
    '/this-week/': 'This Week in the 90s: Your Week, 30 Years Earlier',
    '/stories/friday-at-the-video-store/': 'Friday at the Video Store: 90s Movie Rental Nights',
    '/stories/choosing-your-screen-name/': 'Choosing Your Screen Name: AIM in the 90s',
    '/archive/objects/aim-away-message/': 'AIM Away Messages: A Little Room of Your Own',
    '/archive/objects/y2k-office/': 'Y2K Office: Technology at Midnight in 1999',
}


def metadata(route):
    title = COLLECTION_TITLES.get(route['path'], FOCUSED_TITLES.get(route['path'], route['title']))
    if route.get('type') == 'years':
        year = int(route['path'].strip('/').split('/')[-1])
        title = f'{year} Timeline & Defining Moments'
    description = route['summary']
    if route['path'] == '/this-week/':
        description = 'Explore the equivalent Monday–Sunday week 30 years ago: sourced events from the 1990s, a few defining moments, and the full day-by-day calendar.'
    return {'title':f'{title} — 90s.land', 'description':description,
            'canonical':SITE_URL+route['path'], 'indexable':route['path'] not in NOINDEX}


def card_routes():
    """Specific cards for all principal pages and curated historical events."""
    return [r for r in archive.all_routes() if r['type'] != 'events' or r['id'].removeprefix('event-') in archive.DEFINING_IDS]


def card_route(route):
    if route.get('type') == 'events' and route['id'].removeprefix('event-') not in archive.DEFINING_IDS:
        year = archive.EVENT_BY_ID[route['id'].removeprefix('event-')]['date'][:4]
        return '/timeline/'+year+'/'
    return route['path'] if route['path'] != '/404.html' else '/'


def social_spec(route):
    path = route['path']; kind = route['type']; objects = {a['id']:a for a in archive.ARTIFACTS}
    title = route['title']; label = 'EXPLORE THE MUSEUM'; art = None
    if path == '/': title = 'The 90s live on'; label = 'A PLAYABLE MUSEUM'; art = 'home'
    elif kind == 'years':
        year = int(path.strip('/').split('/')[-1]); title = str(year); label = 'DEFINING MOMENTS'
        art = 'timeline' if year == 1996 else next((id for id in archive.YEARS[year]['objectIds'] if objects[id]['media']['kind']=='image'), None)
    elif kind == 'objects':
        a = next(a for a in archive.ARTIFACTS if archive.object_url(a)==path)
        label = 'OBJECT ARCHIVE · '+a['dateRange']['label']; art = a['id']
    elif kind == 'stories':
        s = next(s for s in archive.STORIES if archive.story_url(s)==path)
        label = 'A STORY FROM THE 90s'; art = s['art'] or next(iter(s['objectIds']), None)
    elif kind == 'events':
        e = next(e for e in archive.EVENTS if archive.event_url(e)==path)
        label = e['date']+' · '+archive.event_label(e).upper(); art = e['art']
    elif path in COLLECTION_TITLES:
        title = COLLECTION_TITLES[path].split(':')[0]; label = 'EXPLORE A COLLECTION'
        art = {'/zones/music/':'music','/zones/tv-movies/':'movies','/zones/games/':'games','/zones/tech-toys/':'tech','/zones/culture/':'culture','/zones/fashion/':'culture','/zones/internet-culture/':'mosaic-browser','/zones/transparent-tech/':'bondi-imac'}[path]
    elif path == '/this-week/': title = 'Your week. 30 years earlier.'; label = 'THIS WEEK IN THE 90s'; art = 'cassette'
    elif kind == 'tours': title = 'Before the Feed'; label = 'SIX STOPS THROUGH THE PERSONAL WEB'; art = 'family-pc'
    elif route.get('artifactIds'): art = route['artifactIds'][0]
    visual = None
    if art in archive.HEROES:
        visual = {'src':f'/assets/editorial/{art}-hero-1440.webp', 'credit':'Original AI-generated editorial illustration · OpenAI', 'license':'Original artwork', 'label':'EDITORIAL ILLUSTRATION'}
    elif art in objects and objects[art]['media']['kind'] == 'image':
        media = objects[art]['media']; visual = {'src':media['src'], 'credit':media['credit'], 'license':media['license'], 'label':'OBJECT FROM THE COLLECTION'}
    else:
        visual = {'src':None, 'credit':'90s.land · original graphic', 'license':'Original artwork', 'label':'ORIGINAL GRAPHIC'}
    subtitle = archive.YEARS[int(title)]['caption'] if kind == 'years' else route['summary']
    return {'path':path, 'id':route['id'], 'title':title, 'label':label, 'subtitle':subtitle,
            'visual':visual, 'alt':f'90s.land sharing card: {title}. '+visual['label'].capitalize()+'.'}


def structured_navigation(route, parent):
    if route['path'] == '/':
        data = {'@context':'https://schema.org', '@type':'WebSite', 'name':'90s.land', 'url':SITE_URL+'/', 'description':metadata(route)['description']}
    elif route['path'] == '/404.html': return ''
    else:
        items = [('Home','/')]
        label, href = parent
        if href not in ('/',route['path']): items.append((label,href))
        items.append((route['title'],route['path']))
        data = {'@context':'https://schema.org', '@type':'BreadcrumbList', 'itemListElement':[{'@type':'ListItem','position':i,'name':label,'item':SITE_URL+href} for i,(label,href) in enumerate(items,1)]}
    return '<script type="application/ld+json">'+json.dumps(data,ensure_ascii=False).replace('<','\\u003c')+'</script>'
