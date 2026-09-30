#!/usr/bin/env python3
"""Content-driven sharing cards using reviewed local imagery and existing type."""
import argparse
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import launch_meta as meta

ROOT = meta.archive.ROOT
MANIFEST = ROOT/'data/social-cards.json'
FONT_NAMES = ['Jersey10-Regular.ttf','Barlow-Bold.ttf','Barlow-Regular.ttf','BarlowCondensed-Bold.ttf']


@lru_cache(None)
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def input_digest(spec):
    sources = [Path(__file__), ROOT/'assets/editorial/palm-sunset.svg', *[ROOT/'assets/fonts'/f for f in FONT_NAMES]]
    if spec['visual']['src']: sources.append(ROOT/spec['visual']['src'].lstrip('/'))
    data = {'spec':spec,'inputs':[sha(p) for p in sources]}
    return hashlib.sha256(json.dumps(data,sort_keys=True,ensure_ascii=False).encode()).hexdigest()


def wrapped(draw, value, font, width):
    lines=[]; line=''
    for word in value.split():
        trial=(line+' '+word).strip()
        if line and draw.textlength(trial,font=font)>width:lines.append(line);line=word
        else:line=trial
    if line:lines.append(line)
    return lines


def generate(spec, path):
    from PIL import Image, ImageDraw, ImageFont, ImageOps
    image=Image.new('RGB',(1200,630),'#040817');draw=ImageDraw.Draw(image)
    def font(name,size):return ImageFont.truetype(ROOT/'assets/fonts'/name,size)
    display=font('Jersey10-Regular.ttf',68); body=font('Barlow-Regular.ttf',25); label=font('BarlowCondensed-Bold.ttf',22)
    draw.rectangle((0,0,1199,629),outline='#34375d',width=3)
    draw.text((52,30),'90s.land',font=font('Jersey10-Regular.ttf',58),fill='#f7f5ff')
    draw.rectangle((52,99,169,104),fill='#ff149f')
    draw.text((52,133),spec['label'],font=label,fill='#ffd24a')
    lines=wrapped(draw,spec['title'],display,610)
    if spec['title'].isdigit():display=font('Jersey10-Regular.ttf',178);lines=[spec['title']]
    else:
        for size in range(68,37,-2):
            display=font('Jersey10-Regular.ttf',size);lines=wrapped(draw,spec['title'],display,610)
            if len(lines)*(size+5)<=270:break
    y=185
    for line in lines:
        draw.text((54,y+3),line,font=display,fill='#ff149f');draw.text((52,y),line,font=display,fill='#f7f5ff')
        y+=display.size+5
    summary=wrapped(draw,spec['subtitle'],body,600)
    y=max(y+16,380 if spec['title'].isdigit() else y+16)
    for line in summary[:max(1,min(3,(535-y)//31))]:draw.text((52,y),line,font=body,fill='#bbc3d7');y+=31
    draw.rounded_rectangle((715,62,1148,535),radius=8,fill='#10172c',outline='#34375d',width=2)
    visual=spec['visual']
    if visual['src']:
        with Image.open(ROOT/visual['src'].lstrip('/')) as source:
            fit = ImageOps.fit if visual['label']=='EDITORIAL ILLUSTRATION' else ImageOps.contain
            fitted=fit(source.convert('RGB'),(407,408),Image.Resampling.LANCZOS)
            image.paste(fitted,(728+(407-fitted.width)//2,85+(408-fitted.height)//2))
    else:
        for offset,color in [(0,'#9453f4'),(28,'#39d9dd'),(56,'#ff149f')]:
            draw.rectangle((760+offset,155+offset,1000+offset,342+offset),fill='#080e20',outline=color,width=3)
            draw.rectangle((760+offset,155+offset,1000+offset,180+offset),fill=color)
        draw.text((810,274),'90s',font=font('Jersey10-Regular.ttf',90),fill='#f7f5ff')
    draw.text((734,506),visual['label'],font=font('BarlowCondensed-Bold.ttf',16),fill='#39d9dd')
    draw.line((52,567,1148,567),fill='#34375d',width=2)
    credit=visual['credit']+' · '+visual['license']
    for row,line in enumerate(wrapped(draw,credit,font('Barlow-Regular.ttf',14),880)[:2]):draw.text((52,582+row*17),line,font=font('Barlow-Regular.ttf',14),fill='#bbc3d7')
    draw.text((970,588),'90s.land/credits',font=font('Barlow-Regular.ttf',16),fill='#39d9dd')
    path.parent.mkdir(parents=True,exist_ok=True);image.save(path,'JPEG',quality=88,optimize=True,progressive=True)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
    old=json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {'cards':{}}
    cards={};errors=[];generated=0
    for route in meta.card_routes():
        spec=meta.social_spec(route);digest=input_digest(spec)
        src=f'/assets/generated/share/{spec["id"]}-{digest[:12]}.jpg';path=ROOT/src.lstrip('/')
        previous=old['cards'].get(route['path'],{})
        valid=path.is_file() and previous.get('inputDigest')==digest and previous.get('sha256')==sha(path)
        if not valid:
            if args.check:errors.append('Missing or stale sharing card: '+route['path'])
            else:generate(spec,path);sha.cache_clear();generated+=1
        cards[route['path']]={'src':src,'width':1200,'height':630,'alt':spec['alt'],'inputDigest':digest,'sha256':sha(path) if path.is_file() else None,'visual':spec['visual']}
    manifest={'schemaVersion':1,'cards':cards}
    if args.check:
        if manifest!=old:errors.append('Sharing manifest is stale')
    else:
        MANIFEST.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
        keep={ROOT/c['src'].lstrip('/') for c in cards.values()}
        for obsolete in (ROOT/'assets/generated/share').glob('*.jpg'):
            if obsolete not in keep:obsolete.unlink()
    print(json.dumps({'cards':len(cards),'generated':generated,'errors':errors},indent=2))
    return bool(errors)


if __name__=='__main__':raise SystemExit(main())
