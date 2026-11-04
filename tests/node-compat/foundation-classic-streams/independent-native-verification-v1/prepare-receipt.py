"""Record only owned pure-host preparation tests; never invoke verifier main."""
from pathlib import Path
import ast
import datetime
import hashlib
import json
import subprocess
import sys

HERE = Path(__file__).resolve().parent
assert all(not (HERE / name).exists() for name in ('host.stdout.txt', 'host.stderr.txt', 'preparation-results.json', 'index.json'))
for name in ('verify.py', 'test-reader.py', 'prepare-receipt.py'):
    ast.parse((HERE / name).read_text(), filename=name)
result = subprocess.run([sys.executable, '-B', str(HERE / 'test-reader.py')], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
for name, data in [('host.stdout.txt', result.stdout), ('host.stderr.txt', result.stderr)]:
    with (HERE / name).open('xb') as stream:
        stream.write(data)
assert result.returncode == 0 and b'Ran 7 tests' in result.stderr and result.stderr.endswith(b'OK\n')
document = {'schemaVersion': 1, 'state': 'INDEPENDENT_CLASSIC_NATIVE_READER_PREPARED_ACTUAL_PINS_NULL',
    'preparedAtUtc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'command': [sys.executable, '-B', str(HERE / 'test-reader.py')], 'exitCode': result.returncode,
    'pureHostGroupsPassed': 7, 'pythonAstSourcesParsed': 3,
    'actualEnginePins': None, 'actualArtifactPositivePathExecuted': False,
    'producerImported': False, 'compilerExecuted': False, 'ninjaExecuted': False,
    'freezerExecuted': False, 'componentizerExecuted': False, 'guestExecuted': False,
    'plannedSources': {'native': 342, 'external': 3, 'nativeCommands': 61, 'strictCommands': 4,
                       'privateTargetCommands': 5, 'afterOnlyEmbeddingCommands': 1, 'frozenCopies': 405},
    'testScope': 'Synthetic compiler-token parsing, schema/anchor refusal, owned tiny JSON, AST imports. No compiler strings executed.',
    'actualNativeVerificationState': 'NOT_RUN'}
with (HERE / 'preparation-results.json').open('x') as stream:
    json.dump(document, stream, indent=2)
    stream.write('\n')
files = []
for path in sorted(HERE.iterdir()):
    assert path.is_file() and not path.is_symlink(), path
    data = path.read_bytes()
    files.append({'path': path.name, 'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)})
with (HERE / 'index.json').open('x') as stream:
    json.dump({'schemaVersion': 1, 'state': document['state'], 'files': files,
               'actualEnginePins': None, 'actualArtifactPositivePathExecuted': False}, stream, indent=2)
    stream.write('\n')
print(json.dumps({'state': document['state'], 'indexedFiles': len(files),
    'indexSha256': hashlib.sha256((HERE / 'index.json').read_bytes()).hexdigest(),
    'preparationResultsSha256': hashlib.sha256((HERE / 'preparation-results.json').read_bytes()).hexdigest()}))
