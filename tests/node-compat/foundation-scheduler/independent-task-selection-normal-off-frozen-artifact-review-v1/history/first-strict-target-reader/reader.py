"""Independent read/hash/JSON/static source audit only. No foreign code import."""
import ast
import hashlib
import json
import os
import shlex
import stat
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
S = HERE.parent
FREEZE = Path('/private/tmp/starling-node-compat/scheduler-resource-selection-v1-freeze')
SOURCE = Path('/private/tmp/starling-node-compat/scheduler-resource-selection-v1-source')
WORK = Path('/private/tmp/starling-node-compat/scheduler-resource-selection-v1-build')
ROOT = S / 'task-selection-normal-off-freeze-v2-root-results.json'
ROOT_SHA = '433311626e0d3b673cd503afdd5cd64199a3729cc9bbad0f2332f0b0a945ea00'
SOURCE_SHA = '88af5db1cb6bc98960eaa12dac7df2d8595602c47806a25f9ebc7c6ed04474f1'
FREEZER_SHA = '83c07efa19f56c0ad725212bf63dfac4b70ca1ed225b7737174e7357f15737e8'
ENGINE_SHA = 'f6a775f019ca48bb6b9a46a88364aa51a2691101a9e79325848afb5504c3034f'
META_SHA = '8219b7aaea6f5a311ccd9e2d038edcd213663078f9ff18917c155dfeb51dde4f'
RECEIPT_SHA = '42a81bc12bbd083dfb278bcd108bbbd4fba89b11436dc6d345221c69cec91641'
checks = 0
rows = {}
hash_cache = {}
families = []


def check(condition, label):
    global checks
    checks += 1
    if not condition:
        raise AssertionError(label)


def identity(s):
    return (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns, s.st_mode)


def take(descriptor, role):
    path = Path(descriptor['path'])
    check(path.is_absolute(), 'absolute original descriptor')
    st = path.lstat()
    check(stat.S_ISREG(st.st_mode), 'regular leaf: ' + str(path))
    key = identity(st)
    if key not in hash_cache:
        digest = hashlib.sha256()
        with path.open('rb') as f:
            for chunk in iter(lambda: f.read(4 * 1024 * 1024), b''):
                digest.update(chunk)
        check(identity(path.lstat()) == key, 'unchanged during read')
        hash_cache[key] = digest.hexdigest()
    sha = hash_cache[key]
    check(sha == descriptor['sha256'], 'actual hash: ' + str(path))
    if 'bytes' in descriptor:
        check(st.st_size == descriptor['bytes'], 'actual size: ' + str(path))
    canonical = str(path.resolve())
    out = rows.setdefault(canonical, dict(path=canonical, sha256=sha, bytes=st.st_size,
        declaredPaths=[], roles=[], identity=list(key), linkCount=st.st_nlink))
    check(out['sha256'] == sha and out['bytes'] == st.st_size, 'same physical source identity')
    for field, value in [('declaredPaths', str(path)), ('roles', role)]:
        if value not in out[field]:
            out[field].append(value)
    return dict(path=str(path), sha256=sha, bytes=st.st_size)


def newrow(path, role):
    path = Path(path)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    return take(dict(path=str(path), sha256=digest, bytes=path.stat().st_size), role)


def load(descriptor, role):
    row = take(descriptor, role)
    return json.loads(Path(row['path']).read_bytes())


def family(descriptor, role, exact=False):
    value = load(descriptor, role + ' index')
    root = Path(descriptor['path']).parent
    names = {'index.json'}
    for item in value['files']:
        relative = item['path']
        check(not Path(relative).is_absolute() and '..' not in Path(relative).parts and relative not in names, 'finite family row')
        names.add(relative)
        take(dict(item, path=str(root / relative)), role + ' member')
    actual = {str(p.relative_to(root)) for p in root.rglob('*') if p.is_file()}
    check(names <= actual, 'all indexed family members present')
    if exact:
        check(names == actual, 'exact live family membership')
    families.append(dict(index=descriptor, role=role, indexed=len(names) - 1,
                         unindexedPhysicalData=sorted(actual - names)))
    return value


