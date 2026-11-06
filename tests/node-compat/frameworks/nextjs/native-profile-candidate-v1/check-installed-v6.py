"""Check canonical generators in the actual new installed Source context."""
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
NODE = Path('/private/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node')
assert __debug__ and sys.dont_write_bytecode and sys.flags.isolated == 1
assert len(sys.argv) == 2
root = Path(sys.argv[1])
source = root / 'source'
composition = json.loads((root / 'composition.json').read_text())
out = root / 'installed-checks'; out.mkdir(mode=0o700)
assert hashlib.sha256(NODE.read_bytes()).hexdigest() == 'e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0'


def protect():
    assert sorted(p.relative_to(source).as_posix() for p in source.rglob('*') if p.is_file()) == [r['path'] for r in composition['files']]
    for row in composition['files']:
        p = source / row['path']; data = p.read_bytes()
        assert not p.is_symlink() and len(data) == row['bytes'] and hashlib.sha256(data).hexdigest() == row['sha256'], row['path']


protect()
commands = [
    ['generate-factories.mjs', '--crypto-random'],
    ['generate-fs-factory.mjs'],
    ['generate-module-factory.mjs'], ['generate-async-hooks-factory.mjs'],
    ['generate-vm-data-factory.mjs'],
    ['zlib/generate-factory.mjs', '--repository', str(source)],
    ['zlib/generate-stream-factory.mjs'],
    ['next-http/generate-http-factory.mjs'],
    ['next-imports/generate-imports-factory.mjs'],
]
results = []
env = {'PATH': str(NODE.parent) + ':/usr/bin:/bin'}
for key in ('HOME', 'USER', 'LOGNAME'):
    if key in os.environ: env[key] = os.environ[key]
for i, command in enumerate(commands):
    argv = [str(NODE), str(source / 'builtins/node-compat' / command[0]), *command[1:], '--check']
    cp = subprocess.run(argv, cwd=str(source), env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30)
    (out / (str(i) + '.stdout')).write_bytes(cp.stdout)
    (out / (str(i) + '.stderr')).write_bytes(cp.stderr)
    results.append({'argv': argv, 'rawExitCode': cp.returncode,
                    'stdoutSha256': hashlib.sha256(cp.stdout).hexdigest(), 'stderrSha256': hashlib.sha256(cp.stderr).hexdigest()})
protect()
result = {'schemaVersion': 1, 'state': 'ACTUAL_INSTALLED_NEXT_PROFILE_GENERATOR_CHECK',
          'passed': all(r['rawExitCode'] == 0 for r in results), 'sourceFiles': len(composition['files']),
          'commands': results, 'sourceBeforeAfterUnchanged': True, 'nativeOrGuestExecuted': False}
(out / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({'passed': result['passed'], 'commands': len(results), 'nativeSourceFiles': result['sourceFiles']}))
raise SystemExit(0 if result['passed'] else 1)
