"""UNBOUND Source for one stock wasmCloud full-contract owner; original guard contexts."""
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil
import sys

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
ACTOR = BASE / 'wasmcloud-full-contract-candidate-v1'
ACTOR_SOURCE_SHA256 = 'f22d805c38fd9ae0074c71be054defca56e893e61cb0b193445fa4c896e9b898'  # Bind only a genuine sealed full-contract actor index after whole Source peer.
PYTHON = dict(path='/opt/homebrew/Cellar/python@3.11/3.11.10/Frameworks/Python.framework/Versions/3.11/bin/python3.11',
              sha256='b76df9b72b06c2592c34e234c10fb51a587fa4aaf3d57fd98325ea2774f4f758', bytes=52640)
FULL_GUARD = dict(path=str(BASE / 'next-full-build-runtime-root-results-v1/run-full-native-requests.py'),
                  sha256='47c9cab9461a63aa12b38e6f4e8cae3cc714270c370a313fab571f53991cdfe0', bytes=14500)
WORLD_GUARD = dict(path=str(BASE / 'peer-disconnect-root-results-v3/launch-peer-v3-construction.py'),
                   sha256='b7a15f315cde9f87d511eaf2cb0c315853bf343965e825b78abddfb68be82921', bytes=4683)


def read(path):
    return json.loads(Path(path).read_text())


def row(path):
    path = Path(path)
    assert path.is_absolute() and path.resolve() == path and not path.is_symlink() and path.is_file()
    data = path.read_bytes()
    return dict(path=str(path), sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))


def verify(ref):
    assert set(ref) == {'path', 'sha256', 'bytes'} and row(Path(ref['path'])) == ref


def load_original(name, ref):
    verify(ref)
    spec = importlib.util.spec_from_file_location(name, ref['path'])
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def require_bound():
    assert isinstance(ACTOR_SOURCE_SHA256, str) and re.fullmatch('[a-f0-9]{64}', ACTOR_SOURCE_SHA256), 'Unbound Source: no helper, output, port or action is authorized'


def canonical_self_origin(value):
    assert isinstance(value, str)
    match = re.fullmatch(r'http://127\.0\.0\.1:([1-9][0-9]{0,4})', value)
    assert match is not None, 'Root supplies one canonical literal loopback HTTP origin, without credentials/path/query/fragment'
    port = int(match.group(1))
    assert 1 <= port <= 65535 and port != 80, 'Explicit nondefault port required; URL normalization must not erase the egress pin'
    assert value == 'http://127.0.0.1:' + str(port)
    return value


def context():
    require_bound()  # Refuse before any original helper load or input/output/port/action.
    assert __debug__ and sys.flags.isolated and sys.dont_write_bytecode
    assert row(Path(sys.executable).resolve()) == PYTHON
    source = row(ACTOR / 'index.json')
    assert source['sha256'] == ACTOR_SOURCE_SHA256
    native = load_original('original_full_native_guard_for_wasmcloud_full', FULL_GUARD)
    native.family(source)
    world = load_original('original_world_guard_for_wasmcloud_full', WORLD_GUARD)
    return native, world


def capacity(plan, required):
    assert type(required) is int and required == 1073741824
    free = shutil.disk_usage(Path(plan['outputPrefix']).parent).free
    assert free >= required, 'Root full-contract launch requires at least1GiB free'
    return free