def clean(terminal, pid, role):
    check(terminal['pid'] == pid and terminal['rawExitCode'] == 0, role + ' actual zero')
    for k in ('parentOwnedGroupGone', 'allObservedOwnedGroupsGone'):
        check(terminal[k] is True, role + ' ' + k)
    for k in ('timeout', 'forcedCleanup'):
        check(terminal[k] is False, role + ' ' + k)
    for k in ('interruptedSignals', 'remainingObservedPids', 'signals', 'errors'):
        check(terminal[k] == [], role + ' ' + k)
    for group in terminal['finalGroups']:
        check(group['alive'] is False and group['signalAllowed'] is False, role + ' final group')
    check(pid in {p['pid'] for p in terminal['observedProcesses']}, role + ' actual observed parent')
    for key in ('stdout', 'stderr'):
        take(terminal[key], role + ' full raw ' + key)


root = load(dict(path=str(ROOT), sha256=ROOT_SHA, bytes=6094), 'actual Root record')
check(root['rawRootOuterControllerExitCode'] == 0 and root['rootToolSession'] == 34677, 'Root tool observation scope')
family(root['sourceIndex'], 'actual freezer source', exact=True)
check(root['sourceIndex']['sha256'] == FREEZER_SHA, 'exact freezer source')
family(root['sourceReview']['index'], 'independent source peer', exact=True)
peer = load(root['sourceReview']['result'], 'independent source result')
check(peer['state'] == 'INDEPENDENT_SCHEDULER_TASK_SELECTION342_NORMAL_OFF_FREEZER_SOURCE_REVIEW_PASSED_V1', 'actual source-only peer state')
check(peer['freezerSourceIndexSha256'] == FREEZER_SHA and peer['taskSelectionSourceIndexSha256'] == SOURCE_SHA, 'source identities separate')
authority = load(root['rootAuthority'], 'actual freeze authority')
config = load(root['config'], 'actual freeze config')
check(config['rootAuthority'] == root['rootAuthority'] and config['freezerIndex'] == root['sourceIndex'], 'exact config/Root source roles')
check(authority['phase'] == 'freeze' and authority['variant'] == 'normal-off', 'freeze-only authority')
check(authority['externalParentDeadlineSeconds'] == 2400 and authority['rootOuterDeadlineSeconds'] == 3000, 'nested finite deadlines')
for key in ('buildAllowed', 'gcReconfigureAllowed', 'exportAllowed', 'bootstrapAllowed', 'componentAllowed', 'engineExecutionAllowed',
            'guestAllowed', 'keyOrCryptoAllowed', 'runtimeAcceptanceClaim', 'operationalAdmission', 'sourcePromotionAllowed', 'metadataProjectionAllowed', 'timingAllowed'):
    check(authority[key] is False, 'closed nonfreeze authority ' + key)
for key, path in [('configuredSourceRoot', SOURCE), ('workRoot', WORK), ('freezeRoot', FREEZE)]:
    check(authority[key] == str(path), 'exact actual context ' + key)
take(authority['rootOuterController'], 'actual Root controller source')
take(authority['rootOuterMonitor'], 'actual outer monitor source')
monitor_source = Path(authority['rootOuterMonitor']['path']).read_text()
check('<= 7200' in monitor_source and 'def monitor(' in monitor_source, 'genuine0af extended finite monitor API')
controller_source = Path(authority['rootOuterController']['path']).read_text()
check('monitor.monitor(argv, str(REPO)' in controller_source and 'OBSERVER, 3000' in controller_source, 'actual outer caller uses3000')

outer = load(root['outerTerminal'], 'actual outer terminal')
inner = load(root['innerTerminal'], 'actual inner terminal')
clean(outer, 69997, 'outer')
clean(inner, 70150, 'inner')
check(outer['authority'] == inner['authority'] == root['rootAuthority'], 'raw terminal authority identity')
for key in ('outerRawStdout', 'outerRawStderr', 'innerRawStdout', 'innerRawStderr'):
    take(root[key], 'actual full ' + key)
check(outer['stdout'] == root['outerRawStdout'] and inner['stdout'] == root['innerRawStdout'], 'full streams/terminals match')
outer_lines = [json.loads(line) for line in Path(root['outerRawStdout']['path']).read_text().splitlines()]
check(len(outer_lines) == 2, 'whole outer JSONL exactly2')
check(outer_lines[0] == {'pid': 70150, 'timeoutSeconds': 2400} and outer_lines[1] == inner, 'whole final outer record equals inner terminal')
capsule = json.loads(Path(root['innerRawStdout']['path']).read_bytes())
check(capsule == root['actualCapsule'], 'whole inner capsule exactly Root observation')
check(root['outerRawStderr']['bytes'] == root['innerRawStderr']['bytes'] == 0, 'complete empty raw stderrs')
outer_observation = load(root['outerObservation'], 'actual Root outer observation')
check(outer_observation['rawParentTerminal'] == root['outerTerminal'] and outer_observation['cleanOwnedCleanup'] is True, 'outer observation binds actual raw')

