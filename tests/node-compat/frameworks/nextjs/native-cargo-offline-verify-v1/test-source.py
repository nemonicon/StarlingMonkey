"""Inert Source/DATA tests; never invoke Cargo, monitor, worker, or restorer."""
from pathlib import Path
import ast
import copy
import importlib.util
import json
import os
import shutil
import tempfile

HERE = Path(__file__).absolute().parent
spec = importlib.util.spec_from_file_location('offline_metadata_source', HERE / 'run.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
p = m.plan(); checks = 0


def check(value):
    global checks
    checks += 1
    assert value is True


def refuses(call):
    global checks
    checks += 1
    try:
        call()
    except (ValueError, KeyError, TypeError, StopIteration):
        return
    raise AssertionError('Source predicate accepted negative DATA')


check(p['seconds'] == 300 and p['minimumStartFreeBytes'] == 512 * 1024**2 and p['minimumPhaseFreeBytes'] == 384 * 1024**2)
ref = m.reference_metadata(p)
check(len(m.graph(ref)) == 84)
root = Path('/source-only-example-not-created')
output = Path('/source-only-metadata-output-not-created')
admitted = dict(root=str(root), baseRoot=str(root / 'sources/base'), firefoxRoot=str(root / 'sources/firefox'), vendorRoot=str(root / 'vendor'))
check(m.invocation(p, admitted, output) == [p['cargo']['path'], 'metadata', '--manifest-path', str(root / 'project/Cargo.toml'), '--format-version', '1', '--filter-platform', 'wasm32-wasip1', '--offline', '--locked'])
check('build' not in m.invocation(p, admitted, output))
env = m.environment(p, output, dict(HOME='/retained-home', USER='retained-user', LOGNAME='retained-logname', home='/retained-lower', CODEX_HOME='/retained-codex', CARGO_HOME='/unselected', RUSTUP_HOME='/unselected', RUSTC_WRAPPER='/unselected'))
for key, value in [('HOME', '/retained-home'), ('USER', 'retained-user'), ('LOGNAME', 'retained-logname'), ('home', '/retained-lower'), ('CODEX_HOME', '/retained-codex')]:
    check(env[key] == value)
check(env['CARGO_HOME'] == str(output / 'cargo-home') and env['CARGO_TARGET_DIR'] == str(output / 'target') and env['TMPDIR'] == str(output / 'tmp'))
check('RUSTUP_HOME' not in env and 'RUSTC_WRAPPER' not in env)
check(env['CARGO_NET_OFFLINE'] == 'true' and env['CARGO_NET_GIT_FETCH_WITH_CLI'] == 'false' and env['CARGO_BUILD_JOBS'] == '1')
refuses(lambda: m.authority(HERE / 'root-authority.template.json'))

# Clearly synthetic path-ID transformations for function tests only; no fresh
# receipt/raw metadata/process result is manufactured or admitted.
meta = copy.deepcopy(ref)
ids = {x['id']: 'synthetic-package-' + str(i) for i, x in enumerate(meta['packages'])}
local = {'rust-staticlib': root / 'project', 'rust-encoding': Path(admitted['baseRoot']) / 'crates/rust-encoding',
 'rust-hooks': Path(admitted['baseRoot']) / 'crates/rust-hooks', 'rust-url': Path(admitted['baseRoot']) / 'crates/rust-url',
 'multipart': Path(admitted['baseRoot']) / 'crates/rust-multipart', 'icu_capi': Path(admitted['firefoxRoot']) / 'intl/icu_capi',
 'icu_segmenter_data': Path(admitted['firefoxRoot']) / 'intl/icu_segmenter_data', 'unicode-bidi-ffi': Path(admitted['firefoxRoot']) / 'intl/bidi/rust/unicode-bidi-ffi'}
for package in meta['packages']:
    package['id'] = ids[package['id']]
    parent = local[package['name']] if package['source'] is None else Path(admitted['vendorRoot']) / (package['name'] + '-' + package['version'])
    package['manifest_path'] = str(parent / 'Cargo.toml')
meta['resolve']['root'] = ids[meta['resolve']['root']]
for node in meta['resolve']['nodes']:
    node['id'] = ids[node['id']]
    node['dependencies'] = [ids[x] for x in node['dependencies']]
    for dep in node['deps']:
        dep['pkg'] = ids[dep['pkg']]
meta['workspace_root'] = str(root / 'project'); meta['target_directory'] = str(output / 'target')
check(m.graph(meta) == m.graph(ref))
check(m.validate_metadata(meta, admitted, p, output, ref)['logicalGraphAndFeaturesMatch'])
for mutation in ['missing-package', 'duplicate-id', 'version', 'feature', 'edge', 'manifest-path', 'target-directory', 'workspace-root', 'root-dependency', 'staticlib']:
    value = copy.deepcopy(meta)
    if mutation == 'missing-package': value['packages'].pop()
    elif mutation == 'duplicate-id': value['packages'][1]['id'] = value['packages'][0]['id']
    elif mutation == 'version': value['packages'][0]['version'] = '99.0.0'
    elif mutation == 'feature': value['resolve']['nodes'][0]['features'].append('unselected')
    elif mutation == 'edge': value['resolve']['nodes'][0]['deps'].append({'pkg': value['packages'][0]['id']})
    elif mutation == 'manifest-path': value['packages'][0]['manifest_path'] = '/old/source/Cargo.toml'
    elif mutation == 'target-directory': value['target_directory'] = '/old/target'
    elif mutation == 'workspace-root': value['workspace_root'] = '/old/project'
    else:
        root_package = next(x for x in value['packages'] if x['id'] == value['resolve']['root'])
        if mutation == 'root-dependency': root_package['dependencies'].pop()
        else: root_package['targets'][0]['crate_types'] = ['rlib']
    refuses(lambda: m.validate_metadata(value, admitted, p, output, ref))

outer = dict(rawExitCode=0, timeout=False, forcedCleanup=False, parentOwnedGroupGone=True,
 allObservedOwnedGroupsGone=True, errors=[], signals=[], interruptedSignals=[], remainingObservedPids=[], finalGroups=[{'alive': False}])
check(m.clean_outer(outer))
for key, value in [('rawExitCode', 1), ('rawExitCode', True), ('timeout', True), ('forcedCleanup', True), ('parentOwnedGroupGone', False), ('allObservedOwnedGroupsGone', False), ('errors', ['x']), ('signals', [15]), ('interruptedSignals', [2]), ('remainingObservedPids', [1]), ('finalGroups', [{'alive': True}])]:
    check(m.clean_outer(dict(outer, **{key: value})) is False)
inner = dict(rawChildExitCode=0, lifecycleComplete=True, stopReason=None, sigtermReceived=0,
 stoppedForDiskSpace=False, launcherErrors=[], ownedGroupCleanup={'complete': True, 'events': [], 'errors': []})
check(m.clean_inner(inner))
for key, value in [('rawChildExitCode', 1), ('rawChildExitCode', True), ('lifecycleComplete', False), ('stopReason', 'disk-space-stop'), ('sigtermReceived', 1), ('stoppedForDiskSpace', True), ('launcherErrors', ['x']), ('ownedGroupCleanup', {'complete': False, 'events': [], 'errors': []})]:
    check(m.clean_inner(dict(inner, **{key: value})) is False)

# Exercise the actual ancestor-config filesystem guard, using only a few tiny
# Source-test files. No restored tree, application, tool, or actor is copied.
with tempfile.TemporaryDirectory(prefix='source-only-cargo-config-', dir='/private/tmp') as folder:
    tmp = Path(folder); cwd = tmp / 'project'; cwd.mkdir(mode=0o700)
    check(len(m.ancestor_config_absence(cwd)) > 0)
    dot = tmp / '.cargo'; dot.mkdir(mode=0o700)
    for name in ['config', 'config.toml']:
        file = dot / name; file.write_text('# inert Source test\n')
        refuses(lambda: m.ancestor_config_absence(cwd)); file.unlink()
    dot.rmdir(); other = tmp / 'other'; other.mkdir(mode=0o700); dot.symlink_to(other)
    refuses(lambda: m.ancestor_config_absence(cwd)); dot.unlink()
    check(len(m.ancestor_config_absence(cwd)) > 0)

# Proposed Root stage wire is exercised as synthetic dictionaries only; these
# are not files, observed executions, restoration receipts, or future proofs.
entry = m.module_ref(p['restoreSourceIndex'], 'restore.py')
fake_ref = dict(path='/synthetic-not-created/restore-result.json', sha256='0' * 64, bytes=1)
fake_config = dict(path='/synthetic-not-created/donors.json', sha256='1' * 64, bytes=1)
stage_admission = dict(admitted, receipt=fake_ref)
stage = dict(schemaVersion=1, state='ROOT_LOCKED_CARGO_SOURCE_RESTORE_OBSERVED_V1', sourceIndex=p['restoreSourceIndex'],
 restorerEntry=entry, inputConfig=fake_config, restoreReceipt=fake_ref, outputRoot=admitted['root'],
 argv=[p['python']['path'], '-I', '-B', entry['path'], '--donors', fake_config['path'], '--output', admitted['root']],
 rawExitCode=0, preserved=True, sourceOnly=True, actualCargoMetadata=None, actualNativeBuild=None, actualEngine=None, actualRuntime=None,
 processEvidenceKind='exec_command terminal exit and raw streams; no monitor/OS-sandbox attestation')
receipt = dict(inputConfig=fake_config)
summary = dict(passed=True, state='LOCKED_CARGO_SOURCES_RESTORED_UNCHECKED_BY_CARGO_V1', outputRoot=admitted['root'],
 error=None, finalProtectionError=None, actualCargoMetadata=None, actualNativeBuild=None, actualEngine=None, actualRuntime=None)
check(m.validate_stage_data(stage, p, stage_admission, entry, receipt, summary) == stage)
for key, value in [('schemaVersion', True), ('rawExitCode', 1), ('rawExitCode', True), ('preserved', False), ('sourceOnly', False),
                   ('argv', ['unselected']), ('restoreReceipt', {}), ('sourceIndex', {}), ('inputConfig', {}),
                   ('outputRoot', '/old/root'), ('restorerEntry', {}), ('actualCargoMetadata', {})]:
    refuses(lambda: m.validate_stage_data(dict(stage, **{key: value}), p, stage_admission, entry, receipt, summary))
for key, value in [('passed', False), ('outputRoot', '/old/root'), ('error', False), ('actualCargoMetadata', {})]:
    refuses(lambda: m.validate_stage_data(stage, p, stage_admission, entry, receipt, dict(summary, **{key: value})))

# Genuine current Root stage wire, consumed as retained DATA only. Do not
# rerun restoration/admission/metadata here; the readback record pins its refs.
readback = json.loads((HERE / 'checks/admission-readback.json').read_text())
observed = m.read(readback['actualRootStageObservation'])
actual_receipt = m.read(readback['restoreReceipt'])
actual_summary = m.read(observed['stdout'])
actual_admission_roles = dict(root=readback['root'], receipt=readback['restoreReceipt'])
check(m.validate_stage_data(observed, p, actual_admission_roles, entry, actual_receipt, actual_summary) == observed)

# These are source joins to genuine APIs; no lifecycle or monitor call is run.
tree = ast.parse((HERE / 'run.py').read_text())
for name in ['run', 'worker', 'invoke', 'admit_restore', 'validate_metadata']:
    check(any(isinstance(n, ast.FunctionDef) and n.name == name for n in tree.body))
for file in ['run.py', 'test-source.py']: ast.parse((HERE / file).read_text()); checks += 1
check('minimum_free=p[\'minimumPhaseFreeBytes\']' in (HERE / 'run.py').read_text())
print(json.dumps(dict(passed=True, sourceDataChecks=checks, actualCargoOrRestorerOrMonitorInvoked=False,
 actualNewMetadata=None, syntheticMetadataUsedOnlyForFunctionTests=True, tinyConfigFixturesRemoved=True)))
