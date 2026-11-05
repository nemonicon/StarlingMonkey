"""Dormant fresh tool build: authenticated copies, private vendor cache, owned tools.

No adapter publication/pruning or application engine/component execution.
"""
from pathlib import Path
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
import time
import urllib.request

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
PROPOSAL = HERE.parent / 'clock-io-pruning-candidate-v1'
MONITOR = REPO / 'tests/node-compat/foundation-crypto/ownership-gc-build-controller-candidate-v1'
SOURCE = Path('/private/tmp/starling-node-compat/import-abi-clock-io-v1-source')
WORK = Path('/private/tmp/starling-node-compat/import-abi-clock-io-v1-build')
PACKAGE = Path('/private/tmp/starling-node-compat/import-abi-clock-io-v1-package')
EXTERNAL = Path('/private/tmp/starling-node-compat/import-abi-clock-io-v1-build-external-root')
SOURCE_SHA = '55338bc0e5e0f47ed473ccd283ed1eae70183f081abb8f6a61e5c8001711945f'
FLOOR = 800 * 1024 * 1024


def need(value, message):
    if not value:
        raise ValueError(message)


def row(path):
    path = Path(path)
    need(path.is_absolute() and '..' not in path.parts and not path.is_symlink(), 'ordinary absolute file')
    before = path.stat()
    need(stat.S_ISREG(before.st_mode), 'regular input')
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for data in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            digest.update(data)
    after = path.stat()
    identity = lambda s: (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns)
    need(identity(before) == identity(after), 'stable input')
    return dict(path=str(path), sha256=digest.hexdigest(), bytes=after.st_size)


def verify(value):
    need(type(value) is dict and set(value) == {'path', 'sha256', 'bytes'}, 'exact descriptor')
    need(row(value['path']) == value, 'exact current bytes')
    return Path(value['path'])


def read(value):
    need(value['bytes'] <= 32 * 1024 * 1024, 'bounded JSON DATA')
    return json.loads(verify(value).read_bytes())


def family(value):
    index = read(value)
    base = Path(value['path']).parent
    names = {'index.json'}
    result = [value]
    for item in index['files']:
        name = local(item['path'])
        need(name not in names, 'unique member')
        names.add(name)
        descriptor = dict(item, path=str(base / name))
        verify(descriptor)
        result.append(descriptor)
    need(not any(p.is_symlink() for p in base.rglob('*')), 'no family symlinks')
    need({str(p.relative_to(base)) for p in base.rglob('*') if p.is_file()} == names, 'exact family')
    return result


def local(value):
    need(type(value) is str and value and not value.startswith('/') and '\\' not in value
         and '\0' not in value and all(p not in ('', '.', '..') for p in value.split('/')), 'local member')
    return value


def phase_model(root):
    need(root['schemaVersion'] == 1 and root['state'] == 'ROOT_REVIEWED_CLOCK_IO_TOOLS_BUILD_V1', 'issued Root build')
    need(root['phase'] == 'build-clock-io-tools' and root['sourceIndex']['sha256'] == SOURCE_SHA, 'exact phase/source')
    need(root['sourceRoot'] == str(SOURCE) and root['workRoot'] == str(WORK)
         and root['packageRoot'] == str(PACKAGE) and root['externalRoot'] == str(EXTERNAL), 'fresh exact roots')
    for name in ('stageAllowed', 'privateVendorAllowed', 'downloadThreeLockedArchivesAllowed', 'rustBuildAndUnitTestsAllowed', 'jcoToolPackagingAllowed'):
        need(root[name] is True, 'explicit phase operation '+name)
    for name in ('adapterPublicationAllowed', 'adapterPruningAllowed', 'nativeEngineBuildAllowed', 'applicationComponentAllowed',
                 'applicationGuestAllowed', 'keyOrCryptoAllowed', 'timingAllowed', 'sourcePromotionAllowed', 'operationalAdmission', 'runtimeAcceptanceClaim'):
        need(root[name] is False, 'no additional action '+name)
    need(root['deadlineSeconds'] == 7200 and root['cargoJobs'] == 1 and root['requiredStartFreeBytes'] == 2 * 1024**3, 'bounded resources')


