"""Current genuine DATA + tiny Source-only fixtures. No tool/build/runtime action."""
from pathlib import Path
import ast
import copy
import importlib.util
import json
import os
import tempfile

HERE = Path(__file__).absolute().parent
REPO = HERE.parents[4]
spec = importlib.util.spec_from_file_location('portable_cargo_selection_test', HERE / 'cargo-selection.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
checks = 0


def check(value):
    global checks
    checks += 1
    assert value is True


def refuses(call):
    global checks
    checks += 1
    try:
        call()
    except (ValueError, KeyError, TypeError, StopIteration, FileNotFoundError):
        return
    raise AssertionError('accepted negative Source DATA')


def policy():
    base = HERE.parent; q = base / 'native-cargo-offline-verify-root-results-v2'; inputs = m.Inputs()
    return dict(schemaVersion=1, helper=inputs.file(HERE / 'cargo-selection.py'),
      metadataResult=dict(path='/private/tmp/starling-node-compat/native-cargo-offline-metadata-first-relocated-v2/result.json', sha256='effebd8ecca53caed232b763fac151b67525a651e81dbfe030fc1a3a4dfbfd4b', bytes=10128),
      metadataArchive=inputs.file(q / 'metadata-output.tar.gz'), metadataArchiveIndex=inputs.file(q / 'payload-index.json'),
      rootLaunchProcess=inputs.file(q / 'launch-process.json'), rootLaunchStdout=inputs.file(q / 'launch.stdout.log'), rootLaunchStderr=inputs.file(q / 'launch.stderr.log'),
      verifierSourceIndex=inputs.file(base / 'native-cargo-offline-verify-v2/index.json'),
      producerSourceIndex=inputs.file(base / 'native-cargo-restore-v1/index.json'), admissionSourceIndex=inputs.file(base / 'native-cargo-restore-admission-v2/index.json'),
      baseManifest=inputs.file(base / 'spidermonkey-intl-build-v1/cargo-root-results-v1/base-source-manifest.json'),
      expectedLockSha256='dc098f33febee6952974705077140ff543ca37eb1cedad2e0b07496646c3bd61',
      expectedMetadataSha256='65544c7b180112e645902ff961db1198ea6d8699a78462cd6e935933ab3de08d', expectedPackages=84, expectedBaseFiles=21)


p = policy(); inputs = m.Inputs(); proof = m.Proof(inputs, p)
result = proof.read(p['metadataResult']); authority = {k: result[k] for k in ['cargo', 'rustc']}
source = json.loads(Path('/private/tmp/starling-node-compat/next-native-portable-build-preparation-v1-first/portable-selection.json').read_text())
# Parent independently authenticates the full825 selection. This helper joins
# the exact21 base projection across the supplied full role inventory.
selected = m.inspect(p['metadataResult'], source, authority, p, REPO)
check(selected['intlCargoAudit'] == p['metadataResult'])
check(selected['audit']['packageCount'] == 84 and len(selected['base21']) == 21)
check(all(r['nativeRole'] == 'native-policy-source' for r in selected['base21']))
check({k: sum(r['kind'] == 'file' for r in v['entries']) for k, v in selected['treeSnapshots'].items()} == {'intl-firefox': 1127, 'intl-vendor': 2354})
check(all(v['inventory'] is None and v['provenance'] == p['metadataArchive'] for v in selected['reusedTrees'].values()))
check(all(set(r) == {'path', 'sha256', 'bytes'} for r in selected['protectedInputs']))
check(not any(r['path'].startswith(proof.index['originalRoot'] + '/') for r in selected['protectedInputs']))
check(selected['nativeBuildOrGuestInvoked'] is False and selected['oldMetadataDescriptorsRetargeted'] is False)

# Exercise genuine pure validator against exact retained raw records, mutating
# DATA dictionaries only. No Root authority, packet or producer is executed.
verifier = inputs.load(inputs.member(p['verifierSourceIndex'], 'run.py'), 'retained_genuine_pure_verifier_test')
qp = inputs.read(inputs.member(p['verifierSourceIndex'], 'plan.json'))
admission = inputs.load(inputs.member(p['admissionSourceIndex'], 'admit.py'), 'retained_readonly_source_admission_test')
admitted = admission.admit_restore(result['restoreReceipt'])
root = Path(proof.index['originalRoot'])
check(m.validate_records(result, root, qp, admitted, proof, verifier, p['verifierSourceIndex'])['logicalGraphAndFeaturesMatch'])
for key, value in [('schemaVersion', True), ('passed', False), ('inputsPreserved', False), ('outputCapSatisfied', False),
                   ('rawCargoExitCode', 1), ('rawCargoExitCode', True), ('errors', ['x']), ('operationSeconds', 301),
                   ('restoreSourceIndex', {}), ('restoreAdmissionSourceIndex', {}), ('actualLock', {}),
                   ('commandKind', 'build'), ('sourceCompilationClaimed', True), ('command', ['unselected'])]:
    bad = dict(result, **{key: value})
    refuses(lambda: m.validate_records(bad, root, qp, admitted, proof, verifier, p['verifierSourceIndex']))


class ChangedProof:
    def __init__(self, target, value):
        self.target, self.value, self.inputs, self.data = target, value, proof.inputs, proof.data
    def read(self, ref):
        return self.value if ref['path'] == self.target else proof.read(ref)
    def ref(self, ref): return proof.ref(ref)
    def named(self, name): return proof.named(name)


for key, field, value in [('outerTerminal', 'interruptedSignals', [2]), ('outerTerminal', 'rawExitCode', True),
                          ('outerStarted', 'timeoutSeconds', 299), ('outerStarted', 'pid', -1),
                          ('workerResult', 'stopReason', 'disk-space-stop'), ('cargoStatus', 'rawCargoExitCode', 1),
                          ('rootAuthority', 'networkAllowed', True), ('rootAuthority', 'command', ['build'])]:
    bad = copy.deepcopy(proof.read(result[key])); bad[field] = value
    changed = ChangedProof(result[key]['path'], bad)
    refuses(lambda: m.validate_records(result, root, qp, admitted, changed, verifier, p['verifierSourceIndex']))
started = proof.read(result['outerStarted']); launch_raw = inputs.ref(p['rootLaunchStdout'])
check(m.launch_frames(launch_raw, started, result))
for raw in [launch_raw.split(b'\n', 1)[0], launch_raw + b'{}\n', b'\n' + launch_raw, launch_raw + b'\n', b'junk\n{}\n']:
    refuses(lambda: m.launch_frames(raw, started, result))

manifest = inputs.read(p['baseManifest'])
for mutation in ['missing', 'wrong-role', 'wrong-hash', 'wrong-size', 'duplicate']:
    value = copy.deepcopy(source); name = manifest['files'][0]['path']
    entry = next(r for r in value['files'] if r['path'] == name)
    if mutation == 'missing': value['files'].remove(entry)
    elif mutation == 'wrong-role': entry['role'] = 'build-support'
    elif mutation == 'wrong-hash': entry['sha256'] = '0' * 64
    elif mutation == 'wrong-size': entry['bytes'] += 1
    else:
        other = next(r for r in value['files'] if r['path'] != name and r['role'] == 'native-policy-source')
        other.update(entry)
    refuses(lambda: m.base_projection(value, manifest, admitted['baseRoot'], m.Inputs()))

# Only selection JSON and the21 tiny source text inputs are copied. No825tree,
# SDK, compiler, app, engine or binary is copied or invoked.
with tempfile.TemporaryDirectory(prefix='source-only-portable-cargo-', dir='/private/tmp') as temp:
    outer = Path(temp); output = outer / 'cargo'
    prepared = m.prepare(p['metadataResult'], source, authority, p, REPO, output=output)
    current = prepared['admitted']
    check({f.name for f in output.iterdir()} == {'cargo-selection.json', 'intl-firefox-inventory.json', 'intl-vendor-inventory.json'})
    check(all(v['provenance'] == p['metadataArchive'] for v in current['reusedTrees'].values()))
    extra = output / 'unknown.json'; extra.write_text('{}')
    refuses(lambda: m.admit(prepared['portableCargoSelection'], source, authority, p, REPO)); extra.unlink()
    refuses(lambda: m.prepare(p['metadataResult'], source, authority, p, REPO, output=output))
    work = outer / 'work-native'; work.mkdir(mode=0o700)
    for r in current['base21']:
        dst = work / r['relativePath']; dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(Path(r['source']['path']).read_bytes()); dst.chmod(0o600)
    check(m.verify_work_base(current, work)['baseFiles'] == 21)
    target = work / current['base21'][0]['relativePath']; before = target.read_bytes()
    target.write_bytes(before + b'\n'); refuses(lambda: m.verify_work_base(current, work)); target.write_bytes(before)
    target.chmod(0o644); refuses(lambda: m.verify_work_base(current, work)); target.chmod(0o600)
    alias = outer / 'alias'; alias.symlink_to(work); refuses(lambda: m.verify_work_base(current, alias))
    check(m.verify_work_base(current, work)['exactBytesAndModes'])

for name in ['cargo-selection.py', 'test-cargo-selection.py']:
    ast.parse((HERE / name).read_text()); checks += 1
print(json.dumps(dict(passed=True, helperDataChecks=checks, currentGenuineMetadataProofRead=True,
    selectedBaseFiles=21, fullPortableRoleFiles=825, tinySelectionAndBaseFixturesRemoved=True,
    noCargoRestorerProducerMonitorCompilerBuildOrGuestInvoked=True)))
