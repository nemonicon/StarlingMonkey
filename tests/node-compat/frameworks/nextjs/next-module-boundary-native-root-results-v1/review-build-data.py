"""Finite read-only actual build DATA audit. No target code/process is imported or invoked.
Writes only its new factual primary-lane review after all original files verify.
"""
from pathlib import Path
import json, hashlib, stat, os, posixpath

W = Path('/private/tmp/starling-node-compat/next-native-intl-build-guard825-first')
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


def clean(terminal):
    assert type(terminal['rawExitCode']) is int and terminal['rawExitCode'] == 0
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
assert result['passed'] is True and result['primaryError'] is None and result['postCollectionErrors'] == []
assert result['engineOrGuestExecuted'] is result['adoption'] is False
assert result['inputProtection'] == dict(files=1841, wholeTrees=10, unchanged=True, errors=[], currentBeforeFinalOnly=True)
assert obs['workerResult'] == desc(W / 'result.json') and obs['workerReportedPassed'] is obs['ownedCleanRawZero'] is True
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
checked(result['engineCandidate'])
assert md['engine'] == result['engineCandidate'] and result['metadata'] == desc(W / 'metadata.json')
with Path(md['engine']['path']).open('rb') as stream:
    assert stream.read(8) == b'\0asm\1\0\0\0'
for q in [obs['draft'], obs['launcher'], obs['issuedAuthority'], a['entry'], a['plan'], a['callerIndex']]:
    checked(q)
started, terminal = load(O / 'started.json'), load(O / 'terminal.json')
clean(terminal)
outer_owned = owned(O, terminal)
assert started['pid'] == terminal['pid'] == 96055 and started['timeoutSeconds'] == 7200
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
    assert row['argv'] == argv and type(row['rawExitCode']) is int and row['rawExitCode'] == row['outerRawExitCode'] == 0
    assert row['innerOwnedClean'] is row['ownedGone'] is True and row['timeout'] is row['forcedCleanup'] is False
    assert all(row[k] == [] for k in ['errors', 'signals', 'interruptedSignals', 'remainingObservedPids'])
    root = W / 'results' / row['label']
    packet, worker = load(root / 'packet.json'), load(root / 'worker-result.json')
    ps, pt = load(root / 'owned-monitor/started.json'), load(root / 'owned-monitor/terminal.json')
    clean(pt)
    count = owned(root / 'owned-monitor', pt)
    record_count += count
    assert packet['authority'] == ps['authority'] == pt['authority'] == desc(W / 'root-authority.json')
    assert packet['argv'] == worker['argv'] == row['argv'] and packet['cwd'] == str(W)
    assert packet['environment'] == env and packet['output'] == str(root)
    assert ps['pid'] == pt['pid'] and ps['timeoutSeconds'] == cap
    assert ps['argv'] == [a['wrapperPython']['path'], '-B', '-I', a['entry']['path'], '--worker-packet', str(root / 'packet.json')]
    assert worker['rawChildExitCode'] == worker['status'] == 0 and worker['stoppedForDiskSpace'] is False
    assert worker['stopReason'] is None and worker['sigtermReceived'] == 0 and worker['temporarySigtermHandlerRestored'] is True
    assert worker['childStarted'] is worker['lifecycleComplete'] is True and worker['launcherErrors'] == []
    assert 'resultWriteError' not in worker
    cleanup = worker['ownedGroupCleanup']
    assert cleanup['complete'] is True and cleanup['events'] == cleanup['errors'] == [] and cleanup['rawChildExitCode'] == 0
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
    phases.append(dict(label=row['label'], rawCommandExitCode=0, rawOuterExitCode=0, clean=True,
                       outerTerminal=desc(root / 'owned-monitor/terminal.json'), workerResult=desc(root / 'worker-result.json'),
                       rawCombinedLog=worker['rawCombinedLog'], observedOwnedRecords=count))
lines = [json.loads(x) for x in (O / 'stdout.log').read_text().splitlines() if x.strip()]
assert len(lines) == 7 and lines[:6] == phase_starts
assert lines[-1] == dict(result=desc(W / 'result.json'), passed=True, engine=result['engineCandidate'], metadata=result['metadata'])
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
assert len(unique) == 1841, ('protected count', len(unique))
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
assert len(treecounts) == 10 and sum(treecounts.values()) == 15766
for path, before_stat in alltreepaths:
    assert snap(path) == before_stat, ('tree changed', path)
for path, before_stat in stats.items():
    assert snap(path) == before_stat, ('input changed', path)
summary = dict(schemaVersion=1, state='ACTUAL_GUARDED_FULL_NATIVE_BUILD_PRIMARY_DATA_LANE_PASSED_V1', passed=True,
               scope='Original owner/phase lifecycle, exact1841 protected descriptor union, complete ten current tree inventories and physical read bookends; coordinated Source/TU/link lane separate.',
               actualResult=desc(W / 'result.json'), metadata=desc(W / 'metadata.json'), engine=result['engineCandidate'],
               actualRootObservation=desc(O / 'observation.json'), issuedAuthority=desc(O / 'authority.issued.json'),
               recipe=a['entry'], callerSourceIndex=a['callerIndex'],
               outerOwner=dict(pid=96055, timeoutSeconds=7200, rawExitCode=0, clean=True, observedOwnedRecords=outer_owned,
                               terminal=desc(O / 'terminal.json')),
               phases=phases, allSixPhaseAndOuterStartedTerminalAuthorityArgvRawStreamsAndOwnedRecordsVerified=True,
               ownedObservationRecordCount=record_count, rawAndSelectionRecordsHashedByPrimaryReviewer=len(cache),
               protectedFileDescriptorsChecked=len(unique), wholeTreesCurrentContentAndPhysicalRowsEqualCapturedBefore=True,
               currentTreeEntriesExcludingRoots=treecounts, wholeTreeEntryCount=sum(treecounts.values()),
               wholeTreeRegularFileBytesHashed=treebytes[0], allSelectedPhysicalReadBookendsUnchanged=True,
               environmentPolicy=desc(W / 'environment-policy.json'), requestedCMakeMatchesObserved=True,
               minimumPhaseSampledFreeBytes=min(minimum),
               diskScope='Source3GiB-start/1GiB-phase policy preserved; actual phase samples and boundaries, not continuous outer/zero-gap enforcement or measured peak.',
               sourceCounts=dict(native=435, support=387, embedding=3, copies=825, publicManifests=22, privateManifests=2),
               engineOrGuestExecuted=False, componentConstructed=False, importsOrGuestAbiVerified=False,
               runtimeAccepted=False, adoption=False, authorizesFutureAction=False,
               relationship='Reviewer authored predecessor runner/launcher/helper and reviewed guard Source; new materializer and guard authored elsewhere. Independent current DATA inspection, not independent shared-code authorship, observation of every execution step, or cryptographic process attestation.')
raw = (json.dumps(summary, indent=2) + '\n').encode()
target = R / 'actual-build-primary-lane.json'
fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
with os.fdopen(fd, 'wb') as stream:
    stream.write(raw)
    stream.flush()
    os.fsync(stream.fileno())
print('PRIMARY', json.dumps(dict(path=str(target), sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw))), flush=True)
print('COUNTS', len(cache), record_count, treebytes[0], flush=True)
