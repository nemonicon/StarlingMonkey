"""M2 source seal only. Standard-library read/hash, no action execution."""
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

c = load(D / 'source-checks.json')
assert c['state'] == 'COMPLETE_RUNTIME_SOURCE_FAMILY_AUTHENTICATION_SOURCE_CHECKS_PASSED_V3'
assert (c['checks'], c['readHashScratchChecks'], c['syntaxFiles'], c['inputFiles']) == (3456, 23, 9, 918)
for row in load(D / 'source-inputs.json')['files']:
    assert desc(row['path']) == row
for row in load(D / 'module-edges.json')['modules']:
    assert desc(row['path']) == row
for item in load(D / 'scratch-evidence.json')['copies']:
    assert desc(item['original']['path']) == item['original']
    got = desc(D / item['copy'])
    assert got['sha256'] == item['original']['sha256'] and got['bytes'] == item['original']['bytes']
inherit = load(D / 'inherited-source.json')
for key in ['heldV1Index', 'heldV2Index', 'holdV1Index', 'holdV2Index', 'm2CorrectionContract', 'm1Verifier', 'originalBenignEvidence']:
    assert desc(inherit[key]['path']) == inherit[key]
for name in ['future-authority.template.json', 'future-plan-authority.template.json']:
    v = load(D / name)
    assert v['sourceIndexSha256'] is None and v['sourceIndependentReview'] is None
    assert v.get('actionAllowed', False) is False and v.get('dataPublicationAllowed', False) is False
    for field in ['phaseAuthority', 'quietWindowAuthority', 'warmNPlan', 'warmNMatchedPlan', 'preparedPlan', 'globalBudgetMs']:
        if field in v:
            assert v[field] is None
write('results.json', {'schemaVersion': 1, 'state': 'ZLIB_COST_PILOT_TIMING_COMPLETE_SOURCE_FAMILY_CHECKS_PASSED_V3',
    'sourceOnly': True, 'findingId': 'ZLIB-COST-PILOT-TIMING-V2-M2', 'findingCorrectedInSource': True,
    'heldV1Index': inherit['heldV1Index'], 'heldV2Index': inherit['heldV2Index'],
    'holdV1Index': inherit['holdV1Index'], 'holdV2Index': inherit['holdV2Index'],
    'm2CorrectionContract': inherit['m2CorrectionContract'], 'allOldMembersAndHoldsPreserved': True,
    'sourceDataChecks': 3456, 'actualInheritedFamilyAndScratchChecks': 23, 'syntaxFiles': 9, 'sourceInputFiles': 918,
    'fixedAncestorSourceFamilies': 2, 'ownV3SourceFamilyAuthenticatedAtRuntime': True,
    'runtimeSourceDependencyFiles': 28, 'workerStaticDependencyFiles': 20,
    'publicBootstrapAuthenticatesBeforeCustomBodyImport': True, 'privateIssuedSourceCapsuleRequiredByBodies': True,
    'initialAndFinalParentAndWorkerFamilyRechecksImplemented': True,
    'actualV1V2FamilyInitialAndPrivateRecheckPassed': True,
    'memberIndexAndMembershipTamperInitialAndRecheckRefused': True, 'importedDependencyTamperRefused': True,
    'm1StreamedVerifierUnchanged': True, 'protocolNativeGuestProviderComponentsCapsLoaderCollectorOwnedLifecycleChanged': False,
    'originalBenignEvidenceInheritedUnchanged': inherit['originalBenignEvidence'],
    'newHostLifecycleActionsExecuted': False, 'scratchSourceFixturesNeverImportedOrExecuted': True,
    'preflightOperationalHelperWorkerGuestProviderCodecNativeJcoWasmtimePilotTimingExecuted': False,
    'sourceIndependentReview': None, 'rootAction': None, 'planAuthority': None, 'phaseAuthority': None,
    'quietWindowAuthority': None, 'warmNPlan': None, 'globalBudgetMs': None,
    'runtimeAcceptanceClaim': False, 'operationalAdmission': False, 'sourcePromotionAllowed': False,
    'timingAllowed': False, 'actionAuthorityIssued': False})
write('source-receipt.json', {'schemaVersion': 1, 'state': 'AUTHOR_SEALED_COMPLETE_SOURCE_FAMILY_AUTHENTICATION_V3',
    'result': desc(D / 'results.json'), 'sourceChecks': desc(D / 'source-checks.json'),
    'heldV1Index': inherit['heldV1Index'], 'heldV2Index': inherit['heldV2Index'],
    'independentSourceReviewRequired': True, 'futureRootActionAuthority': None, 'operationalAdmission': False})
write('verification.json', {'schemaVersion': 1, 'state': 'V3_FINAL_SOURCE_AND_INHERITED_INPUT_REHASH_PASSED',
    'externalInputFilesRehashed': 918, 'runtimeModuleFilesRehashed': c['moduleFiles'],
    'allOldSourceAndBothHoldMembersUnchanged': True, 'benchmarkOrNewLifecycleActionsExecuted': False})
members = []
for path in sorted(D.rglob('*')):
    if path.is_file():
        row = desc(path)
        assert row['bytes'] <= 4 * 1024 * 1024 and path.suffix not in ('.pyc', '.tmp')
        members.append({'path': str(path.relative_to(D)), 'sha256': row['sha256'], 'bytes': row['bytes']})
write('index.json', {'schemaVersion': 1, 'state': 'SEALED_ZLIB_COST_PILOT_TIMING_COMPLETE_SOURCE_FAMILY_AMENDMENT_V3',
    'files': members, 'sourceOnly': True, 'authorChecksPassed': True, 'findingId': 'ZLIB-COST-PILOT-TIMING-V2-M2',
    'sourceIndependentReview': None, 'futureRootPhaseAuthority': None, 'operationalAdmission': False})
for row in members:
    got = desc(D / row['path'])
    assert got['sha256'] == row['sha256'] and got['bytes'] == row['bytes']
assert sorted(str(p.relative_to(D)) for p in D.rglob('*') if p.is_file()) == sorted([r['path'] for r in members] + ['index.json'])
print(json.dumps({'index': desc(D / 'index.json'), 'result': desc(D / 'results.json'),
    'receipt': desc(D / 'source-receipt.json'), 'indexedFiles': len(members), 'actualRegularFiles': len(members) + 1,
    'sourceDataChecks': 3456, 'readHashScratchChecks': 23, 'syntaxFiles': 9, 'sourceInputFiles': 918,
    'benchmarkOrNewLifecycleActions': False}))
