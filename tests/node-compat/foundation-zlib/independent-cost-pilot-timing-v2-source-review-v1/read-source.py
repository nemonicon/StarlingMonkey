"""Independent finite source/data reader; no reviewed module/helper execution."""
from pathlib import Path
import hashlib
import json
import os
import stat

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / 'cost-pilot-timing-candidate-v2'
SHA = '1a294044a4f2414d35fdd817dae95598c2e079aa64a9044737f4791aefe630a2'
seen = {}
checks = []


def need(ok, label):
    if not ok:
        raise AssertionError(label)
    checks.append(label)


def load(path):
    def pairs(rows):
        result = {}
        for k, v in rows:
            need(k not in result, 'unique JSON key')
            result[k] = v
        return result
    return json.loads(Path(path).read_bytes(), object_pairs_hook=pairs)


def hash_file(path):
    p = Path(path)
    a = p.lstat()
    need(stat.S_ISREG(a.st_mode) and not p.is_symlink(), 'ordinary read leaf')
    identity = (a.st_dev, a.st_ino, a.st_size, a.st_mtime_ns, a.st_ctime_ns)
    if str(p) in seen:
        need(seen[str(p)]['identity'] == identity, 'stable prior path identity')
        return seen[str(p)]['descriptor']
    h = hashlib.sha256()
    with p.open('rb') as stream:
        for b in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            h.update(b)
    z = p.lstat()
    need(identity == (z.st_dev, z.st_ino, z.st_size, z.st_mtime_ns, z.st_ctime_ns), 'stable streamed hash')
    r = {'path': str(p), 'sha256': h.hexdigest(), 'bytes': z.st_size}
    seen[str(p)] = {'descriptor': r, 'identity': identity}
    return r


def verify(r):
    need(hash_file(r['path']) == {k: r[k] for k in ('path', 'sha256', 'bytes')}, 'exact descriptor ' + r['path'])


def index(row):
    verify(row)
    root = Path(row['path']).parent
    v = load(row['path'])
    need(v['schemaVersion'] == 1 and isinstance(v['files'], list), 'finite source inventory')
    names = []
    for r in v['files']:
        n = r['path']
        need(not n.startswith('/') and all(x not in ('', '.', '..') for x in n.split('/')) and n not in names, 'unique local member')
        names.append(n)
        verify({'path': str(root / n), 'sha256': r['sha256'], 'bytes': r['bytes']})
    files = []
    for parent, dirs, leaves in os.walk(root, followlinks=False):
        for n in dirs:
            need(not (Path(parent)/n).is_symlink(), 'ordinary source directory')
        for n in leaves:
            p = Path(parent)/n
            need(p.is_file() and not p.is_symlink(), 'ordinary source member')
            files.append(str(p.relative_to(root)))
    need(sorted(files) == sorted(names+['index.json']), 'complete exact packet membership')
    return v['files']


def descriptors(v):
    rows = {}
    def walk(x):
        if isinstance(x, dict):
            if isinstance(x.get('path'), str) and isinstance(x.get('sha256'), str) and type(x.get('bytes')) is int:
                row = {k: x[k] for k in ('path', 'sha256', 'bytes')}
                rows[json.dumps(row, sort_keys=True)] = row
            for y in x.values(): walk(y)
        elif isinstance(x, list):
            for y in x: walk(y)
    walk(v)
    return list(rows.values())


own = hash_file(SOURCE/'index.json')
need(own['sha256'] == SHA and own['bytes'] == 4460, 'final actual1a294 source seal')
own_rows = index(own)
need(len(own_rows) == 26, 'all26 own members')
inputs = load(SOURCE/'source-inputs.json')['files']
need(len(inputs) == 861 and len({r['path'] for r in inputs}) == 861, 'all861 finite input identities')
for r in inputs: verify(r)
inherited = load(SOURCE/'inherited-source.json')
need(inherited['heldSourceIndex']['sha256'] == '55db1fc3895a0dbd10ca07e08c59bd68da8edeb9793632c8e05cb41704c5135b', 'original55db unchanged')
need(inherited['formalHoldIndex']['sha256'] == '1a2148e89e8018ada23d48b0a2225e2203c51272eeb722933b7842a0c6f48aa1', 'originalHOLD1a21 unchanged')
need(len(index(inherited['heldSourceIndex'])) == 85, 'all85 held source members unchanged')
need(len(index(inherited['formalHoldIndex'])) == 8, 'all8 HOLD members unchanged')
old_inputs = load(inherited['inheritedOriginalInputFreeze']['path'])['files']
need(all(r in inputs for r in old_inputs), 'all original699 prep identities contained')
for r in descriptors(inherited): verify(r)

