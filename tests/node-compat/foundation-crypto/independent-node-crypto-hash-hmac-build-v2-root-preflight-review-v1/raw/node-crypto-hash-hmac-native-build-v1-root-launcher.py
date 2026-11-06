"""Root build-only launcher; requires final independent Source review digests.

It cannot freeze, execute an engine, run crypto or admit a production profile.
"""
from pathlib import Path
import hashlib
import importlib.util
import json
import os
import re
import sys

R = Path('/Users/dan/dev/StarlingMonkey')
K = R / 'tests/node-compat/foundation-crypto'
P = K / 'node-crypto-hash-hmac-native-controller-candidate-v1'
PEER = K / 'independent-node-crypto-hash-hmac-native-controller-source-review-v1'


def row(path):
    p = Path(path)
    assert p.is_file() and not p.is_symlink()
    h = hashlib.sha256()
    with p.open('rb') as stream:
        for b in iter(lambda: stream.read(4194304), b''):
            h.update(b)
    return dict(path=str(p), sha256=h.hexdigest(), bytes=p.stat().st_size)


def read(path):
    return json.loads(Path(path).read_bytes())


def family(base):
    names = {'index.json'}
    for r in read(base / 'index.json')['files']:
        name = r['path']
        assert name not in names and not Path(name).is_absolute() and '..' not in Path(name).parts
        names.add(name)
        assert row(base / name) == dict(r, path=str(base / name))
    assert not any(p.is_symlink() for p in base.rglob('*'))
    assert {p.relative_to(base).as_posix() for p in base.rglob('*') if p.is_file()} == names
    return row(base / 'index.json')


def write(path, value):
    with Path(path).open('x') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())


assert len(sys.argv) == 3 and all(re.fullmatch('[a-f0-9]{64}', x) for x in sys.argv[1:])
own = family(P)
assert own['sha256'] == '9e5195b90e20708a8a398fa9013eba867e2f2e5e1d18c2f5b76ed5bbc3c01d3b'
peer_index = family(PEER)
assert peer_index['sha256'] == sys.argv[1]
peer_result = row(PEER / 'results.json')
assert peer_result['sha256'] == sys.argv[2]
proof = read(peer_result['path'])
assert proof['state'] == 'INDEPENDENT_NODE_CRYPTO_HASH_HMAC357_NATIVE_CONTROLLER_SOURCE_REVIEW_PASSED_V1'
assert proof['controllerSourceIndexSha256'] == own['sha256']
assert proof['sourceOnly'] is proof['sourceReviewPassed'] is True
for key in ['ownerActionsInvoked', 'hostActionsInvoked', 'nativeBuildActionsInvoked',
            'freezeActionsInvoked', 'cryptoOperationsInvoked']:
    assert proof[key] is False
refs = read(P / 'references.json')
assert proof['integrationSourceIndexSha256'] == refs['integrationSourceIndex']['sha256']
assert proof['actualStageReviewIndexSha256'] == refs['actualStageReview']['index']['sha256']
policy = read(P / 'root-environment-policy.json')
assert proof['requiredRootEnvironmentPolicy'] == policy
for path in [refs['workRoot'], refs['freezeRoot'], refs['buildOutputRoot'],
             refs['buildExternalRoot'], refs['observerBase'] + '-build']:
    assert not Path(path).exists() and not Path(path).is_symlink()
source_peer = dict(index=peer_index, result=peer_result)
root = read(P / 'future-build-root-authority.template.json')
root.update(state='ROOT_REVIEWED_NODE_CRYPTO_HASH_HMAC357_NATIVE_PHASE_V1',
            phase='build', variant='normal-off', controllerIndex=own,
            controllerEntry=row(P / 'controller.py'), controllerSourceReview=source_peer,
            rootEnvironmentPolicy=policy, rootLauncherRequired=True,
            nativeBuildAllowed=True, freezeAllowed=False,
            readOnlySourceAdmissionAllowed=False, postBuildNinjaListingAllowed=False,
            externalParentDeadlineSeconds=7200, externalOutputRoot=refs['buildExternalRoot'],
            buildOutputRoot=refs['buildOutputRoot'], rootObserverOutputRoot=refs['observerBase'] + '-build',
            parallelBuilds=1, requiredStartFreeBytes=2147483648,
            stopBelowFreeBytes=838860800, nativeSourceFiles=357,
            externalEmbeddingSources=3, selectedManifestCount=12, rawMetadataFields=83,
            hashHmacEnabled=True, auditedBorrowEnabled=False, entropyPolicy='off', defaultCopyOnly=True,
            actualFreezeReview=None)
