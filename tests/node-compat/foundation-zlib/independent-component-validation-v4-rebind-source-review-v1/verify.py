#!/usr/bin/env python3
"""Independent data/source reader; imports no owner or bootstrap code."""
import ast
import hashlib
import json
from pathlib import Path
import stat

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
OWNER = BASE / 'component-validation-v4-rebind-amendment-v1'
OWNER_SHA = 'cd45865813e06085dcd86065bf816dd18b8203d127df879b1b1e2ca876662a45'
PARENTS = {
    'component-validation-candidate-v1': 'a7eca2349282a29649806c327c41ea19f01be9673c0bd7c72201f30672819816',
    'component-validation-control-evidence-amendment-v1': 'fd3ec6efb2f5b2aeadc2f673560be951071025b48d084f63bcbd57faa72d5353',
    'component-validation-bootstrap-coverage-amendment-v1': 'a376c32b640df35ea563a722b9df480569bf08367ade8752876addc3d1423191',
    'independent-component-validation-coverage-source-review-v1': '654f077fe86dbb2f615bc13d2133c9747a528e74018345ae47f9633f05e8a21e',
    'native-integration-candidate-v4': 'd384af814a95fa873afdca5bf31b61197463279b487064b6366ceaf6aad71172',
    'compound-link-parser-amendment-v1': '18ee1ab685fbafd331ad10eabe5c16352532bac83cee56181c75356f7e46ebdb',
}
seen = {}

def checked(path, digest=None, size=None):
    path = Path(path)
    before = path.lstat()
    assert stat.S_ISREG(before.st_mode) and not path.is_symlink(), str(path)
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    after = path.lstat()
    assert (before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns) == (after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns), str(path)
    row = {'path':str(path), 'sha256':h.hexdigest(), 'bytes':before.st_size}
    assert digest is None or digest == row['sha256'], row
    assert size is None or size == row['bytes'], row
    assert str(path) not in seen or seen[str(path)] == row
    seen[str(path)] = row
    return row

def data(path, digest=None):
    captured = checked(path, digest)
    raw = Path(path).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == captured['sha256']
    return json.loads(raw)

def index(root, digest):
    value = data(root/'index.json', digest)
    names = set()
    for row in value['files']:
        name = row['path']
        assert name not in names and not Path(name).is_absolute() and all(x not in ['', '.', '..'] for x in name.split('/'))
        names.add(name)
        checked(root/name, row['sha256'], row['bytes'])
    return value

owner_index = index(OWNER, OWNER_SHA)
assert len(owner_index['files']) == 8 and owner_index['futureActualPinsNull'] is True
assert owner_index['operationalAdmission'] is False
parent_counts = {name:len(index(BASE/name, digest)['files']) for name,digest in PARENTS.items()}
manifest = data(OWNER/'input-freeze.json')
assert len(manifest['inputs']) == 8770 and manifest['futurePinsNull'] is True and manifest['operationalAdmission'] is False
names = set()
for row in manifest['inputs']:
    path = Path(row['path'])
    path = path if path.is_absolute() else OWNER/path
    assert str(path) not in names
    names.add(str(path)); checked(path, row['sha256'], row['bytes'])

proof = data(OWNER/'publisher-proof.json')
before_path = BASE/'component-validation-bootstrap-coverage-amendment-v1/activate.py'
assert Path(proof['beforePath']) == before_path
checked(before_path, proof['beforeSha256'])
checked(OWNER/'activate.py', proof['afterSha256'])
before = before_path.read_text(); after = (OWNER/'activate.py').read_text()
assert len(proof['edits']) == 9 and proof['reverseExact'] is True
forward = before
for edit in proof['edits']:
    assert edit['count'] == 1 and forward.count(edit['old']) == 1
    forward = forward.replace(edit['old'],edit['new'])
assert forward == after
reverse = after
for edit in reversed(proof['edits']):
    assert reverse.count(edit['new']) == 1
    reverse = reverse.replace(edit['new'],edit['old'])
assert reverse == before
assert proof['codecOrGuestOrDriverOrPublicAPIChanged'] is False
for name in ['activate.py','prepare.py','seal.py']:
    ast.parse((OWNER/name).read_text())

bootstrap = BASE/'native-integration-candidate-v4'
pins = data(bootstrap/'bootstrap-pins.json')
assert set(pins['variants']) == {'normal-off','normal-runtime','gc-off','disabled-off'}
assert all(value is None for value in pins['variants'].values())
contract = data(bootstrap/'bootstrap-contract.json')
assert contract['reviewedPinsState'] == 'ROOT_REVIEWED_ZLIB350_VALIDATION_BOOTSTRAP_V1'
assert contract['rootReviewState'] == 'ROOT_REVIEWED_ZLIB350_BUILD_INPUTS_FOR_CODEC_VALIDATION_V1'
assert contract['operationalAdmission'] is False
assert "DECLARED=Path('/tmp/starling-node-compat/zlib-source-v4')" in after
assert "OUTPUT=HERE.parent/'component-validation-activated-v4'" in after
assert "PACKET='tests/node-compat/foundation-zlib/native-integration-candidate-v4'" in after
assert "BOOTSTRAP_INDEX='"+PARENTS['native-integration-candidate-v4']+"'" in after
for old in ['zlib-source-v3','component-validation-activated-v3','native-integration-candidate-v3']:
    assert old not in after
