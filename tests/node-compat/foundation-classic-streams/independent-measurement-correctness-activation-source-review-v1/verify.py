"""Independent data/source reader. Imports no owner code; runs no action helper."""
from pathlib import Path
import ast
import hashlib
import json
import os
import stat

HERE = Path(__file__).resolve().parent
FAMILY = HERE.parent
REPO = FAMILY.parents[2]
OWNER = FAMILY / 'measurement-correctness-activation-candidate-v1'
BASE = FAMILY / 'measurement-correctness-candidate-v1'
AMEND = FAMILY / 'measurement-correctness-reporting-amendment-v1'
DECLARED = Path('/tmp/starling-node-compat/classic-benchmark-trace-v2-source')
CANONICAL = Path('/private/tmp/starling-node-compat/classic-benchmark-trace-v2-source')
PRODUCER = CANONICAL / 'tests/node-compat/foundation-classic-streams/measurement-producer-candidate-v3'
FREEZE = Path('/tmp/starling-node-compat/classic-benchmark-trace-v3-artifacts/native-freeze')
LABEL = 'benchmark-classic-on'
seen = {}
checks = []

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def read(path, expected=None, size=None):
    path = Path(path)
    before = path.lstat()
    assert stat.S_ISREG(before.st_mode) and not path.is_symlink(), path
    raw = path.read_bytes()
    after = path.lstat()
    assert (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) == (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns), path
    digest = sha(raw)
    assert expected is None or digest == expected, path
    assert size is None or len(raw) == size, path
    key = str(path.resolve(strict=True))
    row = {'path': key, 'sha256': digest, 'bytes': len(raw)}
    assert key not in seen or seen[key] == row, path
    seen[key] = row
    return raw

def document(path, expected=None):
    return json.loads(read(path, expected))

def indexed(root, expected):
    value = document(root / 'index.json', expected)
    names = set()
    for row in value['files']:
        name = row['path']
        assert name not in names and not Path(name).is_absolute() and all(part not in ('', '.', '..') for part in name.split('/'))
        names.add(name)
        current = root
        for part in name.split('/'):
            current /= part
            assert not current.is_symlink(), current
        read(current, row['sha256'], row['bytes'])
    return value

def check(name, condition=True):
    assert condition, name
    checks.append(name)

def tree(root):
    assert root.is_dir() and not root.is_symlink()
    rows = []
    for directory, dirs, files in os.walk(root, followlinks=False):
        for name in sorted(dirs + files):
            path = Path(directory) / name
            mode = path.lstat().st_mode
            kind = 'symlink' if stat.S_ISLNK(mode) else 'directory' if stat.S_ISDIR(mode) else 'file' if stat.S_ISREG(mode) else None
            assert kind, path
            rows.append({'path': str(path.relative_to(root)), 'kind': kind})
            if kind == 'file':
                read(path)
        dirs[:] = [name for name in dirs if not (Path(directory) / name).is_symlink()]
    return sorted(rows, key=lambda row: row['path'])

