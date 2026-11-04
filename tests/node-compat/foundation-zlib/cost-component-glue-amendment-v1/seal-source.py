"""Bounded source/AST-data seal; never invoke build/preflight/Jco/guest mains."""
import ast
import difflib
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess

HERE = Path(__file__).resolve().parent
PARENT = HERE.with_name('cost-component-wit-amendment-v1')
BASE = HERE.with_name('cost-component-candidate-v1')
NODE = '/private/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node'
inputs = {}


def h(raw):
    return hashlib.sha256(raw).hexdigest()


def capture(path, expected=None, size=None):
    p = Path(path)
    s = p.lstat()
    assert stat.S_ISREG(s.st_mode) and not p.is_symlink()
    raw = p.read_bytes()
    assert expected is None or h(raw) == expected, str(p)
    assert size is None or len(raw) == size, str(p)
    row = {'path': str(p.resolve()), 'sha256': h(raw), 'bytes': len(raw)}
    assert row['path'] not in inputs or inputs[row['path']] == row
    inputs[row['path']] = row
    return raw


def indexed(root, expected):
    raw = capture(root / 'index.json', expected)
    for row in json.loads(raw)['files']:
        capture(root / row['path'], row['sha256'], row['bytes'])
    return raw


def write(name, value):
    p = HERE / name
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('x') as f:
        json.dump(value, f, indent=2)
        f.write('\n')


assert not (HERE / 'index.json').exists()
parent_ix = indexed(PARENT, 'e7252156f464f3a73621c002d01b95fa309ebc8208934539687d54d885257caa')
base_ix = indexed(BASE, 'a2fa62b3ab63a6aca044aec9a83c1ff5a09edaa208eb615226a13845bf1522f9')
tooling_ix = capture(HERE.with_name('cost-tooling-candidate-v3') / 'index.json',
                     'ff208e72d0b87933aa75cdeb7c1ae16f29aa6ae94c357318a9d6676af04b36b8')
peer = HERE.with_name('independent-cost-component-wit-source-review-v1')
indexed(peer, '6d54fd8a9210fcd342a457a8da9e1c4f9dc939e4bbcbc0b8a5e7721182a015a4')
failure_path = HERE.with_name('cost-component-native-on-v2-failure-root-results.json')
failure_raw = capture(failure_path, 'd6f87cbf10f77d8190043c7fafef5f63d236b9389441ab588d2355d9204b1e8b')
failure = json.loads(failure_raw)
assert failure['parentRawExitCode'] == failure['workerRawExitCode'] == 1
assert failure['ordinaryGuestExportsInvoked'] is False
assert failure['overallBuildOrComponentAcceptanceIssued'] is False
for row in failure['partialFiles']:
    capture(row['path'], row['sha256'], row['bytes'])
for key in ['externalTerminal', 'externalStdout', 'externalStderr']:
    row = failure[key]
    capture(row['path'], row['sha256'], row['bytes'])
publication = Path('/private/tmp/starling-node-compat/zlib-cost-source-v3')
publication_ix = capture(publication / 'index.json', '4621f7e72b4fb0555a5df630b1aedd4d2a04743b0db9188fc50099779f07387b')
selected = ['tools/toolchain/node_modules/rolldown/package.json',
            'tools/toolchain/node_modules/rolldown/dist/parse-ast-index.mjs',
            'tools/toolchain/node_modules/@bytecodealliance/jco/package.json',
            'tools/toolchain/node_modules/@bytecodealliance/jco-transpile/package.json',
            'tools/toolchain/node_modules/@bytecodealliance/jco-transpile/dist/transpile.js']
for row in json.loads(publication_ix)['files']:
    if row['path'] in selected:
        capture(publication / row['path'], row['sha256'], row['bytes'])
assert all(str((publication / name).resolve()) in inputs for name in selected)
assert (HERE / 'public-abi.wit').read_bytes() == (PARENT / 'public-abi.wit').read_bytes()
parser_wit = HERE.with_name('cost-component-wit-parameter-parser-regression-root-v1') / 'corrected.wit'
assert (HERE / 'public-abi.wit').read_bytes() == capture(parser_wit, '84a5fb9b33dc1e9e7f77d490c3799a6a933d93cde2c0d4d63a6c438d40dd7c89')
changes = []
for name in ['guard.mjs', 'build-worker.mjs', 'abi.mjs']:
    before = capture(PARENT / name)
    after = (HERE / name).read_bytes()
    delta = list(difflib.ndiff(before.decode().splitlines(keepends=True), after.decode().splitlines(keepends=True)))
    assert ''.join(difflib.restore(delta, 1)).encode() == before
    assert ''.join(difflib.restore(delta, 2)).encode() == after
    changes.append({'path': name, 'beforeSha256': h(before), 'afterSha256': h(after), 'exactReverse': True, 'ndiff': delta})
same = ['authority.mjs', 'collector.mjs', 'proofs.mjs', 'durable.mjs', 'durable-host.mjs', 'public-abi.wit', 'build.mjs']
for name in same:
    assert (HERE / name).read_bytes() == capture(PARENT / name)
