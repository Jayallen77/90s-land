#!/usr/bin/env python3
"""Local-only release preview with negotiated gzip and genuine 404 responses."""
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

def gzip_accepted(header):
    values={}
    for entry in header.split(','):
        coding,*parameters=entry.strip().split(';'); quality=1
        for value in parameters:
            if value.strip().startswith('q='):
                try: quality=float(value.strip()[2:])
                except ValueError: quality=0
        values[coding.strip()]=quality
    return values.get('gzip',values.get('*',0))>0

class Handler(SimpleHTTPRequestHandler):
    def handle(self):
        try:super().handle()
        except (BrokenPipeError,ConnectionResetError):pass  # A browser can cancel lazy requests.
    def send_head(self):
        target=Path(self.translate_path(self.path))
        if target.is_dir():
            if not self.path.split('?')[0].endswith('/'):return super().send_head()
            target=target/'index.html'
        status=200
        if not target.is_file():target=Path(self.directory)/'404.html';status=404
        if not target.is_file():return super().send_head()
        mime=self.guess_type(str(target))
        compressed=target.with_name(target.name+'.gz')
        accepts_gzip=gzip_accepted(self.headers.get('Accept-Encoding',''))
        use_gzip=accepts_gzip and compressed.is_file()
        response=open(compressed if use_gzip else target,'rb')
        self.send_response(status); self.send_header('Content-Type',mime)
        self.send_header('Content-Length',str((compressed if use_gzip else target).stat().st_size))
        self.send_header('Vary','Accept-Encoding');self.send_header('Cache-Control','no-cache')
        if use_gzip:self.send_header('Content-Encoding','gzip')
        self.end_headers();return response
    def log_message(self,*args):pass

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True);parser.add_argument('--port',type=int,default=4174);args=parser.parse_args()
    server=ThreadingHTTPServer(('127.0.0.1',args.port),partial(Handler,directory=str(args.root.resolve())))
    print(f'Release preview: http://127.0.0.1:{args.port}',flush=True)
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()
