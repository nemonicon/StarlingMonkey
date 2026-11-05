"""Capture only this packet's read/hash/model checker; no owner action."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
label = sys.argv[1] if len(sys.argv) == 2 else 'source-checks'
assert label in ('source-checks', 'final')
out = HERE / 'evidence' / label
out.mkdir(parents=True, exist_ok=False)
argv = [sys.executable, '-I', str(HERE / 'check-source.py')]
completed = subprocess.run(argv, cwd=HERE, capture_output=True, timeout=60)
rows = {}
for name, data in [('stdout.json', completed.stdout), ('stderr.log', completed.stderr)]:
    (out / name).write_bytes(data)
    rows[name] = {'path': str(out / name), 'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)}
(out / 'terminal.json').write_text(json.dumps({'schemaVersion': 1, 'argv': argv,
    'cwd': str(HERE), 'rawExitCode': completed.returncode, 'streams': rows,
    'sourceDataModelsOnly': True, 'ownerModulesOrActionsInvoked': False}, indent=2) + '\n')
print(json.dumps({'rawExitCode': completed.returncode, 'evidence': str(out)}))
raise SystemExit(completed.returncode)
