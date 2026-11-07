"""Read-only Cargo proof admission; explicit prepare writes three selection JSONs.
No Cargo, restorer producer, monitor, compiler, build, or runtime is invoked.
"""
from pathlib import Path
import hashlib
import importlib.util
import json
import os
import re
import stat
import tarfile

HERE = Path(__file__).absolute().parent


def need(value, message):
    if value is not True:
        raise ValueError(message)


def canonical(value, exists=True):
    p = Path(value)
    need(p.is_absolute() and '..' not in p.parts and str(p) == str(value) and p.resolve() == p, 'canonical absolute path')
    for q in (p, *p.parents):
        need(not q.is_symlink(), 'path alias')
    need(not exists or p.exists(), 'missing path')
    return p


def identity(path):
    s = path.stat()
    return dict(dev=s.st_dev, ino=s.st_ino, mode=stat.S_IMODE(s.st_mode), nlink=s.st_nlink,
                mtimeNs=s.st_mtime_ns, ctimeNs=s.st_ctime_ns)


def same(left, right):
    return json.dumps(left, sort_keys=True, separators=(',', ':')) == json.dumps(right, sort_keys=True, separators=(',', ':'))


def launch_frames(raw, started, result):
    lines = raw.decode('utf8').splitlines()
    need(len(lines) == 2 and all(line.strip() for line in lines), 'exact two original launch JSONL frames')
    first, second = [json.loads(line) for line in lines]
    need(same(first, dict(pid=started['pid'], timeoutSeconds=300)) and same(second, result), 'launch monitor/result frames')
    return True


class Inputs:
    def __init__(self):
        self.refs = {}
        self.records = {}
        self.families = {}

    def file(self, path, expected=None):
        path = canonical(path); before = identity(path)
        need(path.is_file() and before['nlink'] == 1, 'regular single-link file')
        h = hashlib.sha256()
        with path.open('rb') as stream:
            for block in iter(lambda: stream.read(1048576), b''):
                h.update(block)
        ref = dict(path=str(path), sha256=h.hexdigest(), bytes=path.stat().st_size)
        need(identity(path) == before, 'input changed during read')
        if expected is not None:
            need(set(expected) == {'path', 'sha256', 'bytes'} and type(expected['bytes']) is int and same(ref, expected), 'file descriptor')
        if str(path) in self.refs:
            need(same(self.refs[str(path)], ref) and same(self.records[str(path)]['physical'], before), 'input changed across reads')
        self.refs[str(path)] = ref
        self.records[str(path)] = dict(ref, kind='file', physical=before)
        return ref

    def ref(self, ref):
        self.file(ref['path'], ref)
        return Path(ref['path']).read_bytes()

    def read(self, ref):
        need(ref['bytes'] <= 16 * 1048576, 'bounded JSON')
        return json.loads(self.ref(ref))

    def family(self, ref):
        index = self.read(ref); root = Path(ref['path']).parent; names, directories = set(), set()
        need(Path(ref['path']).name == 'index.json', 'family root index')
        for r in index['files']:
            rel = Path(r['path'])
            need(not rel.is_absolute() and '..' not in rel.parts and str(rel) == r['path'] and r['path'] not in names, 'confined unique Source member')
            names.add(r['path']); directories.update(str(x) for x in rel.parents if x != Path('.'))
            self.ref(dict(r, path=str(root / rel)))
        nodes = list(root.rglob('*'))
        need(not any(x.is_symlink() for x in nodes) and all(x.is_file() or x.is_dir() for x in nodes), 'Source aliases/special members')
        need({str(x.relative_to(root)) for x in nodes if x.is_file()} == names | {'index.json'}, 'exact Source files incl nested indices')
        need({str(x.relative_to(root)) for x in nodes if x.is_dir()} == directories, 'exact Source directories')
        self.families[ref['path']] = ref
        return index

    def member(self, index, name):
        rows = self.family(index)['files']; row = next(r for r in rows if r['path'] == name)
        return dict(row, path=str(Path(index['path']).parent / name))

    def load(self, ref, name):
        self.ref(ref)
        spec = importlib.util.spec_from_file_location(name, ref['path'])
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        return module

    def finish(self):
        for ref in list(self.families.values()):
            self.family(ref)
        for ref in list(self.refs.values()):
            self.file(ref['path'], ref)


