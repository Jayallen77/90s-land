"""Small original worked examples with readable, disabled static fallbacks."""
IDS={'mp3-budget','keypad'}

def render(id):
    if id not in IDS:raise ValueError('Unknown reading tool: '+id)
    if id=='mp3-budget':
        controls='''<label>Storage (decimal MB)<input name="capacity" type="number" min="1" max="512" step="1" value="32" disabled /></label><label>Constant bitrate<select name="bitrate" disabled><option value="64">64 kbps</option><option value="96">96 kbps</option><option value="128" selected>128 kbps</option><option value="192">192 kbps</option><option value="256">256 kbps</option></select></label><label>Track length (minutes)<input name="minutes" type="number" min="1" max="12" step="0.5" value="4" disabled /></label>'''
        title='Try the storage budget'
        result='At 128 kbps, 32 MB holds at most 33:20 of audio payload: 8 whole four-minute tracks. Each track needs 3.84 MB.'
        note='Original arithmetic model. Decimal MB, constant bitrate, no file headers or device overhead. Lower bitrates change the quality tradeoff; this does not emulate a Rio player.'
    else:
        controls='''<label>Word to compare (A–Z)<input name="word" type="text" value="HELLO" maxlength="24" pattern="[A-Za-z]+" autocomplete="off" autocapitalize="characters" spellcheck="false" disabled /></label>'''
        title='Try the letter keys'
        result='HELLO: traditional 44 · 33 · 555 · 555 · 666 — 13 letter presses. Predictive letter keys 43556 — 5 presses.'
        note='Original key-mapping demonstration, not Nokia or T9 software. Counts letters only, excluding pauses, cursor movement, suggestions and confirmation. GOOD, HOME, HOOD and GONE all map to 4663.'
    return f'''<section class="reading-tool" data-reading-tool="{id}" aria-label="{title}"><form><fieldset><legend>{title}</legend><div class="reading-tool-controls">{controls}</div></fieldset></form><p class="reading-tool-result" role="status" aria-live="polite" aria-atomic="true" data-reading-result>{result}</p><p class="reading-tool-note">{note}</p><noscript><p>Enable JavaScript to change the example. The calculation above is available without it.</p></noscript></section>'''
