"""Independent finite READ/HASH/JSON DATA review; no owner code is loaded."""
from pathlib import Path
import hashlib
import json
import os
import stat

REPO = Path('/Users/dan/dev/StarlingMonkey')
K = REPO / 'tests/node-compat/foundation-crypto'
OUT = K / 'independent-native-v2-validation-bootstrap-results-review-v1'
SOURCE = K / 'native-integration-candidate-v2'
STAGE = Path('/private/tmp/starling-node-compat/crypto-owner-source-v2')
FROZEN = Path('/tmp/starling-node-compat/production-crypto-owner-v2/native-freeze')
EXPORT = Path('/tmp/starling-node-compat/crypto-owner-v2-normal-off-pin-export-root')
BOOT = Path('/tmp/starling-node-compat/crypto-owner-v2-normal-off-bootstrap-root')
SOURCE_SHA = '68b6f2a50174adbf30d8257f8107dd6c5b38beddf0db4b95ad972e3f47e25575'
SOURCE_PEER_SHA = 'ebbfda800fc288ea249b9c2e3af2f77a6a0ae1153bc9586b9aab91999a060dac'
NATIVE_SHA = '27b88caeb580bfa0e4f1ab0f6ed6b18c028177f19167d9e5b1cd7b2493144f36'
LABELS = ['normal-off', 'normal-runtime', 'gc-off', 'disabled-off']
BACKEND = {'verified': False, 'version': None, 'vernum': None}
ledger = {}
index_reviews = []

def require(condition, message):
    if not condition:
        raise ValueError(message)

def equal(actual, expected, message):
    require(json.dumps(actual, sort_keys=True, separators=(',', ':')) ==
            json.dumps(expected, sort_keys=True, separators=(',', ':')), message)

def same_file_descriptor(actual, expected, message):
    equal(actual['sha256'], expected['sha256'], message + ' hash')
    equal(actual['bytes'], expected['bytes'], message + ' bytes')
    require(canonical(actual['path']) == canonical(expected['path']), message + ' documented /tmp alias only')

def canonical(path):
    value = str(path)
    return Path('/private' + value) if value == '/tmp' or value.startswith('/tmp/') else Path(value)

def safe_regular(path):
    path = Path(path)
    require(path.is_absolute() and str(path) == os.path.normpath(str(path)), 'absolute normalized path: ' + str(path))
    actual = canonical(path)
    for ancestor in reversed([actual, *actual.parents]):
        info = ancestor.lstat()
        require(not stat.S_ISLNK(info.st_mode), 'unexpected symlink: ' + str(ancestor))
        if ancestor != actual:
            require(stat.S_ISDIR(info.st_mode), 'ancestor not directory: ' + str(ancestor))
    require(stat.S_ISREG(actual.lstat().st_mode), 'not a regular file: ' + str(path))
    return actual

def observed(path, expected=None, size=None, retain=False):
    path = Path(path)
    key = str(path)
    if key in ledger and not retain:
        row = ledger[key]
        require(expected is None or row['sha256'] == expected, 'conflicting hash: ' + key)
        require(size is None or row['bytes'] == size, 'conflicting size: ' + key)
        return row
    physical = safe_regular(path)
    before = physical.stat()
    digest = hashlib.sha256()
    blocks = [] if retain else None
    with physical.open('rb') as stream:
        while True:
            block = stream.read(4 * 1024 * 1024)
            if not block:
                break
            digest.update(block)
            if retain:
                blocks.append(block)
    after = physical.stat()
    signature = lambda info: (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns, info.st_ctime_ns)
    require(signature(before) == signature(after), 'file changed during read: ' + key)
    row = {'path': key, 'sha256': digest.hexdigest(), 'bytes': after.st_size}
    require(expected is None or row['sha256'] == expected, 'hash mismatch: ' + key)
    require(size is None or row['bytes'] == size, 'size mismatch: ' + key)
    if key in ledger:
        equal(row, ledger[key], 'file changed after prior read: ' + key)
    ledger[key] = row
    return (row, b''.join(blocks)) if retain else row

def checked(row):
    require(set(row) >= {'path', 'sha256', 'bytes'}, 'descriptor fields')
    require(type(row['bytes']) is int and row['bytes'] >= 0, 'descriptor byte count')
    result = observed(row['path'], row['sha256'], row['bytes'])
    equal(result, {key: row[key] for key in ['path', 'sha256', 'bytes']}, 'descriptor exact')
    return result