failure = load(root['priorOuterPreconditionFailure'], 'retained prior outer-only precondition failure')
check(failure['exitCode'] == 1 and failure['monitorCapSeconds'] == 2400 and failure['attemptedOuterDeadlineSeconds'] == 3000, 'original wrong monitor boundary retained')
check(failure['sourceFreezeParentStarted'] is False and failure['sourceCandidateChanged'] is False, 'no old freeze child/source mutation')
failure_stderr = Path(root['priorOuterPreconditionFailure']['path']).parent / 'raw-root-stderr.log'
newrow(failure_stderr, 'retained actual precondition raw traceback')
check('AssertionError' in failure_stderr.read_text() and 'monitor.py' in failure_stderr.read_text(), 'actual prior assertion source scope')

receipt = load(root['receipt'], 'actual freeze receipt')
check(root['receipt']['sha256'] == RECEIPT_SHA and receipt['variant'] == 'normal-off', 'exact receipt/variant')
check(receipt['nativeSourceIndexed']['sha256'] == SOURCE_SHA and receipt['freezerSourceIndexed'] == root['sourceIndex'], 'native/freezer source roles truthful')
check(receipt['rootAuthority'] == root['rootAuthority'] and receipt['sourceIndependentReview'] == root['sourceReview'], 'receipt active control roles')
check(receipt['engine'] == root['engine'] == capsule['engine'] and receipt['metadata'] == root['metadata'] == capsule['metadata'], 'all actual artifact descriptor relations')
check(root['engine']['sha256'] == ENGINE_SHA and root['metadata']['sha256'] == META_SHA, 'new selector engine/meta, no old substitution')
check(receipt['taskSelectionSourceIndexSha256'] == SOURCE_SHA and receipt['freezerSourceIndexSha256'] == FREEZER_SHA, 'receipt explicit source ids')
check(receipt['configuredSourceRoot'] == str(SOURCE) and receipt['workRoot'] == str(WORK), 'receipt configured/work contexts')
check(receipt['sourceRoot'] == str(FREEZE / 'source') and receipt['componentizeSourceRoot'] == str(FREEZE / 'componentize-source'), 'actual frozen contexts distinct')

copies = receipt['copies']
check(len(copies) == 762, 'observed762 actual copies')
check(sum(c['original'] is not None for c in copies) == 755, 'observed755 actual original references')
check(len({c['path'] for c in copies}) == 762, 'no duplicate copy destinations')
inode_set = set()
for c in copies:
    take(c, 'actual frozen ' + c['role'])
    p = Path(c['path'])
    check(p.is_relative_to(FREEZE), 'actual copy inside exact freeze root')
    st = p.lstat()
    check(stat.S_IMODE(st.st_mode) == 0o600 and st.st_nlink == 1 and st.st_uid == os.getuid(), 'actual private owned file')
    inode = (st.st_dev, st.st_ino)
    check(inode not in inode_set, 'no shared frozen inode')
    inode_set.add(inode)
    if c['original']:
        take(c['original'], 'actual preserved original ' + c['role'])
        original = Path(c['original']['path']).stat()
        check(inode != (original.st_dev, original.st_ino), 'copy distinct from actual original')
        check(c['sha256'] == c['original']['sha256'] and c['bytes'] == c['original']['bytes'], 'complete copy equals complete source bytes')
actual_files = set()
for p in [FREEZE, *FREEZE.rglob('*')]:
    st = p.lstat()
    check(not stat.S_ISLNK(st.st_mode), 'no frozen symlinks')
    if stat.S_ISDIR(st.st_mode):
        check(stat.S_IMODE(st.st_mode) == 0o700 and st.st_uid == os.getuid(), 'actual private owned directory')
    else:
        check(stat.S_ISREG(st.st_mode) and stat.S_IMODE(st.st_mode) == 0o600, 'only private regular frozen members')
        actual_files.add(str(p))
check(actual_files == {c['path'] for c in copies} | {root['receipt']['path']}, 'exact763 frozen physical members')
check(len(actual_files) == 763, 'actual763 count')
check(Path(root['receipt']['path']).stat().st_mtime_ns >= max(Path(c['path']).stat().st_mtime_ns for c in copies), 'receipt written after all captured copies')

