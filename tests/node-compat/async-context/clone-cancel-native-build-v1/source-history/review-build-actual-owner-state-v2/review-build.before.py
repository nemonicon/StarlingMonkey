"""Root runs after the real native owner closes. Stdlib DATA review only."""
import ast
import copy
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shlex
import stat
import sys
import tomllib

if not __debug__ or not sys.flags.isolated or not sys.dont_write_bytecode:
    raise RuntimeError('requires unoptimized Python -I -B before input IO')

ACTUAL_RESULT = {'path': '/private/tmp/starling-node-compat/next-clone-cancel-native-build-v1-first/closed-collection-v2/result.json', 'sha256': 'd1c29a586c1a1d6f4e176e4f9ae1de166a42745dca0effff60f5197beaeb846a', 'bytes': 735488}
ACTUAL_METADATA = {'path': '/private/tmp/starling-node-compat/next-clone-cancel-native-build-v1-first/closed-collection-v2/metadata.json', 'sha256': 'c7e225af3046b87939ec057ecf6c4ecbea3a3102a77c1fc05e4bf6f39b74f026', 'bytes': 1161902}
ACTUAL_OUTER_TERMINAL = {'path': '/private/tmp/starling-node-compat/next-clone-cancel-native-recovery-v1-first/commands/native-build-v2/terminal.json', 'sha256': '59f4407118302c3f57c229ab872579dc01798b635883b08af0a74aa8333974e0', 'bytes': 269166}
if any(value is None for value in (ACTUAL_RESULT, ACTUAL_METADATA, ACTUAL_OUTER_TERMINAL)):
    raise RuntimeError('Root must bind the corrected collection result/metadata and original raw1 owner descriptors before input IO')

HERE = Path(__file__).resolve().parent
WORK = Path('/private/tmp/starling-node-compat/next-clone-cancel-native-build-v1-first')
OUTER = Path('/private/tmp/starling-node-compat/next-clone-cancel-native-recovery-v1-first/commands/native-build-v2')
OUTPUT = HERE / 'actual-engine-admission.json'
BUILDER = dict(path=str(HERE / 'run-build.py'), sha256='1cad0ccb6ffd3a5fe55f243b0c3728957e282970503f88287c8d8b59e870f3de', bytes=40260)
SELECTION = dict(path=str(HERE / 'build-selection.json'), sha256='cc807f6ea77a7ac951114d11ec03c952ad6cdffcdfc9d79192a48a23c41c8bcc', bytes=21843)
COLLECTOR = dict(path=str(HERE.parent / 'clone-cancel-native-build-collection-v2/collect.py'), sha256='21e1bbe4669e67f0fb554a4d47e693904275581e1b0b997af3f91b762ac94d79', bytes=25193)
ORIGINAL_RESULT = dict(path=str(WORK / 'result.json'), sha256='54291d8dd9b7b8ed954ef996e7dbdf2e75cf46c81c70adb6516e523e42bfed7c', bytes=2092519)
ORIGINAL_METADATA = dict(path=str(WORK / 'metadata.json'), sha256='779bd077b36a94f62091a30ec4018c008dd91b80437f1445a36632867d24f34f', bytes=1158971)
ORIGINAL_OUTER = dict(path=str(OUTER / 'terminal.json'), sha256='59f4407118302c3f57c229ab872579dc01798b635883b08af0a74aa8333974e0', bytes=269166)
COLLECTION_TERMINAL = dict(path='/private/tmp/starling-node-compat/next-clone-cancel-native-recovery-v1-first/commands/collect-native-v2/terminal.json', sha256='18fd16d01558d4302599db4374ff115a17bf49f339dd3180fcc4c6d07a67d725', bytes=1549)
GENERATED_REVIEW = dict(path=str(HERE.parent / 'next-clone-cancel-native-root-results-v1/generated-tu-source-data-review.json'), sha256='4f91d134d91a3d2cabe109ef9817bdd052e04f9c79646388677310aad41d9043', bytes=9065)
CORE_VALIDATION = dict(path='/private/tmp/starling-node-compat/next-clone-cancel-native-recovery-v1-first/commands/validate-built-core/terminal.json', sha256='d2bcc02b0a0b712f9ef5b11ef3b6dbedd4296a93f00141b97fd0f694e95d89e6', bytes=1527)
NULL_CPP = dict(path=str(WORK / 'build/starling-raw.wasm/null.cpp'), sha256='e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', bytes=0)
NULL_WRITER = dict(path=str(WORK / 'native-source/cmake/spidermonkey.cmake'), sha256='af02f2af5ac9d5ceeb6e6e1b63ff433f33377b52d1ec1719732f008c12ad2da7', bytes=8409)
NULL_CONSUMER = dict(path=str(WORK / 'native-source/cmake/build-crates.cmake'), sha256='3cbf3f9f080345694c40bc329bbc56b553b137d6291eaf745213c285e5a50dab', bytes=5761)
REL = 'builtins/web/fetch/request-response.cpp'
AFTER_SHA = '0431184d4562972c98538494caf46d2b11cdf0280f51d0e7143cd8534526442e'
DOC_LIMIT = 32 * 1024**2
FILE_LIMIT = 2 * 1024**3
AGGREGATE_LIMIT = 96 * 1024**3
seen = {}
groups = dict(build=set(), source=set())
charged = 0


def need(condition, message):
    if not condition:
        raise RuntimeError(message)


def core(ref):
    need(isinstance(ref, dict), 'descriptor must be an object')
    out = {key: ref[key] for key in ('path', 'sha256', 'bytes')}
    need(isinstance(out['path'], str) and isinstance(out['sha256'], str) and
         re.fullmatch('[0-9a-f]{64}', out['sha256']) is not None and
         type(out['bytes']) is int and 0 <= out['bytes'] <= FILE_LIMIT, 'invalid descriptor')
    return out


def stamp(s):
    return (s.st_dev, s.st_ino, s.st_mode, s.st_nlink, s.st_size, s.st_mtime_ns, s.st_ctime_ns)