def unique_object(pairs):
    value = {}
    for key, item in pairs:
        require(key not in value, 'duplicate JSON key: ' + key)
        value[key] = item
    return value

def data(path, sha=None, size=None):
    _, raw = observed(path, sha, size, retain=True)
    require(not raw.startswith(b'\xef\xbb\xbf'), 'unexpected BOM')
    return json.loads(raw.decode('utf-8', errors='strict'), object_pairs_hook=unique_object)

def text(path):
    return observed(path, retain=True)[1].decode('utf-8', errors='strict')

def relative(value):
    require(isinstance(value, str) and value and '\\' not in value and '\0' not in value,
            'finite relative path')
    require(not value.startswith('/') and all(part not in ('', '.', '..') for part in value.split('/')),
            'normalized relative path')
    return value

def tree_files(root):
    root = canonical(root)
    require(root.is_dir() and not root.is_symlink(), 'tree root')
    files = []
    for directory, dirs, names in os.walk(root, followlinks=False):
        for name in dirs:
            require(not (Path(directory) / name).is_symlink(), 'tree directory symlink')
        for name in names:
            path = Path(directory) / name
            safe_regular(path)
            files.append(str(path.relative_to(root)))
    return sorted(files)

def index(root, sha, count):
    root = Path(root)
    value = data(root / 'index.json', sha)
    rows = value['files']
    require(len(rows) == count, 'index count: ' + str(root))
    names = [relative(row['path']) for row in rows]
    require(len(names) == len(set(names)), 'index duplicate member')
    for row in rows:
        observed(root / row['path'], row['sha256'], row['bytes'])
    equal(tree_files(root), sorted(names + ['index.json']), 'exact indexed membership: ' + str(root))
    index_reviews.append({'index': observed(root / 'index.json'), 'indexedFiles': count,
                          'actualRegularFiles': count + 1, 'exactMembership': True})
    return value

def write(name, value):
    path = OUT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False)
        stream.write('\n')

