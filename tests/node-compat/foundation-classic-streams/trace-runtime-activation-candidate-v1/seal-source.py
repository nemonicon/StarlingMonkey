"""Seal only this NEW source packet. No activation or artifact actions."""
from pathlib import Path
import ast
import hashlib
import json
import stat

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
SOURCE = Path('/tmp/starling-node-compat/classic-trace-source-v1')
rows = {}


def sha(data): return hashlib.sha256(data).hexdigest()


def add(path, expected=None, role='preparation-source-or-tool-byte'):
    path = Path(path).absolute()
    before = path.lstat(); assert stat.S_ISREG(before.st_mode) and not path.is_symlink(), str(path)
    data = path.read_bytes(); after = path.lstat()
    assert (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) == (
        after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)
    checksum = sha(data)
    if expected is not None: assert checksum == expected, str(path)
    key = str(path)
    row = {'path': key, 'sha256': checksum, 'bytes': len(data), 'role': role}
    if key in rows: assert rows[key]['sha256'] == checksum and rows[key]['bytes'] == len(data)
    else: rows[key] = row
    return data


def indexed(root, expected, role):
    index = json.loads(add(root / 'index.json', expected, role))
    for row in index['files']: add(root / row['path'], row['sha256'], role)
    return index


def put(name, value):
    with (HERE / name).open('x') as output:
        json.dump(value, output, indent=2); output.write('\n')


def main():
    assert not (HERE / 'index.json').exists() and not (HERE / 'input-freeze.json').exists()
    integration = HERE.parent / 'trace-integration-candidate-v1'
    indexed(integration, '224fba889e72283d68e5ad01008c91ccfb7970e743a249019856aa43e7422d0b', 'original-preparation-context-source')
    staged = SOURCE / integration.relative_to(REPO)
    indexed(staged, '224fba889e72283d68e5ad01008c91ccfb7970e743a249019856aa43e7422d0b', 'actual-corrected-checkout-proposal-bytes-not-relocated-preparation-rows')
    policy = json.loads(add(integration / 'policy.json'))
    for row in policy['expectedNativeSourceManifest']:
        add(SOURCE / row['path'], row['sha256'], 'actual-corrected-native342-source')
    tools = json.loads(add(integration / 'artifact-tools/tool-pins.json'))
    for row in tools['toolDependencies']:
        add(SOURCE / row['path'], row['sha256'], 'actual-corrected-tool92-source')
    base = HERE.parent / 'production-runtime-activated-v3'
    indexed(base, '7e9520e0859b939a8586e6d0cfa1fe376a3ace75a2624dd777d5825bbf91cf66', 'immutable-old-runtime-body-and-tool-ancestry-not-pass-reuse')
    old = json.loads(add(base / 'input-freeze.json', '085b85656558e28aa748bcbc3551a0bd9054f0fb8a43c59ee9814ce1e8d51d68'))
    for row in old['inputs']:
        path = Path(row['path'])
        if not path.is_absolute(): path = base / path
        add(path, row['sha256'], 'historical-runtime-source-or-locked-tool-byte-not-corrected-artifact-authority')
    indexed(HERE.parent / 'stream-trace-regression-candidate-v2', '5b40a987b3a2bba08b3192c8a3e3b80a16a32d8de2019c4ecdc9406d3733ef30', 'exact-eleven-case-public-fixture-and-oracle-source')
    for path in sorted(HERE.rglob('*')):
        if path.is_file(): add(path, role='new-source-packet-byte')
    for path in sorted(HERE.rglob('*.py')): ast.parse(path.read_text(), filename=str(path))
    assert not (HERE.parent / 'production-trace-runtime-activated-v1').exists()
    assert not (HERE.parent / 'production-trace-runtime-activated-v1.staging').exists()
    seal = {'schemaVersion': 1, 'state': 'SOURCE_PREPARATION_ONLY_TRACE_RUNTIME_ACTIVATION_EXACT_INPUT_CLOSURE',
        'inputs': sorted(rows.values(), key=lambda row: row['path']),
        'scope': 'Explicit immutable source/history/tool records only. Old artifacts are ancestry references, never new pin authority. Original preparation1175 remains in original context; copied list bytes are not followed.',
        'actualNewArtifactPins': None, 'activationOutputCreated': False}
    put('input-freeze.json', seal)
    receipt = {'schemaVersion': 1, 'state': 'TRACE_RUNTIME_ACTIVATION_PRODUCER_SOURCE_READY_ACTIONS_UNEXECUTED',
        'integrationIndexSha256': '224fba889e72283d68e5ad01008c91ccfb7970e743a249019856aa43e7422d0b',
        'sourceContractVersion': 'sm-classic-trace-source-v1',
        'configuredSourceRoot': str(SOURCE), 'nativeSources': 342, 'unchangedNativePaths': 339, 'correctedNativePaths': 3,
        'toolDependencies': 92, 'inputFreezeSha256': sha((HERE / 'input-freeze.json').read_bytes()),
        'consumedPreparationInputs': len(rows), 'exactReversibleDriverAndTemplateDerivations': 3,
        'unchangedInheritedHarnessFiles': 9, 'unchangedElevenCasePayloadAndOracleFiles': 3,
        'sourceAndAuthorityChecks': 51, 'pureNodeNullAndScratchSealChecks': 12, 'syntaxChecks': 18,
        'newEngineHashes': None, 'reviewedNewRuntimePins': None,
        'futureRootAuthoritySchemaProposedNotPopulated': True,
        'activationMainOrGenuineArtifactVerifierExecuted': False, 'actualNativePreflightExecuted': False,
        'configureCompilerBuildFreezeExporterMainPackagerGuestHostTimingExecuted': False,
        'liveSourceOrActiveCheckoutOrOldPacketsModified': False, 'activationOutputCreated': False,
        'runtimeAcceptanceClaim': False, 'performanceClaim': False}
    put('source-receipt.json', receipt)
    files = []
    for path in sorted(HERE.rglob('*')):
        if path.is_file():
            data = path.read_bytes(); files.append({'path': str(path.relative_to(HERE)), 'sha256': sha(data), 'bytes': len(data)})
    put('index.json', {'schemaVersion': 1, 'state': 'SEALED_TRACE_RUNTIME_ACTIVATION_SOURCE_ONLY_FUTURE_PINS_NULL',
        'files': files, 'runtimeAcceptanceClaim': False})
    print(json.dumps({'indexSha256': sha((HERE / 'index.json').read_bytes()), 'files': len(files),
        'inputFreezeSha256': receipt['inputFreezeSha256'], 'inputs': len(rows), 'activationOutputCreated': False}))


if __name__ == '__main__': main()
