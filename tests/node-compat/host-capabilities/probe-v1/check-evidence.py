"""Recheck retained, byte-exact deployment evidence; runs no host or guest."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent / 'results'
summary = json.loads((HERE / 'summary.json').read_text())
assert summary['state'] == 'ACTUAL_STANDARD_WASI_HOST_DEPLOYMENT_EVIDENCE_V1'
for item in summary['copies']:
    data = (HERE / item['file']).read_bytes()
    assert len(data) == item['bytes'] and hashlib.sha256(data).hexdigest() == item['sha256'], item['file']
expected = sorted(['wasi:' + name + '@0.2.10' for name in (
    'cli/environment', 'clocks/monotonic-clock', 'clocks/wall-clock',
    'filesystem/preopens', 'filesystem/types', 'http/types',
    'io/error', 'io/poll', 'io/streams', 'random/random')])
assert summary['emittedImports'] == expected
assert summary['emittedExports'] == ['wasi:http/incoming-handler@0.2.10']
for host in summary['hosts']:
    result = json.loads((HERE / host['result']).read_text())
    terminal = json.loads((HERE / host['name'] / 'monitor/terminal.json').read_text())
    assert result['passed'] and result['realComponentExecuted']
    assert not result['nextExecuted'] and not result['starlingMonkeyExecuted']
    assert result['component'] == summary['component'] and result['imports'] == expected
    assert terminal['rawExitCode'] == 0 and terminal['allObservedOwnedGroupsGone'] and terminal['parentOwnedGroupGone']
    assert not terminal['timeout'] and not terminal['forcedCleanup']
    assert all(terminal[k] == [] for k in ('errors', 'signals', 'interruptedSignals', 'remainingObservedPids'))
wt = json.loads((HERE / 'deployment-host-wasmtime-v1/result.json').read_text())
wc = json.loads((HERE / 'deployment-host-wasmcloud-v1/result.json').read_text())
assert [[r['body']['counter'] for r in mode['responses']] for mode in wt['modes']] == [[1, 1, 1], [1, 2, 3]]
assert [r['body']['counter'] for r in wc['responses']] == [1, 1, 1]
print(json.dumps({'passed': True, 'copiedFiles': len(summary['copies']), 'hostModes': 3,
                  'realComponentEvidence': True, 'starlingMonkeyOrNextExecution': False}))
