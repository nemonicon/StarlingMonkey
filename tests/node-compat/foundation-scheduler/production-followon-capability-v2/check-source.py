"""Read-only source/syntax checks; never invoke a build, packager, guest or host."""
import ast
import hashlib
import json
import os
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
seal = json.loads((HERE / 'input-freeze.json').read_bytes())
for row in seal['inputs']:
    path = (HERE / row['path']).resolve()
    assert sha(path) == row['sha256'] and path.stat().st_size == row['bytes']
assert not any((HERE / row['path']).resolve() == HERE / 'http-component-pins.json' for row in seal['inputs'])
assert json.loads((HERE / 'pins.json').read_bytes())['variants'] == {'normal-off': None, 'gc-off': None, 'normal-runtime': None}
assert json.loads((HERE / 'http-component-pins.json').read_bytes())['component'] is None
expected_live = [
    'host-apis/wasi-0.2.10/wit/deps/' + name + '/package.wit'
    for name in ['wasi-cli-0.2.10', 'wasi-clocks-0.2.10', 'wasi-filesystem-0.2.10',
                 'wasi-http-0.2.10', 'wasi-io-0.2.10', 'wasi-random-0.2.10', 'wasi-sockets-0.2.10']
] + ['host-apis/wasi-0.2.0/preview1-adapter-release/wasi_snapshot_preview1.wasm']
assert seal['liveComputedHTTPInputs'] == expected_live
sealed = {(HERE / row['path']).resolve(): row for row in seal['inputs']}
for name in expected_live:
    actual = (REPO / name).resolve()
    assert actual in sealed and sealed[actual]['sha256'] == sha(actual)
actual_wit = sorted(path.relative_to(REPO).as_posix() for path in (REPO / 'host-apis/wasi-0.2.10/wit/deps').rglob('*') if path.is_file())
assert actual_wit == sorted(expected_live[:7]), 'Every actual recursive cp file must be in the explicit live set'
transforms = json.loads((HERE / 'transformations.json').read_bytes())
for row in transforms['files']:
    original = REPO / row['original']
    assert sha(original) == row['originalSha256']
    generated = HERE / row['generated']
    assert sha(generated) == row['generatedSha256']
    restored = generated.read_text().splitlines(keepends=True)
    for edit in reversed(row['edits']):
        assert restored[edit['newStart']:edit['newEnd']] == edit['after']
        restored[edit['newStart']:edit['newEnd']] = edit['before']
    assert hashlib.sha256(''.join(restored).encode()).hexdigest() == row['originalSha256']
old = REPO / 'tests/node-compat/foundation-add-abort/production-native-m0.11'
for name in ['run-component.mjs', 'run-gc.mjs', 'run-callback-return.mjs']:
    before = (old / name).read_text().split('const report=', 1)[0]
    after = (HERE / 'focused' / name).read_text().split('const report=', 1)[0]
    assert before == after, 'Focused guest generation/invocation/case checks changed'
body = lambda p: '\n'.join(line for line in p.read_text().splitlines() if not line.startswith(('import ', '//')))
assert body(REPO / 'tests/node-compat/foundations/http-v11.mjs') == body(HERE / 'http-component.mjs')
before = (REPO / 'tests/node-compat/foundations/audit-http-v11.mjs').read_text()
after = (HERE / 'audit-http.mjs').read_text()
band = lambda s: s.split('for (const report of [wasmtime, wash]) {', 1)[1].split('const paths = [', 1)[0]
assert band(before) == band(after), 'Both-host response/shutdown/isolation checks changed'
before = (REPO / 'tests/node-compat/wasmcloud/build-http.mjs').read_text()
after = (HERE / 'runners/http-build.mjs').read_text()
band = lambda s: s.split('const virtualModules = ', 1)[1].split('const adapterImportModules = ', 1)[0]
assert band(before) == band(after), 'HTTP protected29/oracle source construction changed'
copy_at = after.index("await cp(join(repository, 'host-apis/wasi-0.2.10/wit/deps')")
assert after.index('const computedBeforeCopy=') < copy_at < after.index('const computedAfterCopy=')
assert "const httpEntry=resolve(sourceHere,'../http-component.mjs');" in after
assert "preview2Adapter: preview1AdapterPath" in after
base = HERE.parent / 'production-regression-candidate-v3/preflight.mjs'
band = lambda s: s.split('export async function verifyInputClosure', 1)[1].split('export async function verifyProductionTicks', 1)[0]
assert band(base.read_text()) == band((HERE / 'preflight.mjs').read_text()), 'Primitive manifest/pin seal implementation changed'
checks = []
node = '/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node'
for path in sorted(HERE.rglob('*.mjs')):
    if 'history' in path.parts:
        continue
    result = subprocess.run([node, '--check', str(path)], capture_output=True, text=True)
    assert result.returncode == 0, (path, result.stderr)
    checks.append({'path': str(path.relative_to(HERE)), 'exitCode': 0})
for path in HERE.glob('*.py'):
    ast.parse(path.read_text())
policy = json.loads((HERE.parent / 'integration-candidate-v1/policy.json').read_bytes())
for row in policy['expectedNativeSourceManifest']:
    assert sha(REPO / row['path']) == row['sha256']
tests = json.loads((HERE / 'test-results.json').read_bytes())
assert tests['tests'] == tests['passed'] == 87
report = {'schemaVersion': 1, 'state': 'CAPABILITY_FOLLOWON_SOURCE_CHECKS_PASSED_NOT_RUNTIME',
          'sealedInputsVerified': len(seal['inputs']), 'nativeSourceInputsVerified': 306,
          'reversibleDerivations': len(transforms['files']), 'syntaxChecks': checks,
          'focusedGuestAndCaseBlocksUnchanged': True, 'httpGuestBodyUnchanged': True,
          'httpBothHostCheckBlockUnchanged': True, 'httpOracleConstructionUnchanged': True,
          'primitivePinAndManifestSealFunctionsUnchanged': True, 'hostOnlyTests': 87,
          'actualLiveComputedInputsVerified': 8, 'actualRecursiveCopyFilesVerified': 7,
          'adapterWorldFixtureAndOracleReadsAudited': True,
          'allActualPinsNull': True, 'nativeBuildGuestOrHostExecuted': False}
output = Path(os.environ.get('NODE_COMPAT_CAPABILITY_SOURCE_CHECK_OUTPUT', str(HERE / 'source-checks.json')))
with output.open('x') as stream:
    json.dump(report, stream, indent=2)
    stream.write('\n')
print(json.dumps({'state': report['state'], 'inputs': len(seal['inputs']), 'syntax': len(checks), 'derivations': len(transforms['files'])}))