def authorize(config_descriptor):
    need(__debug__ and sys.dont_write_bytecode and sys.flags.isolated, 'isolated assertions')
    need(not any(os.environ.get(name) for name in ('PYTHONPATH', 'PYTHONHOME', 'PYTHONOPTIMIZE', 'NODE_OPTIONS', 'NODE_PATH',
         'LD_PRELOAD', 'LD_LIBRARY_PATH', 'DYLD_INSERT_LIBRARIES', 'DYLD_LIBRARY_PATH', 'RUSTC_WRAPPER', 'RUSTC_WORKSPACE_WRAPPER',
         'RUSTFLAGS', 'CARGO_ENCODED_RUSTFLAGS')), 'no inherited loader/compiler overrides')
    captured = {config_descriptor['path']: config_descriptor}
    def capture(value):
        verify(value)
        if value['path'] in captured:
            need(captured[value['path']] == value, 'consistent descriptor')
        captured[value['path']] = value
    def capture_family(value):
        for entry in family(value):
            capture(entry)
    config = read(config_descriptor)
    own = config['controllerIndex']
    need(own['path'] == str(HERE / 'index.json'), 'own original context')
    capture_family(own)
    root = read(config['rootAuthority'])
    capture(config['rootAuthority'])
    phase_model(root)
    need(root['controllerIndex'] == own and root['controllerEntry'] == row(Path(__file__).resolve()), 'actual caller bytes')
    source = root['sourceIndex']
    need(source['path'] == str(PROPOSAL / 'index.json'), 'genuine Source context')
    capture_family(source)
    for name, state, key in (
        ('sourceReview', 'INDEPENDENT_SCHEDULER_CLOCK_IO_PRUNING_SOURCE_REVIEW_PASSED_V1', 'sourceIndexSha256'),
        ('controllerReview', 'INDEPENDENT_CLOCK_IO_BUILD_CONTROLLER_SOURCE_REVIEW_PASSED_V1', 'controllerSourceIndexSha256')):
        pair = root[name]
        capture_family(pair['index'])
        proof = read(pair['result'])
        capture(pair['result'])
        need(proof['state'] == state and proof['sourceOnly'] is proof['sourceReviewPassed'] is True, 'separate Source peer')
        need(proof[key] == (source['sha256'] if name == 'sourceReview' else own['sha256']), 'exact peer subject')
        need(proof['ownerActionsInvoked'] is False, 'review action-free')
    inputs = read(row(PROPOSAL / 'source-inputs.json'))
    for entry in inputs['files']:
        capture(entry)
    monitor_index = row(MONITOR / 'index.json')
    need(monitor_index['sha256'] == '0afae87d0a1d7d32b272005cf6b252f9a318ed1799ff4c4605686c507d947f1b', 'genuine monitor source')
    capture_family(monitor_index)
    context = read(row(HERE / 'host-context.json'))
    for name in ('sdkSettings', 'hostLinkerDriver', 'appleLinker', 'wasmLinker', 'xcodeVersionPlist'):
        capture(context[name])
    settings = read(context['sdkSettings'])
    need(settings['Version'] == context['sdkVersion'] == '27.0' and settings['CanonicalName'] == context['sdkCanonicalName'], 'selected SDK')
    frame = dict(config=config, root=root, captured=captured, context=context,
                 tools=read(row(PROPOSAL / 'tool-cut-references.json')),
                 cut=read(row(PROPOSAL / 'source-cut.json')), plan=read(row(PROPOSAL / 'future-build-plan.json')))
    return frame


def recheck(frame):
    for value in frame['captured'].values():
        verify(value)
    for item in frame['tools']['jsToolchain']['symlinks']:
        path = Path(frame['tools']['jsToolchain']['root']) / item['path']
        need(path.is_symlink() and os.readlink(path) == item['target'] and str(path.resolve()) == item['resolved']['path'], 'unchanged JS alias')


def save(path, value):
    with Path(path).open('x') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())
    return row(path)


def space():
    need(shutil.disk_usage(WORK.parent).free >= FLOOR, '800MiB free-space floor')


