import tarfile
from functools import cache
from io import BytesIO
from re import findall
from subprocess import run
from tempfile import NamedTemporaryFile
from urllib.request import urlopen

from ._common import ROOT, pdf_to_png

STYLESHEET = '''
    @page { margin: 0; size: 680px }
    body { margin: 8px }
'''


def render_images(path, version, generate=False):
    with NamedTemporaryFile() as pdf:
        run([
            ROOT / 'tools' / 'pdfreactor' / version / 'bin' / 'pdfreactor-cmd',
            '-c', STYLESHEET, '-i', path, '-o', pdf.name])
        return pdf_to_png(generate, filename=pdf.name)


@cache
def list_versions():
    changelog = urlopen('https://www.pdfreactor.com/product/changelog.htm').read()
    return findall(r'PDFreactor (\d{1,2}\.\d{1,2}\.\d{1,2})', changelog.decode())


def install(version):
    path = ROOT / 'tools' / 'pdfreactor'
    if int(version.split('.', 1)[0]) >= 12:
        url = (
            'https://download.realobjects.com/'
            f'PDFreactorWebService_{version.replace(".", "_")}_unix_installer.tar.gz')
    else:
        url = (
            'https://download.realobjects.com/'
            f'PDFreactor_{version.replace(".", "_")}_unix_installer.tar.gz')
    tarfile.open(fileobj=BytesIO(urlopen(url).read())).extractall(path)
    (path / 'PDFreactor').rename(path / version)
