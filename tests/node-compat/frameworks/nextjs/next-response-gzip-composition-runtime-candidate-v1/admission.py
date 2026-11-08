"""Read-only admission/guards. No producer, constructor or runtime entrypoint calls."""
from pathlib import Path
import hashlib
import importlib.util
import json
import os
import stat

HERE = Path(__file__).resolve().parent
_model_spec = importlib.util.spec_from_file_location('gzip_pure_models', HERE / 'models.py')
_models = importlib.util.module_from_spec(_model_spec)
_model_spec.loader.exec_module(_models)
authority_shape, phase_grant, need, clean, ownership_clean = (
    _models.authority_shape, _models.phase_grant, _models.need, _models.clean, _models.ownership_clean)


def read(path):
    return json.loads(Path(path).read_bytes())


def row(path):
    path = Path(path)
    need(path.is_absolute() and path.resolve() == path and
         not any(p.is_symlink() for p in (path, *path.parents)), 'Canonical nonalias input')
    before = path.stat()
    need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1, 'Independent regular input')
    h, size = hashlib.sha256(), 0
    with path.open('rb') as source:
        for block in iter(lambda: source.read(4 * 1024**2), b''):
            h.update(block); size += len(block)
    after = path.stat()
    fields = ['st_dev', 'st_ino', 'st_mode', 'st_nlink', 'st_size', 'st_mtime_ns', 'st_ctime_ns']
    need(all(getattr(before, k) == getattr(after, k) for k in fields), 'Input read bookend')
    return dict(path=str(path), sha256=h.hexdigest(), bytes=size)


def verify(ref):
    need(type(ref) is dict and set(ref) == {'path', 'sha256', 'bytes'} and type(ref['bytes']) is int,
         'Exact descriptor')
    need(row(ref['path']) == ref, 'Input descriptor')


def family(ref):
    verify(ref); root = Path(ref['path']).parent; index = read(ref['path'])
    names = {r['path']: r for r in index['files']}
    need(len(names) == len(index['files']) and 'index.json' not in names, 'Unique Source names')
    expected_dirs = set()
    for name, item in names.items():
        rel = Path(name)
        need(not rel.is_absolute() and all(p not in ['', '.', '..'] for p in name.split('/')), 'Safe Source member')
        expected_dirs.update(p.as_posix() for p in rel.parents if p != Path('.'))
        verify(dict(item, path=str(root / rel)))
    nodes = list(root.rglob('*'))
    need(all(not p.is_symlink() and (p.is_file() or p.is_dir()) for p in nodes), 'Source aliases/specials')
    need({p.relative_to(root).as_posix() for p in nodes if p.is_file()} == set(names) | {'index.json'} and
         {p.relative_to(root).as_posix() for p in nodes if p.is_dir()} == expected_dirs, 'Closed Source family')


def load(ref, name):
    verify(ref)
    spec = importlib.util.spec_from_file_location(name, ref['path'])
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


def context(authority_path):
    p = read(HERE / 'plan.json')
    # Fail before output, tool hashing or dynamic imports while the Source cut is unbound.
    a = read(authority_path); layout = authority_shape(a, p)
    ar = row(authority_path)
    need(a['sourceIndex'] == row(HERE / 'index.json') and a['plan'] == row(HERE / 'plan.json'), 'Own Source pins')
    family(a['sourceIndex'])
    for ref in p['sourceFamilies']:
        family(ref)
    for ref in p['protectedInputs']:
        verify(ref)
    need(a['inputSourceIndex'] == p['probeSourceIndex'] and a['inputEntry'] == p['probeEntry'] and
         a['worldSourceIndex'] == p['worldSourceIndex'] and a['worldGuardImplementation'] == p['worldGuardImplementation'],
         'Probe and whole-world roles')
    for phase, key in [('reference', 'nodeReferenceAuthority'), ('wire', 'wireAuthority')]:
        verify(a[key]); phase_grant(read(a[key]['path']), phase, a)
    for ref in p['expectedBindings'].values():
        verify(ref)
    for ref in a['engineBuildEvidence'] + a['nativeProtectedInputs'] + a['worldInputs']:
        verify(ref)
    for ref in a['nativeSourceFamilies']:
        family(ref)
    return a, p, ar, layout


