"""Source-only request preparer for the separately reviewed new native engine.

Root binds ENGINE_ADMISSION only after the build and its actual review close.
No old fixed-engine context, project helper, compiler or host is imported.
"""
import hashlib
import json
import os
from pathlib import Path
import stat
import sys

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
RESULTS = HERE.parent / 'next-clone-cancel-component-root-results-v1'
OUTPUT = Path('/private/tmp/starling-node-compat/next-clone-cancel-component-v1-first')
ENGINE_ADMISSION = None  # Root supplies the actual closed B admission descriptor.
COMPILER = {'path': str(HERE.parent / 'next-lifecycle-root-results-v1/compiler-selection.json'), 'sha256': '36277ca5d6a71773f75842c7a290aea3acbd5d713e569d84888ea61926b2329b', 'bytes': 2001991}
FIXTURE = {'path': str(HERE.parent / 'web-stream-context-component-v2/index.json'), 'sha256': 'efc000da0331090f1ea0127806b076223bdcb68368907f217aea69d736edf5df', 'bytes': 1718}
WORLD = {'path': str(REPO / 'tests/node-compat/frameworks/nextjs/regexp-unicode-probe-candidate-v1/index.json'), 'sha256': '802595f5a32dd93fc95c63eb95c901352ecb8da180152735982c344d6b827f58', 'bytes': 4565}
CALLER = {'path': str(HERE / 'componentize.mjs'), 'sha256': '143a29f71408680f55adbf85914f2dcdb2e9b515c4d25e7bcc127b8b50468d43', 'bytes': 6730}
CAPTURE = {'path': str(REPO / 'tests/node-compat/frameworks/nextjs/next-node-fs-atomic-construction-v2/capture.mjs'), 'sha256': '5393f6beb74bec2b5f80f8a781ddb0290554830f987c1857c2632630956070ee', 'bytes': 4872}
ADAPTER = {'path': '/private/tmp/starling-node-compat/next-preview1-adapter-v1/next-preview1-adapter.wasm', 'sha256': 'd30ade5b0a146ab1f6cbb878322fa937ec19c4a2b09f7497e9f08e49fb13cfd7', 'bytes': 49672}
INPUTS = {}


def snapshot(p):
    s = p.lstat()
    return tuple(getattr(s, k) for k in ('st_dev', 'st_ino', 'st_mode', 'st_nlink', 'st_size', 'st_mtime_ns', 'st_ctime_ns'))


def descriptor(p):
    p = Path(p)
    before = snapshot(p)
    assert p.is_absolute() and p.resolve(strict=True) == p and stat.S_ISREG(before[2])
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(1024 * 1024), b''):
            h.update(b)
    assert snapshot(p) == before
    return dict(path=str(p), sha256=h.hexdigest(), bytes=before[4])


def checked(ref):
    assert isinstance(ref, dict) and set(ref) == {'path', 'sha256', 'bytes'}
    assert type(ref['bytes']) is int and ref['bytes'] >= 0
    p = Path(ref['path'])
    before = snapshot(p)
    assert descriptor(p) == ref
    previous = INPUTS.get(str(p))
    assert previous is None or previous == (ref, before), 'conflicting input role'
    INPUTS[str(p)] = (ref, before)
    return p


def document(ref):
    assert ref['bytes'] <= 32 * 1024 * 1024
    p = checked(ref)
    data = p.read_bytes()
    assert len(data) == ref['bytes'] and hashlib.sha256(data).hexdigest() == ref['sha256']
    assert snapshot(p) == INPUTS[str(p)][1]
    return json.loads(data)


def member_path(parent, value):
    assert isinstance(value, str)
    p = Path(value)
    if not p.is_absolute():
        assert p.parts and '..' not in p.parts and p.as_posix() == value
        p = parent / p
    assert parent in p.parents and p.resolve(strict=True) == p
    return p


