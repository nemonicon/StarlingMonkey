#!/usr/bin/env python3
"""Independent standard-library data/hash reader; executes no reviewed project code."""
from pathlib import Path
import datetime
import hashlib
import json
import os
import stat

HERE = Path(__file__).resolve().parent
FAMILY = HERE.parent
BASE = FAMILY / 'production-runtime-activated-v3'
INDEX = '7e9520e0859b939a8586e6d0cfa1fe376a3ace75a2624dd777d5825bbf91cf66'
PINS = 'c998dce40ff66a1764ad8c44f8a492b830d40bb6dce958aab711ecf3c5bcbf3e'
ROOT = '1df0d5bcbb4792efa9fe7329b164aede3a2da7bc4dec6c90d011972cfb6d7f56'
RECIPE = '71b48d2e70c5e003fcbcce7620366744c089dd55036036e52926224dfa2614f7'
ENGINES = {'normal-off': ('b8279ee1fedc4e26b7319b6777f6a413242cee0c36169a14195f5c24c44511e4', 9973535, False, 'off'), 'normal-runtime': ('1a3f4628d4f63445ec0c1a212a38f1eb3ac01fe22ea2d5d2d54f0210f388fd14', 9980809, False, 'runtime-only'), 'gc-off': ('f9f48f4f8351654a2f2859eeda944ed144ba5c334f914b7f09bec14b0a5e4236', 9975084, True, 'off'), 'disabled-off': ('27e625a7aa483448b9c6b9b258d1f8c4e45da99c2a41f9844c1afce3924fc526', 9759514, False, 'off')}

checks = {}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def absolute(path):
    return Path(os.path.abspath(path))


def regular(path, expected=None, size=None):
    path = absolute(path)
    before = path.lstat()
    assert stat.S_ISREG(before.st_mode), str(path)
    if size is not None:
        assert before.st_size == size, str(path)
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    after = path.lstat()
    assert (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) == (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns), str(path)
    row = {'path': str(path), 'sha256': h.hexdigest(), 'bytes': before.st_size}
    assert expected is None or expected == row['sha256'], str(path)
    if str(path) in checks:
        assert checks[str(path)] == row
    checks[str(path)] = row
    return row


def document(path, expected=None, size=None):
    row = regular(path, expected, size)
    data = Path(path).read_bytes()
    assert digest(data) == row['sha256']
    return json.loads(data)


def below(root, path):
    root, path = absolute(root), absolute(path)
    assert path != root and path.is_relative_to(root), (str(root), str(path))
    assert root.is_dir() and not root.is_symlink(), str(root)
    cursor = path
    while cursor != root:
        assert not cursor.is_symlink(), str(cursor)
        cursor = cursor.parent


def membership(root):
    assert root.is_dir() and not root.is_symlink(), str(root)
    rows = []
    for directory, dirs, files in os.walk(root, followlinks=False):
        for name in sorted(dirs + files):
            path = Path(directory) / name
            mode = path.lstat().st_mode
            kind = ('symlink' if stat.S_ISLNK(mode) else 'directory' if stat.S_ISDIR(mode) else 'file' if stat.S_ISREG(mode) else None)
            assert kind, str(path)
            rows.append({'path': str(path.relative_to(root)), 'kind': kind})
        dirs[:] = [name for name in dirs if not (Path(directory) / name).is_symlink()]
    return sorted(rows, key=lambda row: row['path'])