def native_guard(a, p):
    """Use the genuine full-build and world APIs, in their original contexts."""
    native = read(a['nativeMetadata']['path'])
    guard = load(p['fullBuildGuardImplementation'], 'genuine_gzip_full_native_guard')
    guard.protect_full_build(a, native)
    need(a['fullNativeBuildSourceIndex'] == p['requiredBuildSourceIndex'], 'Fresh required builder Source')
    compiled_authority = read(native['rootAuthority']['path'])
    verify(compiled_authority['plan']); build_plan = read(compiled_authority['plan']['path'])
    policy = build_plan['portableSourcePolicy']
    need(policy['materializerIndex']['sha256'] == p['requiredMaterializerIndex']['sha256'] and
         policy['roleContentSha256'] == p['requiredSourceRoleContentSha256'], 'Cleanup Mat6 Source policy')
    family(p['cleanupCorrectionSourceIndex'])
    version = read(Path(p['cleanupCorrectionSourceIndex']['path']).parent / 'version-manifest.json')
    selected = {r['path']: r for r in native['nativePolicyInputManifest']}
    for expected in [dict(relativePath=version['relativePath'], after=version['after']), *version['inheritedAfterimages']]:
        item = selected[expected['relativePath']]
        need(all(item[k] == expected['after'][k] for k in ['sha256', 'bytes']), 'Six selected cleanup inputs')
    need(selected[version['relativePath']]['sha256'] == p['requiredSelectedRequestResponseAfterimage']['sha256'], 'Corrected selected CPP')
    fixed = a['metadataExpectedFixedValues']
    need(type(fixed) is dict and {'schemaVersion', 'metadataKind', 'engine'} <= set(fixed) and
         fixed['engine'] == a['engine'] and all(native[k] == v for k, v in fixed.items()), 'Genuine whole metadata fixed fields')
    construction = read(a['constructionResult']['path']); ctor = read(construction['rootAuthority']['path'])
    verify(construction['rootAuthority']); verify(construction['plan']); cp = read(construction['plan']['path'])
    family(a['constructionCallerIndex'])
    need(construction['passed'] is True and construction['error'] is None and
         construction['entryMode'] == ctor['entryMode'] == 'gzip' and construction['finalProtection']['unchanged'] is True,
         'Fresh successful gzip INIT only')
    need(construction['callerIndex'] == a['constructionCallerIndex'] and construction['plan'] == a['constructionPlan'] and
         cp['inputSourceIndex'] == p['probeSourceIndex'] and cp['entries'] == {'gzip': p['probeEntry']}, 'Lifecycle constructor selector')
    need(cp['worldSourceIndex'] == p['worldSourceIndex'] and cp['selectedInterfaces'] == p['selectedInterfaces'], 'Ctor standard world')
    for key in ['engine', 'nativeMetadata', 'metadataExpectedFixedValues', 'engineBuildEvidence']:
        need(ctor[key] == a[key], 'Exact constructor ' + key)
    for key in ['component', 'componentAudit', 'engine', 'nativeMetadata', 'inputEntry', 'inputSourceIndex']:
        need(construction['artifacts'][key] == a[key], 'Exact constructed artifact ' + key)
    need(construction['artifacts']['adapter'] == p['adapter'], 'Unchanged selected Preview1 adapter')
    need(ctor['componentizeInitAllowed'] is True and all(ctor[k] is False for k in
         ['ordinaryExportsAllowed', 'httpServingAllowed', 'networkAllowed', 'nativeBuildAllowed', 'packageMutationAllowed',
          'globalPinMutationAllowed', 'debugAllowed', 'applicationMountAtInitAllowed', 'deployedResnapshotAllowed']), 'INIT permission boundary')
    review = read(a['constructionDataReview']['path'])
    need(review['state'] == p['prospectiveConstructorReviewState'] and review['verifiedPassed'] is True and
         review['completeReturnedImportAuditVerified'] is True, 'Complete actual returned-import review; no fixed function count')
    for key, value in dict(actualResult=a['constructionResult'], rootAuthority=construction['rootAuthority'],
        callerIndex=a['constructionCallerIndex'], plan=a['constructionPlan'], component=a['component'],
        componentAudit=a['componentAudit'], engine=a['engine'], nativeMetadata=a['nativeMetadata'],
        inputSourceIndex=p['probeSourceIndex'], inputEntry=p['probeEntry'], fullBuildReview=a['fullNativeBuildReview']).items():
        need(review[key] == value, 'Reviewed construction role ' + key)
    for key in ['ordinaryExportsInvoked', 'httpServed', 'appMountedAtInit', 'filesystemFixtureMountedAtInit',
                'deployedFetchProbeInvoked', 'runtimeAccepted', 'nodeParityProved', 'productionProfilePromoted']:
        need(review[key] is False, 'INIT-only review ' + key)
    audit = read(a['componentAudit']['path'])
    need(audit['passed'] is True and audit['entryMode'] == 'gzip' and audit['allEmittedVersion'] == '0.2.10' and
         audit['component'] == a['component'] and audit['engine'] == a['engine'] and audit['nativeMetadata'] == a['nativeMetadata'], 'Actual component audit')
    need(set(audit['emittedImports']) == set(p['selectedInterfaces']) and len(audit['emittedImports']) == len(set(audit['emittedImports'])) == 13 and
         audit['exports'] == ['wasi:http/incoming-handler@0.2.10'] and audit['noExternalPreview1OrCustomImports'] is True, 'Exact actual std13 audit')
    started = read(a['constructionRootStarted']['path']); terminal = read(a['constructionRootTerminal']['path'])
    need(clean(terminal) and started['pid'] == terminal['pid'] and started['timeoutSeconds'] == 2400 and
         started['authority'] == terminal['authority'] == construction['rootAuthority'], 'Original constructor outer owner')
    for key in ['stdout', 'stderr']:
        verify(terminal[key])
    need([r['label'] for r in construction['commands']] == ['componentize-init', 'component-validate', 'component-wit'], 'Three constructor phases')
    for command in construction['commands']:
        verify(command['terminal']); term = read(command['terminal']['path'])
        need(clean(term) and term['authority'] == construction['rootAuthority'] and command['rawExitCode'] == 0 and command['clean'] is True, 'Original inner owner')
        for key in ['stdout', 'stderr']:
            need(term[key] == command[key], 'Inner stream role'); verify(command[key])
    world = load(p['worldGuardImplementation'], 'genuine_gzip_world_guard')
    wa = dict(callerIndex=a['constructionCallerIndex'], newSourceEvidence=[p['probeSourceIndex'], *a['worldInputs']], worldSourceIndex=p['worldSourceIndex'])
    actual = world.world_guard(wa); old = read(a['constructionWorldGuard']['path'])
    need(old['unchanged'] is True and old['before'] == old['after'] == actual and
         actual['sourceIndex'] == p['worldSourceIndex'] and actual['members'] == 28 and actual['witFiles'] == 8, 'Whole-world before/after')
    return actual


def save(path, value, fresh=False):
    flags = os.O_WRONLY | os.O_CREAT | (os.O_EXCL if fresh else os.O_TRUNC) | os.O_NOFOLLOW
    fd = os.open(path, flags, 0o600)
    with os.fdopen(fd, 'wb') as target:
        target.write((json.dumps(value, indent=2) + '\n').encode()); target.flush(); os.fsync(target.fileno())