own = Path(root['sourceIndex']['path']).parent
refs = load(newrow(own / 'references.json', 'actual pinned freezer references'), 'actual pinned freezer references')
plan = load(newrow(own / 'capture-plan.json', 'actual pinned copy plan'), 'actual pinned copy plan')
check(plan['baseCopies'] == 712 and len(plan['copies']) == 712, 'actual base copy plan712')
by_path = {c['path']: c for c in copies}
for item in plan['copies']:
    c = by_path[str(FREEZE / item['destination'])]
    check(c['original'] == item['source'] and c['role'] == item['role'], 'every actual base copy matches exact plan')
roles = Counter(c['role'] for c in copies)
check(roles['native-source342'] == 342 and roles['actual-external-embedding-source'] == 3, 'actual342+3 physical copies')
check(roles['actual-configured-nonnative-source-DATA'] == 224 and roles['actual-compiled-object-DATA'] == 68, 'actual native tooling/object provenance copies')
check(roles['selected-static-library'] == 29, 'actual29 static archives physically copied')
check(roles['new-selector-freezer-source-capsule'] == 28 and roles['new-freezer-source-review'] == 13, 'actual own source/peer capsules')
check(roles['fresh-source-admission-Ninja-or-control-data'] == 7, 'actual seven generated records')
for c in copies:
    if c['role'] == 'new-selector-freezer-source-capsule':
        check(Path(c['original']['path']).is_relative_to(own), 'own executable/source bytes original context')
    if c['role'] == 'new-freeze-config':
        check(c['original'] == root['config'], 'actual copied new Root config')
    if c['role'] == 'new-freeze-authority':
        check(c['original'] == root['rootAuthority'], 'actual copied new Root authority')

for frame in refs['families']:
    family(frame['index'], frame['role'])
for item in refs['files']:
    take(item, 'pinned reference source DATA')
for manifest in refs['preparationManifests']:
    data = load(manifest, 'original-context preparation manifest DATA')
    for item in data['files']:
        take(item, 'original-context preparation row; no rebasing')

ledger = load(receipt['verifiedBuildInputLedger'], 'complete actual20761 BUILD ledger32MiB DATA')
check(len(ledger['files']) == receipt['verifiedOriginalReferenceCount'] == 20761, 'all20761 original BUILD references')
for item in ledger['files']:
    take(item, 'actual complete BUILD original ledger')
    # The original reader retained identity/mode as well as content. Freeze is
    # read/copy-only and should not replace/reconfigure these inputs.
    check(list(identity(Path(item['path']).lstat())) == item['identity'], 'original BUILD identity/mode/mtime/ctime preserved')
print(json.dumps({'phase': 'actual-copy-and-full-build-ledger-passed', 'files': len(rows), 'checks': checks}), flush=True)

for key, count in [('actualStageResult', 566), ('oldResourceStage', 501)]:
    stage = load(refs[key], 'protected ' + key)
    check(len(stage['copies']) == count, 'exact protected stage count')
    for item in stage['copies']:
        actual = dict(item['original'], path=item['path'])
        take(actual, 'protected staged copy ' + key)
        take(item['original'], 'protected stage provenance ' + key)
old = load(refs['oldResourceFreeze'], 'protected old normal receipt')
check(len(old['copies']) == 666 and sum(c['original'] is not None for c in old['copies']) == 663, 'old666/663 protection')
for c in old['copies']:
    take(c, 'protected old normal frozen copy')
    if c['original']:
        take(c['original'], 'protected old normal original including cache/DB')
for alias in receipt['verifiedSdkAliases']:
    p = Path(alias['path'])
    check(p.is_symlink() and os.readlink(p) == alias['linkText'], 'exact declared SDK leaf alias')
    check(str(p.resolve()) == alias['resolvedPath'], 'exact SDK alias endpoint')
    check(alias in refs['sdkAliases'], 'alias not invented after action')
    check(alias['resolvedPath'] in rows, 'alias endpoint authenticated in full actual ledger')
check(len(receipt['verifiedSdkAliases']) == 31, 'all31 declared SDK aliases')
for pair in receipt['declaredArchiveHardlinks']:
    a, b = Path(pair['path']).stat(), Path(pair['target']).stat()
    check((a.st_dev, a.st_ino) == (b.st_dev, b.st_ino) and a.st_nlink == b.st_nlink == 2, 'one declared SM header hardlink preserved')