def main():
    root_path = K / 'native-v2-validation-bootstrap-root-results-v1.json'
    root = data(root_path, '63471df120d18a24bb5625833337a2ef541d9eec0a99d0679ff4571e4339d4d8', 4513)
    for value in root.values():
        if isinstance(value, dict) and set(value) >= {'path', 'sha256', 'bytes'}:
            checked(value)
    native_ref = root['independentNormalNativeReview']
    checked(native_ref['index']); checked(native_ref['result'])
    native_dir = Path(native_ref['index']['path']).parent
    index(native_dir, NATIVE_SHA, 21)
    native = data(native_ref['result']['path'])
    require(native['artifactReviewPassed'] is True and native['variant'] == 'normal-off', 'accepted native review')
    require(native['ownerActionsInvoked'] is False and native['concreteBlockers'] == [], 'native scope')
    for row in native['verifiedFiles']:
        checked(row)
    require(len(native['verifiedFiles']) == 8821, 'native finite ledger count')
    source_peer_dir = K / 'independent-crypto-owner355-native-integration-v2-source-review-v1'
    index(source_peer_dir, SOURCE_PEER_SHA, 8)
    source_peer = data(source_peer_dir / 'results.json')
    equal(source_peer['resolvedFinding'], 'CRYPTO-OWNER355-CONTEXT-API-M1', 'resolved source M1')
    require(source_peer['sourceReviewPassed'] is True and source_peer['ownerActionsInvoked'] is False, 'source peer scope')
    source_peer_rows = data(source_peer_dir / 'rehashed-inputs.json')
    require(len(source_peer_rows) == 1711, 'source peer finite inputs')
    for row in source_peer_rows:
        checked(row)
    source_index = index(SOURCE, SOURCE_SHA, 44)
    staged_base = STAGE / SOURCE.relative_to(REPO)
    equal(data(staged_base / 'index.json', SOURCE_SHA), source_index, 'configured source index')
    for row in source_index['files']:
        observed(staged_base / row['path'], row['sha256'], row['bytes'])
    prep = data(SOURCE / 'input-freeze.json')
    require(len(prep['files']) == 1323, 'source preparation rows')
    for row in prep['files']:
        checked(row)
    policy = data(SOURCE / 'policy.json')
    contract = data(SOURCE / 'admission-pins.json')
    bootstrap_contract = data(SOURCE / 'bootstrap-contract.json')
    tools = data(SOURCE / 'artifact-tools/tool-pins.json')
    require(len(tools['toolDependencies']) == 922 and tools['reviewedEnginePins'] is None, 'configured tool closure')
    for row in tools['toolDependencies']:
        observed(STAGE / relative(row['path']), row['sha256'], row['bytes'])
    candidate = data(root['candidateData']['path'])
    pins = data(root['reviewedPins']['path'])
    review = data(root['rootReview']['path'])
    require(candidate['state'] == 'UNREVIEWED_CRYPTO_OWNER355_PRODUCTION_PIN_CANDIDATES_V1', 'candidate remains unreviewed')
    equal(candidate, {'schemaVersion': 1,
        'state': 'UNREVIEWED_CRYPTO_OWNER355_PRODUCTION_PIN_CANDIDATES_V1',
        'variants': candidate['variants'], 'requiresIndependentReviewAndNewAdmissionRevision': True,
        'notAcceptedByReviewedClassicPinSelector': True, 'consumerPinsModified': False,
        'guestExecutedByExporter': False}, 'exact exporter wrapper')
    equal(list(candidate['variants']), LABELS, 'candidate variant order')
    equal(list(pins['variants']), LABELS, 'reviewed variant order')
    equal(list(review['variants']), LABELS, 'root review variant order')
    for label in LABELS[1:]:
        require(candidate['variants'][label] is None and pins['variants'][label] is None and review['variants'][label] is None,
                'other variant stays null: ' + label)
    original = candidate['variants']['normal-off']
    pin = pins['variants']['normal-off']
    require(original['state'] == 'unreviewed-crypto-owner355-freeze-pin-candidate' and original['reviewRequired'] is True,
            'original unreviewed variant')
    expected_pin = dict(original)
    expected_pin.update(state='reviewed-crypto-owner355-native-build-for-validation', reviewRequired=False,
        independentProofIndexPath=native_ref['index']['path'], independentProofIndexSha256=native_ref['index']['sha256'],
        independentProofResultPath=native_ref['result']['path'], independentProofResultSha256=native_ref['result']['sha256'])
    equal(pin, expected_pin, 'exact six-field per-variant derivation')
    require(pins['state'] == 'ROOT_REVIEWED_CRYPTO_OWNER355_VALIDATION_BOOTSTRAP_V2', 'reviewed wrapper state')
    equal(pins['candidateData'], root['candidateData'], 'wrapper original binding')
    equal(pins['independentNativeReview'], native_ref, 'wrapper native binding')
    equal(review['independentNativeReview'], native_ref, 'root review native binding')
    equal(review['candidateData'], root['candidateData'], 'root review original binding')
    equal(review['reviewedPinsSha256'], root['reviewedPins']['sha256'], 'reviewed pin root hash')
    for document in [pins, review]:
        require(document['sourceFiles'] == 355 and document['externalSources'] == 3, 'wrapper counts')
        equal(document['proposalIndexSha256'], SOURCE_SHA, 'wrapper source binding')
        require(document['runtimeAcceptanceClaim'] is False and document['operationalAdmission'] is False, 'closed wrapper scope')
    require(review['normalOnly'] is True, 'normal-only review')
    equal(review['state'], 'ROOT_REVIEWED_CRYPTO_OWNER355_BUILD_INPUTS_FOR_CODEC_VALIDATION_V2', 'root reviewed state')
    for field in ['recipeSha256', 'policySha256', 'helperSha256']:
        key = 'productionRecipeSha256' if field == 'recipeSha256' else field
        equal(review[field], contract[key], 'root review contract digest: ' + field)
        equal(native[field], contract[key], 'native contract digest: ' + field)
    expected_authority = {field: pin[field] for field in ['engineSha256', 'engineBytes', 'receiptSha256',
        'freezeReceiptSha256', 'independentProofIndexSha256', 'independentProofResultSha256']}
    equal(review['variants']['normal-off'], expected_authority, 'exact selected root variant tuple')
    freeze = data(pin['freezeReceiptPath'], pin['freezeReceiptSha256'])
    metadata_row = observed(Path(pin['enginePath'] + '.build.json'), pin['receiptSha256'])
    metadata = data(metadata_row['path'])
    engine_row = observed(pin['enginePath'], pin['engineSha256'], pin['engineBytes'])
    same_file_descriptor(engine_row, native['engine'], 'actual engine equals accepted native tuple')
    same_file_descriptor(metadata_row, native['metadata'], 'actual metadata equals accepted native tuple')
    same_file_descriptor(observed(pin['freezeReceiptPath']), native['freezeReceipt'], 'actual freeze equals accepted native tuple')
    require(freeze['state'] == 'immutable-crypto-owner-release-engine-frozen' and freeze['label'] == 'normal-off', 'freeze state')
    for field in ['engineSha256', 'engineBytes', 'receiptSha256', 'recipeSha256']:
        equal(pin[field], freeze[field], 'freeze pin field: ' + field)
    equal(pin['frozenFiles'], [{key: row[key] for key in ['path', 'sha256', 'bytes']} for row in freeze['copies']],
          'all frozen file rows preserved and ordered')
    require(len(pin['frozenFiles']) == 1390, 'frozen copies count')
    for row in pin['frozenFiles']:
        checked(row)
    equal(tree_files(FROZEN), sorted([str(Path(row['path']).relative_to(FROZEN)) for row in pin['frozenFiles']] +
        ['normal-off-freeze-receipt.json']), 'exact frozen output membership')
    for field in ['coreSources', 'runtimeBackendProof']:
        equal(pin[field], freeze[field], 'preserved freeze field: ' + field)
    equal(pin['runtimeBackendProof'], BACKEND, 'backend proof remains closed')
    equal(pin['coreSources'], freeze['coreSources'], 'core map exact')
    equal(pin['sourceRoot'], str(FROZEN / 'source'), 'frozen primitive root')
    equal(pin['componentizeSourceRoot'], str(FROZEN / 'componentize-source'), 'embedding primitive root')
    equal(metadata['sourceManifest'], policy['expectedNativeSourceManifest'], 'exact 355 metadata policy inventory')
    require(len(metadata['sourceManifest']) == 355 and len(metadata['componentizeSourceManifest']) == 3, 'native/external counts')
    for row in metadata['sourceManifest']:
        relative(row['path'])
        observed(STAGE / row['path'], row['sha256'])
        observed(FROZEN / 'source' / row['path'], row['sha256'])
    for row in metadata['componentizeSourceManifest']:
        observed(FROZEN / 'componentize-source' / relative(row['path']), row['sha256'])
    equal(metadata['cryptoKeyOwnershipPolicy'], policy['cryptoKeyOwnershipSourcePolicy'], 'ownership policy exact')
    equal(pin['cryptoKeyOwnershipPolicy'], metadata['cryptoKeyOwnershipPolicy'], 'pin ownership policy exact')
    require(metadata['cryptoKeyOwnershipBuildEvidence']['cryptoBuiltinEnabled'] is True, 'captured crypto build ON')
    require(metadata['gcStress'] is False and metadata['entropyPolicy'] == 'off', 'normal-off build settings')
    for field in ['classicStreamsEnabled', 'zlibEnabled', 'streamConsumersEnabled']:
        require(metadata[field] is True and pin[field] is True, 'enabled finite build flag ' + field)
    for field in ['gcStress', 'entropyPolicy', 'classicStreamsEnabled', 'zlibEnabled', 'streamConsumersEnabled',
                  'classicTraceSourcePolicy', 'zlibSourcePolicy', 'streamConsumersSourcePolicy',
                  'cmakeCacheSha256', 'compileCommandsSha256']:
        equal(pin[field], metadata[field], 'metadata pin field: ' + field)
    parent_policy_path = REPO / 'tests/node-compat/foundation-stream-consumers/native-integration-candidate-v2/policy.json'
    ownership = policy['cryptoKeyOwnershipSourcePolicy']
    parent_policy = data(parent_policy_path, ownership['parent355PolicySha256'])
    old_map = {row['path']: row['sha256'] for row in parent_policy['expectedNativeSourceManifest']}
    new_map = {row['path']: row['sha256'] for row in metadata['sourceManifest']}
    equal(sorted(old_map), sorted(new_map), 'native path set unchanged from parent355')
    changes = [path for path in sorted(new_map) if old_map[path] != new_map[path]]
    equal(changes, sorted(row['path'] for row in ownership['changes']), 'exact five changed native paths')
    require(len(changes) == 5 and len(new_map) - len(changes) == 350, '355 native delta sizes')
    for row in ownership['changes']:
        equal(old_map[row['path']], row['beforeSha256'], 'parent native replacement base')
        equal(new_map[row['path']], row['afterSha256'], 'new native replacement digest')
        observed(row['afterimage'], row['afterSha256'], row['bytes'])
    frame = data(root['completeReturnedFrameData']['path'])
    result = data(root['bootstrapResult']['path'])
    equal(frame['metadata'], metadata, 'full retained metadata exact')
    equal(frame['pin'], pin, 'full retained reviewed pin exact')
    for field, value in [('enginePath', pin['enginePath']), ('sourceRoot', pin['sourceRoot']),
                         ('configuredSourceRoot', str(STAGE)), ('variant', 'normal-off'),
                         ('validationBootstrapOnly', True), ('operationalAdmission', False)]:
        equal(frame[field], value, 'retained frame field: ' + field)
    require(canonical(frame['sourceRoot']) != canonical(frame['configuredSourceRoot']), 'physically distinct configured/frozen contexts')
    require(len(frame['selectedManifests']) == 11 and len(metadata['selectedModuleManifests']) == 11, 'selected manifest count')
    source_map = {row['path']: row['sha256'] for row in metadata['sourceManifest']}
    manifest_rows = []
    for declared, selected in zip(metadata['selectedModuleManifests'], frame['selectedManifests']):
        equal(source_map[declared['path']], declared['sha256'], 'selected manifest native binding')
        actual = data(FROZEN / 'source' / relative(declared['path']), declared['sha256'])
        equal(selected, actual, 'entire returned selected manifest')
        equal(actual['profileVersion'], declared['profileVersion'], 'selected profile')
        manifest_rows.append({'source': observed(FROZEN / 'source' / declared['path']),
            'profileVersion': actual['profileVersion'], 'moduleIds': list(actual['modules'])})
    module_ids = [item for row in manifest_rows for item in row['moduleIds']]
    for name in ['node:zlib', 'node:stream/consumers', 'node:stream', 'node:stream/promises']:
        require(name in module_ids, 'selected finite build module: ' + name)
    require('node:crypto' not in module_ids, 'no new node:crypto surface')
    equal(result['state'], 'ROOT_OBSERVED_GENUINE_CRYPTO_OWNER355_NORMAL_OFF_TWO_CONTEXT_JS_BOOTSTRAP_PASSED_V1', 'bootstrap result state')
    for field, value in [('reviewedPins', root['reviewedPins']), ('rootReview', root['rootReview']),
        ('frameData', root['completeReturnedFrameData']), ('variant', 'normal-off'),
        ('enginePath', pin['enginePath']), ('engineSha256', pin['engineSha256']), ('sourceFiles', 355),
        ('sourceRoot', pin['sourceRoot']), ('configuredSourceRoot', str(STAGE)), ('selectedManifests', 11),
        ('recheckPassed', True), ('readOnlyAdmissionHelpersInvoked', True),
        ('intermediatePythonHelperObjectsSeparatelyRetained', False),
        ('sourceControlFlowAndCleanFinalOutcomeSupportHelperRechecks', True),
        ('engineKeyCryptoGcComponentGuestHostOrTimingExecuted', False),
        ('runtimeAcceptanceClaim', False), ('operationalAdmission', False)]:
        equal(result[field], value, 'retained result field: ' + field)
    exports_expected = ['launch.py', 'started.json', 'stderr.log', 'stdout.log', 'terminal.json']
    boot_expected = ['bootstrap.mjs', 'frame-data.json', 'launch.py', 'result.json', 'started.json', 'stderr.log', 'stdout.log', 'terminal.json']
    equal(tree_files(EXPORT), exports_expected, 'finite exporter capture membership')
    equal(tree_files(BOOT), boot_expected, 'finite bootstrap capture membership')
    for root_dir, names in [(EXPORT, exports_expected), (BOOT, boot_expected)]:
        for name in names:
            observed(root_dir / name)
    exporter_terminal = data(root['actualPinExportTerminal']['path'])
    bootstrap_terminal = data(root['actualJsBootstrapTerminal']['path'])
    export_auth = data(root['pinExportAuthority']['path'])
    equal(export_auth['labels'], ['normal-off'], 'export authority only normal')
    equal(export_auth['output'], root['candidateData']['path'], 'export output authority')
    equal(export_auth['sourceIndexSha256'], SOURCE_SHA, 'export source authority')
    equal(export_auth['independentNativeReview'], native_ref, 'export native authority')
    for field in ['engineExecutionAllowed', 'reviewedPinsIssuedByExporter', 'runtimeAcceptanceClaim', 'operationalAdmission']:
        require(export_auth[field] is False, 'export false authority: ' + field)
    expected_argvs = [
        ['/usr/bin/python3', str(staged_base / 'artifact-tools/export-pin-candidate.py'), root['candidateData']['path'], 'normal-off'],
        ['/private/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node', str(BOOT / 'bootstrap.mjs')]]
    raw_statuses = []
    for directory, terminal, pid, argv, authority in [
        (EXPORT, exporter_terminal, 89088, expected_argvs[0], root['pinExportAuthority']),
        (BOOT, bootstrap_terminal, 91553, expected_argvs[1], root['rootReview'])]:
        equal(terminal['pid'], pid, 'actual retained PID')
        equal(terminal['argv'], argv, 'actual retained argv')
        require(type(terminal['rawExitCode']) is int and terminal['rawExitCode'] == 0, 'actual raw child exit0')
        require(terminal['timeout'] is False and terminal['deadlineSeconds'] == 900, 'no actual timeout')
        equal(terminal['authority'], authority, 'actual launch authority')
        checked(terminal['stdout']); checked(terminal['stderr'])
        require(terminal['stderr']['bytes'] == 0, 'empty actual stderr')
        started = data(directory / 'started.json')
        equal(started, {key: terminal[key] for key in ['pid', 'argv', 'startedAtUtc', 'authority', 'deadlineSeconds']}, 'started/terminal capture')
        raw_statuses.append({'terminal': observed(directory / 'terminal.json'), 'pid': pid, 'argv': argv,
            'rawExitCode': 0, 'timeout': False, 'stdout': terminal['stdout'], 'stderr': terminal['stderr'],
            'outerSessionIdDeclaredByRoot': root['pinExportSessionId' if directory == EXPORT else 'bootstrapSessionId'],
            'outerExecRawStatusSeparatelyRetained': False, 'ownedProcessGroupGoneProbeRetained': False,
            'elapsedSecondsIsOperationalBookkeepingOnly': True})
    equal(data(EXPORT / 'stdout.log'), {'output': root['candidateData']['path'],
        'state': candidate['state'], 'labels': ['normal-off'], 'admitted': False}, 'exact exporter stdout')
    equal(data(BOOT / 'stdout.log'), {'result': root['bootstrapResult'], 'frameData': root['completeReturnedFrameData'],
        'variant': 'normal-off', 'sourceFiles': 355, 'engineExecuted': False}, 'exact bootstrap stdout')
    node_row = observed(expected_argvs[1][0], 'e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0', 108619024)
    source_flow = {}
    for name in ['artifact-tools/bootstrap-preflight.mjs', 'artifact-tools/bootstrap-classifier.py',
                 'artifact-tools/bootstrap-contexts.mjs', 'artifact-tools/artifact_common.py',
                 'artifact-tools/metadata-admission.mjs', 'artifact-tools/export-pin-candidate.py',
                 'build-admission.mjs', 'artifact-tools/build-manifests.mjs']:
        source_flow[name] = {'source': observed(staged_base / name), 'readAsTextOnly': True}
        text(staged_base / name)
    bootstrap_text = text(BOOT / 'bootstrap.mjs')
    require('await cryptoOwnerBootstrapPreflight(' in bootstrap_text and 'await frame.recheck();' in bootstrap_text,
            'actual entry calls genuine bootstrap and returned recheck')
    require(bootstrap_text.index('await frame.recheck();') < bootstrap_text.index("state:'ROOT_OBSERVED_GENUINE_"),
            'final durable success requires awaited recheck')
    preflight_text = text(staged_base / 'artifact-tools/bootstrap-preflight.mjs')
    require('const actual=await execute();' in preflight_text and 'await recheck();' in preflight_text,
            'source initial execute and pre-return recheck')
    require("execFile" in preflight_text and "bootstrap-classifier.py" in preflight_text, 'read-only Python classification call')
    require(preflight_text.index('await own();') < preflight_text.index('const actual=await execute();'),
            'own authenticated source before classification')
    classifier_text = text(staged_base / 'artifact-tools/bootstrap-classifier.py')
    require(classifier_text.index("for row in index['files']") < classifier_text.index('spec.loader.exec_module(common)'),
            'complete source authentication before owner import')
    common_text = text(staged_base / 'artifact-tools/artifact_common.py')
    require('tool_dependencies(REPO)  # Authenticate every configured helper before any dynamic import.' in common_text,
            'full configured helper barrier retained')
    require("process=subprocess.run(command,check=True" in classifier_text and "admission=json.loads(process.stdout)" in classifier_text,
            'genuine metadata Node admission child source path')
    for launch_name in ['pinExportLaunchSource', 'bootstrapLaunchSource']:
        launch_text = text(root[launch_name]['path'])
        require("start_new_session=True" in launch_text and "child.wait(timeout=900)" in launch_text,
                'owned launch and finite deadline source')
        require("'PYTHONOPTIMIZE','PYTHONPATH','PYTHONHOME','NODE_OPTIONS','NODE_PATH'" in launch_text,
                'sanitized launch variables source')
        require("env['PYTHONDONTWRITEBYTECODE']='1'" in launch_text, 'no bytecode writes source')
    history = data(root['postReaderSyntaxHistory']['path'])
    equal(history['state'], 'ROOT_POST_BOOTSTRAP_READER_SYNTAX_PREPARATION_FAILURE', 'separate retained history')
    require(history['errorType'] == 'SyntaxError' and history['actualBootstrapRawExitCode'] == 0 and history['sourceOrArtifactsModified'] is False,
            'reader history is not native/bootstrap failure')
    descriptors = {
        'actualRootResults': observed(root_path), 'candidatePins': root['candidateData'],
        'reviewedPins': root['reviewedPins'], 'rootReview': root['rootReview'],
        'sourceIndex': observed(SOURCE / 'index.json'), 'configuredSourceIndex': observed(staged_base / 'index.json'),
        'independentSourceReviewIndex': observed(source_peer_dir / 'index.json'),
        'independentNativeReviewIndex': native_ref['index'], 'independentNativeReviewResult': native_ref['result'],
        'nativeReviewEngineOriginalSpelling': native['engine'], 'nativeReviewMetadataOriginalSpelling': native['metadata'],
        'nativeReviewFreezeReceiptOriginalSpelling': native['freezeReceipt'],
        'engine': engine_row, 'metadata': metadata_row, 'freezeReceipt': observed(pin['freezeReceiptPath']),
        'pinExportAuthority': root['pinExportAuthority'], 'pinExportTerminal': root['actualPinExportTerminal'],
        'bootstrapTerminal': root['actualJsBootstrapTerminal'], 'bootstrapEntrySource': root['bootstrapEntrySource'],
        'bootstrapResult': root['bootstrapResult'], 'frameData': root['completeReturnedFrameData'],
        'nodeBinary': node_row, 'postReaderSyntaxHistory': root['postReaderSyntaxHistory']}
    report = {
        'schemaVersion': 1, 'state': 'INDEPENDENT_CRYPTO_OWNER355_NORMAL_OFF_PIN_AND_JS_BOOTSTRAP_RESULTS_REVIEW_PASSED_V1',
        'verifiedPassed': True, 'variant': 'normal-off', 'normalOnly': True, 'descriptors': descriptors,
        'sourceIndexSha256': SOURCE_SHA, 'independentSourceReviewIndexSha256': SOURCE_PEER_SHA,
        'independentNativeReviewIndexSha256': NATIVE_SHA,
        'exactIndexedFamilies': index_reviews, 'nativePriorInputRowsRehashed': 8821,
        'sourcePeerInputRowsRehashed': 1711, 'sourcePreparationRowsRehashed': 1323,
        'configuredToolDependencyRowsRehashed': 922, 'frozenCopiesRehashed': 1390,
        'frozenActualRegularFiles': 1391, 'sourceFiles': 355, 'externalEmbeddingSources': 3,
        'unchangedParentNativePaths': 350, 'changedNativePaths': changes,
        'perVariantChangesExactly': ['state', 'reviewRequired', 'independentProofIndexPath',
            'independentProofIndexSha256', 'independentProofResultPath', 'independentProofResultSha256'],
        'topLevelReviewedWrapperAddedSeparately': True,
        'otherThreeVariantsRemainNull': True, 'unreviewedCandidatePreserved': True,
        'configuredSourceRoot': str(STAGE), 'frozenSourceRoot': pin['sourceRoot'],
        'contextsAreDistinct': True, 'contextApiFindingM1ResolvedInSource': True,
        'fullReturnedMetadataAndPinEqualAuthenticatedFiles': True,
        'selectedManifests': manifest_rows, 'rawStatuses': raw_statuses,
        'sourceFlow': source_flow,
        'observedGenuineJsBootstrapAndCallerRecheckPassed': True,
        'rootPythonExporterExecuted': True, 'rootNodeBootstrapExecuted': True,
        'rootReadOnlyAdmissionHelpersInvoked': True,
        'sourceRequiresThreeClassifierExecutionsBeforeFinalSuccess': True,
        'intermediatePythonAndMetadataAdmissionObjectsSeparatelyRetained': False,
        'internalHelperRechecksEvidence': 'Authenticated exact source control flow plus clean raw final outcome and retained complete frame/result; no separately retained internal helper objects.',
        'completeInheritedEnvironmentRetained': False, 'processGroupGoneProbeRetained': False,
        'environmentSourcePolicyOnly': 'Launchers filter NODE_COMPAT_/NAPI_RS_ and PYTHONOPTIMIZE/PYTHONPATH/PYTHONHOME/NODE_OPTIONS/NODE_PATH, set PYTHONDONTWRITEBYTECODE=1 and BINARYEN_CORES/RAYON_NUM_THREADS/CARGO_BUILD_JOBS=1; no exact full child-env capture.',
        'reviewerReadHashJsonDataOnly': True,
        'reviewerOwnerImportsHelpersNodeCliEngineKeyCryptoGcGuestOrHostActions': False,
        'rootTargetEngineKeyCryptoGcComponentGuestOrHostFixtureActions': False,
        'runtimeBackendProof': BACKEND, 'validationBootstrapOnly': True, 'readOnlyBootstrapOnly': True,
        'ordinaryOperationalAdmission': False, 'operationalAdmission': False, 'runtimeAcceptanceClaim': False,
        'componentBuildOrGuestExecutedByThisProof': False, 'keyBehaviorAccepted': False,
        'performanceClaim': False, 'timingAllowed': False, 'sourcePromotionAllowed': False,
        'futureComponentActionAuthority': None, 'futureKeyCryptoGcActionAuthority': None,
        'futureOperationalApproval': None, 'concreteBlockers': [],
        'limitations': [
            'Normal-OFF exact build-input pin derivation and actual read-only JS bootstrap only; no other native variant is configured.',
            'No engine execution, key/crypto behavior, finalizer, complete erasure, GC, component/guest fixture, runtime acceptance or ordinary admission follows.',
            'Prior native build/symbol/source evidence is retained and rehashed; no compiler, symbol tool, SDK parser or genuine artifact verifier was rerun.',
            'Root Node/Python read-only admission helpers ran. Reviewer only read/hashed/decoded JSON and inspected authenticated source as text.',
            'Three internal classifier executions are source-control-flow supported, not independently captured child terminal records.',
            'Only target child terminal codes are retained; no separate Root exec outer terminal or process-group-gone probe or full inherited environment is asserted.',
            'Retained post-reader SyntaxError is separate pre-I/O preparation history; actual bootstrap terminal remains raw0.'
        ]}
    write('reader-results.json', report)
    write('rehashed-inputs.json', [ledger[key] for key in sorted(ledger)])
    print(json.dumps({'state': report['state'], 'uniqueInputs': len(ledger), 'sourceFiles': 355,
                      'frozenCopies': 1390, 'selectedManifests': 11, 'blockers': []}))

if __name__ == '__main__':
    main()
