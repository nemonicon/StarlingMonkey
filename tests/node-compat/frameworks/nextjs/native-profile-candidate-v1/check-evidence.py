"""Portable, data-only recheck of joined Source and SDK observations."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent / 'syntax-results-v2'
x = json.loads((HERE / 'summary.json').read_text())
assert x['state'] == 'ACTUAL_NEXT430_THIRTEEN_FRONTEND_PORTABLE_EVIDENCE'
assert x['passed'] and x['compilerUnits'] == 13 and x['nativeSourceFiles'] == 430
for r in x['copies']:
    data = (HERE / r['file']).read_bytes()
    assert len(data) == r['bytes'] and hashlib.sha256(data).hexdigest() == r['sha256'], r['file']
result = json.loads((HERE / 'result.json').read_text())
assert result['passed'] and result['sourceAndInheritedInputsBeforeAfterUnchanged']
assert not result['nativeOrGuestExecuted'] and not result['objectOrLinkProduced']
for r in result['terminals']:
    t = r['terminal']
    assert t['rawExitCode'] == 0 and t['stdout']['bytes'] == t['stderr']['bytes'] == 0
    assert t['parentOwnedGroupGone'] and t['allObservedOwnedGroupsGone']
    assert not t['timeout'] and not t['forcedCleanup']
    assert all(t[k] == [] for k in ('errors','signals','interruptedSignals','remainingObservedPids'))
assert len(x['dependencies']) == x['dependencyObservations'] == 13508
assert len({r['resolvedPath'] for r in x['dependencies']}) == x['uniqueResolvedDependencies'] == 1204
composition = json.loads((HERE / 'composition.json').read_text())
assert len(composition['files']) == 430 and not composition['engineBuilt'] and not composition['legacyMetadataProjected']
installed = json.loads((HERE / 'installed/result.json').read_text())
assert installed['passed'] and installed['sourceBeforeAfterUnchanged']
assert len(installed['commands']) == 8 and all(r['rawExitCode'] == 0 for r in installed['commands'])
print(json.dumps({'passed': True, 'sourceFiles': 430, 'installedChecks': 8, 'actualSDKFrontends': 13,
                  'dependencyObservations': 13508, 'engineOrGuestExecuted': False}))
