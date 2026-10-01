#!/usr/bin/env python3
"""Reproducible local WebP/WOFF2 derivatives; original media stays untouched."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'data/asset-variants.json'
FONTS = ['Jersey10-Regular', 'Barlow-Regular', 'Barlow-Bold',
         'BarlowCondensed-SemiBold', 'BarlowCondensed-Bold']

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    if args.check:
        manifest = json.loads(MANIFEST.read_text())
        files = manifest['files']
        stale = [name for name, expected in files.items()
                 if not (ROOT/name).is_file() or digest(ROOT/name) != expected]
        expected_sources={a['media']['src'] for a in json.loads((ROOT/'data/artifacts.json').read_text()) if a['media']['kind']=='image'}
        if expected_sources != set(manifest['images']): stale.append('Artifact image inventory changed')
        print(f'Optimized asset integrity: {len(files)} files; {len(stale)} stale')
        for name in stale: print(name)
        return bool(stale)
    from PIL import Image
    previous = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {'files':{}}
    manifest = {'version': 1, 'imageOptions': {'format': 'WebP', 'quality': 80, 'method': 6},
                'images': {}, 'files': {}}
    def record(path):
        manifest['files'][str(path.relative_to(ROOT))] = digest(path)
    out = ROOT/'assets/generated/editorial'
    out.mkdir(parents=True, exist_ok=True)
    for artifact in json.loads((ROOT/'data/artifacts.json').read_text()):
        media = artifact['media']
        if media['kind'] != 'image': continue
        source = ROOT/media['src'].lstrip('/')
        record(source)
        with Image.open(source) as image:
            image.seek(0)
            sizes = sorted({min(width, image.width) for width in (240,480,960)})
            variants = []
            for width in sizes:
                height = round(image.height*width/image.width)
                resized = image.convert('RGB').resize((width,height), Image.Resampling.LANCZOS)
                target = out/f'{artifact["id"]}-{width}.webp'
                resized.save(target, 'WEBP', quality=80, method=6)
                record(target)
                variants.append({'src':'/'+str(target.relative_to(ROOT)), 'width':width,'height':height})
        manifest['images'][media['src']] = variants
    for name in FONTS:
        source = ROOT/f'assets/fonts/{name}.ttf'
        target = source.with_suffix('.woff2')
        unchanged = all(path.exists() and previous['files'].get(str(path.relative_to(ROOT))) == digest(path) for path in (source,target))
        if not unchanged:
            from fontTools.ttLib import TTFont
            font = TTFont(source, recalcTimestamp=False)
            font.flavor = 'woff2'
            font.save(target)
        record(source); record(target)
    MANIFEST.write_text(json.dumps(manifest,indent=2)+'\n')
    print(f'Created variants for {len(manifest["images"])} images and {len(FONTS)} fonts')
    return 0

if __name__ == '__main__': raise SystemExit(main())