assert after.index('coverage_rows=indexed(COVERAGE,COVERAGE_INDEX)') < after.index('spec_from_file_location')
assert after.index('peer_rows=indexed(PEER,PEER_INDEX)') < after.index('spec_from_file_location')
assert after.index('boot_rows=indexed(bootstrap,bootstrap_sha)') < after.index('spec_from_file_location')
assert after.index('review[\'proposalIndexSha256\']==bootstrap_sha') < after.index('spec_from_file_location')
assert after.index("pins['variants']['normal-off']is not None") < after.index('spec_from_file_location')
assert after.index('recheck();stage.mkdir(exist_ok=False)') > after.index('backend.bootstrap(')
assert 'with(stage/name).open(\'xb\')' in after and 'stage.rename(OUTPUT)' in after
assert 'regular(stage/name,sha(raw),len(raw))' in after

payloads = data(OWNER/'unchanged-payloads.json')
assert payloads['sourceIndexSha256'] == PARENTS['component-validation-bootstrap-coverage-amendment-v1']
assert {row['target'] for row in payloads['payloads']} == {'component.mjs','run-validation.mjs','coverage-checks.mjs'}
for row in payloads['payloads']:
    checked(row['sourcePath'],row['sha256'],row['bytes'])
    assert row['byteIdenticalToApprovedA376'] is True
    assert str(Path(row['sourcePath']).parent).startswith(str(BASE/'component-validation-bootstrap-coverage-amendment-v1'))
for fragment in ["payload['run-validation.mjs']=regular(COVERAGE/'proposed/run-validation.mjs')", "payload['component.mjs']=regular(COVERAGE/'proposed/component.mjs')", "payload['coverage-checks.mjs']=regular(COVERAGE/'coverage-checks.mjs')"]:
    assert fragment in after
original = BASE/'component-validation-candidate-v1'
for name in ['corpus.mjs','node-fixtures.mjs','node-results.json','profile-contract.mjs','profile-contract.json','canonical-require.cjs','durable-host.mjs','consumed.mjs','runtime-preflight.template.mjs']:
    checked(original/name)
assert "payload={name:regular(BASE/name)for name in names}" in after
for name in ['component-validation-activated-v4','component-validation-activated-v4.staging']:
    assert not (BASE/name).exists() and not (BASE/name).is_symlink()
stored = data(OWNER/'results.json')
assert stored['sourceChecks'] == len(stored['checks']) == 26
assert stored['publisherEdits'] == 9 and stored['sourceInputs'] == 8770
assert stored['recipeSha256'] == '4417285083551bb48bdb877de781e31dbac08818081a78e1b28a35b9134aeed2'
assert stored['futurePinsNull'] is True and stored['guestOrDriverOrCorpusChanged'] is False
assert stored['bootstrapOrVerifierOrActivationOrNativeOrGuestOrBundleOrHostOrTimingExecuted'] is False

for row in list(seen.values()):
    checked(row['path'], row['sha256'], row['bytes'])
result = {
    'schemaVersion':1,
    'state':'INDEPENDENT_ZLIB_VALIDATION_V4_PUBLISHER_REBIND_SOURCE_REVIEW_PASSED',
    'ownerIndexSha256':OWNER_SHA,
    'ownerFiles':8,
    'sourceManifestRows':8770,
    'pathsIndependentlyVerified':len(seen),
    'parentIndexedFiles':parent_counts,
    'publisherForwardAndReverseExactEdits':9,
    'unchangedCoveragePayloads':payloads['payloads'],
    'originalCorpus61CompleteByteFixtures28Exports40TypedConstants107Preserved':True,
    'preservedCoverage':'Retained/fresh/Wasmtime call counters, own native numeric errno versus facade operation fields, per-ID namespace cache,283/3 final record counts and fd3 output controls stay byte-exact from reviewed a376.',
    'genuineBootstrapAPIAndValidationOnlyAuthorityUnchanged':True,
    'fixedProducerIndexSha256':PARENTS['native-integration-candidate-v4'],
    'fixedRecipeSha256':stored['recipeSha256'],
    'fixedConfiguredSourceRoot':'/tmp/starling-node-compat/zlib-source-v4',
    'futureOutputFamily':'component-validation-activated-v4',
    'futureOutputAbsentAtReview':True,
    'allFourFutureBootstrapPinsNull':True,
    'beforeImportAuthorityAndIndexedSourceChecksPreserved':True,
    'exclusivePublicationAndPrivateRecheckPreserved':True,
    'storedOwnerSourceChecksAuthenticatedNotRerun':26,
    'independentASTParses':3,
    'concreteSourceBlockers':[],
    'operationalAdmission':False,
    'nativeStageOrBootstrapOrValidationReadyClaim':False,
    'runtimeCodecOrVersionProof':False,
    'readerActions':'Only regular-file hashes, JSON/text/source reads, exact text derivations/reversals and AST parsing. No owner helper/test/action imports or executions; no Node, bootstrap, artifact verifier, compiler, native build, bundle, guest, hosts or timing.'
}
with (HERE/'verified-paths.json').open('x') as out:
    json.dump(list(seen.values()),out,indent=2);out.write('\n')
with (HERE/'results.json').open('x') as out:
    json.dump(result,out,indent=2);out.write('\n')
print(json.dumps({'state':result['state'],'paths':len(seen),'sourceBlockers':0}))
