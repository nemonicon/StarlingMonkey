"""Independent read/hash/DATA audit. Does not import any reviewed JS or helper."""
from pathlib import Path
import hashlib
import json
import os
import stat

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / 'cost-pilot-timing-candidate-v1'
EXPECTED = '55db1fc3895a0dbd10ca07e08c59bd68da8edeb9793632c8e05cb41704c5135b'
verified = {}
checks = []


def need(value, message):
    if not value:
        raise AssertionError(message)
    checks.append(message)


def digest(path):
    path = Path(path)
    before = path.lstat()
    need(stat.S_ISREG(before.st_mode) and not path.is_symlink(), 'ordinary leaf ' + str(path))
    key = str(path)
    identity = (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns)
    if key in verified:
        need(verified[key]['identity'] == identity, 'unchanged already-read identity')
        return verified[key]['descriptor']
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            h.update(block)
    after = path.lstat()
    need(identity == (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns), 'stable hash read')
    row = {'path': key, 'sha256': h.hexdigest(), 'bytes': before.st_size}
    verified[key] = {'descriptor': row, 'identity': identity}
    return row


def verify(row):
    expected = {k: row[k] for k in ('path', 'sha256', 'bytes')}
    need(digest(row['path']) == expected, 'exact file ' + row['path'])
    return expected


def load(path):
    def pairs(items):
        result = {}
        for k, v in items:
            need(k not in result, 'no duplicate JSON member')
            result[k] = v
        return result
    return json.loads(Path(path).read_bytes(), object_pairs_hook=pairs)


def descs(v):
    found = {}
    def walk(x):
        if isinstance(x, dict):
            if isinstance(x.get('path'), str) and isinstance(x.get('sha256'), str) and type(x.get('bytes')) is int:
                row = {k: x[k] for k in ('path', 'sha256', 'bytes')}
                found[json.dumps(row, sort_keys=True)] = row
            for y in x.values():
                walk(y)
        elif isinstance(x, list):
            for y in x:
                walk(y)
    walk(v)
    return list(found.values())


def member_names(root):
    files = []
    for parent, dirs, names in os.walk(root, followlinks=False):
        for name in dirs:
            p = Path(parent) / name
            need(not p.is_symlink(), 'no packet directory symlink')
        for name in names:
            p = Path(parent) / name
            need(p.is_file() and not p.is_symlink(), 'ordinary packet member')
            files.append(str(p.relative_to(root)))
    return sorted(files)


def index(row, completion=False):
    verify(row)
    root = Path(row['path']).parent
    v = load(row['path'])
    need(v['schemaVersion'] == 1 and isinstance(v['files'], list), 'finite indexed schema')
    names = []
    rows = []
    for r in v['files']:
        name = r['path']
        need(not name.startswith('/') and all(p not in ('', '.', '..') for p in name.split('/')), 'local index path')
        need(name not in names, 'unique index member')
        names.append(name)
        absolute = {'path': str(root / name), 'sha256': r['sha256'], 'bytes': r['bytes']}
        verify(absolute)
        rows.append(absolute)
    expected = names + ['index.json'] + (['completion.json'] if completion else [])
    need(member_names(root) == sorted(expected), 'complete exact index membership ' + str(root))
    return rows


own = digest(SOURCE / 'index.json')
need(own['sha256'] == EXPECTED and own['bytes'] == 15141, 'actual final immutable 55db seal')
own_rows = index(own)
need(len(own_rows) == 85, 'all85 source members')
inputs = load(SOURCE / 'source-inputs.json')['files']
need(len(inputs) == 699 and len({r['path'] for r in inputs}) == 699, 'all699 finite preparation inputs')
for row in inputs:
    verify(row)
need(all(r['bytes'] < 4 * 1024 * 1024 for r in own_rows), 'all own worker intake files fit actual4MiB bound')

derivations = load(SOURCE / 'successor-derivations.json')['files']
edit_count = 0
for item in derivations:
    verify(item['origin'])
    before = Path(item['origin']['path']).read_bytes()
    after = (SOURCE / item['afterimage']).read_bytes()
    data = before
    for edit in item['edits']:
        old, new, at = edit['old'].encode(), edit['new'].encode(), edit['afterOffsetAtEdit']
        need(data.count(old) == 1 and data.find(old) == at, 'single exact derivation offset')
        data = data[:at] + new + data[at + len(old):]
        edit_count += 1
    need(data == after and hashlib.sha256(after).hexdigest() == item['afterSha256'], 'exact derived afterimage')
    for edit in reversed(item['edits']):
        old, new, at = edit['old'].encode(), edit['new'].encode(), edit['afterOffsetAtEdit']
        need(data[at:at + len(new)] == new, 'exact reverse segment')
        data = data[:at] + old + data[at + len(new):]
    need(data == before, 'complete original donor reconstructed')
need(len(derivations) == 2 and edit_count == 35, 'two actual donor derivations35 exact edits')