class Proof:
    """Exact retained23-file DATA capsule; original path spellings are preserved."""
    def __init__(self, inputs, policy):
        self.inputs = inputs; self.index = inputs.read(policy['metadataArchiveIndex'])
        need(self.index['archive'] == policy['metadataArchive'] and self.index['originalFilesPreserved'] is True
             and self.index['pathsInPayloadsUnchanged'] is True, 'preserved actual query capsule')
        raw = inputs.ref(policy['metadataArchive'])
        self.rows = {r['member']: r['original'] for r in self.index['files']}
        need(len(self.rows) == len(self.index['files']) == 23, 'exact23 proof members')
        root = Path(self.index['originalRoot']); self.data = {}
        import io
        with tarfile.open(fileobj=io.BytesIO(raw), mode='r:gz') as archive:
            for m in archive:
                path = Path(m.name)
                need(m.isfile() and not path.is_absolute() and '..' not in path.parts and str(path) == m.name
                     and m.name in self.rows and m.name not in self.data, 'safe unique proof member')
                expected = self.rows[m.name]
                need(expected['path'] == str(root / path) and m.size == expected['bytes'], 'original proof role')
                value = archive.extractfile(m).read()  # Metadata DATA only, never extract to filesystem.
                need(len(value) == expected['bytes'] and hashlib.sha256(value).hexdigest() == expected['sha256'], 'proof member bytes')
                self.data[m.name] = value
        need(set(self.data) == set(self.rows) and sum(len(x) for x in self.data.values()) == self.index['rawLogicalBytes'] == 4351460, 'whole proof payload')
        self.origins = {r['path']: name for name, r in self.rows.items()}
        need(len(self.origins) == 23, 'unique original proof paths')

    def ref(self, ref):
        if ref['path'] not in self.origins:
            return self.inputs.ref(ref)
        name = self.origins[ref['path']]
        need(same(self.rows[name], ref), 'exact archived descriptor')
        return self.data[name]

    def read(self, ref):
        return json.loads(self.ref(ref))

    def named(self, name):
        need(name in self.data, 'required original raw proof')
        return json.loads(self.data[name])


def snapshot(root):
    root = canonical(root); rows = []
    need(root.is_dir(), 'tree root')
    for p in sorted(root.rglob('*')):
        canonical(p); info = identity(p)
        r = dict(path=str(p.relative_to(root)), mode=info['mode'], dev=info['dev'], ino=info['ino'],
                 nlink=info['nlink'], mtimeNs=info['mtimeNs'])
        if p.is_dir():
            r['kind'] = 'directory'
        else:
            need(p.is_file() and info['nlink'] == 1, 'tree regular member')
            h = hashlib.sha256(p.read_bytes()).hexdigest()
            r.update(kind='file', sha256=h, bytes=p.stat().st_size)
        rows.append(r)
    root_info = identity(root)
    return dict(root=str(root), rootIdentity={k: root_info[k] for k in ['mode', 'dev', 'ino', 'nlink', 'mtimeNs']}, entries=rows)


def base_projection(source_selection, manifest, restored_root, inputs):
    need(len(source_selection['files']) == 825 and source_selection['roleCounts'] ==
         {'native-policy-source': 435, 'build-support': 387, 'componentize-embedding': 3}, 'full portable825 role cohort')
    need(len(manifest['files']) == 21, 'exact base21 manifest')
    rows = []
    for expected in manifest['files']:
        name = expected['path']; rel = Path(name)
        need(not rel.is_absolute() and '..' not in rel.parts and str(rel) == name, 'base relative path')
        matches = [r for r in source_selection['files'] if r['path'] == name and r['role'] in ['native-policy-source', 'build-support']]
        need(len(matches) == 1, 'unique full-selection base role')
        selected = matches[0]
        need(selected['role'] == 'native-policy-source' and selected['sha256'] == expected['sha256'] and selected['bytes'] == expected['bytes'], 'base21 selected role/content')
        ref = dict(path=str(Path(source_selection['sourceRoot']) / rel), sha256=expected['sha256'], bytes=expected['bytes'])
        inputs.ref(ref)
        restored = dict(ref, path=str(Path(restored_root) / rel)); inputs.ref(restored)
        rows.append(dict(relativePath=name, sha256=expected['sha256'], bytes=expected['bytes'], nativeRole=selected['role'], source=ref, restored=restored))
    need(len({r['relativePath'] for r in rows}) == 21, 'unique base21')
    return sorted(rows, key=lambda r: r['relativePath'])


