"""Finite read-only actual build DATA audit. No target code/process is imported or invoked.
Writes only its new factual primary-lane review after all original files verify.
"""
from pathlib import Path
import json, hashlib, stat, os, posixpath, re, shlex

W = Path('/private/tmp/starling-node-compat/next-native-intl-build-interop825-first')
O = Path(str(W) + '-root-monitor')
R = Path(__file__).resolve().parent
cache, stats = {}, {}


def snap(path):
    s = Path(path).lstat()
    return s.st_dev, s.st_ino, s.st_nlink, s.st_mode, s.st_size, s.st_mtime_ns, s.st_ctime_ns


def desc(path):
    path = Path(path)
    assert path.is_absolute() and '..' not in path.parts and not path.is_symlink() and path.is_file()
    for parent in path.parents:
        assert not parent.is_symlink()
    key, before = str(path), snap(path)
    if key in cache:
        assert stats[key] == before, ('changed', key)
        return cache[key]
    h, size = hashlib.sha256(), 0
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(4 * 1024**2), b''):
            h.update(block)
            size += len(block)
    assert snap(path) == before
    cache[key] = dict(path=key, sha256=h.hexdigest(), bytes=size)
    stats[key] = before
    return cache[key]


def checked(row):
    actual = desc(row['path'])
    assert all(actual[k] == row[k] for k in ['path', 'sha256', 'bytes']), row
    return actual


def load(path):
    desc(path)
    return json.loads(Path(path).read_bytes())


def family(row):
    checked(row)
    index = load(row['path'])
    root = Path(row['path']).parent
    expected = {x['path']: x for x in index['files']}
    assert len(expected) == len(index['files'])
    nodes = list(root.rglob('*'))
    assert all(not p.is_symlink() and (p.is_file() or p.is_dir()) for p in nodes)
    assert {p.relative_to(root).as_posix() for p in nodes if p.is_file()} == set(expected) | {'index.json'}
    return [checked(dict(path=str(root / name), sha256=q['sha256'], bytes=q['bytes']))
            for name, q in expected.items()]


def clean(terminal, expected=0):
    assert type(terminal['rawExitCode']) is int and terminal['rawExitCode'] == expected
    assert terminal['timeout'] is terminal['forcedCleanup'] is False
    assert terminal['parentOwnedGroupGone'] is terminal['allObservedOwnedGroupsGone'] is True
    assert all(terminal[k] == [] for k in ['errors', 'signals', 'interruptedSignals', 'remainingObservedPids'])
    assert all(q['alive'] is False and q['signalAllowed'] is False for q in terminal['finalGroups'])


def owned(root, terminal):
    rows = []
    for n, path in enumerate(sorted(root.glob('owned-*.json'))):
        row = load(path)
        assert row['sequence'] == n
        rows.append(row['process'])
    assert rows == terminal['observedProcesses']
    return len(rows)


