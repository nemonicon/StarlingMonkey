"""Optional Root-owned pure decision seam; no runtime/parser/analyzer invocation."""
import ast
import hashlib
import json
from pathlib import Path

SOURCE_SHA256 = '9bc964bb4e79af76f3158e5541a96c9806deb16b4704655ad340e717761340c4'
source = Path(__file__).resolve().with_name('analyze.py').read_bytes()
assert len(source) <= 128 * 1024 and hashlib.sha256(source).hexdigest() == SOURCE_SHA256
tree = ast.parse(source)
nodes = [x for x in tree.body if isinstance(x, ast.FunctionDef) and x.name == 'native_site_join']
assert len(nodes) == 1
scope = {}
exec(compile(ast.Module(body=nodes, type_ignores=[]), '<actual-pure-native-site-join>', 'exec'), scope)
decide = scope['native_site_join']
nonce = '0' * 64
other_nonce = '1' * 64


def observation(status='single-valid', method='POST', path='/actions', reason='-', corr=nonce):
    return {'record': dict(status=status, observations=2 if status == 'ambiguous' else 1,
                           method=method, path=path, reason=reason,
                           corr=corr, corrCount=1 if status == 'single-valid' else None)}


valid = observation()
missing = observation('unavailable', reason='missing', corr=None)
other = observation(corr=other_nonce)
get = observation(method='GET')
invalid = observation('unavailable', reason='invalid', corr=None)
duplicate = observation('unavailable', reason='duplicate', corr=None)
nonlinear = observation('unavailable', reason='nonlinear-string', corr=None)
cleared = observation('unavailable', method='-', path='-', reason='invalid-arguments', corr=None)
ambiguous = observation('ambiguous', method='-', path='-', reason='multiple-observations', corr=None)
get_unknown = observation('unavailable', method='GET', reason='invalid', corr=None)

# Handclassified public-cardinality policy cases, not captured runtime evidence.
cases = [
    ('absent', True, False, [], False),
    ('single-public-post-site', True, False, [valid], True),
    ('separate-certified-missing-post', True, False, [missing, valid], True),
    ('separate-explicit-other-nonce', True, False, [other, valid], True),
    ('get-is-not-post', True, False, [get], False),
    ('known-get-does-not-substitute-or-erase-post', True, False, [valid, get], True),
    ('unknown-invalid-post-blocks', True, False, [valid, invalid], False),
    ('unknown-duplicate-post-blocks', True, False, [valid, duplicate], False),
    ('unknown-nonlinear-post-blocks', True, False, [valid, nonlinear], False),
    ('cleared-route-blocks', True, False, [valid, cleared], False),
    ('multiple-observations-block', True, False, [valid, ambiguous], False),
    ('replayed-matching-public-value-blocks', True, False, [valid, valid], False),
    ('browser-or-v2-unjoined-blocks', False, False, [valid], False),
    ('native-loss-or-truncation-blocks', True, True, [valid], False),
    ('wrong-public-value-only', True, False, [other], False),
    ('missing-is-not-positive-site', True, False, [missing], False),
    ('known-nonpost-unknown-value-is-separate', True, False, [get_unknown, valid], True),
]
results = []
for name, public, loss, frames, expected in cases:
    value = decide(public, loss, frames, nonce)
    assert value['joined'] is expected, name
    results.append(dict(case=name, expected=expected, actual=value['joined']))
print(json.dumps(dict(passed=True, cases=results, sourceSha256=SOURCE_SHA256,
                      analyzerInvoked=False, capturedDataParsed=False,
                      sourceFunction='native_site_join only', targetInvoked=False), indent=2))
