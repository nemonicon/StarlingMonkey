"""Inert retained-DATA tests only. No sockets, children, application or actor calls."""
import base64
import ast
import re
import contextlib
import copy
import gzip
import importlib.util
import io
import json
from pathlib import Path

HERE = Path(__file__).absolute().parent
spec = importlib.util.spec_from_file_location('request_data_checker', HERE / 'check.py')
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)
count = 0


def check(value):
    global count
    count += 1
    assert value is True


def refuses(call):
    global count
    count += 1
    try:
        call()
    except (ValueError, AssertionError, KeyError, TypeError, FileNotFoundError):
        return
    raise AssertionError('accepted negative DATA')


policy = c.loads((HERE / 'policy.json').read_bytes())
roles = policy['roles']
reader = c.Reader()
pure = c.pure_functions(reader, roles)
root = Path(roles['nativeSource']['path']).parent
retained = {}
for mode in ['positive', 'crossed-context', 'malformed-transport-failure', 'partial-response-close']:
    value = c.loads((root / 'checks' / ('fake-http-v2.json.' + mode + '.json')).read_bytes())
    check(value['fakeServerOnly'] is True)
    raw = value['raw']
    retained[mode] = raw
    check(c.capture_integrity(raw)['captureIntegrityPassed'])
    validation = c.supplemental_semantics(raw)
    check(validation['passed'] is (mode == 'positive'))
    check(len(raw['observations']) == 6)
    if mode == 'positive':
        check(validation['checks'] == 80)
        check(c.additional_ordering(raw))
    if mode == 'partial-response-close':
        partial = next(r for r in raw['observations'] if r['id'] == 'malformed-json')
        check(partial['error'] is not None and partial['bodyEofObserved'] is False)
        check(c.b64(partial['bodyBase64']) == b'{"marker":"NEXT_JSON_BAD_')
        check(c.capture_integrity(raw)['partialOrFailedOutcomes'] == 1)

# Genuine pinned Node DOMException serialization DATA, not an actual timeout.
serialization = c.loads((HERE / 'checks' / 'serialization.stdout.json').read_bytes())
check(serialization['node'] == 'v22.14.0' and serialization['serializationOnly'] is True)
check([r['error']['code'] for r in serialization['cases']] == [20, 23])
for row in serialization['cases']:
    error = row['error']
    check(type(error['code']) is int and c.valid_error(error))
    raw = copy.deepcopy(retained['partial-response-close' if row['name'] == 'TimeoutError' else 'malformed-transport-failure'])
    failed = next(r for r in raw['observations'] if r['id'] == 'malformed-json')
    failed['error'] = error
    check(c.capture_integrity(raw)['captureIntegrityPassed'])
    check(c.supplemental_semantics(raw)['passed'] is False)
    for code in [True, False, float('nan'), float('inf'), -float('inf'), {}, []]:
        invalid = dict(error, code=code)
        check(c.valid_error(invalid) is False)
        failed['error'] = invalid
        refuses(lambda: c.capture_integrity(raw))
    for code in [0, -1, 1.5, 'ERR_EXAMPLE', None]:
        check(c.valid_error(dict(error, code=code)))

positive = retained['positive']
for mutate in [
    lambda r: r['observations'].pop(),
    lambda r: r['observations'].__setitem__(1, copy.deepcopy(r['observations'][0])),
    lambda r: r['observations'][0].__setitem__('bodyBase64', 'AA=='),
    lambda r: r['observations'][0]['responseChunks'][0].__setitem__('sha256', '0' * 64),
    lambda r: r['observations'][0].__setitem__('bodyEofObserved', False),
    lambda r: r['observations'][0].__setitem__('terminalNs', '0'),
    lambda r: r.__setitem__('schemaVersion', True),
    lambda r: r.__setitem__('completionOrder', []),
]:
    negative = copy.deepcopy(positive)
    mutate(negative)
    refuses(lambda: c.capture_integrity(negative))