result, md, obs = load(W / 'result.json'), load(W / 'metadata.json'), load(O / 'observation.json')
a = load(O / 'authority.issued.json')
spec = load(a['plan']['path'])
base = load(spec['basePlan']['path'])
sel = load(a['portableSelection']['path'])
generated, comp = load(a['installedGeneratorResult']['path']), load(a['composition']['path'])
cargo = md['portableCargoAdmission']
assert result['passed'] is False and result['state'] == 'EXPERIMENTAL_NEXT_INTL_NATIVE_BUILD_FAILED_UNACCEPTED_V1'
assert result['primaryError']['type'] == 'AssertionError' and result['primaryError']['message'] == 'build failed' and result['postCollectionErrors'] == []
assert result['engineOrGuestExecuted'] is result['adoption'] is False
protection_count = result['inputProtection']['files']
assert type(protection_count) is int and protection_count > 0
assert result['inputProtection'] == dict(files=protection_count, wholeTrees=10, unchanged=True, errors=[], currentBeforeFinalOnly=True)
assert obs['workerResult'] == desc(W / 'result.json') and obs['workerReportedPassed'] is obs['ownedCleanRawZero'] is False
assert obs['errors'] == [] and obs['originalInputProtection']['unchanged'] is True
assert obs['originalInputProtection']['errors'] == [] and obs['workerInputProtection'] == result['inputProtection']
assert obs['automaticRetry'] is obs['engineOrGuestExecuted'] is False
assert a['state'] == 'ROOT_EXPERIMENTAL_NEXT_INTL_NATIVE_BUILD_AUTHORITY_V1'
assert a['buildAllowed'] is a['configureAllowed'] is True
assert all(a[k] is False for k in ['engineOrGuestExecutionAllowed', 'freezeAllowed', 'networkAllowed', 'rustupAllowed'])
assert desc(W / 'root-authority.json') == dict(desc(O / 'authority.issued.json'), path=str(W / 'root-authority.json'))
assert md['rootAuthority'] == desc(W / 'root-authority.json') and md['recipe'] == a['entry']
assert md['sourceComposition'] == result['sourceComposition'] == a['composition']
assert md['metadataKind'] == 'EXPERIMENTAL_NEXT_INTL_NATIVE_BUILD_ACTUAL_V1'
assert md['engineExecuted'] is md['guestExecuted'] is md['old83MetadataProjected'] is md['adoption'] is False
assert result['engineCandidate'] is md['engine'] is None
assert result['metadata'] == desc(W / 'metadata.json')
assert md['actualSeparateEmbeddingCompileRows'] is None
assert not (W / 'componentize-source/lib/starlingmonkey_embedding.wasm').exists()
for q in [obs['draft'], obs['launcher'], obs['issuedAuthority'], a['entry'], a['plan'], a['callerIndex']]:
    checked(q)
started, terminal = load(O / 'started.json'), load(O / 'terminal.json')
clean(terminal, 1)
outer_owned = owned(O, terminal)
assert started['pid'] == terminal['pid'] == 28790 and started['timeoutSeconds'] == 7200
assert started['authority'] == terminal['authority'] == desc(O / 'authority.issued.json')
assert started['argv'] == [a['wrapperPython']['path'], '-B', '-I', a['entry']['path'], '--authority', str(O / 'authority.issued.json')]
for q in obs['rawFiles'].values():
    checked(q)
