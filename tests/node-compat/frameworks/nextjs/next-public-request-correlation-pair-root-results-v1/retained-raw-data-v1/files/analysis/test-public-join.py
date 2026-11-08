"""Root-only pure decision seam: no DATA/analyzer main/producer/helper/target calls."""
import ast
import hashlib
import json
from pathlib import Path

SOURCE_SHA256 = 'bea8ebd58b1ca8f8539273f7caade5873b4a66312507d223f7ca4fe648f6f965'


def stamp(path):
    s = path.stat()
    return (s.st_dev, s.st_ino, s.st_mode, s.st_nlink, s.st_size, s.st_mtime_ns, s.st_ctime_ns)


def main():
    path = Path(__file__).resolve().with_name('analyze.py')
    before = stamp(path); assert 0 < before[4] < 100000
    source = path.read_bytes()
    assert hashlib.sha256(source).hexdigest() == SOURCE_SHA256 and stamp(path) == before
    tree = ast.parse(source)
    selected = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'public_join']
    assert len(selected) == 1
    # The exact actual pure decision function, not a mirrored implementation.
    namespace = {}
    exec(compile(ast.Module(body=selected, type_ignores=[]), str(path), 'exec'), namespace)
    decide = namespace['public_join']
    nonce, other = 'a' * 64, 'b' * 64

    def enter(lane, state='valid', corr=nonce, method='POST', route='/actions', count=1):
        return {'line': 1, 'record': {'lane': lane, 'event': lane + '-enter', 'method': method,
            'path': route, 'corrState': state, 'corr': corr, 'corrCount': count}}

    normal = [enter('adapter'), enter('classic')]
    cases = [
        ('single-valid-per-lane', normal, True, False, True),
        ('prior-missing-count0-both', normal + [enter('adapter', 'missing', None, count=0),
                                              enter('classic', 'missing', None, count=0)], True, False, True),
        ('valid-other-public-nonce', normal + [enter('adapter', corr=other), enter('classic', corr=other)], True, False, True),
        ('invalid-null-adapter', normal + [enter('adapter', 'invalid', None)], True, False, False),
        ('invalid-shape-count0', normal + [enter('classic', 'invalid', None, count=0)], True, False, False),
        ('duplicate-null-classic', normal + [enter('classic', 'duplicate', None, count=2)], True, False, False),
        ('coalesced-value-classified-invalid', normal + [enter('adapter', 'invalid', None)], True, False, False),
        ('both-ambiguous', normal + [enter('adapter', 'duplicate', None, count=2), enter('classic', 'invalid', None)], True, False, False),
        ('replayed-valid-adapter', normal + [enter('adapter')], True, False, False),
        ('replayed-valid-classic', normal + [enter('classic')], True, False, False),
        ('forwarded-get-additional', normal + [enter('adapter', method='GET', route='/action-result'),
                                              enter('classic', method='GET', route='/action-result')], True, False, True),
        ('get-cannot-substitute-post', [enter('adapter', method='GET', route='/action-result'),
                                      enter('classic', method='GET', route='/action-result')], True, False, False),
        ('wrong-browser-evidence', normal, False, False, False),
        ('logger-malformed-or-truncation-loss', normal, True, True, False),
        ('missing-classic', [enter('adapter')], True, False, False),
        ('wrong-valid-nonce-only', [enter('adapter', corr=other), enter('classic', corr=other)], True, False, False),
        ('empty-records', [], True, False, False),
    ]
    results = []
    for name, frames, browser, loss, expected in cases:
        result = decide(browser, loss, frames, nonce)
        assert result['joined'] is expected, (name, result)
        if name in {'invalid-null-adapter', 'invalid-shape-count0', 'duplicate-null-classic',
                    'coalesced-value-classified-invalid', 'both-ambiguous'}:
            assert result['ambiguousInvalidOrDuplicatePostEnterObservations']
        results.append({'case': name, 'expectedJoin': expected, 'actual': result})
    assert stamp(path) == before
    print(json.dumps({'passed': True, 'cases': len(cases), 'sourceSha256': SOURCE_SHA256,
        'scope': 'Actual pure decision function only; hand-authored already-classified frame fixtures. No marker parser, NetLog parser, logger, guest, target or actual analyzer main execution.',
        'results': results}, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
