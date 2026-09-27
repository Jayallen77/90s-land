"""Shared editorial shell and core compositions built from authored source files."""
from __future__ import annotations

import calendar
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORE = {'/': 'home', '/zones/games/': 'games'}
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
        active = current == href or (href == '/timeline/' and current.startswith('/timeline/'))
        items.append(f'<a href="{href}"'+(' aria-current="page"' if active else '')+f'>{esc(label)}</a>')
    return f'''<header class="ed-header" id="top">
      <a class="ed-brand" href="/" aria-label="90s.land home"><img src="/assets/editorial/palm-sunset.svg" alt="" width="180" height="105" loading="eager" decoding="async" /><span class="ed-wordmark">90s.land</span><span class="ed-tagline">RELIVE THE DECADE</span></a>
      <p class="ed-motto"><span aria-hidden="true">☻</span> GOOD TIMES<br />ALWAYS HERE</p>
      <button class="menu-toggle" id="menuToggle" type="button" aria-expanded="false" aria-controls="siteNav">☰ <span>Menu</span></button>
      <nav id="siteNav" class="ed-nav" aria-label="Main navigation">{''.join(items)}<a class="ed-search" href="/search/" aria-label="Search the 90s">{icon('search')}</a></nav>
    </header>'''


def discovery():
    return f'''<nav class="ed-discovery" aria-label="More ways to explore"><span>{icon('book')} KEEP EXPLORING</span><a href="/tours/before-the-feed/">Take the tour <b>↗</b></a><a href="/surprise/" data-surprise-trigger>Surprise me</a><button type="button" data-passport-trigger hidden>Passport <span data-passport-count>0</span></button><a href="/webring/">The old web ↗</a><a href="/guestbook/">Guestbook</a></nav>'''


def shell_footer():
    return '''<footer class="ed-footer"><span>© 1999–forever <b>90s.land</b> · Same decade. Different day.</span><nav aria-label="Footer"><a href="/sitemap/">Site map</a><a href="/credits/">Sources & artwork</a><a href="#top">Back to top ↑</a></nav></footer>'''


def apply_shell(source, route):
    source = re.sub(r'<header class="(?:topbar|ed-header)".*?</header>', lambda _: shell_header(route), source, count=1, flags=re.S)
    source = re.sub(r'<footer class="(?:footer|ed-footer)".*?</footer>', lambda _: shell_footer(), source, count=1, flags=re.S)
    source = re.sub(r'<nav class="ed-discovery".*?</nav>\s*(?=<footer class="ed-footer")', '', source, flags=re.S)
    # Core compositions put discovery before their preserved reading rooms.
    if route['path'] not in CORE:
        source = source.replace('<footer class="ed-footer">', discovery()+'\n<footer class="ed-footer">',1)
    if '/editorial.css?' not in source:
        source = source.replace('</head>', '  <link rel="stylesheet" href="/editorial.css?v=phase4-1" />\n</head>')
    source = source.replace("</head>", '  <link rel="stylesheet" href="/archive.css?v=phase4-1" />\n  <link rel="stylesheet" href="/hub.css?v=phase4-1" />\n</head>')
    return source


def media(key, *, hero=False):
    if key in ('home','timeline','games','music','movies','tech','culture'):
        alt = {'home':'Original illustrated collage of a CRT television, VHS tapes, sneaker and game hardware.','timeline':'Original illustrated collage of 1996-era game consoles, sports car, basketball and music.','games':'Original illustrated collage of a CRT platform game, console, handheld and arcade cabinet.','music':'Original AI-generated still-life collage of cassettes, CDs, headphones and music equipment.','movies':'Original AI-generated still-life collage of VHS tapes, a CRT, popcorn and movie-night objects.','tech':'Original AI-generated still-life collage of a translucent computer, a beige PC, discs and portable electronics.','culture':'Original AI-generated still-life collage of mall-era shopping, sneakers, toys and personal accessories.'}[key]
        return f'<img src="/assets/editorial/{key}-hero-1440.webp" srcset="/assets/editorial/{key}-hero-768.webp 768w, /assets/editorial/{key}-hero-1440.webp 1440w, /assets/editorial/{key}-hero-2172.webp 2172w" sizes="'+('(max-width: 1440px) 100vw, 1440px' if hero else '(max-width: 600px) 90vw, 420px')+f'" alt="{alt}" width="2172" height="724" loading="'+('eager' if hero else 'lazy')+'" decoding="async"'+(' fetchpriority="high"' if hero else '')+' />'
    item = ARTIFACTS[key]['media']
    return f'<img src="{esc(item["src"])}" alt="{esc(item["alt"])}" width="{item["width"]}" height="{item["height"]}" loading="lazy" decoding="async" />'


