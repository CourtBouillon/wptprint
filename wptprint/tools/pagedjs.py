import json
from functools import cache
from subprocess import run
from tempfile import NamedTemporaryFile
from urllib.request import urlopen

from ._common import ROOT, pdf_to_png

STYLESHEET = '''
    @page { margin: 0; size: 680px 680px }
    body { margin: 8px }
'''

# Create default stylesheet
css_path = ROOT / 'tools' / 'pagedjs' / 'style.css'
css_path.write_text(STYLESHEET)


def render_images(path, version, generate=False):
    # Work around file extension detection
    with NamedTemporaryFile(suffix='.html') as html:
        html.write(path.read_bytes())
        html.seek(0)
        with NamedTemporaryFile() as pdf:
            run([
                ROOT / 'tools' / 'pagedjs' / version / 'bin' / 'pagedjs-cli',
                '--style', css_path, html.name, '-o', pdf.name])
            return pdf_to_png(generate, filename=pdf.name)


@cache
def list_versions():
    url = 'https://gitlab.coko.foundation/api/v4/projects/717/repository/tags'
    return [version['name'][1:] for version in json.load(urlopen(url))]


def install(version):
    path = ROOT / 'tools' / 'pagedjs' / version
    run((ROOT / 'venv' / 'bin' / 'nodeenv', path), cwd=ROOT)
    env = {
        'NODE_PATH': path / 'lib' / 'node_modules',
        'NPM_CONFIG_PREFIX': path}
    run((
        path / 'bin' / 'npm', 'install', '-g',
        'pagedjs-cli', f'pagedjs@{version}'),
        env=env, cwd=(path / 'lib'))