for mutate in [
    lambda r: r['observations'][0]['request']['headers'].__setitem__('x-fixture-probe', 'crossed'),
    lambda r: r['observations'][0].__setitem__('status', 500),
    lambda r: r['observations'][0].__setitem__('signalAborted', True),
    lambda r: r.__setitem__('schemaVersion', True),
    lambda r: r['uploadEvents'].append({'event': 'upload-cancelled', 'ns': '9'}),
]:
    negative = copy.deepcopy(positive)
    mutate(negative)
    check(c.supplemental_semantics(negative)['passed'] is False)
for marker in ['0', str(int(positive['completedNs']) + 1000000)]:
    negative = copy.deepcopy(positive)
    negative['phaseOneTerminalNs'] = marker
    refuses(lambda: c.additional_ordering(negative))
negative = copy.deepcopy(positive)
negative['chunkedRequest']['body']['sha256'] = '0' * 64
refuses(lambda: c.additional_ordering(negative))
for text in ['{"a":1,"a":2}', '{"a":NaN}']:
    refuses(lambda: c.loads(text))
for text in ['AA', 'AA==\n', '!!!', 'AB==']:
    refuses(lambda: c.b64(text))
for text in ['１', '١', '1\n', '-1', '1.0']:
    refuses(lambda: c.ns(text))
for value in [0, False, '']:
    negative = copy.deepcopy(positive)
    negative['observations'][0]['error'] = value
    check(c.supplemental_semantics(negative)['passed'] is False)
    refuses(lambda: c.capture_integrity(negative))

# Strict raw0 acceptance is separate from ownership cleanup; these are inert dictionaries.
base = dict(rawExitCode=0, timeout=False, forcedCleanup=False, parentOwnedGroupGone=True,
            allObservedOwnedGroupsGone=True, errors=[], signals=[], interruptedSignals=[],
            remainingObservedPids=[], finalGroups=[{'alive': False}])
check(c.clean_status(base))
check(pure['clean'](base))
raw1 = dict(base, rawExitCode=1)
check(c.clean_status(raw1))
check(pure['clean'](raw1) is False)
for key, value in [('rawExitCode', True), ('rawExitCode', 1), ('timeout', True),
                   ('forcedCleanup', True), ('parentOwnedGroupGone', False),
                   ('allObservedOwnedGroupsGone', False), ('errors', ['x']),
                   ('signals', [15]), ('interruptedSignals', [2]),
                   ('interruptedSignals', [15]), ('remainingObservedPids', [1]),
                   ('finalGroups', [{'alive': True}])]:
    check(pure['clean'](dict(base, **{key: value})) is False)

for arm in ['native', 'stock']:
    template = reader.json_ref(roles[arm + 'AuthorityTemplate'])
    c.validate_authority(template, template, arm)
    count += 1
    for mutation in ['runId', 'sourceIndex', 'permission']:
        value = copy.deepcopy(template)
        if mutation == 'runId':
            value['runId'] = 'bad\n'
        elif mutation == 'sourceIndex':
            value['sourceIndex']['sha256'] = '0' * 64
        else:
            value['browserAllowed'] = False
        refuses(lambda: c.validate_authority(value, template, arm))

# The retained local-fake-server monitor is genuine Source-test DATA, not an
# eligible application arm. Exercise the generic original-monitor join only.
monitor_root = root / 'checks' / 'fake-http-owned-v2'
terminal_ref = reader.data(monitor_root / 'terminal.json')
terminal = reader.json_ref(terminal_ref)
started = reader.read(monitor_root / 'started.json')
check(c.monitor_records(reader, terminal_ref, terminal['authority'], started['argv'], 90)[0] == terminal)


class AlteredMonitor:
    def __init__(self, t, s):
        self.terminal, self.started = t, s
    def json_ref(self, reference):
        assert reference == terminal_ref
        return self.terminal
    def read(self, path):
        if Path(path).name == 'started.json':
            return self.started
        return reader.read(path)
    def ref(self, reference):
        return reader.ref(reference)


for key, value in [('rawExitCode', 1), ('rawExitCode', True), ('interruptedSignals', [15]),
                   ('timeout', True), ('forcedCleanup', True), ('errors', ['bad']),
                   ('allObservedOwnedGroupsGone', False), ('observedProcesses', [])]:
    t = dict(terminal, **{key: value})
    refuses(lambda: c.monitor_records(AlteredMonitor(t, started), terminal_ref, terminal['authority'], started['argv'], 90))
