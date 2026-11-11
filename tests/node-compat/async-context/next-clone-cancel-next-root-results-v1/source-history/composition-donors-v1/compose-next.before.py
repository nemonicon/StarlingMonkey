"""Compose the unchanged reviewed Next inner with the V4 observer after genuine seven-case metadata acceptance."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
WORK = Path('/private/tmp/starling-node-compat/next-standard-handler-observer-next-v4-first')
PREPARER = dict(path=str(BASE / 'next-native-export-diagnostic-next-root-results-v1/prepare-construction.py'),
    sha256='4bafbb2fd675bcee84746aea3988ae6eb597d64570d19cd3c8819aa158d2c5e4', bytes=19784)
INNER_REVIEW = dict(path=str(BASE / 'next-native-export-diagnostic-next-root-results-v1/actual-construction-review.json'),
    sha256='5c284564e0ddefba507c5429acd98c42393d5c0f2764105a4046f0665f51e16a', bytes=22550)
INNER_AUTHORITY = dict(path=str(BASE / 'next-native-export-diagnostic-next-root-results-v1/diagnostic-next-construction-authority.json'),
    sha256='23313b9b1858e22df729b379c10750cd92ba00ce4aa9bee179fc21142fdfea66', bytes=5597386)
OBSERVER_REVIEW = dict(path=str(HERE / 'actual-v4-composition-review.json'),
    sha256='214c1d9bcfd1858666d460afe72811b858fc8018e9f5e4bfb9519d8ddbe04224', bytes=11140)
METADATA_REVIEW = {'path': '/Users/dan/dev/StarlingMonkey/tests/node-compat/frameworks/nextjs/next-standard-handler-observer-v4-root-results-v1/actual-metadata-runtime-review.json', 'sha256': '61bb6690df9cf8fef3c455314352a95816a20bc01920909b75632bf5333c47c8', 'bytes': 7272}
WAC = dict(path='/private/tmp/starling-node-compat/next-standard-handler-wac-build-v1-first/target/debug/wac',
    sha256='6577e5eedeb0644025a8454c3d600ecad14a3788432c48e8d40b7ba56d271f5f', bytes=30168152)
WASM_TOOLS = dict(path='/private/tmp/starling-node-compat/node-crypto-hash-hmac-v3-build/cache/wasm-tools/1448/wasm-tools',
    sha256='b332dd79057dafdcc8a36ca933d0d499acea506b56b1ea28e28fbb036c9e713d', bytes=17556208)


def main():
    if not (__debug__ and sys.flags.isolated and sys.dont_write_bytecode and len(sys.argv) == 1 and type(METADATA_REVIEW) is dict):
        raise RuntimeError('Use non-optimized Python -I -B and a genuine bound V4 metadata review; no helper read or action')
    source = Path(PREPARER['path'])
    raw = source.read_bytes()
    assert source.resolve() == source and not source.is_symlink() and source.stat().st_nlink == 1
    assert (hashlib.sha256(raw).hexdigest(), len(raw)) == (PREPARER['sha256'], PREPARER['bytes'])
    spec = importlib.util.spec_from_file_location('genuine_next_v4_observer_composition_admission', source)
    prep = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(prep)
    review = prep.document(INNER_REVIEW)
    assert review['state'] == 'COORDINATED_NATIVE_EXPORT_DIAGNOSTIC_NEXT_COMPONENT_INIT_DATA_REVIEW_PASSED_V1'
    assert review['verifiedPassed'] is True and review['rootAuthority'] == INNER_AUTHORITY
    observer = prep.document(OBSERVER_REVIEW)
    assert observer['state'] == 'COORDINATED_STANDARD_HANDLER_OBSERVER_V4_COMPOSITION_DATA_REVIEW_PASSED_V1'
    assert observer['verifiedPassed'] is True and observer['verifiedDataReviewPassed'] is True
    assert review['completeReturnedImportAuditVerified'] is True
    assert observer['rawChildBytesVerified'] is observer['siblingDefiningInstancesVerified'] is True
    assert observer['sharedNominalResourceAliasesVerified'] is observer['fieldsNominalResourceAliasesVerified'] is True
    assert observer['metadataGetterCanonicalOptionsVerified'] is observer['correlationSnapshotIndependentOfMethodAndPathSourceVerified'] is True
    assert observer['allSevenRequestedToolStepsRawZero'] is observer['allSevenToolStderrEmpty'] is True
    assert observer['runtimeAccepted'] is observer['actualMetadataBehaviorProved'] is False
    metadata = prep.document(METADATA_REVIEW)
    assert metadata['state'] == 'COORDINATED_STANDARD_HANDLER_OBSERVER_V4_METADATA_DATA_REVIEW_PASSED_V1'
    for key in ('verifiedPassed', 'verifiedDataReviewPassed', 'allCollectionsCompletedCleanly', 'actualMetadataBehaviorProved', 'runtimeAccepted', 'cleanOwner', 'finalInputsPreserved'):
        assert metadata[key] is True
    assert type(metadata['metadataCasesPassed']) is int and metadata['metadataCasesPassed'] == 7
    assert metadata['originalOwnerSeconds'] == 900 and metadata['rawExitCode'] == 0
    assert metadata['compositionReview'] == OBSERVER_REVIEW
    assert metadata['envelope'] == observer['envelope'] and metadata['observerBinary'] == observer['observerBinary']
    assert metadata['innerComponent'] == observer['innerComponent']
    assert metadata['nextWorkloadExecuted'] is metadata['fullNextAccepted'] is False
    assert metadata['allocatorOrAbsentPathExecuted'] is metadata['recordLimitExecuted'] is False
    assert len(metadata['caseResults']) == 7 and all(item['passed'] is True for item in metadata['caseResults'])
    inner, binary = review['component'], observer['observerBinary']
    assert inner == dict(path='/private/tmp/starling-node-compat/next-native-export-diagnostic-next-component-v2-real-next-diagnostic-next-native-export-first/api-return/returned-component.wasm', sha256='6b2084d0a7abe06862825f70cb87016811654ed1fb0e5db9377ccf3a303df3ce', bytes=37282148)
    assert binary == dict(path='/private/tmp/starling-node-compat/next-standard-handler-observer-build-v4-first/observer.wasm', sha256='3534089e3a28ef109cffef9bc2c6b9bebf1e7ab7c90d1781c91272d01ac3092f', bytes=5771)
    refs = [PREPARER, INNER_REVIEW, INNER_AUTHORITY, OBSERVER_REVIEW, METADATA_REVIEW, WAC, WASM_TOOLS, inner, binary]
    refs += [observer[k] for k in ('observerSource', 'observerManifest', 'observerProtocol')]
    self_ref = prep.row(Path(__file__).resolve())

    def protect():
        for ref in refs + [self_ref]:
            prep.checked(ref)

    protect()
    authority = prep.document(INNER_AUTHORITY)
    before = prep.admit(authority)
    assert not WORK.exists() and not WORK.is_symlink() and WORK.resolve() == WORK
    output = HERE / 'next-v4-composition-result.json'
    assert not output.exists() and not output.is_symlink()
    WORK.mkdir(mode=0o700)
    envelope = WORK / 'next-with-observer.wasm'
    skeleton = WORK / 'envelope.skeleton.wat'
    steps = [
        ('compose', [WAC['path'], 'plug', '--plug', inner['path'], binary['path'], '-o', str(envelope)]),
        ('validate', [WASM_TOOLS['path'], 'validate', str(envelope)]),
        ('wit', [WASM_TOOLS['path'], 'component', 'wit', str(envelope)]),
        ('skeleton', [WASM_TOOLS['path'], 'print', '--skeleton', '--print-offsets', str(envelope), '-o', str(skeleton)]),
    ]
    result = dict(schemaVersion=1, state='ROOT_NEXT_STANDARD_HANDLER_OBSERVER_V4_COMPOSITION_COLLECTING_V1',
        controller=self_ref, innerComponent=inner, innerConstructionReview=INNER_REVIEW,
        innerConstructionAuthority=INNER_AUTHORITY, observerBinary=binary,
        observerSourceReview=OBSERVER_REVIEW, observerMetadataReview=METADATA_REVIEW, commands=[], error=None, finalizationErrors=[],
        constructorGuardBefore=before, constructorGuardAfter=None, finalInputsPreserved=False,
        runtimeInvoked=False, fullNextAccepted=False)
    primary = None
    try:
        for label, argv in steps:
            protect()
            out, err = WORK / (label + '.stdout.log'), WORK / (label + '.stderr.log')
            attempt = dict(label=label, argv=argv, rawExitCode=None, timeout=False, error=None, stdout=None, stderr=None)
            result['commands'].append(attempt)
            try:
                with out.open('xb') as stdout, err.open('xb') as stderr:
                    completed = subprocess.run(argv, cwd=WORK, env=dict(PATH='/usr/bin:/bin', LANG='C', LC_ALL='C'),
                        stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr, timeout=120, check=False)
                attempt['rawExitCode'] = completed.returncode
            except BaseException as error:
                attempt['timeout'] = isinstance(error, subprocess.TimeoutExpired)
                attempt['error'] = dict(name=type(error).__name__, message=str(error)[:2048])
                raise
            finally:
                for key, path in [('stdout', out), ('stderr', err)]:
                    if path.exists():
                        try:
                            attempt[key] = prep.row(path)
                        except BaseException as error:
                            if attempt['error'] is None:
                                raise
                            result['finalizationErrors'].append(dict(stage=label + '-' + key, name=type(error).__name__, message=str(error)[:2048]))
            assert completed.returncode == 0, 'Composition tool failed: ' + label
        result.update(envelope=prep.row(envelope), actualSkeleton=prep.row(skeleton),
            externalWit=prep.row(WORK / 'wit.stdout.log'), allRequestedToolStepsPassed=True)
    except BaseException as error:
        primary = error
        result['error'] = dict(name=type(error).__name__, message=str(error)[:2048])
    finally:
        try:
            result['constructorGuardAfter'] = prep.admit(authority)
            protect()
            result['finalInputsPreserved'] = True
        except BaseException as error:
            if primary is None:
                primary = error
            result['finalizationErrors'].append(dict(stage='final-admission', name=type(error).__name__, message=str(error)[:2048]))
        result['state'] = ('ROOT_NEXT_STANDARD_HANDLER_OBSERVER_V4_COMPOSITION_COMPLETED_UNREVIEWED_V1'
            if primary is None else 'ROOT_NEXT_STANDARD_HANDLER_OBSERVER_V4_COMPOSITION_FAILED_PRESERVED_V1')
        try:
            receipt = prep.save(output, result)
            print(json.dumps(dict(result=receipt, state=result['state'], runtimeInvoked=False)))
        except BaseException:
            if primary is not None:
                raise primary
            raise
    if primary is not None:
        raise primary
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