def copy_file(value, destination, mode=0o600):
    space()
    source = verify(value)
    destination.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    with source.open('rb') as original, destination.open('xb') as target:
        shutil.copyfileobj(original, target, 4 * 1024 * 1024)
        target.flush()
        os.fsync(target.fileno())
    destination.chmod(mode)
    need(row(destination)['sha256'] == value['sha256'], 'copied bytes')
    need(destination.stat().st_nlink == 1 and (source.stat().st_dev, source.stat().st_ino) != (destination.stat().st_dev, destination.stat().st_ino), 'independent copy')
    return dict(source=value, destination=row(destination), mode=mode)


def archive_model(item):
    need(re.fullmatch('[A-Za-z0-9_-]+', item['name']) is not None, 'literal crate name')
    need(re.fullmatch('[0-9][A-Za-z0-9.+_-]*', item['version']) is not None, 'literal crate version')
    need(re.fullmatch('[a-f0-9]{64}', item['sha256']) is not None, 'locked checksum')


def vendor_archive(archive, item, vendor):
    archive_model(item)
    need(row(archive)['sha256'] == item['sha256'], 'locked archive checksum')
    prefix = item['name'] + '-' + item['version']
    target = vendor / prefix
    target.mkdir(mode=0o700)
    files = {}
    with tarfile.open(archive, 'r:*') as bundle:
        for member in bundle:
            space()
            need(member.name.startswith(prefix + '/'), 'one crate prefix')
            name = local(member.name[len(prefix) + 1:])
            path = target / name
            if member.isdir():
                path.mkdir(parents=True, exist_ok=True, mode=0o700)
                continue
            need(member.isfile() and name not in files and name != '.cargo-checksum.json', 'regular unique crate member')
            path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            with bundle.extractfile(member) as incoming, path.open('xb') as outgoing:
                shutil.copyfileobj(incoming, outgoing, 1024 * 1024)
            path.chmod(member.mode & 0o777)
            files[name] = row(path)['sha256']
    need('Cargo.toml' in files, 'real crate manifest')
    save(target / '.cargo-checksum.json', dict(files=files, package=item['sha256']))
    return dict(name=item['name'], version=item['version'], archive=row(archive), files=len(files))


def stage(frame):
    for path in (SOURCE, WORK, PACKAGE):
        need(not path.exists() and not path.is_symlink(), 'fresh output')
        path.mkdir(mode=0o700)
    need(shutil.disk_usage(WORK).free >= 2 * 1024**3, 'start at2GiB')
    tools, cut = frame['tools'], frame['cut']
    copies = []
    modes = {r['relativePath']: r['mode'] for r in cut['baseline']['files']}
    for item in cut['files']:
        source = item['baseline'] if item['origin'] == 'UNCHANGED_BASELINE' else dict(path=str(PROPOSAL / 'after' / local(item['path'])), sha256=item['sha256'], bytes=item['bytes'])
        copies.append(copy_file(source, SOURCE / local(item['path']), modes[item['path']]))
    need(len(cut['files']) == 271, 'exact271 source cut')
    for name in frame['plan']['packageSourceFiles']:
        copies.append(copy_file(row(SOURCE / local(name)), PACKAGE / name))
    for item in tools['jsToolchain']['files']:
        copies.append(copy_file(item['descriptor'], PACKAGE / local(item['relativePath']), item['mode']))
    for item in tools['jsToolchain']['symlinks']:
        destination = PACKAGE / local(item['path'])
        destination.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        destination.symlink_to(item['target'])
        need(destination.resolve().is_relative_to(PACKAGE) and row(destination.resolve())['sha256'] == item['resolved']['sha256'], 'private internal alias')
    vendor = WORK / 'vendor'
    vendor.mkdir(mode=0o700)
    downloads = WORK / 'locked-archives'
    downloads.mkdir(mode=0o700)
    archives = []
    for item in tools['lockedRegistryArchives']:
        value = item['descriptor']
        copy = downloads / (item['name'] + '-' + item['version'] + '.crate')
        copies.append(copy_file(value, copy))
        archives.append(dict(name=item['name'], version=item['version'], sha256=value['sha256'], path=copy))
    for item in tools['missingLockedRegistryArchives']:
        archive_model(item)
        url = 'https://static.crates.io/crates/{0}/{0}-{1}.crate'.format(item['name'], item['version'])
        path = downloads / (item['name'] + '-' + item['version'] + '.crate')
        with urllib.request.urlopen(url, timeout=60) as response, path.open('xb') as target:
            total = 0
            for block in iter(lambda: response.read(1024 * 1024), b''):
                total += len(block)
                need(total <= 16 * 1024 * 1024, 'bounded locked archive download')
                target.write(block)
            target.flush()
            os.fsync(target.fileno())
        need(row(path)['sha256'] == item['sha256'], 'exact downloaded locked crate')
        archives.append(dict(item, path=path, url=url))
    need(len(archives) == 121, '118cached plus3locked downloads')
    vendored = [vendor_archive(item['path'], item, vendor) for item in archives]
    cargo_home = WORK / 'cargo-home'
    cargo_home.mkdir(mode=0o700)
    config_text = '[source.crates-io]\nreplace-with = "private-vendor"\n[source.private-vendor]\ndirectory = ' + json.dumps(str(vendor)) + '\n[net]\noffline = true\n'
    with (cargo_home / 'config.toml').open('x') as stream:
        stream.write(config_text)
    return save(WORK / 'stage-receipt.json', dict(schemaVersion=1, sourceIndex=frame['root']['sourceIndex'], copies=copies,
                sources=271, jsToolFiles=4862, jsAliases=21, vendored=vendored, privateCargoHome=str(cargo_home),
                originalSourceOrCacheModified=False, allOutputsFresh=True, adapterPublished=False))