metadata = load(root['metadata'], 'actual frozen raw metadata')
build = load(refs['actualBuildReview']['result'], 'complete prior actual BUILD result retained by hash')
check(build['verifiedPassed'] is True and build['engineSha256'] == ENGINE_SHA and build['metadataSha256'] == META_SHA, 'exact inherited actual BUILD proof')
check(metadata['sourceManifest'] == build['fullActualSourceManifest'] and len(metadata['sourceManifest']) == 342, 'new342 full source manifest')
check(metadata['componentizeSourceManifest'] == build['fullActualExternalManifest'] and len(metadata['componentizeSourceManifest']) == 3, 'fresh actual external3 source manifest')
check(metadata['taskSelectionPolicy'] == receipt['taskSelectionPolicy'] == build['taskSelectionPolicy'], 'full new task-selection policy identity')
check(metadata['resourceOwnershipPolicy'] == receipt['resourceOwnershipPolicy'] == build['resourceOwnershipPolicy'], 'retained timer ownership policy identity')
check(metadata['selectedModuleManifests'] == build['selectedModuleManifests'] == refs['selectedManifests'], 'exact nine selected manifests')
check(metadata['engineSha256'] == ENGINE_SHA and metadata['enginePath'] == refs['engine']['path'], 'raw metadata preserves original configured engine path')
check(metadata['gcStress'] is False and metadata['oomTesting'] is False and metadata['debuggerEnabled'] is False, 'ordinary Release no stress/OOM/DEBUG')
check(metadata['entropyPolicy'] == 'off', 'actual raw lowercase off entropy policy')
for item in metadata['sourceManifest']:
    p = FREEZE / 'source' / item['path']
    take(dict(path=str(p), sha256=item['sha256']), 'frozen exact native342 source')
for item in metadata['componentizeSourceManifest']:
    p = FREEZE / 'componentize-source' / item['path']
    take(dict(path=str(p), sha256=item['sha256']), 'frozen actual external3 source')
for item in metadata['selectedModuleManifests']:
    value = load(dict(path=str(FREEZE / 'source' / item['path']), sha256=item['sha256']), 'frozen selected manifest')
    check(value['profileVersion'] == item['profileVersion'], 'manifest full selected version')

admission_rows = receipt['sourceAdmissionEvidence']
admission_terminal = load(admission_rows['terminal'], 'actual source admission raw terminal')
admission = load(admission_rows['stdout'], 'whole actual source admission JSON')
take(admission_rows['stderr'], 'whole actual source admission stderr')
embedding_rows = receipt['postBuildEmbeddingEvidence']
embedding_terminal = load(embedding_rows['terminal'], 'actual postbuild Ninja raw terminal')
take(embedding_rows['stdout'], 'whole actual postbuild Ninja raw stdout')
take(embedding_rows['stderr'], 'whole actual postbuild Ninja raw stderr')
for terminal, timeout, label in [(admission_terminal, 600, 'source-admission'), (embedding_terminal, 120, 'embedding-after')]:
    check(terminal['role'] == label and terminal['timeoutSeconds'] == timeout and terminal['rawExitCode'] == 0, 'actual helper role/deadline/zero')
    check(terminal['timedOut'] is False and terminal['errorType'] is None and terminal['capturedStreamsComplete'] is True, 'complete no-clipping helper capture')
    check(terminal['cwd'] == str(SOURCE), 'helper actual configured execution context')
    check(terminal['compilerExecuted'] is False and terminal['engineExecuted'] is False, 'read-only helper command scope')
    check(terminal['stderr']['bytes'] == 0, 'empty actual helper stderr')
