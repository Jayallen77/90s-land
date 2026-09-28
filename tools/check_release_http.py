#!/usr/bin/env python3
"""Verify the packaged preview's routes, encodings, 404s and source exclusion."""
import argparse
import gzip
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT=Path(__file__).resolve().parents[1]

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--base-url',default='http://127.0.0.1:4174');parser.add_argument('--release',type=Path,required=True);args=parser.parse_args()
    manifest=json.loads((args.release/'release-manifest.json').read_text())
    routes=json.loads((ROOT/'data/routes.json').read_text())
    def head(path):
        try:
            with urlopen(Request(args.base_url+path,method='HEAD'),timeout=10) as response:return path,response.status
        except HTTPError as error:return path,error.code
    with ThreadPoolExecutor(max_workers=6) as pool:status=list(pool.map(lambda r:head(r['path']),routes))
    errors=[f'{path}: {code}' for path,code in status if code!=200]
    excluded=['/does-not-exist/','/.git/config','/content/editorial/catalog.json','/docs/REBUILD_HANDOFF.md','/reports/PHASE_5_QA.md','/assets/editorial/home-hero-original.png']
    missing=[head(path) for path in excluded]
    errors.extend(f'Expected 404: {path}: {code}' for path,code in missing if code!=404)
    for path in ['/','/timeline/1996/','/js/app.js','/editorial.css','/data/editorial-index.json']:
        request=Request(args.base_url+path,headers={'Accept-Encoding':'gzip'})
        with urlopen(request,timeout=10) as response:
            if response.headers.get('Content-Encoding')!='gzip':errors.append('Missing gzip: '+path)
            if 'Accept-Encoding' not in response.headers.get('Vary',''):errors.append('Missing Vary: '+path)
            body=gzip.decompress(response.read())
        name=path.lstrip('/')+('index.html' if path.endswith('/') else '')
        if hashlib.sha256(body).hexdigest()!=manifest['files'][name]['sha256']:errors.append('Served content mismatch: '+path)
    result={'routes':len(routes),'routeStatus':200,'excludedPaths':dict(missing),'gzipSamples':5,'contentDigest':manifest['contentDigest'],'errors':errors}
    output=ROOT/'reports/phase-5/release-http.json';output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
    return bool(errors)

if __name__=='__main__':raise SystemExit(main())
