"""Root-issued preliminary pure control, separate from full lifecycle adoption."""
from pathlib import Path
import hashlib
import importlib.util
import json
import os

REPO = Path('/Users/dan/dev/StarlingMonkey')
SCHEDULER = REPO / 'tests/node-compat/foundation-scheduler'
SOURCE = SCHEDULER / 'combined-native-pure-runtime-control-candidate-v1'
PEER = SCHEDULER / 'independent-combined355-pure-runtime-control-source-review-v1'


def descriptor(path):
    path = Path(path)
    assert path.is_file() and not path.is_symlink()
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(4194304), b''):
            h.update(block)
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
    rows = read(path / 'index.json')['files']
    names = {'index.json'}
    for row in rows:
        n = row['path']
        assert n not in names and not Path(n).is_absolute() and '..' not in Path(n).parts
        names.add(n)
        actual = descriptor(path / n)
        assert (actual['sha256'], actual['bytes']) == (row['sha256'], row['bytes'])
    assert not any(p.is_symlink() for p in path.rglob('*'))
    assert {p.relative_to(path).as_posix() for p in path.rglob('*') if p.is_file()} == names
    return descriptor(path / 'index.json')


own = family(SOURCE)
assert own['sha256'] == '8feef25e0b40980877ad3d7b335256d937ed7603bd2a7e65a159b06fa0e0f41f'
peer_index = family(PEER)
assert peer_index['sha256'] == 'ca26fa82c40332061dae1c360edcb5f2aa6be5c0fa02e20dd999c42f61bdb6f7'
proof = read(PEER / 'results.json')
contract = read(SOURCE / 'future-source-review-contract.json')
assert proof['state'] == contract['requiredState'] and proof['sourceIndexSha256'] == own['sha256']
for key, value in contract['requiredFixedValues'].items():
    assert type(proof[key]) is type(value) and proof[key] == value
refs = read(SOURCE / 'references.json')
output = Path(refs['outputRoot'])
external = Path(str(output) + '-external-root')
caller = Path(str(output) + '-root-caller')
for path in [output, external, caller]:
    assert not path.exists() and not path.is_symlink()
root = read(SOURCE / 'future-root-authority.template.json')
root.pop('requiredIssuedState')
root.update(state='ROOT_REVIEWED_COMBINED355_PRELIMINARY_PURE_CONTROL_V1',
            sourceIndex=own,
            sourceIndependentReview=dict(index=peer_index, result=descriptor(PEER / 'results.json')),
            entry=descriptor(SOURCE / 'entry.mjs'), externalController=descriptor(SOURCE / 'external.py'),
            outputRoot=str(output), externalRoot=str(external))
for key in ['actualPureReview', 'actualPureContract', 'component', 'fixtureSource', 'readOnlyConfig']:
    root[key] = refs[key]
for key in ['parentNativeReadOnlyApiAllowed', 'nodeFixtureOracleAllowed',
            'pureGeneratedImportAllowed', 'pureRunAllowed', 'stockWasmtimeAllowed']:
    root[key] = True
prefix = SCHEDULER / 'combined-native-pure-runtime-control-v1'
authority_path = Path(str(prefix) + '-root-authority.json')
write(authority_path, root)
config = read(SOURCE / 'future-config.template.json')
config.update(sourceIndex=own, rootAuthority=descriptor(authority_path))
config_path = Path(str(prefix) + '-root-config.json')
write(config_path, config)
assert descriptor(refs['python']['path']) == refs['python']
assert descriptor(refs['node']['path']) == refs['node']
assert descriptor(refs['wasmtime']['path']) == refs['wasmtime']
argv = [refs['python']['path'], '-B', '-I', str(SOURCE / 'external.py'),
        json.dumps(descriptor(config_path), separators=(',', ':'))]
invocation = dict(schemaVersion=1, sourceIndex=own, sourcePeer=root['sourceIndependentReview'],
                  rootAuthority=descriptor(authority_path), config=descriptor(config_path),
                  launcher=descriptor(Path(__file__).resolve()), actualArgv=argv,
                  originalOuterDeadlineSeconds=1800, originalInnerDeadlineSeconds=1200,
                  ownedChildDeadlineMs=60000, preliminaryPureControlOnly=True,
                  nodeOracleCalls=3, componentCalls=7, resourceRuntimeAllowed=False,
                  keyOrCryptoAllowed=False, fullRoadmapComplete=False)
write(str(prefix) + '-root-invocation.json', invocation)
family(Path(refs['monitorIndex']['path']).parent)
assert descriptor(refs['monitorEntry']['path']) == refs['monitorEntry']
spec = importlib.util.spec_from_file_location('genuine0af_pure_control_root_observer', refs['monitorEntry']['path'])
monitor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(monitor)
caller.mkdir(mode=0o700)
env = {k: os.environ[k] for k in ['HOME', 'USER', 'LOGNAME', 'TMPDIR'] if k in os.environ}
env.update(PATH='/usr/bin:/bin:/usr/sbin:/sbin', PYTHONDONTWRITEBYTECODE='1')
write(caller / 'environment-policy.json', dict(keys=sorted(env), valuesRetained=False))
print(json.dumps(dict(event='root-preliminary-pure-control-start', invocation=descriptor(str(prefix) + '-root-invocation.json'))), flush=True)
terminal = monitor.monitor(argv, str(REPO), env, caller, 1800, descriptor(authority_path))
clean = (terminal['rawExitCode'] == 0 and terminal['parentOwnedGroupGone'] is True
         and terminal['allObservedOwnedGroupsGone'] is True and not terminal['timeout']
         and not terminal['forcedCleanup'] and all(terminal[k] == [] for k in
             ['errors', 'signals', 'interruptedSignals', 'remainingObservedPids']))
print(json.dumps(dict(event='root-preliminary-pure-control-terminal', rawExitCode=terminal['rawExitCode'],
                      clean=clean, terminal=descriptor(caller / 'terminal.json'))), flush=True)
raise SystemExit(0 if clean else 1)