edits = 0
for item in load(SOURCE/'source-derivations.json')['files']:
    verify(item['origin'])
    before = Path(item['origin']['path']).read_bytes()
    data = before
    for e in item['edits']:
        old, new, at = e['old'].encode(), e['new'].encode(), e['afterOffsetAtEdit']
        need(data.count(old) == 1 and data.find(old) == at, 'exact unique forward offset')
        data = data[:at]+new+data[at+len(old):]
        edits += 1
    actual = (SOURCE/item['afterimage']).read_bytes()
    need(data == actual and hashlib.sha256(actual).hexdigest() == item['afterSha256'], 'exact successor afterimage')
    for e in reversed(item['edits']):
        old, new, at = e['old'].encode(), e['new'].encode(), e['afterOffsetAtEdit']
        need(data[at:at+len(new)] == new, 'exact reverse bytes')
        data = data[:at]+old+data[at+len(new):]
    need(data == before, 'exact donor restored')
need(edits == 22, 'four thin afterimages22 exact transformations')

refs = load(SOURCE/'references.json')
families = []
all_rows = {}
for name in ['fullCorrectness', 'stockWasmtimeStrings', 'actualControlsProof']:
    p = refs[name]
    for r in descriptors(p): verify(r)
    result, contract = load(p['result']['path']), load(p['contract']['path'])
    need(result['verifiedPassed'] is True and result['state'] == contract['requiredReviewState'], 'actual fixed proof state')
    rows = descriptors([result, contract['requiredExactDescriptors']])
    families.append({'name': name, 'descriptors': len(rows)})
    for r in rows:
        all_rows[json.dumps(r, sort_keys=True)] = r
actual = list(all_rows.values())
recorded = load(SOURCE/'nested-contract-rows.json')
need(sorted(actual, key=lambda r: json.dumps(r, sort_keys=True)) == sorted(recorded['files'], key=lambda r: json.dumps(r, sort_keys=True)), 'actual full nested lists exactly reconstructed')
need(len(actual) == 91 and sum(r['bytes'] for r in actual) == 306945530, '91 unique actual descriptors306945530 referenced bytes')
large = [r for r in actual if r['bytes'] > 67108864]
need(len(large) == 1 and large == recorded['largeRows'], 'only one current large role')
node = refs['node']
need(large == [node] and node['bytes'] == 108619024 and node['sha256'] == 'e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0', 'exact genuine Node executable tuple')
for r in actual: verify(r)
for r in actual: verify(r)
need(Path(node['path']).resolve() == Path(node['path'].replace('/private/tmp/', '/tmp/')).resolve(), 'known physical tmp alias only')
code = (SOURCE/'contract-descriptors.mjs').read_text()
guard = (SOURCE/'parent-guard.template.mjs').read_text()
need('if(row.bytes<=MAX_REGULAR_BYTES)' in code and 'maximumBytes:MAX_REGULAR_BYTES' in code, 'bounded regular64MiB kept')
need('canonicalAlias(row.path)===r.path&&row.sha256===r.sha256&&row.bytes===r.bytes' in code, 'large role requires exact canonical path/hash/size')
need('await streamHash(plan.row,{maximumBytes:plan.maximumBytes})' in code and 'const plan=descriptorReadPlan(value)' in code, 'captured exact finite streamed reader')
need('const rows=Object.freeze(values.map(descriptor))' in code and 'for(const row of rows)await verifyContractDescriptor(row)' in code, 'private immutable list recheck')
need(guard.count('await verifyContractDescriptor(row)') == 2 and 'referenced=[...captureProofDescriptors(v,c)]' in guard and 'for(const row of referenced)await regular(row' not in guard, 'both genuine initial and recheck caller loops corrected')
stream = (SOURCE.parent/'cost-tooling-candidate-v3/context.mjs').read_text()
need('createReadStream(row.path,{highWaterMark:1024*1024})' in stream and 'digest.digest(\'hex\')===row.sha256' in stream and 'info.ino===after.ino' in stream, 'existing streamed primitive checks bytes/hash/identity')

