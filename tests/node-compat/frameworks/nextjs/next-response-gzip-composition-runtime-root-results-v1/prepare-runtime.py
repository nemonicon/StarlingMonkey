"""Bind real gzip INIT DATA to one independent Node/wire completion comparison.

This preparer writes JSON grants only. The sealed actor owns actual execution.
"""
import hashlib
import json
import os
from pathlib import Path
import shutil
import socket

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
ACTOR = BASE / 'next-response-gzip-composition-runtime-candidate-v1'
CTOR = BASE / 'next-response-gzip-composition-construction-root-results-v1'


def row(path):
    path = Path(path)
    assert path.is_absolute() and path.resolve() == path and path.is_file()
    before = path.stat()
    assert before.st_nlink == 1
    digest, size = hashlib.sha256(), 0
    with path.open('rb') as source:
        for block in iter(lambda: source.read(4 * 1024**2), b''):
            digest.update(block)
            size += len(block)
    after = path.stat()
    assert all(getattr(before, k) == getattr(after, k) for k in
               ['st_dev', 'st_ino', 'st_mode', 'st_nlink', 'st_size', 'st_mtime_ns', 'st_ctime_ns'])
    return dict(path=str(path), sha256=digest.hexdigest(), bytes=size)


def read(path):
    return json.loads(Path(path).read_bytes())


def checked(ref):
    assert set(ref) == {'path', 'sha256', 'bytes'} and row(ref['path']) == ref
    return Path(ref['path'])


def write(path, value):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'w') as target:
        target.write(json.dumps(value, indent=2) + '\n')
        target.flush()
        os.fsync(target.fileno())


