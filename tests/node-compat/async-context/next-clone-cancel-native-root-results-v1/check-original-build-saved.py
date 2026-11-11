"""Portable closed original build DATA; no original path or engine is opened."""
import gzip
import hashlib
import io
import json
from pathlib import Path
import shlex
import stat
import sys

if not __debug__ or not sys.flags.isolated or not sys.dont_write_bytecode:
    raise RuntimeError('Use Python -I -B without optimization before payload reads')

ROOT = Path(__file__).resolve().parent / 'original-build-records'
INDEX_SHA256 = '863b27fbd83e9b8a7a80e33875d2ae63fb727d85e647a505d0bd03db2d97a380'
WORK = '/private/tmp/starling-node-compat/next-clone-cancel-native-build-v1-first'
ENGINE_SHA256 = 'e3075c14ec903831fb43dd305fb9c21eeaeb99a0d0a71c052fbda3a914faa965'
EMPTY_SHA256 = 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'
CMAKE_SOURCE_REFS = {
    'cmake/spidermonkey.cmake': ('af02f2af5ac9d5ceeb6e6e1b63ff433f33377b52d1ec1719732f008c12ad2da7', 8409),
    'cmake/build-crates.cmake': ('3cbf3f9f080345694c40bc329bbc56b553b137d6291eaf745213c285e5a50dab', 5761),
}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def stamp(p):
    s = p.lstat()
    return (s.st_dev, s.st_ino, s.st_mode, s.st_nlink, s.st_size, s.st_mtime_ns, s.st_ctime_ns)


def local(name, limit):
    rel = Path(name)
    assert not rel.is_absolute() and '..' not in rel.parts and rel.as_posix() == name
    p = ROOT / rel
    before = stamp(p)
    assert p.resolve(strict=True) == p and stat.S_ISREG(before[2]) and before[3] == 1 and before[4] <= limit
    with p.open('rb') as f:
        raw = f.read(limit + 1)
    assert len(raw) == before[4] and stamp(p) == before
    return raw


def owned(t, expected):
    assert t['rawExitCode'] == expected and t['parentOwnedGroupGone'] is True
    assert t['allObservedOwnedGroupsGone'] is True and t['timeout'] is False and t['forcedCleanup'] is False
    assert t['errors'] == t['signals'] == t['interruptedSignals'] == t['remainingObservedPids'] == []