def check(reference, group='build'):
    global charged
    ref = core(reference)
    p = Path(ref['path'])
    need(p.is_absolute() and p.resolve(strict=True) == p, 'noncanonical file: ' + str(p))
    before = p.lstat()
    need(stat.S_ISREG(before.st_mode) and before.st_size == ref['bytes'], 'file kind/size: ' + str(p))
    groups[group].add(str(p))
    if str(p) in seen:
        old, old_stamp = seen[str(p)]
        need(old == ref and old_stamp == stamp(before), 'conflicting/changed input: ' + str(p))
        return p
    charged += ref['bytes']
    need(charged <= AGGREGATE_LIMIT, 'aggregate read declaration limit')
    h = hashlib.sha256()
    with p.open('rb') as f:
        need(stamp(os.fstat(f.fileno())) == stamp(before), 'changed before open')
        remaining = ref['bytes']
        while remaining:
            data = f.read(min(1024**2, remaining))
            need(bool(data), 'short file')
            h.update(data)
            remaining -= len(data)
        need(f.read(1) == b'' and stamp(os.fstat(f.fileno())) == stamp(before), 'file grew/changed')
    need(stamp(p.lstat()) == stamp(before) and h.hexdigest() == ref['sha256'], 'hash/bookend: ' + str(p))
    # Host make/git are OS-managed hardlinked stubs; output-tree rules below
    # separately enforce nlink1 where the actual recipe promises it.
    seen[str(p)] = (ref, stamp(before))
    return p


def observe(path, group='build'):
    p = Path(path)
    before = p.lstat()
    need(stat.S_ISREG(before.st_mode) and before.st_size <= FILE_LIMIT, 'observed file bound')
    h = hashlib.sha256()
    with p.open('rb') as f:
        for data in iter(lambda: f.read(1024**2), b''):
            h.update(data)
    need(stamp(p.lstat()) == stamp(before), 'observed file changed')
    ref = dict(path=str(p), sha256=h.hexdigest(), bytes=before.st_size)
    check(ref, group)
    return ref


def payload(ref, group='build', limit=DOC_LIMIT):
    need(core(ref)['bytes'] <= limit, 'document/text bound')
    p = check(ref, group)
    with p.open('rb') as f:
        data = f.read(limit + 1)
    need(len(data) == ref['bytes'] and len(data) <= limit and
         hashlib.sha256(data).hexdigest() == ref['sha256'], 'bounded read mismatch')
    return data


def unique(pairs):
    out = {}
    for key, value in pairs:
        need(key not in out, 'duplicate JSON key')
        out[key] = value
    return out


def read(ref, group='build'):
    return json.loads(payload(ref, group), object_pairs_hook=unique,
                      parse_constant=lambda _: (_ for _ in ()).throw(RuntimeError('nonfinite JSON')))


def local(path, group='build'):
    ref = observe(path, group)
    return read(ref, group), ref


def relative(name):
    p = PurePosixPath(name)
    need(isinstance(name, str) and not p.is_absolute() and name == p.as_posix() and
         p.parts and all(part not in ('', '.', '..') for part in p.parts), 'unsafe relative path')
    return p


def terminal(ref, argv=None, seconds=None, authority=None, raw_exit=0):
    t = read(ref)
    need(type(t['rawExitCode']) is int and t['rawExitCode'] == raw_exit and t['timeout'] is False and t['forcedCleanup'] is False and
         t['parentOwnedGroupGone'] is True and t['allObservedOwnedGroupsGone'] is True and
         t['interruptedSignals'] == t['remainingObservedPids'] == t['signals'] == t['errors'] == [],
         'original owner did not finish with required raw code and clean ownership')
    need(type(t['pid']) is int and t['pid'] > 1 and t['finalGroups'] and
         all(row['alive'] is False for row in t['finalGroups']), 'owner final group facts')
    check(t['stdout']); check(t['stderr'])
    start, _ = local(Path(ref['path']).parent / 'started.json')
    need(start['pid'] == t['pid'] and start['authority'] == t['authority'], 'owner start/terminal join')
    if argv is not None:
        need(start['argv'] == argv, 'owner actual argv')
    if seconds is not None:
        need(start['timeoutSeconds'] == seconds, 'owner original cap')
    if authority is not None:
        need(t['authority'] == authority, 'owner authority descriptor')
    check(t['authority'])
    return t


def tree(snapshot):
    root = Path(snapshot['root'])
    need(root.is_absolute() and root.resolve(strict=True) == root and root.is_dir(), 'tree root')
    rs = root.lstat()
    for key, value in dict(mode=stat.S_IMODE(rs.st_mode), dev=rs.st_dev, ino=rs.st_ino,
                           nlink=rs.st_nlink, mtimeNs=rs.st_mtime_ns).items():
        if key in snapshot['rootIdentity']:
            need(snapshot['rootIdentity'][key] == value, 'tree root identity: ' + str(root))
    names = set()
    for row in snapshot['entries']:
        rel = relative(row['path']).as_posix()
        need(rel not in names, 'duplicate tree member')
        names.add(rel)
        p = root / rel
        s = p.lstat()
        need(stat.S_IMODE(s.st_mode) == row['mode'], 'tree mode: ' + str(p))
        for key, value in dict(dev=s.st_dev, ino=s.st_ino, nlink=s.st_nlink, mtimeNs=s.st_mtime_ns).items():
            if key in row:
                need(row[key] == value, 'tree physical bookend: ' + str(p))
        if row['kind'] == 'file':
            need(stat.S_ISREG(s.st_mode), 'tree regular kind')
            check(dict(path=str(p), sha256=row['sha256'], bytes=row['bytes']))
        elif row['kind'] == 'directory':
            need(stat.S_ISDIR(s.st_mode), 'tree directory kind')
        else:
            need(row['kind'] == 'symlink' and stat.S_ISLNK(s.st_mode) and
                 os.readlink(p) == row['target'] and p.resolve(strict=True).is_relative_to(root), 'tree confined alias')
    need({p.relative_to(root).as_posix() for p in root.rglob('*')} == names, 'whole tree membership')


def cache_values(ref):
    out = {}
    for line in payload(ref).decode().splitlines():
        if not line or line.startswith(('#', '//')) or '=' not in line:
            continue
        left, value = line.split('=', 1)
        if ':' in left:
            name, kind = left.split(':', 1)
            need(name not in out, 'duplicate cache name')
            out[name] = dict(type=kind, value=value)
    return out


