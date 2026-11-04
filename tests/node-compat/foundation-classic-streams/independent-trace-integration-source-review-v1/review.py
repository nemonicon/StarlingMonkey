"""Independent read/hash/AST review. Does not import or execute owner code."""
from pathlib import Path
import ast
import copy
import difflib
import hashlib
import json
import stat
import sys

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
SOURCE = HERE.parent / 'trace-integration-candidate-v1'
EXPECTED = '224fba889e72283d68e5ad01008c91ccfb7970e743a249019856aa43e7422d0b'
observed = {}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def regular(path, digest=None, size=None):
    path = Path(path)
    before = path.lstat()
    assert stat.S_ISREG(before.st_mode), str(path)
    data = path.read_bytes()
    after = path.lstat()
    assert (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) == (
        after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)
    checksum = sha(data)
    if digest is not None:
        assert checksum == digest, str(path)
    if size is not None:
        assert len(data) == size, str(path)
    key = str(path.resolve())
    row = {'path': key, 'sha256': checksum, 'bytes': len(data)}
    assert key not in observed or observed[key] == row
    observed[key] = row
    return data


def document(path, digest=None):
    return json.loads(regular(path, digest))


def indexed(root, expected):
    index = document(root / 'index.json', expected)
    names = set()
    for row in index['files']:
        name = row['path']
        assert name not in names and not Path(name).is_absolute()
        assert all(part not in ('', '.', '..') for part in name.split('/'))
        names.add(name)
        regular(root / name, row['sha256'], row['bytes'])
    return index


