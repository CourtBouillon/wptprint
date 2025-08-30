from importlib import import_module
from os import system
from pathlib import Path
from time import time

from func_timeout import func_timeout

from .utils import flatten_tests

ROOT = Path(__file__).parent.parent


def render(tool, version, path, folder, counters):
    from . import TESTS

    tests = TESTS
    for part in path.split('/'):
        tests = tests[part]
    hash, (_, conditions, tags) = tests

    rendering_images = []
    result = {
        'test': f'/{path}',
        'subtests': [],
        'message': '',
        'duration': 0,
        'known_intermittent': [],
    }

    path = (ROOT / 'wpt' / path)
    if path.exists():
        html = path.read_text()
        if '<script' in html:
            tags['script'] = None

    if not path.exists() or set(tags) & getattr(tool, 'REJECTED_TAGS', set()):
        result['status'] = 'NA'
        counters['na'] += 1
        return result

    args = (path, version, True)
    start = time()
    try:
        images = func_timeout(10, tool.render_images, args=args)
    except KeyboardInterrupt as exception:
        raise exception
    except BaseException:
        images = []
    stop = time()
    result['duration'] = int((stop - start) * 1000)
    if images:
        for i, image in enumerate(images):
            rendering_images.append(image)
            (folder / f'{hash}-{i}.png').write_bytes(image)

        references = [
            ROOT / 'wpt' / reference.lstrip('/')
            for reference, condition in conditions
            if condition == '==']
        reference_images_list = []
        for reference in references:
            reference_images = []
            reference_images_list.append(reference_images)
            images = tool.render_images(reference, version, generate=True)
            for i, image in enumerate(images):
                reference_images.append(image)
                (folder / f'{hash}-ref-{i}.png').write_bytes(image)

        for reference_images in reference_images_list:
            if len(reference_images) != len(rendering_images):
                continue
            if reference_images == rendering_images:
                counters['passing'] += 1
                result['status'] = 'PASS'
                break
        else:
            counters['failing'] += 1
            result['status'] = 'FAIL'
    else:
        counters['failing'] += 1
        result['status'] = 'ERROR'
    return result


def generate(name, version, results, pattern, force):
    from . import TESTS

    tool = import_module(f'.tools.{name}', 'wptprint')
    folder = ROOT / 'results' / name / version
    folder.mkdir(parents=True, exist_ok=True)
    counters = {'passing': 0, 'failing': 0, 'na': 0}
    full_start = time()

    flat_tests = flatten_tests(TESTS['css'], 'css')
    if pattern:
        flat_tests = {path: test for path, test in flat_tests.items() if pattern in path}
    for number, (path, _) in enumerate(flat_tests.items(), start=1):
        if not force and path in results and 'status' in results[path]:
            status = {'PASS': 'passing', 'NA': 'na'}
            counters[status.get(results[path]['status'], 'failing')] += 1
            yield results[path]
        else:
            yield render(tool, version, path, folder, counters)
            system('clear')
            passing, failing, na = counters.values()
            print(
                f'{number / len(flat_tests):.2%} − {int(time() - full_start)}s'
                f' − {passing} pass, {failing} fail, {na} not appliable '
                f'({(passing / ((passing + failing) or 1)):.2%} pass) − {path}')
