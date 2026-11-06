"""Data-only recheck of the actual three frontend results."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
index = json.loads((HERE / 'evidence-index.json').read_text())
for row in index['copies']:
    data = (HERE / 'evidence' / row['file']).read_bytes()
    assert len(data) == row['bytes'] and hashlib.sha256(data).hexdigest() == row['sha256']
result = json.loads((HERE / 'evidence/result.json').read_text())
assert result['passed'] and len(result['terminals']) == 3
for row in result['terminals']:
    terminal = row['terminal']
    assert terminal['rawExitCode'] == 0 and terminal['allObservedOwnedGroupsGone'] and terminal['parentOwnedGroupGone']
    assert not terminal['timeout'] and not terminal['forcedCleanup']
    assert all(terminal[k] == [] for k in ('errors', 'signals', 'interruptedSignals', 'remainingObservedPids'))
    assert terminal['stderr']['bytes'] == terminal['stdout']['bytes'] == 0
assert result['sourceCompilerDatabaseMonitorPreserved'] and result['dependencyCaptureError'] is None
assert len(result['dependenciesCapturedAfterCompile']) == index['dependencyRecords'] == 3080
assert not result['objectBuilt'] and not result['linked'] and not result['nativeOrGuestExecuted']
print(json.dumps({'passed': True, 'actualSDKFrontends': 3, 'dependencyRecords': 3080, 'guestExecuted': False}))
