"""Explicit Linux CI guest-library build. Importing this module starts nothing.
Uses the existing owned-process and disk-floor controllers, not a host service.
"""
from pathlib import Path
import hashlib
import importlib.util
import json
import os
import shutil
import sys
import tarfile
import time
import traceback

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
COMMIT = '9dab3d6f643e926a340c391ea30968e940390dec'
SDK_URL = 'https://github.com/WebAssembly/wasi-sdk/releases/download/wasi-sdk-30/wasi-sdk-30.0-x86_64-linux.tar.gz'
SDK_SHA = '0507679dff16814b74516cd969a9b16d2ced1347388024bc7966264648c78bfb'
MONITOR = ('tests/node-compat/foundation-crypto/ownership-gc-build-controller-candidate-v1/monitor.py', '86913867251bc889701859ca6a361ccf9c17288a6a3bfc7a5c8d8e5bbe5c4cbe')
LIFECYCLE = ('tests/node-compat/foundation-scheduler/resource-build-controller-candidate-v1/lifecycle.py', '54557e22b4cd1c99cdc67c6dc8ff55826fae0d47a6b6481b72019c9480e5293d')
START_FREE = 20 * 1024**3
STOP_FREE = 4 * 1024**3


def descriptor(path):
    path = Path(path)
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(4 * 1024**2), b''):
            h.update(block)
    return dict(path=str(path), bytes=path.stat().st_size, sha256=h.hexdigest())


def save(path, value):
    with Path(path).open('x') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')


def utility(row, name):
    path = REPO / row[0]
    assert descriptor(path)['sha256'] == row[1]
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def worker(packet_path):
    packet = json.loads(Path(packet_path).read_text())
    out = Path(packet_path).parent
    life = utility(LIFECYCLE, 'intl_build_disk_controller')
    samples = []

    def free():
        value = shutil.disk_usage(packet['cwd']).free
        samples.append(dict(monotonic=time.monotonic(), freeBytes=value))
        return value

    with (out / 'command.log').open('xb') as log:
        result = life.monitor_owned_command(packet['argv'], packet['cwd'], packet['environment'], log, free, minimum_free=STOP_FREE)
    result['diskSamples'] = samples
    result['commandLog'] = descriptor(out / 'command.log')
    save(out / 'worker-result.json', result)
    cleanup = result.get('ownedGroupCleanup') or {}
    clean = (result['rawChildExitCode'] == 0 and result['lifecycleComplete'] and
             cleanup.get('complete') and not cleanup.get('events') and not cleanup.get('errors') and
             not result.get('stopReason') and not result.get('sigtermReceived') and not result['launcherErrors'])
    return 0 if clean else 1


