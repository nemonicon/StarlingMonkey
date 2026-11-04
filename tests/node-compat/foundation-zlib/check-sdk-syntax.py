#!/usr/bin/env python3
"""Actual SDK/SM flags; syntax only. Does not link or run a component."""
import hashlib
import json
import os
from pathlib import Path
import shlex
import subprocess

HERE = Path(__file__).resolve().parent
BASE = Path('/tmp/starling-node-compat/foundations-v7/native-freeze')
receipt = json.loads((BASE / 'off-foundations.engine.wasm.build.json').read_text())
commands_path = Path(receipt['cmakeCachePath']).with_name('compile_commands.json')
commands_bytes = commands_path.read_bytes()
assert hashlib.sha256(commands_bytes).hexdigest() == receipt['compileCommandsSha256']
commands = json.loads(commands_bytes)
entry = next(c for c in commands if c['file'].endswith('/builtins/node-compat/buffer.cpp'))
original = entry.get('arguments') or shlex.split(entry['command'])
args = []
i = 0
while i < len(original):
    arg = original[i]
    if arg in ('-o', '-MF', '-MT', '-MQ'):
        i += 2
        continue
    if arg in ('-c', '-MD', '-MMD') or arg == entry['file']:
        i += 1
        continue
    args.append(arg)
    i += 1
args.extend(['-fsyntax-only', str(HERE / 'native-driver.cpp')])
result = subprocess.run(args, cwd=entry['directory'], capture_output=True, text=True)
out = Path(os.environ.get('NODE_COMPAT_ZLIB_OUTPUT', '/tmp/starling-node-compat/zlib-template-v1'))
out.mkdir(parents=True, exist_ok=True)
report_path = out / 'sdk-syntax-results.json'
assert not report_path.exists(), 'Preserve earlier syntax report; choose a fresh output path'
report = {
    'schema': 1,
    'state': 'actual-sdk30-sm147-syntax-pass' if result.returncode == 0 else 'syntax-failed',
    'scope': 'C++ syntax only; no linking, engine, component, host import or GC evidence.',
    'baseEngineSha256': hashlib.sha256((BASE / 'off-foundations.engine.wasm').read_bytes()).hexdigest(),
    'compileCommandsPath': str(commands_path),
    'compileCommandsSha256': hashlib.sha256(commands_bytes).hexdigest(),
    'command': args, 'cwd': entry['directory'],
    'sources': [{'path': name, 'sha256': hashlib.sha256((HERE / name).read_bytes()).hexdigest()}
                for name in ('bounded-zlib.template.h', 'native-driver.cpp', 'check-sdk-syntax.py')],
    'exitCode': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr,
}
report_path.write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({'state': report['state'], 'report': str(report_path)}))
raise SystemExit(result.returncode)
