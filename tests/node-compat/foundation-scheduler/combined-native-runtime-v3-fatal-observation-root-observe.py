"""Read the original failed fatal observation; never rerun or accept its cause."""
from pathlib import Path
import hashlib
import json
import os

R = Path('/Users/dan/dev/StarlingMonkey')
S = R / 'tests/node-compat/foundation-scheduler'
PREFIX = S / 'combined-native-runtime-v3-fatal-fatal'


def row(path):
    p = Path(path)
    a = p.lstat()
    assert p.is_file() and not p.is_symlink()
    b = p.read_bytes()
    z = p.lstat()
    assert (a.st_dev, a.st_ino, a.st_size, a.st_mtime_ns, a.st_ctime_ns) == (
        z.st_dev, z.st_ino, z.st_size, z.st_mtime_ns, z.st_ctime_ns)
    return dict(path=str(p), sha256=hashlib.sha256(b).hexdigest(), bytes=len(b))


def read(path):
    return json.loads(Path(path).read_bytes())


def checked(d):
    assert row(d['path']) == d
    return read(d['path'])


authority = row(str(PREFIX) + '-root-authority.json')
config = row(str(PREFIX) + '-root-config.json')
invocation = row(str(PREFIX) + '-root-invocation.json')
r, cfg, inv = checked(authority), checked(config), checked(invocation)
assert r['phase'] == cfg['phase'] == 'fatal' and r['fixtureId'] == cfg['fixtureId'] == 'fatal'
assert cfg['rootAuthority'] == inv['rootAuthority'] == authority
assert cfg['sourceIndex'] == r['sourceIndex'] == inv['sourceIndex']
assert r['sourceIndex']['sha256'] == '54a70237f27aa9f0d1c0d6d0f7766f1575734031c806478017f304d9a73cd424'
assert row(r['sourceIndex']['path']) == r['sourceIndex']
assert r['expectedFatalCallbackAcceptanceAllowed'] is r['current355NativeCallbackDiagnosticAvailable'] is False
assert r['actualResourceRuntimeReview']['index']['sha256'] == 'd77c82e2abf8678b527910ae6be2f2df7250da7e72010e6cf5b90a8a35f90387'
assert r['actualMappedReview']['index']['sha256'] == '580e1f5902d1a8e0cc47840b49c8735db7b3d64a80966bd4fa53199814fe0bb5'
output = Path(r['outputRoot'])
external = Path(r['externalOutputRoot'])
caller = Path(str(output) + '-root-caller')
parents = {}
for name, base in [('inner', external), ('outer', caller)]:
    d = row(base / 'terminal.json')
    t = checked(d)
    assert t['authority'] == authority and t['rawExitCode'] == 1
    assert t['parentOwnedGroupGone'] is t['allObservedOwnedGroupsGone'] is True
    assert t['timeout'] is t['forcedCleanup'] is False
    for key in ['errors', 'signals', 'interruptedSignals', 'remainingObservedPids']:
        assert t[key] == []
    parents[name] = d
frames = [json.loads(x) for x in (caller / 'stdout.log').read_text().splitlines() if x.startswith('{')]
frames = [x for x in frames if x.get('state') == 'COMBINED355_RUNTIME_RAW_TERMINAL_UNREVIEWED_V3']
assert len(frames) == 1 and frames[0]['rawExitCode'] == 1
assert frames[0]['terminal'] == parents['inner'] and frames[0]['phase'] == 'fatal'
actual = {}
for p in output.rglob('*'):
    assert not p.is_symlink()
    if p.is_file():
        actual[p.relative_to(output).as_posix()] = row(p)
assert len(actual) == 15
for n in ['result.json', 'index.json', 'completion.json', 'fatal-classification.json']:
    assert n not in actual
