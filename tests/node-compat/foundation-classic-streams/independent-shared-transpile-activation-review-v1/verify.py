"""Independent static-source, hash and reverse-proof reader; no owner code import."""
import datetime
import hashlib
import json
from pathlib import Path
import stat

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
AMEND = BASE/'shared-transpile-interface-amendment-v1'
ACT = BASE/'runtime-activation-candidate-v3'
seen = {}


def file(path, sha=None, size=None):
    path = Path(path)
    before = path.lstat()
    assert stat.S_ISREG(before.st_mode), path
    data = path.read_bytes()
    after = path.lstat()
    assert (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) == (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)
    digest = hashlib.sha256(data).hexdigest()
    assert sha is None or digest == sha, path
    assert size is None or len(data) == size, path
    row = {'path': str(path), 'sha256': digest, 'bytes': len(data)}
    assert str(path) not in seen or seen[str(path)] == row
    seen[str(path)] = row
    return data


def load(path, sha=None):
    return json.loads(file(path, sha))


def index(root, sha, count):
    document = load(root/'index.json', sha)
    assert len(document['files']) == len({row['path'] for row in document['files']}) == count
    for row in document['files']:
        relative = Path(row['path'])
        assert not relative.is_absolute() and '..' not in relative.parts
        file(root/relative, row['sha256'], row['bytes'])


def seal(root, count):
    receipt = load(root/'source-receipt.json')
    document = load(root/'input-freeze.json', receipt['inputFreezeSha256'])
    assert len(document['inputs']) == count
    for row in document['inputs']:
        path = Path(row['path'])
        file(path if path.is_absolute() else root/path, row['sha256'], row['bytes'])


def main():
    index(AMEND, '40166f0eef5bb65a73c89c264933f18f7757f5eb205453d55ac7b8a4a920ed4c', 19)
    index(ACT, '695e17df33a870df86dc15b1494b93a5427a916ccbf18a86e1a38cecf573d2be', 17)
    seal(AMEND, 57)
    seal(ACT, 56)
    transformation = load(AMEND/'transformation-proof.json')
    for row in transformation['files']:
        before = file(AMEND/'before'/row['path'], row['beforeSha256'])
        after = file(AMEND/'proposed/harness'/row['path'], row['afterSha256'])
        assert before == file(BASE/'harness-completion-amendment-v1/proposed/harness'/row['path'])
        reverse = after.decode()
        for edit in reversed(row['edits']):
            assert reverse.count(edit['new']) == edit['occurrences']
            reverse = reverse.replace(edit['new'], edit['old'])
        assert reverse.encode() == before
    assert file(AMEND/'test-inherited-completion.mjs') == file(BASE/'harness-completion-amendment-v1/test-host.mjs')
    driver = file(AMEND/'proposed/harness/component-driver.mjs').decode()
    assert driver.count("await tracked.writeGenerated(join(output,name),bytes,{flag:'wx'});") == 2
    derivation = load(ACT/'derivation-proof.json')
    before = file(BASE/'runtime-activation-candidate-v2/activate.py', derivation['beforeProducerSha256'])
    after = file(ACT/'activate.py', derivation['afterProducerSha256'])
    assert len(derivation['edits']) == 7
    reverse = after.decode()
    for edit in reversed(derivation['edits']):
        assert reverse.count(edit['new']) == 1
        reverse = reverse.replace(edit['new'], edit['old'])
    assert reverse.encode() == before
    assert len(derivation['unchangedBackendFiles']) == 7
    for row in derivation['unchangedBackendFiles']:
        assert file(ACT/row['path'], row['sha256']) == file(BASE/'runtime-activation-candidate-v2'/row['path'], row['sha256'])
    host = load(AMEND/'host-test-results.json')
    assert host['passed'] == 15 and host['failures'] == 0 and host['trackedActualGeneratedFiles'] == 7
    assert host['sharedGeneratedFiles'] == ['interfaces/wasi-random-random.d.ts']
    assert host['jcoVersion'] == '1.40.0'
    assert all(host[key] is False for key in ['guestModuleImported', 'guestExportCalled', 'componentizerInvoked', 'targetHostInvoked'])
    for component in host['actualComponents']:
        file(component['componentPath'], component['componentSha256'], component['componentBytes'])
        for row in component['generatedFiles']:
            file(Path(host['output'])/'actual-two-components'/row['path'], row['sha256'], row['bytes'])
    assert len(host['actualComponents']) == 2
    inherited = load(AMEND/'inherited-completion-results.json')
    owned = load(ACT/'host-test-results.json')
    authority = load(ACT/'authority-test-results.json')
    assert (inherited['passed'], inherited['failures']) == (13, 0)
    assert (owned['passed'], owned['failures']) == (12, 0)
    assert (authority['passed'], authority['failures']) == (6, 0)
    result = {'schemaVersion': 1, 'state': 'INDEPENDENT_SHARED_INTERFACE_AMENDMENT_AND_ACTIVATION_V3_SOURCE_REVIEW_PASSED',
        'reviewedAtUtc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'amendmentIndexSha256': seen[str(AMEND/'index.json')]['sha256'], 'amendmentIndexedFilesRehashed': 19, 'amendmentInputsRehashed': 57,
        'activationIndexSha256': seen[str(ACT/'index.json')]['sha256'], 'activationIndexedFilesRehashed': 17, 'activationInputsRehashed': 56,
        'helperReversibleEdits': 3, 'driverReversibleEdits': 1, 'driverOccurrences': 2, 'activationReversibleEdits': 7, 'backendFilesByteIdentical': 7,
        'sourceReview': ['First writes remain exclusive and require an ordinary output parent.',
            'Only direct interfaces/*.d.ts already tracked in this run may repeat; original, current and new digest/length/bytes must all agree.',
            'Old existing files, changed declarations, core/JavaScript duplicates and symlinks remain refused. This is not a crash/concurrent-writer guarantee.',
            'Completion publication still follows the final admission recheck and requires a separate external raw terminal exit zero.',
            'Only the two Jco output loops change writer. All guest checks, explicit CJS fixture, native authority and five-parameter backend are inherited unchanged.',
            'The new producer binds the amendment index and both afterimages in source/input lineage and writes only a fresh activated-v3 family.',
            'The two Runtime-v2 components used for host transpilation are partial failed-run inputs, not completed guest-suite evidence.'],
        'ownerReportedChecks': {'ownedOutput': 15, 'inheritedCompletion': 13, 'actualHostTranspiledExistingComponents': 2, 'ownedSeal': 12, 'negativeAuthority': 6},
        'independentExecutionScope': 'Static Python data/hash/reverse-proof reader only; no owner helper/test/producer/transpiler/JavaScript admission/guest/target host/native build was executed.',
        'runtimeAcceptanceClaim': False, 'nativePinsChanged': False, 'remainingConcreteSourceBlockers': []}
    (HERE/'results.json').write_text(json.dumps(result, indent=2)+'\n')
    (HERE/'verified-files.json').write_text(json.dumps({'schemaVersion': 1, 'files': sorted(seen.values(), key=lambda row: row['path'])}, indent=2)+'\n')
    print(json.dumps({'state': result['state'], 'uniqueFilesRehashed': len(seen)}))


if __name__ == '__main__':
    main()