refs = load(SOURCE / 'references.json')
for row in descs(refs):
    verify(row)
proofs = {}
oversize = []
actual_output_members = {}
for name in ['fullCorrectness', 'stockWasmtimeStrings', 'actualControlsProof']:
    p = refs[name]
    members = index(p['index'])
    need(sum(r == p['result'] for r in members) == 1 and sum(r == p['contract'] for r in members) == 1, 'result and stable contract each indexed once')
    v, c = load(p['result']['path']), load(p['contract']['path'])
    need(v['schemaVersion'] == 1 and v['verifiedPassed'] is True and c['requiredReviewState'] == v['state'], 'genuine existing proof state')
    for k, wanted in c.get('requiredFixedValues', {}).items():
        need(v[k] == wanted, 'actual pinned fixed proof field ' + k)
    for k, wanted in c.get('requiredCoverage', {}).items():
        need(v['coverage'][k] == wanted, 'actual pinned coverage ' + k)
    for row in descs([v, c.get('requiredExactDescriptors', {})]):
        verify(row)
        if row['bytes'] > 64 * 1024 * 1024:
            oversize.append({'proof': name, **row, 'sourceRegularMaxBytes': 64 * 1024 * 1024, 'actualSizePredicatePasses': False})
    for row in c.get('requiredExactDescriptors', {}).values():
        need(row in descs(v) or row in members, 'required descriptor actually bound')
    if 'requiredComponents' in c:
        need(v.get('components', v.get('requiredComponents')) == c['requiredComponents'], 'actual three component bindings')
    if 'requiredActualComponentReviews' in c:
        need(v.get('actualComponentReviews', v.get('requiredActualComponentReviews')) == c['requiredActualComponentReviews'], 'actual three artifact proof bindings')
    if 'actualIndex' in v:
        actual_output_members[name] = len(index(v['actualIndex'], completion=True))
    proofs[name] = {'state': v['state'], 'index': p['index'], 'result': p['result'], 'contract': p['contract']}
need(len(oversize) == 1 and oversize[0]['path'] == refs['node']['path'] and oversize[0]['bytes'] == 108619024, 'sole actual M1 oversized binary is pinned Node108619024')
guard = (SOURCE / 'parent-guard.template.mjs').read_text()
regular = (SOURCE.parent / 'cost-jco-correctness-candidate-v2/authority.mjs').read_text()
need('for(const row of referenced)await regular(row,{maxBytes:64*1024*1024})' in guard, 'genuine first-read64MiB call seam')
need('for(const row of referenced)await regular(row,{maxBytes:64*1024*1024});if(actualNames)' in guard, 'same genuine recheck64MiB seam')
need('row.bytes<=maxBytes' in regular, 'actual regular predicate rejects oversized input before read')

benign = load(SOURCE / 'benign-lifecycle-evidence.json')
for r in benign['sourceBindings']:
    verify(r)
for entry in benign['copies']:
    verify(entry['original'])
    c = entry['copy']
    verify({'path': str(SOURCE / c['path']), 'sha256': c['sha256'], 'bytes': c['bytes']})
benign_root = Path(benign['successfulRoot'])
success_index = digest(benign_root / 'index.json')
need(success_index['sha256'] == '09261426248c94eed6d84b1a5235cc9bd1134ba34989adfc3d928e30903e42c3', 'exact actual benign suite index')
benign_members = index(success_index, completion=True)
benign_results = load(benign_root / 'results.json')
outcomes = {}
for item in benign_results['outcomes']:
    v = load(item['terminal'])
    for r in [v['stdout'], v['stderr']]:
        verify(r)
    need(v['ownedGroupGone'] is True and v['closed'] is True and v['stderr']['bytes'] == 0, 'actual benign terminal/cleanup/empty stderr')
    mode = item['mode']
    if mode == 'normal':
        need(v['status'] == 0 and v['terminalExitZeroObserved'] is True and not v['signals'] and not v['errors'], 'actual normal ACK/end clean0')
    elif mode == 'unfinished-raw0':
        need(v['status'] == 0 and v['terminalExitZeroObserved'] is False and any('incomplete public-call' in e.get('message', '') for e in v['errors']), 'actual unfinished end raw0 refused')
    else:
        need(mode == 'blocking' and v['publicCallTimeoutMs'] == 100 and v['timedOut'] is True and v['signal'] == 'SIGKILL' and any(s['signal'] == 'SIGKILL' for s in v['signals']), 'external100ms fake-call termination')
        need(not (benign_root / 'jobs/blocking/raw.json').exists(), 'interrupted fake-call has no completed raw return')
    outcomes[mode] = {k: v[k] for k in ['pid', 'status', 'signal', 'timedOut', 'publicCallTimeoutMs', 'ownedGroupGone', 'errors', 'signals', 'terminalExitZeroObserved', 'operationalElapsedMs']}
