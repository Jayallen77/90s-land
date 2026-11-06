"""Small, escaped editorial blocks; plain paragraph sources remain compatible."""
import re
import json
from pathlib import Path
from html import escape
from urllib.parse import urlsplit

def local_url(value):
    return value.removeprefix('https://90s.land') if value.startswith('https://90s.land/') else value

def inline(text):
    parts=[];last=0
    for m in re.finditer(r'\[([^\]]+)\]\(([^\s)]+)\)|\*\*([^*]+)\*\*|`([^`]+)`',text):
        parts.append(escape(text[last:m.start()]))
        label,url,bold,code=m.groups()
        if url:
            safe=(url.startswith('/') and not url.startswith('//')) or urlsplit(url).scheme=='https'
            parts.append(f'<a href="{escape(url,quote=True)}">{escape(label)}</a>' if safe else escape(label))
        elif bold:parts.append(f'<strong>{escape(bold)}</strong>')
        else:parts.append(f'<code>{escape(code)}</code>')
        last=m.end()
    return ''.join(parts)+escape(text[last:])

def parse(text):
    blocks=[]
    for chunk in re.split(r'\n\s*\n',text.strip()):
        lines=chunk.strip().splitlines()
        figure=re.fullmatch(r'\{\{figure:([a-z0-9-]+)\}\}',chunk.strip())
        tool=re.fullmatch(r'\{\{tool:([a-z0-9-]+)\}\}',chunk.strip())
        if figure:blocks.append({'type':'figure','id':figure[1]})
        elif tool:
            from reading_tools import IDS
            if tool[1] not in IDS:raise ValueError('Unknown reading tool: '+tool[1])
            blocks.append({'type':'tool','id':tool[1]})
        elif len(lines)>1 and lines[0].startswith('|') and re.fullmatch(r'[\s|:\-]+',lines[1]):
            cells=lambda line:[c.strip() for c in line.strip().strip('|').split('|')]
            blocks.append({'type':'table','headers':cells(lines[0]),'rows':[cells(line) for line in lines[2:]]})
        elif all(re.match(r'^[-*] ',line) for line in lines):blocks.append({'type':'list','items':[line[2:] for line in lines]})
        elif all(re.match(r'^\d+\. ',line) for line in lines):blocks.append({'type':'ordered','items':[re.sub(r'^\d+\. ','',line) for line in lines]})
        elif all(line.startswith('> ') for line in lines):blocks.append({'type':'note','text':' '.join(line[2:] for line in lines)})
        elif chunk.strip():blocks.append({'type':'paragraph','text':chunk.strip()})
    return blocks

def render(blocks,heading):
    result=[]
    for block in blocks:
        kind=block['type']
        if kind=='tool':
            from reading_tools import render as render_tool
            result.append(render_tool(block['id']))
        elif kind=='figure':
            figures=json.loads((Path(__file__).resolve().parents[1]/'content/editorial/figures.json').read_text())
            f=figures[block['id']]
            src=escape(f['src'],quote=True);large=escape(f.get('vectorSrc',f['src']),quote=True)
            result.append(f'<figure class="article-figure"><a href="{large}" aria-label="Open figure: {escape(f["alt"],quote=True)}"><img src="{src}" width="{f["width"]}" height="{f["height"]}" alt="{escape(f["alt"],quote=True)}" loading="lazy" decoding="async" /></a><figcaption>{escape(f["caption"])} <a href="{escape(local_url(f["sourceUrl"]),quote=True)}">{escape(f["credit"])}</a> · <a href="{escape(local_url(f["licenseUrl"]),quote=True)}">{escape(f["license"])}</a>. <a href="{large}">View large →</a></figcaption></figure>')
        elif kind=='table':
            headers=''.join(f'<th scope="col">{inline(c)}</th>' for c in block['headers'])
            rows=''.join('<tr>'+''.join(f'<td>{inline(c)}</td>' for c in row)+'</tr>' for row in block['rows'])
            result.append(f'<div class="article-table" role="region" aria-label="{escape(heading,quote=True)} comparison" tabindex="0"><table><caption>{escape(heading)}</caption><thead><tr>{headers}</tr></thead><tbody>{rows}</tbody></table></div>')
        elif kind in ('list','ordered'):
            tag='ol' if kind=='ordered' else 'ul';result.append(f'<{tag} class="article-list">'+''.join(f'<li>{inline(item)}</li>' for item in block['items'])+f'</{tag}>')
        else:result.append(f'<p'+(' class="article-note"' if kind=='note' else '')+f'>{inline(block["text"])}</p>')
    return ''.join(result)
