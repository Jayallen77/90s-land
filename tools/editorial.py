"""Shared editorial shell and core compositions built from authored source files."""
from __future__ import annotations

import calendar
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORE = {'/': 'home'}
ARTIFACTS = {a['id']: a for a in json.loads((ROOT / 'data/artifacts.json').read_text())}
NAVIGATION = json.loads((ROOT / 'data/navigation.json').read_text())


def esc(value):
    return html.escape(str(value), quote=True)


def icon(name):
    paths = {
        'star': '<path d="m12 2 3 6 7 1-5 5 1 7-6-3-6 3 1-7-5-5 7-1z"/>',
        'games': '<path d="M7 7h10c3 0 5 12 2 12-2 0-4-4-5-4h-4c-1 0-3 4-5 4C2 19 4 7 7 7Z"/><path d="M7 10v4m-2-2h4m7-2h.1m2 3h.1"/>',
        'music': '<path d="M9 17V5l11-2v12M9 8l11-2"/><ellipse cx="6" cy="18" rx="3" ry="2"/><ellipse cx="17" cy="16" rx="3" ry="2"/>',
        'movies': '<rect x="3" y="8" width="18" height="13" rx="1"/><path d="m3 8-1-5 18-2 1 5-18 2m3-5 3 4m3-5 3 4"/>',
        'tech': '<rect x="3" y="2" width="18" height="14" rx="1"/><path d="M9 16v4m6-4v4M5 21h14"/>',
        'culture': '<path d="M2 9h8l2 3 2-3h8l-2 6h-5l-3-3-3 3H4z"/>',
        'fashion': '<path d="m8 3 4 2 4-2 6 5-4 4-2-2v12H8V10l-2 2-4-4z"/>',
        'calendar': '<rect x="3" y="5" width="18" height="17" rx="1"/><path d="M3 10h18M7 2v6m10-6V2M7 14h2m3 0h2m3 0h1M7 18h2m3 0h2"/>',
        'folder': '<path d="M2 7V4h8l3 3h9v14H2zM2 10h20"/>',
        'search': '<circle cx="10" cy="10" r="7"/><path d="m15 15 7 7"/>',
        'book': '<path d="M12 5C8 2 4 2 2 3v17c4-1 7-1 10 2 3-3 6-3 10-2V3c-2-1-6-1-10 2v17"/>',
        'bolt': '<path d="m13 1-9 13h7l-1 9 10-14h-7z"/>',
        'arrow': '<path d="M3 12h18m-7-7 7 7-7 7"/>',
        'trophy': '<path d="M7 2h10v8a5 5 0 0 1-10 0zM7 4H2v4c0 3 3 5 6 5m9-9h5v4c0 3-3 5-6 5m-4 2v6m-5 0h10"/>',
    }
    return f'<svg class="ed-icon" viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">{paths.get(name, paths["star"])}</svg>'


def shell_header(route):
    links = [(item['label'], item['href']) for item in NAVIGATION]
    current = route['path']
    items = []
    for label, href in links:
        active = current == href or (href == '/timeline/' and current.startswith('/timeline/')) or (href != '/' and parent_section(route)[1] == href)
        items.append(f'<a href="{href}"'+(' aria-current="page"' if active else '')+f'>{esc(label)}</a>')
    return f'''<header class="ed-header" id="top">
      <a class="ed-brand" href="/"><img src="/assets/editorial/palm-sunset.svg" alt="" width="180" height="105" loading="eager" decoding="async" /><span class="ed-wordmark">90s.land</span> <span class="ed-tagline">RELIVE THE DECADE</span><span class="sr-only"> home</span></a>
      <p class="ed-motto"><span aria-hidden="true">☻</span> GOOD TIMES<br />ALWAYS HERE</p>
      <button class="menu-toggle" id="menuToggle" type="button" aria-expanded="false" aria-controls="museumDirectory" aria-haspopup="dialog">☰ <span>Menu</span></button>
      <a class="directory-fallback" href="/sitemap/">Museum directory</a>
      <nav id="siteNav" class="ed-nav" aria-label="Main navigation">{''.join(items)}<a class="ed-search" href="/search/" aria-label="Search the 90s">{icon('search')}</a></nav>
    </header>'''


