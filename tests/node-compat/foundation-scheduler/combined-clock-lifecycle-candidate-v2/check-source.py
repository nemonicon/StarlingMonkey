"""Finite data/source checks. No imported owner module or process invocation."""
import ast
import hashlib
import json
from pathlib import Path
import stat

OWN = Path(__file__).resolve().parent
checks = 0
observed = {}


def need(value, message):
    global checks
    checks += 1
    if not value:
        raise AssertionError(message)


def checked(row):
    path = Path(row['path'])
    need(path.is_absolute(), 'original absolute descriptor: ' + str(path))
    need(stat.S_ISREG(path.lstat().st_mode), 'regular descriptor: ' + str(path))
    raw = path.read_bytes()
    need(len(raw) == row['bytes'], 'complete bytes: ' + str(path))
    need(hashlib.sha256(raw).hexdigest() == row['sha256'], 'complete hash: ' + str(path))
    observed[str(path)] = row
    return raw


def json_file(name):
    return json.loads((OWN / name).read_text())


refs = json_file('references.json')
target = refs['nativeTarget']
for key in ['engine', 'metadata', 'freezeReceipt', 'nativeSourceIndex']:
    checked(target[key])
for row in target['actualFrozenReview'].values():
    checked(row)
metadata = json.loads(checked(target['metadata']))
need(len(metadata) == 80, 'genuine complete80-field sidecar')
need(metadata['engineSha256'] == target['engine']['sha256'] == '355550f1d0bdc7455fd81ffbd739ac1453a56f3537b277eb644441d87434af3b', 'new355 engine identity')
need(metadata['entropyPolicy'] == 'off' and metadata['gcStress'] is False, 'normal-OFF; no GC pressure variant')
need(metadata['observedCMakeOptions']['CMAKE_BUILD_TYPE'] == 'Release', 'actual Release')
native = metadata['sourceManifest']
need(len(native) == 355 and len({r['path'] for r in native}) == 355, 'whole genuine355 native inventory')
source_root = Path(refs['nativeSourceRoot'])
for row in native:
    path = source_root / row['path']
    need(not Path(row['path']).is_absolute() and '..' not in Path(row['path']).parts, 'native relative layout')
    need(stat.S_ISREG(path.lstat().st_mode), 'frozen native regular file')
    need(hashlib.sha256(path.read_bytes()).hexdigest() == row['sha256'], 'actual frozen native: ' + row['path'])
embedding = metadata['componentizeSourceManifest']
need(len(embedding) == 3 and len({r['path'] for r in embedding}) == 3, 'genuine external embedding3')
for row in embedding:
    path = Path(refs['externalEmbeddingRoot']) / row['path']
    need(stat.S_ISREG(path.lstat().st_mode), 'external embedding regular file')
    need(hashlib.sha256(path.read_bytes()).hexdigest() == row['sha256'], 'actual frozen external embedding')
need(len(metadata['selectedModuleManifests']) == 11, 'all eleven manifests')
for row in metadata['selectedModuleManifests']:
    need(hashlib.sha256((source_root / row['path']).read_bytes()).hexdigest() == row['sha256'], 'whole selected manifest')
for name in ['resourceOwnershipPolicy', 'taskSelectionPolicy', 'combinedNativeSourcePolicy']:
    need(isinstance(metadata[name], dict) and bool(metadata[name]), 'real current policy: ' + name)
for row in refs['currentSource'] + refs['externalEmbedding'] + refs['mechanismAndHistoryReferences']:
    checked(row)
for row in refs['proposedCombinedBootstrapApi'].values():
    if isinstance(row, dict) and 'path' in row:
        checked(row)
checked(refs['nodeParserAndPureTests'])
for name, row in refs['originalFixtures'].items():
    original = checked(row)
    current = (OWN / 'fixtures' / name).read_bytes()
    if name == 'resource.mjs':
        before = b'// UNEXECUTED source fixture. Only a newly admitted resource342 engine may run it.\n'
        after = b'// UNCOMPILED/UNEXECUTED test source. Requires genuine new combined355 admission.\n'
        need(original.startswith(before) and current.startswith(after), 'one explicit target comment derivation')
        need(current.replace(after, before, 1) == original, 'all seven original case bodies reverse exactly')
    else:
        need(current == original, 'exact unchanged fixture: ' + name)
