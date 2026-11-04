"""Independent v3 data/hash reader. Does not import any reviewed project helper."""
from pathlib import Path
import datetime
import hashlib
import json
import os
import re
import stat

HERE = Path(__file__).resolve().parent
FAMILY = HERE.parent
BASE = FAMILY / 'production-runtime-activated-v3'
ACTIVATED = '7e9520e0859b939a8586e6d0cfa1fe376a3ace75a2624dd777d5825bbf91cf66'
PINS = 'c998dce40ff66a1764ad8c44f8a492b830d40bb6dce958aab711ecf3c5bcbf3e'
ROOT_REVIEW = '1df0d5bcbb4792efa9fe7329b164aede3a2da7bc4dec6c90d011972cfb6d7f56'
RECIPE = '71b48d2e70c5e003fcbcce7620366744c089dd55036036e52926224dfa2614f7'
AUTHORITIES = {
    'integration-candidate-v1': ('5826a3dfc8d79ebbbbd139665dd06f9f493af3aa6f48302f2865611591fcff6d', 191),
    'harness-completion-amendment-v1': ('76e735336884634ab4811963586738da6c70fdcda722a74706e917a07c615489', 12),
    'harness-cjs-contract-amendment-v1': ('5a15ceca10c8037440eb08fc6d47b26e204a0d9b5be752f6866e8dd2ce0169f1', 14),
    'runtime-activation-candidate-v2': ('052a63818003cb4e4f80fbe5aeb0f449f7ab2711829d0a40ed9a05b1b1cd5341', 17),
    'runtime-activation-candidate-v3': ('695e17df33a870df86dc15b1494b93a5427a916ccbf18a86e1a38cecf573d2be', 17),
    'shared-transpile-interface-amendment-v1': ('40166f0eef5bb65a73c89c264933f18f7757f5eb205453d55ac7b8a4a920ed4c', 19),
}
PRIOR_REVIEW = ('independent-shared-transpile-activation-review-v1',
                '460d8f7e2906476a5137aa2fecf7e776e6aca7615c5040141400227bc41b9d40')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def absolute(path):
    return Path(os.path.abspath(path))


def below(root, path):
    assert path != root and path.is_relative_to(root), (root, path)
    assert stat.S_ISDIR(root.lstat().st_mode) and not root.is_symlink(), root
    cursor = path
    while cursor != root:
        assert not cursor.is_symlink(), cursor
        cursor = cursor.parent


def checked(path, expected, size=None):
    path = Path(path)
    before = path.lstat()
    assert stat.S_ISREG(before.st_mode) and not stat.S_ISLNK(before.st_mode), path
    if size is not None:
        assert before.st_size == size, path
    value = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            value.update(block)
    after = path.lstat()
    assert (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) == (
        after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns), path
    assert value.hexdigest() == expected, path
    return before.st_size


def document(path, expected):
    checked(path, expected)
    return json.loads(Path(path).read_bytes())


def membership(root):
    assert stat.S_ISDIR(root.lstat().st_mode) and not root.is_symlink(), root
    rows = []
    for directory, dirs, files in os.walk(root, followlinks=False):
        for name in sorted(dirs + files):
            path = Path(directory) / name
            mode = path.lstat().st_mode
            kind = ('symlink' if stat.S_ISLNK(mode) else 'directory' if stat.S_ISDIR(mode)
                    else 'file' if stat.S_ISREG(mode) else None)
            assert kind, path
            rows.append({'path': str(path.relative_to(root)), 'kind': kind})
        dirs[:] = [name for name in dirs if not (Path(directory) / name).is_symlink()]
    return sorted(rows, key=lambda row: row['path'])


def checked_index(root, expected, count=None):
    index = document(root / 'index.json', expected)
    rows = {row['path']: row for row in index['files']}
    assert len(rows) == len(index['files']), root
    if count is not None:
        assert len(rows) == count, root
    for name, row in rows.items():
        path = absolute(root / name)
        below(root, path)
        checked(path, row['sha256'], row['bytes'])
    return index, rows


