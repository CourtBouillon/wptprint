def merge(dict1, dict2):
    dict1 = dict1.copy()
    for key in dict2:
        if key in dict1:
            merge(dict1[key], dict2[key])
        else:
            dict1[key] = dict2[key]
    return dict1


def flatten_tests(tests, path, flat_tests=None, previous=None):
    if flat_tests is None:
        flat_tests = {}
    for test, subtests in tests.items():
        if isinstance(subtests, dict):
            flatten_tests(
                subtests, f'{path}/{test}', flat_tests, previous=previous)
            if flat_tests:
                previous = tuple(flat_tests.values())[-1]
        else:
            sub_path = f'{path}/{test}'.lstrip('/')
            links = {'path': sub_path}
            if previous is not None:
                links['previous'] = previous
                previous['next'] = links
            flat_tests[sub_path] = links
            previous = links
    return flat_tests
