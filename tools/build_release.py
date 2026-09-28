#!/usr/bin/env python3
"""Package only public routes and their local runtime dependencies. Never deploy."""
import argparse
import gzip
import hashlib
import json
import re
import shutil
import tarfile
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
TEXT_TYPES = {'.html','.css','.js','.json','.xml','.txt','.svg','.webmanifest'}

class References(HTMLParser):
    def __init__(self): super().__init__(convert_charrefs=True); self.urls=[]
    def handle_starttag(self, tag, attrs):
        values=dict(attrs)
        for key in ('href','src','poster'):
            if values.get(key): self.urls.append(values[key])
        for key in ('srcset','imagesrcset'):
            self.urls.extend(value.strip().split()[0] for value in values.get(key,'').split(',') if value.strip())

def dependencies(root, relative):
    path=root/relative
    if path.suffix not in TEXT_TYPES: return set()
    source=path.read_text(); urls=[]
    if path.suffix=='.html':
        parser=References(); parser.feed(source); urls=parser.urls
    elif path.suffix=='.css':
        urls=re.findall(r'url\([\s\"\']*([^\)\"\']+)',source)
    elif path.suffix=='.js':
        urls=re.findall(r'(?:from\s*|import\s*\(\s*|fetch\s*\(\s*)[\"\']([^\"\']+)',source)
    elif path.suffix in ('.json','.webmanifest'):
        urls=re.findall(r'/(?:assets|data|js)/[^\s\"\',]+',source)
    found=set()
    for url in urls:
        parts=urlsplit(url)
        if parts.scheme or parts.netloc or not parts.path: continue
        raw=unquote(parts.path)
        candidate=root/raw.lstrip('/') if raw.startswith('/') else path.parent/raw
        candidate=candidate.resolve()
        if not candidate.is_relative_to(root.resolve()): raise ValueError(f'Outside public root: {url}')
        if candidate.is_dir(): candidate=candidate/'index.html'
        rel=candidate.relative_to(root.resolve())
        if not candidate.is_file(): raise ValueError(f'Missing dependency from {relative}: {url}')
        if rel.parts[0] not in {'assets','data','js'} and candidate.suffix not in {'.html','.css','.webmanifest','.txt','.xml'}:
            raise ValueError(f'Unexpected public dependency: {rel}')
        if rel.parts[0] in {'content','docs','reports','tests','tools','node_modules'}: raise ValueError(f'Private source linked as runtime: {rel}')
        found.add(rel)
    return found

def collect_files(root):
    routes=json.loads((root/'data/routes.json').read_text())
    seeds={Path(r['path'].strip('/'))/'index.html' for r in routes}
    seeds|={Path(p) for p in ['404.html','robots.txt','sitemap.xml','manifest.webmanifest','assets/generated/og-card.png']}
    included=set(); pending=list(seeds)
    while pending:
        path=pending.pop()
        if path in included:continue
        included.add(path)
        pending.extend(dependencies(root,path)-included)
    return included

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def verify(directory):
    manifest=json.loads((directory/'release-manifest.json').read_text())
    web=directory/'public'; expected=manifest['files']; errors=[]
    actual={str(p.relative_to(web)) for p in web.rglob('*') if p.is_file()}
    if actual!=set(expected): errors.append('Public file inventory differs from manifest')
    for name,record in expected.items():
        p=web/name
        if not p.resolve().is_relative_to(web.resolve()): raise ValueError('Manifest path escapes public directory')
        if not p.is_file() or sha(p)!=record['sha256']:errors.append('Checksum mismatch: '+name)
    for name in expected:
        if name.endswith('.gz'):continue
        try:
            for dep in dependencies(web,Path(name)):
                if str(dep) not in expected:errors.append('Unpackaged dependency: '+str(dep))
        except (ValueError,OSError) as error:errors.append(str(error))
    if errors:raise ValueError('\n'.join(errors))
    archive=directory/'90s-land.tar.gz'
    if archive.exists() and sha(archive)!=(directory/'90s-land.tar.gz.sha256').read_text().split()[0]:raise ValueError('Release archive checksum mismatch')
    return manifest

def build(root,directory):
    if directory.exists() and any(directory.iterdir()):raise ValueError('Output must be new or empty; existing releases are never overwritten')
    web=directory/'public'; web.mkdir(parents=True,exist_ok=True)
    paths=collect_files(root)
    for relative in sorted(paths):
        source=root/relative; target=web/relative; target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(source,target)
        if target.suffix in TEXT_TYPES and target.stat().st_size>1024:
            target.with_name(target.name+'.gz').write_bytes(gzip.compress(target.read_bytes(),compresslevel=9,mtime=0))
    files={str(p.relative_to(web)):{'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(web.rglob('*')) if p.is_file()}
    identity=hashlib.sha256(json.dumps(files,sort_keys=True).encode()).hexdigest()
    manifest={'schemaVersion':1,'contentDigest':identity,'routes':len(json.loads((root/'data/routes.json').read_text())),
              'runtimeFiles':len(paths),'files':files}
    (directory/'release-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    archive=directory/'90s-land.tar.gz'
    with archive.open('wb') as output:
        with gzip.GzipFile(filename='',mode='wb',fileobj=output,mtime=0) as compressed:
            with tarfile.open(fileobj=compressed,mode='w') as tar:
                for path in [directory/'release-manifest.json']+sorted(p for p in web.rglob('*') if p.is_file()):
                    entry=tar.gettarinfo(str(path),str(path.relative_to(directory)))
                    entry.uid=entry.gid=entry.mtime=0;entry.uname=entry.gname='';entry.mode=0o644
                    with path.open('rb') as stream:tar.addfile(entry,stream)
    (directory/'90s-land.tar.gz.sha256').write_text(sha(archive)+'  90s-land.tar.gz\n')
    verify(directory)
    return manifest

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);parser.add_argument('--check',action='store_true');args=parser.parse_args()
    manifest=verify(args.output.resolve()) if args.check else build(ROOT,args.output.resolve())
    print(json.dumps({k:v for k,v in manifest.items() if k!='files'},indent=2))

if __name__=='__main__':main()
