"""Plan/read-only by default; one future Root-authorized offline metadata command."""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tarfile
import traceback

HERE = Path(__file__).resolve().parent


def need(value, message):
    if value is not True:
        raise ValueError(message)


def physical(value, exists=True):
    p = Path(value)
    need(p.is_absolute() and str(p) == str(value) and '..' not in p.parts, 'canonical absolute path')
    for q in (p, *p.parents):
        need(not q.is_symlink(), 'symlink/alias path')
    need(p.resolve() == p and (not exists or p.exists()), 'physical path')
    return p


def row(value):
    p = physical(value)
    info = p.stat()
    need(p.is_file() and info.st_nlink == 1, 'regular single-link input')
    h = hashlib.sha256()
    with p.open('rb') as stream:
        for b in iter(lambda: stream.read(1048576), b''):
            h.update(b)
    return dict(path=str(p), sha256=h.hexdigest(), bytes=info.st_size)


def verify(ref):
    need(set(ref) == {'path', 'sha256', 'bytes'} and type(ref['bytes']) is int and row(ref['path']) == ref, 'descriptor mismatch')
    return physical(ref['path'])


def read(ref):
    need(ref['bytes'] <= 32 * 1048576, 'bounded JSON')
    return json.loads(verify(ref).read_bytes())


def family(ref):
    value = read(ref)
    root = Path(ref['path']).parent
    names, directories = set(), set()
    for r in value['files']:
        p = Path(r['path'])
        need(not p.is_absolute() and '..' not in p.parts and str(p) == r['path'] and r['path'] not in names, 'family confined unique members')
        names.add(r['path'])
        directories.update(str(q) for q in p.parents if q != Path('.'))
        verify(dict(r, path=str(root / p)))
    nodes = list(root.rglob('*'))
    need(not any(p.is_symlink() for p in nodes), 'family alias')
    need({str(p.relative_to(root)) for p in nodes if p.is_file()} == names | {'index.json'}, 'whole family file membership')
    need({str(p.relative_to(root)) for p in nodes if p.is_dir()} == directories, 'whole family directory membership')
    need(all(p.is_file() or p.is_dir() for p in nodes), 'family special file')
    return value


def save(path, value):
    data = (json.dumps(value, indent=2) + '\n').encode()
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(data)
        stream.flush()
        os.fchmod(stream.fileno(), 0o600)
        os.fsync(stream.fileno())
    return row(path)


def load(ref, name):
    spec = importlib.util.spec_from_file_location(name, verify(ref))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def plan():
    return json.loads((HERE / 'plan.json').read_bytes())


def module_ref(index_ref, name):
    index = family(index_ref)
    member = next(r for r in index['files'] if r['path'] == name)
    return dict(member, path=str(Path(index_ref['path']).parent / name))


def admit_restore(p, receipt_ref):
    module = load(module_ref(p['restoreAdmissionSourceIndex'], 'admit.py'), 'held_restored_cargo_admission')
    admitted = module.admit_restore(receipt_ref)
    need(admitted['schemaVersion'] == 1 and admitted['state'] == 'RESTORED_CARGO_SOURCE_DATA_CONSISTENT_V2'
         and admitted['dataConsistent'] is True and admitted['actualCargoMetadata'] is None
         and admitted['nativeBuildOrGuestExecutionProved'] is admitted['sourceProcessExecutionAttested'] is False,
         'restore DATA admission scope')
    need(admitted['sourceIndex'] == p['restoreSourceIndex'] and admitted['receipt'] == receipt_ref, 'restore Source/receipt coupling')
    need(admitted['admissionSourceIndex'] == p['restoreAdmissionSourceIndex'], 'separate read-only admission Source')
    links = admitted['rootLinkCountObservation']
    need(links['crossPublicationNlinkCompared'] is False and links['currentFullRootRowGuardedWithinRead'] is True
         and links['linkCountsAreNotResourceOrTeardownProof'] is True, 'truthful root link-count observation')
    root = physical(admitted['root'])
    need(admitted['intlLockfile']['path'] == str(root / 'project/Cargo.lock')
         and admitted['offlineCargoConfig']['path'] == str(root / 'offline-cargo/config.toml'), 'restored project/config roles')
    need(admitted['intlLockfile']['sha256'] == p['lockSha256'], 'exact84 lock')
    need(admitted['baseRoot'] == str(root / 'sources/base')
         and admitted['firefoxRoot'] == str(root / 'sources/firefox')
         and admitted['vendorRoot'] == str(root / 'vendor'), 'fresh restored roots')
    return admitted


