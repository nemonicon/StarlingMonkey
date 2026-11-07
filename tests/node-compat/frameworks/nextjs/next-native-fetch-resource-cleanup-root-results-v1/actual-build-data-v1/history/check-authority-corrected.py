"""Read retained full-native build DATA only; no producer, compiler or engine imports."""
import argparse
from collections import Counter
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import re
import shlex
import stat
import tarfile
import tomllib
import zlib

HERE = Path(__file__).resolve().parent
MAX_MEMBERS = 2500
MAX_BYTES = 32 * 1024**2
MAX_ARCHIVE = 8 * 1024**2
RESULT_SHA = 'ece47f14ab3a867830e4e0ccb7e1e146e4d3fa3f40980b05ee786da20539f3d7'
METADATA_SHA = '22f1d4561b73ce58b194afd5614368d30b16fc90f8fc7d63fe5c413916711b48'
ENGINE_SHA = '476b1c1d7a5f8b37d2c40d17510a98dd45676994b894663d445ae2f519cc33f6'
ROLE_COUNTS = {'native-policy-source': 435, 'build-support': 387, 'componentize-embedding': 3}
LABELS = ['rust-version', 'cargo-version', 'rust-sysroot', 'configure', 'build', 'ninja-commands']


def need(value, message):
    if value is not True:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def pairs(items):
    d = {}
    for key, value in items:
        need(key not in d, 'duplicate JSON key')
        d[key] = value
    return d


def obj(data):
    return json.loads(data, object_pairs_hook=pairs,
                      parse_constant=lambda _: (_ for _ in ()).throw(ValueError('nonfinite JSON')))


def physical(path):
    s = path.lstat()
    return [s.st_dev, s.st_ino, s.st_mode, s.st_nlink, s.st_size, s.st_mtime_ns, s.st_ctime_ns]