def main():
    assert not (HERE / 'results.json').exists()
    owner = indexed(OWNER, 'ce2f254f2cf27d44df5f0d23915ca4e09c98ac15b2f88f762d41f57fb8e6048e')
    check('owner index nineteen immutable rows', len(owner['files']) == 19)
    preparation = document(OWNER / 'input-freeze.json', 'd408cd54ad451fdb3c56e94e3220a1d2e8b5162b51eb42c9524dbaf701cc2d9e')
    check('preparation source inventory count', len(preparation['inputs']) == 6908)
    for row in preparation['inputs']:
        assert Path(row['path']).is_absolute()
        read(row['path'], row['sha256'], row['bytes'])
    parents = [
        (BASE, '138a4e0bcfe22ef3b48375257a50958f595dcebb607fc9267a30080948d612da', 36),
        (AMEND, '0558b50589680f9e1b812c8a62210233a768385bfabeae2f07be47c2e1fe5350', 14),
        (FAMILY / 'measurement-producer-candidate-v3', '46c031d36c1691c3980c51d44102e1a7cc651ff4bf8b9470c9e746697eece8bc', 40),
        (PRODUCER, '46c031d36c1691c3980c51d44102e1a7cc651ff4bf8b9470c9e746697eece8bc', 40),
        (FAMILY / 'independent-measurement-correctness-source-review-v1', 'c6958e3efcc22ccd980e7900d3ff129318e1e32f48b915aec65389601283b2ac', 6),
    ]
    parent_counts = {}
    for root, digest, count in parents:
        value = indexed(root, digest)
        assert len(value['files']) == count, (root, len(value['files']))
        parent_counts[str(root)] = len(value['files'])
    check('correctness reporting genuine verifier and prior peer sealed parents')
    assert DECLARED.resolve(strict=True) == CANONICAL and not DECLARED.is_symlink() and not CANONICAL.is_symlink()
    check('declared tmp and canonical private tmp identify same unchanged native source root')
    pins_path = FAMILY / 'production-adoption-v1/reviewed-diagnostic-v3-on-pins.json'
    review_path = FAMILY / 'production-adoption-v1/diagnostic-v3-on-root-review-receipt.json'
    pins = document(pins_path, '2e9811a54b03733d7d4dde0b42f66831a9b97da2c2f26313f078443dc329165c')
    review = document(review_path, '9681578ea64c826f72baa1e1bff1533af276ff27d6dda52c5bf1dbe064697001')
    assert pins['state'] == 'ROOT_REVIEWED_CLASSIC_TRACE_BENCHMARK_DIAGNOSTIC_FREEZES_V3'
    assert set(pins['variants']) == {LABEL, 'benchmark-classic-off'} and pins['variants']['benchmark-classic-off'] is None
    pin = pins['variants'][LABEL]
    assert pin['state'] == 'reviewed-classic-trace-benchmark-diagnostic-freeze' and pin['reviewRequired'] is False
    assert review['state'] == 'ROOT_REVIEWED_CLASSIC_DIAGNOSTIC_CORRECTNESS_INPUTS_V1'
    assert review['reviewedPinsSha256'] == sha(read(pins_path))
    for key in ('engineSha256', 'engineBytes', 'metadataSha256', 'freezeReceiptSha256', 'sourceIndexSha256', 'recipeSha256', 'sourceContractVersion', 'sourceFiles', 'addonFiles'):
        assert review[key] == pin[key], key
    assert review['declaredConfiguredSourceRoot'] == str(DECLARED) and review['canonicalDiagnosticSourceRoot'] == str(CANONICAL)
    assert review['runtimeAcceptanceClaim'] is False and review['performanceClaim'] is False
    check('actual Root ON only authority and four tuple cross binding')
    proof_root = FAMILY / 'independent-measurement-producer-v3-on-native-review-v1'
    indexed(proof_root, review['independentProofIndexSha256'])
    document(proof_root / 'results.json', review['independentProofResultSha256'])
    check('Root names actual independent native proof bytes')
    receipt = document(FREEZE / (LABEL + '-freeze-receipt.json'), pin['freezeReceiptSha256'])
    assert len(receipt['copies']) == 525 and len({row['path'] for row in receipt['copies']}) == 525
    for row in receipt['copies']:
        path = Path(row['path'])
        assert path.is_relative_to(FREEZE)
        read(path, row['sha256'], row['bytes'])
    metadata = document(FREEZE / (LABEL + '.engine.wasm.build.json'), pin['metadataSha256'])
    read(FREEZE / (LABEL + '.engine.wasm'), pin['engineSha256'], pin['engineBytes'])
    for key in ('engineSha256', 'engineBytes', 'metadataSha256', 'recipeSha256', 'sourceIndexSha256'):
        assert receipt[key] == pin[key]
    assert metadata['diagnosticOnly'] is True and metadata['classicStreamsEnabled'] is True and metadata['gcStress'] is False
    assert {key: receipt[key] for key in ('nativeInputsVerified', 'addonInputsVerified', 'externalEmbeddingInputsVerified', 'actualNativeCommands', 'actualStrictCommands', 'actualPrivateCommands', 'actualEmbeddingCommands', 'actualDiagnosticCommands')} == {
        'nativeInputsVerified': 342, 'addonInputsVerified': 2, 'externalEmbeddingInputsVerified': 3, 'actualNativeCommands': 61, 'actualStrictCommands': 4, 'actualPrivateCommands': 5, 'actualEmbeddingCommands': 1, 'actualDiagnosticCommands': 1}
    check('actual frozen 525 inventory and diagnostic ON tuple rehashed as data')
    assert len(metadata['sourceManifest']) == 342
    for row in metadata['sourceManifest']:
        read(CANONICAL / row['path'], row['sha256'])
        read(FREEZE / 'source' / row['path'], row['sha256'])
    contract = document(PRODUCER / 'contract.json')
    assert len(contract['addonSources']) == 2
    for row in contract['addonSources']:
        read(CANONICAL / row['path'], row['sha256'])
        read(FREEZE / 'addon' / row['path'], row['sha256'])
    assert len(metadata['componentizeSourceManifest']) == 3
    for row in metadata['componentizeSourceManifest']:
        read(FREEZE / 'componentize-source' / row['path'], row['sha256'])
    assert len(receipt['toolDependencyClosure']) == 92
    for row in receipt['toolDependencyClosure']:
        read(CANONICAL / row['sourcePath'], row['sha256'], row['bytes'])
        read(row['path'], row['sha256'], row['bytes'])
    check('actual mutable source342 addon2 external3 and corrected tool92 bytes match frozen evidence')
    original = document(BASE / 'input-freeze.json')
    assert len(original['toolTrees']) == 2 and len(original['toolLinks']) == 22
    for row in original['toolTrees']:
        root = Path(row['path'])
        assert str(root.resolve(strict=True)) == row['realPath']
        assert tree(root) == row['entries']
    canonical_roots = [Path(row['realPath']) for row in original['toolTrees']]
    for row in original['toolLinks']:
        path = Path(row['path'])
        assert path.is_symlink() and os.readlink(path) == row['linkText']
        target = path.resolve(strict=True)
        assert str(target) == row['resolvedTarget'] and any(target.is_relative_to(root) for root in canonical_roots)
        assert ('directory' if target.is_dir() else 'file' if target.is_file() else None) == row['targetKind']
        if row['targetKind'] == 'file':
            read(target, row['targetSha256'], row['targetBytes'])
    check('two exact tool root memberships and twenty two link targets')
    inherited = document(BASE / 'inherited-inputs.json')
    for row in inherited['files']:
        assert read(BASE / row['path'], row['sha256'], row['bytes']) == read(REPO / row['origin'], row['sha256'], row['bytes'])
    proof = document(AMEND / 'transformation-proof.json')
    before = read(BASE / 'component-driver.mjs', proof['beforeSha256']).decode()
    after = read(AMEND / 'proposed/component-driver.mjs', proof['afterSha256']).decode()
    current = before
    for row in proof['edits']:
        assert current.count(row['old']) == row['count']
        current = current.replace(row['old'], row['new'])
    assert current == after
    for row in reversed(proof['edits']):
        assert current.count(row['new']) == row['count']
        current = current.replace(row['new'], row['old'])
    assert current == before
    check('five original semantic oracle completion files exact and mandatory reporting nine edits reverse')
    source = read(OWNER / 'activate.py').decode()
    authority = read(OWNER / 'authority.py').decode()
    template = read(BASE / 'runtime-preflight.template.mjs').decode()
    check('authority and all forty verifier bytes hashed before genuine verifier import', source.index('load_authority(pin_path') < source.index('producer_rows=indexed(PRODUCER,PRODUCER_INDEX)') < source.index("spec_from_file_location('benchmark_common'"))
    check('genuine verifier no projected or fabricated metadata backend', 'backend.require_source_root(CANONICAL)' in source and 'backend.verify_frozen(LABEL)' in source and 'assert pin[key]==value' in source)
    check('full actual frozen source addons tools authorities and preparation source closure collected', all(value in source for value in ("receipt['copies']", "metadata['sourceManifest']", 'backend.capture_addons()', 'backend.tool_dependencies(CANONICAL)', 'for root in [BASE,PRODUCER]', 'add(pin_path,pin_sha);add(review_path,review_sha)')))
    check('mandatory reporting driver and bounded helper selected', "payload['component-driver.mjs']=regular(AMEND/'proposed/component-driver.mjs')" in source and "payload['bounded-comparison.mjs']=regular(AMEND/'bounded-comparison.mjs')" in source)
    check('private original rows backend recheck and config manifest digests retained', 'const frozenRows=index.files.map(row=>({...row}))' in template and 'const nativeRecheck=native.recheck' in template and 'await nativeRecheck()' in template and "CONFIG_SHA='@CONFIG_SHA@',INPUTS_SHA='@INPUTS_SHA@'" in template)
    check('exclusive pre and post publication seals and tool member checks', source.count('load_authority(pin_path,pin_sha,review_path,review_sha)') == 3 and source.count('assert tool_snapshot(roots)==(tool_trees,tool_links)') == 2 and "path.open('xb')" in source and source.rfind('load_authority(pin_path') > source.index('stage.mkdir(exist_ok=False)') and source.index('stage.rename(OUTPUT)') > source.rfind('for row in inputs.values():'))
    check('exact ON authority schema hash before JSON and OFF null', "pins['variants']['benchmark-classic-off']is None" in authority and authority.index("hashlib.sha256(raw).hexdigest()==expected") < authority.index('return json.loads(raw),raw'))
    future = document(OWNER / 'future-authority.json')
    check('future authority template remains null no actual positive tuple in code', future['reviewedPins'] is None and future['rootReviewReceipt'] is None and future['actualONEngineTuple'] is None and pin['engineSha256'] not in source + authority and pin['metadataSha256'] not in source + authority)
    for path in OWNER.glob('*.py'):
        ast.parse(read(path).decode())
    check('owner four Python files parse only no owner import')
    tests = document(OWNER / 'evidence/source-tests.json')
    assert tests['passed'] == len(tests['checks']) == 27 and tests['actionMainOrGenuineVerifierOrPreflightOrGuestOrNativeOrTargetHostInvoked'] is False
    check('stored twenty seven source and negative authority tests authenticated not replayed')
    output = FAMILY / 'measurement-correctness-activated-v1'
    check('future output and staging absent', not output.exists() and not output.is_symlink() and not output.with_name(output.name + '.staging').exists() and not output.with_name(output.name + '.staging').is_symlink())
    # Finish with a second byte read of every item observed by this independent reader.
    for row in list(seen.values()):
        read(row['path'], row['sha256'], row['bytes'])
    evidence = {'schemaVersion': 1, 'files': sorted(seen.values(), key=lambda row: row['path'])}
    evidence_bytes = (json.dumps(evidence, indent=2) + '\n').encode()
    result = {'schemaVersion': 1, 'state': 'INDEPENDENT_FINITE_MEASUREMENT_CORRECTNESS_ACTIVATION_SOURCE_REVIEW_PASSED',
        'ownerIndexSha256': 'ce2f254f2cf27d44df5f0d23915ca4e09c98ac15b2f88f762d41f57fb8e6048e',
        'checks': checks, 'passed': len(checks), 'ownerFiles': 19, 'preparationInputs': 6908, 'genuineProducerFiles': 40,
        'mandatoryReportingFiles': 14, 'frozenCopies': 525, 'actualNativeSources': 342, 'addonSources': 2, 'externalEmbeddingSources': 3,
        'actualCorrectedToolDependencies': 92, 'toolTrees': 2, 'toolLinks': 22, 'uniquePathsRehashed': len(seen),
        'evidenceSha256': sha(evidence_bytes), 'actionMainOrOwnerHelperOrGenuineVerifierOrPreflightOrNodeOrGuestOrNativeOrBundleOrTargetHostExecuted': False,
        'activationOutputCreated': False, 'futureAuthorityTemplateNull': True, 'runtimeAcceptanceClaim': False, 'timingAllowed': False,
        'limitations': ['Source/data review authenticates the actual frozen evidence; it does not invoke the genuine verifier or native preflight.', 'Actual20 workloads plus14 boundaries in retained/fresh Jco and fresh Wasmtime remain a future gate.', 'No scheduler queue-counter visibility, VM root isolation, reset/ALS, whole Streams parity or performance claim.', 'Stored source tests include source-text assertions and pure authority negatives; they are not positive actual activation or guest tests.']}
    for name, raw in [('evidence.json', evidence_bytes), ('results.json', (json.dumps(result, indent=2) + '\n').encode())]:
        with (HERE / name).open('xb') as stream:
            stream.write(raw)
    print(json.dumps({'passed': len(checks), 'paths': len(seen), 'resultSha256': sha((HERE / 'results.json').read_bytes())}))

if __name__ == '__main__':
    main()
