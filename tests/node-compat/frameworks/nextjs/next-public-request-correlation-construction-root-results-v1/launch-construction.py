"""Root-owned sequential constructor launcher; no ordinary guest calls."""
import hashlib, importlib.util, json, os, shutil, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PYTHON = '/Applications/Xcode.app/Contents/Developer/Library/Frameworks/Python3.framework/Versions/3.9/bin/python3.9'
MONITOR = HERE.parents[2] / 'foundation-crypto/ownership-gc-build-controller-candidate-v1/monitor.py'

def row(p):
    p = Path(p)
    return dict(path=str(p), sha256=hashlib.sha256(p.read_bytes()).hexdigest(), bytes=p.stat().st_size)

CALLER_SOURCE_INDEX = {'path': '/Users/dan/dev/StarlingMonkey/tests/node-compat/frameworks/nextjs/next-public-request-correlation-construction-v1/index.json', 'sha256': '6ef36102de1115744cdc7f811fff70e2be2799fb5d6dff376583c2fae22483c0', 'bytes': 3555}  # Genuine sealed caller pin; fail before DATA/helper/output/action while unbound.
FULL_GUARD = dict(path=str(HERE.parent / 'next-full-build-runtime-root-results-v1/run-full-native-requests.py'), sha256='47c9cab9461a63aa12b38e6f4e8cae3cc714270c370a313fab571f53991cdfe0', bytes=14500)
WORLD_GUARD = dict(path=str(HERE.parent / 'peer-disconnect-root-results-v3/launch-peer-v3-construction.py'), sha256='b7a15f315cde9f87d511eaf2cb0c315853bf343965e825b78abddfb68be82921', bytes=4683)
WORK = Path('/private/tmp/starling-node-compat/next-native-intl-build-fetch-cleanup825-first')
ROOT_LOGS = Path(str(WORK) + '-root-monitor')


def require_bound():
    assert isinstance(CALLER_SOURCE_INDEX, dict) and set(CALLER_SOURCE_INDEX) == {'path', 'sha256', 'bytes'}, 'Unbound constructor Source; no helper/output/action'


def checked(ref):
    p = Path(ref['path'])
    assert p.is_absolute() and p.resolve() == p and p.is_file() and p.stat().st_nlink == 1
    assert row(p) == ref
    return p


def load_original(name, ref):
    checked(ref)
    spec = importlib.util.spec_from_file_location(name, ref['path'])
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def admission(authority):
    require_bound()
    assert authority['callerIndex'] == CALLER_SOURCE_INDEX
    checked(CALLER_SOURCE_INDEX)
    review_path = HERE.parent / 'next-native-fetch-resource-cleanup-root-results-v1/actual-build-review.json'
    assert row(review_path)['sha256'] == '41857258d4da6f9fc47c8fbce60fb8818335d6ab5607c1d77f3e2c5742da3b72'
    review = json.loads(review_path.read_text())
    assert review['verifiedPassed'] is True and review['engine'] == authority['engine'] and review['metadata'] == authority['nativeMetadata']
    checked(authority['nativeMetadata']); checked(authority['engine'])
    metadata = json.loads(Path(authority['nativeMetadata']['path']).read_text())
    # These are exactly the seven actual fields read by genuine protect_full_build.
    # This local data context is not a runtime/constructor permission authority.
    full_build_roles = dict(engine=authority['engine'], nativeMetadata=authority['nativeMetadata'],
        fullNativeBuildResult=row(WORK / 'result.json'),
        fullNativeBuildObservation=row(ROOT_LOGS / 'observation.json'),
        fullNativeBuildReview=row(review_path), fullNativeBuildSourceIndex=review['callerSourceIndex'],
        fullBuildGeneratedNullSource=row(WORK / 'build/starling-raw.wasm/null.cpp'))
    native = load_original('original_full_native_guard_public_correlation_ctor', FULL_GUARD)
    world = load_original('original_world_guard_public_correlation_ctor', WORLD_GUARD)
    native.protect_full_build(full_build_roles, metadata)
    return world.world_guard(authority)


def main():
    assert __debug__ and sys.flags.isolated and sys.dont_write_bytecode
    assert len(sys.argv) == 2
    require_bound()
    kind = sys.argv[1]
    assert kind == 'public-request-correlation'
    authority = HERE / (kind + '-construction-authority.json')
    ar = row(authority)
    a = json.loads(authority.read_text())
    caller = Path(a['callerIndex']['path']).parent
    assert row(caller / 'index.json') == a['callerIndex']
    assert row(MONITOR)['sha256'] == '86913867251bc889701859ca6a361ccf9c17288a6a3bfc7a5c8d8e5bbe5c4cbe'
    assert shutil.disk_usage('/private/tmp').free >= 1024**3
    before = admission(a)
    logs = Path(a['outputRoot'] + '-external-root')
    logs.mkdir(mode=0o700)
    spec = importlib.util.spec_from_file_location('original_owned_monitor', MONITOR)
    monitor = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(monitor)
    env = {k: os.environ[k] for k in ('HOME', 'USER', 'LOGNAME') if k in os.environ}
    env.update(PATH='/usr/bin:/bin', LANG='C', LC_ALL='C')
    try:
        terminal = monitor.monitor([PYTHON, '-I', '-B', str(caller/'run.py'), '--authority', str(authority), '--sha256', ar['sha256']], str(caller), env, logs, 2400, ar)
    finally:
        after = admission(a)
        assert row(authority) == ar
        with (logs/'world-guard.json').open('x') as handle:
            handle.write(json.dumps(dict(before=before, after=after, unchanged=before == after, nativeInputsPreserved=True, fullNativeGuardImplementation=FULL_GUARD, worldGuardImplementation=WORLD_GUARD), indent=2)+'\n')
    print(json.dumps({k: terminal[k] for k in ('rawExitCode', 'timeout', 'forcedCleanup', 'allObservedOwnedGroupsGone', 'errors', 'signals', 'interruptedSignals')}), flush=True)
    return 0 if terminal['rawExitCode'] == 0 and not terminal['timeout'] and not terminal['forcedCleanup'] and terminal['allObservedOwnedGroupsGone'] and all(not terminal[k] for k in ('errors', 'signals', 'interruptedSignals', 'remainingObservedPids')) else 1

if __name__ == '__main__':
    raise SystemExit(main())