assert terminal['stdout'] == desc(O / 'stdout.log') and terminal['stderr'] == desc(O / 'stderr.log')
assert desc(O / 'stderr.log')['bytes'] == 0 and obs['terminal'] == desc(O / 'terminal.json')
envdoc = load(W / 'environment-policy.json')
env = envdoc['environment']
assert envdoc['HOMEInherited'] is envdoc['privateCargoHome'] is envdoc['offline'] is True
assert envdoc['rustupInvoked'] is False and env['HOME'] == '/Users/dan'
assert env['CARGO_HOME'] == str(W / 'cargo-home') and env['CARGO_TARGET_DIR'] == str(W / 'rust-target')
assert env['TMPDIR'] == str(W / 'tmp') and env['CARGO_NET_OFFLINE'] == 'true'
assert env['CARGO_NET_GIT_FETCH_WITH_CLI'] == 'false' and env['CARGO_BUILD_JOBS'] == '1'
assert env['RUSTC'] == a['rustc']['path'] and 'RUSTUP_HOME' not in env and 'RUSTUP_TOOLCHAIN' not in env
flags = md['requestedCMake']
assert all(md['observedCMake'][k]['value'] == v for k, v in flags.items())
assert flags['SPIDERMONKEY_INTL'] == flags['NODE_COMPAT_PREINSTALLED_RUST'] == flags['NODE_COMPAT_LOCKED_RUST'] == 'ON'
assert flags['Rust_RESOLVE_RUSTUP_TOOLCHAINS'] == 'OFF'
assert all(flags[k] == 'OFF' for k in ['NODE_COMPAT_GC_STRESS', 'NODE_COMPAT_OOM_TESTING', 'NODE_CRYPTO_AUDITED_BORROW', 'ENABLE_JS_DEBUGGER', 'WEVAL'])
phases, phase_starts, minimum = [], [], []
record_count = outer_owned
assert [q['label'] for q in result['phases']] == ['rust-version', 'cargo-version', 'rust-sysroot', 'configure', 'build', 'ninja-commands']
cmake = next(t['executable']['path'] for t in base['hostTools'] if t['name'] == 'cmake')
ninja = next(t['executable']['path'] for t in base['hostTools'] if t['name'] == 'ninja')
expected = [
    [a['rustc']['path'], '--version', '--verbose'], [a['cargo']['path'], '--version', '--verbose'],
    [a['rustc']['path'], '--print', 'sysroot'],
    [cmake, '-S', str(W / 'componentize-source'), '-B', str(W / 'build'), '-G', 'Ninja', *['-D' + k + '=' + v for k, v in flags.items()]],
    [cmake, '--build', str(W / 'build'), '--target', 'starlingmonkey_embedding', '--parallel', '1', '--', '-d', 'keeprsp'],
    [ninja, '-C', str(W / 'build'), '-t', 'commands'],
]
for row, argv, cap in zip(result['phases'], expected, [120, 120, 120, 2400, 7200, 120]):
    expected_code = 1 if row['label'] == 'build' else 0
    assert row['argv'] == argv and type(row['rawExitCode']) is int and row['rawExitCode'] == row['outerRawExitCode'] == expected_code
    assert row['innerOwnedClean'] is row['ownedGone'] is True and row['timeout'] is row['forcedCleanup'] is False
    assert all(row[k] == [] for k in ['errors', 'signals', 'interruptedSignals', 'remainingObservedPids'])
    root = W / 'results' / row['label']
    packet, worker = load(root / 'packet.json'), load(root / 'worker-result.json')
    ps, pt = load(root / 'owned-monitor/started.json'), load(root / 'owned-monitor/terminal.json')
    clean(pt, expected_code)
    count = owned(root / 'owned-monitor', pt)
    record_count += count
    assert packet['authority'] == ps['authority'] == pt['authority'] == desc(W / 'root-authority.json')
    assert packet['argv'] == worker['argv'] == row['argv'] and packet['cwd'] == str(W)
    assert packet['environment'] == env and packet['output'] == str(root)
    assert ps['pid'] == pt['pid'] and ps['timeoutSeconds'] == cap
    assert ps['argv'] == [a['wrapperPython']['path'], '-B', '-I', a['entry']['path'], '--worker-packet', str(root / 'packet.json')]
    assert worker['rawChildExitCode'] == worker['status'] == expected_code and worker['stoppedForDiskSpace'] is False
    assert worker['stopReason'] is None and worker['sigtermReceived'] == 0 and worker['temporarySigtermHandlerRestored'] is True
    assert worker['childStarted'] is worker['lifecycleComplete'] is True and worker['launcherErrors'] == []
    assert 'resultWriteError' not in worker
    cleanup = worker['ownedGroupCleanup']
    assert cleanup['complete'] is True and cleanup['events'] == cleanup['errors'] == [] and cleanup['rawChildExitCode'] == expected_code
    assert worker['rawCombinedLog'] == desc(root / 'command.combined.log')
    assert load(root / 'phase.json') == row
    assert checked(row['outerTerminal']) == desc(root / 'owned-monitor/terminal.json')
    assert checked(row['workerResult']) == desc(root / 'worker-result.json')
    for q in [pt['stdout'], pt['stderr']]:
        checked(q)
    assert pt['stderr']['bytes'] == 0 and json.loads((root / 'owned-monitor/stdout.log').read_text()) == worker
    assert worker['diskSamples'] and all(type(x['bytes']) is int and x['bytes'] >= 1073741824 for x in worker['diskSamples'])
    minimum += [x['bytes'] for x in worker['diskSamples']]
    phase_starts.append(dict(pid=ps['pid'], timeoutSeconds=cap))
    phases.append(dict(label=row['label'], rawCommandExitCode=expected_code, rawOuterExitCode=expected_code, clean=True,
                       outerTerminal=desc(root / 'owned-monitor/terminal.json'), workerResult=desc(root / 'worker-result.json'),
                       rawCombinedLog=worker['rawCombinedLog'], observedOwnedRecords=count))
