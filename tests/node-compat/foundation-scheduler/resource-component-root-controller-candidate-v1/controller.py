"""Dormant fixture-specific Root construction controller; no import-time action."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import sys

HERE = Path(__file__).resolve().parent
S = HERE.parent
REPO = S.parents[2]
SOURCE = S / 'resource-component-candidate-v1'
SOURCE_SHA = '74413aa9d1520139dc2ac4d8e43f0d99bab06477b8d8eb6e9d2db6bb58580055'
PEER = S / 'independent-resource-component-source-review-v1'
PEER_SHA = 'dc452069b619be3a50dbf3bf71ba9487fe39194637da1dcb60806516a21fe02c'
MONITOR = S.parent / 'foundation-crypto/ownership-gc-build-controller-candidate-v1'
MONITOR_SHA = '0afae87d0a1d7d32b272005cf6b252f9a318ed1799ff4c4605686c507d947f1b'
OUTPUT_BASE = Path('/private/tmp/starling-node-compat/scheduler-resource-component-v1')
FIXTURES = ('resource', 'pure', 'fatal', 'init-fatal')


def row(path):
    path = Path(path)
    assert path.is_absolute() and '..' not in path.parts
    assert not any(p.is_symlink() for p in [path, *path.parents])
    before = path.stat()
    assert stat.S_ISREG(before.st_mode)
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            digest.update(block)
    after = path.stat()
    assert (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns) == (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns)
    return dict(path=str(path), sha256=digest.hexdigest(), bytes=after.st_size)


def checked(value):
    assert row(value['path']) == {k: value[k] for k in ('path', 'sha256', 'bytes')}
    return Path(value['path'])


def load(value):
    assert value['bytes'] <= 32 * 1024 * 1024
    return json.loads(checked(value).read_bytes())


def family(path, sha):
    descriptor = row(path)
    assert descriptor['sha256'] == sha
    value = load(descriptor)
    assert value['schemaVersion'] == 1 and 0 < len(value['files']) <= 2048
    root, names = Path(path).parent, set()
    for item in value['files']:
        name = item['path']
        assert isinstance(name, str) and name and not name.startswith('/') and '\\' not in name and '\0' not in name
        assert all(p not in ('', '.', '..') for p in name.split('/')) and name not in names
        names.add(name)
        checked(dict(item, path=str(root / name)))
    assert not any(p.is_symlink() for p in root.rglob('*'))
    assert {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()} == names | {'index.json'}
    return descriptor


def write(path, value):
    with Path(path).open('x') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())
    return row(path)


def action_model(fixture):
    assert fixture in FIXTURES
    output = Path(str(OUTPUT_BASE) + '-' + fixture)
    return dict(fixture=fixture, outputRoot=str(output), externalRoot=str(output) + '-external-root', timeoutSeconds=2400)


def owned_clean(terminal):
    return terminal['allObservedOwnedGroupsGone'] is True and terminal['timeout'] is False and terminal['forcedCleanup'] is False and all(terminal[key] == [] for key in ['remainingObservedPids', 'errors', 'signals', 'interruptedSignals'])


def inventory(root):
    root = Path(root)
    if not root.exists():
        return dict(exists=False, files=[], failure=None)
    rows = []
    try:
        assert root.is_dir() and not root.is_symlink()
        paths = list(root.rglob('*'))
        assert len(paths) <= 1024
        for path in sorted(paths):
            assert not path.is_symlink()
            if path.is_dir():
                continue
            assert path.stat().st_size <= 64 * 1024 * 1024
            rows.append(row(path))
        return dict(exists=True, files=rows, failure=None)
    except Exception as error:
        return dict(exists=True, files=rows, failure=dict(type=type(error).__name__, partialObservation=True))


def main():
    assert __debug__ and sys.dont_write_bytecode and len(sys.argv) == 4
    source_sha, fixture, review_json = sys.argv[1:]
    model = action_model(fixture)
    own = family(HERE / 'index.json', source_sha)
    source = family(SOURCE / 'index.json', SOURCE_SHA)
    peer = dict(index=family(PEER / 'index.json', PEER_SHA), result=row(PEER / 'results.json'))
    proof = load(peer['result'])
    assert proof['sourceOnly'] is proof['sourceReviewPassed'] is True and proof['ownerActionsInvoked'] is False and proof['sourceIndexSha256'] == SOURCE_SHA
    review = json.loads(review_json)
    review_index = family(review['index']['path'], review['index']['sha256'])
    assert review_index == review['index']
    review_value = load(review['result'])
    members = load(review_index)['files']
    assert dict(review['result'], path=str(Path(review['result']['path']).relative_to(Path(review_index['path']).parent))) in members
    assert review_value['schemaVersion'] == 1 and review_value['state'] == 'INDEPENDENT_RESOURCE342_COMPONENT_ROOT_CONTROLLER_SOURCE_REVIEW_PASSED_V1'
    assert review_value['controllerSourceIndexSha256'] == source_sha and review_value['sourceOnly'] is review_value['sourceReviewPassed'] is True and review_value['ownerActionsInvoked'] is False
    refs = json.loads((SOURCE / 'references.json').read_bytes())
    checked(refs['node'])
    for key in ['bootstrapConfig', 'bootstrapRootObservation', 'reviewedPins', 'rootPinReview']:
        checked(refs[key])
    prefix = 'resource-component-' + fixture + '-v1-root-'
    paths = {name: S / (prefix + name + '.json') for name in ['authority', 'config', 'results']}
    assert all(not p.exists() for p in [Path(model['outputRoot']), Path(model['externalRoot']), *paths.values()])
    authority = json.loads((SOURCE / 'future-root-authority.template.json').read_bytes())
    authority.update(state='ROOT_REVIEWED_SCHEDULER_RESOURCE342_COMPONENT_CONSTRUCTION_PHASE_V1', sourceIndexSha256=SOURCE_SHA, phase='construct-component', fixture=fixture, outputRoot=model['outputRoot'], sourceIndependentReview=peer, componentConstructionAllowed=True, externalController=row(Path(__file__).resolve()), externalControllerSourceIndex=own, externalControllerSourceReview=review, outerTimeoutSeconds=2400)
    for key in ['bootstrapConfig', 'bootstrapRootObservation', 'reviewedPins', 'rootPinReview']:
        authority[key] = refs[key]
    root_row = write(paths['authority'], authority)
    config = dict(schemaVersion=1, sourceIndexSha256=SOURCE_SHA, rootAuthority=root_row)
    config_row = write(paths['config'], config)
    # The only custom Python import is the complete authenticated original
    # generic owned-process monitor. Its context/globals remain unchanged.
    monitor_index = family(MONITOR / 'index.json', MONITOR_SHA)
    spec = importlib.util.spec_from_file_location('genuine_resource_component_outer_monitor', MONITOR / 'monitor.py')
    monitor = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(monitor)
    blocked = ['PYTHONOPTIMIZE', 'PYTHONPATH', 'PYTHONHOME', 'NODE_OPTIONS', 'NODE_PATH', 'DYLD_INSERT_LIBRARIES', 'DYLD_LIBRARY_PATH', 'LD_PRELOAD', 'LD_LIBRARY_PATH', 'NAPI_RS_NATIVE_LIBRARY_PATH', 'NAPI_RS_FORCE_WASI', 'NAPI_RS_WASI_FLAVOR', 'NAPI_RS_ENFORCE_VERSION_CHECK', 'NODE_COMPAT_LEGACY_COMPONENTIZER']
    environment = {k: v for k, v in os.environ.items() if k not in blocked}
    environment.update(PYTHONDONTWRITEBYTECODE='1', NODE_COMPAT_TOOLCHAIN=refs['toolchainRoot'], NODE_COMPAT_COMPONENTIZE_MODULE=refs['packagerRoot'] + '/src/componentize.js')
    argv = [refs['node']['path'], str(SOURCE / 'entry.mjs'), SOURCE_SHA, 'construct', json.dumps(config_row, separators=(',', ':'))]
    output = Path(model['externalRoot'])
    output.mkdir(mode=0o700)
    terminal = monitor.monitor(argv, str(REPO), environment, output, model['timeoutSeconds'], root_row)
    for key in ['stdout', 'stderr']:
        checked(terminal[key])
    assert terminal['authority'] == root_row
    capture = inventory(model['outputRoot'])
    records, parse_errors = [], []
    for number, line in enumerate(Path(terminal['stdout']['path']).read_bytes().splitlines(), 1):
        try:
            records.append(json.loads(line))
        except (ValueError, UnicodeDecodeError):
            parse_errors.append(number)
    final = records[-1] if records and isinstance(records[-1], dict) else None
    publications = {}
    if final is not None and final.get('root') == model['outputRoot']:
        for key in ['index', 'completion']:
            value = final.get(key)
            if isinstance(value, dict) and value.get('path') == key + '.json':
                descriptor = dict(value, path=str(Path(model['outputRoot']) / value['path']))
                checked(descriptor)
                publications[key] = descriptor
    clean = owned_clean(terminal)
    success = terminal['rawExitCode'] == 0 and clean and not parse_errors and capture['failure'] is None and len(publications) == 2
    summary = dict(schemaVersion=1, state='ROOT_OBSERVED_RESOURCE342_COMPONENT_CONSTRUCTION_RAW_ZERO_UNREVIEWED_V1' if success else 'ROOT_OBSERVED_RESOURCE342_COMPONENT_CONSTRUCTION_FAILURE_NO_ACCEPTANCE_V1', fixture=fixture, sourceIndex=source, sourceReview=peer, controllerSourceIndex=own, controllerSourceReview=review, monitorSourceIndex=monitor_index, rootAuthority=root_row, config=config_row, externalTerminal=row(output / 'terminal.json'), rawExitCode=terminal['rawExitCode'], cleanOwnedTermination=clean, stdout=terminal['stdout'], stderr=terminal['stderr'], stdoutJsonRecords=len(records), stdoutNonJsonLineNumbers=parse_errors, originalLastStdoutRecord=final, absolutePublications=publications, actualOutputInventory=capture, constructionRawZeroObserved=success, ordinaryGuestExportsInvoked=False, generatedModuleImported=False, timerRuntimeInvoked=False, operationalAdmission=False, runtimeAcceptanceClaim=False)
    report = write(paths['results'], summary)
    for value in [root_row, config_row]:
        checked(value)
    family(HERE / 'index.json', source_sha)
    family(SOURCE / 'index.json', SOURCE_SHA)
    family(PEER / 'index.json', PEER_SHA)
    family(MONITOR / 'index.json', MONITOR_SHA)
    print(json.dumps(dict(result=report, rawExitCode=terminal['rawExitCode'], constructionRawZeroObserved=success)), flush=True)
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