check(admission_terminal['argv'] == [refs['python']['path'], '-B', '-I', str(own / 'entry.py'), 'admit', json.dumps(root['config'], separators=(',', ':'))], 'exact admission caller argv')
check(admission['metadata'] == refs['metadata'] and admission['sourceManifest'] == metadata['sourceManifest'], 'actual admission full raw metadata/source')
check(admission['externalSourceManifest'] == metadata['componentizeSourceManifest'] and admission['selectedManifestRows'] == metadata['selectedModuleManifests'], 'actual admission full external/manifests')
check(admission['selectedManifests'] == refs['selectedManifestValues'], 'all nine complete raw admitted manifest values')
check(admission['taskSelectionPolicy'] == metadata['taskSelectionPolicy'] and admission['resourceOwnershipPolicy'] == metadata['resourceOwnershipPolicy'], 'actual raw policy equality')
check(admission['configuredLayerRoot'] == str(SOURCE / 'tests/node-compat/foundation-scheduler/task-selection-integration-candidate-v1'), 'genuine actual staged model/layer context')
check(admission['metadataClassifier'] == dict(state='FINITE_RESOURCE_TASK_SELECTION342_METADATA_SHAPE_ONLY', nativeFiles=342, engineRead=False, runtimeAccepted=False, grantsAuthority=False), 'classifier source-only semantics not engine execution')
counts = dict(sourceFiles=342, externalSources=3, selectedManifestCount=9, compileDatabaseRows=67,
              policyCppCommands=61, otherConfiguredSourceRows=5, generatedNullCppRows=1,
              separateEmbeddingCommands=1, strictCommands=4, privateCommands=5)
for key, value in counts.items():
    check(admission[key] == value, 'actual raw admission count ' + key)
check(admission['engineHashedAsGuardData'] is True and admission['engineExecuted'] is False, 'engine hashed DATA, not classifier or runtime')

db = load(refs['compileCommands'], 'unchanged actual current67 compile database')
check(len(db) == 67 and len({r['file'] for r in db}) == 67, 'actual67 unique DB rows')
policy_cpp = [r for r in db if r['file'].startswith((str(SOURCE / 'builtins') + '/', str(SOURCE / 'runtime') + '/'))]
generated = [r for r in db if r['file'].endswith('/_starling_null.cpp') or r['file'].endswith('/null.cpp')]
check(len(policy_cpp) == 61, 'actual61 policy CPP rows')
check(len(generated) == 1 and generated[0]['file'] == str(Path(metadata['cmakeCachePath']).parent / 'starling-raw.wasm/null.cpp'), 'actual single generated null row')
other_configured = [r for r in db if r not in policy_cpp and r not in generated]
check(len(other_configured) == 5 and all(r['file'].startswith(str(SOURCE) + '/') for r in other_configured), 'actual other5 configured source rows')
all_tokens = {r['file']: shlex.split(r['command']) for r in db}
strict = [r['command'] for r in db if '-DNODE_COMPAT_STRICT_INITIALIZATION=1' in all_tokens[r['file']]]
private = [r['command'] for r in db if '-DNODE_COMPAT_CLASSIC_STREAMS=1' in all_tokens[r['file']]]
check(len(strict) == 4 and len(private) == 5, 'actual strict4/private5 flags')
check(set(strict) == set(metadata['strictEventExceptionPolicy']['actualNativeCompileCommands']), 'exact strict command metadata relation')
check(set(private) == set(metadata['classicStreamsPolicy']['actualPrivateTargetCompileCommands']), 'exact private command metadata relation')
for key in ('actualHostApiCompileCommands', 'actualEventLoopCompileCommands'):
    values = metadata['taskSelectionPolicy'][key]
    check(len(values) == 1 and values[0] in [r['command'] for r in db], 'actual selector ABI caller compiler evidence')
embedding_raw = Path(embedding_rows['stdout']['path']).read_text()
embedding_source = embedding_rows['sourcePath']
observed_embedding = [line for line in embedding_raw.splitlines() if ' -c ' in line and shlex.split(line)[-1] == embedding_source]
check(observed_embedding == metadata['actualEmbeddingCompileCommands'] == embedding_rows['commands'], 'raw postbuild command equals original separate embedding command')
check(len(observed_embedding) == 1, 'exact one separate embedding command')
tokens = shlex.split(observed_embedding[0])
check(not any(t.startswith('-flto') for t in tokens) and '-DNODE_COMPAT_STRICT_INITIALIZATION=1' in tokens, 'embedding no-LTO and strict macro')
check(embedding_terminal['argv'] == [refs['ninja']['path'], '-C', str(Path(metadata['cmakeCachePath']).parent), '-t', 'commands', 'builtin_componentize_embedding'], 'actual resolved pinned Ninja readonly argv')
check(embedding_terminal['argv'][0] == '/opt/homebrew/Cellar/ninja/1.13.2/bin/ninja', 'resolved real Ninja endpoint')
check(embedding_rows['beforeBuildCaptureExists'] is False, 'postbuild command not mislabelled prebuild')

