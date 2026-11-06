"""Host Node controls only: no guest/engine/crypto-profile admission."""
from pathlib import Path
import hashlib
import importlib.util
import json
import os

R = Path('/Users/dan/dev/StarlingMonkey')
K = R / 'tests/node-compat/foundation-crypto'
P = K / 'node-crypto-hash-hmac-runtime-fixtures-v2'
OUT = Path('/private/tmp/starling-node-compat/node-crypto-hash-hmac-node-oracle-v1')
NODE = Path('/private/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node')
PYTHON = Path('/Applications/Xcode.app/Contents/Developer/Library/Frameworks/Python3.framework/Versions/3.9/bin/python3.9')
MONITOR = K / 'ownership-gc-build-controller-candidate-v1'


def row(path):
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
    names = {'index.json'}
    for r in read(path / 'index.json')['files']:
        name = r['path']
        assert name not in names and not Path(name).is_absolute() and '..' not in Path(name).parts
        names.add(name)
        assert row(path / name) == dict(r, path=str(path / name))
    assert {p.relative_to(path).as_posix() for p in path.rglob('*') if p.is_file()} == names
    assert not any(p.is_symlink() for p in path.rglob('*'))
    return row(path / 'index.json')


source_index = family(P)
assert source_index['sha256'] == '16b195e6c6d82f955dac92f1f4f209ffd2fd8791866734aa65379231a8ca5c2d'
node, python, monitor = row(NODE), row(PYTHON), row(MONITOR / 'monitor.py')
assert node['sha256'] == 'e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0'
assert python['sha256'] == '4a81cbef89c3cded9c9435c2faf747823dfed9ca9a0da82df374834a18c70dc8'
assert monitor['sha256'] == '86913867251bc889701859ca6a361ccf9c17288a6a3bfc7a5c8d8e5bbe5c4cbe'
family(MONITOR)
probe = row(K / 'node-crypto-hash-hmac-node-oracle-v1-probe.mjs')
fixture = row(P / 'fixture.mjs')
assert fixture['sha256'] == '79530f7745174021dd6a86ed05cec66cf9cb96292616d5aba11252db155cf46e'
assert not OUT.exists()
authority = K / 'node-crypto-hash-hmac-node-oracle-v1-root-authority.json'
write(authority, dict(schemaVersion=1, state='ROOT_HOST_NODE22_HASH_HMAC_ORACLE_V1',
    sourceIndex=source_index, fixture=fixture, node=node, probe=probe,
    outputRoot=str(OUT), retainedCalls=3, deadlineSeconds=60,
    hostHashHmacOracleAllowed=True, guestOrEngineAllowed=False,
    nativeBuildAllowed=False, componentAllowed=False, gcOomResetAllowed=False,
    runtimeAcceptanceClaim=False, operationalAdmission=False))
argv = [str(NODE), probe['path'], json.dumps(dict(node=node, fixture=fixture), separators=(',', ':'))]
invocation = K / 'node-crypto-hash-hmac-node-oracle-v1-root-invocation.json'
write(invocation, dict(schemaVersion=1, rootAuthority=row(authority), sourceIndex=source_index,
    launcher=row(Path(__file__).resolve()), actualArgv=argv, deadlineSeconds=60,
    guestExecuted=False, hostOracleOnly=True))
OUT.mkdir(mode=0o700)
env = {k: os.environ[k] for k in ['HOME', 'home', 'CODEX_HOME', 'USER', 'LOGNAME', 'TMPDIR'] if k in os.environ}
env.update(PATH='/usr/bin:/bin:/usr/sbin:/sbin', PYTHONDONTWRITEBYTECODE='1')
spec = importlib.util.spec_from_file_location('genuine0af_host_crypto_oracle', monitor['path'])
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
print(json.dumps(dict(event='root-host-node-oracle-start', invocation=row(invocation))), flush=True)
t = m.monitor(argv, str(R), env, OUT, 60, row(authority))
clean = (t['rawExitCode'] == 0 and t['parentOwnedGroupGone'] is t['allObservedOwnedGroupsGone'] is True
         and t['timeout'] is t['forcedCleanup'] is False and all(t[k] == [] for k in
            ['errors', 'signals', 'interruptedSignals', 'remainingObservedPids']))
assert family(P) == source_index and row(NODE) == node
print(json.dumps(dict(event='root-host-node-oracle-terminal', rawExitCode=t['rawExitCode'],
    clean=clean, terminal=row(OUT / 'terminal.json'))), flush=True)
raise SystemExit(0 if clean else 1)
