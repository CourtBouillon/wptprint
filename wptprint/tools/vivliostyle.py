import json
from functools import cache
from subprocess import run
from tempfile import NamedTemporaryFile
from urllib.request import urlopen

from ._common import ROOT, pdf_to_png

STYLESHEET = '''
    @page { margin: 0; size: 680px }
    body { margin: 8px }
'''


def render_images(path, version, generate=False):
    with NamedTemporaryFile(suffix='.pdf') as pdf:
        run((
            ROOT / 'tools' / 'vivliostyle' / version / 'bin' / 'vivliostyle',
            'build', '--css', STYLESHEET, path, '-o', pdf.name))
        return pdf_to_png(generate, filename=pdf.name)


@cache
def list_versions():
    versions = json.load(urlopen(
        'https://api.github.com/repos/vivliostyle/vivliostyle.js/'
        'git/matching-refs/tags/'))
    return [
        version['ref'].split('/')[-1][1:] for version in versions
        if version['ref'].split('/')[-1].startswith('v')][::-1]


def install(version):
    path = ROOT / 'tools' / 'vivliostyle' / version
    run((ROOT / 'venv' / 'bin' / 'nodeenv', path), cwd=ROOT)
    env = {
        'NODE_PATH': path / 'lib' / 'node_modules',
        'NPM_CONFIG_PREFIX': path}
    run((
        path / 'bin' / 'npm', 'install', '-g',
        '@vivliostyle/cli', f'@vivliostyle/core@{version}'),
        env=env, cwd=(path / 'lib'))