def admission(a, plan, native, world):
    """Current full-contract authority, literal self-origin, full-build provenance and genuine world; no actor here."""
    assert a['state'] == 'ROOT_NEXT_WASMCLOUD_FULL_CONTRACT_AUTHORIZED_V1' and a['unissued'] is False
    assert a['sourceIndex'] == row(ACTOR / 'index.json') and a['plan'] == row(ACTOR / 'plan.json')
    assert a['wrapperPython'] == PYTHON and a['fullNativeGuardImplementation'] == FULL_GUARD
    assert a['worldGuardImplementation'] == WORLD_GUARD
    template = read(ACTOR / 'root-authority-template.json')
    for key in ['coldNextGuestAllowed', 'localhostServeAllowed', 'configInspectAllowed', 'fullContractClientAllowed', 'browserAllowed']:
        assert a[key] is True and template[key] is None
    for key, value in template.items():
        if value is False:
            assert a[key] is False
    assert re.fullmatch('[a-z0-9][a-z0-9-]{0,47}', a['runId'])
    assert template['selfOrigin'] is None and canonical_self_origin(a['selfOrigin']) == a['selfOrigin']
    assert plan['outputPrefix'] == '/private/tmp/starling-node-compat/next-wasmtime-deployment'
    assert plan['clientSource'] == row(BASE / 'next-completion-a-runtime-candidate-v1/run-contracts.mjs')
    assert plan['clientSource']['sha256'] == 'd24e08ce60eeeb16aae9f23723101ec2619549ff6d2f651efb6d67f9ec90bd35'
    assert plan['browserSource'] == row(BASE / 'next-browser-netlog-candidate-v1/browser-check.mjs')
    assert plan['browserSource']['sha256'] == 'f19d6c42ea44897ed026ba437657a9749396ee138301e5abbfaa17eb508c7ffa'
    native.family(a['sourceIndex']); native.family(a['constructionCallerIndex']); native.family(a['inputSourceIndex'])
    for key, expected in plan['expectedArtifacts'].items():
        verify(a[key]); assert all(a[key][name] == expected[name] for name in ['sha256', 'bytes'])
    for key in ['node', 'monitor']:
        verify(plan[key])
    verify(PYTHON); verify(FULL_GUARD); verify(WORLD_GUARD)
    for ref in plan['protectedSourceReferences'] + a['engineBuildEvidence'] + a['nativeProtectedInputs']:
        verify(ref)
    for ref in a['nativeSourceFamilies']:
        native.family(ref)
    policy = plan['requiredExternalRootAdmission']
    assert a['constructionDataReview'] == policy['constructionReview']
    assert a['fullNativeBuildReview'] == policy['fullNativeBuildReview']
    assert a['applicationBuildDataReview'] == policy['applicationBuildReview']
    assert a['applicationRootIdentityEvidence'] == policy['applicationRootIdentity']
    c = read(a['constructionResult']['path']); review = read(a['constructionDataReview']['path'])
    assert review['state'] == 'COORDINATED_REAL_NEXT_INTEROP_COMPONENT_INIT_DATA_REVIEW_PASSED_V1'
    assert review['verifiedPassed'] is review['completeReturnedImportAuditVerified'] is True
    assert 'deployedCompletionDiagnosticObserved' not in review, 'Genuine pinned A9256 schema; do not alias a missing field'
    verify(review['complementaryOwnerWorldReview'])
    assert c['passed'] is True and c['error'] is None and c['finalProtection']['unchanged'] is True
    assert c['entryMode'] == review['entryMode'] == 'real-next'
    for key in ['ordinaryExportsInvoked', 'httpServed', 'appMountedAtInit', 'productionProfilePromoted']:
        assert c[key] is False
    for key in ['ordinaryExportsInvoked', 'httpServed', 'appMountedAtInit', 'filesystemFixtureMountedAtInit',
                'deployedFetchProbeInvoked', 'deployedImportOrFilesystemProbeInvoked', 'runtimeAccepted',
                'nodeParityProved', 'productionProfilePromoted']:
        assert review[key] is False
    assert review['actualResult'] == a['constructionResult']
    assert review['callerIndex'] == c['callerIndex'] == a['constructionCallerIndex']
    assert review['rootAuthority'] == c['rootAuthority'] and review['plan'] == c['plan']
    assert review['fullBuildReview'] == a['fullNativeBuildReview']
    for key in ['component', 'componentAudit', 'engine', 'nativeMetadata', 'inputEntry', 'inputSourceIndex']:
        assert review[key] == c['artifacts'][key] == a[key]
    verify(c['rootAuthority']); verify(c['plan'])
    ctor = read(c['rootAuthority']['path']); ctor_plan = read(c['plan']['path'])
    assert ctor['state'] == 'ROOT_NEXT_NATIVE_COMPONENT_CONSTRUCTION_V2' and ctor['entryMode'] == 'real-next'
    assert ctor['callerIndex'] == a['constructionCallerIndex']
    assert ctor_plan['inputSourceIndex'] == a['inputSourceIndex'] and ctor_plan['entries']['real-next'] == a['inputEntry']
    assert len(ctor['metadataExpectedFixedValues']) == 31 and len(ctor['engineBuildEvidence']) == 39
    assert len(ctor['newSourceEvidence']) == 18
    assert ctor['componentizeInitAllowed'] is True
    for key in ['ordinaryExportsAllowed', 'httpServingAllowed', 'networkAllowed', 'nativeBuildAllowed',
                'packageMutationAllowed', 'globalPinMutationAllowed', 'debugAllowed',
                'applicationMountAtInitAllowed', 'deployedResnapshotAllowed']:
        assert ctor[key] is False
    for key in ['engine', 'nativeMetadata', 'metadataExpectedFixedValues', 'engineBuildEvidence']:
        assert ctor[key] == a[key]
    assert c['artifacts']['engineBuildEvidence'] == a['engineBuildEvidence']
    metadata = read(a['nativeMetadata']['path'])
    assert metadata['engine'] == a['engine'] and metadata['metadataKind'] == plan['expectedMetadataKind']
    for key, value in a['metadataExpectedFixedValues'].items():
        assert metadata[key] == value, key
    native.protect_full_build(a, metadata)
    outer = read(a['constructionOuterTerminal']['path'])
    assert native.clean(outer) and outer['authority'] == c['rootAuthority']
    for key in ['stdout', 'stderr']:
        verify(outer[key])
    assert [item['label'] for item in c['commands']] == ['componentize-init', 'component-validate', 'component-wit']
    for command in c['commands']:
        verify(command['terminal']); terminal = read(command['terminal']['path'])
        assert native.clean(terminal) and terminal['authority'] == c['rootAuthority']
        assert command['rawExitCode'] == 0 and command['clean'] is True
        for key in ['stdout', 'stderr']:
            assert terminal[key] == command[key]; verify(command[key])
    app_review = read(a['applicationBuildDataReview']['path'])
    assert app_review['state'] == 'PORTABLE_CACHE_APP_HOST_BUILD_DATA_REVIEW_PASSED_V1' and app_review['verifiedPassed'] is True
    assert app_review['actualResult'] == plan['applicationBuildResult']
    assert app_review['sourceFiles'] == 31 and app_review['unchangedParentFiles'] == 28
    assert a['applicationInputs'] == plan['applicationInputs'] and a['applicationSource'] == plan['applicationSource']
    root_identity = read(a['applicationRootIdentityEvidence']['path'])
    assert root_identity['inventory'] == a['applicationInputs']
    assert {k:root_identity['rootIdentity'][k] for k in ['dev', 'ino', 'mode', 'nlink']} == plan['applicationRootIdentity']
    assert root_identity['rootIdentity']['path'] == a['applicationSource']
    assert a['worldSourceIndex'] == ctor['worldSourceIndex'] == plan['worldFamily']['sourceIndex']
    assert a['worldInputs'] == [ref for ref in ctor['newSourceEvidence'] if ref['path'].endswith('.wit')]
    world_authority = dict(callerIndex=a['constructionCallerIndex'], newSourceEvidence=ctor['newSourceEvidence'],
                           worldSourceIndex=a['worldSourceIndex'])
    current = world.world_guard(world_authority)
    saved = read(a['constructionWorldGuard']['path'])
    assert saved['unchanged'] is True and saved['before'] == saved['after'] == current
    return current


