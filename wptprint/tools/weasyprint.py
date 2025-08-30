import atexit
import json
from functools import cache
from subprocess import Popen, run
from time import sleep
from urllib.request import Request, urlopen
from venv import EnvBuilder

from ._common import ROOT, pdf_to_png

REJECTED_TAGS = {'script'}
STYLESHEET = '''
    @page { margin: 0; size: 680px }
    :root { image-rendering: pixelated; orphans: 1; widows: 1 }
'''

PROCESSES = {}
PROCESS_CODE = f'''
import http.server, socketserver, time, weasyprint
from func_timeout import func_timeout
css = weasyprint.CSS(string={repr(STYLESHEET)})
def render(string, path):
  html = weasyprint.HTML(string=string, base_url=path)
  document = html.render(stylesheets=[css], presentational_hints=True)
  return document.write_pdf()
class Handler(http.server.BaseHTTPRequestHandler):
  def do_POST(self):
    self.send_response(200)
    self.end_headers()
    string = self.rfile.read(int(self.headers['Content-Length']))
    try: self.wfile.write(func_timeout(10, render, args=(string, self.path)))
    except KeyboardInterrupt as exception: raise exception
    except: pass
socketserver.TCPServer.allow_reuse_address = True
try: socketserver.TCPServer(('localhost', %i), Handler).serve_forever()
except KeyboardInterrupt: pass
'''


def render_images(path, version, generate=False):
    # Work around CDATA support missing
    html = path.read_bytes() if path.exists() else b''
    if path.suffix == '.xht':
        html = html.replace(b'<![CDATA[', b'').replace(b']]>', b'')

    # Launch HTTP server subprocess
    if version in PROCESSES:
        while not PROCESSES[version]:
            sleep(1)
        weasyprint, port = PROCESSES[version]
    else:
        PROCESSES[version] = None
        port = 5000 + len(PROCESSES)
        weasyprint = Popen((
            ROOT / 'tools' / 'weasyprint' / version / 'bin' / 'python',
            '-u', '-c', PROCESS_CODE % port))
        sleep(3)
        PROCESSES[version] = weasyprint, port

    # Generate PDF bytestring
    pdf = urlopen(Request(f'http://localhost:{port}{path}', data=html)).read()

    return pdf_to_png(generate, pdf=pdf)


@cache
def list_versions():
    versions = json.load(urlopen(
        'https://api.github.com/repos/Kozea/WeasyPrint/'
        'git/matching-refs/tags/'))
    return [version['ref'].split('/')[-1][1:] for version in versions][::-1]


def install(version):
    path = ROOT / 'tools' / 'weasyprint' / version
    EnvBuilder(with_pip=True).create(path)
    run((
        path / 'bin' / 'pip', 'install',
        'func_timeout', f'weasyprint=={version}'))


atexit.register(lambda: [p.terminate() for p, _ in PROCESSES.values()])
