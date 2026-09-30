"""Complete archive compositions built from the reviewed source catalog."""
from __future__ import annotations
import calendar
import json
from datetime import date, timedelta
import editorial as ed
import archive_content as model

esc = ed.esc
CAT = model.CATEGORIES


def stamp(value):
    return date.fromisoformat(value).strftime('%b %-d, %Y')


def art(key, label='90s archive'):
    if key in model.HEROES: return ed.graphic(label, 'FROM THE COLLECTION')
    if key:
        item = ed.ARTIFACTS.get(key)
        if not item or item['media']['kind'] == 'image': return ed.media(key)
    return ed.graphic(label, 'FROM THE COLLECTION', 'calendar')


def event_card(e):
    return f'''<article class="ar-event" data-event data-category="{e['category']}" data-region="{esc(e['region'])}" data-date="{e['date']}"><a href="{model.event_url(e)}"><div class="ar-card-art">{art(e['art'], e['title'])}</div><div class="ar-card-copy"><p class="ar-meta"><time datetime="{e['date']}">{stamp(e['date'])}</time> · {esc(e['region'])}</p><h3>{esc(e['title'])}</h3><p>{esc(e['summary'])}</p><span class="ed-badge">{model.event_label(e)}</span></div></a></article>'''


def story_card(s):
    return f'<a class="ar-story-card" href="{model.story_url(s)}"><div class="ar-card-art">{art(s["art"], s["title"])}</div><div class="ar-card-copy"><span class="ed-badge">{CAT[s["category"]]} · STORY</span><h3>{esc(s["title"])}</h3><p>{esc(s["summary"])}</p></div></a>'


def heading(kicker, title, summary):
    return f'<header class="ar-heading"><p class="ar-kicker">{esc(kicker)}</p><h1>{esc(title)}</h1><p>{esc(summary)}</p></header>'


def decade(year):
    return '<nav class="ed-decade" aria-label="Explore the decade"><strong>EXPLORE THE DECADE</strong>'+''.join(f'<a href="/timeline/{y}/"'+(' aria-current="page"' if y==year else '')+f'>{y}</a>' for y in range(1990,2000))+'</nav>'


def year_highlights(year):
    picks=model.defining_events(year)
    cards=''.join(f'<li><a class="ar-related ed-moment" data-defining-event="{e["id"]}" href="{model.event_url(e)}"><span class="ar-meta"><time datetime="{e["date"]}">{stamp(e["date"])}</time> · {model.event_label(e)}</span><h3>{esc(e["title"])}</h3><p>{esc(e["summary"])}</p></a></li>' for e in picks)
    title=ed.heading(f'{len(picks)} defining moments','bolt').replace('<h2>','<h2 id="defining-title">')
    return f'<section class="hub-section" id="defining-moments" aria-labelledby="defining-title">{title}<p class="hub-intro">Start here for a taste of {year}, then follow any date into its sources and connections.</p><ol class="ed-moments">{cards}</ol></section>'


def year_connections(year):
    picks=[next(s for s in model.STORIES if s['id']==id) for id in model.YEARS[year]['storyIds']]
    cards=''.join(f'<div><p class="ar-kicker">{CAT[s["category"]]}</p>{story_card(s)}</div>' for s in picks)
    return f'<section class="hub-section" id="year-stories">{ed.heading("Life around the dates","book","/stories/")}<p class="hub-intro">Albums on the shelf, evenings around the screen, and the everyday things between the headlines.</p><div class="ed-year-stories">{cards}</div></section><nav class="ed-year-links" aria-label="Related collections"><strong>FOLLOW A COLLECTION</strong><a href="/zones/music/">Music</a><a href="/zones/tv-movies/">Movies & TV</a><a href="/zones/games/">Games</a><a href="/zones/tech-toys/">Tech</a><a href="/zones/culture/">Culture</a><a href="/zones/fashion/">Fashion</a><a href="/zones/internet-culture/">Internet Culture</a></nav>'


def calendar_table(year, month, events):
    rows = []
    for week in calendar.Calendar(firstweekday=0).monthdayscalendar(year, month):
        cells = []
        for day in week:
            if not day:
                cells.append('<td class="ar-outside"></td>'); continue
            iso = date(year,month,day).isoformat()
            links = ''.join(f'<a data-event data-category="{e["category"]}" data-region="{esc(e["region"])}" href="{model.event_url(e)}" aria-label="{esc(e["title"])} · {esc(e["region"])} · {stamp(e["date"])}"><span>{esc(e["title"])}</span><small>{esc(e["region"])}</small><b class="ar-calendar-mobile" aria-hidden="true">{CAT[e["category"]].split()[0]}</b></a>' for e in events if e['date']==iso)
            cells.append(f'<td><time datetime="{iso}">{day}</time>{links}</td>')
        rows.append('<tr>'+''.join(cells)+'</tr>')
    return f'<table class="ar-calendar"><caption>{calendar.month_name[month]} {year} · dated events</caption><thead><tr>'+''.join(f'<th scope="col"><abbr title="{name}">{name[:3]}</abbr></th>' for name in calendar.day_name)+'</tr></thead><tbody>'+''.join(rows)+'</tbody></table>'


