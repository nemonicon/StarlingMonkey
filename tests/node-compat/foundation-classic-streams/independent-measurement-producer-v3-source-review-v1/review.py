"""Independent source/hash/proof reader. No owner module/action/test imports."""
from pathlib import Path
import ast
import hashlib
import json
import stat

HERE = Path(__file__).resolve().parent
FAMILY = HERE.parent
PACKET = FAMILY / 'measurement-producer-candidate-v3'
AMEND = FAMILY / 'measurement-import-path-amendment-v1'
OLD = FAMILY / 'measurement-producer-candidate-v2'
seen = {}


def sha(data): return hashlib.sha256(data).hexdigest()


def read(path, expected=None, size=None):
    path = Path(path); before = path.lstat()
    assert stat.S_ISREG(before.st_mode) and not path.is_symlink(), str(path)
    data = path.read_bytes(); after = path.lstat()
    assert (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) == (
        after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)
    if expected is not None: assert sha(data) == expected, str(path)
    if size is not None: assert len(data) == size, str(path)
    seen[str(path)] = {'path': str(path), 'sha256': sha(data), 'bytes': len(data)}
    return data


def doc(path, expected=None): return json.loads(read(path, expected))


def index(root, expected, count):
    j = doc(root / 'index.json', expected); assert len(j['files']) == count
    for row in j['files']: read(root / row['path'], row['sha256'], row['bytes'])
    return j