for key, value in [('argv', ['fake']), ('timeoutSeconds', 300), ('pid', 0), ('authority', {})]:
    s = dict(started, **{key: value})
    refuses(lambda: c.monitor_records(AlteredMonitor(terminal, s), terminal_ref, terminal['authority'], started['argv'], 90))

# Source-derived namespace examples use the ACTUAL owner expressions, not an
# invented expected parent record. No owner main or actor is imported/called.
for arm in ['native', 'stock']:
    plan = reader.json_ref(roles[arm + 'Plan'])
    here = Path(roles[arm + 'Source']['path']).parent
    owner = ast.parse((here / 'run-owned.py').read_text())
    run_id = 'data-only-wire-example'
    if arm == 'native':
        output_assign = next(n for n in ast.walk(owner) if isinstance(n, ast.Assign)
                             and any(isinstance(t, ast.Name) and t.id == 'output' for t in n.targets))
        actual = eval(compile(ast.Expression(output_assign.value), '<actual-native-owner-output-expression>', 'eval'),
                      {'Path': Path, 'plan': plan, 'run_id': run_id})
    else:
        fn = next(n for n in owner.body if isinstance(n, ast.FunctionDef) and n.name == 'derive_invocation')
        scope = {'Path': Path, 're': re}
        exec(compile(ast.Module(body=[fn], type_ignores=[]), '<actual-stock-owner-derive>', 'exec', optimize=0), scope)
        authority = copy.deepcopy(reader.json_ref(roles['stockAuthorityTemplate']))
        authority['runId'] = run_id
        actual, monitor, argv = scope['derive_invocation'](authority, plan, here)
        check(monitor == Path(str(actual) + '-monitor'))
        check(argv == [plan['node']['path'], str(here / 'run-stock.mjs'), str(actual), plan['standaloneSource'], plan['browserTools'], run_id])
    check(c.runtime_paths(plan, run_id, arm)[0] == actual)
    check(c.runtime_paths(plan, run_id, arm)[1] == Path(str(actual) + ('-external-root' if arm == 'native' else '-monitor')))
    for bad in ['bad\n', '../bad', 'x/../y', 'A', '', 'x' * 49]:
        refuses(lambda: c.runtime_paths(plan, bad, arm))
check(c.js_json_equal(True, 1) is False)
check(c.js_json_equal(False, 0) is False)
check(c.js_json_equal(1, 1.0))
check(c.js_json_equal({'x': True}, {'x': 1}) is False)
check(c.js_json_equal([None, True], [None, 1]) is False)
# Reproduce C's actual old-pass/new-refuse permission typing counterexamples.
reader.family(roles['preservedCheckerV1'])
old_tree = ast.parse((Path(roles['preservedCheckerV1']['path']).parent / 'check.py').read_text())
old_scope = {'re': re}
old_defs = [n for n in old_tree.body if isinstance(n, ast.FunctionDef) and n.name in ['require', 'validate_authority']]
exec(compile(ast.Module(body=old_defs, type_ignores=[]), '<held-v1-authority-predicate>', 'exec', optimize=0), old_scope)
for arm, field in [('native', 'localhostServeAllowed'), ('stock', 'browserAllowed')]:
    template = reader.json_ref(roles[arm + 'AuthorityTemplate'])
    negative = copy.deepcopy(template)
    negative[field] = 1
    old_scope['validate_authority'](negative, template, arm)
    count += 1
    refuses(lambda: c.validate_authority(negative, template, arm))

# Re-evaluate original gates against the sealed first-pair *retained DATA*.
# Test-only originalContractPassed=True supplies the later V8/V6 conjunction field;
# it does not turn these older records into a V8/V6 actual pair.
bundle_root = Path(roles['pureReaderIndex']['path']).parent
manifest = c.loads((bundle_root / 'evidence-index.json').read_bytes())
blobs = {k: base64.b64decode(v, validate=True) for k, v in c.loads(gzip.decompress((bundle_root / 'evidence.json.gz').read_bytes()))['blobs'].items()}
rows = {r['path']: r for r in manifest['files']}
origins = {r['origin']: r for r in manifest['files']}