def builder_keys():
    source = payload(BUILDER).decode()
    parsed = ast.parse(source)
    assignments = [n for n in parsed.body if isinstance(n, ast.Assign) and
                   any(isinstance(t, ast.Name) and t.id == 'METADATA_KEYS' for t in n.targets)]
    need(len(assignments) == 1, 'builder metadata key declaration')
    declared = ast.literal_eval(assignments[0].value)
    functions = [n for n in parsed.body if isinstance(n, ast.FunctionDef) and n.name == 'actual_metadata']
    need(len(functions) == 1, 'builder actual metadata source')
    calls = [n.value for n in ast.walk(functions[0]) if isinstance(n, ast.Assign) and
             any(isinstance(t, ast.Name) and t.id == 'metadata' for t in n.targets) and
             isinstance(n.value, ast.Call) and isinstance(n.value.func, ast.Name) and n.value.func.id == 'dict']
    need(len(calls) == 1 and all(k.arg is not None for k in calls[0].keywords), 'builder explicit whole-object construction')
    emitted = [k.arg for k in calls[0].keywords]
    need(len(declared) == len(set(declared)) and len(emitted) == len(set(emitted)) and
         set(declared) == set(emitted), 'builder whole keyset agreement')
    collector = ast.parse(payload(COLLECTOR).decode())
    metadata_functions = [n for n in collector.body if isinstance(n, ast.FunctionDef) and n.name == 'actual_metadata']
    need(len(metadata_functions) == 1, 'selected collector metadata source')
    constructed = [n.value for n in ast.walk(metadata_functions[0]) if isinstance(n, ast.Assign) and
                   any(isinstance(t, ast.Name) and t.id == 'metadata' for t in n.targets) and
                   isinstance(n.value, ast.Call) and isinstance(n.value.func, ast.Name) and n.value.func.id == 'dict']
    need(len(constructed) == 1 and all(k.arg is not None for k in constructed[0].keywords) and
         len(constructed[0].keywords) == len(emitted) and
         {k.arg for k in constructed[0].keywords} == set(emitted), 'whole collector/builder keyset agreement')
    return sorted(emitted)


def source_evidence(s, old):
    m = read(s['sourceMaterialization'], 'source')
    need(m['state'] == 'CLONE_CANCEL_825_INPUTS_MATERIALIZED_V1' and m['workRoot'] == str(WORK) and
         m['predecessorWholeMetadata'] == s['predecessorMetadata'] and m['inputsUnchanged'] is True and
         m['previousMetadataProjected'] is False and m['changedNativePaths'] == [REL], 'source materialization facts')
    need((m['nativeCount'], m['supportCount'], m['embeddingCount']) == (435, 387, 3) and len(m['copies']) == 825,
         'actual selected source recipe')
    base = {r['path']: r for r in old['nativePolicyInputManifest']}
    old_support = {r['relativePath']: r for r in old['buildSupportInputManifest']}
    old_embedding = {r['relativePath']: r for r in old['embeddingInputManifest']}
    names = set()
    roles = dict(native=[], support=[], embedding=[])
    for r in m['copies']:
        rel = relative(r['relativePath']).as_posix()
        need(r['role'] in roles, 'source role')
        parent = WORK / ('componentize-source' if r['role'] == 'embedding' else 'native-source')
        need(r['target']['path'] == r['destination'] == str(parent / rel) and
             r['destination'] not in names and
             all(r['source'][k] == r['target'][k] for k in ('sha256', 'bytes')), 'source copy join')
        names.add(r['destination'])
        for key in ('source', 'target', 'predecessor'):
            if key in r:
                check(r[key], 'source')
        st = Path(r['destination']).lstat()
        need(st.st_nlink == 1 and stat.S_IMODE(st.st_mode) == r['mode'], 'source mode/link')
        if r['role'] == 'native':
            expected = base[rel]
            if rel == REL:
                need(expected['sha256'] == '1fe296b8472f14e50556910227b184552e0a0ac424f97a0f170c4b91cfd35fa6' and
                     r['target']['sha256'] == AFTER_SHA and r['target']['bytes'] == 130742, 'one exact afterimage')
            else:
                need(all(r['target'][k] == expected[k] for k in ('sha256', 'bytes')), 'unexpected native source delta')
        else:
            expected = (old_support if r['role'] == 'support' else old_embedding)[rel]
            need(r['source'] == expected['source'] and r['mode'] == expected['mode'], 'support/embedding change')
        roles[r['role']].append(r)
    need(tuple(len(roles[k]) for k in ('native', 'support', 'embedding')) == (435, 387, 3), 'source role cardinality')
    for ref in m['protectedInputs']:
        check(ref, 'source')
    check(m['recipe'], 'source')
    check(m['predecessorComposition'], 'source')
    for ref in m['cargo'].values():
        if isinstance(ref, dict) and {'path', 'sha256', 'bytes'} <= ref.keys():
            check(ref, 'source')
    g = read(s['generatorResult'], 'source')
    request = read(g['request'], 'source')
    need(g['state'] == 'CLONE_CANCEL_GENERATOR_CHECKS_COMPLETED_V1' and g['passed'] is True and
         g['inputsUnchanged'] is True and g['primaryError'] is None and g['verificationError'] is None and
         request['sourceMaterialization'] == s['sourceMaterialization'] and
         len(g['commands']) == len(m['generatorCommands']) == 10, 'actual generator checks')
    for record, expected in zip(g['commands'], m['generatorCommands']):
        need(record['command'] == expected and record['rawExitCode'] == 0 and record['clean'] is True and
             expected['argv'][0] == m['generatorNode']['path'] and expected['argv'][-1] == '--check', 'generator command')
        terminal(record['terminal'], expected['argv'], 120)
        check(record['stdout'], 'source'); check(record['stderr'], 'source')
        need(record['stderr']['bytes'] == 0, 'generator stderr')
    return m, roles


def expected_manifests(old):
    out = dict(public=[], private=[], moduleNames=[])
    modules = set()
    for kind in ('public', 'private'):
        for prior in old['selectedModuleManifests'][kind]:
            name = relative(prior['relativePath']).as_posix()
            ref = observe(WORK / 'native-source' / name, 'source')
            data = read(ref, 'source')
            need(data == prior['wholeManifest'], 'selected whole manifest changed')
            if kind == 'public':
                need(data['schemaVersion'] == 1 and data['nodeVersion'] == 'v22.14.0', 'public manifest header')
                for module, body in data['modules'].items():
                    need(module.startswith('node:') and module not in modules and
                         len(body['exports']) == len(set(body['exports'])), 'public module surface')
                    modules.add(module)
            else:
                need(data['publicNodeManifest'] is False and data['specifier'].startswith('starling:'), 'private manifest')
            out[kind].append(dict(relativePath=name, descriptor=ref, wholeManifest=data))
    out['moduleNames'] = sorted(modules)
    return out


