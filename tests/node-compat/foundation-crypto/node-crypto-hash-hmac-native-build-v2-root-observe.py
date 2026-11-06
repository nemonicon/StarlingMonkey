"""Data-only observation of failed native-build preparation; never retries."""
from pathlib import Path
import hashlib
import json
import os
import stat

R = Path('/Users/dan/dev/StarlingMonkey')
K = R / 'tests/node-compat/foundation-crypto'
P = K / 'node-crypto-hash-hmac-native-controller-candidate-v1'
PREFIX = K / 'node-crypto-hash-hmac-native-build-v2'


def row(p):
    p = Path(p)
    a = p.lstat()
    assert p.is_file() and not p.is_symlink()
    b = p.read_bytes()
    z = p.lstat()
    assert (a.st_dev, a.st_ino, a.st_size, a.st_mtime_ns, a.st_ctime_ns) == (
        z.st_dev, z.st_ino, z.st_size, z.st_mtime_ns, z.st_ctime_ns)
    return dict(path=str(p), sha256=hashlib.sha256(b).hexdigest(), bytes=len(b))


def read(p):
    return json.loads(Path(p).read_bytes())


refs = read(P / 'references.json')
authority = row(str(PREFIX) + '-root-authority.json')
config = row(str(PREFIX) + '-root-config.json')
invocation = row(str(PREFIX) + '-root-invocation.json')
r, cfg, inv = read(authority['path']), read(config['path']), read(invocation['path'])
assert r['phase'] == 'build' and r['nativeBuildAllowed'] is True and r['freezeAllowed'] is False
assert r['controllerIndex']['sha256'] == '9e5195b90e20708a8a398fa9013eba867e2f2e5e1d18c2f5b76ed5bbc3c01d3b'
assert cfg['rootAuthority'] == inv['rootAuthority'] == authority
assert cfg['controllerIndex'] == r['controllerIndex'] == inv['controllerIndex']
work, out = Path(refs['workRoot']), Path(refs['buildOutputRoot'])
external = Path(refs['buildExternalRoot'])
caller = Path(refs['observerBase'] + '-build-root-caller-v2')
parents = {}
for name, base in [('inner', external), ('outer', caller)]:
    d = row(base / 'terminal.json')
    t = read(d['path'])
    assert t['authority'] == authority and t['rawExitCode'] == 1
    assert t['parentOwnedGroupGone'] is t['allObservedOwnedGroupsGone'] is True
    assert t['timeout'] is t['forcedCleanup'] is False
    for key in ['errors', 'signals', 'interruptedSignals', 'remainingObservedPids']:
        assert t[key] == []
    parents[name] = d
result_row = row(out / 'result.json')
result = read(result_row['path'])
assert result['controllerIndex'] == r['controllerIndex'] and result['rootAuthority'] == authority
assert result['sourceIndexSha256'] == refs['integrationSourceIndex']['sha256']
assert result['launcherExitCode'] == 1 and result['rawChildExitCode'] is None
assert result['cacheCopiesCompleted'] == result['diskFreeSamplesDuringBuildCommand'] == []
assert result['allSourceStageOriginalAndCacheInputsPreserved'] is True
assert result['launcherErrors'] == [dict(stage='build-cache-or-metadata', type='AssertionError', message='')]
assert result['engineExecuted'] is result['guestExecuted'] is result['cryptoOperationsInvoked'] is False
assert not (out / 'build.log').exists() and not Path(refs['freezeRoot']).exists()
assert not Path(refs['enginePath']).exists() and not Path(refs['enginePath'] + '.build.json').exists()
assert not any(p.is_symlink() for p in work.rglob('*'))
assert {p.relative_to(work).as_posix() for p in work.rglob('*') if p.is_file()} == {'componentize-source.tar.gz'}
plan = read(P / 'cache-plan.json')
first = plan['copies'][0]
partial = row(work / first['target'])
source = row(first['source']['path'])
assert source == first['source']
assert (partial['sha256'], partial['bytes']) == (source['sha256'], source['bytes'])
a, b = Path(source['path']).stat(), Path(partial['path']).stat()
assert (a.st_dev, a.st_ino) != (b.st_dev, b.st_ino) and b.st_nlink == 1
assert stat.S_IMODE(a.st_mode) == first['sourceMode'] == first['outputMode'] == 0o644
assert stat.S_IMODE(b.st_mode) == 0o600
assert {p.relative_to(out).as_posix() for p in out.rglob('*') if p.is_file()} == {'launch.json', 'result.json'}
report = dict(schemaVersion=1, state='ROOT_OBSERVED_HASH_HMAC357_BUILD_PREPARATION_FAILED_V2',
    toolObservation=dict(sessionId=14463, rawExitCode=1), controllerIndex=r['controllerIndex'],
    integrationSourceIndex=refs['integrationSourceIndex'], sourcePeer=r['controllerSourceReview'],
    rootAuthority=authority, config=config, invocation=invocation,
    observer=row(Path(__file__).resolve()), actualBuildResult=result_row,
    actualBuildLaunch=row(out / 'launch.json'), externalParentTerminal=parents['inner'],
    outerTerminal=parents['outer'], externalStdout=row(external / 'stdout.log'),
    externalStderr=row(external / 'stderr.log'), outerStdout=row(caller / 'stdout.log'),
    outerStderr=row(caller / 'stderr.log'), partialWorkFile=partial,
    sourceCacheFile=source, sourceMode=0o644, requestedOutputMode=0o644,
    observedOutputMode=0o600, distinctInode=True, singleLink=True,
    completedCacheCopies=0, partialWorkFileCount=1, ownerResultFiles=2,
    originalErrorType='AssertionError', originalErrorMessage='',
    originalCaughtAssertionStackRetained=False,
    sourceDerivedFailureCause='populate_cache requests0644 under umask077 then requires0644 without fchmod; retained copy is0600',
    causeAttributionUsesSourceAndRetainedFileProperties=True,
    recipeStarted=False, compilerStarted=False, buildLogCreated=False,
    newEngineObserved=False, newMetadataObserved=False, actualNewEngine=None,
    actualNewMetadata=None, engineExecuted=False, guestExecuted=False,
    cryptoOperationsInvoked=False, freezeInvoked=False, workloadRerun=False,
    sourceControlledFinalPreservationPassed=True, ownedProcessCleanupVerified=True,
    nativeSourceFiles=357, externalEmbeddingSources=3, selectedWholeManifests=12,
    expectedRawMetadataFields=83, actualMetadataFieldsObserved=None,
    phaseSucceeded=False, buildAcceptanceClaim=False, runtimeAcceptanceClaim=False,
    liveEvpSnapshotAdmission=False, operationalAdmission=False,
    requiresIndependentActualFailureReview=True)
path = Path(str(PREFIX) + '-root-results.json')
with path.open('x') as stream:
    json.dump(report, stream, indent=2)
    stream.write('\n')
    stream.flush()
    os.fsync(stream.fileno())
print(json.dumps(dict(rootResult=row(path), accepted=False, recipeStarted=False)))