for name in ['authority.mjs', 'collector.mjs', 'proofs.mjs', 'durable.mjs', 'durable-host.mjs']:
    assert (HERE / name).read_text().endswith("export * from '../cost-component-candidate-v1/" + name + "';\n")
guard = (HERE / 'guard.mjs').read_text()
assert "sourceIndex(join(HERE,'../cost-component-wit-amendment-v1/index.json'),COMPONENT_WIT_SHA)" in guard
assert 'await witParent.recheck()' in guard
build = (HERE / 'build.mjs').read_text()
for name in ['authority.mjs', 'abi.mjs', 'collector.mjs', 'proofs.mjs', 'durable.mjs', 'durable-host.mjs']:
    assert "'" + name + "'" in build
assert "'control/'" in build and "'../cost-component-candidate-v1',name" in build
env = dict(os.environ)
for key in ['NODE_OPTIONS', 'NODE_PATH', 'NAPI_RS_NATIVE_LIBRARY_PATH', 'NAPI_RS_FORCE_WASI',
            'NAPI_RS_WASI_FLAVOR', 'NAPI_RS_ENFORCE_VERSION_CHECK']:
    assert not env.get(key), 'Unreviewed parser loader environment ' + key
capture(NODE, 'e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0')
run = subprocess.run([NODE, str(HERE / 'test-pure.mjs')], capture_output=True, env=env)
for name, data in [('stdout.log', run.stdout), ('stderr.log', run.stderr)]:
    p = HERE / 'evidence' / name
    p.parent.mkdir(exist_ok=True)
    with p.open('xb') as f:
        f.write(data)
assert run.returncode == 0, run.stderr.decode()
pure = json.loads(run.stdout)
assert pure['hostRolldownParserLibraryInvoked'] is True and pure['generatedGlueImported'] is False
syntax = []
for p in sorted(HERE.iterdir()):
    if p.suffix == '.mjs':
        result = subprocess.run([NODE, '--check', str(p)], capture_output=True, env=env)
        assert result.returncode == 0, result.stderr.decode()
        syntax.append({'path': p.name, 'nodeCheckExitCode': 0})
    elif p.suffix == '.py':
        ast.parse(p.read_text())
        syntax.append({'path': p.name, 'ASTParsed': True})
for row in list(inputs.values()):
    capture(row['path'], row['sha256'], row['bytes'])
write('derivations.json', {'schemaVersion': 1, 'files': changes, 'byteIdenticalToE725': same,
                         'scalarABIAndGuestProtocolUnchanged': True, 'newJSHelperRolePolicy': True})
write('input-freeze.json', {'schemaVersion': 1, 'files': list(inputs.values()),
                          'preparationReferencesOnly': True, 'parentConsumedManifestsFollowed': False})
write('evidence/syntax-results.json', {'checks': len(syntax), 'files': syntax})
write('source-receipt.json', {'schemaVersion': 1, 'state': 'EXPLICIT_EMPTY_JCO_GLUE_HELPER_SOURCE_CORRECTION_UNREVIEWED',
    'componentWitSourceIndexSha256': h(parent_ix), 'componentBaseSourceIndexSha256': h(base_ix),
    'toolingSourceIndexSha256': h(tooling_ix), 'actualFailedV2RootReceiptSha256': h(failure_raw),
    'sourceOnly': True, 'sourceReviewPassed': None, 'pureAndCapturedSourceChecks': pure['checks'],
    'parseChecks': len(syntax), 'hostRolldownParserLibraryInvoked': True,
    'generatedModuleImported': False, 'JcoTranspileComponentizerCodecGuestNativeOrHostInvoked': False,
    'oldAttemptRawExitCode': 1, 'oldArtifactAccepted': False, 'operationalAdmission': False,
    'sourcePromotionIssued': False, 'runtimeAcceptanceClaim': False, 'performanceClaim': False,
    'newRootAction': None, 'newOutputNamespace': 'zlib-cost-component-v3',
    'independentReviewContract': {'schemaVersion': 1, 'state': 'INDEPENDENT_ZLIB_COST_COMPONENT_SOURCE_REVIEW_PASSED_V1',
        'componentSourceIndexSha256': 'EXACT_NEW_INDEX_SHA256', 'sourceOnly': True,
        'sourceReviewPassed': True, 'ownerActionsInvoked': False}})
rows = []
for p in sorted(HERE.rglob('*')):
    if p.is_dir():
        continue
    assert p.is_file() and not p.is_symlink()
    raw = p.read_bytes()
    rows.append({'path': str(p.relative_to(HERE)), 'sha256': h(raw), 'bytes': len(raw)})
write('index.json', {'schemaVersion': 1, 'state': 'SOURCE_ONLY_EXACT_EMPTY_JCO_HELPER_AMENDMENT',
                     'sourceOnly': True, 'actionsAllowed': False, 'files': rows})
print(json.dumps({'indexSha256': h((HERE / 'index.json').read_bytes()),
                  'files': len(rows), 'inputRows': len(inputs), 'sourceOnly': True,
                  'hostParserLibraryInvoked': True, 'codecOrComponentOrGuestInvoked': False}))
