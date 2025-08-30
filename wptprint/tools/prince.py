import tarfile
from io import BytesIO
from functools import cache
from re import findall
from subprocess import run
from tempfile import NamedTemporaryFile
from urllib.request import urlopen

from ._common import ROOT, pdf_to_png

STYLESHEET = '''
    @page { margin: 0; size: 680px }
    body { margin: 8px }
'''

# Create default stylesheet
css_path = ROOT / 'tools' / 'prince' / 'style.css'
css_path.write_text(STYLESHEET)


def render_images(path, version, generate=False):
    with NamedTemporaryFile(delete=False) as pdf:
        run([
            ROOT / 'tools' / 'prince' / version /
            'lib' / 'prince' / 'bin' / 'prince',
            '-s', css_path, '--fileroot', ROOT / 'wpt',
            path, '-o', pdf.name])
        return pdf_to_png(generate, filename=pdf.name)


@cache
def list_versions():
    versions = []
    main_changelog = urlopen('https://www.princexml.com/releases/').read()
    links = dict.fromkeys(findall(r'/releases/\d{1,2}/', main_changelog.decode()))
    for link in links:
        changelog = urlopen(f'https://www.princexml.com{link}').read()
        versions.extend(findall(
            r'Prince (\d{1,2}\.\d{1,2}\.?\d{0,2})', changelog.decode()))
    return versions


def install(version):
    path = ROOT / 'tools' / 'prince'
    filename = f'prince-{version}-linux-generic-x86_64'
    url = f'https://www.princexml.com/download/{filename}.tar.gz'
    tarfile.open(fileobj=BytesIO(urlopen(url).read())).extractall(path)
    (path / filename).rename(path / version)
