"""Shared utility and specialist collection compositions, with explicit deep-link aliases."""
import json
import re
from pathlib import Path
import editorial as ed
import archive_content as model
import archive_pages as ar

ROOT = Path(__file__).resolve().parents[1]
esc = ed.esc
COLLECTIONS = {
    '/zones/fashion/': {
        'kicker': 'CULTURE / THE LOOKBOOK', 'headline': 'Style with a soundtrack', 'art': 'culture',
        'intro': 'Flannel at the thrift store. Logos in the music video. Metallic nylon under club lights. The decade had more than one uniform.',
        'stories': ['clothes-with-a-soundtrack', 'the-catalog-on-your-bedroom-floor', 'meet-me-at-the-mall'],
        'notes': [('Thrift racks & record stores', 'Flannel, faded band tees, thermal layers, worn denim, and scuffed boots made the lived-in look feel personal.'), ('Meet by the fountain', 'Cargo pockets, baby tees, sporty logos, chokers, and catalog wish lists turned the mall into a shared dressing room.'), ('After dark, toward 2000', 'Rave nylon, tiny sunglasses, silver fabric, and iridescent bags gave the end of the decade its synthetic glow.')],
    },
    '/zones/internet-culture/': {
        'kicker': 'CULTURE / THE PERSONAL WEB', 'headline': 'You had to be there', 'art': 'tech',
        'intro': 'A homepage was a place you made. A guestbook was a trace you left. A screen name was a tiny reinvention.',
        'stories': ['a-web-you-could-make', 'choosing-your-screen-name', 'the-internet-came-in-the-mail'],
        'notes': [('Make a little corner of the web', 'Tiled stars, favorite links, a visitor counter, and an under-construction badge: a homepage could be proudly unfinished.'), ('Follow the next link', 'Webrings connected neighboring pages by shared interests. Guestbooks made a quiet visit visible.'), ('Pick your screen name', 'Buddy lists and away messages turned a shared family computer into a surprisingly personal social space.')],
    },
    '/zones/transparent-tech/': {
        'kicker': 'TECH / DESIGN COLLECTION', 'headline': 'The future, in full color', 'art': 'tech',
        'intro': 'At the end of the decade, electronics stopped trying to disappear. Colorful shells made circuitry part of the appeal.',
        'stories': ['you-could-see-through-it', 'the-family-computer', 'a-computer-in-your-pocket'],
        'notes': [('A friendlier desktop', 'The Bondi blue iMac made a computer feel like a designed object for a home, not just office equipment.'), ('Choose your color', 'Translucent handhelds and controllers offered a small act of personalization before you even switched them on.'), ('A glimpse inside', 'Visible boards and screws made sealed consumer technology feel a little more approachable—and collectible.')],
    },
}


def collection(route, builder):
    c = COLLECTIONS[route['path']]
    stories = [next(s for s in model.STORIES if s['id'] == key) for key in c['stories']]
    hero = f'<header class="collection-hero"><div><p class="ar-kicker">{c["kicker"]}</p><h1>{esc(c["headline"])}</h1><p>{esc(c["intro"])}</p><a class="ed-cta" href="#collection-stories">Follow the stories →</a></div><div class="collection-art">{ed.media(c["art"],hero=True)}</div></header>'
    notes = '<section class="collection-notes" id="collection-notes">'+''.join(f'<article><span class="ar-kicker">0{i+1}</span><h2>{esc(title)}</h2><p>{esc(copy)}</p></article>' for i,(title,copy) in enumerate(c['notes']))+'</section>'
    cards = '<section class="hub-section" id="collection-stories">'+ed.heading('The stories behind the style' if 'fashion' in route['path'] else 'Follow the connections','book')+'<div class="collection-stories">'+''.join(ar.story_card(s) for s in stories)+'</div></section>'
    exhibit = ''
    if 'internet-culture' in route['path']:
        exhibit = '<section class="panel interactive-exhibit" id="homepage-exhibit"><p class="ar-kicker">INTERACTIVE EXHIBIT · ORIGINAL RECREATION</p><h2>Your first homepage</h2><p>Add a few essentials of the handmade web.</p>'+builder()+'<p><a href="/guestbook/">Try the guestbook preview →</a> · <a href="/tours/before-the-feed/">Take the personal web tour →</a></p></section>'
    return '<main id="main-content" class="ed-main">'+hero+notes+cards+exhibit+'</main>'