def main():
    index = indexed(SOURCE, EXPECTED)
    assert len(index['files']) == 159
    actual = {str(path.relative_to(SOURCE)) for path in SOURCE.rglob('*') if path.is_file()}
    assert actual == {row['path'] for row in index['files']} | {'index.json'}
    assert not any(path.is_symlink() for path in SOURCE.rglob('*'))
    receipt = document(SOURCE / 'source-receipt.json')
    closure = document(SOURCE / 'input-freeze.json', receipt['inputFreezeSha256'])
    assert len(closure['inputs']) == 1175
    for row in closure['inputs']:
        regular(SOURCE / row['path'], row['sha256'], row['bytes'])
    contract = document(SOURCE / 'contract.json')
    policy = document(SOURCE / 'policy.json', contract['sourcePolicySha256'])
    old = document(SOURCE / 'ancestry/policy.json', contract['previousPolicySha256'])
    before = {row['path']: row['sha256'] for row in old['expectedNativeSourceManifest']}
    after = {row['path']: row['sha256'] for row in policy['expectedNativeSourceManifest']}
    assert len(before) == len(after) == 342 and before.keys() == after.keys()
    changed = {name for name in before if before[name] != after[name]}
    assert len(changed) == 3
    fix = HERE.parent / 'trace-semantics-candidate-v1'
    indexed(fix, contract['fixSourceIndexSha256'])
    indexed(HERE.parent / 'independent-trace-semantics-source-review-v1',
            contract['independentFixSourceReviewIndexSha256'])
    delta = policy['classicTraceSourcePolicy']['changes']
    assert {row['path'] for row in delta} == changed
    for row in delta:
        name = row['path']
        assert before[name] == row['beforeSha256'] and after[name] == row['afterSha256']
        old_data = regular(REPO / name, row['beforeSha256'], row['beforeBytes'])
        assert old_data == regular(SOURCE / 'ancestry/native-before' / name)
        assert regular(SOURCE / 'source' / name, row['afterSha256'], row['afterBytes']) == regular(
            fix / 'proposed' / Path(name).name)
    for name in before.keys() - changed:
        regular(REPO / name, before[name])
    expected_policy = copy.deepcopy(old)
    expected_policy['version'] = 'sm-private-ticks-classic-streams-trace-source-v1'
    expected_policy['classicPolicyVersion'] = 'sm-classic-streams-trace-install-v1'
    expected_policy['classicTraceSourcePolicy'] = policy['classicTraceSourcePolicy']
    for row in delta:
        expected_policy['sourceLayer'][row['path']]['afterSha256'] = row['afterSha256']
        next(item for item in expected_policy['expectedNativeSourceManifest']
             if item['path'] == row['path'])['sha256'] = row['afterSha256']
    assert policy == expected_policy
    preimages = {row['path']: row for row in document(SOURCE / 'ancestry/preimages.json')['files']}
    proofs = document(SOURCE / 'transformations.json')['files']
    assert len(proofs) == 10
    for row in proofs:
        snap = preimages[row['origin']]
        original = regular(SOURCE / snap['copy'], row['beforeSha256'], snap['bytes']).decode()
        assert regular(REPO / row['origin'], row['beforeSha256']).decode() == original
        text = original
        for edit in row['edits']:
            assert text.count(edit['old']) == edit['count']
            text = text.replace(edit['old'], edit['new'])
        assert text == regular(SOURCE / row['afterimage'], row['afterSha256']).decode()
        patch = ''.join(difflib.unified_diff(original.splitlines(True), text.splitlines(True),
            fromfile='a/' + row['origin'], tofile='b/' + row['afterimage']))
        assert patch == regular(SOURCE / row['patch'], row['patchSha256']).decode()
        for edit in reversed(row['edits']):
            for offset in reversed(edit['offsets']):
                assert text[offset:offset + len(edit['new'])] == edit['new']
                text = text[:offset] + edit['old'] + text[offset + len(edit['new']):]
        assert text == original
    tools = document(SOURCE / 'artifact-tools/tool-pins.json', contract['toolPinsSha256'])
    assert len(tools['toolDependencies']) == 92
    prefix = 'tests/node-compat/foundation-classic-streams/trace-integration-candidate-v1/'
    for row in tools['toolDependencies']:
        name = row['path']
        if name.startswith(prefix):
            path = SOURCE / name[len(prefix):]
        elif (SOURCE / 'source' / name).is_file():
            path = SOURCE / 'source' / name
        else:
            path = REPO / name
        regular(path, row['sha256'], row['bytes'])
    primary = document(fix / 'primary-source-pins.json')
    deps = {row['path']: row for row in tools['toolDependencies']}
    for row in primary['sources']:
        relative = str((fix / row['path']).relative_to(REPO))
        assert deps[relative]['sha256'] == row['sha256']
        regular(fix / row['path'], row['sha256'], row['bytes'])
    assert str((fix / 'LICENSE.node').relative_to(REPO)) in deps
    selector = regular(SOURCE / 'source/tests/node-compat/module-selection.mjs',
                       contract['productionSelectorSha256'])
    assert selector == regular(REPO / 'tests/node-compat/module-selection.mjs')
    launcher = regular(SOURCE / 'artifact-tools/build-one.py').decode()
    old_launcher = regular(SOURCE / 'ancestry/artifact-build-one.py').decode()
    assert launcher[launcher.index('def error_record'):launcher.index('def main():')] == (
        old_launcher[old_launcher.index('def error_record'):old_launcher.index('def main():')])
    assert contract['minimumStartFreeBytes'] == 2 * 1024**3
    assert contract['stopBelowFreeBytes'] == 800 * 1024**2 and contract['jobs'] == 1
    assert set(document(SOURCE / 'runtime-pins.json')['variants'].values()) == {None}
    assert contract['newEngineHashes'] is None and contract['reviewedFutureEnginePins'] is None
    syntax = []
    for path in sorted(SOURCE.rglob('*.py')):
        ast.parse(path.read_text(), filename=str(path))
        syntax.append(str(path.relative_to(SOURCE)))
    evidence = {}
    for name, count in [('python-source-tests.json', 75), ('node-source-tests.json', 68),
                        ('compile-flag-tests.json', 50), ('external-capture-tests.json', 4)]:
        data = document(SOURCE / 'evidence' / name)
        assert data['passed'] == count and len(data['checks']) == count
        evidence[name] = count
    assert document(SOURCE / 'evidence/syntax-results.json')['count'] == 9
    generator = document(SOURCE / 'evidence/generator-results.json')
    assert generator['exitCode'] == 0 and generator['factoryInvoked'] is False
    assert generator['observed']['vendorFiles'] == 24
    assert generator['observed']['headerSha256'] == next(
        row['afterSha256'] for row in delta if row['path'].endswith('/factories.generated.h'))
    # A final pass binds the whole proposal after this independent read-only review.
    indexed(SOURCE, EXPECTED)
    return {'schemaVersion': 1, 'state': 'INDEPENDENT_TRACE_INTEGRATION_SOURCE_REVIEW_PASSED_ACTIONS_UNEXECUTED',
        'candidateIndexSha256': EXPECTED, 'indexedFiles': 159, 'consumedInputs': 1175,
        'nativeSourceFiles': 342, 'unchangedNativePaths': 339, 'changedNativePaths': 3,
        'exactForwardReverseAndUnifiedPatchProofs': 10, 'toolDependencies': 92,
        'pythonFilesAstParsed': len(syntax), 'storedOwnerEvidenceAuthenticatedNotReexecuted': evidence,
        'allFutureArtifactPinsNull': True, 'concreteBlockers': [],
        'reviewLimitations': [
            'Source review and stored test authentication only; no corrected engine or guest proof.',
            'Owner test mains have fixed stage/output paths or write HERE/evidence; not replayed in the sealed packet.',
            'Native builds/freezes/independent actual artifact review and runtime activation remain future gates.',
            'The generic generator stored result is authenticated, not reexecuted by this reviewer.',
            'Boundary tags and public API profile stay unchanged while source policy/helper/recipe identities change.',
            'Measurement producer successor and real correctness before timing remain required.'],
        'ownerCodeImported': False, 'ownerTestMainsExecuted': False,
        'configureCompilerActionMainsRuntimePreflightPackagerGuestHostOrTimingExecuted': False,
        'sourcePacketChanged': False, 'runtimeAcceptanceClaim': False,
        'uniqueReadInputs': len(observed), 'observedInputs': list(sorted(observed.values(), key=lambda row: row['path']))}


if __name__ == '__main__':
    result = main()
    assert len(sys.argv) == 2
    with Path(sys.argv[1]).open('x') as output:
        json.dump(result, output, indent=2)
        output.write('\n')
    print(json.dumps({key: value for key, value in result.items() if key != 'observedInputs'}))
