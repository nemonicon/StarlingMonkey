"""Prepare one INIT-only constructor using genuine accepted guarded-build DATA."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
WORK = Path('/private/tmp/starling-node-compat/next-native-intl-build-guard825-first')


def row(path):
    path = Path(path)
    data = path.read_bytes()
    return dict(path=str(path), sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))


def main():
    prior = BASE / 'next-entry-fixes-root-results-v6/next-v6-construction-authority.json'
    authority = json.loads(prior.read_text())
    caller = BASE / 'next-module-boundary-construction-v1'
    plan = json.loads((caller / 'plan.json').read_text())
    metadata = json.loads((WORK / 'metadata.json').read_text())
    result = json.loads((WORK / 'result.json').read_text())
    build_review_path = BASE / 'next-module-boundary-native-root-results-v1/actual-build-review.json'
    review = json.loads(build_review_path.read_text())
    assert review['verifiedPassed'] is True
    assert review['state'] == 'INDEPENDENT_PORTABLE_NEXT_INTL_NATIVE_BUILD_DATA_REVIEW_PASSED_V1'
    assert review['actualResult'] == row(WORK / 'result.json')
    assert review['metadata'] == row(WORK / 'metadata.json')
    assert review['engine'] == metadata['engine']
    assert review['callerSourceIndex'] == row(BASE / 'next-native-portable-build-preparation-v4/index.json')
    assert result['passed'] is True and result['primaryError'] is None
    assert metadata['metadataKind'] == 'EXPERIMENTAL_NEXT_INTL_NATIVE_BUILD_ACTUAL_V1'
    assert len(metadata['actualCompileRows']) == 80
    assert len(metadata['actualSeparateEmbeddingCompileRows']) == 1
    assert len(result['sourceCopies']) == 825
    authority['callerIndex'] = row(caller / 'index.json')
    authority['runId'] = 'guard-ca84-first'
    authority['outputRoot'] = plan['outputPrefix'] + '-real-next-' + authority['runId']
    authority['engine'] = metadata['engine']
    authority['nativeMetadata'] = row(WORK / 'metadata.json')
    authority['metadataExpectedFixedValues'] = {
        key: metadata[key] for key in authority['metadataExpectedFixedValues']
    }
    root_monitor = Path(str(WORK) + '-root-monitor')
    evidence = [WORK / 'result.json', root_monitor / 'observation.json', build_review_path,
                root_monitor / 'authority.issued.json', root_monitor / 'terminal.json',
                root_monitor / 'started.json', root_monitor / 'stdout.log', root_monitor / 'stderr.log',
                WORK / 'build/compile_commands.json', WORK / 'results/ninja-commands/command.combined.log',
                WORK / 'protection-before.json',
                BASE / 'next-native-portable-build-preparation-v4/run.py',
                BASE / 'next-native-portable-build-preparation-v4/index.json',
                BASE / 'next-native-portable-build-preparation-v4/plan.json',
                WORK / 'configured-inputs.json']
    for phase in result['phases']:
        assert phase['rawExitCode'] == phase['outerRawExitCode'] == 0
        monitor = WORK / 'results' / phase['label'] / 'owned-monitor'
        evidence += [monitor / 'terminal.json', WORK / 'results' / phase['label'] / 'worker-result.json',
                     monitor / 'stdout.log', monitor / 'stderr.log']
    assert len(evidence) == len(set(evidence)) == 39
    authority['engineBuildEvidence'] = [row(path) for path in evidence]
    old_caller = BASE / 'next-entry-fixes-construction-v6/index.json'
    old_builder = BASE / 'next-native-portable-build-preparation-v3/index.json'
    authority['newSourceEvidence'] = [
        authority['callerIndex'] if ref['path'] == str(old_caller)
        else row(BASE / 'next-native-portable-build-preparation-v4/index.json') if ref['path'] == str(old_builder)
        else ref for ref in authority['newSourceEvidence']
    ]
    authority['nativeProfileLabel'] = (
        'Genuine fresh guarded435/387/3 full native build:80nativeTUs(79CPP/1C '
        'including generatednull.cpp),separateembeddingCPP,freshlockedRust, '
        'previouslybuilt pinnedSpiderMonkey library. No incremental metadata projection.'
    )
    authority['completion'] = 'No new component result yet. INIT construction/validation/WIT DATA only; no app mount or ordinary export.'
    authority['rootReview'] = (
        'One fresh owned INIT construction on genuine accepted ca84/e674 guarded '
        'full-build DATA, same three V6 constructor executables/unchanged V5 '
        'entry73b/1e49/private61685/d30/world8025. Full actual metadata retained '
        'without scalar-row/old-frame projection. Existing2400/1800/120 caps and '
        '1GiB start, all ordinary exports/HTTP/app mount/network/nativebuild/'
        'package-global mutation/DEBUG/deployed-resnapshot permissions false. '
        'The separate3856 CJS/fileURL prototype is not in this engine and no '
        'runtime/import-safety/production claim follows from construction.'
    )
    assert plan['expectedEngineForRootAuthority'] == authority['engine']
    assert plan['expectedNativeMetadataForRootAuthority'] == authority['nativeMetadata']
    assert not Path(authority['outputRoot']).exists()
    assert not Path(authority['outputRoot'] + '-external-root').exists()
    target = HERE / 'guard-next-v1-construction-authority.json'
    with target.open('x') as handle:
        handle.write(json.dumps(authority, indent=2) + '\n')
    receipt = dict(state='ROOT_GUARD_NEXT_INIT_CONSTRUCTION_PREPARED_NOT_LAUNCHED',
                   authority=row(target), priorAuthority=row(prior),
                   engine=authority['engine'], nativeMetadata=authority['nativeMetadata'],
                   buildReview=row(build_review_path), genuineBuildEvidenceCount=39,
                   inputEntry=plan['entries']['real-next'], actorInvoked=False)
    with (HERE / 'preparation.json').open('x') as handle:
        handle.write(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt), flush=True)


if __name__ == '__main__':
    main()