def validate_records(result, root, query_plan, admitted, proof, verifier, source_index):
    need(type(result['schemaVersion']) is int and result['schemaVersion'] == 1 and result['state'] == 'PORTABLE_CARGO_OFFLINE_METADATA_VERIFIED_V1'
         and result['passed'] is result['inputsPreserved'] is result['outputCapSatisfied'] is True
         and result['errors'] == [] and type(result['rawCargoExitCode']) is int and result['rawCargoExitCode'] == 0, 'actual successful metadata result')
    need(result['sourceIndex'] == source_index and result['restoreSourceIndex'] == admitted['sourceIndex']
         and result['restoreAdmissionSourceIndex'] == admitted['admissionSourceIndex']
         and result['restoreReceipt'] == admitted['receipt'] and result['actualLock'] == admitted['intlLockfile']
         and result['offlineCargoConfig'] == admitted['offlineCargoConfig'], 'actual Source/restore/lock/config joins')
    need(result['commandKind'] == 'metadata' and result['operationSeconds'] == 300
         and result['oldMetadataDescriptorsRetargeted'] is result['sourceCompilationClaimed'] is result['nativeBuildOrGuestRequested'] is False, 'metadata-only scope')
    need(result['command'] == verifier.invocation(query_plan, admitted, root), 'literal metadata argv')
    auth = proof.read(result['rootAuthority'])
    need(auth['state'] == 'ROOT_PORTABLE_CARGO_OFFLINE_METADATA_AUTHORIZED_V1' and auth['unissued'] is False
         and auth['cargoMetadataAllowed'] is True and auth['sourceIndex'] == source_index
         and auth['plan'] == result['plan'] and auth['restoreSourceIndex'] == admitted['sourceIndex']
         and auth['restoreAdmissionSourceIndex'] == admitted['admissionSourceIndex'] and auth['restoreReceipt'] == admitted['receipt']
         and auth['stageObservation'] == result['stageObservation'] and auth['command'] == result['command']
         and auth['cwd'] == str(Path(admitted['root']) / 'project'), 'genuine Root metadata authority')
    need(all(auth[k] is False for k in ['nativeCompilationAllowed', 'engineAllowed', 'guestAllowed', 'networkAllowed', 'rustupAllowed']), 'Root permission restriction')
    need(isinstance(auth['runId'], str) and re.fullmatch('[a-z0-9][a-z0-9-]{0,47}', auth['runId']) is not None
         and str(root) == query_plan['outputPrefix'] + '-' + auth['runId'], 'actual query namespace')
    stage = proof.read(result['stageObservation']); entry = proof.inputs.member(admitted['sourceIndex'], 'restore.py')
    receipt = proof.read(admitted['receipt']); stdout = proof.read(stage['stdout']); proof.ref(stage['stderr']); proof.ref(stage['inputConfig'])
    verifier.validate_stage_data(stage, query_plan, admitted, entry, receipt, stdout)
    before, after = proof.read(result['sourceBefore']), proof.read(result['sourceAfter'])
    need(same(before, after) and same(after, admitted), 'actual query bookends equal current full admission')
    terminal, started = proof.read(result['outerTerminal']), proof.read(result['outerStarted'])
    worker = proof.read(result['workerResult']); status = proof.read(result['cargoStatus'])
    need(verifier.clean_outer(terminal) and verifier.clean_inner(worker), 'original ownership/lifecycle cleanup')
    need(terminal['authority'] == started['authority'] == result['rootAuthority'] and terminal['pid'] == started['pid']
         and started['timeoutSeconds'] == 300, 'original started PID/authority/deadline')
    entry_ref = proof.inputs.member(source_index, 'run.py')
    need(started['argv'] == [query_plan['python']['path'], '-I', '-B', entry_ref['path'], '--worker', str(root / 'packet.json')], 'original owned verifier command')
    need(terminal['stdout'] == result['outerStdout'] and terminal['stderr'] == result['outerStderr'], 'outer stream roles')
    need(type(status['rawCargoExitCode']) is int and status['rawCargoExitCode'] == 0, 'original raw Cargo0')
    for key in ['outerStdout', 'outerStderr', 'lifecycleLog', 'metadataStdout', 'metadataStderr', 'privateCargoConfig']:
        proof.ref(result[key])
    need(result['actualMetadata'] == result['metadataStdout'] and result['metadataStderr']['bytes'] == 0, 'actual raw metadata/empty stderr')
    need(proof.ref(result['privateCargoConfig']) == proof.ref(admitted['offlineCargoConfig']), 'actual exact private config')
    owned = [json.loads(proof.data[n]) for n in sorted(proof.data) if re.fullmatch(r'owned-monitor/owned-[0-9]+\.json', n)]
    need([x['sequence'] for x in owned] == list(range(len(owned)))
         and {json.dumps(x['process'], sort_keys=True) for x in owned} == {json.dumps(x, sort_keys=True) for x in terminal['observedProcesses']}, 'complete original owned record inventory')
    packet = proof.named('packet.json'); env = proof.named('environment.json')['environment']
    inherited = {k: env[k] for k in ['HOME', 'home', 'CODEX_HOME', 'USER', 'LOGNAME'] if k in env}
    need(packet['authority'] == result['rootAuthority'] and packet['argv'] == result['command'] and packet['cwd'] == auth['cwd']
         and same(packet['environment'], env) and same(env, verifier.environment(query_plan, root, inherited)), 'actual private command/environment packet')
    need(result['freeBytesAtAdmission'] >= 512 * 1024**2 and result['freeBytesAtFinalBoundary'] >= 384 * 1024**2
         and worker['diskSamplesBytes'] and min(worker['diskSamplesBytes']) >= 384 * 1024**2, 'metadata-specific floors preserved')
    need(result['ancestorConfigsBefore'] == result['ancestorConfigsAfter'] == verifier.ancestor_config_absence(Path(admitted['root']) / 'project'), 'ancestor Cargo config absence')
    metadata = proof.read(result['actualMetadata'])
    audit = verifier.validate_metadata(metadata, admitted, query_plan, root, verifier.reference_metadata(query_plan))
    need(same(audit, result['audit']), 'independently recomputed exact84 graph/features/root6/fresh paths')
    return audit