def reference_metadata(p):
    index = read(p['referencePayloadIndex'])
    expected = next(r for r in index['entries'] if r['path'] == p['referenceMetadataMember'])
    need(expected['sha256'] == p['referenceMetadataSha256'], 'retained reference identity')
    with tarfile.open(verify(p['referenceBundle']), 'r:gz') as archive:
        member = archive.getmember(p['referenceMetadataMember'])
        need(member.isfile() and member.size == expected['bytes'] <= 2 * 1048576, 'retained metadata member')
        value = archive.extractfile(member).read()  # Read text DATA only; no filesystem extraction.
    need(hashlib.sha256(value).hexdigest() == expected['sha256'], 'retained metadata bytes')
    return json.loads(value)


def graph(metadata):
    packages = {p['id']: p for p in metadata['packages']}
    need(len(packages) == len(metadata['packages']) == 84, '84 unique package IDs')
    def identity(identifier):
        p = packages[identifier]
        return (p['name'], p['version'], p['source'])
    nodes = metadata['resolve']['nodes']
    need({n['id'] for n in nodes} == set(packages) and len(nodes) == 84, '84 complete resolve nodes')
    value = {}
    for node in nodes:
        ids = sorted((identity(x) for x in node['dependencies']), key=repr)
        need(ids == sorted({identity(d['pkg']) for d in node['deps']}, key=repr), 'redundant dependency inventories agree')
        dependencies = [dict(name=d['name'], package=identity(d['pkg']), depKinds=d['dep_kinds']) for d in node['deps']]
        value[identity(node['id'])] = dict(features=sorted(node['features']), dependencies=sorted(dependencies, key=repr))
    need(len(value) == 84, 'unique logical package identities')
    return value


def validate_metadata(metadata, admitted, p, output, reference):
    need(graph(metadata) == graph(reference), 'exact logical identities/features/dependency edges')
    packages = {x['id']: x for x in metadata['packages']}
    root = packages[metadata['resolve']['root']]
    need(root['name'] == 'rust-staticlib' and {d['name'] for d in root['dependencies']} == set(p['rootDependencies'])
         and len(root['dependencies']) == 6, 'exact six root dependencies')
    need([t['crate_types'] for t in root['targets'] if 'staticlib' in t['crate_types']] == [['staticlib']], 'one root staticlib')
    project = Path(admitted['root']) / 'project'
    need(metadata['workspace_root'] == str(project) and metadata['target_directory'] == str(output / 'target'), 'fresh workspace/target roles')
    local = {'rust-staticlib': project,
             'rust-encoding': Path(admitted['baseRoot']) / 'crates/rust-encoding',
             'rust-hooks': Path(admitted['baseRoot']) / 'crates/rust-hooks',
             'rust-url': Path(admitted['baseRoot']) / 'crates/rust-url',
             'multipart': Path(admitted['baseRoot']) / 'crates/rust-multipart',
             'icu_capi': Path(admitted['firefoxRoot']) / 'intl/icu_capi',
             'icu_segmenter_data': Path(admitted['firefoxRoot']) / 'intl/icu_segmenter_data',
             'unicode-bidi-ffi': Path(admitted['firefoxRoot']) / 'intl/bidi/rust/unicode-bidi-ffi'}
    for package in packages.values():
        if package['source'] is None:
            expected = local[package['name']] / 'Cargo.toml'
        else:
            expected = Path(admitted['vendorRoot']) / (package['name'] + '-' + package['version']) / 'Cargo.toml'
        need(package['manifest_path'] == str(expected), 'fresh manifest role: ' + package['name'])
    return dict(packageCount=84, logicalGraphAndFeaturesMatch=True, rootDependencies=p['rootDependencies'],
                allManifestPathsBoundToFreshRoles=True, oneAggregateStaticlib=True,
                oldMetadataDescriptorsRetargeted=False, referenceUsedAsLogicalGraphOnly=True)


def invocation(p, admitted, output):
    return [p['cargo']['path'], 'metadata', '--manifest-path', str(Path(admitted['root']) / 'project/Cargo.toml'),
            '--format-version', '1', '--filter-platform', 'wasm32-wasip1', '--offline', '--locked']


