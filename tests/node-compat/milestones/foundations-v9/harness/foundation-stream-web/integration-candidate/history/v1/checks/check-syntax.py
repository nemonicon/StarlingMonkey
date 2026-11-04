"""Actual pinned compiler/header syntax only for staged native sources."""
import hashlib
import json
from pathlib import Path
import shlex
import subprocess

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / 'source'
metadata_path = Path('/tmp/starling-node-compat/foundations-v8/native-freeze/off-foundations.engine.wasm.build.json')
metadata = json.loads(metadata_path.read_text())
database = json.loads(Path(metadata['compileCommandsPath']).read_text())
cases = []
for path, unit_suffix, selected in [
    ('builtins/node-compat/stream-web-kernel.cpp', '/node-compat/buffer.cpp', True),
    ('builtins/node-compat/register.cpp', '/node-compat/register.cpp', True),
    ('builtins/node-compat/register.cpp', '/node-compat/register.cpp', False),
    ('builtins/web/streams/transform-stream-default-controller.cpp', '/streams/transform-stream-default-controller.cpp', False),
]:
    unit = next(entry for entry in database if entry['file'].endswith(unit_suffix))
    original = shlex.split(unit['command'])
    arguments = [original[0], '-I' + str(SOURCE / 'include'), '-I' + str(SOURCE), '-I' + str(SOURCE / 'runtime')]
    if selected:
        arguments.append('-DNODE_COMPAT_STREAM_WEB=1')
    index = 1
    while index < len(original):
        item = original[index]
        if item == '-o':
            index += 2
            continue
        if item == '-c':
            index += 1
            continue
        if item == unit['file']:
            item = str(SOURCE / path)
        arguments.append(item)
        index += 1
    arguments.append('-fsyntax-only')
    result = subprocess.run(arguments, cwd=unit['directory'], capture_output=True, text=True)
    cases.append({'path': path, 'moduleSelected': selected, 'command': arguments, 'exitCode': result.returncode,
                  'stdout': result.stdout, 'stderr': result.stderr,
                  'sourceSha256': hashlib.sha256((SOURCE / path).read_bytes()).hexdigest()})
    assert result.returncode == 0, cases[-1]
report = {'scope': 'Actual SDK30/SM147 compiler and header syntax-only; staged source overlay, no linking/runtime/native entry',
          'baseEngineSha256': metadata['engineSha256'], 'cases': cases, 'linked': False, 'engineBuilt': False}
(HERE / 'syntax-results.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({'syntaxCases': len(cases), 'passed': True, 'linked': False, 'engineBuilt': False}))
