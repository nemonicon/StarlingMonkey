"""Seal only completed source/check/evidence DATA; runs no tests or actions."""
from pathlib import Path
import hashlib
import json
import stat

D = Path(__file__).resolve().parent

def load(path):
    return json.loads(Path(path).read_text())

def desc(path):
    path = Path(path)
    before = path.lstat()
    assert stat.S_ISREG(before.st_mode) and not path.is_symlink()
    value = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            value.update(block)
    after = path.stat()
    assert (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns) == (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns)
    return {'path': str(path), 'sha256': value.hexdigest(), 'bytes': after.st_size}

def write(name, value):
    with (D / name).open('x') as output:
        json.dump(value, output, indent=2)
        output.write('\n')

c = load(D / 'source-checks.json')
assert c['state'] == 'ZLIB_COST_PILOT_TIMING_SOURCE_DATA_CHECKS_PASSED_V1'
assert c['pureMockChecks'] == 90 and c['syntaxFiles'] == 17 and c['checks'] == 6924
assert c['ownerPreflightProviderCodecGuestNativeJcoWasmtimePilotTimingExecuted'] is False
assert c['realBenignHostInfrastructureExecutedSeparately'] is True and c['realBenignSuitePassed'] is True
inputs = load(D / 'source-inputs.json')['files']
assert len(inputs) == 699
for row in inputs:
    assert desc(row['path']) == row
edges = load(D / 'module-edges.json')
for row in edges['modules']:
    assert desc(row['path']) == row
for name in ['future-authority.template.json', 'future-phase-authority.template.json', 'future-plan-authority.template.json', 'future-quiet-window.template.json']:
    value = load(D / name)
    assert value['sourceIndexSha256'] is None
    for key in ['actionAllowed', 'dataPublicationAllowed', 'exclusiveMeasurementApproved']:
        if key in value:
            assert value[key] is False
    for key in ['phaseAuthority', 'quietWindowAuthority', 'warmNPlan', 'warmNMatchedPlan', 'preparedPlan', 'globalBudgetMs']:
        if key in value:
            assert value[key] is None
benign = load(D / 'benign-lifecycle-evidence.json')
for row in benign['sourceBindings']:
    assert desc(row['path']) == row
for copy in benign['copies']:
    assert desc(copy['original']['path']) == copy['original']
    got = desc(D / copy['copy']['path'])
    assert got['sha256'] == copy['copy']['sha256'] and got['bytes'] == copy['copy']['bytes']
refs = load(D / 'references.json')
state = 'ZLIB_COST_PILOT_TIMING_SOURCE_AND_BENIGN_INFRASTRUCTURE_CHECKS_PASSED_V1'
result = {'schemaVersion': 1, 'state': state, 'sourceOnly': True, 'authorSourceChecksPassed': True,
    'sourceDataChecks': c['checks'], 'pureMockChecks': 90, 'syntaxFiles': 17, 'sourceInputFiles': 699,
    'moduleFiles': c['moduleFiles'], 'moduleEdges': c['moduleEdges'], 'workerDependencies': c['workerDependencies'],
    'sealedExistingSourceFamilies': c['sealedPhysicalFamilies'],
    'calibrationDecision': refs['calibrationDecision'], 'actualControlsProof': refs['actualControlsProof'],
    'fullCorrectness': refs['fullCorrectness'], 'stockWasmtimeStrings': refs['stockWasmtimeStrings'],
    'actualHostInfrastructureExecuted': True, 'realBenignHostSuitePassed': True,
    'priorBenignDriverFailurePreservedAndUnaccepted': True,
    'benignEvidence': desc(D / 'benign-lifecycle-evidence.json'),
    'benchmarkPreflightGuestProviderCodecNativeJcoWasmtimePilotTimingExecuted': False,
    'actualGeneratedModuleImportedByThisPreparation': False,
    'actualGlobalPilotBudgetSelected': None, 'sourceIndependentReview': None,
    'rootAction': None, 'phaseAuthority': None, 'quietWindowAuthority': None, 'warmNPlan': None,
    'timingWorkersPlanned': 360, 'codecBatchCallsPlanned': 3600, 'n1ControlCallsPlanned': 2160,
    'maximumPilotPairs': 768, 'maximumPilotWorkers': 1536, 'maximumSeparatePilotControls': 9216,
    'performanceClaim': False, 'runtimeAcceptanceClaim': False, 'operationalAdmission': False,
    'sourcePromotionAllowed': False, 'actionAuthorityIssued': False,
    'scope': 'Concrete sealed source plus separately authorized short benign host lifecycle evidence. Not actual guest/codec/pilot/timing, full two-hour wallclock, capacity, reuse or runtime acceptance.'}
write('results.json', result)
write('source-receipt.json', {'schemaVersion': 1, 'state': 'AUTHOR_SEALED_CODEC_PILOT_TIMING_SOURCE_NO_BENCHMARK_ACTION_AUTHORITY_V1',
    'results': desc(D / 'results.json'), 'sourceChecks': desc(D / 'source-checks.json'),
    'actualBenignHostInfrastructureExecuted': True, 'benchmarkActionsExecuted': False,
    'sourceIndependentReview': None, 'futureRootPhaseAndWarmNAndWindowAuthorities': None,
    'operationalAdmission': False})
write('verification.json', {'schemaVersion': 1, 'state': 'AUTHOR_FINAL_SOURCE_AND_DECLARED_INPUT_REHASH_PASSED_V1',
    'sourceInputFilesRehashed': len(inputs), 'newAndInheritedModuleFilesRehashed': len(edges['modules']),
    'exactInfrastructureCopiesRehashed': len(benign['copies']), 'noExistingSealedFileWritten': True,
    'independentSourceReviewStillRequired': True, 'benchmarkActionsInvoked': False})
members = []
for path in sorted(D.rglob('*')):
    if path.is_file():
        assert path.suffix not in ('.pyc', '.tmp')
        row = desc(path)
        assert row['bytes'] <= 4 * 1024 * 1024, 'compact source packet consumed by worker authentication'
        members.append({'path': str(path.relative_to(D)), 'sha256': row['sha256'], 'bytes': row['bytes']})
write('index.json', {'schemaVersion': 1, 'state': 'SEALED_ZLIB_COST_PILOT_TIMING_SOURCE_PROPOSAL_V1',
    'files': members, 'sourceOnly': True, 'authorChecksPassed': True,
    'actualBenignHostInfrastructureExecuted': True, 'benchmarkActionsExecuted': False,
    'sourceIndependentReview': None, 'futureRootActionAuthority': None, 'operationalAdmission': False})
for row in members:
    actual = desc(D / row['path'])
    assert actual['sha256'] == row['sha256'] and actual['bytes'] == row['bytes']
assert sorted(str(p.relative_to(D)) for p in D.rglob('*') if p.is_file()) == sorted([row['path'] for row in members] + ['index.json'])
print(json.dumps({'index': desc(D / 'index.json'), 'result': desc(D / 'results.json'),
    'receipt': desc(D / 'source-receipt.json'), 'indexedFiles': len(members), 'actualRegularFiles': len(members) + 1,
    'sourceDataChecks': 6924, 'pureMockChecks': 90, 'syntaxFiles': 17, 'benignHostSuitePassed': True,
    'actualBenchmarkActions': False}))