def raw_step(name, argv, environment, timeout):
    space()
    folder = WORK / 'commands' / local(name)
    folder.mkdir(parents=True, mode=0o700)
    start = time.monotonic()
    timed_out = False
    with (folder / 'stdout.log').open('xb') as stdout, (folder / 'stderr.log').open('xb') as stderr:
        try:
            result = subprocess.run(argv, cwd=SOURCE, env=environment, stdin=subprocess.DEVNULL,
                                    stdout=stdout, stderr=stderr, timeout=timeout, check=False)
            code = result.returncode
        except subprocess.TimeoutExpired:
            timed_out = True
            code = None
        stdout.flush()
        stderr.flush()
        os.fsync(stdout.fileno())
        os.fsync(stderr.fileno())
    terminal = dict(schemaVersion=1, argv=argv, cwd=str(SOURCE), rawExitCode=code, timedOut=timed_out,
                    timeoutSeconds=timeout, operationalSeconds=time.monotonic()-start,
                    stdout=row(folder/'stdout.log'), stderr=row(folder/'stderr.log'), streamsClipped=False,
                    diskFloorCheckedBeforeAndAfter=True, diskFloorMonitoredDuringCommand=False)
    terminal_row = save(folder / 'terminal.json', terminal)
    need(code == 0 and not timed_out, 'raw command zero '+name)
    space()
    return terminal_row