def family(index_ref, expected_files):
    index = document(index_ref)
    parent = Path(index_ref['path']).parent
    rows = index['files']
    assert len(rows) == expected_files
    names = set()
    result = [index_ref]
    for row in rows:
        p = member_path(parent, row['path'])
        assert p not in names
        names.add(p)
        ref = dict(path=str(p), sha256=row['sha256'], bytes=row['bytes'])
        checked(ref)
        result.append(ref)
    actual = set()
    for p in parent.rglob('*'):
        assert not p.is_symlink(), 'closed Source family contains a link'
        if p.is_file():
            actual.add(p)
    assert actual == names | {Path(index_ref['path'])}, 'closed Source family membership changed'
    return result


def compiler_package(selection):
    assert selection['state'] == 'FRESH_COMPILER_PACKAGE_SELECTED_V1'
    pkg = selection['package']
    root = Path(pkg['root'])
    assert root.resolve(strict=True) == root and root.is_dir()
    files, links = set(), set()
    refs = []
    for row in pkg['files']:
        p = member_path(root, row['relativePath'])
        assert row['path'] == str(p) and row['relativePath'] not in files
        files.add(row['relativePath'])
        ref = {k: row[k] for k in ('path', 'sha256', 'bytes')}
        checked(ref)
        assert stat.S_IMODE(p.stat().st_mode) == row['mode']
        refs.append(ref)
    for row in pkg['links']:
        relative = Path(row['path'])
        assert not relative.is_absolute() and '..' not in relative.parts and relative.as_posix() == row['path']
        assert row['path'] not in links
        links.add(row['path'])
        p = root / relative
        assert p.is_symlink() and os.readlink(p) == row['target']
        resolved = p.resolve(strict=True)
        assert str(resolved) == row['resolvedPath'] and root in resolved.parents
    observed_files, observed_links = set(), set()
    pending = [root]
    while pending:
        for p in pending.pop().iterdir():
            relative = p.relative_to(root).as_posix()
            if p.is_symlink():
                observed_links.add(relative)
            elif p.is_dir():
                pending.append(p)
            else:
                assert p.is_file()
                observed_files.add(relative)
    assert observed_files == files and observed_links == links
    return refs


def protect():
    for path, (ref, before) in INPUTS.items():
        p = Path(path)
        assert snapshot(p) == before and descriptor(p) == ref and snapshot(p) == before


def write_request(path, request):
    raw = (json.dumps(request, indent=2) + '\n').encode()
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    primary = None
    try:
        view = memoryview(raw)
        while view:
            n = os.write(fd, view)
            assert n > 0
            view = view[n:]
        os.fsync(fd)
    except BaseException as error:
        primary = error
    try:
        os.close(fd)
    except BaseException:
        if primary is not None:
            raise primary
        raise
    if primary is not None:
        raise primary
    return descriptor(path)


