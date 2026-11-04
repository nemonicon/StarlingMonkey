#!/usr/bin/env python3
"""Independent source/data reader; never imports owner code or launches children."""
import ast
import difflib
import hashlib
import json
from pathlib import Path
import stat

HERE = Path(__file__).resolve().parent
FAMILY = HERE.parent
OWNER = FAMILY / 'measurement-correctness-persistence-amendment-v1'
PARENT = FAMILY / 'measurement-correctness-reporting-amendment-v1'
ORIGINAL = FAMILY / 'measurement-correctness-candidate-v1'
seen = {}

def checked(path, expected=None, size=None):
    path = Path(path)
    before = path.lstat()
    assert stat.S_ISREG(before.st_mode), str(path)
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    after = path.lstat()
    assert (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) == (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns), str(path)
    value = digest.hexdigest()
    if expected is not None:
        assert value == expected, str(path)
    if size is not None:
        assert before.st_size == size, str(path)
    seen[str(path.resolve())] = {'path': str(path.resolve()), 'sha256': value, 'bytes': before.st_size}
    return value

def load(path):
    checked(path)
    return json.loads(Path(path).read_bytes())

def indexed(root, expected, count):
    checked(root / 'index.json', expected)
    document = load(root / 'index.json')
    assert len(document['files']) == count
    for row in document['files']:
        checked(root / row['path'], row['sha256'], row['bytes'])
    return document

owner_index = indexed(OWNER, '60a8687e9b6bfff4c68df2a36e9dd47ad0f5cd327441f8cf32d63caa67518ba8', 35)
indexed(PARENT, '0558b50589680f9e1b812c8a62210233a768385bfabeae2f07be47c2e1fe5350', 14)
indexed(ORIGINAL, '138a4e0bcfe22ef3b48375257a50958f595dcebb607fc9267a30080948d612da', 36)
manifest = load(OWNER / 'input-freeze.json')
assert len(manifest['inputs']) == 121
for row in manifest['inputs']:
    assert Path(row['path']).is_absolute()
    checked(row['path'], row['sha256'], row['bytes'])

proof = load(OWNER / 'transformation-proof.json')
before = (PARENT / 'proposed/component-driver.mjs').read_text()
after = (OWNER / 'proposed/component-driver.mjs').read_text()
assert hashlib.sha256(before.encode()).hexdigest() == proof['beforeSha256']
assert hashlib.sha256(after.encode()).hexdigest() == proof['afterSha256']
assert proof['reverseExact'] is True and len(proof['edits']) == 8
value = before
for edit in proof['edits']:
    assert edit['count'] == 1 and value.count(edit['old']) == 1
    at = value.index(edit['old'])
    assert edit['afterOffsets'] == [at]
    value = value[:at] + edit['new'] + value[at + len(edit['old']):]
assert value == after
for edit in reversed(proof['edits']):
    at = edit['afterOffsets'][0]
    assert value[at:at + len(edit['new'])] == edit['new']
    value = value[:at] + edit['old'] + value[at + len(edit['new']):]
assert value == before
patch = ''.join(difflib.unified_diff(before.splitlines(True), after.splitlines(True), fromfile='a/component-driver.mjs', tofile='b/component-driver.mjs'))
assert patch == (OWNER / 'persistence.UNAPPLIED.patch').read_text()
assert proof['guestWorkloadBoundaryOracleProviderSchedulerBundleInputsChanged'] is False
assert proof['semanticComparisonChanged'] is False
# This packet has one driver afterimage and one new host helper, not copies or
# substitutes of the corpus/provider/oracles/bundler/comparison/completion.
assert sorted(path.name for path in (OWNER / 'proposed').iterdir()) == ['component-driver.mjs']
unchanged = ['guest.mjs', 'native-provider.mjs', 'workload.mjs', 'encoding-cases.mjs', 'node-workload-oracle.json', 'node-encoding-oracle.json', 'bundle-diagnostic.mjs', 'completion.mjs']
for name in unchanged:
    assert (ORIGINAL / name).is_file()
    checked(ORIGINAL / name)
