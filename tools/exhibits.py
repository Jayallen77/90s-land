"""Original, deliberately invented interface exhibits. No network or visitor data."""
from html import escape

IDS={'geocities-homepage','visitor-counter','guestbook','webring-bar','aim-away-message','yahoo-directory'}

def render(id, interactive=False):
    if id not in IDS:raise ValueError('Unknown web exhibit: '+id)
    controls=''
    if id=='geocities-homepage':
        body='''<div class="homepage-preview" data-homepage-preview><p class="web-window">home.html — my corner of the web</p><p class="web-title homepage-title">WELCOME TO THE MIX TAPE PLANET</p><p>A made-up fan page about music, games, and things worth bookmarking.</p><div class="web-columns"><div><strong>Currently playing</strong><p>A tape with a handwritten label.</p></div><div><strong>Favorite corners</strong><p>Game notes · Record shelf · Cool links</p></div></div><p class="homepage-under-construction" hidden data-builder-layer="construction">UNDER CONSTRUCTION — probably forever</p><p class="homepage-counter" hidden data-builder-layer="counter">visitor no. 000247</p></div>'''
        if interactive:
            body=body.replace('<p>Game notes · Record shelf · Cool links</p>','<ul><li><a href="/stories/the-demo-disc-evening/">Game notes</a></li><li><a href="/stories/bristol-between-the-beats/">Record shelf</a></li><li><a href="/webring/">Cool links</a></li></ul>')
            controls='''<div class="builder-controls ar-js-only" aria-label="Homepage recreation controls"><button type="button" aria-pressed="false" data-homepage-toggle="stars">Add tiled stars</button><button type="button" aria-pressed="false" data-homepage-toggle="construction">Add construction badge</button><button type="button" aria-pressed="false" data-homepage-toggle="counter">Add visitor counter</button><button type="button" data-homepage-reset>Reset page</button></div>'''
    elif id=='visitor-counter':
        body='<p class="web-window">You are visitor number</p><output class="web-counter" data-demo-count aria-live="polite">000247</output><p>A simulated counter, starting at an invented number.</p>'
        if interactive:controls='<div class="builder-controls ar-js-only"><button type="button" data-demo-visit>Preview another visit</button><button type="button" data-demo-reset>Reset counter</button></div>'
    elif id=='guestbook':
        body='''<p class="web-window">The guestbook — example entries</p><div class="web-entry"><strong>moon_radio</strong><small>Example · 1997</small><p>Found this through the music ring. Nice tape collection!</p></div><div class="web-entry"><strong>pixel_pilot</strong><small>Example · 1997</small><p>Bookmarked. Come visit my game page sometime.</p></div>'''
        if interactive:controls='''<form class="web-form ar-js-only" data-guestbook-form><p>Preview only. Nothing is sent or saved.</p><label>Your handle<input name="name" maxlength="24" required /></label><label>Your message<textarea name="message" maxlength="140" required></textarea></label><button type="submit" class="button">Preview my entry</button><div data-guestbook-preview hidden role="status"></div></form>'''
    elif id=='webring-bar':
        body='''<p class="web-window">The late-night bookmarks ring</p><p class="web-title" data-ring-title>Tape Deck Planet</p><p data-ring-copy>Handwritten track lists and one more song for side B.</p><p class="web-ring-strip">← PREVIOUS · RANDOM · NEXT →</p>'''
        if interactive:controls='''<div class="builder-controls ar-js-only"><button type="button" data-ring-step="-1">← Previous page</button><button type="button" data-ring-random>Random page</button><button type="button" data-ring-step="1">Next page →</button></div><p><a data-ring-open href="/stories/from-mixtape-to-file/">Explore the museum connection →</a></p><p>Three invented fan pages demonstrate the ring. The onward links open real museum stories.</p>'''
    elif id=='aim-away-message':
        body='''<p class="web-window">Buddy list — original interface recreation</p><div class="web-columns"><div><strong>Buddies (3)</strong><ul><li>● stargrrl97 — away</li><li>● pixel_pilot</li><li>○ moon_radio — offline</li></ul></div><div><strong>stargrrl97 is away</strong><p class="web-away" data-away-preview>Back after this CD finishes. Leave a message.</p></div></div>'''
        if interactive:controls='''<form class="web-form ar-js-only" data-away-form><label>Your away message<textarea name="away" maxlength="160" required>Back after this CD finishes. Leave a message.</textarea></label><button type="submit" class="button">Preview away message</button><p class="web-status" role="status" data-away-status></p></form>'''
    else:
        body='''<p class="web-window">The web, sorted by people</p><p class="web-title">Directory demonstration</p>'''
        for title,links in [('Music',[('Mixtapes','/stories/from-mixtape-to-file/'),('Bristol records','/stories/bristol-between-the-beats/')]),('Computers & Internet',[('Personal homepages','/stories/a-web-you-could-make/'),('Browsers','/stories/browser-wars-at-home/')]),('Games',[('Console games','/zones/games/'),('Portable play','/stories/handhelds-and-batteries/')])]:
            rows=''.join(f'<li>'+ (f'<a href="{url}">{escape(label)}</a>' if interactive else escape(label))+'</li>' for label,url in links)
            body+=(f'<details class="web-category"><summary>{escape(title)}</summary><ul>{rows}</ul></details>' if interactive else f'<div class="web-category"><strong>{escape(title)}</strong><ul>{rows}</ul></div>')
    # Async modules enable controls only after their event handlers are attached.
    if interactive:controls=controls.replace('<button ', '<button disabled data-exhibit-control ')
    if not interactive:body=body.replace(' data-homepage-preview','')
    attributes=' data-homepage-builder' if id=='geocities-homepage' and interactive else ''
    return f'<div class="web-exhibit web-{id}'+(' web-compact' if not interactive else '')+f'" data-web-exhibit="{id}"{attributes}><span class="web-demo-label">ORIGINAL RECREATION</span>{body}{controls}</div>'
