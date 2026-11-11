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

ACTUAL_RESULT = None
ACTUAL_METADATA = None
ACTUAL_OUTER_TERMINAL = None
if any(value is None for value in (ACTUAL_RESULT, ACTUAL_METADATA, ACTUAL_OUTER_TERMINAL)):
    raise RuntimeError('Root must bind the three actual closed-build descriptors before input IO')

HERE = Path(__file__).resolve().parent
WORK = Path('/private/tmp/starling-node-compat/next-clone-cancel-native-build-v1-first')
OUTER = Path('/private/tmp/starling-node-compat/next-clone-cancel-native-recovery-v1-first/commands/native-build-v2')
OUTPUT = HERE / 'actual-engine-admission.json'
BUILDER = dict(path=str(HERE / 'run-build.py'), sha256='1cad0ccb6ffd3a5fe55f243b0c3728957e282970503f88287c8d8b59e870f3de', bytes=40260)
SELECTION = dict(path=str(HERE / 'build-selection.json'), sha256='cc807f6ea77a7ac951114d11ec03c952ad6cdffcdfc9d79192a48a23c41c8bcc', bytes=21843)
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


def terminal(ref, argv=None, seconds=None, authority=None):
    t = read(ref)
    need(t['rawExitCode'] == 0 and t['timeout'] is False and t['forcedCleanup'] is False and
         t['parentOwnedGroupGone'] is True and t['allObservedOwnedGroupsGone'] is True and
         t['interruptedSignals'] == t['remainingObservedPids'] == t['signals'] == t['errors'] == [],
         'original owner did not finish raw0/clean')
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
    need(len(sys.argv) == 1 and not OUTPUT.exists() and not OUTPUT.is_symlink(), 'fixed reviewer/new admission only')
    need(ACTUAL_RESULT['path'] == str(WORK / 'result.json') and ACTUAL_METADATA['path'] == str(WORK / 'metadata.json') and
         ACTUAL_OUTER_TERMINAL['path'] == str(OUTER / 'terminal.json'), 'fixed actual output paths')
    # Establish quiescence before reading the build result/metadata/artifacts.
    outer = terminal(ACTUAL_OUTER_TERMINAL, [read(SELECTION)['wrapperPython']['path'], '-I', '-B', BUILDER['path']], 7200)
    request = read(outer['authority'])
    need(request['state'] == 'ROOT_FIXED_NATIVE_BUILD_OWNER_REQUEST_V1' and request['seconds'] == 7200 and
         request['configureCapSeconds'] == 2400 and request['buildCapSeconds'] == 7200 and
         request['nativeBuildAllowed'] is True and request['guestExecutionAllowed'] is False, 'actual outer owner request')
    for ref in request['protectedInputs']:
        check(ref, 'source')
    collection, collection_ref = local(OUTER / 'collection.json')
    need(collection['terminal'] == ACTUAL_OUTER_TERMINAL and collection['request'] == outer['authority'] and
         collection['rawExitCode'] == 0 and collection['clean'] is True and collection['inputsUnchanged'] is True and
         collection['primaryError'] is None and collection['verificationError'] is None and collection['collectionErrors'] == [], 'actual outer final collection')
    keys = builder_keys()
    s = read(SELECTION)
    old = read(s['predecessorMetadata'], 'source')
    result = read(ACTUAL_RESULT)
    need(result['state'] == 'CLONE_CANCEL_NATIVE_BUILD_COMPLETED_RUNTIME_PENDING_V1' and result['passed'] is True and
         result['selection'] == SELECTION and result['sourceMaterialization'] == s['sourceMaterialization'] and
         result['ownerQuiescenceKnown'] is True and result['primaryError'] is None and result['postCollectionErrors'] == [] and
         result['buildCommandSucceeded'] is True and result['engineOrGuestExecuted'] is False and result['adoption'] is False and
         result['inputProtection']['unchanged'] is True and result['inputProtection']['errors'] == [] and
         result['inputProtection']['currentBeforeFinalOnly'] is True and result['metadata'] == ACTUAL_METADATA, 'actual complete build result')
    metadata = read(ACTUAL_METADATA)
    need(sorted(metadata) == keys, 'actual whole metadata keyset differs from selected builder source')
    materialized, roles = source_evidence(s, old)
    operations(s, result)
    cargo_review, configured = cargo(s, materialized, result)
    protection = read(result['treeProtectionBefore'])
    need(set(protection) == set(s['reusedTrees']) == set(metadata['toolTreeInputs']) and
         result['inputProtection']['wholeTrees'] == len(protection), 'complete selected tree roles')
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
    # Source composition is the freshly published one-afterimage object.
    composition = read(result['sourceComposition'], 'source')
    native = [dict(path=r['relativePath'], sha256=r['target']['sha256'], bytes=r['target']['bytes']) for r in roles['native']]
    need(composition == dict(schemaVersion=1, state='ACTUAL_ONE_AFTERIMAGE_NATIVE_COMPOSITION_V1', sourceRoot=str(WORK / 'native-source'),
         nativeSourceFiles=435, files=native, inputs=[s['sourceMaterialization'], s['predecessorMetadata']], oneChangedNativePath=REL,
         actualAfterimageSHA256=AFTER_SHA, oldCompositionRetargeted=False), 'fresh source composition')
    db = read(metadata['compileDatabase'])
    need(metadata['compileDatabase']['path'] == str(WORK / 'build/compile_commands.json') and db == metadata['actualCompileRows'] and
         len(db) == len({r['file'] for r in db}) == 80, 'whole actual compile database')
    oldroot = Path(old['compiledSourceRoot'])
    old_files = {Path(r['file']).relative_to(oldroot).as_posix() for r in old['actualCompileRows']}
    actual_files = {Path(r['file']).relative_to(WORK / 'native-source').as_posix() for r in db}
    need(actual_files == old_files and REL in actual_files, 'same native compilation units, including afterimage')
    source_targets = {r['target']['path'] for r in materialized['copies']}
    outputs = set()
    for row in db:
        argv = row.get('arguments') or shlex.split(row['command'])
        need(row['file'] in source_targets and '-c' in argv and argv[argv.index('-c') + 1] == row['file'] and '-o' in argv, 'native compile input/output argv')
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
    observed_ref = observe(WORK / 'build/CMakeCache.txt')
    observed = cache_values(observed_ref)
    need(observed == metadata['observedCMake'] and metadata['requestedCMake'] == s['cmakeFlags'] and
         all(observed.get(k, {}).get('value') == v for k, v in s['cmakeFlags'].items()) and
         observed[macro] == dict(type='BOOL', value='ON') and
         observed.get('Rust_TOOLCHAIN_IS_RUSTUP_MANAGED', {}).get('value') not in ('TRUE', 'ON', '1'), 'whole configured CMake values')
    link_names = sorted(str(p) for p in (WORK / 'build').rglob('*') if p.is_file() and
                        (p.suffix in ('.a', '.o', '.obj', '.rsp') or p.name in ('Cargo.toml', 'Cargo.lock', 'rust-staticlib.rs')))
    need(metadata['linkAndRustInputs'] == result['linkInputs'] and
         [r['path'] for r in result['linkInputs']] == link_names and outputs <= set(link_names), 'complete current link/Rust artifact closure')
    for ref in result['linkInputs']:
        check(ref)
    engine = metadata['engine']
    need(engine == result['engineCandidate'] and engine['path'] == str(WORK / 'componentize-source/lib/starlingmonkey_embedding.wasm'), 'actual engine role')
    ep = check(engine)
    with ep.open('rb') as f:
        need(f.read(8) == b'\x00asm\x01\x00\x00\x00', 'actual native core header')
    expected_diagnostic = dict(option=macro, requested='ON', observed=observed[macro], embeddingDefinition=definition,
        embeddingDefinitionOccurrences=1, separateEmbeddingCommands=1, nativeCompileRows=80,
        nativeRowsWithDiagnosticDefinition=0, compiledSourceAfterimagesAuthenticated=True)
    manifests = expected_manifests(old)
    sdkroot = Path(s['reusedTrees']['spidermonkey']['root'])
    sdk_refs = {key: observe(sdkroot / name) for key, name in [('actualLibrary', 'libspidermonkey.a'),
        ('actualSavedFrameHeader', 'include/js/SavedFrameAPI.h'), ('actualConfigHeader', 'include/js-config.h'), ('actualConfdefs', 'include/js-confdefs.h')]}
    for key, ref in sdk_refs.items():
        need(all(ref[k] == old[key][k] for k in ('sha256', 'bytes')), 'selected coherent SDK content changed')
    # Each actual metadata field has an explicit independently checked meaning.
    expected = dict(schemaVersion=1, metadataKind='CLONE_CANCEL_NATIVE_BUILD_ACTUAL_V1', sourceComposition=result['sourceComposition'],
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
    need(result['nativeExportDiagnosticCompileEvidence'] == expected_diagnostic, 'actual diagnostic result evidence')
    for key in ('actualAggregateLock', 'offlineCargoConfig', 'patchedSpiderMonkeyEvidence', 'savedFramePatchIndex'):
        check(metadata[key], 'source')
    for item in s['hostTools']:
        check(item['executable'])
    for key in ('cbindgen', 'cpmModule', 'monitor', 'lifecycle', 'wrapperPython', 'cargo', 'rustc'):
        check(s[key])
    for key in ('toolRecoveryResult', 'rustRecoveryResult', 'corrosionRecoveryResult', 'sdkRecoveryResult'):
        check(s[key])
    # Source-selected generated compiler wrappers and environment are also retained.
    environment, environment_ref = local(WORK / 'environment-policy.json')
    need(environment['privateCargoHome'] is True and environment['offline'] is True and environment['rustupInvoked'] is False and
         environment['environment']['SPIDERMONKEY_BINARIES'] == str(sdkroot) and
         environment['environment']['STARLINGMONKEY_SRC'] == str(WORK / 'native-source') and
         environment['environment']['RUSTC'] == s['rustc']['path'], 'actual build environment')
    for field in ('CMAKE_C_COMPILER', 'CMAKE_CXX_COMPILER'):
        if field in observed:
            compiler = Path(observed[field]['value']).resolve(strict=True)
            observe(compiler)
    self_ref = observe(Path(__file__).resolve())
    for path, (_, expected_stamp) in seen.items():
        need(stamp(Path(path).lstat()) == expected_stamp, 'review final input bookend: ' + path)
    report = dict(schemaVersion=1, state='CLONE_CANCEL_ACTUAL_ENGINE_ADMISSION_PASSED_V1', passed=True,
        engine=engine, nativeMetadata=ACTUAL_METADATA, metadataKeys=keys, metadataFieldsVerified=keys,
        completeActualMetadataReviewed=True, oldMetadataProjected=False, nativeBuildPassed=True, guestExecuted=False,
        actualBuildResult=ACTUAL_RESULT, buildSelection=SELECTION, actualOuterTerminal=ACTUAL_OUTER_TERMINAL,
        actualOuterCollection=collection_ref, builderSource=BUILDER, reviewerSource=self_ref,
        actualSourceMaterialization=s['sourceMaterialization'], actualGeneratorResult=s['generatorResult'],
        actualSourceComposition=result['sourceComposition'], actualCargoMetadataReview=result['cargoMetadataReview'],
        toolTreeSnapshots=metadata['toolTreeInputs'],
        protectedBuildInputs=[seen[p][0] for p in sorted(groups['build'])],
        protectedSourceInputs=[seen[p][0] for p in sorted(groups['source'])],
        filesVerified=len(seen), fileBytesVerified=charged, sourceRecipe=dict(native=435, support=387, embedding=3, changedNativePaths=[REL]),
        nativeCompileRows=len(db), separateEmbeddingRows=len(embedding), ordinaryExportsInvoked=False,
        coreWasmHeaderVerified=True, componentStandard13Verified=False, componentConstructed=False,
        runtimeAccepted=False, fullNextAccepted=False,
        scope='Actual native-build DATA admission only. Full source/build regular-file closure is explicit; tree snapshots also carry confined aliases. Constructor must add adapter, all closed WIT/fixture/compiler/capture inputs and obtain its own actual standard13/import validation.',
        sourceAuthorRelationship='B authored SDK recovery/shared context cases and this independent reader; C authored native builder; R authored native afterimage and Rust/Corrosion recovery. No builder/helper function is imported or replayed by this reader.')
    data = (json.dumps(report, indent=2) + '\n').encode()
    need(len(data) <= 16 * 1024**2, 'admission publication bound')
    with OUTPUT.open('xb') as f:
        f.write(data); f.flush(); os.fsync(f.fileno())
    saved = OUTPUT.read_bytes()
    need(saved == data, 'admission publication readback')
    print(json.dumps(dict(admission=dict(path=str(OUTPUT), sha256=hashlib.sha256(data).hexdigest(), bytes=len(data)), passed=True)), flush=True)


if __name__ == '__main__':
    main()
