"""Fetch public reference text and Commons candidates for a reviewed editorial pass.

This is a research aid, not a publishing importer. Candidates require visual review.
"""
import concurrent.futures
import json
import re
import urllib.parse
import urllib.request
from pathlib import Path
from html.parser import HTMLParser

class Extract(HTMLParser):
    def __init__(self, raw):
        super().__init__(); self.parts=[]; self.headings=[]; self.links=[]; self.skip=0; self.heading=None; self.link=None; self.feed(raw)
    def handle_starttag(self, tag, attrs):
        attrs=dict(attrs)
        if tag in {'script','style','nav','header','footer'}: self.skip+=1
        if self.skip: return
        if tag in {'h1','h2','h3','h4','h5'}: self.heading=[]
        if tag=='a': self.link={'title':'','url':attrs.get('href','')}
    def handle_endtag(self, tag):
        if tag in {'script','style','nav','header','footer'}: self.skip=max(0,self.skip-1)
        if self.skip: return
        if tag in {'h1','h2','h3','h4','h5'} and self.heading is not None:
            self.headings.append(' '.join(self.heading)); self.heading=None
        if tag=='a' and self.link is not None: self.links.append(self.link); self.link=None
    def handle_data(self, text):
        text=text.strip()
        if not self.skip and text:
            self.parts.append(text)
            if self.heading is not None:self.heading.append(text)
            if self.link is not None:self.link['title']+=text

def plain(raw): return ' '.join(Extract(raw).parts)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'content/research/expansion'
OUT.mkdir(parents=True, exist_ok=True)
HEADERS = {'User-Agent': '90s.land editorial research/1.0 (historical archive; contact via 90s.land)'}

def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=HEADERS), timeout=35) as response:
        return response.read()

def source(pair):
    key, url = pair
    try:
        parsed=Extract(get(url).decode('utf-8',errors='replace'))
        text = ' '.join(parsed.parts)
        headings = parsed.headings
        links = [{'title':a['title'], 'url':urllib.parse.urljoin(url,a['url'])} for a in parsed.links]
        record = dict(id=key,url=url,checkedAt='2026-10-01',headings=headings,text=text,links=links)
        (OUT/(key+'.json')).write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
        return dict(id=key,headings=headings,text=text[-14000:] if key.startswith('chm') else text[:1000])
    except Exception as exc: return dict(id=key,error=str(exc))

SOURCES = [(f'chm-{y}',f'https://www.computerhistory.org/timeline/{y}/') for y in range(1990,2000)] + [
 ('prince','https://discography.prince.com/'),('nin','https://www.nin.com/discography/'),
 ('radiohead','https://www.radiohead.com/library/'),('depeche','https://archives.depechemode.com/discography/albums/'),
 ('prodigy','https://theprodigy.com/music'),('pearl-jam','https://pearljam.com/music/album'),
 ('nintendo','https://www.nintendo.com/us/about/'),('sony-history','https://www.playstation.com/en-us/playstation-history/'),
 ('sonic','https://sonic.sega.jp/SonicChannel/gametitle/'),
 ('tomb-raider','https://www.tombraider.com/games'),('blizzard','https://www.blizzard.com/en-us/company/about/'),
 ('dr-martens','https://www.drmartens.com/us/en/history'),('fubu','https://fubu.com/pages/our-story'),
 ('vans','https://www.vans.com/en-us/company/about'),('scholastic','https://www.scholastic.com/site/about-scholastic/history.html')]

QUERIES = {
 'snes':'Super Nintendo Entertainment System console','game-gear':'Sega Game Gear console',
 'saturn':'Sega Saturn console','minidisc':'Sony MZ-1 MiniDisc',
 'palm-pilot':'PalmPilot Personal','nokia-3210':'Nokia 3210',
 'zip-drive':'Iomega Zip 100 drive','floppy-disk':'3.5 inch floppy disk',
 'memory-card':'PlayStation memory card -Vita -PS2','game-shark':'GameShark PlayStation',
 'webtv':'Sony WebTV INT-W100','quickcam':'Connectix QuickCam',
 'disposable-camera':'Fujifilm QuickSnap camera','talkboy':'Talkboy',
 'furby':'Furby 1998','tamagotchi':'Tamagotchi original',
 'beanie-baby':'Beanie Babies','pogs':'Pogs milk caps',
 'super-soaker':'Super Soaker 50','walkman':'Sony Walkman WM-FX',
 'tb-303':'Roland TB-303','mpc-2000':'Akai MPC2000',
 'mc-303':'Roland MC-303','technics-turntable':'Technics SL-1200MK2',
 'korg-m1':'Korg M1','dat-recorder':'Sony DAT recorder',
 'jewel-case':'CD jewel case','dr-martens':'Dr Martens 1460 boots',
 'vans-shoes':'Vans Old Skool shoes','answering-machine':'answering machine cassette',
 'cd-binder':'CD binder','super-famicom':'Super Famicom console',
 'digital-camera':'Casio QV-10','powerbook':'PowerBook 100','newton':'Apple Newton MessagePad'}

def commons(pair):
    key, query = pair
    params = dict(action='query',format='json',generator='search',gsrsearch=query,gsrnamespace=6,gsrlimit=5,prop='imageinfo',iiprop='url|extmetadata',iiurlwidth=960)
    try:
        result=json.loads(get('https://commons.wikimedia.org/w/api.php?'+urllib.parse.urlencode(params)))
        rows=[]
        for p in sorted(result.get('query',{}).get('pages',{}).values(), key=lambda p:p.get('index',999)):
            i=p.get('imageinfo',[{}])[0];m=i.get('extmetadata',{})
            license=m.get('LicenseShortName',{}).get('value','')
            if not any(x in license for x in ['CC BY','CC0','Public domain','PD']): continue
            rows.append(dict(title=p['title'],url=i.get('thumburl',i.get('url')),original=i.get('url'),descriptionUrl=i.get('descriptionurl'),width=i.get('thumbwidth'),height=i.get('thumbheight'),credit=plain(m.get('Artist',{}).get('value','')),license=license,licenseUrl=m.get('LicenseUrl',{}).get('value',''),description=plain(m.get('ImageDescription',{}).get('value',''))))
        (OUT/('media-'+key+'.json')).write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
        return dict(id=key,candidates=[{k:r[k] for k in ['title','license','description']} for r in rows])
    except Exception as exc: return dict(id=key,error=str(exc))

if __name__=='__main__':
    import sys
    pairs = [(f'albums-{y}',f'https://www.udiscovermusic.com/stories/best-{y}-albums/') for y in range(1990,2000)] if '--albums' in sys.argv else ([(k,v) for k,v in QUERIES.items() if not (OUT/('media-'+k+'.json')).exists() or k=='memory-card'] if '--media' in sys.argv else SOURCES)
    with concurrent.futures.ThreadPoolExecutor(max_workers=1 if '--media' in sys.argv else 4) as pool:
        for r in pool.map(commons if '--media' in sys.argv else source,pairs):
            print(json.dumps(r,ensure_ascii=False),flush=True)
