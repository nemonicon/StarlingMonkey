"""Independent finite source/data reader; no reviewed module/helper execution."""
from pathlib import Path
import hashlib
import json
import os
import stat

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / 'cost-pilot-timing-candidate-v3'
SHA = 'c2ce5f08134d0cd05b9d3f10fe5bf1b49f124b1d32c49bff977d7ddb7ab064e9'
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
need(own['sha256'] == SHA and own['bytes'] == 8574, 'final actualc2ce source seal')
need(len(index(own)) == 50, 'all50 own members')
inputs = load(SOURCE/'source-inputs.json')['files']
need(len(inputs) == 918 and len({r['path'] for r in inputs}) == 918, 'all918 finite preparation inputs')
for r in inputs: verify(r)
ancestors = [
    ('cost-pilot-timing-candidate-v1', '55db1fc3895a0dbd10ca07e08c59bd68da8edeb9793632c8e05cb41704c5135b', 85),
    ('cost-pilot-timing-candidate-v2', '1a294044a4f2414d35fdd817dae95598c2e079aa64a9044737f4791aefe630a2', 26),
    ('independent-cost-pilot-timing-source-review-v1', '1a2148e89e8018ada23d48b0a2225e2203c51272eeb722933b7842a0c6f48aa1', 8),
    ('independent-cost-pilot-timing-v2-source-review-v1', 'fa4c11256f3900817b5d1694f83be1ad0e34c501097a88e99f3b7b2ca88602b9', 9)
]
for name, expected, count in ancestors:
    r = hash_file(SOURCE.parent/name/'index.json')
    need(r['sha256'] == expected and len(index(r)) == count, 'complete old source/HOLD preserved ' + name)
old_inputs = load(SOURCE.parent/'cost-pilot-timing-candidate-v2/source-inputs.json')['files']
need(all(r in inputs for r in old_inputs), 'all861 previous prep identities retained')
changes = load(SOURCE/'source-derivations.json')['files']
edits = 0
for item in changes:
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
        need(data[at:at+len(new)] == new, 'exact reverse segment')
        data = data[:at]+old+data[at+len(new):]
    need(data == before, 'exact held donor restored')
need(len(changes) == 4 and edits == 16, 'four derived bodies16 exact edits')

# Independent reconstruction of actual static and literal-dynamic JS imports.
import re
static = re.compile(r"(?m)^\s*(?:import|export)\s+[^\n]*?\sfrom\s*['\"]([^'\"\n]+)['\"]|^\s*import\s*['\"]([^'\"\n]+)['\"]")
dynamic = re.compile(r"\bimport\s*\(\s*['\"]([^'\"]+)['\"]\s*\)")
pending = [SOURCE/n for n in ['run.mjs', 'worker.mjs', 'prepare-plan.mjs']]
graph = set()
while pending:
    path = pending.pop().resolve()
    if path in graph: continue
    graph.add(path)
    verify(hash_file(path))
    text = path.read_text()
    specs = [m.group(1) or m.group(2) for m in static.finditer(text)] + [m.group(1) for m in dynamic.finditer(text)]
    for spec in specs:
        if spec.startswith('node:'): continue
        need(spec.startswith('.'), 'no unbounded runtime package specifier')
        pending.append((path.parent/spec).resolve())
runtime = load(SOURCE/'runtime-dependencies.json')
runtime_paths = {Path(r['path']).resolve() for r in runtime['files']}
outside = {p for p in graph if not p.is_relative_to(SOURCE)}
need(len(graph) == 36 and len(runtime_paths) == 28 and outside == runtime_paths, 'actual36-module graph exactly own8 plus declared28 dependencies')
for r in runtime['files']: verify(r)
for suffix in ['cost-pilot-timing-candidate-v1/owned-lifecycle.mjs', 'cost-pilot-timing-candidate-v1/result-collector.mjs', 'cost-pilot-timing-candidate-v1/planner.mjs', 'cost-pilot-timing-candidate-v2/contract-descriptors.mjs']:
    need(any(str(p).endswith(suffix) for p in runtime_paths), 'previously omitted role included ' + suffix)
