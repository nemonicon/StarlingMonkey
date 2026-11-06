"""Data-only observation: recipe compiled/linked, wrapper protection failed."""
from pathlib import Path
import hashlib
import json
import os
import re

R = Path('/Users/dan/dev/StarlingMonkey')
K = R / 'tests/node-compat/foundation-crypto'
P = K / 'node-crypto-hash-hmac-native-controller-candidate-v3'
PREFIX = K / 'node-crypto-hash-hmac-native-build-v4'


def row(path):
    p = Path(path)
    a = p.lstat()
    assert p.is_file() and not p.is_symlink()
    h = hashlib.sha256()
    with p.open('rb') as stream:
        for block in iter(lambda: stream.read(4194304), b''):
            h.update(block)
    z = p.lstat()
    assert (a.st_dev, a.st_ino, a.st_size, a.st_mtime_ns, a.st_ctime_ns) == (
        z.st_dev, z.st_ino, z.st_size, z.st_mtime_ns, z.st_ctime_ns)
    return dict(path=str(p), sha256=h.hexdigest(), bytes=z.st_size)


def read(path):
    return json.loads(Path(path).read_bytes())


refs = read(P / 'references.json')
authority = row(str(PREFIX) + '-root-authority.json')
config = row(str(PREFIX) + '-root-config.json')
invocation = row(str(PREFIX) + '-root-invocation.json')
r, cfg, inv = read(authority['path']), read(config['path']), read(invocation['path'])
assert r['controllerIndex']['sha256'] == '2ebed6b8c0f9787c07ef00036e8b903f4a39cfa70f916da45e895743d097969c'
assert cfg['controllerIndex'] == inv['controllerIndex'] == r['controllerIndex']
assert cfg['rootAuthority'] == inv['rootAuthority'] == authority
out = Path(refs['buildOutputRoot'])
external = Path(refs['buildExternalRoot'])
caller = Path(refs['observerBase'] + '-build-root-caller-v4')
parents = {}
for name, base in [('inner', external), ('outer', caller)]:
    d = row(base / 'terminal.json')
    t = read(d['path'])
    assert t['rawExitCode'] == 1 and t['authority'] == authority
    assert t['parentOwnedGroupGone'] is t['allObservedOwnedGroupsGone'] is True
    assert t['timeout'] is t['forcedCleanup'] is False
    for key in ['errors', 'signals', 'interruptedSignals', 'remainingObservedPids']:
        assert t[key] == []
    parents[name] = d
result_row = row(out / 'result.json')
result = read(result_row['path'])
assert result['controllerIndex'] == r['controllerIndex'] and result['rootAuthority'] == authority
assert result['rawChildExitCode'] == result['status'] == 0 and result['launcherExitCode'] == 1
assert result['lifecycleComplete'] is result['childStarted'] is True
assert result['ownedGroupCleanup'] == dict(pgid=87833, complete=True, events=[], errors=[], rawChildExitCode=0)
assert result['evidenceComplete'] is False
assert result.get('allSourceStageOriginalAndCacheInputsPreserved') is not True
assert result['launcherErrors'] == [dict(stage='build-cache-or-metadata', type='AssertionError', message='')]
assert result['finalObservationErrors'] == [dict(stage='final-protection', type='AssertionError', message='')]
assert len(result['cacheCopiesCompleted']) == 4
for key in ['engineExecuted', 'guestExecuted', 'cryptoOperationsInvoked', 'liveEvpSnapshotAdmission', 'operationalAdmission', 'runtimeAcceptanceClaim']:
    assert result[key] is False