def environment(p, output, inherited):
    env = {k: inherited[k] for k in ['HOME', 'home', 'CODEX_HOME', 'USER', 'LOGNAME'] if k in inherited}
    env.update(PATH=str(Path(p['rustc']['path']).parent) + ':/usr/bin:/bin:/usr/sbin:/sbin',
        RUSTC=p['rustc']['path'], CARGO_HOME=str(output / 'cargo-home'), CARGO_TARGET_DIR=str(output / 'target'),
        TMPDIR=str(output / 'tmp'), CARGO_NET_OFFLINE='true', CARGO_NET_GIT_FETCH_WITH_CLI='false',
        CARGO_BUILD_JOBS='1', CARGO_INCREMENTAL='0', CARGO_NET_RETRY='2', LANG='C', LC_ALL='C',
        GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL='/dev/null', GIT_CONFIG_SYSTEM='/dev/null')
    return env


def ancestor_config_absence(cwd):
    values = []
    for parent in (Path(cwd), *Path(cwd).parents):
        for name in ['config', 'config.toml']:
            candidate = physical(parent / '.cargo' / name, exists=False)
            need(not candidate.exists() and not candidate.is_symlink(), 'unexpected ancestor Cargo configuration: ' + str(candidate))
            values.append(dict(path=str(candidate), absent=True))
    return values


def validate_stage_data(observed, p, admitted, entry, receipt, stdout):
    need(type(observed['schemaVersion']) is int and observed['schemaVersion'] == 1
         and observed['state'] == 'ROOT_LOCKED_CARGO_SOURCE_RESTORE_OBSERVED_V1'
         and type(observed['rawExitCode']) is int and observed['rawExitCode'] == 0
         and observed['preserved'] is observed['sourceOnly'] is True, 'actual Root Source-stage observation')
    need(observed['sourceIndex'] == p['restoreSourceIndex'] and observed['restoreReceipt'] == admitted['receipt']
         and observed['outputRoot'] == admitted['root'], 'stage/receipt/source exact joins')
    need(observed['restorerEntry'] == entry, 'actual stage entry')
    need(observed['inputConfig'] == {k: receipt['inputConfig'][k] for k in ['path', 'sha256', 'bytes']}, 'actual stage input config')
    need(observed['argv'] == [p['python']['path'], '-I', '-B', entry['path'], '--donors', observed['inputConfig']['path'],
                             '--output', admitted['root']], 'actual stage literal argv')
    need(observed['processEvidenceKind'] == 'exec_command terminal exit and raw streams; no monitor/OS-sandbox attestation', 'honest Source-stage process scope')
    need(all(observed[k] is None for k in ['actualCargoMetadata', 'actualNativeBuild', 'actualEngine', 'actualRuntime']), 'stage cannot project Cargo/build/runtime proof')
    need(stdout['passed'] is True and stdout['state'] == 'LOCKED_CARGO_SOURCES_RESTORED_UNCHECKED_BY_CARGO_V1'
         and stdout['outputRoot'] == admitted['root'] and stdout['error'] is stdout['finalProtectionError'] is None
         and all(stdout[k] is None for k in ['actualCargoMetadata', 'actualNativeBuild', 'actualEngine', 'actualRuntime']), 'actual stage stdout summary')
    return observed


def stage_observation(observation_ref, p, admitted):
    observed = read(observation_ref)
    verify(observed['inputConfig']); verify(observed['stderr'])
    return validate_stage_data(observed, p, admitted, module_ref(p['restoreSourceIndex'], 'restore.py'),
                               read(admitted['receipt']), read(observed['stdout']))