for r in load(SOURCE/'module-edges.json')['modules']: verify(r)
deps = load(SOURCE/'worker-dependencies.json')['files']
need(len(deps) == 20 and all(r['bytes'] < 4194304 for r in deps), '20 small worker source dependencies')
for r in deps: verify(r)

auth = (SOURCE/'source-families.mjs').read_text()
need(all((m.group(1) or m.group(2)).startswith('node:') for m in static.finditer(auth)), 'source authenticator imports standard Node only')
need('55db1fc3895a0dbd10ca07e08c59bd68da8edeb9793632c8e05cb41704c5135b' in auth and '1a294044a4f2414d35fdd817dae95598c2e079aa64a9044737f4791aefe630a2' in auth, 'primitive fixed inherited manifest hashes')
need(auth.index('raw=await readVerified(ix') < auth.index('v=JSON.parse(raw)'), 'manifest bytes hash-bound before parse/rows')
need('const fixed=Object.freeze(rows)' in auth and 'await readVerified(ix' in auth and 'await exactTree(root,[...names' in auth, 'private original rows/index/membership rechecked')
need('for(const row of [...ANCESTORS,own])' in auth and 'for(const family of families)await family.recheck()' in auth, 'all three complete families initial/final')
need('const dependencies=await checkFileRows(declared.files)' in auth and 'await dependencies.recheck()' in auth, 'all28 runtime dependencies initial/final')
need('issued=new WeakSet()' in auth and 'issued.add(capsule)' in auth and 'issued.has(capsule)' in auth, 'private source-auth capsule brand')
for n in ['run.mjs', 'worker.mjs', 'prepare-plan.mjs']:
    text = (SOURCE/n).read_text()
    imports = [m.group(1) or m.group(2) for m in static.finditer(text)]
    need(all(s.startswith('node:') or s == './source-families.mjs' for s in imports), 'standard/source-auth-only public bootstrap ' + n)
    need(text.index('await captureSourceFamilies(') < text.index('await import('), 'authenticate before custom body import ' + n)
    need('finally{await source.recheck();}' in text, 'wrapper recheck even on failure ' + n)
for n in ['run-body.mjs', 'worker-body.mjs', 'prepare-plan-body.mjs']:
    text = (SOURCE/n).read_text()
    need('assertSourceFamilyAudit(sourceFamilyAudit,' in text and 'if(process.argv[1]' not in text, 'branded capsule/no executable bypass body ' + n)
guard = (SOURCE/'parent-guard.template.mjs').read_text()
worker = (SOURCE/'worker-body.mjs').read_text()
run = (SOURCE/'run-body.mjs').read_text()
need(guard.index('const inheritedFamilies=await captureSourceFamilies(ownRow)') < guard.index("await import('../cost-jco-correctness-candidate-v3/admission.mjs')"), 'genuine guard invoked after full family auth')
need('await inheritedFamilies.recheck();await own.recheck()' in guard, 'admitted parent recheck covers all inherited sources')
need(run.count('await admitted.recheck()') >= 3 and run.index('await admitted.recheck();if(warm)') < run.index("const result=await write('results.json'"), 'parent success/failure prepublication source rechecks')
need('await sourceFamilyAudit.recheck();await regular(inputRow)' in worker and worker.count('await recheck()') >= 3, 'worker before output/final/failure full source rechecks')
need(worker.index('await recheck();const output=') < worker.index('session=await loadTimingSession('), 'full worker source check before actual generated-code load')
need("from '../cost-pilot-timing-candidate-v2/contract-descriptors.mjs'" in guard and guard.count('await verifyContractDescriptor(row)') == 2, 'M1 exact finite descriptor verifier retained both loops')

evidence = load(SOURCE/'evidence/source-families.stdout.log')
need(evidence['checks'] == 23 and evidence['memberAndIndexTamperInitialAndRecheckRefused'] and evidence['unlistedMembershipInitialAndRecheckRefused'] and evidence['runtimeImportedFileRecheckRefused'] and evidence['fakeSourceCapsuleRefused'], 'stored actual23 family/scratch negatives authenticated')
need(evidence['providerGuestPreflightWorkerNativeJcoWasmtimePilotTimingExecuted'] is False and (SOURCE/'evidence/source-families.stderr.log').read_bytes() == b'', 'source/data only and empty stderr')
scratch = load(SOURCE/'scratch-evidence.json')
need(len(scratch['copies']) == 20 and scratch['fixtureMjsFilesNeverImportedOrExecuted'] is True, '20 preserved scratch DATA files no execution')
for item in scratch['copies']:
    verify(item['original'])
    got = hash_file(SOURCE/item['copy'])
    need(got['sha256'] == item['original']['sha256'] and got['bytes'] == item['original']['bytes'], 'exact scratch copy')
