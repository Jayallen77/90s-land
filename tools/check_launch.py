#!/usr/bin/env python3
"""Final publication gate: metadata, share images, structured data and public copy."""
import argparse
from collections import Counter
from html.parser import HTMLParser
import json
import re
import xml.etree.ElementTree as ET
from urllib.parse import urlsplit
import archive_content as archive
import launch_meta

ROOT = archive.ROOT


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title=''; self.metas={}; self.canonicals=[]; self.h1=0; self.images=[]
        self.schema=[]; self.text=[]; self.current=''; self.json=''; self.in_script=False; self.in_style=False
    def handle_starttag(self,tag,attrs):
        values=dict(attrs)
        if tag=='title':self.current='title'
        if tag=='script':self.in_script=True;self.current='json' if values.get('type')=='application/ld+json' else '';self.json=''
        if tag=='style':self.in_style=True
        if tag=='h1':self.h1+=1
        if tag=='img':self.images.append(values)
        if tag=='meta':
            key=values.get('name') or values.get('property')
            if key:self.metas.setdefault(key,[]).append(values.get('content',''))
        if tag=='link' and values.get('rel')=='canonical':self.canonicals.append(values.get('href'))
    def handle_endtag(self,tag):
        if tag=='title':self.current=''
        if tag=='script':
            if self.current=='json':self.schema.append(json.loads(self.json))
            self.in_script=False;self.current=''
        if tag=='style':self.in_style=False
    def handle_data(self,data):
        if self.current=='title':self.title+=data
        if self.current=='json':self.json+=data
        if not self.in_script and not self.in_style:self.text.append(data)


def assess():
    errors=[];rows=[];titles=[];descriptions=[];schema_count=Counter()
    cards=json.loads((ROOT/'data/social-cards.json').read_text())['cards']
    routes=archive.all_routes()+[{'path':'/404.html','title':'404 — Exhibit not found','summary':'The requested 90s.land exhibit could not be found.','type':'highlights'}]
    def require(ok,message):
        if not ok:errors.append(message)
    required=['description','robots','og:type','og:site_name','og:title','og:description','og:url','og:image','og:image:type','og:image:width','og:image:height','og:image:alt','twitter:card','twitter:title','twitter:description','twitter:image','twitter:image:alt']
    for route in routes:
        path=route['path'];source=ROOT/('404.html' if path=='/404.html' else path.strip('/')+'/index.html' if path!='/' else 'index.html')
        page=Page();page.feed(source.read_text());meta=launch_meta.metadata(route)
        for key in required:require(len(page.metas.get(key,[]))==1 and bool(page.metas[key][0]),path+': missing/duplicate '+key)
        value=lambda key:page.metas.get(key,[''])[0]
        require(page.title==meta['title'],path+': wrong title');require(page.canonicals==[meta['canonical']],path+': wrong canonical')
        require(value('og:url')==meta['canonical'],path+': wrong OG URL')
        require(value('robots')==('index,follow' if meta['indexable'] else 'noindex,follow'),path+': wrong index policy')
        require(page.h1==1,path+': needs one h1')
        card=cards[launch_meta.card_route(route)]
        require(value('og:image')==launch_meta.SITE_URL+card['src'] and value('twitter:image')==value('og:image'),path+': wrong sharing image')
        require(value('og:image:width')=='1200' and value('og:image:height')=='630',path+': wrong card dimensions')
        require((ROOT/card['src'].lstrip('/')).is_file(),path+': missing share image')
        for image in page.images:require('alt' in image,path+': missing image alt '+image.get('src',''))
        for data in page.schema:
            schema_count[data['@type']]+=1
            if data['@type']=='BreadcrumbList':
                items=data['itemListElement'];require(items[-1]['item']==meta['canonical'],path+': wrong breadcrumb destination')
                require([i['position'] for i in items]==list(range(1,len(items)+1)),path+': unordered breadcrumbs')
        types={d['@type'] for d in page.schema}
        if path=='/':require('WebSite' in types,'Home: missing site name schema')
        elif path!='/404.html':require('BreadcrumbList' in types,path+': missing breadcrumbs')
        # Match visible text, not authoring comments, form placeholders or source URLs.
        copy=' '.join(page.text)
        require(not re.search(r'\b(?:TODO|FIXME|lorem ipsum|coming soon|insert (?:title|text)|test text)\b',copy,re.I),path+': unfinished public copy')
        titles.append(page.title);descriptions.append(value('description'))
        rows.append({'path':path,'title':page.title,'description':value('description'),'canonical':meta['canonical'],'indexable':meta['indexable'],'shareImage':card['src'],'schemas':sorted(types)})
    require(len(titles)==len(set(titles)),'Duplicate page titles');require(len(descriptions)==len(set(descriptions)),'Duplicate page descriptions')
    sitemap={e.text for e in ET.parse(ROOT/'sitemap.xml').findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')}
    require(sitemap=={r['canonical'] for r in rows if r['indexable']},'Sitemap differs from indexable routes')
    require('Sitemap: '+launch_meta.SITE_URL+'/sitemap.xml' in (ROOT/'robots.txt').read_text(),'Missing robots sitemap')
    return {'routes':len(rows)-1,'errorPageChecked':True,'indexableRoutes':len(sitemap),'uniqueShareCards':len(cards),'structuredData':dict(schema_count),'pages':rows,'errors':errors}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',default='reports/launch-phase3/publication.json');args=parser.parse_args()
    result=assess();path=ROOT/args.output;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='pages'},indent=2));return bool(result['errors'])

if __name__=='__main__':raise SystemExit(main())