catalogue = json_file('fixture-catalogue.json')
need([r['id'] for r in catalogue['fixtures']] == ['resource', 'pure', 'fatal', 'init-fatal', 'clock-snapshot', 'surviving-interest'], 'full finite fixture catalogue')
for row in catalogue['fixtures']:
    checked(row['source']); checked(row['wit'])
    need(row['worldName'] == 'validation', 'actual WIT world')
    need(row['expectedNativeResidualImports'] == (['node:buffer'] if row['id'] in ['resource', 'pure'] else []), 'native import preservation')
    need(row['selectedInterfaces'] == ([] if row['id'] == 'pure' else ['wasi:clocks/wall-clock@0.2.10', 'wasi:clocks/monotonic-clock@0.2.10', 'wasi:io/poll@0.2.10']), 'exact selected clock scope')
    need(row['allOrdinaryCallsRequireSeparateRootAuthority'] is True, 'no workload authority')
resource = (OWN / 'fixtures/resource.mjs').read_text()
for case in range(7):
    need(('caseId===' + str(case)) in resource if case < 6 else 'const cleared=[]' in resource, 'seven-case branch retained')
clock = (OWN / 'fixtures/clock-snapshot.mjs').read_text()
need('const initialization = {dateNow: Date.now(), jobs: 0, moduleEvaluations: 1};' in clock, 'Date only captured at initialization')
need('initPerformanceCalled: false' in clock and 'nativeMonotonicOffsetObserved: false' in clock, 'no native offset projection')
for filename in ['clock-snapshot.mjs', 'surviving-interest.mjs']:
    text = (OWN / 'fixtures' / filename).read_text()
    need(not any(t in text for t in ['Math.random(', 'getRandomValues(', 'crypto.', 'reset(', 'DEBUG', 'gc(']), 'no unsafe/entropy/GC operation added')
schedule = json_file('schedules.json')
need(schedule['resource']['caseIds'] == list(range(7)), 'full seven case inventory')
need(schedule['resource']['retainedJco']['orderedCaseIds'] == list(range(7)) * 3, 'three retained rotations')
need(schedule['resource']['stockWasmtime42']['literalInvoke'] == 'validate()', 'real zero-argument WIT call')
need(schedule['resource']['totalInnerCaseExecutions'] == 3 * 7 + 7 + 3 * 7 == 49, 'finite proposed case count')
need(schedule['resource']['totalCallbackObservations'] == 7 * 14 == 98, 'callback count model')
need(schedule['resource']['totalNewIds'] == 7 * 46 == 322, 'timer ID count model')
requirements = json_file('requirements.json')
need(len(requirements['gates']) == 17 and all(r['actualResult'] is None for r in requirements['gates']), 'full unresolved scope')
gates = json_file('future-gates.json')
need(gates['sourceOnly'] is True and gates['compiled'] is False and gates['runtimeAcceptance'] is False, 'source only')
for key, value in gates.items():
    if key not in ['schemaVersion', 'sourceOnly', 'compiled', 'guestSyntaxChecked', 'runtimeAcceptance']:
        need(value is None, 'unissued gate: ' + key)
for path in OWN.glob('*.py'):
    ast.parse(path.read_text(), filename=str(path)); need(True, 'Python AST: ' + path.name)
facts = json_file('source-facts.json')
for row in facts['anchors']:
    raw = checked(row['file']).decode()
    need(raw.splitlines()[row['line'] - 1].find(row['literalAnchor']) >= 0, 'actual source line anchor')
report = {'schemaVersion': 1, 'kind': 'finite-lifecycle-source-checks', 'sourceChecks': checks,
          'directUniqueDescriptorsVerified': len(observed), 'nativeSourceFilesRehashed': 355,
          'externalEmbeddingFilesRehashed': 3, 'selectedWholeManifestsRehashed': 11,
          'rawMetadataFields': 80, 'historicalRecursiveProofClosureReplayed': False,
          'allSevenBodiesPreserved': True, 'newNativeDiagnosticImplemented': False,
          'ownerModulesImported': False, 'helperOrGuestOrClockOrHostWorkloadInvoked': False,
          'passed': True}
(OWN / 'source-check-results.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report))