control = load(receipt['freezerControl'], 'actual active freezer control provenance')
check(control['nativeSourceIndexed'] == receipt['nativeSourceIndexed'] and control['freezerSourceIndexed'] == receipt['freezerSourceIndexed'], 'honest native/freezer provenance')
check(control['rootAuthority'] == root['rootAuthority'] and control['sourceIndependentReview'] == root['sourceReview'], 'actual control Root/peer roles')
check(control['activeEntry'] == authority['entry'], 'actual active entry source bytes')
check(control['genuineAdmissionModel'] == refs['configuredModel'] and control['genuineAdmissionLayer'] == refs['configuredLayer'], 'actual model/layer source paths, no global rebinding')
for key in ('activeEntry', 'activeBody', 'genuineAdmissionModel', 'genuineAdmissionLayer'):
    take(control[key], 'actual active source ' + key)
for path in (own / 'entry.py', own / 'admission.py', own / 'freeze.py', own / 'verify.py', Path(control['genuineAdmissionModel']['path']), Path(control['genuineAdmissionLayer']['path']), Path(authority['rootOuterController']['path'])):
    ast.parse(path.read_text(), filename=str(path))
    check(True, 'static source Python grammar only')
for key in ('gcReconfigureAllowed', 'engineExecuted', 'bootstrapExecuted', 'componentOrGuestExecuted', 'operationalAdmission', 'runtimeAcceptanceClaim'):
    check(receipt[key] is False, 'no authority or runtime claim ' + key)
for key in ('nativeAllInvalidRuntimeValidation', 'resourceNativeRuntimeValidation', 'reviewedEnginePins'):
    check(receipt[key] is None, 'future runtime/pins null ' + key)

artifacts = dict(engine=root['engine'], metadata=root['metadata'], freezeReceipt=root['receipt'],
    rootObservation=dict(path=str(ROOT), sha256=ROOT_SHA, bytes=6094), rootAuthority=root['rootAuthority'],
    constructionConfig=root['config'], externalParentTerminal=root['outerTerminal'], ownedWorkerTerminal=root['innerTerminal'],
    externalParentStdout=root['outerRawStdout'], externalParentStderr=root['outerRawStderr'],
    ownedWorkerStdout=root['innerRawStdout'], ownedWorkerStderr=root['innerRawStderr'],
    freezerControl=receipt['freezerControl'], sourceAdmission=admission_rows['stdout'],
    sourceAdmissionTerminal=admission_rows['terminal'], embeddingCommands=embedding_rows['stdout'],
    embeddingTerminal=embedding_rows['terminal'])
coverage = dict(actualFrozenCopies=762, actualOriginalReferences=755, actualPhysicalFiles=763,
    completeBuildLedgerReferences=20761, currentStageCopies=566, protectedOldConfiguredCopies=501,
    protectedOldFrozenCopies=666, protectedOldOriginalReferences=663, nativeSourceFiles=342,
    unchangedResourceParentFiles=339, nativeReplacements=3, externalEmbeddingSources=3,
    selectedManifestCount=9, compileDatabaseRows=67, policyCppCommands=61, otherConfiguredSourceRows=5,
    generatedNullCppRows=1, separateEmbeddingCommands=1, strictCommands=4, privateCommands=5,
    staticLibrariesPhysicallyCopied=29, compiledObjectsPhysicallyCopied=68, sdkAliases=31,
    declaredSmHeaderHardlinks=1, outerJsonlRecords=2, helperRawCaptures=2)