def main(work):
    assert __debug__ and sys.dont_write_bytecode and sys.flags.isolated
    assert sys.platform == 'linux', 'This driver is intentionally Linux CI only'
    assert work.is_absolute() and not work.exists() and '..' not in work.parts
    os.umask(0o077)
    work.mkdir()
    evidence = work / 'evidence'
    evidence.mkdir()
    result = dict(schemaVersion=1, state='running', forkCommit=COMMIT,
                  componentOrEngineExecuted=False, runtimeAccepted=False,
                  phases=[], startFreeBytes=shutil.disk_usage(work).free,
                  startRequirementBytes=START_FREE, stopFloorBytes=STOP_FREE,
                  github={k: os.environ.get(k) for k in ('GITHUB_SHA', 'GITHUB_RUN_ID', 'GITHUB_RUN_ATTEMPT')})
    env = {k: os.environ[k] for k in ('PATH', 'HOME', 'USER', 'LOGNAME', 'LANG', 'LC_ALL') if k in os.environ}
    env.update(MOZBUILD_STATE_PATH=str(work / 'mozbuild-state'), MOZCONFIG=str(work / 'build/mozconfig-release'),
               RUSTUP_HOME=str(work / 'rustup-home'), CARGO_HOME=str(work / 'cargo-home'), RUSTUP_TOOLCHAIN='1.88.0',
               CARGO_BUILD_JOBS='1', CARGO_INCREMENTAL='0', MAKEFLAGS='-j1',
               MACH_BUILD_PYTHON_NATIVE_PACKAGE_SOURCE='none', MACH_NO_UV='1', PIP_NO_INDEX='1',
               PYTHONDONTWRITEBYTECODE='1', MOZ_NOSPAM='1', TMPDIR=str(work / 'tmp'),
               CCACHE_DISABLE='1', SCCACHE_DISABLE='1', LC_ALL='C.UTF-8', LANG='C.UTF-8')
    for name in ('tmp', 'tools', 'project', 'cargo-home', 'rustup-home', 'mozbuild-state'):
        (work / name).mkdir()
    monitor = utility(MONITOR, 'intl_build_original_owned_monitor')

    def phase(name, argv, seconds):
        assert shutil.disk_usage(work).free >= STOP_FREE
        out = evidence / name
        out.mkdir()
        packet = dict(argv=list(map(str, argv)), cwd=str(work), environment=env)
        save(out / 'packet.json', packet)
        outer = out / 'owned-monitor'
        outer.mkdir()
        terminal = monitor.monitor([sys.executable, '-B', '-I', str(HERE / 'build.py'), '--worker', str(out / 'packet.json')],
                                   str(work), env, outer, seconds,
                                   dict(github=result['github'], driver=descriptor(__file__)))
        inner = json.loads((out / 'worker-result.json').read_text()) if (out / 'worker-result.json').exists() else None
        row = dict(name=name, terminal=descriptor(outer / 'terminal.json'), worker=descriptor(out / 'worker-result.json') if inner else None)
        result['phases'].append(row)
        assert terminal['rawExitCode'] == 0 and terminal['allObservedOwnedGroupsGone'] and not terminal['forcedCleanup'] and not terminal['timeout']
        assert not terminal['errors'] and not terminal['signals'] and not terminal['interruptedSignals'] and not terminal['remainingObservedPids']
        assert inner and inner['rawChildExitCode'] == 0, name
        return out / 'command.log'

    try:
        assert result['startFreeBytes'] >= START_FREE, 'Need 20 GiB free before source fetch; no global runner cleanup is performed'
        tools = {name: shutil.which(name) for name in ('cmake', 'ninja', 'clang', 'clang++', 'rustup', 'curl', 'git')}
        assert all(tools.values()), tools
        result['tools'] = {name: descriptor(Path(path).resolve()) for name, path in tools.items()}
        save(evidence / 'environment-policy.json', env)
        phase('host-compiler', [tools['clang++'], '--version'], 60)
        phase('cmake-version', [tools['cmake'], '--version'], 60)
        phase('sdk-download', [tools['curl'], '--fail', '--location', '--retry', '2', '--output', work / 'wasi-sdk.tar.gz', SDK_URL], 600)
        assert descriptor(work / 'wasi-sdk.tar.gz')['sha256'] == SDK_SHA
        result['sdkArchive'] = descriptor(work / 'wasi-sdk.tar.gz')
        phase('sdk-extract', ['/usr/bin/tar', '-xzf', work / 'wasi-sdk.tar.gz', '-C', work], 300)
        sdk = work / 'wasi-sdk-30.0-x86_64-linux'
        assert (sdk / 'bin/clang').is_file()
        env['WASI_SYSROOT'] = str(sdk / 'share/wasi-sysroot')
        phase('rust-install', [tools['rustup'], 'toolchain', 'install', '1.88.0', '--profile', 'minimal', '--no-self-update', '--target', 'wasm32-wasip1'], 1200)
        phase('rust-version', [tools['rustup'], 'run', '1.88.0', 'rustc', '--version', '--verbose'], 60)
        phase('cargo-version', [tools['rustup'], 'run', '1.88.0', 'cargo', '--version', '--verbose'], 60)
        phase('sdk-version', [sdk / 'bin/clang', '--version'], 60)
        phase('python-version', [sys.executable, '--version'], 60)
        phase('cbindgen-install', [tools['rustup'], 'run', '1.88.0', 'cargo', 'install', '--locked', '--version', '0.29.1', '--root', work / 'tools', 'cbindgen'], 1200)
        env['PATH'] = str(work / 'tools/bin') + ':' + env['PATH']
        phase('cbindgen-version', [work / 'tools/bin/cbindgen', '--version'], 60)
        shutil.copyfile(HERE / 'CMakeLists.txt', work / 'project/CMakeLists.txt')
        phase('configure', [tools['cmake'], '-S', work / 'project', '-B', work / 'build', '-G', 'Ninja',
              '-DCMAKE_BUILD_TYPE=Release', '-DSPIDERMONKEY_BUILD_FROM_SOURCE=ON', '-DSPIDERMONKEY_INTL=ON',
              '-DSTARLING_SOURCE_ROOT=' + str(REPO), '-DCMAKE_TOOLCHAIN_FILE=' + str(sdk / 'share/cmake/wasi-sdk.cmake'),
              '-DSM_HOST_CC=' + tools['clang'], '-DSM_HOST_CXX=' + tools['clang++']], 1800)
        mozconfig = work / 'build/mozconfig-release'
        with mozconfig.open('a') as stream:
            stream.write('ac_add_options --disable-bootstrap\nmk_add_options MOZ_MAKE_FLAGS=-j1\n')
        shutil.copyfile(mozconfig, evidence / 'mozconfig-release')
        source = work / 'project/deps/spidermonkey-source'
        phase('source-revision', [tools['git'], '-C', source, 'rev-parse', 'HEAD'], 60)
        assert (evidence / 'source-revision/command.log').read_text().strip() == COMMIT
        ffi_paths = ('intl/icu_capi', 'intl/icu_segmenter_data',
                     'intl/bidi/rust/unicode-bidi-ffi', 'third_party/rust/unicode-bidi')
        # These self-contained path crates are inputs for the later SINGLE
        # Rust aggregate. This is not an offline vendor or resolved lockfile.
        assert all((source / rel).is_dir() for rel in ffi_paths)
        assert shutil.disk_usage(work).free >= STOP_FREE
        result['ffiSourceFiles'] = [descriptor(p) for rel in ffi_paths
                                    for p in sorted((source / rel).rglob('*')) if p.is_file()]
        with tarfile.open(evidence / 'intl-ffi-sources.tar.gz', 'w:gz') as archive:
            for rel in ffi_paths:
                archive.add(source / rel, arcname=rel, recursive=True)
            for rel in ('Cargo.toml', 'Cargo.lock', '.cargo/config.toml.in'):
                if (source / rel).is_file():
                    archive.add(source / rel, arcname='upstream-provenance/' + rel)
        result['ffiSourceArchive'] = descriptor(evidence / 'intl-ffi-sources.tar.gz')
        assert shutil.disk_usage(work).free >= STOP_FREE
        phase('build', [tools['cmake'], '--build', work / 'build', '--target', 'spidermonkey_build', '--parallel', '1'], 5400)
        obj = work / 'build/spidermonkey-obj'
        for rel in ('js/src/js-confdefs.h', 'config.status', 'config.log', 'js/src/irregexp/backend.mk', 'js/src/build/backend.mk'):
            path = obj / rel
            if path.is_file():
                target = evidence / ('generated/' + rel)
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(path, target)
        dist = work / 'spidermonkey-dist-release-intl'
        assert shutil.disk_usage(work).free >= STOP_FREE
        dist.mkdir()
        shutil.copytree(obj / 'dist/include', dist / 'include', symlinks=False)
        shutil.copyfile(obj / 'dist/libspidermonkey.a', dist / 'libspidermonkey.a')
        assert shutil.disk_usage(work).free >= STOP_FREE
        config = (dist / 'include/js-config.h').read_text()
        import re
        assert re.search(r'^#define\s+JS_HAS_INTL_API\s+1\s*$', config, re.M)
        phase('static-members', [sdk / 'bin/llvm-ar', 't', obj / 'dist/libjs_static.a'], 300)
        phase('merged-members', [sdk / 'bin/llvm-ar', 't', dist / 'libspidermonkey.a'], 300)
        result['distributionFiles'] = [descriptor(p) for p in sorted(dist.rglob('*')) if p.is_file()]
        with tarfile.open(evidence / 'spidermonkey-static-release-intl.tar.gz', 'w:gz') as archive:
            archive.add(dist, arcname=dist.name, recursive=True)
        assert shutil.disk_usage(work).free >= STOP_FREE
        result['distributionArchive'] = descriptor(evidence / 'spidermonkey-static-release-intl.tar.gz')
        phase('source-clean', [tools['git'], '-C', source, 'diff', '--exit-code', 'HEAD'], 60)
        result['state'] = 'guest-library-built-engine-and-runtime-pending'
    except BaseException as error:
        result['state'] = 'failed-no-runtime-acceptance'
        result['error'] = dict(type=type(error).__name__, message=str(error), traceback=traceback.format_exc())
    finally:
        # Failed compiler/configure phases retain their genuine generated
        # diagnostics too. An incomplete distribution is never published.
        obj = work / 'build/spidermonkey-obj'
        for rel in ('js/src/js-confdefs.h', 'config.status', 'config.log', 'js/src/irregexp/backend.mk', 'js/src/build/backend.mk'):
            path = obj / rel
            target = evidence / ('generated/' + rel)
            if path.is_file() and not target.exists():
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(path, target)
        result['endFreeBytes'] = shutil.disk_usage(work).free
        save(evidence / 'result.json', result)
        print(json.dumps({k: result.get(k) for k in ('state', 'error', 'startFreeBytes', 'endFreeBytes')}), flush=True)
    return 0 if result['state'] == 'guest-library-built-engine-and-runtime-pending' else 1


if __name__ == '__main__':
    if len(sys.argv) == 3 and sys.argv[1] == '--worker':
        raise SystemExit(worker(sys.argv[2]))
    assert len(sys.argv) == 2
    raise SystemExit(main(Path(sys.argv[1])))
