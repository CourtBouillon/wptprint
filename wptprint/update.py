from filecmp import dircmp
from itertools import chain
from pathlib import Path

from .utils import flatten_tests

ROOT = Path(__file__).parent.parent


def update(name, version_from, version_to, results_from, results_to):
    from . import TESTS
    folder_from = ROOT / 'results' / name / version_from
    folder_to = ROOT / 'results' / name / version_to
    ignore = list({
        file.name for file in chain(
            folder_from.glob('*-ref-*.png'), folder_from.glob('*.json'),
            folder_to.glob('*-ref-*.png'), folder_to.glob('*.json'))})
    comp = dircmp(folder_from, folder_to, ignore=ignore)
    differences = {
        file[:40] for file in
        comp.diff_files + comp.left_only + comp.right_only}
    print(f'{len(differences)} differences')
    flat_tests = flatten_tests(TESTS['css'], 'css')
    for path, _ in flat_tests.items():
        result_from = results_from.get(path, {})
        result_to = results_to.get(path, {})
        if not result_to:
            continue
        test = TESTS
        for part in path.split('/'):
            test = test[part]
        hash = test[0]
        if hash in differences:
            result_to['verified'] = None
        else:
            if 'status' in result_from:
                result_to['status'] = result_from['status']
            if 'verified' in result_from:
                result_to['verified'] = result_from['verified']
        yield result_to