def inspect(metadata_result_ref, source_selection, authority, policy, repo):
    repo = canonical(repo); inputs = Inputs()
    need(policy['schemaVersion'] == 1 and policy['expectedPackages'] == 84 and policy['expectedBaseFiles'] == 21, 'Cargo policy cohort')
    need(same(metadata_result_ref, policy['metadataResult']), 'Root-selected genuine metadata proof')
    need(Path(policy['helper']['path']) == HERE / 'cargo-selection.py', 'own helper Source context'); inputs.ref(policy['helper'])
    for key in ['verifierSourceIndex', 'producerSourceIndex', 'admissionSourceIndex']:
        inputs.family(policy[key])
    verifier = inputs.load(inputs.member(policy['verifierSourceIndex'], 'run.py'), 'genuine_metadata_verifier_pure_api')
    query_plan_ref = inputs.member(policy['verifierSourceIndex'], 'plan.json'); query_plan = inputs.read(query_plan_ref)
    need(query_plan['restoreSourceIndex'] == policy['producerSourceIndex'] and query_plan['restoreAdmissionSourceIndex'] == policy['admissionSourceIndex'], 'original producer vs read-only admission Source')
    admission = inputs.load(inputs.member(policy['admissionSourceIndex'], 'admit.py'), 'genuine_restored_cargo_read_only_api')
    proof = Proof(inputs, policy); result = proof.read(metadata_result_ref)
    need(result['plan'] == query_plan_ref and result['actualMetadata']['sha256'] == policy['expectedMetadataSha256'], 'authentic current metadata fields')
    admitted = admission.admit_restore(result['restoreReceipt'])
    need(admitted['state'] == 'RESTORED_CARGO_SOURCE_DATA_CONSISTENT_V2' and admitted['dataConsistent'] is True
         and admitted['sourceIndex'] == policy['producerSourceIndex'] and admitted['admissionSourceIndex'] == policy['admissionSourceIndex'], 'genuine current restore DATA admission')
    need(admitted['intlLockfile']['sha256'] == policy['expectedLockSha256'], 'exact84 lock bytes')
    for key in ['cargo', 'rustc']:
        need(authority[key] == result[key] == query_plan[key], 'selected actual Rust1.88 tool role'); inputs.ref(authority[key])
    for key in ['python', 'monitor', 'lifecycle', 'referenceBundle', 'referencePayloadIndex']:
        inputs.ref(query_plan[key])
    root = Path(proof.index['originalRoot'])
    need(metadata_result_ref['path'] == str(root / 'result.json'), 'original result capsule role')
    audit = validate_records(result, root, query_plan, admitted, proof, verifier, policy['verifierSourceIndex'])
    launch = inputs.read(policy['rootLaunchProcess'])
    need(type(launch['schemaVersion']) is int and launch['schemaVersion'] == 1
         and type(launch['rawExitCode']) is int and launch['rawExitCode'] == 0 and launch['commandKind'] == 'metadata'
         and launch['nativeBuildOrGuestRequested'] is False, 'original Root verifier launch0')
    need(launch['argv'] == [query_plan['python']['path'], '-I', '-B',
         inputs.member(policy['verifierSourceIndex'], 'run.py')['path'], '--run', result['rootAuthority']['path']], 'Root verifier launch argv')
    launch_frames(inputs.ref(policy['rootLaunchStdout']), proof.read(result['outerStarted']), result)
    need(inputs.ref(policy['rootLaunchStderr']) == b'', 'Root raw launch stderr')
    manifest = inputs.read(policy['baseManifest'])
    base = base_projection(source_selection, manifest, admitted['baseRoot'], inputs)
    trees = {'intl-firefox': snapshot(admitted['firefoxRoot']), 'intl-vendor': snapshot(admitted['vendorRoot'])}
    need(sum(r['kind'] == 'file' for r in trees['intl-firefox']['entries']) == 1127
         and sum(r['kind'] == 'file' for r in trees['intl-vendor']['entries']) == 2354, 'complete restored tree inventories')
    # Rehash external refs read via the proof reader, Source/tool/base inputs, then
    # repeat genuine whole restored-tree admission after snapshot construction.
    inputs.finish()
    need(same(admission.admit_restore(result['restoreReceipt']), admitted), 'final restored physical/content bookend')
    return dict(schemaVersion=1, state='PORTABLE_CARGO_INPUTS_DATA_CONSISTENT_V1', sourceOnly=True,
        metadataResult=metadata_result_ref, actualMetadata=result['actualMetadata'], actualRootAuthority=result['rootAuthority'],
        stageObservation=result['stageObservation'], restoreReceipt=result['restoreReceipt'],
        producerSourceIndex=policy['producerSourceIndex'], admissionSourceIndex=policy['admissionSourceIndex'],
        verifierSourceIndex=policy['verifierSourceIndex'], cargo=authority['cargo'], rustc=authority['rustc'],
        intlLockfile=admitted['intlLockfile'], offlineCargoConfig=admitted['offlineCargoConfig'], intlCargoAudit=metadata_result_ref,
        baseRoot=admitted['baseRoot'], firefoxRoot=admitted['firefoxRoot'], vendorRoot=admitted['vendorRoot'],
        nativeSourceRoot=source_selection['sourceRoot'], composition=source_selection['composition'],
        sourceMaterialization=source_selection['sourceMaterialization'], roleContentSha256=source_selection['roleContentSha256'],
        base21=base, treeSnapshots=trees, audit=audit,
        protectedInputs=sorted(inputs.refs.values(), key=lambda r: r['path']),
        physicalRecords=admitted['physicalRecords'] + sorted(inputs.records.values(), key=lambda r: r['path']),
        reusedTrees={k: dict(root=v['root'], inventory=None, provenance=policy['metadataArchive']) for k, v in trees.items()},
        nativeBuildOrGuestInvoked=False, oldMetadataDescriptorsRetargeted=False)