for key in ['buildEnvironment', 'cachePlan', 'recipe', 'helper', 'policy', 'monitorEntry', 'lifecycleEntry']:
    root[key] = refs[key]
for key in ['debugAllowed', 'gcAllowed', 'oomAllowed', 'borrowAllowed', 'engineExecutionAllowed',
            'keyOrCryptoAllowed', 'guestAllowed', 'componentAllowed', 'exportAllowed',
            'bootstrapAllowed', 'globalMutationAllowed', 'metadataProjectionAllowed',
            'liveEvpSnapshotAdmission', 'operationalAdmission', 'runtimeAcceptanceClaim', 'timingAllowed']:
    root[key] = False
prefix = K / 'node-crypto-hash-hmac-native-build-v1'
authority = Path(str(prefix) + '-root-authority.json')
write(authority, root)
config = read(P / 'future-build-config.template.json')
config.update(state='NODE_CRYPTO_HASH_HMAC357_NATIVE_CONFIG_V1', controllerIndex=own,
              rootAuthority=row(authority))
config_path = Path(str(prefix) + '-root-config.json')
write(config_path, config)
argv = [refs['python']['path'], '-B', '-I', str(P / 'controller.py'), 'launcher',
        json.dumps(row(config_path), separators=(',', ':'))]
invocation = Path(str(prefix) + '-root-invocation.json')
write(invocation, dict(schemaVersion=1, controllerIndex=own, sourcePeer=source_peer,
    rootAuthority=row(authority), config=row(config_path), launcher=row(Path(__file__).resolve()),
    actualArgv=argv, originalOuterDeadlineSeconds=7500, originalInnerDeadlineSeconds=7200,
    buildOnly=True, freezeAllowed=False, engineExecutionAllowed=False,
    cryptoOperationsAllowed=False, liveEvpSnapshotAdmission=False, operationalAdmission=False))
family(Path(refs['monitorIndex']['path']).parent)
assert row(refs['monitorEntry']['path']) == refs['monitorEntry']
assert row(refs['python']['path']) == refs['python']
spec = importlib.util.spec_from_file_location('genuine0af_hash_hmac_native_root', refs['monitorEntry']['path'])
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
caller = Path(refs['observerBase'] + '-build-root-caller')
assert not caller.exists()
caller.mkdir(mode=0o700)
env = {k: os.environ[k] for k in ['HOME', 'home', 'CODEX_HOME', 'USER', 'LOGNAME', 'TMPDIR'] if k in os.environ}
env.update(PATH=refs['hostPath'], PYTHONDONTWRITEBYTECODE='1')
write(caller / 'environment-policy.json', dict(keys=sorted(env), valuesRecorded=False))
print(json.dumps(dict(event='root-hash-hmac-native-build-start', invocation=row(invocation))), flush=True)
t = m.monitor(argv, str(R), env, caller, 7500, row(authority))
clean = (t['rawExitCode'] == 0 and t['parentOwnedGroupGone'] is t['allObservedOwnedGroupsGone'] is True
         and t['timeout'] is t['forcedCleanup'] is False and all(t[k] == [] for k in
            ['errors', 'signals', 'interruptedSignals', 'remainingObservedPids']))
print(json.dumps(dict(event='root-hash-hmac-native-build-terminal', rawExitCode=t['rawExitCode'],
                      clean=clean, terminal=row(caller / 'terminal.json'))), flush=True)
raise SystemExit(0 if clean else 1)