lines = [json.loads(x) for x in (O / 'stdout.log').read_text().splitlines() if x.strip()]
assert len(lines) == 7 and lines[:6] == phase_starts
assert lines[-1] == dict(result=desc(W / 'result.json'), passed=False, engine=result['engineCandidate'], metadata=result['metadata'])
# Reconstruct the runner's exact protected union using its retained, authenticated inputs.
rows = [a[k] for k in ['entry', 'plan', 'callerIndex', 'wrapperPython', 'portableCargoSelection']]
rows += [spec[k] for k in ['baseRunner', 'basePlan', 'portableBaseMap', 'baseBuildResult']]
rows += [a[k] for k in ['composition', 'installedGeneratorResult', 'intlLockfile', 'offlineCargoConfig', 'spidermonkeyEvidence', 'savedFramePatchIndex', 'cargo', 'rustc', 'smLibrary', 'smSavedFrameHeader', 'smConfigHeader', 'smConfdefsHeader']]
rows += cargo['protectedInputs'] + [a['portableSelection']] + sel['protectedInputs'] + [a['generatorNode']]
rows += [generated['sourceIndex'], generated['rootAuthority'], generated['plan'], a['portableSelection']] + family(generated['sourceIndex'])
for q in generated['commands']:
    rows += [q[k] for k in ['started', 'terminal', 'stdout', 'stderr']]
rows += [generated[k] for k in ['bodyResult', 'outerStarted', 'outerTerminal', 'outerStdout', 'outerStderr']]
rows += [load(generated['plan']['path'])['python']]
rows += [dict(path=str(Path(comp['sourceRoot']) / q['path']), sha256=q['sha256'], bytes=q['bytes']) for q in comp['files']] + comp['inputs']
rows += [q['source'] for q in md['buildSupportInputManifest'] + md['embeddingInputManifest']]
rows += [base[k] for k in ['cbindgen', 'cpmModule', 'monitor', 'lifecycle']] + [q['executable'] for q in md['compilerTools']]
for tree in a['reusedTrees'].values():
    rows += [tree['inventory'], tree['provenance']]
    if 'archive' in tree:
        rows.append(tree['archive'])
old = load(spec['baseBuildResult']['path'])
rows.append(next(q['archive'] for q in old['archives'] if q['role'] == 'openssl'))
unique = {}
for q in rows:
    if q['path'] in unique:
        assert unique[q['path']] == q
    unique[q['path']] = q
assert len(unique) == protection_count, ('protected count', len(unique), protection_count)
for q in unique.values():
    checked(q)

before = load(md['initialTreeProtection']['path'])
checked(md['initialTreeProtection'])
treecounts, alltreepaths, treebytes = {}, [], [0]


def snapshot(root):
    root = Path(root)
    assert root.resolve(strict=True) == root and root.is_dir()
    s = root.stat()
    identity = dict(mode=stat.S_IMODE(s.st_mode), dev=s.st_dev, ino=s.st_ino, nlink=s.st_nlink, mtimeNs=s.st_mtime_ns)
    rows = []

    def walk(directory):
        for path in sorted(directory.iterdir()):
            s = path.lstat()
            row = dict(path=path.relative_to(root).as_posix(), mode=stat.S_IMODE(s.st_mode), dev=s.st_dev,
                       ino=s.st_ino, nlink=s.st_nlink, mtimeNs=s.st_mtime_ns)
            alltreepaths.append((str(path), snap(path)))
            if stat.S_ISLNK(s.st_mode):
                target = os.readlink(path)
                assert not Path(target).is_absolute()
                logical = posixpath.normpath(posixpath.join(path.parent.relative_to(root).as_posix(), target))
                assert logical != '..' and not logical.startswith('../')
                resolved = path.resolve(strict=True)
                assert resolved == root or root in resolved.parents
                row.update(kind='symlink', target=target)
            elif stat.S_ISDIR(s.st_mode):
                row['kind'] = 'directory'
            else:
                assert stat.S_ISREG(s.st_mode)
                d = desc(path)
                assert d['bytes'] == s.st_size
                row.update(kind='file', sha256=d['sha256'], bytes=d['bytes'])
                treebytes[0] += d['bytes']
            rows.append(row)
            if row['kind'] == 'directory':
                walk(path)
    walk(root)
    alltreepaths.append((str(root), snap(root)))
    return dict(root=str(root), rootIdentity=identity, entries=rows)