def timeline(route):
    year = int(route['path'].strip('/').split('/')[-1])
    selected = date.fromisoformat(model.CATALOG['buildAsOf']).month
    year_events = [e for e in model.EVENTS if e['date'].startswith(str(year))]
    capsule=model.YEARS[year]
    hero = ed.hero('timeline') if year==1996 else heading('THE DECADE, DAY BY DAY',str(year),capsule['caption'])
    intro=f'<div class="ed-year-intro"><p>{esc(capsule["intro"])}</p><nav aria-label="Inside this year"><a href="#defining-moments">Defining moments ↓</a><a href="#chronology">Full calendar ↓</a><a href="#year-objects">Objects ↓</a><a href="#year-stories">Stories ↓</a></nav></div>'
    rail = '<nav class="ed-month-rail" aria-label="Browse months">'+''.join(f'<a data-month="{m}" href="?month={m:02}#events-{year}-{m:02}">{calendar.month_abbr[m].upper()}</a>' for m in range(1,13))+'</nav>'
    regions = sorted({e['region'] for e in model.EVENTS})
    options = lambda values: ''.join(f'<option value="{esc(k)}">{esc(v)}</option>' for k,v in values)
    controls = f'''<div class="ar-controls ar-js-only"><label>Category<select data-category-filter><option value="all">All categories</option>{options(CAT.items())}</select></label><label>Region<select data-region-filter><option value="all">All regions</option>{options((r,r) for r in regions)}</select></label><div class="ed-view-switch" role="group" aria-label="Events display style">{''.join(f'<button type="button" data-archive-view="{v}" aria-pressed="{str(v=="grid").lower()}">{v.title()}</button>' for v in ('grid','list','calendar'))}</div></div>'''
    months = []
    for month in range(1,13):
        events = [e for e in year_events if int(e['date'][5:7]) == month]
        months.append(f'''<section class="ar-month" data-month-panel="{month}" id="events-{year}-{month:02}"><div class="ar-month-title"><h2>{ed.icon('calendar')} {calendar.month_name[month].upper()} {year}</h2></div><div class="ar-event-grid">{''.join(event_card(e) for e in events)}</div>{calendar_table(year,month,events)}<h3 class="ar-mobile-agenda">Dates this month</h3><p class="ar-empty" data-month-empty{'' if not events else ' hidden'}>No events match these filters. Try another category, region, or month.</p></section>''')
    aside = f'''<aside class="ar-sidebar"><section class="ed-panel ar-panel">{ed.heading('In the archive','bolt')}<p class="ar-large-number">{len(year_events)}</p><p>Sourced, day-specific entries for {year}.</p><p class="ar-muted">{esc(model.CATALOG['coverageNote'])}</p><a class="ed-text-link" href="/this-week/">THIS WEEK, 30 YEARS AGO →</a></section><section class="ed-panel ar-panel"><h2>Know the date</h2><p>A US opening, a Japanese game launch, and a worldwide broadcast can fall on different calendars. Each entry keeps its region and source note.</p><a href="/search/?q={year}&amp;filter=events">Search the year →</a></section></aside>'''
    content = hero+intro+year_highlights(year)+f'<section class="hub-section" id="chronology">{ed.heading("The full calendar","calendar")}{rail}<div class="ar-layout"><section data-timeline data-year="{year}" data-default-month="{selected}" data-view="grid">{controls}<div class="ar-paging ar-js-only"><a data-prev-month href="?month={max(1,selected-1):02}">← Previous month</a><p data-timeline-status role="status"></p><a data-next-month href="?month={min(12,selected+1):02}">Next month →</a></div>'+''.join(months)+f'<nav class="ar-paging ar-js-only" aria-label="Event pages" data-event-paging hidden><button type="button" data-event-prev>← Previous</button><span data-event-page></span><button type="button" data-event-next>Next →</button></nav><p class="ar-muted">Dates are regional where labeled. Images illustrate the era; source notes appear on each event.</p></section>{aside}</div></section><div id="year-objects"><!-- object-shelf --></div>'+year_connections(year)+decade(year)
    return f'<main id="main-content" class="ed-main ar-main">{content}</main>'


