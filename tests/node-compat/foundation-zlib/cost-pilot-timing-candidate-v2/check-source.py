"""Thin correction source/DATA checker. No operational helper or worker calls."""
from pathlib import Path
import hashlib
import json
import re
import subprocess

D = Path(__file__).resolve().parent
Z = D.parent
A = Z / 'cost-pilot-timing-candidate-v1'
H = Z / 'independent-cost-pilot-timing-source-review-v1'
inputs = {}
checks = []

def need(ok, message):
    if not ok:
        raise AssertionError(message)
    checks.append(message)

def load(path):
    return json.loads(Path(path).read_text())

def desc(path):
    path = Path(path)
    need(path.is_file() and not path.is_symlink(), 'regular file')
    before = path.stat()
    value = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            value.update(block)
    after = path.stat()
    need((before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns) == (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns), 'stable hash read')
    return {'path': str(path), 'sha256': value.hexdigest(), 'bytes': after.st_size}

def verify(row):
    need(desc(row['path']) == {key: row[key] for key in ['path', 'sha256', 'bytes']}, 'exact descriptor ' + row['path'])
    if not Path(row['path']).is_relative_to(D):
        inputs[row['path']] = row

def write(name, value):
    with (D / name).open('x') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')

def family(root, expected):
    ix = desc(root / 'index.json')
    need(ix['sha256'] == expected, 'unchanged sealed ancestor ' + str(root))
    inputs[ix['path']] = ix
    rows = load(root / 'index.json')['files']
    for row in rows:
        verify({'path': str(root / row['path']), 'sha256': row['sha256'], 'bytes': row['bytes']})
    need(sorted(str(p.relative_to(root)) for p in root.rglob('*') if p.is_file()) == sorted([row['path'] for row in rows] + ['index.json']), 'exact ancestor membership')

family(A, '55db1fc3895a0dbd10ca07e08c59bd68da8edeb9793632c8e05cb41704c5135b')
family(H, '1a2148e89e8018ada23d48b0a2225e2203c51272eeb722933b7842a0c6f48aa1')
need(load(H / 'results.json')['sourceReviewPassed'] is False, 'formal old HOLD not relabeled')
need(load(H / 'required-correction-contract.json')['findingId'] == 'ZLIB-COST-PILOT-TIMING-V1-M1', 'exact M1 correction contract')
for row in load(A / 'source-inputs.json')['files']:
    verify(row)
for record in load(D / 'source-derivations.json')['files']:
    verify(record['origin'])
    original = Path(record['origin']['path']).read_text()
    source = original
    for edit in record['edits']:
        need(source.count(edit['old']) == 1, 'singleton thin edit')
        at = source.index(edit['old'])
        need(at == edit['afterOffsetAtEdit'], 'exact thin forward offset')
        source = source[:at] + edit['new'] + source[at + len(edit['old']):]
    need(source == (D / record['afterimage']).read_text(), 'exact thin afterimage')
    back = source
    for edit in reversed(record['edits']):
        at = edit['afterOffsetAtEdit']
        need(back[at:at + len(edit['new'])] == edit['new'], 'exact thin reverse segment')
        back = back[:at] + edit['old'] + back[at + len(edit['new']):]
    need(back == original, 'held donor fully reconstructed')
    need(hashlib.sha256(source.encode()).hexdigest() == record['afterSha256'], 'recorded thin source digest')

static = re.compile(r"(?m)^\s*(?:import|export)\s+[^\n]*?\sfrom\s*['\"]([^'\"\n]+)['\"]|^\s*import\s*['\"]([^'\"\n]+)['\"]")
modules = {}
edges = []
pending = [D / 'worker.mjs']
seen = set()
while pending:
    path = pending.pop().resolve()
    if path in seen:
        continue
    seen.add(path)
    row = desc(path)
    modules[str(path)] = row
    if not path.is_relative_to(D):
        inputs[str(path)] = row
    for match in static.finditer(path.read_text()):
        spec = match.group(1) or match.group(2)
        if spec.startswith('node:'):
            edges.append({'from': str(path), 'specifier': spec, 'role': 'public Node harness API'})
        else:
            need(spec.startswith('.'), 'no new package/provider module')
            target = (path.parent / spec).resolve()
            need(target.is_file(), 'actual physical import edge')
            edges.append({'from': str(path), 'specifier': spec, 'target': str(target)})
            pending.append(target)
deps = sorted([row for row in modules.values() if not Path(row['path']).is_relative_to(D)], key=lambda r: r['path'])
need(len(deps) <= 256 and all(row['bytes'] <= 4 * 1024 * 1024 for row in deps), 'compact exact worker source dependencies')
write('worker-dependencies.json', {'schemaVersion': 1, 'state': 'THIN_V2_EXACT_WORKER_SOURCE_CLOSURE', 'files': deps, 'genuinePreflightExecutedByWorker': False})
write('module-edges.json', {'schemaVersion': 1, 'modules': [modules[k] for k in sorted(modules)], 'edges': edges, 'scope': 'Concrete worker static graph; parent inherits exact genuine source/API closures through held source.'})

