"""Root source-staging phase only; no native build or crypto execution."""
from pathlib import Path
import hashlib
import importlib.util
import json
import os

R = Path('/Users/dan/dev/StarlingMonkey')
K = R / 'tests/node-compat/foundation-crypto'
P = K / 'node-crypto-hash-hmac-stage-candidate-v2'
PEER = K / 'independent-node-crypto-hash-hmac-stage-v2-source-review-v1'
PYTHON = Path('/Applications/Xcode.app/Contents/Developer/Library/Frameworks/Python3.framework/Versions/3.9/bin/python3.9')
GIT = Path('/Applications/Xcode.app/Contents/Developer/usr/bin/git')


def d(path):
    path = Path(path)
    assert path.is_file() and not path.is_symlink()
    h = hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda: f.read(4194304), b''):
            h.update(b)
    return dict(path=str(path), sha256=h.hexdigest(), bytes=path.stat().st_size)


def read(path):
    return json.loads(Path(path).read_bytes())


def write(path, value):
    with Path(path).open('x') as f:
        json.dump(value, f, indent=2)
        f.write('\n')
        f.flush()
        os.fsync(f.fileno())


def family(path):
    path = Path(path)
    names = {'index.json'}
    for row in read(path / 'index.json')['files']:
        n = row['path']
        assert n not in names and not Path(n).is_absolute() and '..' not in Path(n).parts
        names.add(n)
        actual = d(path / n)
        assert (actual['sha256'], actual['bytes']) == (row['sha256'], row['bytes'])
    assert not any(p.is_symlink() for p in path.rglob('*'))
    assert {p.relative_to(path).as_posix() for p in path.rglob('*') if p.is_file()} == names
    return d(path / 'index.json')


own = family(P)
assert own['sha256'] == 'ed0a32411eb33c5a1ab56ba96d27123fa3e83c31e962ebe81fbcaf066b1b4fbe'
peer_index = family(PEER)
assert peer_index['sha256'] == '11e462eaa19f1cfc043a5515f29427a31c446d1bf6506a2ee2194b36d18268ce'
proof = read(PEER / 'results.json')
assert proof['state'] == 'INDEPENDENT_NODE_CRYPTO_HASH_HMAC357_STAGE_SOURCE_REVIEW_PASSED_V2'
assert proof['controllerSourceIndexSha256'] == own['sha256']
assert proof['integrationSourceIndexSha256'] == '7c5a8468639f8bfab3b06f8a75e8cb74373747562b9826450397f90db2dc2429'
assert proof['sourceOnly'] is proof['sourceReviewPassed'] is True
for key in ['ownerActionsInvoked', 'hostActionsInvoked', 'sourceStageActionsInvoked',
            'nativeBuildActionsInvoked', 'cryptoOperationsInvoked']:
    assert proof[key] is False
refs = read(P / 'references.json')
root = read(P / 'root-authority.template.json')
root.pop('requiredIssuedState')
root.update(state='ROOT_REVIEWED_NODE_CRYPTO_HASH_HMAC357_SOURCE_STAGE_V2',
            sourceStageAllowed=True, stageControllerIndex=own,
            stageControllerEntry=d(P / 'controller.py'),
            stageControllerReview=dict(index=peer_index, result=d(PEER / 'results.json')),
            gitBinary=d(GIT), pythonExecutable=d(PYTHON))
for key in ['configuredSourceRoot', 'workRoot', 'freezeRoot', 'externalOutputRoot', 'stageJournal']:
    path = Path(root[key])
    assert not path.exists() and not path.is_symlink()
prefix = K / 'node-crypto-hash-hmac-stage-v2'
authority = Path(str(prefix) + '-root-authority.json')
write(authority, root)
config = read(P / 'config.template.json')
config.pop('requiredIssuedState')
config.update(state='NODE_CRYPTO_HASH_HMAC357_STAGE_CONFIG_V2', rootAuthority=d(authority), controllerIndex=own)
config_path = Path(str(prefix) + '-root-config.json')
write(config_path, config)
argv = [str(PYTHON), '-B', '-I', str(P / 'controller.py'),
        json.dumps(d(config_path), separators=(',', ':'))]
write(str(prefix) + '-root-invocation.json', dict(
    schemaVersion=1, sourceController=own, sourcePeer=root['stageControllerReview'],
    integrationSource=root['sourceIndex'], integrationPeer=root['integrationSourceReview'],
    rootAuthority=d(authority), config=d(config_path), launcher=d(Path(__file__).resolve()),
    python=d(PYTHON), git=d(GIT), actualArgv=argv, originalOuterDeadlineSeconds=1200,
    originalInnerDeadlineSeconds=600, stageOnly=True, nativeBuildAllowed=False,
    engineExecutionAllowed=False, cryptoOperationsAllowed=False))
family(Path(refs['monitorIndex']['path']).parent)
assert d(refs['monitorEntry']['path']) == refs['monitorEntry']
spec = importlib.util.spec_from_file_location('genuine0af_hash_hmac_stage_root', refs['monitorEntry']['path'])
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
caller = Path(root['externalOutputRoot'] + '-root-caller')
assert not caller.exists()
caller.mkdir(mode=0o700)
env = {k: os.environ[k] for k in ['HOME', 'home', 'CODEX_HOME', 'USER', 'LOGNAME', 'TMPDIR'] if k in os.environ}
env.update(PATH='/usr/bin:/bin:/usr/sbin:/sbin', PYTHONDONTWRITEBYTECODE='1')
write(caller / 'environment-policy.json', dict(keys=sorted(env), valuesRetained=False,
                                               homesPreserved=True, gitStartupScrubPerformedByReviewedWorker=True))
print(json.dumps(dict(event='root-hash-hmac-stage-start', invocation=d(str(prefix) + '-root-invocation.json'))), flush=True)
t = m.monitor(argv, str(R), env, caller, 1200, d(authority))
clean = (t['rawExitCode'] == 0 and t['parentOwnedGroupGone'] is t['allObservedOwnedGroupsGone'] is True
         and t['timeout'] is t['forcedCleanup'] is False and all(t[k] == [] for k in
             ['errors', 'signals', 'interruptedSignals', 'remainingObservedPids']))
print(json.dumps(dict(event='root-hash-hmac-stage-terminal', rawExitCode=t['rawExitCode'],
                      clean=clean, terminal=d(caller / 'terminal.json'))), flush=True)
raise SystemExit(0 if clean else 1)
