"""Complete section compositions and small, sourced discovery collections."""
import json
import editorial as ed
import archive_content as model
import archive_pages as ar

MODULES=json.loads((model.ROOT/'content/editorial/modules.json').read_text())
HUBS={
 '/zones/games/':('games','games','GAME ON','THE 90s GAME ERA','16-bit adventures. 3D worlds. Arcade legends. Pick a platform, find a story, and make room for player two.','the-console-war-couch'),
 '/zones/music/':('music','music','TURN IT UP','THE DECADE ON REPEAT','Mixtapes. Big hooks. No skips. Follow the sounds, scenes, and little silver discs that went everywhere with us.','from-mixtape-to-file'),
 '/zones/tv-movies/':('movies-tv','movies','PRESS PLAY','ONE MORE MOVIE NIGHT','Video-store Fridays. Saturday cartoons. Summers at the multiplex. Settle in—the previews are almost over.','friday-at-the-video-store'),
 '/zones/tech-toys/':('tech','tech','YOU’RE ONLINE','THE FUTURE CAME HOME','The family computer. The dial-up handshake. A whole world on the other side of a very small screen.','the-family-computer'),
 '/zones/culture/':('culture','culture','AS IF!','A DECADE OF EVERYDAY ICONS','Meet at the mall. Pick a screen name. Feed the tiny pet. The objects were ordinary; the memories still aren’t.','meet-me-at-the-mall')}
TOPICS={
 'music':[('All stories','all'),('Grunge & rock','grunge'),('Hip-hop & R&B','hip-hop'),('Teen pop','teen-pop'),('Rave & electronic','rave'),('Mixtapes & MP3','mixtapes'),('CD listening','cd')],
 'movies-tv':[('All stories','all'),('At the movies','film'),('Television','tv'),('Animation','animation'),('Blockbusters','blockbusters'),('Horror','horror'),('VHS nights','vhs')],
 'tech':[('All stories','all'),('Family PC','pc'),('Software','software'),('Going online','online'),('Browsers','browsers'),('Pocket tech','portable'),('Design','design')],
 'culture':[('All stories','all'),('Mall life','mall'),('Fashion','fashion'),('Catalogs','catalogs'),('Toys & collecting','toys'),('Sports','sports'),('Online identity','online')]}
GENRES=[('All games','all'),('Platformers','platformers'),('RPGs','rpg'),('Racing','racing'),('Shooters','shooters'),('Fighting','fighting'),('Action','action')]
PLATFORMS=[('All platforms','all'),('Consoles','consoles'),('PC','pc'),('Arcade','arcade'),('Handhelds','handhelds')]


def hero(art,title,subtitle,summary,href='#section-stories',cta='Explore the stories'):
 return f'<section class="ed-hero hub-hero hub-hero-{art}">{ed.media(art,hero=True)}<div class="ed-hero-copy"><h1>{title}</h1><h2>{ed.esc(subtitle)}</h2><p>{ed.esc(summary)}</p><a class="ed-cta" href="{href}">{ed.esc(cta)} {ed.icon("arrow")}</a></div></section>'


def rail(items,key,anchor,label):
 return f'<nav class="ed-topic-rail hub-rail" aria-label="{label}">'+''.join(f'<a href="?{key}={value}#{anchor}" data-hub-filter="{key}" data-value="{value}"'+(' aria-current="true"' if value=='all' else '')+f'>{ed.esc(title)}</a>' for title,value in items)+'</nav>'


def story(id):return next(s for s in model.STORIES if s['id']==id)
def story_tile(s):return ed.tile(s['title'],model.story_url(s),s['art'],s['summary'],'STORY')
def panel(title,body,glyph='star',href=None):return f'<section class="ed-panel hub-panel">{ed.heading(title,glyph,href)}{body}</section>'


def chart(category):
 ch=MODULES['charts'][category]
 rows=''.join(f'<li><span class="hub-rank-number">{i+1}</span><span><strong>{ed.esc(t)}</strong><small>{ed.esc(sub)}</small></span></li>' for i,(t,sub) in enumerate(ch['rows']))
 return panel(ch['title'],f'<p class="hub-period">{ed.esc(ch["period"])}</p><ol class="hub-chart">{rows}</ol><p class="hub-source"><a href="{ed.esc(ch["sourceUrl"])}">{ed.esc(ch["sourceLabel"])} ↗</a></p><p class="hub-footnote">{ed.esc(ch["note"])}</p>','trophy')