refs = load(D / 'references.json')
all_rows = {}
def nested(value):
    if isinstance(value, dict):
        if set(value) >= {'path', 'sha256', 'bytes'} and type(value['bytes']) is int:
            row = {key: value[key] for key in ['path', 'sha256', 'bytes']}
            all_rows[(row['path'], row['sha256'], row['bytes'])] = row
        for child in value.values():
            nested(child)
    elif isinstance(value, list):
        for child in value:
            nested(child)
for key in ['fullCorrectness', 'stockWasmtimeStrings', 'actualControlsProof']:
    result = load(refs[key]['result']['path'])
    contract = load(refs[key]['contract']['path'])
    nested([result, contract['requiredExactDescriptors']])
rows = [all_rows[k] for k in sorted(all_rows)]
need(len(rows) == 91, 'complete exact current nested descriptor population')
large = [row for row in rows if row['bytes'] > 64 * 1024 * 1024]
need(len(large) == 1 and large[0] == refs['node'], 'all legitimate current large rows: sole exact pinned Node')
for row in rows:
    verify(row)
write('nested-contract-rows.json', {'schemaVersion': 1, 'files': rows, 'largeRows': large, 'allCurrentLargeRowsEnumerated': True, 'arbitraryFutureLargeRowsAccepted': False})
guard = (D / 'parent-guard.template.mjs').read_text()
need(guard.count('await verifyContractDescriptor(row)') == 2 and 'for(const row of referenced)await regular(row' not in guard, 'initial/recheck caller loops route to new verifier')
need("+'-v2'" in guard and "zlib-cost-measurement-plan-v2" in (D / 'prepare-plan.mjs').read_text(), 'fresh coherent v2 output namespaces')
for name in ['future-authority.template.json', 'future-plan-authority.template.json']:
    v = load(D / name)
    need(v['sourceIndexSha256'] is None and v['sourceIndependentReview'] is None, 'future exact source/source-peer slots null')
    need(v.get('actionAllowed', False) is False and v.get('dataPublicationAllowed', False) is False, 'no future action authority')

env = {'PATH': '/usr/bin:/bin:/usr/sbin:/sbin', 'LANG': 'C', 'LC_ALL': 'C', 'TZ': 'UTC', 'RAYON_NUM_THREADS': '1', 'BINARYEN_CORES': '1', 'CARGO_BUILD_JOBS': '1', 'PYTHONDONTWRITEBYTECODE': '1'}
E = D / 'evidence'
E.mkdir(exist_ok=False)
syntax = []
for path in sorted(D.glob('*.mjs')):
    outcome = subprocess.run([refs['node']['path'], '--check', str(path)], env=env, capture_output=True)
    syntax.append({'file': path.name, 'rawExitCode': outcome.returncode, 'stderr': outcome.stderr.decode()})
    need(outcome.returncode == 0, 'source syntax ' + path.name)
(E / 'syntax.json').write_text(json.dumps(syntax, indent=2) + '\n')
outcome = subprocess.run([refs['node']['path'], str(D / 'test-contract-descriptors.mjs')], env=env, capture_output=True)
(E / 'regression.stdout.log').write_bytes(outcome.stdout)
(E / 'regression.stderr.log').write_bytes(outcome.stderr)
need(outcome.returncode == 0 and not outcome.stderr, 'actual read/hash-only descriptor regression passes')
regression = json.loads(outcome.stdout)
need(regression['checks'] == 17 and regression['actualUniqueDescriptors'] == 91 and regression['actualInitialAndPrivateRecheckPassed'] is True, 'genuine nested lists and private recheck exercised')
write('source-inputs.json', {'schemaVersion': 1, 'files': [inputs[k] for k in sorted(inputs)], 'heldSourceAndAllOriginalInputsPreserved': True, 'genuineOwnerPreflightHelperWorkerExecuted': False})
write('source-checks.json', {'schemaVersion': 1, 'state': 'THIN_V2_STREAMED_DESCRIPTOR_SOURCE_DATA_CHECKS_PASSED', 'checks': len(checks), 'regressionChecks': 17, 'syntaxFiles': len(syntax), 'inputFiles': len(inputs), 'workerDependencies': len(deps), 'actualNestedDescriptors': 91, 'actualReadHashRecheckPassed': True, 'newHostLifecycleOrPreflightGuestProviderCodecNativeJcoWasmtimePilotTimingExecuted': False, 'operationalAdmission': False})
print(json.dumps(load(D / 'source-checks.json')))