def main():
    assert len(sys.argv) == 1
    raw = local('index.json', 2 * 1024**2)
    assert len(raw) == 1080981 and sha(raw) == INDEX_SHA256
    index = json.loads(raw)
    assert index['state'] == 'ORIGINAL_NATIVE_COMPILE_SUCCESS_COLLECTION_FAILURE_RETAINED_V1'
    assert (index['payloadFiles'], index['retainedBytes'], index['originalBytes']) == (2315, 3855415, 21077941)
    assert index['originalOuterExitCode'] == 1 and index['originalDriverPassed'] is False
    assert index['compileAndLinkPassed'] is True and index['engineBinaryRetained'] is False
    assert index['metadataCorrectionIncluded'] is False and index['guestExecuted'] is False
    rows = index['files']
    assert len(rows) == 2315 and sum(r['bytes'] for r in rows) == 3855415
    assert sum(r['original']['bytes'] for r in rows) == 21077941
    assert all(type(r['bytes']) is int and 0 <= r['bytes'] <= 4 * 1024**2 and
               type(r['original']['bytes']) is int and 0 <= r['original']['bytes'] <= 8 * 1024**2 for r in rows)
    documents = {}; originals = {}; names = set(); retained = expanded = 0
    for r in rows:
        assert r['path'] not in names
        names.add(r['path'])
        payload = local(r['path'], r['bytes'])
        assert len(payload) == r['bytes'] and sha(payload) == r['sha256']
        assert r['encoding'] in ('gzip', 'identity')
        if r['encoding'] == 'gzip':
            with gzip.GzipFile(fileobj=io.BytesIO(payload)) as f:
                body = f.read(r['original']['bytes'] + 1)
            name = r['path'][:-3]
            assert r['path'].endswith('.gz')
        else:
            body = payload; name = r['path']
        assert len(body) == r['original']['bytes'] and sha(body) == r['original']['sha256']
        assert name not in documents
        documents[name] = body; originals[name] = r['original']
        retained += len(payload); expanded += len(body)
    physical = {p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file()}
    assert physical == names | {'index.json'} and not any(p.is_symlink() for p in ROOT.rglob('*'))
    assert (retained, expanded) == (3855415, 21077941)
    def doc(name):
        return json.loads(documents[name])
    result = doc('build/result.json'); meta = doc('build/metadata.json')
    assert originals['build/result.json']['sha256'] == '54291d8dd9b7b8ed954ef996e7dbdf2e75cf46c81c70adb6516e523e42bfed7c'
    assert originals['build/metadata.json']['sha256'] == '779bd077b36a94f62091a30ec4018c008dd91b80437f1445a36632867d24f34f'
    assert result['state'] == 'CLONE_CANCEL_NATIVE_BUILD_FAILED_UNACCEPTED_V1' and result['passed'] is False
    assert result['primaryError'] is None and result['buildCommandSucceeded'] is True and result['ownerQuiescenceKnown'] is True
    errors = result['postCollectionErrors']
    assert len(errors) == 1 and errors[0]['type'] == 'AssertionError' and errors[0]['message'] == ''
    assert 'line 431, in actual_metadata' in errors[0]['stack']
    assert "assert all(r['file'] in {x['target']['path'] for x in rows} for r in compile_rows)" in errors[0]['stack']
    assert result['inputProtection']['unchanged'] is True and result['inputProtection']['errors'] == []
    assert result['engineOrGuestExecuted'] is False and result['adoption'] is False
    owned(doc('outer/terminal.json'), 1)
    outer = doc('outer/collection.json')
    assert outer['terminal'] == originals['outer/terminal.json'] and outer['rawExitCode'] == 1 and outer['clean'] is False
    assert outer['primaryError'] is None and outer['verificationError'] is None and outer['inputsUnchanged'] is True
    assert outer['collectionErrors'] == [] and outer['guestConformanceClaim'] is False
    phases = result['phases']
    assert [p['label'] for p in phases] == ['rust-version', 'cargo-version', 'rust-sysroot', 'configure', 'build', 'ninja-commands']
    for phase in phases:
        assert phase['rawExitCode'] == phase['outerRawExitCode'] == 0 and phase['innerOwnedClean'] is True and phase['ownedGone'] is True
        assert phase['timeout'] is False and phase['forcedCleanup'] is False
        assert phase['errors'] == phase['signals'] == phase['interruptedSignals'] == phase['remainingObservedPids'] == []
        name = 'build/results/' + phase['label'] + '/owned-monitor/terminal.json'
        assert phase['outerTerminal'] == originals[name]
        owned(doc(name), 0)
    cargo = result['freshCargoAdmission']; review = doc('build/cargo-metadata-review.json')
    assert cargo == review and cargo['passed'] is True and cargo['command']['clean'] is True
    assert cargo['command']['terminal'] == originals['build/results/cargo-metadata/terminal.json']
    owned(doc('build/results/cargo-metadata/terminal.json'), 0)
    engine = {'path': WORK + '/componentize-source/lib/starlingmonkey_embedding.wasm', 'sha256': ENGINE_SHA256, 'bytes': 31353161}
    assert index['engine'] == result['engineCandidate'] == meta['engine'] == engine
    assert meta['metadataKind'] == 'CLONE_CANCEL_NATIVE_BUILD_ACTUAL_V1' and len(meta) == 52
    assert meta['nativeExportDiagnosticCompileEvidence'] is None
    assert meta['engineExecuted'] is meta['guestExecuted'] is meta['adoption'] is False
    assert result['metadata'] == originals['build/metadata.json']
    composition = doc('build/build-composition.json')
    assert result['sourceComposition'] == originals['build/build-composition.json']
    assert composition['files'] == meta['nativePolicyInputManifest'] and len(composition['files']) == 435
    assert composition['oneChangedNativePath'] == 'builtins/web/fetch/request-response.cpp'
    assert composition['actualAfterimageSHA256'] == '0431184d4562972c98538494caf46d2b11cdf0280f51d0e7143cd8534526442e'
    for name, (hash_value, size) in CMAKE_SOURCE_REFS.items():
        matches = [r for r in composition['files'] if r['path'] == name]
        assert len(matches) == 1 and (matches[0]['sha256'], matches[0]['bytes']) == (hash_value, size)
    recipe = {meta['sourceRoot'] + '/' + r['path'] for r in meta['nativePolicyInputManifest']}
    recipe |= {r['source']['path'] for r in meta['buildSupportInputManifest'] + meta['embeddingInputManifest']}
    assert len(recipe) == 825
    database = doc('build/generated/compile_commands.json')
    assert database == meta['actualCompileRows'] and len(database) == len({r['file'] for r in database}) == 80
    source_rows = [r for r in database if r['file'] in recipe]
    generated = [r for r in database if r['file'] not in recipe]
    assert len(source_rows) == 79 and len(generated) == 1
    null = generated[0]; null_path = WORK + '/build/starling-raw.wasm/null.cpp'
    assert null['file'] == null_path and null['directory'] == WORK + '/build'
    assert null['output'] == WORK + '/build/starling-raw.wasm/CMakeFiles/rust-crates.dir/null.cpp.obj'
    tokens = shlex.split(null['command'])
    assert tokens.count('-c') == 1 and tokens[tokens.index('-c') + 1] == null_path
    assert tokens.count('-o') == 1 and tokens[tokens.index('-o') + 1] == 'starling-raw.wasm/CMakeFiles/rust-crates.dir/null.cpp.obj'
    empty = documents['build/generated/starling-raw.wasm/null.cpp']
    assert empty == b'' and sha(empty) == EMPTY_SHA256 and originals['build/generated/starling-raw.wasm/null.cpp']['path'] == null_path
    # CMake payloads are not in this fixed capture. Verify only their recorded
    # recipe hashes; separate Source audit4f91 supplies WRITE47/add_library86.
    print(json.dumps(dict(savedOriginalFailureConsistent=True, files=len(names), retainedBytes=retained,
        originalBytes=expanded, originalOuterExitCode=1, originalDriverPassed=False,
        sixPhaseRawCodes=[0] * 6, cargoRawCode=0, translationUnits=80, recipeTranslationUnits=79,
        generatedEmptyTranslationUnits=1, recordedSourceRefsMatched=True, cmakeSourcePayloadsRetained=False,
        originalMetadataDiagnosticEvidence=None, metadataCorrectionAccepted=False,
        engineDescriptorRecorded=True, engineBinaryVerified=False, engineOrGuestExecuted=False,
        originalAbsolutePathsRead=False, helperOrToolInvoked=False, fullNextAccepted=False), sort_keys=True))


if __name__ == '__main__':
    main()
