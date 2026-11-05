"""M2 source/data and private scratch checks only; no action/helper execution."""
from pathlib import Path
import hashlib
import json

D = Path(__file__).resolve().parent
Z = D.parent
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
    need(path.is_file() and not path.is_symlink(), 'regular source/data')
    before = path.stat()
    value = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            value.update(block)
    after = path.stat()
    need((before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns) == (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns), 'stable read hash')
    return {'path': str(path), 'sha256': value.hexdigest(), 'bytes': after.st_size}

def verify(row):
    need(desc(row['path']) == {k: row[k] for k in ['path', 'sha256', 'bytes']}, 'exact descriptor ' + row['path'])
    if not Path(row['path']).is_relative_to(D):
        inputs[row['path']] = {k: row[k] for k in ['path', 'sha256', 'bytes']}

def write(name, value):
    with (D / name).open('x') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')

families = [('cost-pilot-timing-candidate-v1', '55db1fc3895a0dbd10ca07e08c59bd68da8edeb9793632c8e05cb41704c5135b'),
            ('cost-pilot-timing-candidate-v2', '1a294044a4f2414d35fdd817dae95598c2e079aa64a9044737f4791aefe630a2'),
            ('independent-cost-pilot-timing-source-review-v1', '1a2148e89e8018ada23d48b0a2225e2203c51272eeb722933b7842a0c6f48aa1'),
            ('independent-cost-pilot-timing-v2-source-review-v1', 'fa4c11256f3900817b5d1694f83be1ad0e34c501097a88e99f3b7b2ca88602b9')]
for name, expected in families:
    root = Z / name
    ix = desc(root / 'index.json')
    need(ix['sha256'] == expected, 'preserved exact old source/HOLD')
    inputs[ix['path']] = ix
    rows = load(root / 'index.json')['files']
    for row in rows:
        verify({'path': str(root / row['path']), 'sha256': row['sha256'], 'bytes': row['bytes']})
    need(sorted(str(p.relative_to(root)) for p in root.rglob('*') if p.is_file()) == sorted([r['path'] for r in rows] + ['index.json']), 'preserved exact old membership')
for row in load(Z / 'cost-pilot-timing-candidate-v2/source-inputs.json')['files']:
    verify(row)
for record in load(D / 'source-derivations.json')['files']:
    verify(record['origin'])
    old = Path(record['origin']['path']).read_text()
    source = old
    for e in record['edits']:
        need(source.count(e['old']) == 1, 'single exact M2 edit')
        at = source.index(e['old'])
        need(at == e['afterOffsetAtEdit'], 'exact M2 forward offset')
        source = source[:at] + e['new'] + source[at + len(e['old']):]
    need(source == (D / record['afterimage']).read_text(), 'exact M2 afterimage')
    back = source
    for e in reversed(record['edits']):
        at = e['afterOffsetAtEdit']
        need(back[at:at + len(e['new'])] == e['new'], 'exact M2 reverse segment')
        back = back[:at] + e['old'] + back[at + len(e['new']):]
    need(back == old, 'complete old held body reconstructed')
    need(hashlib.sha256(source.encode()).hexdigest() == record['afterSha256'], 'recorded M2 afterimage hash')
runtime = load(D / 'runtime-dependencies.json')
need(runtime['includesParentAndWorkerImports'] is True and len(runtime['files']) == 28, 'complete actual parent/worker runtime import set')
for row in runtime['files']:
    verify(row)
for row in load(D / 'worker-dependencies.json')['files']:
    verify(row)
for suffix in ['/cost-pilot-timing-candidate-v1/owned-lifecycle.mjs', '/cost-pilot-timing-candidate-v1/result-collector.mjs', '/cost-pilot-timing-candidate-v1/planner.mjs', '/cost-pilot-timing-candidate-v2/contract-descriptors.mjs']:
    need(sum(row['path'].endswith(suffix) for row in runtime['files']) == 1, 'parent/worker actual donor protected ' + suffix)
edges = load(D / 'module-edges.json')
for row in edges['modules']:
    verify(row)
