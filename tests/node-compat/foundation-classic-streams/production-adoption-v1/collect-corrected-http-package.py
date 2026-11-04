"""Read actual corrected packaging output; never starts a guest or target host."""
from pathlib import Path
import datetime
import hashlib
import json
import re
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = Path('/tmp/starling-node-compat/production-classic-corrected-http-v1/http')
OUT = ROOT / 'http-joint'
FAMILY = Path('/private/tmp/starling-node-compat/classic-trace-source-v1/tests/node-compat/foundation-classic-streams/production-trace-http-activated-v1')
NODE = Path('/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node')
WASM_TOOLS = Path('/tmp/starling-node-compat/native-build/cache/wasm-tools/1448/wasm-tools')
IMPORTS = sorted(['wasi:clocks/monotonic-clock@0.2.10', 'wasi:http/types@0.2.10',
                  'wasi:io/error@0.2.10', 'wasi:io/poll@0.2.10',
                  'wasi:io/streams@0.2.10', 'wasi:random/random@0.2.10'])

def digest(data):
    return hashlib.sha256(data).hexdigest()

def record(path):
    data = path.read_bytes()
    return {'path': str(path), 'bytes': len(data), 'sha256': digest(data)}

def read(path):
    return json.loads(path.read_bytes())

terminal = read(Path('/tmp/starling-node-compat/classic-corrected-http-build-v2.terminal.json'))
assert terminal['returncode'] == 0
assert digest(NODE.read_bytes()) == 'e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0'
assert digest(WASM_TOOLS.read_bytes()) == 'b332dd79057dafdcc8a36ca933d0d499acea506b56b1ea28e28fbb036c9e713d'
audit = read(OUT / 'component-audit.json')
component = OUT / 'native-profile-http.component.wasm'
assert record(component)['sha256'] == audit['componentSha256'] == '24d76605a182ad21b0b0196570afd571737e549d2d89a1a4b30a542b4ab96efc'
assert component.stat().st_size == audit['componentBytes'] == 64058731
assert digest((OUT / 'http.bundle.mjs').read_bytes()) == audit['applicationBundleSha256'] == 'c91a66bfa1be4460dc63e925164685a99f90610ecb95c1690554d026d240f7ed'
assert audit['httpEntry'] == str(FAMILY / 'capability/http-component.mjs')
assert audit['engineSha256'] == 'a2fbdfcd9ec928cdec9d35e548b90ca2617ff52ae819c68bd08ad0a8c3ceffa7'
assert audit['emittedImports'] == audit['selectedInterfaces'] == audit['allowedImports'] == IMPORTS
assert audit['emittedExports'] == ['wasi:http/incoming-handler@0.2.10']
clock = audit['clockDependency']
assert clock['typeOnly'] is True and clock['durationRepresentation'] == 'u64'
assert clock['callableImports'] == clock['coreClockImports'] == []
assert digest(Path(clock['componentTypeGraph']['path']).read_bytes()) == clock['componentTypeGraph']['sha256']
assert len(audit['bundleImports']) == 17
assert sorted(audit['bundleImports']) == sorted(['node:buffer', 'node:child_process', 'node:path',
    'node:path/posix', 'node:path/win32', 'node:events', 'node:string_decoder', 'node:assert',
    'node:assert/strict', 'node:querystring', 'node:util', 'node:util/types', 'node:sys',
    'node:stream/web', 'node:stream', 'node:stream/promises', 'wasi:http/types@0.2.10'])
assert audit['computedLiveInputChecks']['beforeCopy'] == audit['computedLiveInputChecks']['afterCopy']
assert audit['computedLiveInputChecks']['beforeCopy']['files'] == 8
assert audit['preview1Adapter']['usedInFinalWrapping'] is False
assert audit['preview1Adapter']['sha256'] == '988224282d03fe0bd3c25b62344aef265b1a8e1f5804bdbc34d6442507fabcc0'
complete = read(OUT / 'production-admission-complete.json')
assert complete['sourceInputsRecheckedAfterRun'] is True
assert complete['inputClosure']['sha256'] == '55822794123728a11f6044ea0b15aec2ba70e674df8c0ce185283793b19e9da2'
manifest = FAMILY / 'input-freeze.json'
assert digest(manifest.read_bytes()) == complete['inputClosure']['sha256']
rows = read(manifest)['inputs']
assert len(rows) == 7496
for row in rows:
    path = (manifest.parent / row['path']).resolve()
    data = path.read_bytes()
    assert len(data) == row['bytes'] and digest(data) == row['sha256'], path
family_index = FAMILY / 'index.json'
assert digest(family_index.read_bytes()) == 'bb37128336a8b3044e4c632f77827c3e9e1f93dc56ec52f2099399791d3f985a'
for row in read(family_index)['files']:
    data = (FAMILY / row['path']).read_bytes()
    assert len(data) == row['bytes'] and digest(data) == row['sha256']
review = HERE.parent / 'independent-workload-v2-results-review-v1/index.json'
assert digest(review.read_bytes()) == '0f59a0dafdf9d0b426f90459ac0ac7ce4a9149b1aeeb568d314a7781dbc447e8'
wit_dir = Path('/tmp/starling-node-compat/corrected-http-package-root-static-v1')
wit_dir.mkdir()
with (wit_dir / 'emitted.wit').open('xb') as stdout, (wit_dir / 'stderr.log').open('xb') as stderr:
    proc = subprocess.run([str(WASM_TOOLS), 'component', 'wit', str(component)], stdout=stdout, stderr=stderr)
assert proc.returncode == 0
wit = (wit_dir / 'emitted.wit').read_text()
assert sorted(re.findall(r'^\s*import\s+([^;\s]+);', wit, re.M)) == IMPORTS
assert re.findall(r'^\s*export\s+([^;\s]+);', wit, re.M) == audit['emittedExports']
files = [record(p) for p in sorted(OUT.rglob('*')) if p.is_file()]
files += [record(ROOT / 'http-inputs.json'), record(family_index), record(manifest), record(review),
          record(wit_dir / 'emitted.wit'), record(wit_dir / 'stderr.log')]
for suffix in ('stdout.log', 'stderr.log', 'terminal.json'):
    files.append(record(Path('/tmp/starling-node-compat/classic-corrected-http-build-v2.' + suffix)))
report = {'schemaVersion': 1, 'state': 'ROOT_VERIFIED_CORRECTED_HTTP_PACKAGING_ONLY',
    'recordedAtUtc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'buildRawOuterExit': 0, 'buildSession': 71459, 'staticWitExit': proc.returncode,
    'componentSha256': audit['componentSha256'], 'componentBytes': audit['componentBytes'],
    'applicationBundleSha256': audit['applicationBundleSha256'], 'sourceEntryPath': audit['httpEntry'],
    'emittedImports': IMPORTS, 'emittedExports': audit['emittedExports'], 'clockDependency': clock,
    'sourceFilesRehashed': len(rows), 'files': files, 'hostExecuted': False,
    'runtimeAcceptanceClaim': False, 'performanceClaim': False,
    'limits': ['Packaging and static component inspection only; target-host instantiation remains outstanding.',
               'The earlier missing-tool environment failure and its unknown raw terminal status remain retained.']}
with (HERE / 'corrected-http-package-root-results.json').open('x') as f:
    json.dump(report, f, indent=2)
    f.write('\n')
print(json.dumps({'state': report['state'], 'files': len(files), 'componentSha256': audit['componentSha256']}))
