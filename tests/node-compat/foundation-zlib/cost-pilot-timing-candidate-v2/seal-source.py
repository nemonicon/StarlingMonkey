"""Immutable thin source correction seal; standard-library read/hash only."""
from pathlib import Path
import hashlib
import json

D = Path(__file__).resolve().parent

def load(path):
    return json.loads(Path(path).read_text())

def desc(path):
    path = Path(path)
    assert path.is_file() and not path.is_symlink()
    before = path.stat()
    value = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            value.update(block)
    after = path.stat()
    assert (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns) == (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns)
    return {'path': str(path), 'sha256': value.hexdigest(), 'bytes': after.st_size}

def write(name, value):
    with (D / name).open('x') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')

checks = load(D / 'source-checks.json')
assert checks['state'] == 'THIN_V2_STREAMED_DESCRIPTOR_SOURCE_DATA_CHECKS_PASSED'
assert (checks['checks'], checks['regressionChecks'], checks['syntaxFiles'], checks['inputFiles']) == (2904, 17, 6, 861)
inputs = load(D / 'source-inputs.json')['files']
for row in inputs:
    assert desc(row['path']) == row
for row in load(D / 'module-edges.json')['modules']:
    assert desc(row['path']) == row
inherited = load(D / 'inherited-source.json')
refs = load(D / 'references.json')
for name in ['future-authority.template.json', 'future-plan-authority.template.json']:
    value = load(D / name)
    assert value['sourceIndexSha256'] is None and value['sourceIndependentReview'] is None
    assert value.get('actionAllowed', False) is False and value.get('dataPublicationAllowed', False) is False
    for field in ['phaseAuthority', 'quietWindowAuthority', 'warmNPlan', 'warmNMatchedPlan', 'preparedPlan', 'globalBudgetMs']:
        if field in value:
            assert value[field] is None
result = {'schemaVersion': 1, 'state': 'ZLIB_COST_PILOT_TIMING_STREAMED_DESCRIPTOR_SOURCE_CHECKS_PASSED_V2',
    'sourceOnly': True, 'findingId': 'ZLIB-COST-PILOT-TIMING-V1-M1', 'findingCorrectedInSource': True,
    'heldSourceIndex': inherited['heldSourceIndex'], 'formalHoldIndex': inherited['formalHoldIndex'],
    'requiredCorrectionContract': inherited['formalCorrectionContract'], 'heldSourceAndHoldPreserved': True,
    'sourceDataChecks': 2904, 'actualReadHashRegressionChecks': 17, 'syntaxFiles': 6,
    'sourceInputFiles': 861, 'workerDependencies': checks['workerDependencies'], 'actualNestedDescriptors': 91,
    'currentLegitimateLargeDescriptorCount': 1, 'regularDescriptorCount': 90,
    'pinnedStreamedNode': refs['node'], 'actualInitialAndPrivateRecheckPassed': True,
    'unknownOversizedRolePathHashSizeRefused': True, 'wholeLargeExecutableBufferOrTextReportLoaded': False,
    'callerInitialAndRecheckLoopsCorrected': True, 'coherentSiblingSourceWorkerPlanNamespaces': True,
    'genuineFilesystemHashLibraryRoutinesUsed': True, 'operationalAdmissionHelpersInvoked': False,
    'protocolGuestNativeProvidersComponentsCapsLoaderCollectorOwnedLifecycleChanged': False,
    'inheritedOriginalBenignHostEvidence': inherited['inheritedBenignHostEvidence'],
    'newHostLifecycleActionsExecuted': False,
    'preflightWorkerGuestProviderCodecNativeJcoWasmtimePilotTimingExecuted': False,
    'sourceIndependentReview': None, 'rootAction': None, 'planAuthority': None,
    'phaseAuthority': None, 'quietWindowAuthority': None, 'warmNPlan': None, 'globalBudgetMs': None,
    'operationalAdmission': False, 'runtimeAcceptanceClaim': False, 'sourcePromotionAllowed': False,
    'timingAllowed': False, 'actionAuthorityIssued': False}
write('results.json', result)
write('source-receipt.json', {'schemaVersion': 1, 'state': 'AUTHOR_SEALED_THIN_PILOT_TIMING_M1_SOURCE_CORRECTION_V2',
    'result': desc(D / 'results.json'), 'sourceChecks': desc(D / 'source-checks.json'),
    'heldSourceIndex': inherited['heldSourceIndex'], 'formalHoldIndex': inherited['formalHoldIndex'],
    'independentSourceReviewRequired': True, 'actualBenchmarkActionAuthority': None,
    'operationalAdmission': False})
write('verification.json', {'schemaVersion': 1, 'state': 'THIN_V2_FINAL_INPUT_AND_SOURCE_REHASH_PASSED',
    'externalInputFilesRehashed': len(inputs), 'heldV1AndFormalHoldUnchanged': True,
    'newLifecycleOrBenchmarkActionsExecuted': False, 'independentSourceReviewRequired': True})
members = []
for path in sorted(D.rglob('*')):
    if path.is_file():
        row = desc(path)
        assert row['bytes'] <= 4 * 1024 * 1024
        assert path.suffix not in ('.tmp', '.pyc')
        members.append({'path': str(path.relative_to(D)), 'sha256': row['sha256'], 'bytes': row['bytes']})
write('index.json', {'schemaVersion': 1, 'state': 'SEALED_ZLIB_COST_PILOT_TIMING_STREAMED_DESCRIPTOR_SOURCE_AMENDMENT_V2',
    'files': members, 'sourceOnly': True, 'authorChecksPassed': True,
    'heldSourceIndexSha256': inherited['heldSourceIndex']['sha256'], 'findingId': 'ZLIB-COST-PILOT-TIMING-V1-M1',
    'sourceIndependentReview': None, 'futureRootPhaseAuthority': None, 'operationalAdmission': False})
for row in members:
    actual = desc(D / row['path'])
    assert actual['sha256'] == row['sha256'] and actual['bytes'] == row['bytes']
assert sorted(str(p.relative_to(D)) for p in D.rglob('*') if p.is_file()) == sorted([row['path'] for row in members] + ['index.json'])
print(json.dumps({'index': desc(D / 'index.json'), 'result': desc(D / 'results.json'),
    'receipt': desc(D / 'source-receipt.json'), 'indexedFiles': len(members), 'actualRegularFiles': len(members) + 1,
    'sourceDataChecks': 2904, 'actualReadHashRegressionChecks': 17, 'syntaxFiles': 6,
    'sourceInputFiles': 861, 'benchmarkActions': False}))