need(set(outcomes) == {'normal', 'unfinished-raw0', 'blocking'}, 'exact three benign modes')
for attempt, expected in [('benign-host-v1', 1), ('benign-host-v2', 0)]:
    t = load(SOURCE / 'evidence' / attempt / 'terminal.json')
    need(t['rawExitCode'] == expected and t['timeout'] is False, 'preserved driver outcome ' + attempt)
    verify(t['stdout']); verify(t['stderr'])
need('Ordinary acyclic JSON only' in (SOURCE / 'evidence/benign-host-v1/stderr.log').read_text(), 'first evidence-writer failure retained')

cases = load(refs['cases']['path'])
need(len(cases) == 30 and [c['index'] for c in cases] == list(range(30)), 'all30 original ordered cases')
need([c['timingNMax'] for c in cases] == [32768]*18 + [128]*12, 'unchanged original operation caps')
schedule = []
for comparison, a, b in [('same-engine-provider', 'native-on', 'fflate-on'), ('unused-profile', 'fflate-on', 'fflate-off')]:
    for case in range(30):
        for repetition in range(3):
            for arm in ([b, a] if repetition == 1 else [a, b]):
                schedule.append((comparison, case, repetition, arm))
need(len(schedule) == 360 and len(set(schedule)) == 360, '360 fresh timing units independently recomputed')
need(len(schedule)*10 == 3600 and len(schedule)*6 == 2160, '3600 codec batches2160 nonsubtracted controls')
pilot_pairs = 2*(18*16+12*8)
need(pilot_pairs == 768 and pilot_pairs*2 == 1536 and pilot_pairs*2*6 == 9216, 'maximum geometric pilot counts recomputed')
protocol = load(refs['originalProtocol']['path'])
need(protocol['sampling']['order'] == 'AB/BA/AB' and protocol['measurement']['controlsSubtracted'] is False, 'actual original paired order and no subtraction')
need(protocol['measurement']['emptyByteThroughput'] is None and protocol['measurement']['emptyOutputRatio'] is None, 'honest empty metrics')
calibration = load(refs['calibrationDecision']['path'])
need(calibration['candidateOrder'] == 'A then B; both arms get fresh workers at every candidate N' and calibration['timingPopulationUnchanged']['workers'] == 360, 'actual Root source-only refinement')
for name in ['future-authority.template.json', 'future-phase-authority.template.json', 'future-plan-authority.template.json', 'future-quiet-window.template.json']:
    v = load(SOURCE / name)
    need(v['sourceIndexSha256'] is None, 'future exact source remains null')
    for k in ['actionAllowed', 'dataPublicationAllowed', 'exclusiveMeasurementApproved']:
        if k in v:
            need(v[k] is False, 'future action remains false')

module_edges = load(SOURCE / 'module-edges.json')
for r in module_edges['modules']:
    verify(r)
worker_deps = load(SOURCE / 'worker-dependencies.json')['files']
need(len(worker_deps) == 11 and all(r['bytes'] < 4*1024*1024 for r in worker_deps), 'small11 physical worker dependencies')
for r in worker_deps:
    verify(r)
need(load(SOURCE / 'source-checks.json')['pureMockChecks'] == 90, 'stored owner90pure checks authenticated only')
summary = {
    'schemaVersion': 1,
    'state': 'INDEPENDENT_SOURCE_DATA_REVIEW_COMPLETED_WITH_M1_HOLD',
    'sourceIndex': own, 'sourceMembers': len(own_rows), 'preparationInputs': len(inputs),
    'uniquePathsHashed': len(verified), 'stableReadChecks': len(checks),
    'derivationFiles': len(derivations), 'exactForwardAndReverseEdits': edit_count,
    'actualOutputMembersRehashedAsDataOnly': actual_output_members,
    'existingProofContracts': proofs,
    'actualBenignSuiteIndex': success_index, 'actualBenignSuiteIndexedMembers': len(benign_members),
    'benignSourceCopies': len(benign['copies']), 'benignOutcomes': outcomes,
    'timingMath': {'workers': 360, 'codecBatchCalls': 3600, 'separateN1ControlCalls': 2160,
        'maxPilotPairs': 768, 'maxPilotWorkers': 1536, 'maxPilotN1Controls': 9216},
    'findingM1': oversize,
    'ownerActionsInvokedByReviewer': False,
    'reviewerScope': 'Independent Python read/hash/data/source review only. No owner module or helper imported/executed; no Node, provider, codec, Jco, WT, guest, pilot or timing.'
}
with (HERE / 'read-results.json').open('x') as out:
    json.dump(summary, out, indent=2)
    out.write('\n')
with (HERE / 'verified-inputs.json').open('x') as out:
    json.dump({'schemaVersion': 1, 'files': [verified[p]['descriptor'] for p in sorted(verified)]}, out, indent=2)
    out.write('\n')
print(json.dumps({k: summary[k] for k in ['state', 'sourceMembers', 'preparationInputs', 'uniquePathsHashed', 'stableReadChecks', 'exactForwardAndReverseEdits']}))
