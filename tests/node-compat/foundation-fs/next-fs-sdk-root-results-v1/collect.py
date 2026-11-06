"""Retain actual SDK result and small raw evidence; no compiler replay."""
import hashlib
import json
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
LIVE = Path('/private/tmp/starling-node-compat/next-fs-sdk-syntax-v1')
OUT = HERE / 'evidence'
OUT.mkdir()
copies = []


def copy(path, name):
    data = path.read_bytes()
    target = OUT / name; target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(path, target)
    assert target.read_bytes() == data == path.read_bytes()
    copies.append({'original': str(path), 'file': str(name), 'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)})


result = json.loads((LIVE / 'result.json').read_text())
assert result['passed'] and result['error'] is None and result['dependencyCaptureError'] is None
assert result['sourceCompilerDatabaseMonitorPreserved']
assert not result['objectBuilt'] and not result['linked'] and not result['nativeOrGuestExecuted']
copy(LIVE / 'result.json', Path('result.json'))
for unit in ('next-fs', 'registration', 'deployed-policy'):
    for name in ('started.json', 'terminal.json', 'stdout.log', 'stderr.log'):
        path = LIVE / unit / name
        if path.exists(): copy(path, Path(unit) / name)
    copy(LIVE / (unit + '.d'), Path(unit) / 'dependencies.d')
outer = Path(str(LIVE) + '-root-monitor')
for name in ('started.json', 'terminal.json', 'stdout.log', 'stderr.log'):
    path = outer / name
    if path.exists(): copy(path, Path('root-monitor') / name)
(HERE / 'evidence-index.json').write_text(json.dumps({'schemaVersion': 1, 'state': 'ACTUAL_FS_THREE_SDK_FRONTENDS_RETAINED',
    'copies': copies, 'dependencyRecords': len(result['dependenciesCapturedAfterCompile']),
    'dependencyScope': result['dependencyScope'], 'guestExecuted': False}, indent=2) + '\n')
print(json.dumps({'copied': len(copies), 'bytes': sum(r['bytes'] for r in copies)}))