def directory():
    groups = [
        ('Explore', [('Home', '/'), ('Timeline', '/timeline/'), ('This Week', '/this-week/'), ('Stories', '/stories/'), ('Objects', '/archive/objects/')]),
        ('Collections', [(item['label'], item['href']) for item in NAVIGATION if item['href'].startswith('/zones/')] + [('Fashion', '/zones/fashion/'), ('Internet Culture', '/zones/internet-culture/'), ('Transparent Tech', '/zones/transparent-tech/')]),
        ('Play / Experience', [('Before the Feed', '/tours/before-the-feed/'), ('Surprise Me', '/surprise/')]),
        ('More', [('Search', '/search/'), ('Resources', '/webring/'), ('Sources & Credits', '/credits/'), ('Sitemap', '/sitemap/'), ('Guestbook preview', '/guestbook/')]),
    ]
    sections = []
    for title, links in groups:
        items = ''.join(f'<a href="{href}">{esc(label)}</a>' for label, href in links)
        if title == 'Play / Experience':
            items += '<button type="button" data-directory-passport>Passport <span data-passport-count>0</span></button>'
        sections.append(f'<section><h3>{esc(title)}</h3>{items}</section>')
    return f'''<dialog class="museum-dialog directory-dialog" id="museumDirectory" aria-labelledby="directoryTitle">
      <div class="dialog-heading"><h2 id="directoryTitle">The museum directory</h2><button type="button" class="dialog-close" data-dialog-close="museumDirectory" aria-label="Close museum directory">×</button></div>
      <nav class="directory-grid" aria-label="Museum directory">{''.join(sections)}</nav>
    </dialog>'''


def discovery():
    return f'''<nav class="ed-discovery" aria-label="More ways to explore"><span>{icon('book')} KEEP EXPLORING</span><a href="/tours/before-the-feed/">Take the tour <b>↗</b></a><a href="/surprise/" data-surprise-trigger>Surprise me</a><button type="button" data-passport-trigger hidden>Passport <span data-passport-count>0</span></button><a href="/webring/">Resources ↗</a><a href="/guestbook/">Guestbook preview</a></nav>'''


def shell_footer():
    return '''<footer class="ed-footer"><span>© 1999–forever <b>90s.land</b> · Same decade. Different day.</span><nav aria-label="Footer"><a href="/sitemap/">Site map</a><a href="/credits/">Sources & artwork</a><a href="#top">Back to top ↑</a></nav></footer>'''


def media(key, *, hero=False):
    if key in ('home','timeline','games','music','movies','tech','culture'):
        alt = {'home':'Original illustrated collage of a CRT television, VHS tapes, sneaker and game hardware.','timeline':'Original illustrated collage of 1996-era game consoles, sports car, basketball and music.','games':'Original illustrated collage of a CRT platform game, console, handheld and arcade cabinet.','music':'Original AI-generated still-life collage of cassettes, CDs, headphones and music equipment.','movies':'Original AI-generated still-life collage of VHS tapes, a CRT, popcorn and movie-night objects.','tech':'Original AI-generated still-life collage of a translucent computer, a beige PC, discs and portable electronics.','culture':'Original AI-generated still-life collage of mall-era shopping, sneakers, toys and personal accessories.'}[key]
        return f'<img src="/assets/editorial/{key}-hero-1440.webp" srcset="/assets/editorial/{key}-hero-768.webp 768w, /assets/editorial/{key}-hero-1440.webp 1440w, /assets/editorial/{key}-hero-2172.webp 2172w" sizes="'+('(max-width: 1440px) 100vw, 1440px' if hero else '(max-width: 600px) 90vw, 420px')+f'" alt="{alt}" width="2172" height="724" loading="'+('eager' if hero else 'lazy')+'" decoding="async"'+(' fetchpriority="high"' if hero else '')+' />'
    if key not in ARTIFACTS or ARTIFACTS[key]['media']['kind'] != 'image':
        label = ARTIFACTS[key]['title'] if key in ARTIFACTS else '90s.land'
        return graphic(label)
    item = ARTIFACTS[key]['media']
    return f'<img src="{esc(item["src"])}" alt="{esc(item["alt"])}" width="{item["width"]}" height="{item["height"]}" sizes="(max-width: 600px) 45vw, (max-width: 1000px) 33vw, 360px" loading="lazy" decoding="async" />'


