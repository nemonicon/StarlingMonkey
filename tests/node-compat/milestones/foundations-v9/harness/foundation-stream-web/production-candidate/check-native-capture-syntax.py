"""Actual SDK/header syntax check only; never edits production or links an engine."""
import hashlib
import json
import os
from pathlib import Path
import shlex
import subprocess

HERE = Path(__file__).resolve().parent
ENGINE = Path(os.environ.get('NODE_COMPAT_ENGINE', '/tmp/starling-node-compat/foundations-v6/native-freeze/off-foundations.engine.wasm'))
SOURCE = Path(os.environ.get('NODE_COMPAT_ENGINE_SOURCE_ROOT', '/tmp/starling-node-compat/foundations-v6/native-freeze/source'))
digest = lambda data: hashlib.sha256(data).hexdigest()
metadata = json.loads(Path(str(ENGINE) + '.build.json').read_text())
assert digest(ENGINE.read_bytes()) == metadata['engineSha256']
for entry in metadata['sourceManifest']:
    assert digest((SOURCE / entry['path']).read_bytes()) == entry['sha256']
database = json.loads(Path(metadata['compileCommandsPath']).read_text())
unit = next(entry for entry in database if entry['file'].endswith('/node-compat/buffer.cpp'))
original = shlex.split(unit['command'])
template = HERE.parent / 'native-kernel.template.cpp'
arguments = [original[0], '-I' + str(SOURCE), '-I' + str(SOURCE / 'include')]
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
        item = str(template)
    arguments.append(item)
    index += 1
arguments += ['-fsyntax-only']
completed = subprocess.run(arguments, cwd=unit['directory'], capture_output=True, text=True)
report = {'scope': 'UNINSTALLED native capture template: actual SDK30/SM147 headers and frozen v6 source overlay; syntax-only',
          'engineSha256': metadata['engineSha256'], 'sourceRoot': str(SOURCE), 'templatePath': str(template),
          'templateSha256': digest(template.read_bytes()), 'compilerPath': original[0],
          'compilerSha256': digest(Path(original[0]).read_bytes()), 'command': arguments,
          'exitCode': completed.returncode, 'stdout': completed.stdout, 'stderr': completed.stderr,
          'syntaxOnly': True, 'linked': False, 'productionApplied': False,
          'limitations': ['Does not prove JS_GetClassObject runtime identities or callback behavior',
                          'No temporary initialization streams, raw-memory or native entry are executed']}
(HERE / 'native-capture-syntax-results.json').write_text(json.dumps(report, indent=2) + '\n')
assert completed.returncode == 0, completed.stderr
print(json.dumps({'syntaxOnly': True, 'exitCode': 0, 'linked': False, 'productionApplied': False}))