def week_days(start, events):
    result = []
    for i in range(7):
        day = start+timedelta(days=i)
        items = [e for e in events if e['date'] == day.isoformat()]
        links = ''.join(f'<a class="ar-week-event" href="{model.event_url(e)}"><span class="ar-meta">{CAT[e["category"]]} · {esc(e["region"])}</span><h3>{esc(e["title"])}</h3><p>{esc(e["summary"])}</p></a>' for e in items)
        result.append(f'<section class="ar-day{' ar-day-empty' if not items else ''}"><h2><time datetime="{day.isoformat()}"><span>{day.strftime("%a")}</span>{day.day}</time></h2><div>{links or "<p class=\"ar-muted\">No entries for this day.</p>"}</div></section>')
    return ''.join(result)


def weekly():
    day = model.historical_date(date.fromisoformat(model.CATALOG['buildAsOf']))
    start, end = model.week_bounds(day)
    range_label = f'{stamp(start.isoformat())} – {stamp(end.isoformat())}'
    in_week = [e for e in model.EVENTS if start.isoformat() <= e['date'] <= end.isoformat()]
    picks = model.selected_events(in_week, movie_limit=2)
    return f'''<main id="main-content" class="ed-main ar-main" data-weekly><header class="ar-week-hero"><p class="ar-kicker">SAME DECADE. DIFFERENT DAY.</p><h1>This week in <span data-week-year>{day.year}</span></h1><p class="ar-week-range" data-week-range>{range_label}</p><p>Releases, milestones, and little time machines. One historical week at a time.</p></header><div class="ar-controls ar-js-only"><button type="button" data-week-prev>← Previous week</button><label>Pick a date<input type="date" data-week-date min="1990-01-01" max="1999-12-31" value="{day.isoformat()}" /></label><label>Year<select data-week-select>{''.join(f'<option{(" selected" if y==day.year else "")}>{y}</option>' for y in range(1990,2000))}</select></label><button type="button" data-week-next>Next week →</button><button type="button" data-week-today>30 years ago</button></div><p class="ar-muted" data-week-explainer>Monday–Sunday, containing the date 30 years before today in America/New_York.</p><p class="ar-nojs-only">Saved week for {model.CATALOG['buildAsOf']}. Enable JavaScript to change weeks, or <a href="/timeline/">browse every year and month</a>.</p><div class="ar-layout"><section><section data-week-highlights{'' if picks else ' hidden'}><h2 class="ar-section-title">A FEW MOMENTS TO START WITH</h2><div class="ar-week-lead" data-week-lead>{event_card(picks[0]).replace("<h3>","<h2>").replace("</h3>","</h2>") if picks else ""}</div><div class="ar-week-picks" data-week-picks>{"".join(event_card(e) for e in picks[1:])}</div></section><h2 class="ar-section-title">ON THE CALENDAR <span role="status" data-week-count>{len(in_week)} sourced {"entry" if len(in_week)==1 else "entries"}</span></h2><div data-week-days>{week_days(start, in_week)}</div><p class="ar-empty" data-week-empty{'' if not in_week else ' hidden'}>No events in the archive for this week. Explore nearby dates below or browse the month.</p><a class="ed-text-link" data-week-month href="/timeline/{day.year}/?month={day.month:02}#events-{day.year}-{day.month:02}">OPEN THE MONTH →</a><section data-week-nearby hidden><h2 class="ar-section-title">NEARBY DATES</h2><p class="ar-muted">Outside the selected week.</p><div data-nearby-events></div></section></section><aside class="ar-sidebar"><section class="ed-panel ar-panel">{ed.heading('Stories from the decade','book')}{''.join(story_card(s) for s in related_stories(in_week)[:3])}</section><section class="ed-panel ar-panel"><h2>Follow your curiosity</h2><nav class="ar-detail-links" data-week-connections aria-label="Explore this week’s year and collections"><a href="/timeline/{day.year}/">Explore {day.year} →</a></nav><p>Browse the objects behind the dates, from familiar hardware to handmade interfaces.</p><a href="/archive/objects/">Explore the object collection →</a></section></aside></div></main>'''


def sources(ids):
    rows = ''.join(f'<li><a href="{esc(model.SOURCES[id]["url"])}">{esc(model.SOURCES[id]["publisher"])} — {esc(model.SOURCES[id]["title"])} ↗</a><p>{esc(model.SOURCES[id]["scope"])}</p><small>Checked {model.SOURCES[id]["checkedAt"]}</small></li>' for id in ids)
    return f'<section class="ar-sources" id="sources"><h2>Sources & date notes</h2><ol>{rows}</ol></section>'