def hero(kind):
    copy = {
        'home': ('THE 90s<br /> LIVE ON', '', 'The music, the movies, the games,<br /> the culture, and everything that<br /> made the 90s legendary.', 'Explore the decade', '/timeline/'),
        'timeline': ('1996','A YEAR THAT HIT DIFFERENT','New dimensions. New sounds. A world getting online.<br /> Revisit the objects, releases, and cultural moments<br /> that made 1996 unforgettable.','',''),
        'games': ('GAME ON','THE 90s GAME ERA','16-bit adventures. 3D worlds. Arcade legends.<br />Handheld gaming everywhere. The 90s changed<br />games forever — and it was only the beginning.','Explore the era','#game-guide')
    }[kind]
    cta = f'<a class="ed-cta" href="{copy[4]}">{copy[3]} {icon("arrow")}</a>' if copy[3] else ''
    return f'<section class="ed-hero ed-hero-{kind}">{media(kind,hero=True)}<div class="ed-hero-copy"><h1>{copy[0]}</h1>'+ (f'<h2>{copy[1]}</h2>' if copy[1] else '')+f'<p>{copy[2]}</p>{cta}</div></section>'


def heading(title, glyph='star', href=None, extra=''):
    return f'<div class="ed-panel-heading"><h2>{icon(glyph)} {esc(title)}</h2>'+ (f'<a href="{href}">VIEW ALL →</a>' if href else '')+extra+'</div>'


def tile(title, href, art, subtitle='', badge='', cls=''):
    return f'<a class="ed-tile {cls}" href="{esc(href)}"><div class="ed-tile-art">{media(art)}</div><div class="ed-tile-copy">'+(f'<span class="ed-badge">{esc(badge)}</span>' if badge else '')+f'<h3>{esc(title)}</h3>'+(f'<p>{esc(subtitle)}</p>' if subtitle else '')+'</div></a>'


def preserved_content(route):
    import archive_content
    source = archive_content.page_source(route)
    content = re.sub(r'^<main[^>]*>', '', source.strip())
    content = re.sub(r'</main>$', '', content)
    content = re.sub(r'<h1(\s[^>]*)?>', r'<h2\1>', content).replace('</h1>','</h2>')
    content = content.replace(' loading="eager"',' loading="lazy"').replace(' fetchpriority="high"','')
    # Primary actions live in discovery now, so avoid duplicate dialog triggers.
    content = content.replace(' data-surprise-trigger','')
    title = {'/':'More to explore: the original museum desk','/timeline/1996/':'The complete 1996 reading room','/zones/games/':'The games reading room & hardware collection'}.get(route['path'], f'The complete {route["title"]} reading room')
    return f'<details class="ed-reading-room" data-reading-room><summary>{icon("book")} {title}<span>OPEN ARCHIVE +</span></summary><div class="ed-preserved">{content}</div></details>'


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
    return hero('home')+f'''<div class="ed-home-grid">
      {week_feature()}
      <section class="ed-panel ed-feature">{heading('Featured')}{tile('A web you could make your own','/stories/a-web-you-could-make/','first-website','A public idea. A more personal kind of internet.','STORY')}</section>
      <section class="ed-panel">{heading('Browse the 90s','folder')}<div class="ed-categories">{category_html}</div></section>
    </div><section class="ed-picks">{heading('On heavy rotation','bolt','/search/', '<span class="ed-selection-note">EDITOR PICKS</span>')}<div class="ed-six-up">{''.join(tile(t,h,a) for t,h,a in picks)}</div></section>'''