result = dict(schemaVersion=1, state='INDEPENDENT_SCHEDULER_TASK_SELECTION342_NORMAL_OFF_FROZEN_ARTIFACT_REVIEW_PASSED_V1',
    verifiedPassed=True, taskSelectionSourceIndexSha256=SOURCE_SHA, freezerSourceIndexSha256=FREEZER_SHA,
    variant='normal-off', nativeSourceFiles=342, externalEmbeddingSources=3, selectedManifestCount=9,
    engineSha256=ENGINE_SHA, metadataSha256=META_SHA, configuredSourceRoot=str(SOURCE), workRoot=str(WORK),
    frozenRoot=str(FREEZE), sourceRoot=receipt['sourceRoot'], componentizeSourceRoot=receipt['componentizeSourceRoot'],
    engine=root['engine'], metadata=root['metadata'], freezeReceipt=root['receipt'], rootObservation=artifacts['rootObservation'],
    externalParentTerminal=root['outerTerminal'], ownedWorkerTerminal=root['innerTerminal'], rootAuthority=root['rootAuthority'],
    config=root['config'], nativeSourceIndexed=receipt['nativeSourceIndexed'], freezerSourceIndexed=receipt['freezerSourceIndexed'],
    sourceIndependentReview=root['sourceReview'], actualBuildReview=receipt['actualBuildReview'], artifacts=artifacts,
    coverage=coverage, copyRoles=dict(roles), checks=checks, physicalInputPathsRead=len(rows),
    rawExternalParentExitCode=0, rawOwnedWorkerExitCode=0, allObservedOwnedGroupsGone=True,
    wholeFinalOuterRecordEqualsInnerTerminal=True, rawMetadataBytesUnchanged=True,
    completeInputLedgerAndOriginalProtectionRehashed=True, sdkAliasesExplicit=True,
    rawAdmissionAndNinjaRetainedBeforeAssertions=True, genuineModelLayerSourceAndContextsVerified=True,
    inheritedBuildProofRehashed=True, noNewCompilerOrLinkProofClaim=True,
    rootV1OuterOnlyFailurePreserved=True, rootV2DifferentOuterMonitorWithoutSourceMutation=True,
    frozenOnlyVerifierExecutedByActualSource=True, frozenOnlyVerifierExecutedByReader=False,
    verifierCausalityScope='Authenticated freeze.py calls its own saved verify.py before successful return; no independently repeated verifier API call.',
    durabilityScope='Actual complete files/modes/inodes/membership and receipt-last timestamps; fsync ordering supported by authenticated code/control flow and successful return, not a crash/recovery experiment.',
    rootToolExitScope='Root-reported outer tool exit0; independently read raw monitor terminals and complete streams; no original tool API response recaptured by this reader.',
    engineExecuted=False, guestExecuted=False, nativeAllInvalidRuntimeValidation=None,
    resourceNativeRuntimeValidation=None, reviewedEnginePins=None, bootstrapFrame=None,
    gcReconfigureAllowed=False, operationalAdmission=False, runtimeAcceptanceClaim=False,
    sourcePromotionAllowed=False, grantsAnyActionAuthority=False,
    ownerHelpersModelsLayersMonitorsVerifiersForeignToolsOrRuntimeActionsInvoked=False)
(HERE / 'results.json').write_text(json.dumps(result, indent=2) + '\n')
contract = dict(schemaVersion=1, state='BOUNDED_SELECTOR342_NORMAL_OFF_FROZEN_ARTIFACT_RESULT_CONTRACT_V1',
    requiredResultState=result['state'], requiredFixedValues={k: result[k] for k in ('schemaVersion','verifiedPassed','taskSelectionSourceIndexSha256','freezerSourceIndexSha256','variant','nativeSourceFiles','externalEmbeddingSources','selectedManifestCount','engineSha256','metadataSha256','engineExecuted','guestExecuted','gcReconfigureAllowed','operationalAdmission','runtimeAcceptanceClaim','grantsAnyActionAuthority')},
    artifacts=artifacts, requiredExactDescriptors=artifacts, requiredCoverage=coverage,
    newPinToolingSource=None, rootExportAuthority=None, reviewedPins=None, bootstrap=None, runtime=None)
(HERE / 'result-contract.json').write_text(json.dumps(contract, indent=2) + '\n')
(HERE / 'input-hashes.json').write_text(json.dumps(dict(schemaVersion=1, files=sorted(rows.values(), key=lambda r:r['path']),
    aliasesDeclaredSeparately=receipt['verifiedSdkAliases'], noOwnerActions=True), indent=2) + '\n')
(HERE / 'family-audit.json').write_text(json.dumps(dict(schemaVersion=1, families=families, noForeignModulesImported=True), indent=2) + '\n')
(HERE / 'raw-and-source-audit.json').write_text(json.dumps(dict(schemaVersion=1, outer=outer, inner=inner,
    completeOuterRecords=outer_lines, actualAdmission=admission, actualAdmissionTerminal=admission_terminal,
    actualEmbeddingTerminal=embedding_terminal, actualEmbeddingCommands=observed_embedding,
    actualControl=control, retainedPriorFailure=failure, staticPythonAstOnly=True), indent=2) + '\n')
print(json.dumps(dict(state=result['state'], checks=checks, physicalInputPathsRead=len(rows),
    frozenCopies=762, originalReferences=755, physicalFrozenFiles=763,
    noForeignHelpersOrRuntimeActions=True)), flush=True)
