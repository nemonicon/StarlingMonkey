"""Collect the completed actual compiler run; never rerun it or repair its driver exit."""
import hashlib
import json
import shlex
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXTERNAL = Path('/private/tmp/starling-node-compat/buffer-concat-sdk-v1')


def row(path):
    data = Path(path).read_bytes()
    return {'path': str(path), 'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)}


authority = json.loads((EXTERNAL / 'authority.json').read_text())
terminal = json.loads((EXTERNAL / 'terminal.json').read_text())
assert terminal['rawExitCode'] == 0
assert terminal['parentOwnedGroupGone'] and terminal['allObservedOwnedGroupsGone']
assert not terminal['forcedCleanup'] and not terminal['timeout']
for key in ('errors', 'signals', 'interruptedSignals', 'remainingObservedPids'):
    assert terminal[key] == []
for key in ('stdout', 'stderr'):
    assert row(Path(terminal[key]['path'])) == terminal[key]
    assert terminal[key]['bytes'] == 0
for key in ('sourceIndex', 'source', 'database', 'compiler', 'monitor'):
    assert row(Path(authority[key]['path'])) == authority[key]
target, dependency_text = (EXTERNAL / 'dependencies.d').read_text().replace('\\\n', '').split(':', 1)
assert target == 'buffer-concat-syntax'
deps = [row(Path(authority['originalCommand']['directory']) / path) for path in shlex.split(dependency_text)]
result = {'schemaVersion': 1, 'state': 'BUFFER_CONCAT_SDK_SYNTAX_READ_ONLY_COLLECTION_V1',
          'compilerSyntaxPassed': True, 'rawCompilerExitCode': 0, 'originalDriverExitCode': 1,
          'originalDriverFailure': 'Post-compiler NameError: key was missing from the preservation comprehension.',
          'sourceIndexSourceDatabaseCompilerAndMonitorPreserved': True,
          'allOwnedGroupsClean': True, 'compilerReplayPerformed': False,
          'dependenciesCapturedAfterCompile': deps,
          'scope': 'Actual fsyntax-only. Header hashes captured after compile; not a whole-SDK before/after preservation proof.',
          'engineLinked': False, 'nativeKernelExecuted': False, 'guestExecuted': False,
          'authority': row(EXTERNAL / 'authority.json'), 'terminal': row(EXTERNAL / 'terminal.json')}
output = HERE / 'results'
output.mkdir()
for name in ('authority.json', 'terminal.json', 'started.json', 'dependencies.d', 'stdout.log', 'stderr.log'):
    shutil.copyfile(EXTERNAL / name, output / name)
(output / 'results.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({'compilerSyntaxPassed': True, 'originalDriverExitCode': 1,
                  'dependencies': len(deps), 'compilerReplayed': False,
                  'result': row(output / 'results.json')}))