def games():
    rail = [('All games','#game-guide','games'),('Consoles','#co-op-path','games'),('PC games','#game-media','tech'),('Arcade','#artifact-arcade-cabinet','bolt'),('Handhelds','/zones/transparent-tech/#artifact-game-boy-color','games'),('Console wars','#why','trophy'),('Co-op','#co-op-path','games'),('Cheat codes','#game-artifacts','star'),('History','#game-media','book')]
    ranked = [('Arcade nights','Quarter up. Your turn is next.','arcade-cabinet','#artifact-arcade-cabinet','ARCADE'),('The console-war couch','Choose a side. Pass a controller.','genesis-controller','#co-op-path','CONSOLE'),('A whole new dimension','The analog stick changes the room.','n64-controller','#artifact-n64-controller','3D'),('Shareware & LAN nights','One disk. A room full of friends.','doom-disks','#game-media','PC'),('Gaming on the go','A world that fits in your pocket.','game-boy-color','/zones/transparent-tech/#artifact-game-boy-color','HANDHELD')]
    ranks = ''.join(f'<a class="ed-rank" href="{href}"><span class="ed-rank-number">{i+1}</span>{media(art)}<span><strong>{title}</strong><small>{desc}</small></span><b>{tag}</b><span aria-hidden="true">›</span></a>' for i,(title,desc,art,href,tag) in enumerate(ranked))
    platforms=[('Console games','#artifact-genesis-controller','genesis-controller','From 16-bit to 3D.'),('PC games','#game-media','family-pc','DOS, discs, and dial-up.'),('Arcade games','#artifact-arcade-cabinet','arcade-cabinet','The original multiplayer.'),('Handheld games','/zones/transparent-tech/#artifact-game-boy-color','game-boy-color','Adventures to go.')]
    facts=[('16-bit generation','Rivalries come home.','games'),('The rise of 3D','Explore a new dimension.','tech'),('Handheld boom','One more level, anywhere.','bolt'),('Arcade culture','Quarter up. Beat the score.','trophy'),('New connections','Play together. Stay up late.','culture')]
    dives=[('LAN parties','#game-media','family-pc','Friends. Cables. All night.'),('The 3D revolution','#artifact-n64-controller','n64-controller','A new dimension of play.'),('Memory cards','#game-artifacts','games','Small cards. Big saves.'),('Cheat codes','#game-artifacts','genesis-controller','Secrets passed between friends.'),('Couch co-op','#co-op-path','games','Multiplayer meant together.')]
    return hero('games')+f'''<nav class="ed-topic-rail" aria-label="Gaming topics">{''.join(f'<a href="{href}">{icon(glyph)} {title}</a>' for title,href,glyph in rail)}</nav>
    <div class="ed-games-grid" id="game-guide"><section class="ed-panel ed-feature">{heading('Featured story')}{tile('A whole new dimension','/stories/a-whole-new-dimension/','games','How 3D changed the spaces we explored—and the controllers in our hands.','STORY')}</section>
    <section class="ed-panel ed-ranking">{heading('Five ways into the era','trophy')}{ranks}<span class="ed-selection-note">A CURATOR’S STARTING FIVE</span></section>
    <section class="ed-panel ed-platforms">{heading('Browse by platform','folder')}<div class="ed-two-up">{''.join(tile(t,h,a,s) for t,h,a,s in platforms)}</div></section>
    <aside class="ed-panel ed-facts">{heading('Era at a glance','bolt')}{''.join(f'<a href="#fast-read">{icon(glyph)}<span><strong>{title}</strong><small>{desc}</small></span></a>' for title,desc,glyph in facts)}</aside></div>
    <div class="ed-games-bottom"><section class="ed-panel">{heading('Deep dives','book')}<div class="ed-five-up">{''.join(tile(t,h,a,s) for t,h,a,s in dives)}</div></section><section class="ed-panel">{heading('From the collection','bolt','/search/?filter=objects')}<div class="ed-three-up">{tile('The six-button advantage','#artifact-genesis-controller','genesis-controller')}{tile('The three-pronged future','#artifact-n64-controller','n64-controller')}{tile('Pocket-sized worlds','/zones/transparent-tech/','game-boy-color')}</div></section></div>'''



def main(route):
    kind = CORE[route['path']]
    composition = {'home':home, 'games':games}[kind]()
    return f'<main id="main-content" class="ed-main ed-page-{kind}">{composition}{discovery()}{preserved_content(route)}</main>'
