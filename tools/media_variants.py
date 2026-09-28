"""Apply optimized assets to generated documents, never to preserved sources."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VARIANTS = json.loads((ROOT/'data/asset-variants.json').read_text())['images']

def image_record(record):
    variants = VARIANTS.get(record['src'])
    if not variants: return record
    default = next((v for v in variants if v['width']>=480), variants[-1])
    return {**record, 'src':default['src'],
            'srcset':', '.join(f'{v["src"]} {v["width"]}w' for v in variants),
            'sizes':'(max-width: 600px) 90vw, 720px'}

def optimize_html(source):
    def replace(match):
        tag = match.group(0)
        src = re.search(r'\bsrc="([^"]+)"',tag)
        if not src or src[1] not in VARIANTS: return tag
        record = image_record({'src':src[1]})
        tag = tag.replace(src[0], f'src="{record["src"]}"',1)
        if 'srcset=' not in tag:
            sizing = '' if 'sizes=' in tag else f' sizes="{record["sizes"]}"'
            tag = tag.replace(' />', f' srcset="{record["srcset"]}"{sizing} />')
        return tag
    return re.sub(r'<img\b[^>]*?/>',replace,source)