def hero(kind):
    copy = {
        'home': ('THE 90s<br /> LIVE ON', '', 'Pick a year. Find a familiar object.<br /> Follow a story you nearly forgot.<br /> Your next rabbit hole starts here.', 'Explore the decade', '#browse-decade'),
        'timeline': ('1996','POCKET MONSTERS. BROWSER INBOXES.','A new controller on the couch.<br /> A tiny pet asking to be fed.<br /> Let’s open the year.','',''),
        'games': ('GAME ON','THE 90s GAME ERA','Plug in a second controller.<br /> Borrow a cartridge. Find a secret.<br /> There’s room on the couch.','Explore the era','#game-guide')
    }[kind]
    cta = f'<a class="ed-cta" href="{copy[4]}">{copy[3]} {icon("arrow")}</a>' if copy[3] else ''
    return f'<section class="ed-hero ed-hero-{kind}">{media(kind,hero=True)}<div class="ed-hero-copy"><h1>{copy[0]}</h1>'+ (f'<h2>{copy[1]}</h2>' if copy[1] else '')+f'<p>{copy[2]}</p>{cta}</div></section>'


def heading(title, glyph='star', href=None, extra=''):
    return f'<div class="ed-panel-heading"><h2>{icon(glyph)} {esc(title)}</h2>'+ (f'<a href="{href}">VIEW ALL →</a>' if href else '')+extra+'</div>'


def tile(title, href, art, subtitle='', badge='', cls=''):
    return f'<a class="ed-tile {cls}" href="{esc(href)}"><div class="ed-tile-art">{media(art)}</div><div class="ed-tile-copy">'+(f'<span class="ed-badge">{esc(badge)}</span>' if badge else '')+f'<h3>{esc(title)}</h3>'+(f'<p>{esc(subtitle)}</p>' if subtitle else '')+'</div></a>'


def week_feature():
    from datetime import date
    import archive_content as archive
    day = archive.historical_date(date.fromisoformat(archive.CATALOG['buildAsOf']))
    start, end = archive.week_bounds(day)
    picks = [e for e in archive.EVENTS if start.isoformat() <= e['date'] <= end.isoformat() and e['category'] != 'news']
    pick = picks[0] if picks else None
    summary = pick['summary'] if pick else 'Turn back the clock. Explore the week’s dates, the decade’s stories, and the objects you remember.'
    title = pick['title'] if pick else 'Open the historical week →'
    href = archive.event_url(pick) if pick else '/this-week/'
    label = f'{start.strftime("%b %-d, %Y")} – {end.strftime("%b %-d, %Y")}'
    return f'''<section class="ed-panel ed-week" id="this-week"><div class="ed-week-art">{media(pick['art'] if pick and pick.get('art') and (pick['art'] not in ARTIFACTS or ARTIFACTS[pick['art']]['media']['kind']=='image') else 'home')}</div><div class="ed-week-copy"><h2>{icon('calendar')} <span>THIS WEEK IN<strong>{day.year}</strong></span></h2><p class="ed-date">{label}</p><p data-home-week-copy>{esc(summary)}</p><a class="ed-cta" href="/this-week/">Explore this week {icon('arrow')}</a></div><div class="ed-week-note"><a href="{href}">{esc(title)} →</a></div></section>'''