def authority(path):
    ar = row(physical(path)); a = read(ar); p = plan()
    need(type(a['schemaVersion']) is int and a['schemaVersion'] == 1 and a['state'] == 'ROOT_PORTABLE_CARGO_OFFLINE_METADATA_AUTHORIZED_V1'
         and a['unissued'] is False and a['cargoMetadataAllowed'] is True, 'issued Root metadata-only authority')
    for key in ['nativeCompilationAllowed', 'engineAllowed', 'guestAllowed', 'networkAllowed', 'rustupAllowed']:
        need(a[key] is False, 'restricted Root permission')
    need(a['sourceIndex'] == row(HERE / 'index.json') and a['plan'] == row(HERE / 'plan.json'), 'own Source/plan')
    family(a['sourceIndex'])
    need(row(Path(sys.executable).resolve()) == p['python'], 'pinned wrapper Python')
    need(a['restoreSourceIndex'] == p['restoreSourceIndex'], 'Root-selected restoration Source')
    need(a['restoreAdmissionSourceIndex'] == p['restoreAdmissionSourceIndex'], 'Root-selected corrected admission Source')
    need(isinstance(a['runId'], str) and re.fullmatch('[a-z0-9][a-z0-9-]{0,47}', a['runId']) is not None, 'safe runId')
    output = physical(p['outputPrefix'] + '-' + a['runId'], exists=False)
    admitted = admit_restore(p, a['restoreReceipt'])
    stage_observation(a['stageObservation'], p, admitted)
    root = Path(admitted['root'])
    need(output != root and output not in root.parents and root not in output.parents
         and output.parent.is_dir(), 'fresh external metadata output')
    need(a['command'] == invocation(p, admitted, output) and a['cwd'] == str(root / 'project'), 'Root literal metadata command/cwd')
    ancestor_config_absence(root / 'project')
    for key in ['cargo', 'rustc', 'python', 'monitor', 'lifecycle', 'referenceBundle', 'referencePayloadIndex']:
        verify(p[key])
    return ar, a, p, admitted, output


def source_guard(ar, a, p, before):
    need(read(ar) == a and row(HERE / 'plan.json') == a['plan'], 'Root/plan unchanged')
    family(a['sourceIndex']); family(p['restoreSourceIndex']); family(p['restoreAdmissionSourceIndex'])
    for ref in [p[k] for k in ['cargo', 'rustc', 'python', 'monitor', 'lifecycle', 'referenceBundle', 'referencePayloadIndex']]:
        verify(ref)
    after = admit_restore(p, a['restoreReceipt'])
    need(after == before, 'all restored payloads/physical identities/receipt unchanged')
    stage_observation(a['stageObservation'], p, after)
    ancestor_config_absence(Path(before['root']) / 'project')
    return after


def clean_outer(t):
    return (type(t['rawExitCode']) is int and t['rawExitCode'] == 0 and t['timeout'] is False
        and t['forcedCleanup'] is False and t['parentOwnedGroupGone'] is True and t['allObservedOwnedGroupsGone'] is True
        and all(t[k] == [] for k in ['errors', 'signals', 'interruptedSignals', 'remainingObservedPids'])
        and all(g['alive'] is False for g in t['finalGroups']))


def clean_inner(value):
    cleanup = value['ownedGroupCleanup']
    return (type(value['rawChildExitCode']) is int and value['rawChildExitCode'] == 0 and value['lifecycleComplete'] is True
        and value['stopReason'] is None and value['sigtermReceived'] == 0 and value['stoppedForDiskSpace'] is False
        and value['launcherErrors'] == [] and cleanup['complete'] is True and cleanup['events'] == cleanup['errors'] == [])


def capacity(path, floor):
    free = shutil.disk_usage(path).free
    need(free >= floor, 'metadata disk floor')
    return free


def packet(path):
    value = read(row(physical(path))); ar, a, p, admitted, output = authority(value['authority']['path'])
    need(value['authority'] == ar and physical(path) == output / 'packet.json', 'exact owned packet')
    need(value['argv'] == invocation(p, admitted, output) and value['cwd'] == str(Path(admitted['root']) / 'project')
         and value['environment'] == environment(p, output, os.environ), 'fixed offline command/environment')
    need(output.is_dir() and stat.S_IMODE(output.stat().st_mode) == 0o700, 'owned metadata output')
    return value, ar, a, p, admitted, output


def invoke(path):
    value, ar, a, p, admitted, output = packet(path)
    capacity(output, p['minimumPhaseFreeBytes'])
    need((output / 'cargo-home/config.toml').read_bytes() == verify(admitted['offlineCargoConfig']).read_bytes(), 'fresh copied config')
    with (output / 'metadata.stdout.json').open('xb') as out, (output / 'metadata.stderr.log').open('xb') as err:
        process = subprocess.run(value['argv'], cwd=value['cwd'], env=value['environment'], stdout=out, stderr=err)
        out.flush(); os.fsync(out.fileno()); err.flush(); os.fsync(err.fileno())
    save(output / 'cargo-status.json', dict(rawCargoExitCode=process.returncode))
    return 0 if process.returncode == 0 else 1