def selection_document(admitted, trees):
    keys = ['schemaVersion', 'state', 'sourceOnly', 'metadataResult', 'actualMetadata', 'actualRootAuthority',
            'stageObservation', 'restoreReceipt', 'producerSourceIndex', 'admissionSourceIndex', 'verifierSourceIndex',
            'cargo', 'rustc', 'intlLockfile', 'offlineCargoConfig', 'intlCargoAudit', 'baseRoot', 'firefoxRoot', 'vendorRoot',
            'nativeSourceRoot', 'composition', 'sourceMaterialization', 'roleContentSha256', 'base21', 'audit',
            'nativeBuildOrGuestInvoked', 'oldMetadataDescriptorsRetargeted']
    return {k: admitted[k] for k in keys} | {'reusedTrees': trees}


def admit(selection_ref, source_selection, authority, policy, repo):
    inputs = Inputs(); value = inputs.read(selection_ref); root = Path(selection_ref['path']).parent
    need(Path(selection_ref['path']).name == 'cargo-selection.json', 'selected Source DATA file')
    need(identity(root)['mode'] == 0o700 and identity(Path(selection_ref['path']))['mode'] == 0o600, 'private selected DATA ownership modes')
    need({str(p.relative_to(root)) for p in root.rglob('*') if p.is_file()} ==
         {'cargo-selection.json', 'intl-firefox-inventory.json', 'intl-vendor-inventory.json'}
         and not any(p.is_symlink() or not p.is_file() for p in root.rglob('*')), 'exact three selection files/no directories or aliases')
    current = inspect(value['metadataResult'], source_selection, authority, policy, repo)
    specs = {}
    for key in ['intl-firefox', 'intl-vendor']:
        ref = value['reusedTrees'][key]['inventory']
        need(ref['path'] == str(root / (key + '-inventory.json')), 'fresh selection inventory role')
        need(identity(Path(ref['path']))['mode'] == 0o600, 'private fresh inventory mode')
        need(same(inputs.read(ref), current['treeSnapshots'][key]), 'current fresh tree inventory')
        specs[key] = dict(root=current['treeSnapshots'][key]['root'], inventory=ref, provenance=policy['metadataArchive'])
    need(same(value, selection_document(current, specs)), 'explicit selection content/paths/tools/base21')
    inputs.finish()
    current['reusedTrees'] = specs
    merged = {r['path']: r for r in current['protectedInputs']}
    for ref in inputs.refs.values():
        need(ref['path'] not in merged or same(merged[ref['path']], ref), 'dedup selected descriptor')
        merged[ref['path']] = ref
    current['protectedInputs'] = sorted(merged.values(), key=lambda r: r['path'])
    current['physicalRecords'] += sorted(inputs.records.values(), key=lambda r: r['path'])
    current['portableCargoSelection'] = selection_ref
    return current


