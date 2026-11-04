"""Collect completed corrected HTTP results; no host or guest execution."""
from pathlib import Path
import datetime
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = Path('/tmp/starling-node-compat/production-classic-corrected-http-v1/http')
COMPONENT_SHA = '24d76605a182ad21b0b0196570afd571737e549d2d89a1a4b30a542b4ab96efc'

def record(path):
    raw = path.read_bytes()
    return {'path': str(path), 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}

def read(path):
    return json.loads(path.read_bytes())

report_path = ROOT / 'combined-http-results.json'
audit = read(report_path)
assert audit['state'] == 'COMBINED_HTTP_BASELINE_AND_CLASSIC19_VALIDATED'
assert audit['componentSha256'] == COMPONENT_SHA
assert audit['requestsPerHost'] == 3 and audit['ordinaryClassicGroups'] == 19
assert audit['protectedAbortGroups'] == 29
assert audit['rawCombinedBodiesPreserved'] is True
assert audit['instanceReuseClaim'] is False and audit['requestIsolationClaim'] is False
phase_path = HERE / 'corrected-http-component-phase-root-review-v1.json'
assert record(phase_path)['sha256'] == 'b7cfeb6b2f4edf508fb12a4ff9e70fe7e4ae3a2f93ef6e5d83119557d06500e7'
evidence = [record(report_path), record(phase_path)]
for label in ('wasmtime', 'wash', 'audit'):
    stem = '/tmp/starling-node-compat/classic-corrected-http-' + label + '-v1.'
    terminal = read(Path(stem + 'terminal.json'))
    assert terminal['returncode'] == 0
    evidence.extend(record(Path(stem + suffix)) for suffix in ('stdout.log', 'stderr.log', 'terminal.json'))
for row in audit['artifacts']:
    assert record(Path(row['path'])) == row
    evidence.append(row)
manifest_path = Path(audit['nativeAdmission']['inputClosure']['path'])
manifest = read(manifest_path)
assert len(manifest['inputs']) == len(audit['sourceFilesVerified']) == 7496
for row in manifest['inputs']:
    path = (manifest_path.parent / row['path']).resolve()
    actual = record(path)
    assert actual['sha256'] == row['sha256'] and actual['bytes'] == row['bytes']
wt = read(ROOT / 'http-joint/wasmtime-v1/wasmtime-results.json')
wash = read(ROOT / 'http-joint-wasmcloud-results.json')
for result in (wt, wash):
    assert len(result['responses']) == 3
    assert result['process']['stopped'] is True
    assert result['process']['exitStatus'] == {'code': 0, 'signal': None}
    assert [row['body']['componentInstanceRequestCount'] for row in result['responses']] == [1, 1, 1]
assert wt['componentSha256'] == wash['component']['sha256'] == COMPONENT_SHA
assert record(Path(wt['command'][0]))['sha256'] == 'a85dec9fcbbad23d0e038e5a99604114dbe9aa77bc784e4bce0f33013eb33c1c'
assert record(Path(wash['host']['binaryPath']))['sha256'] == '365d896eaed3894f1c551a1ed7351c2aae9dfa5548ce82041ead92e6253d1954'
result = {'schemaVersion': 1, 'state': 'ROOT_CORRECTED_COMBINED_HTTP_BOTH_HOSTS_AND_AUDIT_TERMINAL_ZERO',
    'recordedAtUtc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'rootToolSession': 60088, 'wasmtimeWrapperRawExit': 0, 'washWrapperRawExit': 0,
    'finalAuditRawExit': 0, 'componentSha256': COMPONENT_SHA,
    'componentBytes': audit['component']['componentBytes'],
    'requestsPerHost': 3, 'counters': audit['counters'],
    'emittedImports': audit['component']['emittedImports'],
    'emittedExports': audit['component']['emittedExports'],
    'clockTypeOnly': audit['component']['clockDependency']['typeOnly'],
    'sourceRowsRehashed': 7496, 'evidence': evidence,
    'independentFinalResultReview': 'outstanding',
    'instanceReuseClaim': False, 'requestIsolationClaim': False,
    'compatibilityAccepted': False, 'performanceClaim': False,
    'limits': audit['limitations']}
path = HERE / 'corrected-http-combined-root-results.json'
with path.open('x') as stream:
    json.dump(result, stream, indent=2)
    stream.write('\n')
print(json.dumps({'path': str(path), 'sha256': record(path)['sha256'], 'evidenceFiles': len(evidence)}))