checked(PARENT / 'bounded-comparison.mjs')
assert "await requireExactJSON({label:'fresh-Jco-full-rotation',actual:freshJco,expected:retained[0],writeCounterexample});" in after
assert 'for(let index=0;index<20;index++)' in after and 'round<3' in after and 'index<=20' in after
assert 'spawnSync' not in after
assert 'deadlineMs:600000' in after and "invoke('wasmtime-version',['--version'],55000" in after
assert 'selectedInterfaces:[]' in after
assert "'988224282d03fe0bd3c25b62344aef265b1a8e1f5804bdbc34d6442507fabcc0'" in after
assert "'a85dec9fcbbad23d0e038e5a99604114dbe9aa77bc784e4bce0f33013eb33c1c'" in after

jco = after[after.index('async function jcoCase('):after.index('async function oneRotation(')]
assert jco.index("await progress('jco-before'") < jco.index('await instance.run(index)')
assert jco.index("await persist('case-results/'+name+'.raw.txt'") < jco.index('JSON.parse(raw)')
assert jco.index("await persist('case-results/'+name+'.observed.json'") < jco.index('await validateCase(')
assert "await progress('jco-returned'" in jco and "await progress('jco-validated'" in jco
assert "await persist('rotations/'+label+'.json'" in after
wt = after[after.index('const wasmtime=[];'):after.index(' await admission.recheck();\n const report=')]
assert wt.index("await progress('wasmtime-before'") < wt.index('await invoke(name,')
assert wt.index("await progress('wasmtime-process-returned'") < wt.index('if(!actual.terminalExitZeroObserved)')
assert wt.index("await persist('case-results/'+name+'.observed.json'") < wt.index('await validateCase(')
assert wt.index("await persist('case-results/'+name+'.validated.json'") < wt.index('wasmtime.push(record)')
assert after.index(' await admission.recheck();\n const report=') < after.index('await publishCompletion(')
assert "await lstat(output);assert.fail('Choose a fresh correctness output')" in after
assert 'resumeSupported:false,reusedResults:0' in after

helper = (OWNER / 'durable-host.mjs').read_text()
assert "spawn(executable,args,{detached:true,stdio:['ignore','pipe','pipe']})" in helper
assert 'assert(pid>1&&pid!==process.pid)' in helper
assert 'process.kill(-pid,0)' in helper and 'process.kill(-pid,number)' in helper
assert "error.code==='ESRCH'" in helper
assert "signal('SIGTERM')" in helper and "signal('SIGKILL')" in helper
assert 'timeoutMs<=600000' in helper and 'graceMs<=5000' in helper
assert 'const ceiling=timeoutMs+2*graceMs+1000;' in helper
assert "const pumps=[pump(child.stdout,stdoutHandle,'stdout'),pump(child.stderr,stderrHandle,'stderr')];" in helper
assert 'await Promise.all(pumps);' in helper
assert 'await handle.sync()' in helper
assert helper.index("await persistFile({output,write,path:terminalPath") < helper.index('return{...outcome,terminalPath,stdout:')
assert 'closed&&exitCode===0&&!exitSignal&&!spawnError&&!timedOut&&!externalSignal&&!outputLimitExceeded&&errors.length===0' in helper
assert "stage:'owned-descendants'" in helper and "await terminate('owned-descendants')" in helper
assert "open(stdoutPath,'wx')" in helper and "open(stderrPath,'wx')" in helper
assert 'child.stdout.destroy();child.stderr.destroy();child.unref();' in helper
assert "process.removeListener('SIGTERM',onSigterm)" in helper and "process.removeListener('SIGINT',onSigint)" in helper
assert 'relative(root,target)' in helper and 'assert.notEqual(parent,current)' in helper
assert 'maxOutputBytes?await readFile(stdoutPath' in helper