def worker(frame):
    os.umask(0o077)
    steps = []
    error = None
    stage_receipt = None
    try:
        stage_receipt = stage(frame)
        recheck(frame)
        tools = frame['tools']
        context = frame['context']
        environment = {**os.environ, 'PATH': str(Path(tools['cargo']['path']).parent)+os.pathsep+os.environ.get('PATH',''),
            'RUSTC': tools['rustc']['path'], 'RUSTDOC': tools['rustdoc']['path'], 'RUSTUP_TOOLCHAIN': '1.96.1-aarch64-apple-darwin',
            'CARGO_HOME': str(WORK/'cargo-home'), 'CARGO_BUILD_JOBS': '1', 'CARGO_INCREMENTAL': '0',
            'CARGO_TARGET_AARCH64_APPLE_DARWIN_LINKER': context['hostLinkerDriver']['path'],
            'CARGO_TARGET_WASM32_WASIP1_LINKER': context['wasmLinker']['path'], 'SDKROOT': context['sdkRoot']}
        for index, operation in enumerate(frame['plan']['commandPlans']):
            argv = operation['argv']
            if index < 2:
                argv = argv + ['--jobs', '1']
            steps.append(raw_step(operation['role'].lower(), argv, environment, 1800 if index < 2 else 600))
            recheck(frame)
            if index == 0:
                tests = [tools['cargo']['path'], 'test', '--locked', '--offline', '--release', '-p', 'spidermonkey-embedding-splicer', '--lib',
                         '--target', 'aarch64-apple-darwin', '--target-dir', str(WORK/'target'), '--jobs', '1', 'clock_io_policy_tests', '--', '--nocapture']
                steps.append(raw_step('new-rust-unit-tests', tests, environment, 1800))
                recheck(frame)
        for item in frame['cut']['files']:
            need(row(SOURCE/item['path'])['sha256'] == item['sha256'], 'source/cargo lock unchanged by tools')
        artifacts = [row(WORK/'target/aarch64-apple-darwin/release/splicer'), row(WORK/'target/wasm32-wasip1/release/splicer_component.wasm'), row(WORK/'splicer.wasm')]
        artifacts.extend(row(p) for p in sorted((PACKAGE/'lib').rglob('*')) if p.is_file())
    except BaseException as caught:
        error = dict(type=type(caught).__name__, detail=str(caught), partialRawEvidenceRetained=True)
        artifacts = []
    finally:
        try:
            recheck(frame)
            protected = True
        except BaseException as caught:
            protected = False
            error = dict(type=type(caught).__name__, detail='Final input protection failed: '+str(caught))
    need(WORK.is_dir(), 'build outcome location')
    result = dict(schemaVersion=1, state='CLOCK_IO_TOOLS_BUILD_COMPLETE_UNREVIEWED_V1' if error is None and protected else 'CLOCK_IO_TOOLS_BUILD_FAILED_UNACCEPTED_V1',
        sourceIndex=frame['root']['sourceIndex'], rootAuthority=frame['config']['rootAuthority'], stageReceipt=stage_receipt, commandTerminals=steps,
        artifacts=artifacts, error=error, protectedInputsRechecked=protected, adapterArtifactPublished=False, adapterPrunerExecuted=False,
        nativeEngineBuiltOrExecuted=False, applicationComponentConstructed=False, applicationGuestExecuted=False,
        independentArtifactReview=None, operationalAdmission=False, runtimeAcceptanceClaim=False)
    print(json.dumps(save(WORK/'result.json', result)), flush=True)
    return 0 if error is None and protected else 1


def parent(frame, config_descriptor):
    for path in (SOURCE, WORK, PACKAGE, EXTERNAL):
        need(not path.exists() and not path.is_symlink(), 'fresh operation roots')
    spec = importlib.util.spec_from_file_location('genuine_original_clock_build_monitor', MONITOR/'monitor.py')
    monitor = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(monitor)
    os.umask(0o077)
    EXTERNAL.mkdir(mode=0o700)
    argv = [sys.executable, '-B', '-I', str(HERE/'controller.py'), 'worker', json.dumps(config_descriptor,separators=(',',':'))]
    terminal = monitor.monitor(argv, str(REPO), {**os.environ,'PYTHONDONTWRITEBYTECODE':'1'}, EXTERNAL, 7200, frame['config']['rootAuthority'])
    need(read(row(EXTERNAL/'terminal.json')) == terminal, 'durable genuine terminal')
    recheck(frame)
    need(terminal['rawExitCode'] == 0 and terminal['allObservedOwnedGroupsGone'] is True
         and terminal['timeout'] is terminal['forcedCleanup'] is False and terminal['signals'] == []
         and terminal['errors'] == [] and terminal['remainingObservedPids'] == [], 'clean owned build')
    print(json.dumps(terminal), flush=True)
    return 0


def main():
    need(len(sys.argv) == 3 and sys.argv[1] in ('parent','worker'), 'exact CLI')
    descriptor = json.loads(sys.argv[2])
    frame = authorize(descriptor)
    try:
        return parent(frame,descriptor) if sys.argv[1] == 'parent' else worker(frame)
    finally:
        recheck(frame)


if __name__ == '__main__':
    raise SystemExit(main())