def main():
    index(PACKET, '46c031d36c1691c3980c51d44102e1a7cc651ff4bf8b9470c9e746697eece8bc', 40)
    index(AMEND, '801693122f142ef621760e301709e5537cede999008823d95d28f16b39284df4', 13)
    index(OLD, 'e2f8e7be30f32d28f278e39b6ec8ef0a0a6ca01ed2f3dec6aaf4a4374807819f', 36)
    receipt = doc(PACKET / 'source-receipt.json')
    inputs = doc(PACKET / 'input-freeze.json', receipt['inputFreezeSha256'])
    assert len(inputs['inputs']) == 1817
    for row in inputs['inputs']: read(row['path'], row['sha256'], row['bytes'])
    recipe = read(PACKET / 'build-classic-benchmark-engine.sh', 'd98d1129db0a55abe18c2b96e7fe314ab27d6bc9a2ef481abed3f07d996fbba6').decode()
    transform = doc(PACKET / 'producer-transformations.json')
    original = read(FAMILY / 'trace-integration-candidate-v1/source/tests/node-compat/build-engine.sh', transform['parentRecipeSha256']).decode()
    text = original; assert len(transform['edits']) == 17
    for edit in transform['edits']:
        assert text.count(edit['old']) == edit['count']; text = text.replace(edit['old'], edit['new'])
    assert text == recipe
    for edit in reversed(transform['edits']):
        assert text.count(edit['new']) == edit['count']; text = text.replace(edit['new'], edit['old'])
    assert text == original
    support = doc(PACKET / 'support-transformations.json'); assert len(support['files']) == 13
    for row in support['files']:
        parent = FAMILY / row['parentPath'] if 'parentPath' in row else OLD / row['path']
        before = read(parent, row['beforeSha256']).decode()
        after = read(PACKET / row['path'], row['afterSha256']).decode()
        text = before
        for edit in reversed(row['edits']):
            at = edit['beforeOffset']; assert text[at:at + len(edit['old'])] == edit['old']
            text = text[:at] + edit['new'] + text[at + len(edit['old']):]
        assert text == after
        for edit in reversed(row['edits']):
            at = edit['afterOffset']; assert text[at:at + len(edit['new'])] == edit['new']
            text = text[:at] + edit['old'] + text[at + len(edit['new']):]
        assert text == before
    contract = doc(PACKET / 'contract.json')
    assert contract['recipeSha256'] == sha(recipe.encode())
    assert contract['parentRecipeSha256'] == '3694c88b7d000f27e11ffcac835fe0b205b2075f5b1d8d29c61f5b0038ba1cf3'
    assert contract['sourceContractVersion'] == 'sm-classic-trace-source-v1'
    policy = doc(FAMILY / 'trace-integration-candidate-v1/policy.json', contract['sourcePolicySha256'])
    assert contract['classicTraceSourcePolicy'] == policy['classicTraceSourcePolicy']
    assert len(policy['expectedNativeSourceManifest']) == 342
    assert contract['reviewedEnginePins'] is None and contract['nativeSources'] == 342 and contract['declaredNativeAndBuildInputs'] == 344
    assert contract['freezeRoot'] == '/tmp/starling-node-compat/classic-benchmark-trace-v3-artifacts/native-freeze'
    assert contract['diagnosticVersion'] == 'sm-classic-benchmark-trace-diagnostic-v3'
    assert len(contract['addonSources']) == 2
    repo = HERE.parents[3]
    for row in contract['addonSources']: read(repo / row['path'], row['sha256'])
    insertion = "sys.path.insert(0, str(pathlib.Path(packet_root)))\n"
    marker = "benchmark_spec = importlib.util.spec_from_file_location('classic_benchmark_build_policy',pathlib.Path(packet_root)/'benchmark-policy.py')"
    assert recipe.count(insertion) == 1 and insertion + marker in recipe
    assert recipe.index('verify-packet.py') < recipe.index('fetch_checked "https://')
    launch = read(PACKET / 'build-one.py').decode()
    assert "classic-benchmark-trace-v3-build" in launch and "'NODE_COMPAT_JOBS':'1'" in launch
    assert 'requiredStartFreeBytes\':2147483648' in launch and 'stopBelowFreeBytes\':838860800' in launch
    assert "verify_frozen('benchmark-classic-on')" in launch
    assert read(PACKET / 'ancestry/build-one.py') == read(FAMILY / 'trace-integration-candidate-v1/artifact-tools/build-one.py')
    assert doc(PACKET / 'reviewed-pins.json')['variants'] == {'benchmark-classic-on': None, 'benchmark-classic-off': None}
    failure = doc(AMEND / 'source-receipt.json')
    assert failure['wholeBuildRawExitCode'] == 1 and failure['nativeBuildStepsCompleted'] == 109
    assert failure['artifactHasNoMetadata'] is True and failure['artifactHasNoAfterCapture'] is True
    for row in failure['witnesses'] + failure['artifactOutputs']: read(row['path'], row['sha256'], row['bytes'])
    raw = Path(failure['artifactOutputs'][0]['path'])
    assert not Path(str(raw) + '.build.json').exists() and not Path(str(raw) + '.benchmark-after').exists()
    stored = {}
    for name, expected in [('python-test-results.json', 78), ('host-test-results.json', 23), ('import-test-results.json', 8)]:
        data = doc(PACKET / name); assert data['passed'] == expected; stored[name] = expected
    parsed = []
    for path in sorted(PACKET.rglob('*.py')):
        ast.parse(path.read_text(), filename=str(path)); parsed.append(str(path.relative_to(PACKET)))
    index(PACKET, '46c031d36c1691c3980c51d44102e1a7cc651ff4bf8b9470c9e746697eece8bc', 40)
    result = {'schemaVersion': 1, 'state': 'INDEPENDENT_MEASUREMENT_PRODUCER_V3_SOURCE_REVIEW_NO_BLOCKER_NO_ACTIONS',
        'producerIndexSha256': '46c031d36c1691c3980c51d44102e1a7cc651ff4bf8b9470c9e746697eece8bc',
        'amendmentIndexSha256': '801693122f142ef621760e301709e5537cede999008823d95d28f16b39284df4',
        'producerFiles': 40, 'amendmentFiles': 13, 'previousProducerFiles': 36, 'consumedInputs': 1817,
        'recipeEditsForwardReverse': 17, 'supportFilesForwardReverse': 13,
        'pythonAstFiles': len(parsed), 'storedTestsAuthenticatedNotReexecuted': stored,
        'failedV2EvidencePreservedNotAdmitted': True, 'futurePinsNull': True, 'concreteBlockers': [],
        'projectHelpersImported': False, 'actionMainsOrRealPolicyOrNativePreflightOrGuestOrHostExecuted': False,
        'runtimeAcceptanceClaim': False, 'measurementClaim': False, 'uniqueReadFiles': len(seen)}
    with (HERE / 'results.json').open('x') as out: json.dump(result, out, indent=2); out.write('\n')
    with (HERE / 'checked-inputs.json').open('x') as out: json.dump({'schemaVersion': 1, 'files': list(sorted(seen.values(), key=lambda row: row['path']))}, out, indent=2); out.write('\n')
    print(json.dumps(result))


if __name__ == '__main__': main()
