"""Download selected licensed object photographs for local editorial review."""
import io
import json
import concurrent.futures
import time
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw
from research_expansion import get, source

ROOT = Path(__file__).resolve().parents[1]
CHOICES = {'snes':4,'game-gear':0,'saturn':1,'minidisc':3,'palm-pilot':1,
 'nokia-3210':0,'zip-drive':1,'floppy-disk':4,'memory-card':1,'game-shark':0,
 'webtv':0,'quickcam':0,'disposable-camera':0,'talkboy':0,
 'beanie-baby':1,'pogs':0,'super-soaker':0,'walkman':0,'tb-303':2,
 'mpc-2000':0,'mc-303':0,'technics-turntable':0,'korg-m1':0,'dat-recorder':2,
 'jewel-case':1,'dr-martens':2,'vans-shoes':0,'answering-machine':0,
 'super-famicom':1,'digital-camera':0,'powerbook':0,'newton':0}

def download(pair):
 key, index = pair
 candidate = 'memory-card-original' if key == 'memory-card' else key
 row = json.loads((ROOT/f'content/research/expansion/media-{candidate}.json').read_text())[index]
 path=ROOT/f'assets/media/expansion/{key}.jpg';path.parent.mkdir(parents=True,exist_ok=True)
 if not path.exists():
  raw=None
  for attempt in range(4):
   try: raw=get(row['url'] if attempt==0 else row['original']);break
   except Exception:
    if attempt==3:raise
    time.sleep(5*(attempt+1))
  with Image.open(io.BytesIO(raw)) as im:
   im.seek(0);im=im.convert('RGBA');bg=Image.new('RGBA',im.size,'white');bg.alpha_composite(im)
   bg.convert('RGB').save(path,quality=90,optimize=True)
 with Image.open(path) as im:row.update(src='/'+str(path.relative_to(ROOT)),width=im.width,height=im.height)
 print(key, row['title'],flush=True)
 return key,row

if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool: rows=dict(pool.map(download,CHOICES.items()))
 (ROOT/'content/research/expansion/selected-media.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
 sheet=Image.new('RGB',(1000,((len(rows)+3)//4)*205),'#e8e3da');draw=ImageDraw.Draw(sheet)
 for i,(key,row) in enumerate(rows.items()):
  with Image.open(ROOT/row['src'].lstrip('/')) as im:tile=ImageOps.contain(im,(240,170));sheet.paste(tile,((i%4)*250+(250-tile.width)//2,(i//4)*205))
  draw.text(((i%4)*250+8,(i//4)*205+174),key,fill='black')
 sheet.save('/tmp/90s-expansion-contact.jpg')
 index=json.loads((ROOT/'content/research/expansion/snes-index.json').read_text())
 pairs={(Path(x['url']).stem,x['url']) for x in index['links'] if '/soft/' in x['url'] and not x['url'].endswith('index.html') and 's_fox2' not in x['url']}
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
  for result in pool.map(source,[(f'snes-{k}',url) for k,url in sorted(pairs)]):print(json.dumps(result,ensure_ascii=False)[:160],flush=True)