def write_new(path, value):
    data = (json.dumps(value, indent=2) + '\n').encode()
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(data); stream.flush(); os.fchmod(stream.fileno(), 0o600); os.fsync(stream.fileno())
    return Inputs().file(path)


def prepare(metadata_result_ref, source_selection, authority, policy, repo, output=None):
    current = inspect(metadata_result_ref, source_selection, authority, policy, repo)
    if output is None:
        return current
    output = canonical(output, exists=False)
    need(not output.exists() and not output.is_symlink() and output.parent.is_dir(), 'fresh owned selection directory')
    for root in [Path(repo), Path(source_selection['sourceRoot']).parent, Path(current['baseRoot']).parents[1],
                 Path(policy['metadataResult']['path']).parent]:
        need(output != root and root not in output.parents and output not in root.parents, 'selection/input separation')
    output.mkdir(mode=0o700); os.chmod(output, 0o700)
    specs = {}
    for key in ['intl-firefox', 'intl-vendor']:
        inventory = write_new(output / (key + '-inventory.json'), current['treeSnapshots'][key])
        specs[key] = dict(root=current['treeSnapshots'][key]['root'], inventory=inventory, provenance=policy['metadataArchive'])
    selected = write_new(output / 'cargo-selection.json', selection_document(current, specs))
    return dict(portableCargoSelection=selected, admitted=admit(selected, source_selection, authority, policy, repo))


def verify_work_base(admitted, workNativeRoot):
    root = canonical(workNativeRoot); inputs = Inputs(); rows = admitted['base21']
    need(len(rows) == 21 and len({r['relativePath'] for r in rows}) == 21, 'exact21 copied WORK inputs')
    for r in rows:
        rel = Path(r['relativePath'])
        need(not rel.is_absolute() and '..' not in rel.parts and str(rel) == r['relativePath'], 'WORK confined path')
        path = root / rel
        ref = dict(path=str(path), sha256=r['sha256'], bytes=r['bytes']); inputs.ref(ref)
        need(identity(path)['mode'] == 0o600 and identity(path)['nlink'] == 1, 'WORK base file mode/alias')
        for source in [r['source'], r['restored']]:
            inputs.ref(source)
            need((identity(path)['dev'], identity(path)['ino']) != (identity(Path(source['path']))['dev'], identity(Path(source['path']))['ino']), 'WORK copy must have distinct inode')
    inputs.finish()
    return dict(baseFiles=21, exactBytesAndModes=True, independentInodes=True, physicalRecords=list(inputs.records.values()))


if __name__ == '__main__':
    print(json.dumps(dict(sourceOnly=True, actualCargoSelection=None, actionsInvoked=False,
                          api=['inspect', 'prepare(output=None)', 'admit', 'verify_work_base'])))