for name in ['run.mjs', 'worker.mjs', 'prepare-plan.mjs']:
    source = (D / name).read_text()
    need(source.index('await captureSourceFamilies(') < source.index('await import('), 'source families before body import ' + name)
    need('finally{await source.recheck();}' in source, 'final wrapper captured recheck ' + name)
for name in ['run-body.mjs', 'worker-body.mjs', 'prepare-plan-body.mjs']:
    source = (D / name).read_text()
    need('assertSourceFamilyAudit(sourceFamilyAudit,' in source, 'private source capsule required ' + name)
    need('if(process.argv[1]' not in source, 'no bypass body CLI ' + name)
auth = (D / 'source-families.mjs').read_text()
need('new WeakSet()' in auth and 'issued.has(capsule)' in auth, 'source-only capsule cannot be boolean-forged')
need(auth.index('raw=await readVerified(ix') < auth.index('v=JSON.parse(raw)'), 'expected index digest before manifest parse/traversal')
need('for(const row of [...ANCESTORS,own])' in auth and 'await family.recheck()' in auth, 'all3families initial/private final recheck')
need('const dependencies=await checkFileRows(declared.files)' in auth and 'await dependencies.recheck()' in auth, 'external imported sources initial/private recheck')
guard = (D / 'parent-guard.template.mjs').read_text()
need('const inheritedFamilies=await captureSourceFamilies(ownRow)' in guard and 'await inheritedFamilies.recheck();await own.recheck()' in guard, 'parent admission and final recheck include complete sources')
need('await sourceFamilyAudit.recheck();await regular(inputRow)' in (D / 'worker-body.mjs').read_text(), 'worker complete capsule before output/load and final recheck')
need((Z / 'cost-pilot-timing-candidate-v2/contract-descriptors.mjs').read_text().count('108619024') == 1, 'M1 finite Node role inherited unchanged')
test = load(D / 'evidence/source-families.stdout.log')
need(test['checks'] == 23 and test['memberAndIndexTamperInitialAndRecheckRefused'] and test['unlistedMembershipInitialAndRecheckRefused'], '23 actual/read-hash/scratch negatives passed')
need(test['runtimeImportedFileRecheckRefused'] and test['fakeSourceCapsuleRefused'] and test['providerGuestPreflightWorkerNativeJcoWasmtimePilotTimingExecuted'] is False, 'negative imported-source/capsule cases without action')
for item in load(D / 'scratch-evidence.json')['copies']:
    verify(item['original'])
    got = desc(D / item['copy'])
    need(got['sha256'] == item['original']['sha256'] and got['bytes'] == item['original']['bytes'], 'exact preserved scratch DATA')
syntax = load(D / 'evidence/syntax.json')
need(len(syntax) == 9 and all(r['rawExitCode'] == 0 and not r['stderr'] for r in syntax), 'all9 source grammar checks passed')
for name in ['future-authority.template.json', 'future-plan-authority.template.json']:
    v = load(D / name)
    need(v['sourceIndexSha256'] is None and v['sourceIndependentReview'] is None and v.get('actionAllowed', False) is False and v.get('dataPublicationAllowed', False) is False, 'future source/Root action slots remain null/false')
write('source-inputs.json', {'schemaVersion': 1, 'files': [inputs[k] for k in sorted(inputs)], 'bothHoldsAndHeldSourceFamiliesPreserved': True, 'benchmarkActionsExecuted': False})
write('source-checks.json', {'schemaVersion': 1, 'state': 'COMPLETE_RUNTIME_SOURCE_FAMILY_AUTHENTICATION_SOURCE_CHECKS_PASSED_V3', 'checks': len(checks), 'readHashScratchChecks': 23, 'syntaxFiles': 9, 'inputFiles': len(inputs), 'runtimeDependencyFiles': 28, 'workerDependencyFiles': len(load(D / 'worker-dependencies.json')['files']), 'moduleFiles': len(edges['modules']), 'moduleEdges': len(edges['edges']), 'sourceFamiliesBeforeCustomImport': True, 'privateInitialAndFinalSourceAuditsImplemented': True, 'newHostLifecycleOrBenchmarkActionsExecuted': False, 'operationalAdmission': False})
print(json.dumps(load(D / 'source-checks.json')))