def object_tile(id,title=None):
 a=ed.ARTIFACTS[id]
 return ed.tile(title or a['title'],model.object_url(a),id,a['label'])


def hub(route):
 cat,art,title,subtitle,summary,feature=HUBS[route['path']]
 stories=[s for s in model.STORIES if s['category']==cat]
 top=hero(art,title,subtitle,summary, '#game-archive' if cat=='games' else '#section-stories', 'Explore the era' if cat=='games' else 'Explore the stories')
 top+=rail(GENRES,'genre','game-archive','Game genres') if cat=='games' else rail(TOPICS[cat],'topic','section-stories',model.CATEGORIES[cat]+' topics')
 feature_panel=panel('Featured story',story_tile(story(feature)))
 events=[e for e in model.EVENTS if e['category']==cat]
 if cat in MODULES['charts']:middle=chart(cat)
 else:
  picks=[s for s in stories if s['id']!=feature][:5]
  links=''.join(f'<a class="hub-spotlight" href="{model.story_url(s)}"><span>{ed.icon("arrow")}</span><span><strong>{ed.esc(s["title"])}</strong><small>{ed.esc(s["summary"])}</small></span></a>' for s in picks)
  middle=panel({'games':'Five ways into the era','tech':'The next big thing','culture':'Everyday touchstones'}[cat],links,'bolt')
 objects={'games':['playstation-hardware','family-pc','arcade-cabinet','game-boy-color'],'music':['cassette','discman','cdr-spindle','crt-television'],'movies-tv':['blockbuster-store','vhs-tape','crt-television','cdr-spindle'],'tech':['family-pc','pager','windows-95-start','bondi-imac'],'culture':['game-boy-color','cassette','pager','crt-television']}[cat]
 if cat=='games':
  browse=''.join(ed.tile(t,f'?platform={v}#game-archive',a,sub) for t,v,a,sub in [('Console games','consoles','playstation-hardware','From cartridges to discs.'),('PC games','pc','family-pc','The desk becomes an arena.'),('Arcade games','arcade','arcade-cabinet','Quarter up. You’re next.'),('Handheld games','handhelds','game-boy-color','A world in your pocket.')])
 else: browse=''.join(object_tile(id) for id in objects)
 browse_panel=panel('Browse by platform' if cat=='games' else 'From the collection','<div class="ed-two-up hub-objects">'+browse+'</div>','folder')
 facts=f'<a href="#section-stories"><strong>{len(stories):02}</strong><span>Complete stories<br /><small>Objects, scenes & everyday rituals</small></span></a><a href="/search/?filter=events&amp;q={cat}"><strong>{len(events)}</strong><span>Dated entries<br /><small>Regional notes & source links</small></span></a><a href="/timeline/"><strong>10</strong><span>Years to explore<br /><small>1990 through 1999</small></span></a><a href="/credits/"><strong>↗</strong><span>Know the source<br /><small>Photo credits & original art</small></span></a>'
 top+=f'<div class="hub-lead-grid">{feature_panel}{middle}{browse_panel}{panel("At a glance",f"<div class=hub-facts>{facts}</div>","bolt")}</div>'
 top+=f'<section id="section-stories" class="hub-section" data-hub-collection="stories">{ed.heading("Deep dives","book","/stories/")}<p class="hub-status ar-js-only" data-hub-status="stories" role="status">{len(stories)} stories</p><div class="hub-story-grid">'+''.join(f'<div data-hub-story data-topics="{ed.esc(" ".join(s.get("topics",[])))}">{story_tile(s)}</div>' for s in stories)+'</div><p class="ar-empty" data-hub-empty="stories" hidden>No stories match this topic. <a href="?topic=all#section-stories">Show all stories →</a></p></section>'
 if cat=='games':top+=game_archive()
 elif cat=='music':
  scenes=[('Grunge: the breakthrough','when-grunge-broke-through','music'),('Hip-hop & R&B: the crossover','hooks-rhymes-and-radio','cassette'),('Teen pop: the afternoon audience','after-school-on-trl','crt-television'),('Rave: the room and the record','the-flyer-and-the-dancefloor','music')]
  top+=panel('Artists & scenes','<div class="hub-four-up">'+''.join(ed.tile(t,model.story_url(story(s)),a) for t,s,a in scenes)+'</div>','music')
 elif cat=='movies-tv':
  top+=panel('Television & home viewing','<div class="ed-three-up">'+''.join(story_tile(story(id)) for id in ['the-cartoon-morning','same-time-next-week','do-not-tape-over'])+'</div>','movies')
 if events:
  # Distinct genres and years take precedence over an arbitrary recency ranking.
  picks=events[:3]+events[-3:] if len(events)>6 else events
  if cat=='culture':
   featured_ids=['mall-of-america-opens','elvis-stamp-issued','tamagotchi-japan','wnba-first-game','lion-king-broadway','orange-bowl-new-years-eve']
   picks=[next(e for e in events if e['id']==id) for id in featured_ids]
  top+=f'<section class="hub-section">{ed.heading("On the release calendar" if cat in ("music","movies-tv") else "Moments on the timeline","calendar",f"/search/?filter=events&amp;q={cat}")}<div class="hub-event-grid">'+''.join(ar.event_card(e) for e in picks)+'</div></section>'
 if cat in ('tech','culture'):
  links=[('The old web','/zones/internet-culture/','culture','Personal pages, handles & guestbooks.'),('The fashion file','/zones/fashion/','culture','Clothes, references & self-expression.'),('Transparent tech','/zones/transparent-tech/','tech','The future had a translucent shell.')]
  top+=panel('Keep going: specialist collections','<div class="ed-three-up">'+''.join(ed.tile(t,h,a,sub) for t,h,a,sub in links)+'</div>','folder')
 if route['path'] in ed.CORE:top+=ed.discovery()
 if route['path'] in model.PAGES:top+=ed.preserved_content(route)
 return f'<main id="main-content" class="ed-main hub-main" data-hub="{cat}">{top}</main>'


