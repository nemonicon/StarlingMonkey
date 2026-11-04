#!/usr/bin/env python3
"""Compile only the unapplied overlay; no link, engine or guest execution."""
import hashlib
import json
from pathlib import Path
import shlex
import subprocess

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
FREEZE = Path('/tmp/starling-node-compat/foundations-v8/native-freeze')
SOURCE = Path('/tmp/starling-node-compat/add-abort-m0.10-proposal/source')
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
metadata_path = FREEZE / 'off-foundations.engine.wasm.build.json'
metadata = json.loads(metadata_path.read_text())
assert metadata['engineSha256'] == 'e16c19fc567753517d7b61b65372dd7dc86de8f839e7acab959b5cf5eaf294c9'
commands_path = FREEZE / 'off-compile_commands.json'
assert sha(commands_path) == metadata['compileCommandsSha256'] == 'bc4649a72380e2c59b2eccf678765f1225476886585c1035e7de063b12aa30c8'
commands = json.loads(commands_path.read_text())
for entry in metadata['sourceManifest']:
    assert sha(FREEZE / 'source' / entry['path']) == entry['sha256'], entry['path']

FEATURE = 'NODE_COMPAT_EVENTS_ADD_ABORT_LISTENER'
STRICT = 'NODE_COMPAT_STRICT_INITIALIZATION'
cases = [
    ('builtins/web/event/event-target.cpp', True, True, True),
    ('builtins/web/event/event-target.cpp', False, True, True),
    ('builtins/web/event/event-target.cpp', False, False, False),
    ('builtins/node-compat/register.cpp', True, True, True),
    ('builtins/node-compat/register.cpp', False, True, False),
    ('builtins/web/abort/abort-signal.cpp', True, True, True),
    ('builtins/web/event/event.cpp', True, True, True),
]
results = []
for path, feature, strict, events in cases:
    entry = next(e for e in commands if e['file'].endswith('/' + path))
    original = shlex.split(entry['command'])
    args = []
    skip = False
    for value in original:
        if skip:
            skip = False
            continue
        if value in ['-o', '-MF', '-MT', '-MQ']:
            skip = True
            continue
        if value in ['-c', '-MD', '-MMD']:
            continue
        if value.startswith('-D' + FEATURE) or value.startswith('-D' + STRICT):
            continue
        if not events and value.startswith('-DNODE_COMPAT_EVENTS='):
            continue
        args.append(value.replace(str(REPO) + '/', str(SOURCE) + '/'))
    args[1:1] = ['-I' + str(SOURCE / 'include'), '-I' + str(SOURCE / 'runtime'), '-I' + str(SOURCE)]
    if feature:
        args.append('-D' + FEATURE + '=1')
    if strict:
        args.append('-D' + STRICT + '=1')
    args.append('-fsyntax-only')
    process = subprocess.run(args, cwd=entry['directory'], capture_output=True, text=True)
    results.append({'path': path, 'feature': feature, 'strict': strict,
                    'eventsFactory': events if path.endswith('register.cpp') else None,
                    'sourceSha256': sha(SOURCE / path), 'command': args,
                    'compilerWrapperSha256': sha(Path(args[0])),
                    'exitCode': process.returncode, 'stdout': process.stdout, 'stderr': process.stderr})
    if process.returncode:
        break
report = {'state': 'UNAPPLIED_SYNTAX_ONLY', 'linked': False, 'engineBuilt': False,
          'guestExecuted': False, 'baseEngineSha256': metadata['engineSha256'],
          'baseMetadataSha256': sha(metadata_path), 'baseCompileCommandsSha256': sha(commands_path),
          'all293FrozenBaseInputsVerified': len(metadata['sourceManifest']) == 293,
          'sourceOverlay': str(SOURCE), 'driverSha256': sha(Path(__file__)), 'cases': results}
(HERE / 'syntax-results.json').write_text(json.dumps(report, indent=2) + '\n')
assert len(results) == len(cases) and all(case['exitCode'] == 0 for case in results), results[-1]
print('PASS seven actual SDK30/SM147 syntax cases; no linking or guest execution')