stored = load(OWNER / 'evidence/host-tests.json')
assert stored['passed'] == 17 and len(stored['checks']) == 17
assert stored['state'] == 'PURE_HOST_REPORTING_AND_OWNED_CHILD_TESTS_PASSED'
assert stored['actualWorkloadOrBenchmarkExecuted'] is False
assert stored['children'] == 'benign Node host programs only; no Wasmtime/native/guest'
test = (OWNER / 'test-host.mjs').read_text()
for marker in ['nonzero', 'timeout', 'overflow', 'missing', 'EEXIST', 'linked-parent', 'priorSignals', 'runOwnedCommand']:
    assert marker in test
ast_files = []
for path in OWNER.glob('*.py'):
    ast.parse(path.read_text())
    ast_files.append(path.name)

failure = load(OWNER / 'failure-evidence/workload-timeout-attempt1-root-results.json')
long_case = load(OWNER / 'failure-evidence/workload-public-case5-root-results.json')
assert failure['originalTimedOutCaseUnknown'] is True and failure['fullCorrectnessPassed'] is False
assert long_case['wholeTraceAndChecksumEqualNode'] is True and long_case['timeoutSeconds'] == 600
assert long_case['fullTwentyPlusFourteenPassed'] is False
for row in list(seen.values()):
    checked(row['path'], row['sha256'], row['bytes'])
report = {
    'schemaVersion': 1,
    'state': 'INDEPENDENT_CORRECTNESS_PERSISTENCE_SOURCE_REVIEW_PASSED_NO_ACTIONS',
    'ownerIndexSha256': checked(OWNER / 'index.json'),
    'ownerFiles': 35, 'inputRows': 121, 'forwardReverseDriverEdits': 8,
    'corpus': {'workloads': 20, 'boundaryCases': 14, 'retainedRotations': 3, 'freshJcoRotations': 1, 'freshWasmtimeCalls': 21, 'guestProviderWorkloadOraclesBundlerComparisonCompletionUnchanged': True, 'resumeOrOldPassReuse': False},
    'collection': {'jcoRawAndFullParsedRecordSyncedBeforeEquality': True, 'rotationPersistedImmediately': True, 'wasmtimeRawStreamsSyncedAndTerminalRecordedBeforeDriverAssertion': True, 'fullJSONComparisonRetained': True, 'finalNativeSourceRecheckAndCompletionRequired': True, 'counterexampleBeforeCompactMismatchRetained': True},
    'ownedProcessLifecycleSource': {'asyncDetachedFreshSession': True, 'signalsOnlyNegativeOwnedPid': True, 'termThenKillAndEsrchHandled': True, 'finiteCaseDeadlineMs': 600000, 'maxCleanupGraceMsEach': 5000, 'additionalReapAllowanceMs': 1000, 'versionDeadlineMs': 55000, 'perStreamDecodeCapBytes': 16777216, 'overflowIsFailureWithRawFiles': True, 'temporaryParentSignalListenersRemoved': True, 'noBroadProcessSearch': True},
    'evidence': {'ownerBenignHostChecksAuthenticated': 17, 'ownerTestsRerunByReviewer': False, 'pythonASTParsed': sorted(ast_files), 'originalFailedCaseUnknown': True, 'separateLongCase5NotAFullGatePassOrAllCaseDeadlineProof': True},
    'limitations': ['Source review and authenticated stored benign-child tests only; no new target run or runtime acceptance.', 'No crash, ENOSPC, concurrent-writer, reset, ALS, or general lifecycle guarantee.', 'Long case5 justifies a finite larger operational cap but does not prove adequacy for every case.', 'Activation successor requires its own review, same genuine authority, a fresh output family, all cases and external exit0.'],
    'concreteSourceBlockers': [], 'ownerImportsOrHelperMainsExecuted': False,
    'nativeGuestComponentizerHostOrTimingExecuted': False,
    'fullCorrectnessPassed': False, 'runtimeAcceptanceClaim': False,
    'files': sorted(seen.values(), key=lambda row: row['path'])
}
with (HERE / 'results.json').open('x') as stream:
    json.dump(report, stream, indent=2)
    stream.write('\n')
print(json.dumps({'state': report['state'], 'verifiedPaths': len(seen), 'ownerFiles': 35, 'inputRows': 121, 'driverEdits': 8, 'concreteSourceBlockers': 0}))
