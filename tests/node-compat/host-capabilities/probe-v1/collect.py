"""Copy small byte-exact probe evidence. No compiler, host or guest execution."""
import hashlib
import json
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = Path('/private/tmp/starling-node-compat')
OUTPUT = HERE / 'results'


def row(path):
    data = path.read_bytes()
    return {'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)}


OUTPUT.mkdir()
copies = []


def copy(path, target):
    target = OUTPUT / target
    target.parent.mkdir(parents=True, exist_ok=True)
    before = row(path)
    shutil.copyfile(path, target)
    assert row(target) == row(path) == before
    copies.append({'original': str(path), 'file': str(target.relative_to(OUTPUT)), **before})


build = BASE / 'deployment-probe-v3'
audit = json.loads((build / 'component-audit.json').read_text())
assert audit['passed'] and not audit['preview1Imports'] and not audit['adapterUsed']
for name in ('component-audit.json', 'build-authority.json', 'build-steps.json', 'step-4/stdout.log'):
    copy(build / name, Path('build') / name)
for step in range(6):
    for name in ('terminal.json', 'stderr.log'):
        copy(build / ('step-' + str(step)) / name, Path('build') / ('step-' + str(step)) / name)
hosts = []
for name in ('deployment-host-wasmtime-v1', 'deployment-host-wasmcloud-v1'):
    root = BASE / name
    monitor = BASE / (name + '-monitor')
    result = json.loads((root / 'result.json').read_text())
    terminal = json.loads((monitor / 'terminal.json').read_text())
    assert result['passed'] and result['realComponentExecuted'] and not result['nextExecuted'] and not result['starlingMonkeyExecuted']
    assert terminal['rawExitCode'] == 0 and terminal['allObservedOwnedGroupsGone'] and terminal['parentOwnedGroupGone']
    assert not terminal['timeout'] and not terminal['forcedCleanup']
    for key in ('errors', 'signals', 'interruptedSignals', 'remainingObservedPids'):
        assert terminal[key] == []
    for path in sorted(root.iterdir()):
        if path.is_file(): copy(path, Path(name) / path.name)
    for path in sorted(monitor.iterdir()):
        if path.is_file(): copy(path, Path(name) / 'monitor' / path.name)
    if (root / 'project/.wash/config.json').exists():
        copy(root / 'project/.wash/config.json', Path(name) / 'project/.wash/config.json')
    hosts.append({'name': name, 'result': str(Path(name) / 'result.json'),
                  'rawExitCode': 0, 'realComponentExecuted': True, 'starlingMonkeyExecuted': False})
for name in ('deployment-probe-v1', 'deployment-probe-v2'):
    root = BASE / name
    for file in ('build-authority.json', 'build-steps.json', 'step-0/stderr.log', 'step-0/terminal.json'):
        copy(root / file, Path('history') / name / file)
summary = {'schemaVersion': 1, 'state': 'ACTUAL_STANDARD_WASI_HOST_DEPLOYMENT_EVIDENCE_V1',
           'component': audit['component'], 'emittedImports': audit['imports'], 'emittedExports': audit['exports'],
           'hosts': hosts, 'copies': copies,
           'history': ['v1 compiler refused an undeclared tuple-free helper; use actual list-free API.',
                       'v2 six native/tool commands succeeded, then whole-text Preview1 audit hit DWARF names; v3 audits actual import declarations and explicitly drops stream IO errors.'],
           'limitations': ['C deployment probe, not StarlingMonkey or Next.',
                           'Readonly app enforced by owned Unix modes, not per-mount narrowed WASI rights.',
                           'Warm wasmCloud normal-workload configuration remains unexecuted; wash dev main is ephemeral.']}
(OUTPUT / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
print(json.dumps({'files': len(copies), 'bytes': sum(item['bytes'] for item in copies), 'hosts': len(hosts), 'nextExecuted': False}))