class RetainedReader:
    def __init__(self):
        self.override = {}
    def value(self, path):
        if str(path) in self.override:
            return self.override[str(path)]
        return blobs[origins[str(path)]['sha256']]
    def data(self, path):
        b = self.value(path)
        return dict(path=str(path), sha256=c.sha(b), bytes=len(b))
    def read(self, path):
        return c.loads(self.value(path))
    def ref(self, descriptor):
        assert self.data(descriptor['path']) == descriptor
        return self.value(descriptor['path'])
    def json_ref(self, descriptor):
        return c.loads(self.ref(descriptor))


ret = RetainedReader()
old_path = rows['actual/native/client/result.json']['origin']
old_client = ret.read(old_path)
old_client['originalContractPassed'] = True
old_root = Path(old_path).parent
check(c.original_contract(ret, old_client, old_root, pure, roles)['http'] == 24)
for mutation in ['original', 'http-inventory', 'body-hash', 'cache', 'stream', 'browser']:
    client = copy.deepcopy(old_client)
    altered = RetainedReader()
    if mutation == 'original':
        client['originalContractPassed'] = False
    elif mutation == 'http-inventory':
        client['http'].pop()
    elif mutation == 'body-hash':
        client['http'][0]['bodySha256'] = '0' * 64
    elif mutation == 'cache':
        client['cacheInvalidation']['after']['generation'] = client['cacheInvalidation']['before']['generation']
    elif mutation == 'stream':
        client['streaming']['incrementalDeliveryObserved'] = False
    else:
        client['browser']['failedrequests'].append({'failure': {'errorText': 'net::ERR_ABORTED'}})
        altered.override[str(old_root / 'browser' / 'result.json')] = json.dumps(client['browser']).encode()
    refuses(lambda: c.original_contract(altered, client, old_root, pure, roles))

# Current genuine older-generation wire audit, explicitly NOT pair admission.
# NativeV7 Source and StockV4 lack the new six-case cohort and remain ineligible.
wire = c.Reader()
native = wire.json_ref(policy['wireTests']['nativeResult'])
native_authority = wire.json_ref(native['rootAuthority'])
old_native_plan = wire.json_ref(native_authority['plan'])
c.native_joins(wire, native_authority, native, policy['wireTests']['nativeWorld']['path'], old_native_plan, policy['fixed'])
count += 1
stock_observation = wire.json_ref(policy['wireTests']['stockObservation'])
stock = wire.json_ref(stock_observation['result'])
stock['originalContractPassed'] = True  # later field is test-only; no V6 reinterpretation
check(c.original_contract(wire, stock, Path(stock_observation['outputRoot']), pure, roles)['http'] == 24)
wire_terminal = wire.json_ref(stock_observation['terminal'])
stock_authority = wire.json_ref(wire_terminal['authority'])
stock_plan = wire.json_ref(stock_authority['plans'])
old_stock_here = Path(stock_authority['sourceIndex']['path']).parent
stock_argv = [stock_plan['node']['path'], str(old_stock_here / 'run-stock.mjs'), stock_observation['outputRoot'], stock_plan['standaloneSource'], stock_plan['browserTools'], stock_authority['runId']]
check(c.monitor_records(wire, stock_observation['terminal'], wire_terminal['authority'], stock_argv, 300)[0]['rawExitCode'] == 0)
check(wire.finish() > 0)

# Actual pair command must refuse missing evidence and genuine retained Source-test
# monitors (90s fake-server command, not either selected actor/Root chain).
for path in [HERE / 'no-actual-observation.json', root / 'checks' / 'fake-http-owned-v2' / 'terminal.json']:
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        code = c.main(['pair', '--native-observation', str(path), '--stock-observation', str(path), '--native-world-guard', str(path)])
    value = json.loads(output.getvalue())
    check(code == 1 and value['pairAdmission'] is False and value['actorOrNetworkExecuted'] is False)

check(reader.finish() > 0)
print(json.dumps(dict(schemaVersion=1, passed=True, inertChecks=count,
                     retainedSourceFakeCaptures=4, retainedOriginalContractData=1, genuineOlderNativeAndStockWireData=2,
                     actualPairExecuted=False, actualPairModeTested=False,
                     actorNetworkBrowserOrGuestExecuted=False)))