def related(objects, events=(), stories=()):
    selected = [next(a for a in model.ARTIFACTS if a['id']==id) for id in objects][:3]
    event_picks=model.selected_events([e for e in model.EVENTS if e['id'] in events],3)
    story_picks=[s for s in model.STORIES if s['id'] in stories][:2]
    if not (selected or events or stories): return '<aside class="ar-sidebar"><section class="ed-panel ar-panel"><h2>Keep exploring</h2><a href="/timeline/">Browse the decade →</a><p><a href="/stories/">Read the stories →</a></p></section></aside>'
    return '<aside class="ar-sidebar"><section class="ed-panel ar-panel"><h2>Keep exploring</h2>'+''.join(story_card(s) for s in story_picks)+''.join(f'<a class="ar-related" href="{model.object_url(a)}"><span class="ar-meta">OBJECT · {esc(a["dateRange"]["label"])}</span><h3>{esc(a["title"])}</h3></a>' for a in selected)+''.join(f'<a class="ar-related" href="{model.event_url(e)}"><span class="ar-meta">{stamp(e["date"])} · {model.event_label(e)}</span><h3>{esc(e["title"])}</h3></a>' for e in event_picks)+'</section></aside>'


def collection_path(category):
    return ed.SECTION_ROUTES.get(category,('Timeline','/timeline/'))


def contextual_path(category, objects=(), year=None):
    label,href=collection_path(category)
    links=f'<a href="{href}">Explore {label} →</a>'
    if year:links+=f'<a href="/timeline/{year}/#defining-moments">{year}: the defining moments →</a>'
    tours=json.loads((model.ROOT/'data/tours.json').read_text())
    stop=next((s for t in tours for s in t['stops'] if set(s['artifactIds']) & set(objects)),None)
    if stop:links+=f'<a href="/tours/before-the-feed/#{stop["id"]}">Before the Feed: {esc(stop["title"])} →</a>'
    return f'<nav class="ar-detail-links ed-context-path" aria-label="Continue this story">{links}</nav>'


def structured(route, kind, published=None):
    item = {'@context':'https://schema.org','@type':kind,'headline':route['title'],'description':route['summary'],'url':'https://90s.land'+route['path']}
    if published: item['datePublished']=published
    # The historical date belongs to the subject, never to publication metadata.
    return '<script type="application/ld+json">'+json.dumps(item,ensure_ascii=False).replace('<','\\u003c')+'</script>'