syntax = load(SOURCE/'evidence/syntax.json')
need(len(syntax) == 9 and all(r['rawExitCode'] == 0 and not r['stderr'] for r in syntax), 'nine stored grammar outcomes authenticated')

# Authenticated post-seal author's source-read/hash-only observation; no rerun.
external = Path('/private/tmp/starling-node-compat/zlib-cost-v3-source-capsule-hl_a8nj3')
terminal = hash_file(external/'terminal.json')
need(terminal['sha256'] == '5bda128975835ada3f508cf74561e4a3bb41dfd0cf47ead349320ff30afecbaf' and terminal['bytes'] == 1041, 'exact provided post-seal source-only terminal')
tv = load(terminal['path'])
for r in [tv['source'], tv['stdout'], tv['stderr']]: verify(r)
proof = load(tv['stdout']['path'])
need(tv['rawExitCode'] == 0 and tv['sealedSourceWritten'] is False and tv['benchmarkActionsExecuted'] is False and tv['stderr']['bytes'] == 0, 'actual post-seal read/hash0 scope')
need(proof['sourceIndex'] == own and proof['verifiedSourceFamilies'] == 3 and proof['verifiedRuntimeDependencies'] == 28 and proof['privateBrandAsserted'] and proof['initialAndRecheckPassed'] and proof['customImplementationBodyImported'] is False, 'actual own-final-index three-family capsule observed, not workload')
source_text = Path(tv['source']['path']).read_text()
need('captureSourceFamilies(' in source_text and 'assertSourceFamilyAudit(' in source_text and 'await audit.recheck()' in source_text, 'actual captured source-only test API calls')
need('run-body' not in source_text and 'worker-body' not in source_text and 'correctnessPreflight' not in source_text, 'post-seal test did not import action bodies')

for n in ['future-authority.template.json', 'future-plan-authority.template.json']:
    v = load(SOURCE/n)
    need(v['sourceIndexSha256'] is None and v['sourceIndependentReview'] is None, 'future exact ownsource and peer remain null')
    for k in ['actionAllowed', 'dataPublicationAllowed']:
        if k in v: need(v[k] is False, 'future action remains false')
need("+'-v3';" in guard and 'zlib-cost-measurement-plan-v3' in (SOURCE/'prepare-plan-body.mjs').read_text(), 'fresh plan and phases v3')
out = {'schemaVersion': 1, 'state': 'INDEPENDENT_TIMING_V3_READ_HASH_SOURCE_DATA_CHECKS_PASSED',
    'sourceIndex': own, 'sourceMembers': 50, 'prepInputs': len(inputs), 'uniquePathsRehashed': len(seen), 'checks': len(checks),
    'exactDerivationFiles': len(changes), 'exactForwardReverseEdits': edits,
    'oldSourceAndHoldMemberCounts': [85,26,8,9], 'runtimeGraphModules': len(graph), 'runtimeOwnModules': 8,
    'runtimeDependencyFiles': 28, 'workerDependencyFiles': 20, 'scratchDataCopies': 20,
    'postSealAuthorReadHashTerminal': terminal, 'postSealAuthorSourceOnlyCapsuleObservation': proof,
    'reviewerOwnerFunctionsPreflightProviderGuestCodecJcoWasmtimeWorkloadsPilotTimingInvoked': False}
with (HERE/'read-results.json').open('x') as f: json.dump(out,f,indent=2); f.write('\n')
with (HERE/'verified-inputs.json').open('x') as f:
    json.dump({'schemaVersion':1,'files':[seen[k]['descriptor'] for k in sorted(seen)]},f,indent=2); f.write('\n')
print(json.dumps({k:out[k] for k in ['state','sourceMembers','prepInputs','uniquePathsRehashed','checks','exactForwardReverseEdits']}))