log = row(out / 'build.log')
assert log == result['buildLog']
steps = [int(x) for x in re.findall(r'^\[(\d+)/109\]', Path(log['path']).read_text(), re.MULTILINE)]
assert len(steps) == 109 and steps[-2:] == [108, 109]
assert sorted(set(range(1, 110)) - set(steps)) == [40]
assert steps.count(39) == 2
engine = row(refs['enginePath'])
metadata = row(refs['enginePath'] + '.build.json')
assert engine['sha256'] == '9aec9297122c33b60790fcf4e1ce909db0200a426c04de98074e39046aa0f16e'
assert metadata['sha256'] == '2b725c114a3c23e582f87213ec5de6af128416dc8f10e9a9f9d3f6cd5d0fbce6'
m = read(metadata['path'])
assert len(m) == 83 and m['enginePath'] == engine['path']
assert len(m['sourceManifest']) == 357 and len(m['componentizeSourceManifest']) == 3
assert len(m['selectedModuleManifests']) == 12
recheck_row = row(K / 'node-crypto-hash-hmac-native-build-v4-input-recheck-root-data.json')
recheck = read(recheck_row['path'])
assert recheck['checkedFileCount'] == 5375 and recheck['matchingFileCount'] == 5374
assert len(recheck['changed']) == 1
index_change = recheck['changed'][0]
assert row(index_change['actual']['path']) == index_change['actual']
assert index_change['actual']['path'] == refs['configuredSourceRoot'] + '/.git/index'
assert not Path(refs['freezeRoot']).exists()
stderr = (external / 'stderr.log').read_text()
assert "frame['capture'].recheck()" in stderr and "io_guard.py" in stderr
assert "assert sha(p)==r['sha256']and identity(p)==before" in stderr
report = dict(schemaVersion=1,
    state='ROOT_OBSERVED_HASH_HMAC357_COMPILER_ZERO_WRAPPER_GUARD_FAILED_V4',
    toolObservation=dict(sessionId=62405, rawExitCode=1),
    controllerIndex=r['controllerIndex'], sourcePeer=r['controllerSourceReview'],
    integrationSourceIndex=refs['integrationSourceIndex'], rootAuthority=authority,
    config=config, invocation=invocation, observer=row(Path(__file__).resolve()),
    actualBuildResult=result_row, externalParentTerminal=parents['inner'], outerTerminal=parents['outer'],
    externalStdout=row(external / 'stdout.log'), externalStderr=row(external / 'stderr.log'),
    outerStdout=row(caller / 'stdout.log'), outerStderr=row(caller / 'stderr.log'),
    buildLog=log, finalNinjaProgressLabel='109/109', observedNinjaProgressRecords=109,
    duplicateNinjaProgressLabels=[39], missingNinjaProgressLabels=[40],
    uniqueTaskIdentityFromProgressLabelsProved=False, recipeRawExitCode=0,
    recipeLifecycleComplete=True, ownedProcessCleanupVerified=True,
    completedCacheCopies=4, actualEngine=engine, actualMetadata=metadata,
    actualRawMetadataFields=83, observedNativeSourceFiles=357,
    observedExternalEmbeddingSources=3, observedSelectedWholeManifests=12,
    wrapperRawExitCode=1, wrapperEvidenceComplete=False,
    wrapperSourcePreservationClaimPassed=False, inputRecheck=recheck_row,
    changedInput=index_change, originalIndexPreimageRetained=False,
    exactIndexWriterProved=False, indexStatOnlyDeltaProved=False,
    engineExecuted=False, guestExecuted=False, cryptoOperationsInvoked=False,
    freezeInvoked=False, workloadRerun=False, phaseSucceeded=False,
    buildAcceptanceClaim=False, runtimeAcceptanceClaim=False,
    liveEvpSnapshotAdmission=False, operationalAdmission=False,
    requiresIndependentActualFailureAndArtifactReview=True)
path = Path(str(PREFIX) + '-root-results.json')
with path.open('x') as stream:
    json.dump(report, stream, indent=2)
    stream.write('\n')
    stream.flush()
    os.fsync(stream.fileno())
print(json.dumps(dict(rootResult=row(path), recipeRawZero=True, wrapperAccepted=False)))
