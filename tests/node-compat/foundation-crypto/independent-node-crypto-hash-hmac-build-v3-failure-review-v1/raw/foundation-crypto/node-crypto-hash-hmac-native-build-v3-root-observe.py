"""Observe the original early recipe refusal; never runs a producer/helper."""
from pathlib import Path
import hashlib
import json
import os
import re
import stat

R = Path('/Users/dan/dev/StarlingMonkey')
K = R / 'tests/node-compat/foundation-crypto'
P = K / 'node-crypto-hash-hmac-native-controller-candidate-v2'
PREFIX = K / 'node-crypto-hash-hmac-native-build-v3'


def row(path):
    p = Path(path)
    a = p.lstat()
    assert p.is_file() and not p.is_symlink()
    data = p.read_bytes()
    b = p.lstat()
    assert (a.st_dev, a.st_ino, a.st_size, a.st_mtime_ns, a.st_ctime_ns) == (
        b.st_dev, b.st_ino, b.st_size, b.st_mtime_ns, b.st_ctime_ns)
    return dict(path=str(p), sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))


def read(path):
    return json.loads(Path(path).read_bytes())


refs = read(P / 'references.json')
authority = row(str(PREFIX) + '-root-authority.json')
config = row(str(PREFIX) + '-root-config.json')
invocation = row(str(PREFIX) + '-root-invocation.json')
r, cfg, inv = read(authority['path']), read(config['path']), read(invocation['path'])
assert r['controllerIndex']['sha256'] == 'e8b47cc8eac2decb8822f0aded016594fcc10f9d997b5f2461d251bb98d4953a'
assert cfg['rootAuthority'] == inv['rootAuthority'] == authority
assert r['controllerIndex'] == cfg['controllerIndex'] == inv['controllerIndex']
out, work = Path(refs['buildOutputRoot']), Path(refs['workRoot'])
external = Path(refs['buildExternalRoot'])
caller = Path(refs['observerBase'] + '-build-root-caller-v3')
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
assert result['rawChildExitCode'] == result['status'] == result['launcherExitCode'] == 1
assert result['childStarted'] is result['lifecycleComplete'] is True
assert result['launcherErrors'] == []
assert result['ownedGroupCleanup']['complete'] is True
assert result['ownedGroupCleanup']['events'] == result['ownedGroupCleanup']['errors'] == []
assert result['stoppedForDiskSpace'] is False and result['stopReason'] is None
assert result['allSourceStageOriginalAndCacheInputsPreserved'] is True
assert len(result['cacheCopiesCompleted']) == 4
assert row(result['buildLog']['path']) == result['buildLog'] and result['buildLog']['bytes'] == 0
for copy in result['cacheCopiesCompleted']:
    assert row(copy['source']['path']) == copy['source']
    assert row(copy['target']['path']) == copy['target']
    assert (copy['source']['sha256'], copy['source']['bytes']) == (copy['target']['sha256'], copy['target']['bytes'])
    a, b = Path(copy['source']['path']).stat(), Path(copy['target']['path']).stat()
    assert (a.st_dev, a.st_ino) != (b.st_dev, b.st_ino) and b.st_nlink == 1
    assert stat.S_IMODE(a.st_mode) == copy['sourceMode']
    assert stat.S_IMODE(b.st_mode) == copy['outputMode']
    assert copy['sourceMode'] == copy['outputMode'] in [0o644, 0o755]
recipe, policy, helper = row(refs['recipe']['path']), row(refs['policy']['path']), row(refs['helper']['path'])
assert recipe == refs['recipe'] and policy == refs['policy'] and helper == refs['helper']
text = Path(recipe['path']).read_text()
guards = re.findall(r'\[\[ "\$\(sha256_file "\$consumers_layer_root/policy\.json"\)" == ([a-f0-9]{64}) \]\]', text)
assert guards == ['99f15d4a8f39a3eefeeec738597e57218f2a0dbc8d9febc55ed32f40405402d0'] * 2
assert policy['sha256'] == 'b2421527506774820551e448b8536e43e0a4e402cc6788dc62409c161debdf91'
assert all(x != policy['sha256'] for x in guards)
assert "POLICY_SHA256='" + policy['sha256'] + "'" in Path(helper['path']).read_text()
fresh = list(work.glob('fresh-abi-*.json'))
assert len(fresh) == 1
fresh_row, fresh_data = row(fresh[0]), read(fresh[0])
assert fresh_data['sourceDirExisted'] is fresh_data['buildDirExisted'] is fresh_data['artifactExisted'] is False
assert Path(fresh_data['sourceDir'], 'lib').is_dir()
assert not Path(fresh_data['sourceDir'], '.source-archive-sha256').exists()
assert not Path(fresh_data['buildDir']).exists()
assert not Path(refs['enginePath']).exists() and not Path(refs['enginePath'] + '.build.json').exists()
assert not Path(refs['freezeRoot']).exists()
owner_files = {p.relative_to(out).as_posix(): row(p) for p in out.rglob('*') if p.is_file()}
work_files = {p.relative_to(work).as_posix(): row(p) for p in work.rglob('*') if p.is_file()}
assert len(owner_files) == 7 and len(work_files) == 5
assert not any(p.is_symlink() for p in work.rglob('*'))
report = dict(schemaVersion=1, state='ROOT_OBSERVED_HASH_HMAC357_EARLY_RECIPE_FAILED_V3',
    toolObservation=dict(sessionId=83192, rawExitCode=1), controllerIndex=r['controllerIndex'],
    sourcePeer=r['controllerSourceReview'], integrationSourceIndex=refs['integrationSourceIndex'],
    rootAuthority=authority, config=config, invocation=invocation, observer=row(Path(__file__).resolve()),
    actualBuildResult=result_row, externalParentTerminal=parents['inner'], outerTerminal=parents['outer'],
    externalStdout=row(external / 'stdout.log'), externalStderr=row(external / 'stderr.log'),
    outerStdout=row(caller / 'stdout.log'), outerStderr=row(caller / 'stderr.log'),
    ownerOutputFiles=owner_files, partialWorkFiles=work_files, freshAbiRecord=fresh_row,
    cacheCopiesCompleted=result['cacheCopiesCompleted'], completedCacheCopies=4,
    recipeStarted=True, rawRecipeExitCode=1, recipeLifecycleComplete=True,
    ownedProcessCleanupVerified=True, sourceControlledFinalPreservationPassed=True,
    buildLog=result['buildLog'], originalBashExecutionTraceRetained=False,
    producerRecipe=recipe, producerHelper=helper, producerPolicy=policy,
    policyGuardLiterals=guards, actualPolicySha256=policy['sha256'],
    sourceDerivedFailureCause='First policy SHA guard retains old7c5a99f15 value while new owned policy is b242; helper guard matches; refusal precedes helper CLI/fetch/compiler',
    causeAttributionUsesSourceAndRetainedFileProperties=True,
    sourceArchiveExtracted=False, helperCliReached=False, dependencyFetchReached=False,
    configureReached=False, compilerStarted=False, actualNewEngine=None, actualNewMetadata=None,
    engineExecuted=False, guestExecuted=False, cryptoOperationsInvoked=False,
    freezeInvoked=False, workloadRerun=False, expectedNativeSourceFiles=357,
    expectedExternalEmbeddingSources=3, expectedSelectedWholeManifests=12,
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
print(json.dumps(dict(rootResult=row(path), completedCacheCopies=4, accepted=False)))