def worker(path):
    value, ar, a, p, admitted, output = packet(path)
    capacity(output, p['minimumPhaseFreeBytes'])
    lifecycle = load(p['lifecycle'], 'original_metadata_lifecycle')
    samples = []
    def free():
        value = shutil.disk_usage(output).free
        samples.append(value)
        return value
    with (output / 'lifecycle.log').open('xb') as log:
        result = lifecycle.monitor_owned_command([p['python']['path'], '-I', '-B', str(HERE / 'run.py'), '--invoke', str(path)],
            value['cwd'], value['environment'], log, free, minimum_free=p['minimumPhaseFreeBytes'])
        log.flush(); os.fsync(log.fileno())
    result['diskSamplesBytes'] = samples
    save(output / 'worker-result.json', result)
    return 0 if clean_inner(result) else 1


def run(authority_path):
    need(__debug__ and sys.dont_write_bytecode and sys.flags.isolated, 'Python -I -B with assertions')
    ar, a, p, admitted, output = authority(authority_path)
    need(not output.exists() and not output.is_symlink(), 'fresh output, no reuse')
    free = capacity(output.parent, p['minimumStartFreeBytes'])
    source_guard(ar, a, p, admitted)
    os.umask(0o077); output.mkdir(mode=0o700)
    result = dict(schemaVersion=1, state='PORTABLE_CARGO_OFFLINE_METADATA_FAILED_V1', passed=False,
        rootAuthority=ar, sourceIndex=a['sourceIndex'], plan=a['plan'], restoreSourceIndex=p['restoreSourceIndex'],
        restoreAdmissionSourceIndex=p['restoreAdmissionSourceIndex'],
        restoreReceipt=a['restoreReceipt'], commandKind='metadata', command=invocation(p, admitted, output),
        stageObservation=a['stageObservation'], actualLock=admitted['intlLockfile'], offlineCargoConfig=admitted['offlineCargoConfig'],
        cargo=p['cargo'], rustc=p['rustc'],
        operationSeconds=p['seconds'], freeBytesAtAdmission=free, rawCargoExitCode=None, errors=[],
        actualMetadata=None, audit=None, inputsPreserved=False, rustcInformationQueriesAllowed=True,
        observedRustcProcesses=[], processObservationIsSampled=True, sourceCompilationClaimed=False,
        nativeBuildOrGuestRequested=False, oldMetadataDescriptorsRetargeted=False)
    terminal = None
    try:
        result['sourceBefore'] = save(output / 'source-before.json', admitted)
        result['ancestorConfigsBefore'] = ancestor_config_absence(Path(admitted['root']) / 'project')
        for name in ['cargo-home', 'tmp', 'target', 'owned-monitor']:
            (output / name).mkdir(mode=0o700)
        config = verify(admitted['offlineCargoConfig']).read_bytes()
        fd = os.open(output / 'cargo-home/config.toml', os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
        with os.fdopen(fd, 'wb') as stream:
            stream.write(config); stream.flush(); os.fchmod(stream.fileno(), 0o600); os.fsync(stream.fileno())
        result['privateCargoConfig'] = row(output / 'cargo-home/config.toml')
        env = environment(p, output, os.environ)
        save(output / 'environment.json', dict(environment=env, inheritedNames=[k for k in ['HOME', 'home', 'CODEX_HOME', 'USER', 'LOGNAME'] if k in os.environ], operatingSystemHermeticityClaimed=False))
        packet_ref = save(output / 'packet.json', dict(authority=ar, argv=invocation(p, admitted, output), cwd=str(Path(admitted['root']) / 'project'), environment=env))
        monitor = load(p['monitor'], 'original_metadata_process_owner')
        terminal = monitor.monitor([p['python']['path'], '-I', '-B', str(HERE / 'run.py'), '--worker', packet_ref['path']],
            str(Path(admitted['root']) / 'project'), env, output / 'owned-monitor', p['seconds'], ar)
        status = read(row(output / 'cargo-status.json'))
        result['rawCargoExitCode'] = status['rawCargoExitCode']
        need(type(status['rawCargoExitCode']) is int and status['rawCargoExitCode'] == 0 and clean_outer(terminal), 'raw0 original owner/command cleanup')
        need(clean_inner(read(row(output / 'worker-result.json'))), 'original lifecycle cleanup/floor')
        metadata = read(row(output / 'metadata.stdout.json'))
        result['audit'] = validate_metadata(metadata, admitted, p, output, reference_metadata(p))
        result['actualMetadata'] = row(output / 'metadata.stdout.json')
    except BaseException as error:
        result['errors'].append(dict(stage='operation-or-collection', type=type(error).__name__, message=str(error), traceback=traceback.format_exc()))
    finally:
        for name, filename in [('outerTerminal', 'owned-monitor/terminal.json'), ('outerStarted', 'owned-monitor/started.json'),
            ('outerStdout', 'owned-monitor/stdout.log'), ('outerStderr', 'owned-monitor/stderr.log'), ('workerResult', 'worker-result.json'),
            ('lifecycleLog', 'lifecycle.log'), ('cargoStatus', 'cargo-status.json'), ('metadataStdout', 'metadata.stdout.json'), ('metadataStderr', 'metadata.stderr.log')]:
            try:
                result[name] = row(output / filename) if (output / filename).exists() else None
            except BaseException as error:
                result['errors'].append(dict(stage='collect-' + name, type=type(error).__name__, message=str(error)))
        try:
            if terminal is not None:
                result['observedRustcProcesses'] = [x for x in terminal['observedProcesses'] if x['command'].split(' ', 1)[0] == p['rustc']['path']]
        except BaseException as error:
            result['errors'].append(dict(stage='collect-process-observations', type=type(error).__name__, message=str(error)))
        try:
            after = source_guard(ar, a, p, admitted)
            result['sourceAfter'] = save(output / 'source-after.json', after)
            result['ancestorConfigsAfter'] = ancestor_config_absence(Path(admitted['root']) / 'project')
            result['inputsPreserved'] = True
        except BaseException as error:
            result['errors'].append(dict(stage='final-source-tool-protection', type=type(error).__name__, message=str(error)))
        try:
            result['freeBytesAtFinalBoundary'] = capacity(output, p['minimumPhaseFreeBytes'])
        except BaseException as error:
            result['errors'].append(dict(stage='final-disk-floor', type=type(error).__name__, message=str(error)))
        try:
            result['acceptedOutputBytesBeforeResult'] = sum(f.stat().st_size for f in output.rglob('*') if f.is_file())
            # Reserve bounded result bookkeeping before the exclusive pretty-JSON publication.
            result['outputCapSatisfied'] = result['acceptedOutputBytesBeforeResult'] + len(json.dumps(result, indent=2).encode()) + 1024 < p['maximumAcceptedOutputBytes']
            need(result['outputCapSatisfied'], 'postcapture output cap; raw files retained')
        except BaseException as error:
            result['errors'].append(dict(stage='output-cap', type=type(error).__name__, message=str(error)))
        result['passed'] = bool(result['audit'] and result['inputsPreserved'] and not result['errors'])
        if result['passed']:
            result['state'] = 'PORTABLE_CARGO_OFFLINE_METADATA_VERIFIED_V1'
        try:
            save(output / 'result.json', result)
        except BaseException as error:
            result['passed'] = False
            result['errors'].append(dict(stage='result-publication', type=type(error).__name__, message=str(error)))
        print(json.dumps(result), flush=True)
    return 0 if result['passed'] else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--run', type=Path)
    group.add_argument('--inspect-receipt', type=Path)
    group.add_argument('--worker', type=Path)
    group.add_argument('--invoke', type=Path)
    args = parser.parse_args()
    if args.run is not None:
        return run(args.run)
    if args.worker is not None or args.invoke is not None:
        need(__debug__ and sys.dont_write_bytecode and sys.flags.isolated, 'private worker Python -I -B')
        return worker(args.worker) if args.worker is not None else invoke(args.invoke)
    p = plan()
    if args.inspect_receipt is not None:
        family(row(HERE / 'index.json'))
        admitted = admit_restore(p, row(physical(args.inspect_receipt)))
        print(json.dumps(dict(sourceOnly=True, dataConsistent=True, root=admitted['root'], receipt=admitted['receipt'], cargoExecuted=False)))
    else:
        print(json.dumps(dict(sourceOnly=True, plan=p, cargoExecuted=False, actualMetadata=None)))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