def operations(s, result):
    tools = {r['name']: r['executable']['path'] for r in s['hostTools']}
    scheduled = [
        ('rust-version', [s['rustc']['path'], '--version', '--verbose'], 120),
        ('cargo-version', [s['cargo']['path'], '--version', '--verbose'], 120),
        ('rust-sysroot', [s['rustc']['path'], '--print', 'sysroot'], 120),
        ('configure', [tools['cmake'], '-S', str(WORK / 'componentize-source'), '-B', str(WORK / 'build'), '-G', 'Ninja',
                       *['-D' + k + '=' + v for k, v in s['cmakeFlags'].items()]], 2400),
        ('build', [tools['cmake'], '--build', str(WORK / 'build'), '--target', 'starlingmonkey_embedding', '--parallel', '1', '--', '-d', 'keeprsp'], 7200),
        ('ninja-commands', [tools['ninja'], '-C', str(WORK / 'build'), '-t', 'commands'], 120)]
    need(len(result['phases']) == len(scheduled), 'complete actual native phase set')
    for record, (label, argv, cap) in zip(result['phases'], scheduled):
        directory = WORK / 'results' / label
        need(record['label'] == label and record['argv'] == argv and record['rawExitCode'] == record['outerRawExitCode'] == 0 and
             record['innerOwnedClean'] is True and record['ownedGone'] is True and record['timeout'] is False and
             record['forcedCleanup'] is False and record['errors'] == record['signals'] ==
             record['interruptedSignals'] == record['remainingObservedPids'] == [], 'phase result/ownership')
        phase, _ = local(directory / 'phase.json')
        need(phase == record, 'phase publication equality')
        packet, pref = local(directory / 'packet.json')
        need(packet['selection'] == SELECTION and packet['entry'] == BUILDER and packet['label'] == label and
             packet['argv'] == argv and packet['cwd'] == str(WORK) and packet['output'] == str(directory), 'worker packet')
        term = terminal(record['outerTerminal'], [s['wrapperPython']['path'], '-I', '-B', BUILDER['path'], '--worker-packet', pref['path']], cap, SELECTION)
        need(record['outerTerminal']['path'] == str(directory / 'owned-monitor/terminal.json'), 'phase original owner path')
        worker = read(record['workerResult'])
        cleanup = worker['ownedGroupCleanup']
        need(worker['argv'] == argv and worker['rawChildExitCode'] == worker['status'] == 0 and
             worker['childStarted'] is True and worker['lifecycleComplete'] is True and
             worker['stoppedForDiskSpace'] is False and worker['stopReason'] is None and
             worker['sigtermReceived'] == 0 and worker['temporarySigtermHandlerRestored'] is True and
             worker['launcherErrors'] == [] and cleanup['complete'] is True and
             cleanup['rawChildExitCode'] == 0 and cleanup['events'] == cleanup['errors'] == [], 'inner lifecycle')
        need(worker['rawCombinedLog']['path'] == str(directory / 'command.combined.log'), 'raw combined path')
        check(worker['rawCombinedLog'])
        need(worker['diskSamples'] and all(type(x['bytes']) is int and x['bytes'] >= 1024**3 for x in worker['diskSamples']), 'recorded disk floor')
        log = payload(worker['rawCombinedLog'], limit=64 * 1024**2).decode()
        if label == 'rust-version':
            need(re.search(r'^release: 1\.88\.0$', log, re.M) is not None, 'actual Rust version')
        elif label == 'cargo-version':
            need(log.startswith('cargo 1.88.0 '), 'actual Cargo version')
        elif label == 'rust-sysroot':
            need(log.strip() == s['reusedTrees']['rust']['root'], 'actual Rust sysroot')
    return scheduled


def cargo(s, materialized, result):
    review = read(result['cargoMetadataReview'])
    need(review == result['freshCargoAdmission'] and review['state'] == 'FRESH_LOCKED_OFFLINE_CARGO_METADATA_REVIEW_V1' and
         review['passed'] is True and review['sourceMaterialization'] == s['sourceMaterialization'] and
         review['manifest'] == materialized['cargo']['manifest'] and review['lock'] == materialized['cargo']['lock'] and
         review['config'] == materialized['cargo']['config'] and review['oldCapsuleProjected'] is False and
         review['oldInstallationOrAuthorityClaimed'] is False, 'actual fresh Cargo admission')
    command = review['command']
    argv = [s['cargo']['path'], 'metadata', '--locked', '--offline', '--format-version', '1', '--manifest-path', review['manifest']['path']]
    need(command['argv'] == argv and command['clean'] is True, 'Cargo metadata actual argv')
    terminal(command['terminal'], argv, 600, SELECTION)
    actual = read(command['stdout'])
    check(command['stderr'])
    phase, _ = local(WORK / 'results/cargo-metadata/phase.json')
    need(phase == command and actual['version'] == 1 and actual['workspace_root'] == str(WORK / 'cargo-project') and
         actual['target_directory'] == str(WORK / 'rust-target'), 'Cargo actual outputs')
    packages = actual['packages']
    ids = {p['id'] for p in packages}
    need(packages and len(ids) == len(packages) and {n['id'] for n in actual['resolve']['nodes']} == ids and
         all(dep in ids for n in actual['resolve']['nodes'] for dep in n['dependencies']), 'Cargo complete graph')
    allowed = [WORK / 'cargo-project', WORK / 'native-source', Path(s['reusedTrees']['intl-firefox']['root']), Path(s['reusedTrees']['intl-vendor']['root'])]
    for package in packages:
        p = Path(package['manifest_path'])
        need(p.resolve(strict=True) == p and any(root in p.parents for root in allowed), 'Cargo package path')
        observe(p, 'source')
    roots = [p for p in packages if p['manifest_path'] == review['manifest']['path']]
    manifest = tomllib.loads(payload(review['manifest'], 'source').decode())
    names = {'rust-encoding', 'rust-hooks', 'rust-url', 'multipart', 'icu_capi', 'unicode-bidi-ffi'}
    need(len(roots) == 1 and actual['resolve']['root'] == roots[0]['id'] and
         set(manifest['dependencies']) == names and {p['name'] for p in roots[0]['dependencies']} == names and
         review['packages'] == len(packages) and review['resolveNodes'] == len(ids), 'Cargo declared root/dependencies')
    configured = result['configuredRust']
    configured_doc = tomllib.loads(payload(configured['manifest']).decode())
    expected = copy.deepcopy(manifest)
    need(expected['dependencies']['unicode-bidi-ffi'].get('features', []) == [], 'bidi features')
    expected['dependencies']['unicode-bidi-ffi']['features'] = []
    need(configured_doc == expected and configured['lock']['path'] == str(WORK / 'build/starling-raw.wasm/Cargo.lock') and
         all(configured['lock'][k] == materialized['cargo']['lock'][k] for k in ('sha256', 'bytes')) and
         configured['fullNonPathSemanticsVerified'] is True and configured['basePathsBoundToCopiedNativeSources'] is True,
         'actual configured Rust manifest/lock')
    check(configured['lock'])
    need(configured_doc['workspace'] == {} and configured_doc['lib'] == {'crate-type': ['staticlib'], 'path': 'rust-staticlib.rs'} and
         configured_doc['dependencies']['icu_capi']['default-features'] is False and
         configured_doc['dependencies']['icu_capi']['features'] == ['any_provider', 'compiled_data', 'segmenter', 'calendar'], 'configured Rust semantic profile')
    return review, configured