def game_archive():
 rows=[]
 for g in MODULES['games']:
  rows.append(f'<article class="hub-game" data-hub-game data-genre="{g["genre"]}" data-platform="{g["platform"]}"><div class="hub-game-art">{ed.media(g["art"])}</div><div class="hub-game-copy"><p class="ar-meta">{ed.esc(g["platform"])} · {ed.esc(g["genre"])}</p><h3>{ed.esc(g["title"])}</h3><p>{ed.esc(g["summary"])}</p><div><a href="{model.story_url(story(g["storyId"]))}">Read the related story →</a><a href="{ed.esc(g["sourceUrl"])}">{ed.esc(g["sourceLabel"])} ↗</a></div></div></article>')
 return f'<section id="game-archive" class="hub-section">{ed.heading("The game shelf","games")}<p class="hub-intro">Twelve editorial picks. Filter by genre and platform; each entry connects to a story and a publisher or museum record. Hardware photographs illustrate the platform, not game screenshots.</p>{rail(PLATFORMS,"platform","game-archive","Game platforms")}<p class="hub-status ar-js-only" data-hub-status="games" role="status"></p><div class="hub-game-grid">'+''.join(rows)+'</div><p class="ar-empty" data-hub-empty="games" hidden>No games match this combination. <a href="?genre=all&amp;platform=all#game-archive">Reset game filters →</a></p></section>'


def timeline_index(route):
 top=hero('timeline','THE WHOLE<br />DECADE','TEN YEARS. COUNTLESS STORIES.','Choose a year. Jump into a month. Follow the dates that connect a decade of music, movies, games, and change.','#decade-years','Pick your year')
 captions=['A new decade boots up.','New sounds break through.','The desktop opens new windows.','The Web becomes everybody’s idea.','A console waits in the wings.','A Start button and a new dimension.','The middle of everything.','Big worlds on small discs.','The future turns translucent.','One last year before the clock rolls over.']
 cards=[]
 for y in range(1990,2000):
  count=sum(e['date'].startswith(str(y)) for e in model.EVENTS)
  cards.append(f'<a href="/timeline/{y}/" class="hub-year"><span>{y}</span><strong>{captions[y-1990]}</strong><small>{count} sourced entries · 12 months</small></a>')
 top+=f'<section class="hub-section" id="decade-years">{ed.heading("Choose a year","calendar")}<div class="hub-year-grid">'+''.join(cards)+f'</div></section><div class="hub-timeline-bottom">{panel("This week, 30 years ago",ed.tile("Same decade. Different day.","/this-week/","home","Browse a historical Monday–Sunday week."),"calendar")}{panel("Behind the dates","<div class=ed-three-up>"+"".join(story_tile(story(id)) for id in ["from-mixtape-to-file","a-whole-new-dimension","choosing-your-screen-name"])+"</div>","book","/stories/")}</div>'+ed.preserved_content(route)
 return f'<main id="main-content" class="ed-main hub-main">{top}</main>'