def main():
    if not __debug__ or not sys.flags.isolated or not sys.dont_write_bytecode:
        raise RuntimeError('use unoptimized Python -I -B')
    if ENGINE_ADMISSION is None:
        raise RuntimeError('actual closed new-engine admission is unbound; no input reads or outputs')
    assert len(sys.argv) == 1 and not os.path.lexists(OUTPUT)
    assert not os.path.lexists(RESULTS / 'construction-request.json')
    assert OUTPUT.parent.resolve() == OUTPUT.parent and OUTPUT.parent.is_dir()
    admission = document(ENGINE_ADMISSION)
    assert admission['schemaVersion'] == 1 and admission['state'] == 'CLONE_CANCEL_ACTUAL_ENGINE_ADMISSION_PASSED_V1'
    for key in ('passed', 'completeActualMetadataReviewed', 'nativeBuildPassed'):
        assert admission[key] is True
    assert admission['oldMetadataProjected'] is False and admission['guestExecuted'] is False
    metadata = document(admission['nativeMetadata'])
    keys = sorted(metadata)
    assert admission['metadataKeys'] == admission['metadataFieldsVerified'] == keys
    assert metadata['engine'] == admission['engine']
    checked(admission['engine'])
    collection = document(admission['actualBuildResult'])
    assert collection['state'] == 'CLOSED_NATIVE_BUILD_COLLECTION_REVIEW_COMPLETED_V2'
    assert collection['passed'] is collection['collectionReviewPassed'] is collection['nativeCommandsPassed'] is True
    assert collection['originalDriverPassed'] is False and collection['originalOuterRawExitCode'] == 1
    assert collection['nativeMetadata'] == admission['nativeMetadata'] and collection['engine'] == admission['engine']
    assert collection['originalFailedResult'] == admission['originalFailedBuildResult']
    assert collection['originalMetadata'] == admission['originalFailedBuildMetadata']
    old_result = document(admission['originalFailedBuildResult'])
    assert old_result['state'] == 'CLONE_CANCEL_NATIVE_BUILD_FAILED_UNACCEPTED_V1' and old_result['passed'] is False
    document(admission['originalFailedBuildMetadata'])
    for role in ('actualBuildResult', 'buildSelection', 'actualOuterTerminal', 'actualOuterCollection',
                 'builderSource', 'reviewerSource', 'actualSourceMaterialization',
                 'actualGeneratorResult', 'actualSourceComposition', 'actualCargoMetadataReview',
                 'originalFailedBuildResult', 'originalFailedBuildMetadata'):
        checked(admission[role])
    for role in ('protectedBuildInputs', 'protectedSourceInputs'):
        rows = admission[role]
        assert isinstance(rows, list) and rows
        assert [r['path'] for r in rows] == sorted({r['path'] for r in rows})
        for ref in rows:
            checked(ref)
    protected = admission['protectedBuildInputs'] + admission['protectedSourceInputs']
    for ref in (admission['actualBuildResult'], admission['originalFailedBuildResult'],
                admission['originalFailedBuildMetadata'], admission['engine'], admission['nativeMetadata']):
        assert ref in protected, 'actual result/engine ancestry missing from admission closure'
    compiler = document(COMPILER)
    compiler_package(compiler)
    fixture = family(FIXTURE, 6)
    world = family(WORLD, 28)
    wit_directory = Path(WORLD['path']).parent
    assert len([r for r in world if Path(r['path']).suffix == '.wit']) == 8
    entry_path = Path(FIXTURE['path']).parent / 'guest-entry.mjs'
    entry = next(r for r in fixture if r['path'] == str(entry_path))
    assert entry['sha256'] == '8952f5ffde7ea6eea7f2499a70a0b10153417c115fbd5b6f457a28c531cdf584'
    checked(ADAPTER)
    checked(CAPTURE)
    checked(CALLER)
    for p in sorted(HERE.rglob('*')):
        assert not p.is_symlink()
        if p.is_file():
            checked(descriptor(p))
    protect()
    compiler_package(compiler)
    assert not os.path.lexists(OUTPUT)
    request = dict(schemaVersion=1, state='ROOT_CLONE_CANCEL_ENGINE_CONSTRUCTION_V1',
        engineAdmission=ENGINE_ADMISSION, engine=admission['engine'], nativeMetadata=admission['nativeMetadata'],
        metadataKeys=keys, compilerSelection=COMPILER, entry=entry, capture=CAPTURE,
        correctedBuildCollection=admission['actualBuildResult'],
        originalFailedBuildResult=admission['originalFailedBuildResult'],
        originalFailedBuildMetadata=admission['originalFailedBuildMetadata'],
        adapter=ADAPTER, worldSourceIndex=WORLD, fixtureSourceIndex=FIXTURE,
        witDirectory=str(wit_directory), output=str(OUTPUT),
        inputs=sorted((ref for ref, _ in INPUTS.values()), key=lambda r: r['path']),
        ordinaryExportsAllowed=False, hostServicesAdded=False, oldFixedGuardInvoked=False,
        oldMetadataProjected=False, oldCompilerPackageIdentityClaimed=False,
        componentValidated=False, guestExecuted=False, productionPromotionAllowed=False)
    assert RESULTS.parent.resolve() == RESULTS.parent
    RESULTS.mkdir(mode=0o700, exist_ok=True)
    assert RESULTS.resolve() == RESULTS
    ref = write_request(RESULTS / 'construction-request.json', request)
    print(json.dumps(dict(request=ref, engineMetadataKeys=len(keys), protectedInputs=len(request['inputs']),
                         closedWorldFiles=28, witFiles=8, fixturePayloadFiles=6,
                         componentizer=CALLER, outputCreated=False)), flush=True)


if __name__ == '__main__':
    main()