def main():
    need(len(sys.argv) == 1 and not os.path.lexists(OUTPUT), 'fixed reviewer/new admission only')
    need(ACTUAL_RESULT['path'] == str(WORK / 'closed-collection-v2/result.json') and
         ACTUAL_METADATA['path'] == str(WORK / 'closed-collection-v2/metadata.json') and
         ACTUAL_OUTER_TERMINAL == ORIGINAL_OUTER, 'corrected outputs and immutable original owner paths')
    s = read(SELECTION)
    # Establish original ownership quiescence, preserving its actual raw1.
    outer = terminal(ACTUAL_OUTER_TERMINAL, [s['wrapperPython']['path'], '-I', '-B', BUILDER['path']], 7200, raw_exit=1)
    request = read(outer['authority'])
    need(request['state'] == 'ROOT_FIXED_NATIVE_BUILD_OWNER_REQUEST_V1' and request['seconds'] == 7200 and
         request['configureCapSeconds'] == 2400 and request['buildCapSeconds'] == 7200 and
         request['nativeBuildAllowed'] is True and request['guestExecutionAllowed'] is False, 'actual outer owner request')
    for ref in request['protectedInputs']:
        check(ref, 'source')
    outer_collection, collection_ref = local(OUTER / 'collection.json')
    need(outer_collection['terminal'] == ACTUAL_OUTER_TERMINAL and outer_collection['request'] == outer['authority'] and
         outer_collection['rawExitCode'] == 1 and outer_collection['clean'] is False and outer_collection['inputsUnchanged'] is True and
         outer_collection['primaryError'] is None and outer_collection['verificationError'] is None and
         outer_collection['collectionErrors'] == [], 'original raw1 collection retained with clean ownership')
    # The new read-only collector must itself have a genuine successful owner.
    ct = terminal(COLLECTION_TERMINAL, [s['wrapperPython']['path'], '-I', '-B', COLLECTOR['path']], 600)
    collector_request = read(ct['authority'])
    collector_index = observe(HERE.parent / 'clone-cancel-native-build-collection-v2/index.json')
    need(collector_request['argv'] == [s['wrapperPython']['path'], '-I', '-B', COLLECTOR['path']] and
         collector_request['seconds'] == 600 and COLLECTOR in collector_request['inputs'] and
         collector_index in collector_request['inputs'] and s['monitor'] in collector_request['inputs'] and
         s['wrapperPython'] in collector_request['inputs'], 'generic collector authority and closed Source family')
    for ref in collector_request['inputs']:
        check(ref)
    keys = builder_keys()
    old = read(s['predecessorMetadata'], 'source')
    result = read(ORIGINAL_RESULT)
    original_metadata = read(ORIGINAL_METADATA)
    need(result['state'] == 'CLONE_CANCEL_NATIVE_BUILD_FAILED_UNACCEPTED_V1' and result['passed'] is False and
         result['selection'] == SELECTION and result['sourceMaterialization'] == s['sourceMaterialization'] and
         result['ownerQuiescenceKnown'] is True and result['primaryError'] is None and
         result['buildCommandSucceeded'] is True and result['engineOrGuestExecuted'] is False and result['adoption'] is False and
         result['inputProtection']['unchanged'] is True and result['inputProtection']['errors'] == [] and
         result['inputProtection']['currentBeforeFinalOnly'] is True and result['metadata'] == ORIGINAL_METADATA,
         'original failed build facts may not be rewritten')
    errors = result['postCollectionErrors']
    failed_expression = "assert all(r['file'] in {x['target']['path'] for x in rows} for r in compile_rows)"
    need(len(errors) == 1 and errors[0]['type'] == 'AssertionError' and errors[0]['message'] == '' and
         failed_expression in errors[0]['stack'] and 'line 431, in actual_metadata' in errors[0]['stack'] and
         original_metadata['nativeExportDiagnosticCompileEvidence'] is None, 'exclusive original post-collection failure')
    reviewed = read(ACTUAL_RESULT)
    need(reviewed['state'] == 'CLOSED_NATIVE_BUILD_COLLECTION_REVIEW_COMPLETED_V2' and
         reviewed['passed'] is reviewed['collectionReviewPassed'] is reviewed['nativeCommandsPassed'] is True and
         reviewed['originalDriverPassed'] is False and type(reviewed['originalOuterRawExitCode']) is int and
         reviewed['originalOuterRawExitCode'] == 1 and reviewed['originalFailedResult'] == ORIGINAL_RESULT and
         reviewed['originalMetadata'] == ORIGINAL_METADATA and reviewed['actualOuterTerminal'] == ACTUAL_OUTER_TERMINAL and
         reviewed['actualOuterCollection'] == collection_ref and reviewed['actualOuterRequest'] == outer['authority'] and
         reviewed['actualOuterStarted'] == observe(OUTER / 'started.json') and
         reviewed['builderSource'] == BUILDER and reviewed['collectorSource'] == COLLECTOR and reviewed['buildSelection'] == SELECTION and
         reviewed['nativeMetadata'] == ACTUAL_METADATA and reviewed['metadataKeys'] == keys and
         reviewed['originalFailureBitsPreserved'] is reviewed['originalPhaseProvenancePreserved'] is True and
         reviewed['oldMetadataProjected'] is reviewed['toolsInvoked'] is reviewed['nativeRecompiled'] is
         reviewed['guestExecuted'] is reviewed['fullNextAccepted'] is False, 'actual corrected collection roles and scope')
    need(reviewed['coreEngineExecuted'] is reviewed['componentValidated'] is False and
         reviewed['actualStaticCoreValidation'] == CORE_VALIDATION and
         reviewed['originalFailureClassification'] == 'exclusive prebuild recipe-membership predicate rejected selected CMake generated empty TU',
         'collection classification and core-validation scope')
    metadata = read(ACTUAL_METADATA)
    need(sorted(metadata) == sorted(original_metadata) == keys and
         {k for k in metadata if metadata[k] != original_metadata[k]} == {'metadataKind', 'nativeExportDiagnosticCompileEvidence'},
         'whole new metadata and immutable original difference set')
    materialized, roles = source_evidence(s, old)
    operations(s, result)
    cargo_review, configured = cargo(s, materialized, result)
    protection = read(result['treeProtectionBefore'])
    need(set(protection) == set(s['reusedTrees']) == set(metadata['toolTreeInputs']) and
         result['inputProtection']['wholeTrees'] == len(protection) == 11, 'complete selected tree roles')
    for role, selected in s['reusedTrees'].items():
        spec = metadata['toolTreeInputs'][role]
        need(spec['root'] == selected['root'] and spec['provenance'] == selected['provenance'], 'new tree role source')
        snap = read(spec['inventory'])
        need(snap == protection[role], 'protected tree inventory join')
        check(spec['provenance'])
        if 'archive' in spec:
            need(spec['archive'] == selected['archive'], 'tree actual archive join')
            check(spec['archive'])
        tree(snap)
    composition = read(result['sourceComposition'], 'source')
    native = [dict(path=r['relativePath'], sha256=r['target']['sha256'], bytes=r['target']['bytes']) for r in roles['native']]
    need(composition == dict(schemaVersion=1, state='ACTUAL_ONE_AFTERIMAGE_NATIVE_COMPOSITION_V1', sourceRoot=str(WORK / 'native-source'),
         nativeSourceFiles=435, files=native, inputs=[s['sourceMaterialization'], s['predecessorMetadata']], oneChangedNativePath=REL,
         actualAfterimageSHA256=AFTER_SHA, oldCompositionRetargeted=False), 'fresh source composition')
    db = read(metadata['compileDatabase'])
    need(metadata['compileDatabase']['path'] == str(WORK / 'build/compile_commands.json') and db == metadata['actualCompileRows'] and
         len(db) == len({r['file'] for r in db}) == 80, 'whole actual compile database')
    source_targets = {r['target']['path'] for r in roles['native']}
    recipe_rows = [r for r in db if r['file'] in source_targets]
    generated_rows = [r for r in db if r['file'] not in source_targets]
    need(len(recipe_rows) == 79 and len(generated_rows) == 1 and generated_rows[0]['file'] == NULL_CPP['path'],
         'exact 79 recipe plus one selected CMake-generated empty translation unit')
    check(NULL_CPP, 'source'); check(NULL_WRITER, 'source'); check(NULL_CONSUMER, 'source')
    writer_lines = payload(NULL_WRITER, 'source').decode().splitlines()
    consumer_lines = payload(NULL_CONSUMER, 'source').decode().splitlines()
    need(writer_lines[46].strip() == 'file(WRITE ${CMAKE_CURRENT_BINARY_DIR}/null.cpp "")' and
         consumer_lines[85].strip() == 'add_library(rust-crates STATIC ${CMAKE_CURRENT_BINARY_DIR}/null.cpp)',
         'actual selected CMake producer and consumer Source')
    grow = generated_rows[0]
    need(grow['directory'] == str(WORK / 'build') and
         grow['output'] == str(WORK / 'build/starling-raw.wasm/CMakeFiles/rust-crates.dir/null.cpp.obj'), 'generated TU paths')
    oldroot = Path(old['compiledSourceRoot'])
    old_recipe_files = {Path(r['file']).relative_to(oldroot).as_posix() for r in old['actualCompileRows'] if Path(r['file']).is_relative_to(oldroot)}
    actual_files = {Path(r['file']).relative_to(WORK / 'native-source').as_posix() for r in recipe_rows}
    need(actual_files == old_recipe_files and len(actual_files) == 79 and REL in actual_files, 'unchanged 79 native recipe unit set')
    generated_proof = read(GENERATED_REVIEW)
    need(generated_proof['closedBuildResult'] == ORIGINAL_RESULT and generated_proof['originalMetadata'] == ORIGINAL_METADATA and
         generated_proof['sourceMaterialization'] == s['sourceMaterialization'] and
         generated_proof['compilePartition']['total'] == 80 and generated_proof['compilePartition']['authenticatedRecipeMembers'] == 79 and
         generated_proof['compilePartition']['generatedMembers'] == 1 and generated_proof['compilePartition']['otherMembers'] == 0 and
         generated_proof['compilePartition']['generatedRow'] == grow, 'independent generated-TU Source/DATA proof joins')
    for ref in generated_proof['selectedFiles'].values():
        check(ref, 'source')
    generated = dict(source=NULL_CPP, compileRow=grow, writer=NULL_WRITER, writerLine=47, consumer=NULL_CONSUMER,
                     consumerLine=86, emptyContentVerified=True, noOtherUnmappedTranslationUnitAllowed=True,
                     independentSourceDataReview=GENERATED_REVIEW)
    need(reviewed['generatedSourceDataReview'] == GENERATED_REVIEW and reviewed['generatedTranslationUnit'] == generated and
         (reviewed['totalCompileRows'], reviewed['nativeRecipeCompileRows'], reviewed['generatedCompileRows'],
          reviewed['separateEmbeddingCompileRows']) == (80, 79, 1, 1), 'corrected diagnostic partition evidence')
    outputs = set()
    for row in db:
        argv = row.get('arguments') or shlex.split(row['command'])
        need(row['file'] in source_targets | {NULL_CPP['path']} and argv.count('-c') == argv.count('-o') == 1 and
             argv[argv.index('-c') + 1] == row['file'], 'compile input/output argv')
        output = Path(argv[argv.index('-o') + 1])
        if not output.is_absolute():
            output = Path(row['directory']) / output
        need(output.resolve().is_relative_to(WORK / 'build'), 'native object root')
        outputs.add(str(output.resolve()))
        need(not any('NODE_COMPAT_NATIVE_EXPORT_DIAGNOSTIC_V1' in token for token in argv), 'diagnostic macro leaked to native units')
    ninja = payload(metadata['wholeNinjaCommands'], limit=64 * 1024**2).decode()
    embedding = [line for line in ninja.splitlines() if ' -c ' + str(WORK / 'componentize-source/embedding/embedding.cpp') in line]
    need(len(embedding) == 1 and embedding == metadata['actualSeparateEmbeddingCompileRows'], 'one actual separate embedding command')
    macro = 'NODE_COMPAT_NATIVE_EXPORT_DIAGNOSTIC_V1'
    definition = '-D' + macro + '=1'
    need([token for token in shlex.split(embedding[0]) if macro in token] == [definition], 'sole embedding diagnostic token')
    observed = cache_values(observe(WORK / 'build/CMakeCache.txt'))
    allowed_paths = dict(Rust_COMPILER=s['rustc']['path'], Rust_CARGO=s['cargo']['path'],
        NODE_COMPAT_INTL_LOCKFILE=materialized['cargo']['lock']['path'], NODE_COMPAT_INTL_FIREFOX_SOURCE=s['reusedTrees']['intl-firefox']['root'],
        CPM_OpenSSL_SOURCE=str(WORK / 'private-openssl/openssl-3.0.17'))
    allowed_paths.update({'CPM_' + role + '_SOURCE': s['reusedTrees'][role]['root'] for role in
                          ('wasi-sdk', 'binaryen', 'wasm-tools', 'wasmtime', 'weval', 'corrosion')})
    need(s['cmakeFlags'] == {**old['requestedCMake'], **allowed_paths} and observed == metadata['observedCMake'] and
         metadata['requestedCMake'] == s['cmakeFlags'] and all(observed.get(k, {}).get('value') == v for k, v in s['cmakeFlags'].items()) and
         observed[macro] == dict(type='BOOL', value='ON') and
         observed.get('Rust_TOOLCHAIN_IS_RUSTUP_MANAGED', {}).get('value') not in ('TRUE', 'ON', '1'), 'whole selected/configured CMake values')
    link_names = sorted(str(p) for p in (WORK / 'build').rglob('*') if p.is_file() and
                        (p.suffix in ('.a', '.o', '.obj', '.rsp') or p.name in ('Cargo.toml', 'Cargo.lock', 'rust-staticlib.rs')))
    need(metadata['linkAndRustInputs'] == result['linkInputs'] and
         [r['path'] for r in result['linkInputs']] == link_names and outputs <= set(link_names), 'complete current link/Rust artifact closure')
    for ref in result['linkInputs']:
        check(ref)
    engine = metadata['engine']
    need(engine == result['engineCandidate'] == reviewed['engine'] and
         engine['path'] == str(WORK / 'componentize-source/lib/starlingmonkey_embedding.wasm'), 'actual engine role')
    ep = check(engine)
    with ep.open('rb') as f:
        need(f.read(8) == b'\x00asm\x01\x00\x00\x00', 'actual native core header')
    expected_source_names = {r['target']['path'] for r in materialized['copies']} | {engine['path']}
    need({str(p) for name in ('native-source', 'componentize-source') for p in (WORK / name).rglob('*') if p.is_file()} == expected_source_names and
         not any(p.is_symlink() for name in ('native-source', 'componentize-source') for p in (WORK / name).rglob('*')),
         'complete copied Source and engine-only added artifact membership')
    terminal(CORE_VALIDATION, [str(Path(s['reusedTrees']['wasm-tools']['root']) / 'wasm-tools'), 'validate', engine['path']], 120)
    expected_diagnostic = dict(option=macro, requested='ON', observed=observed[macro], embeddingDefinition=definition,
        embeddingDefinitionOccurrences=1, separateEmbeddingCommands=1, nativeCompileRows=80,
        nativeRowsWithDiagnosticDefinition=0, compiledSourceAfterimagesAuthenticated=True,
        totalCompileRows=80, nativeRecipeCompileRows=79, generatedCompileRows=1, generatedTranslationUnits=[generated])
    manifests = expected_manifests(old)
    sdkroot = Path(s['reusedTrees']['spidermonkey']['root'])
    sdk_refs = {key: observe(sdkroot / name) for key, name in [('actualLibrary', 'libspidermonkey.a'),
        ('actualSavedFrameHeader', 'include/js/SavedFrameAPI.h'), ('actualConfigHeader', 'include/js-config.h'), ('actualConfdefs', 'include/js-confdefs.h')]}
    for key, ref in sdk_refs.items():
        need(all(ref[k] == old[key][k] for k in ('sha256', 'bytes')), 'selected coherent SDK content changed')
    # Every actual field is checked; old absent capsule/authority values stay absent.
    expected = dict(schemaVersion=1, metadataKind='CLONE_CANCEL_NATIVE_BUILD_CLOSED_OUTPUT_COLLECTION_V2', sourceComposition=result['sourceComposition'],
        sourceRoot=str(WORK / 'native-source'), compiledSourceRoot=str(WORK / 'native-source'), compiledAfterInputs=[r['target'] for r in roles['native']],
        compilerTools=s['hostTools'], actualRustTools=dict(cargo=s['cargo'], rustc=s['rustc']), nativePolicyInputCount=len(roles['native']),
        nativePolicyInputManifest=native, buildSupportInputCount=len(roles['support']),
        buildSupportInputManifest=[dict(relativePath=r['relativePath'], mode=r['mode'], source=r['target']) for r in roles['support']],
        embeddingInputCount=len(roles['embedding']), embeddingInputManifest=[dict(relativePath=r['relativePath'], mode=r['mode'], source=r['target']) for r in roles['embedding']],
        selectedModuleManifests=manifests, requestedCMake=s['cmakeFlags'], observedCMake=observed, compileDatabase=metadata['compileDatabase'],
        actualCompileRows=db, wholeNinjaCommands=result['wholeNinjaCommands'], actualSeparateEmbeddingCompileRows=embedding,
        **sdk_refs, patchedSpiderMonkeyEvidence=s['provenance']['historicalPatchedSpiderMonkeyProofRecovered'],
        savedFramePatchIndex=old['savedFramePatchIndex'], actualAggregateLock=materialized['cargo']['lock'], actualRustConfiguration=configured,
        offlineCargoConfig=materialized['cargo']['config'], validatedCargoAudit=result['cargoMetadataReview'], portableCargoSelection=None,
        portableCargoAdmission=cargo_review, wrapperPython=s['wrapperPython'], buildToolPython=next(r['executable'] for r in s['hostTools'] if r['name'] == 'python3'),
        portableBuildAdmissionVersion=1, logicalCargoAuditDescriptorFromVerifiedCapsule=False, validatedCargoProofCapsule=None,
        validatedCargoProofIndex=None, toolTreeInputs=metadata['toolTreeInputs'], initialTreeProtection=result['treeProtectionBefore'],
        originalExtractionWholeTreeAttestationClaimed=False, linkAndRustInputs=result['linkInputs'], engine=engine,
        phases=result['phases'], recipe=BUILDER, rootAuthority=None, old83MetadataProjected=False, engineExecuted=False,
        guestExecuted=False, adoption=False, nativeExportDiagnosticCompileEvidence=expected_diagnostic)
    need(sorted(expected) == keys and metadata == expected, 'full actual metadata role/value validation')
    expected_sources = sorted([r['target'] for r in materialized['copies']] + [NULL_CPP], key=lambda r: r['path'])
    need(reviewed['protectedSourceInputs'] == expected_sources, 'collector complete 825 Source plus empty generated TU')
    protected = reviewed['protectedBuildInputs']
    need(protected == sorted(protected, key=lambda r: r['path']) and len({r['path'] for r in protected}) == len(protected) and
         reviewed['currentInputProtection'] == dict(unchanged=True, files=len(protected), trees=11), 'collector current protection wire')
    required = [BUILDER, COLLECTOR, SELECTION, ORIGINAL_RESULT, ORIGINAL_METADATA, ACTUAL_OUTER_TERMINAL,
                collection_ref, outer['authority'], GENERATED_REVIEW, CORE_VALIDATION]
    need(all(core(r) in protected for r in required), 'collector protected ancestry/prerequisite omissions')
    for ref in protected:
        check(ref)
    for ref in expected_sources:
        check(ref, 'source')
    for key in ('actualAggregateLock', 'offlineCargoConfig', 'patchedSpiderMonkeyEvidence', 'savedFramePatchIndex'):
        check(metadata[key], 'source')
    for item in s['hostTools']:
        check(item['executable'])
    for key in ('cbindgen', 'cpmModule', 'monitor', 'lifecycle', 'wrapperPython', 'cargo', 'rustc'):
        check(s[key])
    for key in ('toolRecoveryResult', 'rustRecoveryResult', 'corrosionRecoveryResult', 'sdkRecoveryResult'):
        check(s[key])
    environment, environment_ref = local(WORK / 'environment-policy.json')
    need(environment['privateCargoHome'] is True and environment['offline'] is True and environment['rustupInvoked'] is False and
         environment['environment']['SPIDERMONKEY_BINARIES'] == str(sdkroot) and
         environment['environment']['STARLINGMONKEY_SRC'] == str(WORK / 'native-source') and
         environment['environment']['RUSTC'] == s['rustc']['path'], 'actual build environment')
    for field in ('CMAKE_C_COMPILER', 'CMAKE_CXX_COMPILER'):
        if field in observed:
            observe(Path(observed[field]['value']).resolve(strict=True))
    self_ref = observe(Path(__file__).resolve())
    for path, (_, expected_stamp) in seen.items():
        need(stamp(Path(path).lstat()) == expected_stamp, 'review final input bookend: ' + path)
    report = dict(schemaVersion=1, state='CLONE_CANCEL_ACTUAL_ENGINE_ADMISSION_PASSED_V1', passed=True,
        engine=engine, nativeMetadata=ACTUAL_METADATA, metadataKeys=keys, metadataFieldsVerified=keys,
        completeActualMetadataReviewed=True, oldMetadataProjected=False, nativeBuildPassed=True, guestExecuted=False,
        actualBuildResult=ACTUAL_RESULT, correctedBuildCollection=ACTUAL_RESULT,
        originalFailedBuildResult=ORIGINAL_RESULT, originalFailedBuildMetadata=ORIGINAL_METADATA,
        originalDriverPassed=False, originalOuterRawExitCode=1, originalFailureBitsPreserved=True,
        buildSelection=SELECTION, actualOuterTerminal=ACTUAL_OUTER_TERMINAL, actualOuterCollection=collection_ref,
        actualCollectionTerminal=COLLECTION_TERMINAL, collectorSource=COLLECTOR,
        builderSource=BUILDER, reviewerSource=self_ref, actualSourceMaterialization=s['sourceMaterialization'],
        actualGeneratorResult=s['generatorResult'], actualSourceComposition=result['sourceComposition'],
        actualCargoMetadataReview=result['cargoMetadataReview'], actualStaticCoreValidation=CORE_VALIDATION,
        generatedSourceDataReview=GENERATED_REVIEW, toolTreeSnapshots=metadata['toolTreeInputs'],
        protectedBuildInputs=[seen[p][0] for p in sorted(groups['build'])],
        protectedSourceInputs=[seen[p][0] for p in sorted(groups['source'])],
        filesVerified=len(seen), fileBytesVerified=charged, sourceRecipe=dict(native=435, support=387, embedding=3, changedNativePaths=[REL]),
        totalCompileRows=len(db), nativeRecipeCompileRows=len(recipe_rows), generatedCompileRows=len(generated_rows),
        nativeCompileRows=len(db), separateEmbeddingRows=len(embedding), ordinaryExportsInvoked=False,
        coreWasmHeaderVerified=True, staticCoreValidationVerified=True, componentStandard13Verified=False,
        componentConstructed=False, runtimeAccepted=False, fullNextAccepted=False,
        scope='Full actual native-build DATA admission after genuine readonly collection. Original driver remains failed/raw1; native commands and all independently rederived collection gates passed. Constructor adds its own complete WIT/fixture/adapter/compiler/capture closure and actual component validation.',
        sourceAuthorRelationship='B authored SDK recovery/shared context cases and this reader; C authored builder/closed collector; R authored native afterimage/Rust recovery/generated-TU proof. This reader imports or replays no builder, collector or helper function.')
    data = (json.dumps(report, indent=2) + '\n').encode()
    need(len(data) <= 16 * 1024**2, 'admission publication bound')
    with OUTPUT.open('xb') as f:
        f.write(data); f.flush(); os.fsync(f.fileno())
    saved = OUTPUT.read_bytes()
    need(saved == data, 'admission publication readback')
    print(json.dumps(dict(admission=dict(path=str(OUTPUT), sha256=hashlib.sha256(data).hexdigest(), bytes=len(data)), passed=True)), flush=True)


if __name__ == '__main__':
    main()