def detail(route, render_media):
    type = route['type']
    if type == 'events':
        e = next(e for e in model.EVENTS if model.event_url(e)==route['path'])
        body = heading(f'{model.event_label(e)} · {e["region"]}',e['title'],e['summary'])
        body += f'<p class="ar-detail-date"><time datetime="{e["date"]}">{stamp(e["date"])}</time> · {esc(e["region"])}</p>'
        body += ''.join(f'<p>{esc(p)}</p>' for p in e['paragraphs'])+f'<p class="ar-date-note"><strong>About this date:</strong> {esc(e["dateNote"])}</p>'
        body += f'<div class="ar-detail-art">{art(e["art"],stamp(e["date"]))}</div><p class="ar-muted">Illustrative archive imagery. See related objects for image credits; <a href="/credits/">original collage artwork credits</a>.</p>'
        body += f'<div class="ar-detail-links"><a href="/timeline/{e["date"][:4]}/?month={e["date"][5:7]}#events-{e["date"][:7]}">View the month →</a><a href="/this-week/?date={e["date"]}">View this historical week →</a></div>'+sources(e['sourceIds'])
        body+=contextual_path(e['category'],e['objectIds'],e['date'][:4])
        return wrap_detail(route,body,related(e['objectIds'],stories=e['storyIds']))
    if type == 'stories':
        s = next(s for s in model.STORIES if model.story_url(s)==route['path'])
        body = heading(CAT[s['category']]+' · FROM THE ARCHIVE',s['title'],s['summary'])
        body += f'<div class="ar-detail-art">{art(s["art"], s["title"])}</div>'
        body += ''.join(f'<section><h2>{esc(section["heading"])}</h2>'+''.join(f'<p>{esc(p)}</p>' for p in section['paragraphs'])+'</section>' for section in s['sections'])
        body += sources(s['sourceIds'])+'<p class="ar-muted">Original editorial interpretation by 90s.land. Images are illustrative; <a href="/credits/">artwork credits</a> and related object labels identify their sources.</p>'
        body+=contextual_path(s['category'],s['objectIds'])
        return wrap_detail(route,body,related(s['objectIds'],s['eventIds']),s['publishedAt'])
    a = next(a for a in model.ARTIFACTS if model.object_url(a)==route['path'])
    m = a['media']
    credit = f'<a href="{esc(m["sourceUrl"])}">{esc(m["credit"])} ↗</a>' if m.get('sourceUrl') else esc(m['credit'])
    license_label = f'<a href="{esc(m["licenseUrl"])}">{esc(m["license"])}</a>' if m.get('licenseUrl') else esc(m['license'])
    body = heading('OBJECT FILE · '+a['dateRange']['label'],a['title'],a['curatorNote'])
    body += f'<figure class="ar-object-art">{render_media(a)}<figcaption>{credit} · {license_label}</figcaption></figure><h2>The object’s story</h2><p>{esc(a["whyItMattered"])}</p>'
    if m['kind']=='recreation': body += '<p class="ar-date-note">Original interface recreation. This is an interpretation of the era, not an archived live website.</p>'
    body += f'<div class="ar-detail-links"><button type="button" class="button ar-js-only" data-artifact-inspect="{a["id"]}">Inspect + stamp</button><a href="{esc(a["target"])}">Explore this collection →</a></div><h2>Across the decade</h2><p>'+ ' · '.join(f'<a href="/timeline/{y}/">{y}</a>' for y in a['relatedYears'])+'</p>'
    events = [e['id'] for e in model.EVENTS if a['id'] in e['objectIds']]
    stories = [s['id'] for s in model.STORIES if a['id'] in s['objectIds']]
    others = a['relatedArtifacts'] or [o['id'] for o in model.ARTIFACTS if o['room']==a['room'] and o['id']!=a['id']][:3]
    room_category={'tv-movies':'movies-tv','tech-toys':'tech','transparent-tech':'tech','internet-culture':'tech'}.get(a['room'],a['room'])
    body+=contextual_path(room_category,[a['id']])
    if len(events)>3:body+=f'<p><a href="/search/?q={a["slug"]}&amp;filter=events">More dates connected to this object →</a></p>'
    return wrap_detail(route,body,related(others,events,stories))


def wrap_detail(route, body, aside, published=None):
    return f'<main id="main-content" class="ed-main ar-main"><div class="ar-layout"><article class="ar-article">{body}</article>{aside}</div></main>'+structured(route,'Article' if route['type']=='stories' else 'WebPage',published)


def archive_index(route, render_media):
    if route['path']=='/events/':
        filters = '<nav class="hub-library-filters" aria-label="Event categories">'+''.join(f'<a data-hub-filter="category" data-value="{key}" href="?category={key}#event-library">{esc(label)}</a>' for key,label in [('all','All events')]+list(CAT.items()))+'</nav>'
        content = '<div data-hub="events" id="event-library">'+filters+'<h2 class="ar-section-title">Dated releases & milestones</h2>'+ '<p class="hub-status" data-hub-status="events" role="status"></p><div class="ar-index-grid" data-event-library>'+''.join(f'<div data-hub-event data-category="{e["category"]}">{event_card(e)}</div>' for e in model.EVENTS)+'</div></div>'
    elif route['path']=='/stories/':
        filters = '<nav class="hub-library-filters" aria-label="Story categories">'+''.join(f'<a data-hub-filter="category" data-value="{key}" href="?category={key}#story-library">{esc(label)}</a>' for key,label in [('all','All stories')]+[(k,v) for k,v in CAT.items() if k!='news'])+'</nav>'
        content = '<div data-hub="library" id="story-library">'+filters+'<h2 class="ar-section-title">STORIES TO GET LOST IN</h2><p class="hub-status ar-js-only" data-hub-status="stories" role="status"></p><div class="ar-index-grid">'+''.join(f'<div data-hub-story data-category="{s["category"]}" data-topics="">{story_card(s)}</div>' for s in model.STORIES)+'</div></div>'
    else:
        content = '<div class="ar-index-grid">'+''.join(f'<a class="ar-story-card" href="{model.object_url(a)}"><div class="ar-card-art">{render_media(a)}</div><div class="ar-card-copy"><span class="ar-meta">{esc(a["dateRange"]["label"])}</span><h2>{esc(a["title"])}</h2><p>{esc(a["curatorNote"])}</p></div></a>' for a in model.ARTIFACTS)+'</div>'
    return '<main id="main-content" class="ed-main ar-main">'+heading('THE COLLECTION',route['title'],route['summary'])+content+'</main>'


def related_stories(events):
    ids = {id for e in events for id in e['storyIds']}
    return [s for s in model.STORIES if s['id'] in ids]