def page(route, search, resource_card, builder):
    path = route['path']
    if path in COLLECTIONS: return collection(route, builder)
    intro = ar.heading('90s.LAND', route['title'],route['summary'])
    if path == '/search/':
        controls, results = search()
        content = controls+results
    elif path == '/webring/':
        resources = json.loads((ROOT/'data/resources.json').read_text())
        categories = dict((r['categoryId'],r['category']) for r in resources)
        filters = ''.join(f'<button type="button" data-resource-filter="{key}" aria-pressed="{str(key=="all").lower()}">{esc(label)}</button>' for key,label in [('all','All resources'),*categories.items()])
        content = f'<section class="panel resource-console"><label for="resourceSearch">Find a resource</label><input id="resourceSearch" type="search" placeholder="Try GeoCities, DOS, music…" autocomplete="off" /><div class="resource-filters" aria-label="Resource categories">{filters}</div></section><section id="directory"><h2 class="ar-section-title">Out on the web</h2><p id="resourceCount" role="status">{len(resources)} external destinations</p><div id="resourceGrid" class="resource-grid">'+''.join(resource_card(r) for r in resources)+'</div><p id="resourceNoResults" class="ar-empty" hidden>No resources match. Try a shorter search or another category.</p></section>'
    elif path == '/guestbook/':
        intro = ar.heading('INTERACTIVE EXHIBIT · ORIGINAL RECREATION','Preview a guestbook entry','Leave a little hello, just like the handmade web. This preview lasts only until you leave or refresh.')
        content = '''<div class="guestbook-layout"><section class="panel"><p id="guestbookNotice" class="sandbox-notice"><strong>Preview only.</strong> Nothing is sent, saved, published, or shared.</p><form id="guestbookForm" data-guestbook-form aria-describedby="guestbookNotice"><label>Your handle<input name="name" maxlength="24" placeholder="xX_sk8r_1997_Xx" required /></label><label>Your message<textarea name="message" maxlength="140" placeholder="this site rules!!!" required></textarea></label><button class="button primary" type="submit">Preview my entry — not saved</button></form><div class="guestbook-preview" data-guestbook-preview hidden aria-label="Guestbook entry preview" role="status"></div></section><aside class="panel"><p class="ar-kicker">SMALL TRACES, BIG CONNECTIONS</p><h2>Someone stopped by.</h2><p>Before likes and feeds, guestbooks gave visitors a way to say hello. A handle, a message, a link back home.</p><a href="/zones/internet-culture/">Explore Internet Culture →</a></aside></div>'''
    elif path == '/sitemap/':
        routes = model.all_routes()
        groups = [('Start exploring', [r for r in routes if r['type'] not in ('events','stories','objects','years')]),('The decade',[r for r in routes if r['type']=='years']),('Stories',[r for r in routes if r['type']=='stories']),('Objects',[r for r in routes if r['type']=='objects'])]
        content = ''.join('<section class="panel sitemap-group"><h2>'+title+'</h2><ul class="sitemap-links">'+''.join(f'<li><a href="{r["path"]}">{esc(r["title"])}</a></li>' for r in rs)+'</ul></section>' for title,rs in groups)
        content += '<section class="panel"><h2>Events by year</h2><p>Open a year for every dated entry.</p>'+''.join(f'<details class="sitemap-year"><summary>{y} · {sum(e["date"].startswith(str(y)) for e in model.EVENTS)} events</summary><ul class="sitemap-links">'+''.join(f'<li><a href="{model.event_url(e)}">{esc(e["title"])}</a></li>' for e in model.EVENTS if e['date'].startswith(str(y)))+'</ul></details>' for y in range(1990,2000))+'</section>'
    else:
        raise ValueError('No composition for '+path)
    return '<main id="main-content" class="ed-main">'+intro+content+'</main>'


def finish_main(route, main, shelf):
    """Compose shared navigation and object sections; aliases contain no old content."""
    path = route['path']
    # Detail pages receive the same breadcrumb as every other family.
    main = re.sub(r'<nav class="ar-breadcrumb".*?</nav>', '', main, flags=re.S)
    main = re.sub(r'(<main\b[^>]*>)',lambda m:m[0]+ed.breadcrumb(route),main,count=1)
    if route.get('type') in ('years','zones') or path == '/':
        shelf_route = dict(route)
        if path == '/': shelf_route['artifactIds'] = ['family-pc','cassette','n64-controller','vhs-tape']
        if '<!-- object-shelf -->' in main:main=main.replace('<!-- object-shelf -->',shelf(shelf_route))
        else:main = main.replace('</main>',shelf(shelf_route)+'</main>')
    # Explicit retired anchors point to the nearest corresponding live section.
    aliases = json.loads((ROOT/'content/deep-links.json').read_text()).get(path,{})
    existing = set(re.findall(r'\bid="([^"]+)"',main)) | {'top','menuToggle','siteNav','museumStatus','surpriseDialog','surpriseTitle','passportDialog','passportTitle','passportResetDialog','passportResetTitle'}
    for target, ids in aliases.items():
        tags = ''.join(f'<span class="anchor-alias" id="{esc(id)}" aria-hidden="true"></span>' for id in ids if id not in existing)
        if not tags: continue
        pattern = r'(<[^>]+\bid="'+re.escape(target)+r'"[^>]*>)'
        if re.search(pattern,main): main = re.sub(pattern,lambda m:tags+m[0],main,count=1)
        else: raise ValueError(f'Deep-link destination missing: {path}#{target}')
    return main
