"""Pure source/data checks for this plan. Does not invoke any named API."""
from pathlib import Path
import ast
import hashlib
import json

HERE = Path(__file__).resolve().parent

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def load(name):
    return json.loads((HERE / name).read_text())

manifest = load('source-inputs.json')
assert len(manifest['files']) == 295
for row in manifest['files']:
    path = Path(row['path'])
    assert sha(path) == row['sha256'] and path.stat().st_size == row['bytes']
    assert str(path.resolve()) == row['canonicalPath']
assert manifest['oldNestedConsumedRowsFollowed'] is False
citations = load('source-citations.json')['citations']
assert len(citations) == 49
for row in citations.values():
    value = Path(row['path']).read_text()
    assert sha(row['path']) == row['sha256']
    assert value.splitlines()[row['line'] - 1].find(row['text'].splitlines()[0]) >= 0
    assert row['text'] in value
runtime = load('runtime-only-build.template.json')
assert sha(HERE / 'runtime-only-build.template.json') == '096ad77302cd8f0fcc0fd78a07e557af1dbad5b67d3b5a6e51f8f8dae8f680e1'
assert runtime['ownerCodeChangeRequiredForTheseLabels'] is False and runtime['actionsAllowed'] is False
assert runtime['jobs'] == 1 and runtime['requiredStartFreeBytes'] == 2 * 1024**3 and runtime['stopBelowFreeBytes'] == 800 * 1024**2
assert max(row['utf8Bytes'] for row in runtime['basenameChecks']) == 138
assert all(row['utf8Bytes'] <= 255 for row in runtime['basenameChecks'])
# Its pre-build absence observation is not reinterpreted after Root's separate build.
jobs = load('release-jobs.template.json')
assert len(jobs['jobs']) == 8 and len(jobs['optionalModules']) == 6
assert jobs['futureComponentCount'] is None and jobs['historical40NotPresumed']
bindings = load('gate-bindings.template.json')
assert bindings['RootReleaseAuthority'] is None and bindings['RootHttpComponentPhase'] is None
assert bindings['normalRuntimePin'] is None and bindings['actionsAllowed'] is False
authority = load('future-authority.json')
assert authority['actionsAllowed'] is False and authority['operationalAdmission'] is False
assert all(value is None for key, value in authority.items() if key not in ['schemaVersion', 'state', 'operationalAdmission', 'acceptanceClaim', 'performanceClaim', 'actionsAllowed'])
plan = load('gate-order.json')
assert len(plan['steps']) == 12 and plan['actionsAllowed'] is False
assert plan['OFFWorkDoesNotDependOnRuntimeFourthBuild'] and plan['HttpAndFocusedRuntimeRequireFourthPin']
assert len(load('integration-audit.json')['rows']) == 10
assert load('integration-audit.json')['oldHelpersDeclaredRerunnable'] is False
chain = load('registrar-ancestry-required.json')['chain']
assert [row['sources'] for row in chain] == [306, 342, 350, 355]
assert chain[-1]['sha256'] == '879b74c797eac19f07e86fa4e93bfa29578e11d0250fc3fb00439167580af9f6'
wasi = load('selected-wasi.template.json')
assert wasi['scalarNormalOff'] == wasi['scalarGcOff'] == wasi['consumerDisabledOff'] == []
assert wasi['scalarNormalRuntime'] == ['wasi:random/random@0.2.10']
assert len(wasi['httpNormalRuntime']) == 6 and wasi['clockCallableImportsRequired'] == []
probe = (HERE / 'consumer-http-probe.template.mjs').read_text()
assert "from 'node:stream/consumers'" in probe and 'new Uint8Array([0xe2])' in probe and 'await json(jsonChunks())' in probe
assert 'Buffer.from([' not in probe and 'fetch(' not in probe
for path in HERE.glob('*.py'):
    ast.parse(path.read_text(), filename=str(path))
results = {'schemaVersion':1,'state':'CONSUMERS355_RELEASE_HOST_SOURCE_PLAN_CHECKS_PASSED_ACTIONS_HELD',
    'sourceReferences':295,'sourceCitations':49,'integrationRows':10,'dependencySteps':12,
    'existingEightJobsAndSixOptionalsMapped':True,'runtimeProducerAlreadySupportsLabel':True,
    'runtimeTemplateSha256Preserved':sha(HERE/'runtime-only-build.template.json'),
    'runtimeBuildObservedOrCertifiedByThisPacket':False,'sourceAndDescriptorReferencesHashExact':True,
    'oldConsumedRowsOrOriginalContextsReinterpreted':False,'newAuthority':None,
    'ownerOrPreflightOrBootstrapOrNativeOrBundleOrGuestOrHostOrTimingExecuted':False,
    'runnableReadinessOrOperationalAdmissionOrAcceptanceOrPerformanceClaim':False}
(HERE/'results.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps(results))