def main():
    index, indexed = checked_index(BASE, ACTIVATED, 19)
    assert index['schemaVersion'] == 1 and index['runtimeAcceptanceClaim'] is False
    assert index['state'] == 'ACTUAL_REVIEWED_CLASSIC_RUNTIME_SOURCE_FAMILY_NOT_EXECUTED'
    actual_files = {row['path'] for row in membership(BASE) if row['kind'] == 'file'}
    assert actual_files == set(indexed) | {'index.json'}
    assert not any(row['kind'] == 'symlink' for row in membership(BASE))
    manifest = document(BASE / 'input-freeze.json', indexed['input-freeze.json']['sha256'])
    assert manifest['schemaVersion'] == 1
    inputs, total = {}, 0
    for row in manifest['inputs']:
        path = absolute(BASE / row['path'])
        assert path not in inputs, path
        inputs[path] = row
        if 'boundary' in row:
            below(absolute(BASE / row['boundary']), path)
        total += checked(path, row['sha256'], row['bytes'])
    assert len(inputs) == 6000
    assert len(manifest['toolTrees']) == 2 and len(manifest['toolLinks']) == 22
    canonical, roots, actual_links, tool_files = [], [], set(), 0
    for tree in manifest['toolTrees']:
        root = Path(tree['path'])
        assert str(root.resolve(strict=True)) == tree['realPath']
        canonical.append(Path(tree['realPath']))
        roots.append(root)
        entries = membership(root)
        assert entries == tree['entries'], root
        for row in entries:
            path = absolute(root / row['path'])
            if row['kind'] == 'file':
                assert path in inputs, path
                tool_files += 1
            elif row['kind'] == 'symlink':
                actual_links.add(path)
    declared_links = set()
    for row in manifest['toolLinks']:
        path = Path(row['path'])
        assert path not in declared_links
        declared_links.add(path)
        assert any(path.is_relative_to(root) for root in roots)
        assert path.is_symlink() and os.readlink(path) == row['linkText'], path
        target = path.resolve(strict=True)
        assert str(target) == row['resolvedTarget']
        assert any(target == root or target.is_relative_to(root) for root in canonical), target
        target_mode = target.lstat().st_mode
        kind = 'directory' if stat.S_ISDIR(target_mode) else 'file' if stat.S_ISREG(target_mode) else None
        assert kind == row['targetKind']
        if kind == 'file':
            checked(target, row['targetSha256'], row['targetBytes'])
    assert declared_links == actual_links
    assert tool_files == 4890

    preserved = {}
    for name, (expected, count) in AUTHORITIES.items():
        root = FAMILY / name
        _, rows = checked_index(root, expected, count)
        assert inputs[absolute(root / 'index.json')]['sha256'] == expected
        for relative, row in rows.items():
            consumed = inputs[absolute(root / relative)]
            assert consumed['sha256'] == row['sha256'] and consumed['bytes'] == row['bytes']
        preserved[name] = {'indexSha256': expected, 'indexedFiles': count}
    prior_name, prior_sha = PRIOR_REVIEW
    prior_index, prior_rows = checked_index(FAMILY / prior_name, prior_sha)
    prior_result = json.loads((FAMILY / prior_name / 'results.json').read_bytes())
    assert 'results.json' in prior_rows and prior_result['runtimeAcceptanceClaim'] is False

    pins = document(BASE / 'runtime-pins.json', PINS)
    root_review = document(BASE / 'root-review-receipt.json', ROOT_REVIEW)
    assert (BASE / 'runtime-pins.json').read_bytes() == (FAMILY / 'production-adoption-v1/reviewed-runtime-pins-v1.json').read_bytes()
    assert (BASE / 'root-review-receipt.json').read_bytes() == (FAMILY / 'production-adoption-v1/root-pin-review-receipt.json').read_bytes()
    receipt = json.loads((BASE / 'source-receipt.json').read_bytes())
    assert receipt['pinsSha256'] == PINS and receipt['rootReviewSha256'] == ROOT_REVIEW
    assert receipt['recipeSha256'] == RECIPE
    labels = ['normal-off', 'normal-runtime', 'gc-off', 'disabled-off']
    assert set(pins['variants']) == set(root_review['variants']) == set(labels)
    native = {}
    for label in labels:
        pin = pins['variants'][label]
        assert pin['recipeSha256'] == RECIPE and pin['runtimeAcceptanceClaim'] is False
        for field in ['engineSha256', 'engineBytes', 'receiptSha256', 'freezeReceiptSha256']:
            assert root_review['variants'][label][field] == pin[field] == receipt['actualArtifacts'][label][field]
        frozen_paths = set()
        for row in pin['frozenFiles']:
            path = absolute(row['path'])
            assert path not in frozen_paths
            frozen_paths.add(path)
            consumed = inputs[path]
            assert consumed['sha256'] == row['sha256'] and consumed['bytes'] == row['bytes']
        assert len(frozen_paths) == 405
        assert inputs[absolute(pin['enginePath'])]['sha256'] == pin['engineSha256']
        assert inputs[absolute(pin['enginePath'])]['bytes'] == pin['engineBytes']
        assert inputs[absolute(pin['enginePath'] + '.build.json')]['sha256'] == pin['receiptSha256']
        assert inputs[absolute(pin['freezeReceiptPath'])]['sha256'] == pin['freezeReceiptSha256']
        native[label] = {key: pin[key] for key in ['engineSha256', 'engineBytes', 'receiptSha256', 'freezeReceiptSha256']}

    integration = FAMILY / 'integration-candidate-v1'
    completion = FAMILY / 'harness-completion-amendment-v1'
    shared = FAMILY / 'shared-transpile-interface-amendment-v1'
    cjs = FAMILY / 'harness-cjs-contract-amendment-v1'
    candidate = FAMILY / 'runtime-activation-candidate-v3'
    inherited = ['checks.mjs', 'deferred-snippets.mjs', 'deployed-fixtures.mjs',
                 'node-oracle.mjs', 'node-oracle-results.json', 'run.mjs']
    for name in inherited:
        assert (BASE / 'harness' / name).read_bytes() == (integration / 'harness' / name).read_bytes()
    afterimages = {}
    for name in ['completion.mjs', 'component-driver.mjs']:
        actual = (BASE / 'harness' / name).read_bytes()
        assert actual == (shared / 'proposed/harness' / name).read_bytes()
        before = (shared / 'before' / name).read_bytes()
        assert before == (completion / 'proposed/harness' / name).read_bytes()
        afterimages[name] = digest(actual)
    proof = json.loads((shared / 'transformation-proof.json').read_bytes())
    for row in proof['files']:
        before = (shared / 'before' / row['path']).read_text()
        after = (shared / 'proposed/harness' / row['path']).read_text()
        assert digest(before.encode()) == row['beforeSha256']
        assert digest(after.encode()) == row['afterSha256']
        reconstructed = before
        for edit in row['edits']:
            assert reconstructed.count(edit['old']) == edit['occurrences']
            reconstructed = reconstructed.replace(edit['old'], edit['new'])
        assert reconstructed == after
        reversed_text = after
        for edit in reversed(row['edits']):
            assert reversed_text.count(edit['new']) == edit['occurrences']
            reversed_text = reversed_text.replace(edit['new'], edit['old'])
        assert reversed_text == before
    for name in ['guest.mjs', 'cjs-bindings.cjs']:
        assert (BASE / 'harness' / name).read_bytes() == (cjs / 'proposed/harness' / name).read_bytes()
        afterimages[name] = digest((BASE / 'harness' / name).read_bytes())
    cjs_proof = json.loads((cjs / 'transformation-proof.json').read_bytes())
    guest = (BASE / 'harness/guest.mjs').read_text()
    original_guest = (integration / 'harness/guest.mjs').read_text()
    assert digest(guest.encode()) == cjs_proof['afterGuestSha256']
    for edit in reversed(cjs_proof['edits']):
        assert guest.count(edit['new']) == 1
        guest = guest.replace(edit['new'], edit['old'])
    assert guest == original_guest
    assert digest(guest.encode()) == cjs_proof['beforeGuestSha256']
    assert (BASE / 'runtime-contract.mjs').read_bytes() == (integration / 'runtime-contract.mjs').read_bytes()
    assert (BASE / 'consumed.mjs').read_bytes() == (candidate / 'consumed.mjs').read_bytes()
    template = (BASE / 'runtime-preflight.template.mjs').read_text()
    assert template == (candidate / 'runtime-preflight.template.mjs').read_text()
    parent_receipt = json.loads((integration / 'source-receipt.json').read_bytes())
    replacements = {'PINS_SHA': PINS, 'INPUTS_SHA': indexed['input-freeze.json']['sha256'],
                    'RECIPE_SHA': RECIPE, 'SELECTOR_SHA': parent_receipt['selectorSha256'],
                    'ADMISSION_SHA': parent_receipt['admissionSha256']}
    assert set(re.findall(r'@([A-Z_]+)@', template)) == set(replacements)
    for key, value in replacements.items():
        template = template.replace('@' + key + '@', value)
    assert not re.search(r'@[A-Z_]+@', template)
    assert template.encode() == (BASE / 'runtime-preflight.mjs').read_bytes()
    assert receipt['inputFreezeSha256'] == indexed['input-freeze.json']['sha256']
    assert receipt['consumedFiles'] == len(inputs) and receipt['toolLinks'] == len(actual_links)
    expected_lineage = {
        'activationSourceIndexSha256': AUTHORITIES['runtime-activation-candidate-v3'][0],
        'integrationIndexSha256': AUTHORITIES['integration-candidate-v1'][0],
        'completionAmendmentIndexSha256': AUTHORITIES['harness-completion-amendment-v1'][0],
        'cjsContractAmendmentIndexSha256': AUTHORITIES['harness-cjs-contract-amendment-v1'][0],
        'activationParentIndexSha256': AUTHORITIES['runtime-activation-candidate-v2'][0],
        'sharedTranspileInterfaceAmendmentIndexSha256': AUTHORITIES['shared-transpile-interface-amendment-v1'][0],
    }
    for key, value in expected_lineage.items():
        assert receipt[key] == value
    for field in ['engineMetadataRewritten', 'componentOrHostExecuted', 'runtimeAcceptanceClaim']:
        assert receipt[field] is False
    copied = {row['path']: row for row in receipt['copiedPayloads']}
    assert len(copied) == len(receipt['copiedPayloads'])
    assert set(copied) == set(indexed) - {'source-receipt.json'}
    for name, row in copied.items():
        assert row == indexed[name]
    checked(BASE / 'index.json', ACTIVATED)
    result = {
        'schemaVersion': 1,
        'state': 'INDEPENDENT_ACTIVATED_CLASSIC_RUNTIME_V3_SOURCE_AND_CLOSURE_VERIFIED_NO_GUEST',
        'verifiedAtUtc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'activatedIndexSha256': ACTIVATED,
        'activatedIndexRowsRehashed': len(indexed),
        'activatedFileMembershipExact': True,
        'inputFreezeSha256': indexed['input-freeze.json']['sha256'],
        'consumedFiles': len(inputs),
        'consumedLogicalBytesHashed': total,
        'toolRoots': len(roots), 'toolRegularFiles': tool_files,
        'toolLinks': len(actual_links), 'wholeToolMembershipAndLinkSetExact': True,
        'pinsSha256': PINS, 'rootReviewSha256': ROOT_REVIEW,
        'copiedAuthoritiesByteExact': True, 'authorityTupleFieldsCompared': 16,
        'nativeArtifacts': native, 'fourFrozenInventoriesIncluded': True,
        'frozenInventoryRowsPerVariant': 405,
        'preservedSourceAuthorities': preserved,
        'priorIndependentReviewIndexSha256': prior_sha,
        'priorIndependentReviewFilesRehashed': len(prior_rows),
        'mandatoryAfterimages': afterimages,
        'sharedHelperAndDriverReverseProofsReconstructed': True,
        'cjsPlacementReverseRestoresOriginalGuest': True,
        'inheritedHarnessAndOracleFilesByteExact': len(inherited),
        'compiledPreflightParameters': replacements,
        'compiledPreflightSha256': indexed['runtime-preflight.mjs']['sha256'],
        'compiledPreflightReconstructedByteExact': True,
        'sourceReview': [
            'Only the two Jco result loops use writeGenerated; ordinary output writes retain wx.',
            'First generated writes use the existing exclusive writer. Reuse requires a same-writer tracked direct interfaces/*.d.ts pathname and original/current/new digest, length and byte agreement.',
            'Existing untracked outputs, other duplicate paths, symlink paths and changed declarations remain refused under the reviewed sequential host writer model.',
            'Completion publication follows the final admission recheck and requires independently collected raw terminal exit zero.',
        ],
        'remainingConcreteSourceBlockers': [],
        'readerOnly': True,
        'ownerHelperOrVerifierInvoked': False,
        'javascriptAdmissionInvoked': False,
        'packageLoaderInvoked': False,
        'transpilerOrComponentizerInvoked': False,
        'nativeBuildInvoked': False,
        'wasmOrGuestOrTargetHostInvoked': False,
        'runtimeAcceptanceClaim': False,
        'limitations': [
            'Source, artifact bytes and consumed closure review only; no guest execution, GC correctness, performance or full Node compatibility proof.',
            'Static source review does not establish crash recovery, concurrent writer safety or behavior of future invocations.',
            'The four existing native engine bytes and metadata are unchanged; this review does not repeat their native provenance analysis.',
        ],
    }
    with (HERE / 'results.json').open('x') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
    print(json.dumps({key: result[key] for key in [
        'state', 'activatedIndexRowsRehashed', 'consumedFiles', 'toolRegularFiles',
        'toolLinks', 'compiledPreflightReconstructedByteExact', 'remainingConcreteSourceBlockers']}))


if __name__ == '__main__':
    main()