def main():
    index = document(BASE/'index.json', INDEX)
    assert index['state'] == 'ACTUAL_REVIEWED_CLASSIC_RUNTIME_SOURCE_FAMILY_NOT_EXECUTED'
    assert index['runtimeAcceptanceClaim'] is False
    indexed = {row['path']: row for row in index['files']}
    assert len(indexed) == len(index['files']) == 19
    for name, row in indexed.items():
        path = BASE/name
        below(BASE, path)
        regular(path, row['sha256'], row['bytes'])
    entries = membership(BASE)
    assert {row['path'] for row in entries if row['kind'] == 'file'} == set(indexed) | {'index.json'}
    assert not any(row['kind'] == 'symlink' for row in entries)
    source = document(BASE/'source-receipt.json', indexed['source-receipt.json']['sha256'])
    inputs = document(BASE/'input-freeze.json', source['inputFreezeSha256'])
    assert source['consumedFiles'] == len(inputs['inputs']) == 6000
    assert source['toolLinks'] == len(inputs['toolLinks']) == 22
    assert source['pinsSha256'] == PINS and source['rootReviewSha256'] == ROOT and source['recipeSha256'] == RECIPE
    assert source['engineMetadataRewritten'] is source['componentOrHostExecuted'] is source['runtimeAcceptanceClaim'] is False
    consumed = {}
    total_bytes = 0
    for row in inputs['inputs']:
        path = absolute(BASE/row['path'])
        assert path not in consumed, str(path)
        consumed[path] = row
        if 'boundary' in row:
            below(BASE/row['boundary'], path)
        total_bytes += regular(path, row['sha256'], row['bytes'])['bytes']
    assert len(inputs['toolTrees']) == 2
    trees, canonical, actual_links, tool_files = [], [], set(), 0
    for tree in inputs['toolTrees']:
        root = Path(tree['path'])
        assert str(root.resolve(strict=True)) == tree['realPath'], str(root)
        trees.append(root)
        canonical.append(Path(tree['realPath']))
        entries = membership(root)
        assert entries == tree['entries'], str(root)
        for row in entries:
            path = absolute(root/row['path'])
            if row['kind'] == 'file':
                assert path in consumed, str(path)
                tool_files += 1
            elif row['kind'] == 'symlink':
                actual_links.add(path)
    assert tool_files == 4890
    declared_links = set()
    for row in inputs['toolLinks']:
        path = Path(row['path'])
        assert path not in declared_links
        declared_links.add(path)
        assert any(path.is_relative_to(root) for root in trees)
        assert path.is_symlink() and os.readlink(path) == row['linkText'], str(path)
        target = path.resolve(strict=True)
        assert str(target) == row['resolvedTarget'], str(path)
        assert any(target == root or target.is_relative_to(root) for root in canonical), str(target)
        mode = target.lstat().st_mode
        kind = 'directory' if stat.S_ISDIR(mode) else 'file' if stat.S_ISREG(mode) else None
        assert kind == row['targetKind'], str(path)
        if kind == 'file':
            regular(target, row['targetSha256'], row['targetBytes'])
    assert declared_links == actual_links
    pins = document(BASE/'runtime-pins.json', PINS)
    authority = document(BASE/'root-review-receipt.json', ROOT)
    regular(FAMILY/'production-adoption-v1/reviewed-runtime-pins-v1.json', PINS)
    regular(FAMILY/'production-adoption-v1/root-pin-review-receipt.json', ROOT)
    assert authority['reviewedPinsSha256'] == PINS and authority['runtimeAcceptanceClaim'] is False
    native = {}
    for label, (engine_sha, engine_size, gc_stress, entropy) in ENGINES.items():
        pin = pins['variants'][label]
        assert pin['engineSha256'] == engine_sha and pin['engineBytes'] == engine_size
        assert pin['gcStress'] is gc_stress and pin['entropyPolicy'] == entropy and pin['classicStreamsEnabled'] is (label != 'disabled-off')
        assert pin['sourceFiles'] == 342 and pin['recipeSha256'] == RECIPE
        for field in ['engineSha256', 'engineBytes', 'receiptSha256', 'freezeReceiptSha256']:
            assert pin[field] == authority['variants'][label][field] == source['actualArtifacts'][label][field]
        frozen = {absolute(row['path']): row for row in pin['frozenFiles']}
        assert len(frozen) == len(pin['frozenFiles']) == 405
        for path, row in frozen.items():
            assert path in consumed
            assert consumed[path]['sha256'] == row['sha256'] and consumed[path]['bytes'] == row['bytes']
            regular(path, row['sha256'], row['bytes'])
        engine = regular(pin['enginePath'], engine_sha, engine_size)
        receipt = document(pin['enginePath']+'.build.json', pin['receiptSha256'])
        freeze = document(pin['freezeReceiptPath'], pin['freezeReceiptSha256'])
        assert freeze['state'] == 'immutable-release-engine-frozen' and freeze['label'] == label
        assert freeze['engine'] == pin['enginePath'] and freeze['engineSha256'] == receipt['engineSha256'] == engine_sha
        assert freeze['engineBytes'] == receipt['engineBytes'] == engine_size
        assert freeze['receiptSha256'] == pin['receiptSha256'] and freeze['recipeSha256'] == receipt['buildRecipeSha256'] == RECIPE
        assert freeze['nativeInputsVerified'] == len(receipt['sourceManifest']) == 342
        assert freeze['externalEmbeddingInputsVerified'] == len(receipt['componentizeSourceManifest']) == 3
        assert freeze['originalReceiptPreserved'] is freeze['allInputsValidatedBeforeCopies'] is freeze['allCopiesAndOriginalsRehashed'] is True
        assert freeze['guestExecutedByHelper'] is False
        assert {absolute(row['path']):(row['sha256'],row['bytes']) for row in freeze['copies']} == {path:(row['sha256'],row['bytes']) for path,row in frozen.items()}
        original_engine = regular(freeze['originalEngine'], engine_sha, engine_size)
        original_receipt = regular(freeze['originalMetadataPath'], pin['receiptSha256'])
        assert receipt['hostApi'] == 'wasi-0.2.10'
        assert receipt['gcStress'] is gc_stress and receipt['entropyPolicy'] == entropy
        assert receipt['classicStreamsEnabled'] is (label != 'disabled-off')
        assert receipt['internalTicksEnabled'] is receipt['strictInitialization'] is True
        assert receipt['oomTesting'] is receipt['debuggerEnabled'] is receipt['wptSupportEnabled'] is False
        assert receipt['sourceInputsCapturedBeforeBuild'] is receipt['componentizeSourcesCapturedBeforeBuild'] is receipt['buildRecipeCheckedBeforeAndAfterBuild'] is True
        for root_field, manifest_field in [('sourceRoot','sourceManifest'), ('componentizeSourceRoot','componentizeSourceManifest')]:
            root = Path(pin[root_field])
            rows = receipt[manifest_field]
            assert len({row['path'] for row in rows}) == len(rows)
            for row in rows:
                path = root/row['path']
                below(root,path)
                assert path in frozen and frozen[path]['sha256'] == row['sha256']
                regular(path,row['sha256'])
        for row in receipt['selectedModuleManifests']:
            regular(Path(pin['sourceRoot'])/row['path'],row['sha256'])
        regular(pin['recipePath'], RECIPE)
        regular(pin['cachePath'], pin['cmakeCacheSha256'])
        regular(pin['commandsPath'], pin['compileCommandsSha256'])
        regular(pin['parentEmbeddingCommandPath'],pin['parentEmbeddingCommandSha256'])
        assert receipt['cmakeCacheSha256'] == pin['cmakeCacheSha256'] and receipt['compileCommandsSha256'] == pin['compileCommandsSha256']
        assert freeze['observedCMakeOptions'] == receipt['observedCMakeOptions']
        observed = receipt['observedCMakeOptions']
        assert observed['CMAKE_BUILD_TYPE'] == 'Release' and observed['NODE_COMPAT_CLASSIC_STREAMS'] == ('OFF' if label == 'disabled-off' else 'ON')
        assert observed['NODE_COMPAT_ENTROPY_MODE'] == ('RUNTIME_ONLY' if entropy == 'runtime-only' else 'OFF')
        assert observed['NODE_COMPAT_GC_STRESS'] == ('ON' if gc_stress else 'OFF')
        assert observed['NODE_COMPAT_OOM_TESTING'] == observed['ENABLE_JS_DEBUGGER'] == observed['ENABLE_BUILTIN_WPT_SUPPORT'] == 'OFF'
        cache = {}
        for line in Path(pin['cachePath']).read_text().splitlines():
            if line and not line.startswith(('#','//')) and ':' in line and '=' in line:
                key, value = line.split('=',1)
                cache[key.split(':',1)[0]] = value
        assert all(cache[key] == value for key,value in observed.items())
        command_rows = document(pin['commandsPath'],pin['compileCommandsSha256'])
        commands = [row['command'] for row in command_rows]
        assert len(commands) == len(set(commands))
        for policy_field, command_field in [('classicStreamsPolicy','actualPrivateTargetCompileCommands'), ('classicStreamsPolicy','actualRegistrationCompileCommands'), ('internalTickPolicy','actualLayoutCompileCommands')]:
            for command in receipt[policy_field][command_field]:
                assert command in commands
                assert '-DNODE_COMPAT_INTERNAL_TICKS=1' in command
        post = freeze['postBuildEmbeddingEvidence']
        assert post['exitCode'] == 0 and post['stderr'] == ''
        assert post['path'] == pin['parentEmbeddingCommandPath'] and post['sha256'] == pin['parentEmbeddingCommandSha256']
        text = Path(post['path']).read_text()
        assert all(command in text for command in post['compileCommands'])
        assert receipt['classicStreamsPolicy']['addsExternalCapabilities'] is False
        native[label] = {
            'engine': engine, 'buildReceipt': regular(pin['enginePath']+'.build.json', pin['receiptSha256']),
            'freezeReceipt': regular(pin['freezeReceiptPath'], pin['freezeReceiptSha256']),
            'originalEngine': original_engine, 'originalBuildReceipt': original_receipt,
            'engineMetadataUnchanged': True, 'frozenFilesRehashed': 405, 'sourceManifestFilesCompared': 342,
            'componentizeManifestFilesCompared': 3, 'selectedManifestFilesCompared': len(receipt['selectedModuleManifests']),
            'gcStress': gc_stress, 'entropyPolicy': entropy, 'hostApi': receipt['hostApi'],
            'oomTesting': receipt['oomTesting'], 'debuggerEnabled': receipt['debuggerEnabled'],
            'wptSupportEnabled': receipt['wptSupportEnabled'], 'observedCMakeOptions': observed,
            'actualRecordedPrivateAndLayoutCommandsFoundInFrozenCompileCommands': True,
            'cmakeCache': regular(pin['cachePath'],pin['cmakeCacheSha256']),
            'compileCommands': regular(pin['commandsPath'],pin['compileCommandsSha256']),
            'postBuildEmbeddingCommands': regular(post['path'],post['sha256']),
        }
    regular(BASE/'index.json',INDEX)
    result = {
        'schemaVersion':1,'state':'ACTIVATED_REGRESSION_V2_FULL_RUNTIME_NATIVE_REHASH_PASSED',
        'reviewedAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'activatedIndex':regular(BASE/'index.json',INDEX),'activatedFilesRehashed':19,
        'inputFreeze':regular(BASE/'input-freeze.json',source['inputFreezeSha256']),
        'consumedFilesRehashed':6000,'consumedBytesRehashed':total_bytes,'toolTreesMembershipChecked':2,
        'toolTreeRegularFilesRehashed':4890,'toolLinksRechecked':22,
        'pins':regular(BASE/'runtime-pins.json',PINS),'rootReview':regular(BASE/'root-review-receipt.json',ROOT),
        'sourceReceipt':regular(BASE/'source-receipt.json',indexed['source-receipt.json']['sha256']),
        'native':native,
        'executedReviewedHelpers':False,'guestHostBuildTranspileOrNodeExecuted':False,
        'limitations':['This is current file/manifest and recorded provenance verification, not an independent observation of a past build.','No guest, host, Node, build, componentization, transpilation, or JavaScript admission was executed.'],
    }
    verified = {'schemaVersion':1,'files':sorted(checks.values(),key=lambda row:row['path'])}
    verified_data = (json.dumps(verified,indent=2)+'\n').encode()
    (HERE/'runtime-native-verified-files.json').write_bytes(verified_data)
    result['verifiedFiles'] = {'path':'runtime-native-verified-files.json','sha256':digest(verified_data),'bytes':len(verified_data),'count':len(verified['files'])}
    (HERE/'runtime-native-results.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({key:result[key] for key in ['state','activatedFilesRehashed','consumedFilesRehashed','toolLinksRechecked']}))


if __name__ == '__main__':
    main()