def content(tree):
    return dict(root=tree['root'], rootMode=tree['rootIdentity']['mode'],
                entries=[{k: v for k, v in row.items() if k not in ['dev', 'ino', 'nlink', 'mtimeNs']}
                         for row in tree['entries']])


for role, tree in a['reusedTrees'].items():
    current = snapshot(tree['root'])
    expected = load(tree['inventory']['path'])
    assert content(current) == content(expected), ('tree content', role)
    assert current == before[role], ('tree physical rows', role)
    treecounts[role] = len(current['entries'])
    print('TREE VERIFIED', role, treecounts[role], flush=True)
assert len(treecounts) == result['inputProtection']['wholeTrees'] == 10
for path, before_stat in alltreepaths:
    assert snap(path) == before_stat, ('tree changed', path)
for path, before_stat in stats.items():
    assert snap(path) == before_stat, ('input changed', path)

# Rehash every declared source/copy pair; this does not infer a completed compilation.
assert len(result['sourceCopies']) == 825
copy_modes = {}; copy_bytes = 0; target_paths = set()
for row in result['sourceCopies']:
    checked(row['source']); checked(row['target'])
    src, dst = Path(row['source']['path']), Path(row['target']['path'])
    ss, ds = src.stat(), dst.stat()
    assert ds.st_nlink == 1 and (ss.st_dev, ss.st_ino) != (ds.st_dev, ds.st_ino)
    assert stat.S_IMODE(ds.st_mode) == row['mode']
    assert row['singleLink'] is row['distinctInode'] is True
    assert row['source']['sha256'] == row['target']['sha256'] and row['source']['bytes'] == row['target']['bytes']
    assert str(dst) not in target_paths; target_paths.add(str(dst)); copy_bytes += ds.st_size
    mode = oct(row['mode']); copy_modes[mode] = copy_modes.get(mode, 0) + 1