regression = load(SOURCE/'evidence/regression.stdout.log')
need(regression['checks'] == 17 and regression['actualUniqueDescriptors'] == 91 and regression['actualReferencedBytes'] == 306945530, 'stored actual-data regression17 authenticated')
need(regression['actualInitialAndPrivateRecheckPassed'] and regression['regularDescriptorCount'] == 90 and regression['streamedLargeDescriptorCount'] == 1, 'author exercised actual initial/read/recheck seam')
need(regression['unknownOversizedRolePathHashSizeRefused'] and regression['preflightAdmissionHelperWorkerGuestProviderCodecNativeJcoWasmtimePilotTimingExecuted'] is False, 'negative cases and explicit no-action scope')
test = (SOURCE/'test-contract-descriptors.mjs').read_text()
need('pending=verifyDescriptorList(mutable);mutable[0].path=' in test and 'await captured.recheck()' in test, 'real private-capture mutation check source')
need((SOURCE/'evidence/regression.stderr.log').read_bytes() == b'', 'stored regression stderr empty')
syntax = load(SOURCE/'evidence/syntax.json')
need(len(syntax) == 6 and all(r['rawExitCode'] == 0 for r in syntax), 'six stored grammar outcomes authenticated')

for n in ['inheritedLoader', 'inheritedPlanner', 'inheritedTypedCollector', 'inheritedOwnedLifecycle', 'inheritedBenignHostEvidence']:
    verify(inherited[n])
worker_deps = load(SOURCE/'worker-dependencies.json')['files']
need(len(worker_deps) == 19 and all(r['bytes'] < 4194304 for r in worker_deps), 'all19 small exact worker source dependencies')
for r in worker_deps: verify(r)
for r in load(SOURCE/'module-edges.json')['modules']: verify(r)
need('/zlib-cost-measurement-plan-v2' in (SOURCE/'prepare-plan.mjs').read_text(), 'fresh compact planv2 namespace')
need("+'-v2';" in guard, 'fresh phasev2 namespaces')
need("join(HERE,'worker.mjs')" in (SOURCE/'run.mjs').read_text(), 'new parent invokes ownv2 worker')
need("from './parent-guard.template.mjs'" in (SOURCE/'worker.mjs').read_text(), 'new worker binds actual ownv2 guard/HERE')
for n in ['future-authority.template.json', 'future-plan-authority.template.json']:
    v = load(SOURCE/n)
    need(v['sourceIndexSha256'] is None and v['sourceIndependentReview'] is None, 'future exact ownsource and source-peer remain null')
    for k in ['actionAllowed', 'dataPublicationAllowed']:
        if k in v: need(v[k] is False, 'future action remains false')
res = load(SOURCE/'results.json')
need(res['findingCorrectedInSource'] is True and res['protocolGuestNativeProvidersComponentsCapsLoaderCollectorOwnedLifecycleChanged'] is False and res['preflightWorkerGuestProviderCodecNativeJcoWasmtimePilotTimingExecuted'] is False, 'bounded correction scope no actions')

out = {'schemaVersion': 1, 'state': 'INDEPENDENT_READ_HASH_SOURCE_DATA_V2_CHECKS_PASSED',
       'sourceIndex': own, 'sourceMembers': len(own_rows), 'prepInputs': len(inputs),
       'uniquePathsRehashed': len(seen), 'checks': len(checks),
       'exactDerivationFiles': 4, 'exactForwardReverseEdits': edits,
       'inheritedSourceMembersUnchanged': 85, 'formalHoldMembersUnchanged': 8,
       'actualNestedProofFamilies': families, 'actualNestedDescriptors': len(actual),
       'actualNestedReferencedBytes': sum(r['bytes'] for r in actual),
       'onlyLargeDescriptor': node, 'smallDescriptors': 90,
       'actualAuthorReadHashTestsAuthenticatedOnly': 17,
       'reviewerOwnerFunctionsOrActionsInvoked': False}
with (HERE/'read-results.json').open('x') as f: json.dump(out,f,indent=2); f.write('\n')
with (HERE/'verified-inputs.json').open('x') as f:
    json.dump({'schemaVersion': 1, 'files': [seen[k]['descriptor'] for k in sorted(seen)]},f,indent=2); f.write('\n')
print(json.dumps({k: out[k] for k in ['state','sourceMembers','prepInputs','uniquePathsRehashed','checks','exactForwardReverseEdits']}))
