"""Record pure preparation checks only; never call activation main."""
from pathlib import Path
import ast
import hashlib
import json
import subprocess
import sys

HERE = Path(__file__).resolve().parent
NODE = Path('/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node')
assert hashlib.sha256(NODE.read_bytes()).hexdigest() == 'e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0'
assert not (HERE.parent / 'production-regression-activated-v1').exists()
assert not (HERE.parent / 'production-regression-activated-v1.staging').exists()
for name in ('activate.py', 'authority.py', 'test-source.py', 'record-checks.py'):
    ast.parse((HERE / name).read_text(), filename=name)
commands = [[sys.executable, '-B', str(HERE / 'test-source.py')],
            [str(NODE), '--check', str(HERE / 'native-preflight.template.mjs')]]
records = []
for index, command in enumerate(commands):
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    for name, data in [(f'check{index}.stdout.txt', result.stdout), (f'check{index}.stderr.txt', result.stderr)]:
        with (HERE / name).open('xb') as stream:
            stream.write(data)
    assert result.returncode == 0
    if index == 0:
        assert b'Ran 10 tests' in result.stderr and result.stderr.endswith(b'OK\n')
    else:
        assert result.stdout == result.stderr == b''
    records.append({'command': command, 'exitCode': result.returncode,
                    'stdoutSha256': hashlib.sha256(result.stdout).hexdigest(), 'stderrSha256': hashlib.sha256(result.stderr).hexdigest()})
assert not (HERE.parent / 'production-regression-activated-v1').exists()
assert not (HERE.parent / 'production-regression-activated-v1.staging').exists()
record = {'schemaVersion': 1, 'state': 'CLASSIC_REPLAY_ACTIVATION_MECHANISM_SOURCE_CHECKS_PASSED_MAIN_UNEXECUTED',
    'pureHostGroups': 10, 'pythonAstFiles': 4, 'nodeSyntaxOnlyFiles': 1, 'commands': records,
    'semanticPayloadsCheckedByteIdenticalInMemory': 64,
    'nativeAuthorityPinsSha256': 'c998dce40ff66a1764ad8c44f8a492b830d40bb6dce958aab711ecf3c5bcbf3e',
    'runtimeIndexBoundByTests': False, 'activationMainExecuted': False, 'activatedOutputExists': False,
    'runtimePreflightExecuted': False, 'compilerExecuted': False, 'guestExecuted': False, 'targetHostExecuted': False}
with (HERE / 'check-results.json').open('x') as stream:
    json.dump(record, stream, indent=2)
    stream.write('\n')
print(json.dumps({'state': record['state'], 'pureHostGroups': 10, 'syntaxChecks': 5}))