def ref_shape(value):
    need(type(value) is dict and set(value) == {'path', 'sha256', 'bytes'}, 'plain descriptor')
    need(type(value['path']) is str and value['path'].startswith('/'), 'absolute original path')
    need(type(value['bytes']) is int and value['bytes'] >= 0, 'integer descriptor length')
    need(type(value['sha256']) is str and re.fullmatch('[0-9a-f]{64}', value['sha256']) is not None, 'descriptor SHA')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--draft', action='store_true', help='Explicitly read an unsealed draft packet.')
    parser.add_argument('--current', action='store_true', help='Compare only retained original text files and selected monitor namespaces.')
    args = parser.parse_args()
    local_before = {}

    def local(name, cap):
        path = HERE / name
        need(path.resolve() == path and not path.is_symlink(), 'canonical local packet file')
        before = physical(path)
        need(stat.S_ISREG(before[2]) and before[3] == 1 and before[4] <= cap, 'bounded ordinary packet file')
        data = path.read_bytes()
        need(physical(path) == before, 'local immediate bookend')
        local_before[path] = before
        return data

    sealed = (HERE / 'index.json').exists()
    if sealed:
        final = obj(local('index.json', 64 * 1024))
        listed = final['files']
        need(len({x['path'] for x in listed}) == len(listed), 'unique final membership')
        for item in listed:
            name = item['path']
            need(type(name) is str and PurePosixPath(name).as_posix() == name and not name.startswith('/') and '..' not in PurePosixPath(name).parts, 'confined final filename')
            data = local(name, MAX_BYTES)
            need(sha(data) == item['sha256'] and len(data) == item['bytes'], 'final payload SHA/length')
        actual = sorted(p.relative_to(HERE).as_posix() for p in HERE.rglob('*') if p.is_file())
        need(actual == sorted(['index.json'] + [x['path'] for x in listed]), 'closed final files')
        need(all(not p.is_symlink() for p in HERE.rglob('*')), 'no final symlink')
    else:
        need(args.draft, 'unsealed packet requires --draft')
    index = obj(local('payload-index.json', 2 * 1024**2))
    data = local('data.tar.gz', MAX_ARCHIVE)
    need(index['archive'] == dict(path='data.tar.gz', sha256=sha(data), bytes=len(data)), 'archive descriptor')
    need(index['limits'] == dict(members=MAX_MEMBERS, expandedBytes=MAX_BYTES, archiveBytes=MAX_ARCHIVE), 'fixed packet limits')
    rows = index['members']
    need(type(index['memberCount']) is int and index['memberCount'] == len(rows) <= MAX_MEMBERS, 'member cap/count')
    need(type(index['expandedBytes']) is int and index['expandedBytes'] == sum(r['original']['bytes'] for r in rows) <= MAX_BYTES, 'expanded byte cap/count')
    by_member, by_path = {}, {}
    for row in rows:
        ref_shape(row['original'])
        name = row['member']
        need(type(name) is str and PurePosixPath(name).as_posix() == name and not name.startswith('/') and '..' not in PurePosixPath(name).parts, 'confined member name')
        need(name not in by_member and row['original']['path'] not in by_path, 'unique member/original')
        need(type(row['mode']) is int and row['mode'] in [0o600, 0o644, 0o755], 'ordinary retained file mode')
        before = row['physicalBefore']
        need(len(before) == 7 and all(type(n) is int for n in before) and stat.S_ISREG(before[2]) and before[3] == 1 and before[4] == row['original']['bytes'] and stat.S_IMODE(before[2]) == row['mode'], 'recorded original physical shape')
        by_member[name], by_path[row['original']['path']] = row, row
    # Bounded single gzip member: reject concatenation, unused/trailing input and truncation.
    dec = zlib.decompressobj(31)
    raw = dec.decompress(data, MAX_BYTES + MAX_MEMBERS * 1024 + 10240 + 1)
    need(dec.eof and not dec.unused_data and not dec.unconsumed_tail, 'one complete gzip member without trailing bytes')
    need(len(raw) <= MAX_BYTES + MAX_MEMBERS * 1024 + 10240, 'bounded TAR framing')
    payload, offset = {}, 0
    while offset + 512 <= len(raw) and raw[offset:offset + 512] != bytes(512):
        header = raw[offset:offset + 512]
        info = tarfile.TarInfo.frombuf(header, 'utf-8', 'strict')
        need(info.type == tarfile.REGTYPE and info.name in by_member and info.name not in payload, 'ordinary unique declared TAR member')
        need(not info.linkname and not info.pax_headers and info.uid == info.gid == info.mtime == 0, 'plain deterministic TAR header')
        row = by_member[info.name]
        need(info.size == row['original']['bytes'] and info.mode == row['mode'], 'TAR size/mode')
        start, end = offset + 512, offset + 512 + info.size
        need(end <= len(raw), 'complete TAR body')
        body = raw[start:end]
        need(sha(body) == row['original']['sha256'], 'member SHA')
        body.decode('utf-8')
        need(b'\0' not in body, 'text-only payload')
        payload[info.name] = body
        offset = start + ((info.size + 511) // 512) * 512
        need(raw[end:offset] == bytes(offset - end), 'zero body padding')
    need(set(payload) == set(by_member), 'complete TAR set')
    need(len(raw) % 512 == 0 and len(raw) - offset >= 1024 and raw[offset:] == bytes(len(raw) - offset), 'two EOF blocks and only zero TAR trailer')
    need(all(index[k] is False for k in ['binariesRetained', 'sourcePayload825Retained', 'actorOrProducerInvoked']) and index['allSelectedReadBookendsUnchanged'] is True, 'retention scope')
    current = {}
    if args.current:
        for row in rows:
            path = Path(row['original']['path'])
            need(path.resolve() == path and all(not p.is_symlink() for p in [path, *path.parents]), 'canonical selected current original')
            before = physical(path)
            need(stat.S_ISREG(before[2]) and before[3] == 1 and stat.S_IMODE(before[2]) == row['mode'], 'current regular/mode')
            need(path.read_bytes() == payload[row['member']] and physical(path) == before, 'current selected bytes/read bookend')
            current[path] = before
        for selected in index['selectedTrees']:
            root = Path(selected['root'])
            nodes = [root, *sorted(root.rglob('*'))]
            need(all(not p.is_symlink() for p in nodes), 'current selected namespace symlink refusal')
            need([(p.relative_to(root).as_posix(), 'file' if p.is_file() else 'directory') for p in nodes[1:]] == [tuple(x) for x in selected['entries']], 'complete current selected namespace')
            for path in nodes:
                if path.is_dir():
                    current[path] = physical(path)

    def role(name):
        return obj(payload[index['roles'][name]])

    def role_ref(name):
        return by_member[index['roles'][name]]['original']

    def ref(value):
        ref_shape(value)
        need(value['path'] in by_path and by_path[value['path']]['original'] == value, 'retained descriptor join: ' + value['path'])
        return payload[by_path[value['path']]['member']]

    def path_ref(path):
        need(str(path) in by_path, 'retained literal path: ' + str(path))
        return by_path[str(path)]['original']

    def read_path(path):
        return obj(ref(path_ref(path)))

    def zero(value, message):
        need(type(value) is int and value == 0, message)

    owner_records = 0

    def owner(tref, cap, argv, aref):
        nonlocal owner_records
        terminal = obj(ref(tref))
        root = Path(tref['path']).parent
        start = read_path(root / 'started.json')
        zero(terminal['rawExitCode'], 'original owner raw0')
        need(type(terminal['pid']) is int and terminal['pid'] > 0 and start['pid'] == terminal['pid'], 'owner PID')
        need(start['authority'] == terminal['authority'] == aref and start['argv'] == argv, 'original authority/argv')
        need(type(start['timeoutSeconds']) is int and start['timeoutSeconds'] == cap, 'original deadline')
        need(terminal['timeout'] is terminal['forcedCleanup'] is False, 'no timeout/forced cleanup')
        need(terminal['parentOwnedGroupGone'] is terminal['allObservedOwnedGroupsGone'] is True, 'owned groups gone')
        need(all(terminal[k] == [] for k in ['errors', 'signals', 'interruptedSignals', 'remainingObservedPids']), 'clean original owner arrays')
        need(len(terminal['finalGroups']) > 0 and all(g['alive'] is g['signalAllowed'] is False for g in terminal['finalGroups']), 'original final groups all gone')
        ref(terminal['authority']); ref(terminal['stdout']); ref(terminal['stderr'])
        observations = sorted((r for p, r in by_path.items() if Path(p).parent == root and re.fullmatch(r'owned-[0-9]+\.json', Path(p).name)), key=lambda r: r['original']['path'])
        captures = [obj(payload[r['member']]) for r in observations]
        need(len(captures) > 0 and [v['sequence'] for v in captures] == list(range(len(captures))), 'all original owned sequences')
        need([v['process'] for v in captures] == terminal['observedProcesses'], 'owned records/terminal complete equality')
        owner_records += len(captures)
        return terminal

    result, metadata, authority = role('result'), role('metadata'), role('root-authority')
    review, sr, owner_review = role('root-actual-build-review'), role('root-actual-build-source-review'), role('root-actual-build-owner-review')
    observation, plan = role('outer-observation'), obj(ref(authority['plan']))
    need(role_ref('result')['sha256'] == RESULT_SHA and role_ref('metadata')['sha256'] == METADATA_SHA, 'fixed genuine full-build cohort')
    need(result['passed'] is result['buildCommandSucceeded'] is True and result['primaryError'] is None and result['postCollectionErrors'] == [], 'actual full native result')
    need(ref(result['metadata']) == ref(role_ref('metadata')), 'complete metadata bytes')
    for data_review in [review, sr, owner_review]:
        need(data_review['verifiedPassed'] is True and data_review['actualResult'] == role_ref('result') and data_review['metadata'] == role_ref('metadata'), 'accepted review actual role joins')
        need(data_review['callerSourceIndex'] == authority['callerIndex'] and data_review['plan'] == authority['plan'] and data_review['engine'] == metadata['engine'], 'review Source/plan/engine joins')
    need(review['coordinatedSourceReview'] == role_ref('root-actual-build-source-review') and review['primaryLaneReview'] == role_ref('root-actual-build-owner-review'), 'coordinated review refs')
    need(review['actualRootObservation'] == role_ref('outer-observation'), 'review original outer observation')
    work = Path(authority['workRoot'])
    need(work == Path(role_ref('result')['path']).parent and str(work).endswith('/next-native-intl-build-fetch-cleanup825-first'), 'selected completed WORK')
    need(metadata['rootAuthority'] == role_ref('root-authority') and ref(observation['issuedAuthority']) == ref(metadata['rootAuthority']), 'actual authority bytes')
    need(observation['workerResult'] == role_ref('result') and observation['workRoot'] == str(work) and observation['portableCargoSelection'] == authority['portableCargoSelection'], 'Root result/source roles')
    need(observation['ownedCleanRawZero'] is observation['workerReportedPassed'] is observation['completedUnreviewed'] is True and observation['errors'] == [], 'original Root observation success')
    zero(observation['rawExitCode'], 'Root raw0')
    need(observation['automaticRetry'] is observation['engineOrGuestExecuted'] is False, 'Root no retry/execution')
    need(observation['originalInputProtection']['unchanged'] is True and observation['originalInputProtection']['errors'] == [], 'Root final input protection report')
    need(observation['workerInputProtection'] == result['inputProtection'], 'Root worker protection equality')
    for value in observation['rawFiles'].values():
        ref(value)
    need(authority['configureAllowed'] is authority['buildAllowed'] is True, 'issued native-only scope')
    need(all(authority[k] is False for k in ['engineOrGuestExecutionAllowed', 'freezeAllowed', 'networkAllowed', 'rustupAllowed']), 'forbidden scopes')
    draft = role('root-authority.unissued')
    need(draft['configureAllowed'] is draft['buildAllowed'] is None and type(draft['preparationOnly']) is str, 'unissued original draft')
    need(set(authority) == set(draft) and {k for k in authority if authority[k] != draft[k]} == {'state', 'configureAllowed', 'buildAllowed'}, 'only Root state/two permission changes')
    need(ref(observation['draft']) == ref(role_ref('root-authority.unissued')) and ref(observation['launcher']) == ref(role_ref('root-launch.py')), 'actual Root launcher/draft')
    outer_argv = [authority['wrapperPython']['path'], '-B', '-I', authority['entry']['path'], '--authority', observation['issuedAuthority']['path']]
    outer = owner(observation['terminal'], 7200, outer_argv, observation['issuedAuthority'])
    need(outer['pid'] == 11018, 'original outer PID cohort')
    need(ref(outer['stderr']) == b'', 'outer stderr retained empty')
    need([p['label'] for p in result['phases']] == LABELS and metadata['phases'] == result['phases'], 'six actual phase inventory')
    tools = {x['name']: x['executable'] for x in metadata['compilerTools']}
    expected = {
        'rust-version': [authority['rustc']['path'], '--version', '--verbose'],
        'cargo-version': [authority['cargo']['path'], '--version', '--verbose'],
        'rust-sysroot': [authority['rustc']['path'], '--print', 'sysroot'],
        'build': [tools['cmake']['path'], '--build', str(work / 'build'), '--target', 'starlingmonkey_embedding', '--parallel', '1', '--', '-d', 'keeprsp'],
        'ninja-commands': [tools['ninja']['path'], '-C', str(work / 'build'), '-t', 'commands'],
    }
    starts, floor_samples = [], []
    env = role('environment-policy')
    for phase in result['phases']:
        label = phase['label']
        phase_root = work / 'results' / label
        need(read_path(phase_root / 'phase.json') == phase, 'phase summary exact bytes')
        cap = {'configure': 2400, 'build': 7200}.get(label, 120)
        argv = [authority['wrapperPython']['path'], '-B', '-I', authority['entry']['path'], '--worker-packet', str(phase_root / 'packet.json')]
        terminal = owner(phase['outerTerminal'], cap, argv, metadata['rootAuthority'])
        starts.append(dict(pid=terminal['pid'], timeoutSeconds=cap))
        for key in ['rawExitCode', 'outerRawExitCode']:
            zero(phase[key], 'phase raw0')
        need(phase['innerOwnedClean'] is phase['ownedGone'] is True and phase['timeout'] is phase['forcedCleanup'] is False, 'phase cleanup flags')
        need(all(phase[k] == [] for k in ['errors', 'signals', 'interruptedSignals', 'remainingObservedPids']), 'phase cleanup arrays')
        packet, worker = read_path(phase_root / 'packet.json'), obj(ref(phase['workerResult']))
        need(packet['authority'] == metadata['rootAuthority'] and packet['argv'] == worker['argv'] == phase['argv'], 'phase packet/worker actual child argv')
        need(packet['cwd'] == str(work) and packet['output'] == str(phase_root) and packet['environment'] == env['environment'], 'exact phase cwd/output/environment')
        if label in expected:
            need(phase['argv'] == expected[label], 'literal phase child command')
        else:
            need(phase['argv'][:7] == [tools['cmake']['path'], '-S', str(work / 'componentize-source'), '-B', str(work / 'build'), '-G', 'Ninja'], 'actual configure command')
            definitions = dict(item[2:].split('=', 1) for item in phase['argv'][7:])
            need(definitions == metadata['requestedCMake'], 'all configure definitions')
        zero(worker['rawChildExitCode'], 'actual child raw0'); zero(worker['status'], 'worker status0')
        zero(worker['sigtermReceived'], 'no worker SIGTERM')
        need(worker['childStarted'] is worker['lifecycleComplete'] is worker['temporarySigtermHandlerRestored'] is True, 'child started/full lifecycle')
        need(worker['stoppedForDiskSpace'] is False and worker['stopReason'] is None and worker['launcherErrors'] == [], 'no worker error')
        cleanup = worker['ownedGroupCleanup']
        zero(cleanup['rawChildExitCode'], 'cleanup raw0')
        need(type(cleanup['pgid']) is int and cleanup['complete'] is True and cleanup['events'] == cleanup['errors'] == [], 'complete direct child cleanup')
        need(obj(ref(terminal['stdout'])) == worker and ref(terminal['stderr']) == b'', 'raw worker stdout/empty stderr')
        ref(worker['rawCombinedLog'])
        need(worker['rawCombinedLog'] == path_ref(phase_root / 'command.combined.log'), 'complete combined child log')
        need(len(worker['diskSamples']) > 0 and all(type(x['bytes']) is int and x['bytes'] >= 1024**3 for x in worker['diskSamples']), 'recorded sampled1GiB phase floors')
        floor_samples += [x['bytes'] for x in worker['diskSamples']]
    frames = [obj(line) for line in ref(outer['stdout']).splitlines()]
    need(frames[:-1] == starts and frames[-1] == dict(result=role_ref('result'), passed=True, engine=metadata['engine'], metadata=role_ref('metadata')), 'all six startup frames + final build stdout')
    root_frames = [obj(line) for line in ref(role_ref('root-build.stdout.log')).splitlines()]
    need(root_frames == [dict(pid=outer['pid'], timeoutSeconds=7200), observation], 'exact Root two-frame stdout')
    need(ref(role_ref('root-build.stderr.log')) == b'', 'Root stderr empty')
    need(owner_records == review['originalOwnedObservationRecordsChecked'] == 2217, 'complete seven-owner2217 snapshots')
    need(metadata['metadataKind'] == 'EXPERIMENTAL_NEXT_INTL_NATIVE_BUILD_ACTUAL_V1' and metadata['portableBuildAdmissionVersion'] == 3, 'full actual metadata kind')
    need(metadata['engine'] == result['engineCandidate'] and metadata['engine']['sha256'] == ENGINE_SHA and metadata['engine']['bytes'] == 31347353, 'new actual core descriptor; binary omitted')
    need(all(metadata[k] is False for k in ['engineExecuted', 'guestExecuted', 'adoption', 'old83MetadataProjected']), 'metadata no guest/adoption/projection')
    need(result['engineOrGuestExecuted'] is result['adoption'] is False, 'result scope')
    selection, composition = role('portable-selection'), role('input-sourceComposition')
    need(selection['composition'] == metadata['sourceComposition'] == result['sourceComposition'] == authority['composition'], 'composition role joins')
    need(selection['roleCounts'] == ROLE_COUNTS and len(selection['files']) == len(selection['physicalRecords']) == 825 and len(selection['directoryRecords']) == 171, '825/171 selected input roles')
    need(selection['roleContentSha256'] == 'c0d113eccc91c6646aadcf29ec3d9272e866a3e794eeb195c6f784472ecec799', 'actual Mat6 selection fingerprint')
    need(Counter(x['role'] for x in selection['files']) == ROLE_COUNTS, 'complete per-role roster')
    fingerprint_rows = sorted(selection['files'], key=lambda x: (x['role'], x['path']))
    need(sha(json.dumps(fingerprint_rows, sort_keys=True, separators=(',', ':')).encode()) == selection['roleContentSha256'], 'role fingerprint recomputed')
    copies = result['sourceCopies']
    need(len(copies) == 825 and len({x['source']['path'] for x in copies}) == len({x['target']['path'] for x in copies}) == 825, 'complete unique825copies')
    copied = {x['source']['path']: x for x in copies}
    manifests = {'native-policy-source': metadata['nativePolicyInputManifest'], 'build-support': metadata['buildSupportInputManifest'], 'componentize-embedding': metadata['embeddingInputManifest']}
    role_sources, role_targets = {k: [] for k in ROLE_COUNTS}, {k: [] for k in ROLE_COUNTS}
    for item in selection['files']:
        kind, rel = item['role'], item['path']
        folder = {'native-policy-source': 'source', 'build-support': 'build-support', 'componentize-embedding': 'componentize-source'}[kind]
        source = str(Path(selection['sourceRoot']).parent / folder / rel)
        need(source in copied, 'every selected role has a real copy record')
        copy = copied[source]
        target_root = work / ('componentize-source' if kind == 'componentize-embedding' else 'native-source')
        need(copy['target']['path'] == str(target_root / rel), 'actual copied role path')
        need(copy['source'] == dict(path=source, sha256=item['sha256'], bytes=item['bytes']) and copy['target'] == dict(path=str(target_root / rel), sha256=item['sha256'], bytes=item['bytes']), 'role/copy SHA and length')
        need(copy['mode'] == item['mode'] and copy['singleLink'] is copy['distinctInode'] is True, 'recorded copy modes/independent identities')
        role_sources[kind].append(copy['source']); role_targets[kind].append(copy['target'])
    for kind, manifest in manifests.items():
        if kind == 'native-policy-source':
            need(manifest == composition['files'], 'all435composition-native metadata rows')
            source_refs = [dict(path=str(Path(selection['sourceRoot']) / x['path']), sha256=x['sha256'], bytes=x['bytes']) for x in manifest]
        else:
            source_refs = [x['source'] for x in manifest]
        need(len(manifest) == ROLE_COUNTS[kind] and sorted(source_refs, key=lambda x: x['path']) == sorted(role_sources[kind], key=lambda x: x['path']), 'metadata source role complete manifest')
    native_targets = sorted(role_targets['native-policy-source'], key=lambda x: x['path'])
    need(sorted(role('configured-inputs'), key=lambda x: x['path']) == native_targets == sorted(metadata['compiledAfterInputs'], key=lambda x: x['path']), '435native configured and final manifests')
    need(sorted(result['sourceAfter'], key=lambda x: x['path']) == sorted([x['target'] for x in copies], key=lambda x: x['path']), 'all825final copied descriptors')
    by_target = {x['target']['path']: x['target'] for x in copies}
    need(by_target[str(work / 'native-source/builtins/web/fetch/request-response.cpp')]['sha256'] == '1fe296b8472f14e50556910227b184552e0a0ac424f97a0f170c4b91cfd35fa6', 'corrected cleanup TU')
    need(by_target[str(work / 'native-source/runtime/script_loader.cpp')]['sha256'] == '40eeb699d87b30dd3c146421f189a99848715a19b2efc83b081f0d61d3832d67', 'unchanged corrected interop loader')
    db = obj(ref(metadata['compileDatabase']))
    need(db == metadata['actualCompileRows'] and len(db) == 80 and len({x['file'] for x in db}) == 80, 'all80actual compile DB rows')
    need(Counter(Path(x['file']).suffix for x in db) == {'.cpp': 79, '.c': 1}, '79C++ plus oneC DB rows')
    generated = work / 'build/starling-raw.wasm/null.cpp'
    outside = [x['file'] for x in db if not x['file'].startswith(str(work / 'native-source') + '/')]
    need(outside == [str(generated)] and ref(path_ref(generated)) == b'', 'only generated empty null.cpp outside selected native rows')
    ninja = ref(metadata['wholeNinjaCommands']).decode()
    need(result['wholeNinjaCommands'] == metadata['wholeNinjaCommands'] and result['compileDatabase'] == metadata['compileDatabase'], 'full Ninja/DB role joins')
    for item in db:
        argv = shlex.split(item['command'])
        need(all(x in argv for x in ['--target=wasm32-wasi', '-m32', '-O3', '-DNDEBUG', '-flto=thin', '-Werror']), 'actual native release flags')
        need(item['directory'] == str(work / 'build') and item['command'] in ninja, 'actual compile command retained in whole Ninja graph')
    embedding = metadata['actualSeparateEmbeddingCompileRows']
    need(len(embedding) == 1 and embedding[0] in ninja and str(work / 'componentize-source/embedding/embedding.cpp') in shlex.split(embedding[0]), 'one separate actual embedding command')
    need(len(metadata['linkAndRustInputs']) == 1078 and metadata['linkAndRustInputs'] == result['linkInputs'], 'all1078recorded link/Rust inputs, payloads omitted')
    for item in metadata['linkAndRustInputs']:
        ref_shape(item)
    cache_text = ref(result['cmakeCache']).decode()
    cache = {}
    for line in cache_text.splitlines():
        match = re.fullmatch('([^/#][^:=]*):([^=]+)=(.*)', line)
        if match:
            cache[match[1]] = dict(type=match[2], value=match[3])
    need(cache == metadata['observedCMake'] == result['observedCMake'], 'all actual CMakeCache entries')
    need(all(cache[k]['value'] == v for k, v in metadata['requestedCMake'].items()), 'all56requested configure values')
    protection = result['inputProtection']
    need(type(protection['files']) is int and protection['files'] == review['protectedFileDescriptorsChecked'] == 1931 and protection['wholeTrees'] == 10, 'actual1931/10 protection inventory')
    need(protection['unchanged'] is protection['currentBeforeFinalOnly'] is True and protection['errors'] == [], 'reported before/final protection')
    trees = role('protection-before')
    need(ref(metadata['initialTreeProtection']) == ref(role_ref('protection-before')) and metadata['toolTreeInputs'] == authority['reusedTrees'], 'exact initial ten tree snapshot')
    need(set(trees) == set(authority['reusedTrees']) and len(trees) == 10, 'ten exact tree roles')
    entry_count = 0
    for name, spec in authority['reusedTrees'].items():
        inventory, snapshot = obj(ref(spec['inventory'])), trees[name]
        need(spec['root'] == inventory['root'] == snapshot['root'], 'tree root role')
        def content(tree):
            return dict(root=tree['root'], rootMode=tree['rootIdentity']['mode'], entries=[{k:v for k,v in row.items() if k not in ['dev','ino','nlink','mtimeNs']} for row in tree['entries']])
        need(content(inventory) == content(snapshot), 'tree content/mode identity after legitimate directory physical drift')
        paths = [row['path'] for row in snapshot['entries']]
        need(paths == sorted(set(paths)) and all(not PurePosixPath(x).is_absolute() and '..' not in PurePosixPath(x).parts for x in paths), 'closed safe tree inventory paths')
        for row in snapshot['entries']:
            need(row['kind'] in ['file', 'directory', 'symlink'], 'documented inventory node kind')
            if row['kind'] == 'file':
                ref_shape(dict(path=str(Path(snapshot['root']) / row['path']), sha256=row['sha256'], bytes=row['bytes']))
        entry_count += len(paths)
    need(entry_count == review['wholeTreeEntryCount'] == 15766 and review['wholeTreesCurrentContentAndPhysicalRowsEqualCapturedBefore'] is True, 'recorded full tree count/current reviewer scope')
    cargo = metadata['portableCargoAdmission']
    need(authority['portableCargoSelection'] == metadata['portableCargoSelection'] == result['portableCargoSelection'] == cargo['portableCargoSelection'], 'new actual Cargo selection role')
    ref(authority['portableCargoSelection'])
    need(cargo['sourceOnly'] is True and cargo['nativeBuildOrGuestInvoked'] is cargo['oldMetadataDescriptorsRetargeted'] is False, 'Source-only genuine Cargo proof admission')
    need(cargo['audit']['packageCount'] == 84 and cargo['audit']['logicalGraphAndFeaturesMatch'] is True and cargo['audit']['allManifestPathsBoundToFreshRoles'] is True, 'genuine recorded84graph audit')
    need(len(cargo['base21']) == result['verifiedWorkBase']['baseFiles'] == 21 and result['workBaseVerified'] is True and result['verifiedWorkBase']['exactBytesAndModes'] is result['verifiedWorkBase']['independentInodes'] is True, 'all21copied Rust base records')
    for row in cargo['base21']:
        need(row['nativeRole'] == 'native-policy-source' and row['source'] in role_sources['native-policy-source'], 'all21join selected native825')
        need(by_target[str(work / 'native-source' / row['relativePath'])] == dict(path=str(work / 'native-source' / row['relativePath']), sha256=row['sha256'], bytes=row['bytes']), 'all21copied work afterimages')
    rust = metadata['actualRustConfiguration']
    need(rust == result['configuredRust'] and rust['fullNonPathSemanticsVerified'] is rust['basePathsBoundToCopiedNativeSources'] is True, 'actual Rust configuration roles')
    manifest, lock = tomllib.loads(ref(rust['manifest']).decode()), tomllib.loads(ref(rust['lock']).decode())
    need(ref(rust['lock']) == ref(metadata['actualAggregateLock']) and rust['lock']['sha256'] == 'dc098f33febee6952974705077140ff543ca37eb1cedad2e0b07496646c3bd61', 'exact aggregate84lock')
    need(len(lock['package']) == 84 and len({(p['name'],p['version'],p.get('source')) for p in lock['package']}) == 84, 'all84unique locked packages')
    roots = ['rust-encoding','rust-hooks','rust-url','multipart','icu_capi','unicode-bidi-ffi']
    need(list(manifest['dependencies']) == rust['dependencyNames'] == cargo['audit']['rootDependencies'] == roots, 'six exact root dependencies')
    need(manifest['lib'] == {'crate-type':['staticlib'],'path':'rust-staticlib.rs'} and manifest['workspace'] == {}, 'one aggregate staticlib/empty workspace')
    ffi = Path(cargo['firefoxRoot'])
    dep_paths = {name: str(work / 'native-source/crates' / folder) for name,folder in zip(roots[:4], ['rust-encoding','rust-hooks','rust-url','rust-multipart'])}
    dep_paths |= {'icu_capi': str(ffi/'intl/icu_capi'), 'unicode-bidi-ffi': str(ffi/'intl/bidi/rust/unicode-bidi-ffi')}
    need(all(manifest['dependencies'][k]['path'] == v for k,v in dep_paths.items()), 'fresh copied/native and restored FFI dependency paths')
    need(manifest['dependencies']['icu_capi'] == dict(path=dep_paths['icu_capi'], **{'default-features':False}, features=['any_provider','compiled_data','segmenter','calendar']), 'exact ICU feature selection')
    need(metadata['actualRustTools'] == dict(cargo=authority['cargo'], rustc=authority['rustc']), 'real direct Rust tools')
    need(metadata['wrapperPython'] == observation['wrapperPython'] == authority['wrapperPython'] and metadata['buildToolPython'] == observation['nativeBuildToolPython'] == tools['python3'], 'Python3.11 wrapper vs3.9 build roles')
    need(env['HOMEInherited'] is env['privateCargoHome'] is env['offline'] is True and env['rustupInvoked'] is False, 'inherited/private/offline policy')
    need(env['environment']['CARGO_NET_OFFLINE'] == 'true' and env['environment']['CARGO_BUILD_JOBS'] == '1' and env['environment']['MAKEFLAGS'] == '-j1', 'offline one-job actual environment')
    # Authenticate only the finite selected Source witnesses against their retained indexes.
    witness_count = 0
    for path,row in by_path.items():
        if '/source-witnesses/' in '/' + row['member'] and Path(path).name != 'index.json':
            root = Path(path).parent
            idx = read_path(root / 'index.json')
            entry = next((x for x in idx['files'] if x['path'] == Path(path).name), None)
            need(entry is not None and dict(entry, path=path) == row['original'], 'indexed finite Source witness')
            witness_count += 1
    need(ref(authority['entry']) == ref(metadata['recipe']) and authority['callerIndex'] == review['callerSourceIndex'], 'selected recipe/Source role')
    need(plan['disk'] == dict(startBytes=3 * 1024**3, stopBytes=1024**3) and plan['timeouts'] == dict(tool=120, configure=2400, build=7200, harvest=120), 'unchanged original disk floors/deadlines')
    for path,before in current.items():
        need(physical(path) == before, 'whole current selected-read bookend')
    for path,before in local_before.items():
        need(physical(path) == before, 'whole local packet-read bookend')
    print(json.dumps(dict(state='FETCH_CLEANUP_FULL_NATIVE_FINITE_DATA_REPLAY_PASSED_V1', capsuleSealed=sealed,
          members=len(rows), expandedBytes=index['expandedBytes'], originalOwnedRecords=owner_records,
          sixRawZeroPhases=True, sourceCopyRecords=825, nativeCompileRows=80, separateEmbeddingCommands=1,
          lockedPackages=84, protectedDescriptorRecords=1931, treeSnapshotRoles=10, treeSnapshotEntries=entry_count,
          selectedSourceWitnesses=witness_count, minimumRecordedPhaseFreeBytes=min(floor_samples),
          currentSelectedTextCompared=args.current, nativeBuildDataPassed=True, engineOrGuestExecuted=False,
          omittedBinaryOr825PayloadRehashed=False, componentOrRuntimeAccepted=False, adoption=False,
          scope='Structural/hash checks of retained producer/reviewer DATA; no cryptographic execution or continuous filesystem attestation.')))


if __name__ == '__main__':
    main()