def main():
    assert __debug__
    os.umask(0o077)
    assert row(ACTOR / 'plan.json')['sha256'] == '4aed386dbeff6a088fc421c3969896c11d456e19e92d6095cc211835b85d001a'
    plan = read(ACTOR / 'plan.json')
    assert plan['prospectiveActualBindingsPending'] is False
    authority = read(ACTOR / 'root-authority.template.json')
    authority.update(plan['expectedBindings'])
    for ref in plan['expectedBindings'].values():
        checked(ref)
    ctor_path = CTOR / 'gzip-construction-authority.json'
    ctor = read(ctor_path)
    result = read(checked(authority['constructionResult']))
    review = read(checked(authority['constructionDataReview']))
    assert result['passed'] is review['verifiedPassed'] is True
    assert result['error'] is None and result['finalProtection']['unchanged'] is True
    assert result['entryMode'] == ctor['entryMode'] == 'gzip'
    assert result['rootAuthority'] == review['rootAuthority'] == row(ctor_path)
    assert review['actualResult'] == authority['constructionResult']
    assert review['state'] == plan['prospectiveConstructorReviewState']
    assert review['completeReturnedImportAuditVerified'] is True
    for key in ['engine', 'nativeMetadata']:
        assert ctor[key] == authority[key] == result['artifacts'][key]
    assert ctor['callerIndex'] == result['callerIndex'] == authority['constructionCallerIndex']
    assert result['plan'] == authority['constructionPlan']
    assert result['artifacts']['component'] == authority['component']
    assert result['artifacts']['componentAudit'] == authority['componentAudit']
    for key in ['engineBuildEvidence', 'metadataExpectedFixedValues']:
        authority[key] = ctor[key]
    assert len(authority['engineBuildEvidence']) == 39
    assert len(authority['metadataExpectedFixedValues']) == 31
    authority['state'] = 'ROOT_GZIP_COMPOSITION_RUNTIME_AUTHORIZED_V1'
    authority['sourceIndex'] = row(ACTOR / 'index.json')
    authority['plan'] = row(ACTOR / 'plan.json')
    authority['runId'] = 'gzip-476b-first'
    for key in ['controllerAllowed', 'nodeReferenceAllowed', 'guestAllowed',
                'hostProbeRequestAllowed', 'rawWireCaptureAllowed', 'dataValidationAllowed']:
        authority[key] = True
    # A temporary bind-only lease selects one literal port, without a listener.
    with socket.socket() as lease:
        lease.bind(('127.0.0.1', 0))
        authority['origin'] = 'http://127.0.0.1:' + str(lease.getsockname()[1])
    build = Path(authority['nativeMetadata']['path']).parent
    native = read(authority['nativeMetadata']['path'])
    build_result = read(checked(authority['fullNativeBuildResult']))
    build_review = read(checked(authority['fullNativeBuildReview']))
    assert build_review['verifiedPassed'] is True
    assert build_review['callerSourceIndex'] == authority['fullNativeBuildSourceIndex']
    assert build_review['actualResult'] == authority['fullNativeBuildResult']
    assert build_review['actualRootObservation'] == authority['fullNativeBuildObservation']
    assert build_review['engine'] == authority['engine']
    assert build_review['metadata'] == authority['nativeMetadata']
    assert (native['nativePolicyInputCount'], native['buildSupportInputCount'],
            native['embeddingInputCount']) == (435, 387, 3)
    assert all(native[k] == v for k, v in authority['metadataExpectedFixedValues'].items())
    authority['fullBuildGeneratedNullSource'] = row(build / 'build/starling-raw.wasm/null.cpp')
    authority['nativeSourceFamilies'] = [authority['fullNativeBuildSourceIndex'],
        plan['requiredMaterializerIndex'], plan['cleanupCorrectionSourceIndex']]
    world = Path(authority['worldSourceIndex']['path']).parent
    wit = sorted(world.rglob('*.wit'))
    assert len(wit) == 8
    authority['worldInputs'] = [row(path) for path in wit]
    refs, by_path = [], {}

    def add(ref):
        checked(ref)
        if ref['path'] in by_path:
            assert by_path[ref['path']] == ref
        else:
            refs.append(ref)
            by_path[ref['path']] = ref

    # These are genuine current825 source and target records; no old-array retargeting.
    assert len(build_result['sourceCopies']) == 825
    for copy in build_result['sourceCopies']:
        add(copy['source'])
        add(copy['target'])
    assert len(refs) == 1650
    for ref in plan['expectedBindings'].values():
        add(ref)
    for key in ['actualLibrary', 'actualSavedFrameHeader', 'actualConfigHeader', 'actualConfdefs',
                'patchedSpiderMonkeyEvidence', 'savedFramePatchIndex', 'actualAggregateLock',
                'offlineCargoConfig', 'portableCargoSelection', 'validatedCargoProofCapsule',
                'validatedCargoProofIndex', 'sourceComposition']:
        add(native[key])
    for ref in ctor['newSourceEvidence'] + ctor['engineBuildEvidence'] + authority['worldInputs']:
        add(ref)
    for ref in [row(Path(__file__).resolve()), row(ctor_path),
                authority['worldGuardImplementation'], plan['fullBuildGuardImplementation'],
                authority['fullBuildGeneratedNullSource']]:
        add(ref)
    for command in result['commands']:
        assert command['rawExitCode'] == 0 and command['clean'] is True
        for key in ['terminal', 'stdout', 'stderr']:
            add(command[key])
    terminal = read(authority['constructionRootTerminal']['path'])
    for key in ['stdout', 'stderr']:
        add(terminal[key])
    authority['nativeProtectedInputs'] = refs
    output = Path(plan['outputPrefix'] + '-' + authority['runId'])
    assert not os.path.lexists(output) and not os.path.lexists(str(output) + '-external-root')
    assert shutil.disk_usage(output.parent).free >= plan['minimumFreeBytes']
    for phase, key in [('reference', 'nodeReferenceAuthority'), ('wire', 'wireAuthority')]:
        grant = read(ACTOR / 'phase-authority.template.json')
        grant.update(state='ROOT_GZIP_COMPOSITION_PHASE_AUTHORIZED_V1', phase=phase,
                     operationAllowed=True, nodeReferenceAllowed=phase == 'reference',
                     rawWireCaptureAllowed=phase == 'wire', guestAllowed=False)
        for field in ['sourceIndex', 'plan', 'runId', 'origin']:
            grant[field] = authority[field]
        path = HERE / (phase + '-authority.json')
        write(path, grant)
        authority[key] = row(path)
    target = HERE / 'gzip-runtime-authority.json'
    write(target, authority)
    receipt = dict(state='ROOT_GZIP_COMPOSITION_RUNTIME_PREPARED_NOT_LAUNCHED_V1',
                   authority=row(target), sourceTargetDescriptors=1650,
                   totalProtectedDescriptors=len(refs), actorInvoked=False,
                   reservedOriginReleased=True, output=str(output))
    write(HERE / 'runtime-preparation.json', receipt)
    print(json.dumps(receipt), flush=True)


if __name__ == '__main__':
    main()