def home():
    categories = [('Music','music','/zones/music/'),('Movies & TV','movies','/zones/tv-movies/'),('Games','games','/zones/games/'),('Tech','tech','/zones/tech-toys/'),('Culture','culture','/zones/culture/'),('Fashion','fashion','/zones/fashion/')]
    category_html = ''.join(f'<a class="ed-category ed-color-{i}" href="{href}">{icon(key)}<strong>{title}</strong></a>' for i,(title,key,href) in enumerate(categories))
    picks = [('Friday night at the video store','/stories/friday-at-the-video-store/','blockbuster-store'),('The art of the mixtape','/stories/from-mixtape-to-file/','cassette'),('The controller that changed play','/stories/a-whole-new-dimension/','n64-controller'),('Before every room had a screen','/stories/the-family-computer/','family-pc'),('The transparent tech obsession','/stories/you-could-see-through-it/','game-boy-color'),('When the internet came in the mail','/stories/the-internet-came-in-the-mail/','aol-cd')]
    from archive_content import YEARS
    years='<section class="ed-home-decade" id="browse-decade">'+heading('Browse the decade','calendar')+'<nav class="ed-decade" aria-label="Browse a year">'+''.join(f'<a href="/timeline/{y}/" aria-label="{y}: {esc(YEARS[y]["caption"])}">{y}</a>' for y in range(1990,2000))+'</nav></section>'
    finder='<form class="ed-home-search" action="/search/" role="search"><label for="home-search">Something on your mind?</label><input id="home-search" name="q" type="search" placeholder="Try N64, Friends, or 1998" /><button type="submit" class="button">Search the museum →</button></form>'
    experiences=f'''<section class="hub-section ed-experiences" id="take-an-experience">{heading('Take an experience','bolt')}<div class="ed-three-up"><article class="ed-panel"><p class="ar-kicker">GUIDED TOUR · 10 MINUTES</p><h3>Before the Feed</h3><p>A shared PC, a handmade homepage, a carefully chosen screen name. Follow six stops through the personal web.</p><a class="ed-cta" href="/tours/before-the-feed/">Start the tour →</a></article><article class="ed-panel"><p class="ar-kicker">ONE UNEXPECTED OBJECT</p><h3>Surprise Me</h3><p>Let the museum pick your next memory. A controller, a cassette, or a little corner of the early Web.</p><a class="ed-cta" href="/surprise/">Find a surprise →</a></article><article class="ed-panel"><p class="ar-kicker">YOUR COLLECTION</p><h3>Museum Passport</h3><p>Inspect objects, visit collections, and collect stamps. Your progress stays on this device.</p><button type="button" class="ed-cta" data-home-passport hidden>Open Passport →</button><noscript><p><a href="/archive/objects/">Browse objects</a>. Enable JavaScript to collect stamps.</p></noscript></article></div></section>'''
    return hero('home')+years+f'''<div class="ed-home-grid">
      {week_feature()}
      <section class="ed-panel ed-feature">{heading('Featured')}{tile('A web you could make your own','/stories/a-web-you-could-make/','mosaic-browser','A public idea. A more personal kind of internet.','STORY')}</section>
      <section class="ed-panel">{heading('Explore a collection','folder')}<div class="ed-categories">{category_html}</div><a class="ed-text-link" href="/zones/internet-culture/">Internet Culture →</a></section>
    </div>{finder}<section class="ed-picks">{heading('On heavy rotation','bolt','/stories/', '<span class="ed-selection-note">EDITOR PICKS</span>')}<div class="ed-six-up">{''.join(tile(t,h,a) for t,h,a in picks)}</div></section><!-- object-shelf -->{experiences}'''


def main(route):
    return '<main id="main-content" class="ed-main">'+home()+'</main>'

SECTION_ROUTES = {'music': ('Music', '/zones/music/'), 'movies-tv': ('Movies & TV', '/zones/tv-movies/'), 'games': ('Games', '/zones/games/'), 'tech': ('Tech', '/zones/tech-toys/'), 'culture': ('Culture', '/zones/culture/')}


def parent_section(route):
    import archive_content as model
    path = route['path']
    if path == '/events/': return ('Timeline', '/timeline/')
    if path.startswith('/timeline/'): return ('Timeline', '/timeline/')
    if path in ('/zones/fashion/', '/zones/internet-culture/'): return SECTION_ROUTES['culture']
    if path == '/zones/transparent-tech/': return SECTION_ROUTES['tech']
    for item in model.STORIES + model.EVENTS:
        if path in (model.story_url(item), model.event_url(item)):
            return SECTION_ROUTES.get(item['category'], ('Timeline', '/timeline/'))
    if route.get('type') == 'objects': return ('Objects', '/archive/objects/')
    return ('Home', '/')


def breadcrumb(route):
    if route['path'] == '/': return ''
    label, href = parent_section(route)
    parent = f'<span aria-hidden="true">/</span><a href="{href}">{esc(label)}</a>' if href not in ('/',route['path']) else ''
    return f'<nav class="ar-breadcrumb" aria-label="Breadcrumb"><a href="/">Home</a>{parent}<span aria-hidden="true">/</span><span aria-current="page">{esc(route["title"])}</span></nav>'


def graphic(title, kicker='FROM THE 90s', glyph='star'):
    return f'<div class="ed-graphic"><span>{icon(glyph)} {esc(kicker)}</span><strong>{esc(title)}</strong><span class="graphic-rule" aria-hidden="true"></span></div>'