def main():
    assert len(sys.argv) == 2
    native, world = context()
    authority_ref = row(Path(sys.argv[1]).resolve()); a = read(authority_ref['path']); plan = read(ACTOR / 'plan.json')
    required = a['rootLaunchMinimumFreeBytes']; capacity(plan, required)
    verify(a['rootPreparation']); verify(a['rootWrapper'])
    assert a['rootWrapper'] == row(Path(__file__).resolve())
    before = admission(a, plan, native, world)
    output = Path(plan['outputPrefix'] + '-' + a['runId'])
    receipt = HERE / (a['runId'] + '-full-world-guard.json')
    for path in [output, Path(str(output) + '-external-root'), receipt]:
        assert not path.exists() and not path.is_symlink()
    free = capacity(plan, required)
    owned = load_original('original_wasmcloud_full_contract_owner', row(ACTOR / 'run-owned.py'))
    code = 1
    try:
        code = owned.main()
        assert type(code) is int and code in (0, 1)
    finally:
        verify(authority_ref)
        after = admission(a, plan, native, world)
        assert before == after
        with receipt.open('x') as handle:
            handle.write(json.dumps(dict(before=before, after=after, unchanged=True, nativeInputsPreserved=True,
                                         authority=authority_ref, freeBytesAtAdmission=free, minimumFreeBytes=required), indent=2)+'\n')
    return code


if __name__ == '__main__':
    raise SystemExit(main())