assert (md['nativePolicyInputCount'], md['buildSupportInputCount'], md['embeddingInputCount']) == (435,387,3)
for row in result['sourceAfter']: checked(row)
assert len(result['sourceAfter']) == 435
for row in result['linkInputs']: checked(row)
assert md['linkAndRustInputs'] == result['linkInputs']
db = load(result['compileDatabase']['path'])
assert db == md['actualCompileRows'] and len(db) == 80
loader = W / 'native-source/runtime/script_loader.cpp'
assert desc(loader)['sha256'] == '25c19d29caf370104f40036df8d20633fdb64396c30f5993a5fe52315e619b28'
loader_rows = [q for q in db if q['file'] == str(loader)]; assert len(loader_rows) == 1
loader_args = shlex.split(loader_rows[0]['command'])
assert '-DNODE_COMPAT_MODULE=1' in loader_args and '-std=gnu++23' in loader_args
failed_object = Path(loader_args[loader_args.index('-o')+1]); failed_object = failed_object if failed_object.is_absolute() else Path(loader_rows[0]['directory'])/failed_object
assert not failed_object.exists()
log = (W / 'results/build/command.combined.log').read_text()
assert len(re.findall(r'^.*: error:',log,re.M)) == 1
assert "runtime/script_loader.cpp:324:35: error: no matching function for call to 'JS_ConcatStrings'" in log
assert 'JS_ConcatStrings(cx, tag, canonical_url.toString())' in log
assert 'String.h:313:32: note: candidate function not viable' in log
assert "cannot convert argument of incomplete type 'JSString *' to 'JS::Handle<JSString *>' for 3rd argument" in log
assert '1 error generated.' in log and 'ninja: build stopped: subcommand failed.' in log
assert '[113/120] Building CXX object' in log
sdk_header = Path(a['smLibrary']['path']).parent/'include/js/String.h'
header = sdk_header.read_text(); assert 'JS_ConcatStrings' in header
relevant = header[header.index('extern JS_PUBLIC_API JSString* JS_ConcatStrings'):][:300]
assert 'JS::Handle<JSString*> left' in relevant and 'JS::Handle<JSString*> right' in relevant
for path, before_stat in stats.items(): assert snap(path) == before_stat, ('final changed',path)
summary = dict(
 schemaVersion=1,state='ACTUAL_INTEROP_CPP_BUILD_FAILURE_DATA_REVIEW_PASSED_V1',
 verifiedDataConsistent=True, buildPassed=False, acceptedForConstruction=False,
 scope='Actual failed build and post-collection metadata; all six original phases and outer, derived protected union, ten whole current tree inventories/physical rows,825 source copies. Configured compile commands are not successful compile proof.',
 actualResult=desc(W/'result.json'),actualRootObservation=desc(O/'observation.json'),
 issuedAuthority=desc(O/'authority.issued.json'),callerSourceIndex=a['callerIndex'],recipe=a['entry'],
 metadata=desc(W/'metadata.json'),metadataRetainedButFailedAndUnaccepted=True,
 outerOwner=dict(pid=terminal['pid'],timeoutSeconds=7200,rawExitCode=1,ownedGroupsClean=True,terminal=desc(O/'terminal.json'),observedOwnedRecords=outer_owned),
 phases=phases,allSixPhaseAndOuterStartedTerminalAuthorityArgvRawStreamsAndOwnedRecordsVerified=True,
 ownedObservationRecordCount=record_count,primaryError=result['primaryError'],postCollectionErrors=[],
 compileFailure=dict(source=desc(loader),line=324,operation='JS_ConcatStrings',diagnostic='raw JSString* third argument requires JS::Handle<JSString*>',
   actualSdkDeclaration=desc(sdk_header),failedObjectAbsent=True,failedObject=str(failed_object),rawCombinedLog=desc(W/'results/build/command.combined.log'),ninjaProgressLabel='113/120'),
 protectedFileDescriptorsChecked=len(unique),protectedCountDerivedFromActualRunnerUnionAndResult=True,
 wholeTreesCurrentContentAndPhysicalRowsEqualCapturedBefore=True,currentTreeEntriesExcludingRoots=treecounts,
 wholeTreeEntryCount=sum(treecounts.values()),wholeTreeRegularFileBytesHashed=treebytes[0],
 allSelectedPhysicalReadBookendsUnchanged=True,
 copies=dict(count=825,modes=copy_modes,totalBytes=copy_bytes,sourceAndTargetHashBytesEqual=True,targetNlinkOne=True,sourceAndTargetInodesDistinct=True),
 manifests=dict(native=435,support=387,embedding=3),configuredCompileDatabaseRows=len(db),
 configuredRowsAreNotCompletedCompilationAttestation=True,separateEmbeddingCompileRows=None,
 availableWorkBuildArtifactDescriptorsRehashed=len(result['linkInputs']),availableArtifactBytes=sum(q['bytes']for q in result['linkInputs']),
 artifactInventoryDoesNotProveFinalLink=True,engineCandidate=None,engineArtifactExists=False,
 environmentPolicy=desc(W/'environment-policy.json'),requestedCMakeMatchesObserved=True,
 minimumPhaseSampledFreeBytes=min(minimum),diskScope='Unchanged3GiB start/1GiB phase policy, actual sampled/boundary observations only; no peak or zero-gap enforcement claim.',
 engineOrGuestExecuted=False,componentConstructed=False,runtimeAccepted=False,adoption=False,automaticRetry=False,authorizesFutureAction=False,
 relationship='Reviewer authored predecessor runner/helper/controller and the probe-source/guard-constructor plan; interop C++ prototype and current materializer authored elsewhere. Independent captured/current DATA inspection, not independent shared-code authorship or cryptographic process attestation.')
raw=(json.dumps(summary,indent=2)+'\n').encode(); target=R/'actual-build-failure-review.json'
fd=os.open(target,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
with os.fdopen(fd,'wb')as stream:stream.write(raw);stream.flush();os.fsync(stream.fileno())
print('REVIEW',json.dumps(dict(path=str(target),sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw))),flush=True)
