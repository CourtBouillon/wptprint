from pathlib import Path
from subprocess import PIPE, run

from .. import app

ROOT = Path(__file__).parent.parent.parent
MAGIC_NUMBER = b'\x89\x50\x4e\x47\x0d\x0a\x1a\x0a'
CONFIG = app.config


def pdf_to_png(generate, filename=None, pdf=None):
    if not filename and not pdf:
        return []
    command = ['pdftoppm', '-r', '72' if generate else '96', '-png']
    if generate:
        command.extend(['-aa', 'no', '-aaVector', 'no'])
    command.append('-')
    input = pdf or Path(filename).read_bytes()
    pngs = run(command, input=input, stdout=PIPE).stdout
    if not pngs.startswith(MAGIC_NUMBER):
        return []
    return [MAGIC_NUMBER + png for png in pngs[8:].split(MAGIC_NUMBER)]