failure = checked(actual['failure.json'])
assert failure['primaryPresent'] is failure['partialEvidenceOnly'] is True
assert failure['finalErrors'] == failure['sessions'] == []
marker = checked(actual['fatal-jco/fatal-armed.json'])
assert marker['state'] == 'COMBINED355_FATAL_PUBLIC_CALL_ARMED_V3'
assert marker['sourceIndex'] == r['sourceIndex'] and marker['fixtureId'] == 'fatal'
assert marker['moduleImportCompleted'] is marker['publicExportAboutToBeInvoked'] is True
assert marker['name'] == 'run' and marker['args'] == []
typed = checked(actual['fatal-jco/raw/001.json'])
assert typed['sequence'] == 1 and typed['kind'] == 'throw' and typed['name'] == 'run' and typed['args'] == []
caught = checked(actual['fatal-jco/caught-failure.json'])
assert caught['capture']['attempted'] == caught['capture']['written'] == 1
assert caught['capture']['captureFailures'] == [] and caught['expectedFatalClaim'] is False
children = {}
for name, code in [('jco-fatal', 1), ('wasmtime-fatal', 134)]:
    d = actual['processes/' + name + '.terminal.json']
    t = checked(d)
    assert t['status'] == code and t['signal'] is None and t['spawnError'] is None
    assert t['closed'] is t['ownedGroupGone'] is True
    assert t['timedOut'] is t['outputLimitExceeded'] is t['terminalExitZeroObserved'] is False
    assert t['externalSignal'] is None and t['signalCount'] == 0
    assert t['errors'] == t['signals'] == []
    for key in ['stdout', 'stderr']:
        assert row(t[key]['path']) == t[key]
    children[name] = d
wt_stderr = Path(actual['processes/wasmtime-fatal.stderr.txt']['path']).read_text()
assert 'wasm `unreachable` instruction executed' in wt_stderr
assert 'RESOURCE_UNHANDLED_TIMER_CALLBACK' not in wt_stderr
node_stderr = (external / 'stderr.log').read_text()
assert 'WT fatal identity/reach evidence pending if diagnostic absent; nonzero alone never enough' in node_stderr
assert not (output / 'fatal-jco/unexpected-normal-return.json').exists()
report = dict(schemaVersion=1,
    state='ROOT_OBSERVED_COMBINED355_FATAL_OBSERVATION_UNACCEPTED_V3',
    toolObservation=dict(sessionId=52435, rawExitCode=1),
    sourceIndex=r['sourceIndex'], rootAuthority=authority, config=config,
    invocation=invocation, observer=row(Path(__file__).resolve()),
    actualMappedReview=r['actualMappedReview'], actualResourceRuntimeReview=r['actualResourceRuntimeReview'],
    externalParentTerminal=parents['inner'], outerTerminal=parents['outer'],
    externalStdout=row(external / 'stdout.log'), externalStderr=row(external / 'stderr.log'),
    outerStdout=row(caller / 'stdout.log'), outerStderr=row(caller / 'stderr.log'),
    actualPartialFiles=actual, partialFileCount=15, childTerminals=children,
    completeCurrentPartialMembershipAndHashesVerified=True,
    originalResultPublished=False, originalIndexPublished=False,
    originalCompletionPublished=False, originalFatalClassificationPublished=False,
    jcoModuleImportCompletedAndBeforePublicCallMarkerObserved=True,
    typedJcoThrowRetained=True, jcoRawExitCode=1, wasmtimeRawExitCode=134,
    wasmtimeSourceSpecificDiagnosticObserved=False,
    failureStage='Parent refuses absent Wasmtime source-specific callback diagnostic',
    callbackCause='inconclusive', expectedCallbackFailureProved=False,
    fatalCallbackGateSatisfied=False, nativeCallbackReachedObserved=False,
    uniqueOriginalJsErrorIdentityProved=False, phaseSucceeded=False,
    ownedProcessCleanupVerified=True, sourceControlledFailureFinalErrors=[],
    freshJcoAttempts=1, freshWasmtimeAttempts=1, workloadRerun=False,
    nativeSourceFiles=355, externalEmbeddingSources=3,
    fullMetadataFields=80, selectedWholeManifests=11,
    runtimeAcceptanceClaim=False, operationalAdmission=False,
    requiresIndependentActualFailureReview=True)
path = Path(str(PREFIX) + '-root-results.json')
with path.open('x') as stream:
    json.dump(report, stream, indent=2)
    stream.write('\n')
    stream.flush()
    os.fsync(stream.fileno())
print(json.dumps(dict(rootResult=row(path), partialFiles=15, accepted=False)))
