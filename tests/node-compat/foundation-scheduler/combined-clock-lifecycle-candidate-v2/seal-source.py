"""Compact Source publication only; run after source/pure/grammar data exists."""
import hashlib
import json
from pathlib import Path

OWN = Path(__file__).resolve().parent


def desc(path):
    raw = path.read_bytes()
    return {'path': str(path), 'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}


def put(name, value):
    (OWN / name).write_text(json.dumps(value, indent=2) + '\n')


assert not (OWN / 'index.json').exists(), 'sealed Source must remain immutable'
source = json.loads((OWN / 'source-check-results.json').read_text())
grammar = json.loads((OWN / 'evidence/grammar-summary.json').read_text())
pure = json.loads((OWN / 'evidence/pure.stdout.json').read_text())
assert source['passed'] and pure['passed'] and grammar['passed']
assert all(r['exitCode'] == 0 for r in grammar['commands'])
assert json.loads((OWN / 'evidence/pure.terminal.json').read_text())['exitCode'] == 0
put('results.json', {
    'schemaVersion': 1, 'state': 'UNCOMPILED_COMBINED355_CLOCK_LIFECYCLE_TEST_SOURCE_PREPARED_V2',
    'sourceOnly': True, 'sourcePreparationPassed': True, 'independentSourceReview': None,
    'correctedCollectorParentIndexSha256': '6cfcc7e4db1196e0ecc5339928f691f2020f8422b517dd87a7a6fc07498f3e84',
    'allSevenOriginalCaseBodiesPreserved': True, 'originalBodyChange': 'first target-comment only',
    'nativeSourceIndexSha256': '08bfe069eec4d0bbfa8ad09b81ac4e0667f380de847de860c58495258c28df65',
    'targetEngineSha256': '355550f1d0bdc7455fd81ffbd739ac1453a56f3537b277eb644441d87434af3b',
    'nativeSourceFiles': 355, 'externalEmbeddingSources': 3,
    'selectedWholeManifests': 11, 'rawMetadataFields': 80,
    'sourceCheck': source, 'pureChecks': pure['checks'], 'grammarChecks': len(grammar['commands']),
    'fixtureCatalogue': desc(OWN / 'fixture-catalogue.json'),
    'proposedCaseExecutions': 49, 'proposedCallbackObservations': 98, 'proposedNewIds': 322,
    'requiredGateCount': 17, 'actualRuntimeResults': None,
    'nativeCountersAdded': False, 'diagnosticVariantImplemented': False,
    'nativeInterestDropTeardownProved': False, 'snapshotOffsetProved': False,
    'actualCombinedAdmissionIssuedByThisPacket': False,
    'nativeHelperInvoked': False, 'guestInvoked': False, 'clockOrHostWorkloadInvoked': False,
    'resetOrGcPressureOrKeysInvoked': False, 'runtimeAcceptance': False,
    'adoptionOrSecurityOrPerformanceAuthority': None})
put('source-receipt.json', {
    'schemaVersion': 1, 'scope': 'compact uncompiled test sources and finite direct current355 source references',
    'result': desc(OWN / 'results.json'), 'references': desc(OWN / 'references.json'),
    'fixtureCatalogue': desc(OWN / 'fixture-catalogue.json'),
    'fixtureDerivation': 'Resource target comment changes; five original sources/WIT byte-identical; all original seven branch bodies byte-identical.',
    'newSources': ['fixtures/clock-snapshot.mjs', 'fixtures/surviving-interest.mjs', 'collectors.mjs', 'test-models.mjs'],
    'diagnosticProposalOnly': True, 'recursiveHistoricalTreesCopied': False,
    'actualWorkloadActionsInvoked': False, 'rootAuthority': None})
rows = []
for path in sorted(OWN.rglob('*')):
    assert not path.is_symlink(), 'Source packet links forbidden'
    if path.is_file() and path != OWN / 'index.json':
        row = desc(path); row['path'] = str(path.relative_to(OWN)); rows.append(row)
put('index.json', {'schemaVersion': 1, 'state': 'SEALED_SOURCE_ONLY_NOT_RUNTIME_AUTHORITY_V1', 'files': rows})
for name in ['index.json', 'results.json', 'source-receipt.json', 'fixture-catalogue.json']:
    print(json.dumps(desc(OWN / name)))
