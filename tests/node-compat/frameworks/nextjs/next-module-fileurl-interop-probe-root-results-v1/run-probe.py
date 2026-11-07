"""Apply existing full-native/whole-world guards around one deployed interop probe."""
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sys

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
ACTOR = BASE / 'next-module-fileurl-interop-probe-runtime-candidate-v1'
FULL = BASE / 'next-full-build-runtime-root-results-v1/run-full-native-requests.py'
WORLD = BASE / 'peer-disconnect-root-results-v3/launch-peer-v3-construction.py'


def row(path):
    data = path.read_bytes()
    return dict(path=str(path), sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    assert __debug__ and sys.flags.isolated and sys.dont_write_bytecode and len(sys.argv) == 2
    authority_path = Path(sys.argv[1])
    assert authority_path.is_absolute() and authority_path.resolve() == authority_path
    authority_ref = row(authority_path)
    authority = json.loads(authority_path.read_text())
    assert authority['state'] == 'ROOT_FILE_URL_INTEROP_PROBE_AUTHORIZED_V1'
    assert authority['sourceIndex'] == row(ACTOR / 'index.json')
    assert authority['fullBuildGuardImplementation'] == row(FULL)
    assert authority['worldGuardImplementation'] == row(WORLD)
    assert row(FULL)['sha256'] == '47c9cab9461a63aa12b38e6f4e8cae3cc714270c370a313fab571f53991cdfe0'
    assert row(WORLD)['sha256'] == 'b7a15f315cde9f87d511eaf2cb0c315853bf343965e825b78abddfb68be82921'
    native_guard = load('genuine_full_native_build_data_guard', FULL)
    world_guard = load('genuine_complete_constructor_world_guard', WORLD)
    world_authority = dict(callerIndex=authority['constructionCallerIndex'],
        newSourceEvidence=authority['newSourceEvidence'], worldSourceIndex=authority['worldSourceIndex'])
    receipt = HERE / (authority['runId'] + '-full-native-world-guard.json')
    assert not receipt.exists() and not receipt.is_symlink()

    def protect():
        assert row(authority_path) == authority_ref
        for key in ['sourceIndex', 'constructionCallerIndex', 'worldSourceIndex']:
            native_guard.family(authority[key])
        for ref in authority['nativeSourceFamilies']:
            native_guard.family(ref)
        for ref in authority['nativeProtectedInputs'] + authority['engineBuildEvidence']:
            native_guard.verify(ref)
        for key in ['engine', 'nativeMetadata', 'component', 'componentAudit', 'constructionDataReview']:
            native_guard.verify(authority[key])
        native = json.loads(Path(authority['nativeMetadata']['path']).read_text())
        native_guard.protect_full_build(authority, native)

    protect()
    before = world_guard.world_guard(world_authority)
    ctor_world = json.loads(Path(authority['constructionWorldGuard']['path']).read_text())
    assert ctor_world['unchanged'] is True and ctor_world['before'] == ctor_world['after'] == before
    free = shutil.disk_usage('/private/tmp').free
    assert free >= 1073741824
    owned = load('genuine_single_guard_probe_owner', ACTOR / 'run-owned.py')
    code = 1
    try:
        try:
            owned.main()
        except SystemExit as status:
            assert type(status.code) is int and status.code in (0, 1)
            code = status.code
    finally:
        after = world_guard.world_guard(world_authority)
        protect()
        assert before == after
        with receipt.open('x') as handle:
            handle.write(json.dumps(dict(state='ROOT_SINGLE_INTEROP_PROBE_NATIVE_WORLD_GUARDS_COMPLETED_V1',
                authority=authority_ref, before=before, after=after, unchanged=True,
                nativeInputsPreserved=True, freeBytesAtAdmission=free, minimumFreeBytes=1073741824,
                rootReportedActorExitCode=code, nodeCompatibilityAccepted=False), indent=2) + '\n')
    return code


if __name__ == '__main__':
    raise SystemExit(main())
