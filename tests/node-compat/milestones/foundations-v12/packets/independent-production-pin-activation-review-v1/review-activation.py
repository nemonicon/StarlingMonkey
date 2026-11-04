"""Read-only final activation seal/source checks; no runtime entry is imported."""
from pathlib import Path
import datetime
import hashlib
import json

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
REPO = HERE.parents[3]
HOST = Path('/tmp/starling-node-compat/independent-production-activation-host-v1')
verified = {}


def sha(path):
    value = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b''):
            value.update(chunk)
    return value.hexdigest()


def read(path):
    return json.loads(path.read_bytes())


def checked(path,digest=None,size=None):
    path = Path(path).absolute()
    assert path.is_file() and not path.is_symlink(),path
    value = sha(path)
    assert digest is None or digest == value,path
    assert size is None or path.stat().st_size == size,path
    verified[str(path)] = dict(path=str(path),sha256=value,bytes=path.stat().st_size)
    return value


trio = [
 ('production-regression-candidate-v5','0a65a102b89eaa68f583246c7a95d2dd6b5826b80931a6b59b9926a0c719b2cd',43,667),
 ('production-followon-off-v3','6354d57c9dc0a5161b0910a56c98886480d343e1aed8642c15debf1367081efd',37,755),
 ('production-release-runner-v3','70e60105aded35a37e9a53027dab4397824f9e6c5bb60039266bf02a988f9ed7',46,1442),
]
common,off,release,cap = [BASE/name for name in ['production-regression-candidate-v5','production-followon-off-v3','production-release-runner-v3','production-followon-capability-v3']]
for name,digest,count,_ in trio:
    packet = BASE/name
    checked(packet/'index.json',digest)
    rows = read(packet/'index.json')['files']
    assert len(rows) == count
    for row in rows:
        checked(packet/row['path'],row['sha256'],row['bytes'])
seals = {}
for packet,count in [(common,667),(off,755),(release,1442),(cap,778)]:
    checked(packet/'input-freeze.json')
    rows = read(packet/'input-freeze.json')['inputs']
    assert len(rows) == count
    mapping = {}
    for row in rows:
        path = (packet/row['path']).resolve()
        assert path not in mapping
        checked(path,row['sha256'],row['bytes'])
        mapping[path] = row
    seals[packet] = mapping
    adapter = (REPO/'host-apis/wasi-0.2.0/preview1-adapter-release/wasi_snapshot_preview1.wasm').resolve()
    assert mapping[adapter]['sha256'] == '988224282d03fe0bd3c25b62344aef265b1a8e1f5804bdbc34d6442507fabcc0'
assert set(seals[common]) <= set(seals[off]) <= set(seals[release])
assert sha(cap/'input-freeze.json') == 'd7e4dddef6da2d36aa091001c0d17adf4dbe1d0d07ff743fdd8318853e1a54ad'
assert not (cap/'index.json').exists()
assert read(cap/'http-component-pins.json')['component'] is None
assert (common/'pins.json').read_bytes() == (BASE/'production-pin-review-v1/common-pins.json').read_bytes()
assert (cap/'pins.json').read_bytes() == (BASE/'production-pin-review-v1/capability-pins.json').read_bytes()
helper = common/'dependency-bindings.mjs'
for packet in [off,release,cap]:
    doc = read(packet/'dependency-pins.json')
    assert doc['state'] == 'REVIEWED_SEALED_PARENT_INDICES_V1' and doc['schemaVersion'] == 1
    assert doc['commonIndexSha256'] == trio[0][1]
    assert helper.resolve() in seals[packet]
    assert (packet/'dependency-pins.json').resolve() in seals[packet]
    assert (common/'index.json').resolve() in seals[packet]
    assert (common/'input-freeze.json').resolve() in seals[packet]
    source = (packet/'preflight.mjs').read_text()
    assert "dependencySha256=hash(dependencyBytes)" in source
    assert "hash(await readFile(dependencyPath)),dependencySha256" in source
    assert source.index("dependencySha256=hash(dependencyBytes)") < source.index("JSON.parse(dependencyBytes)")
    assert source.index("Parent index pins changed during run") < source.index("await verifyInputClosure({manifestPath",source.index('async function recheck')) if packet!=cap else True
assert read(release/'dependency-pins.json')['offIndexSha256'] == trio[1][1]
assert (off/'index.json').resolve() in seals[release]

# Exact unchanged implementation bodies and finite routing-only edits.
old_common,old_off,old_release,old_cap = [BASE/name for name in ['production-regression-candidate-v4','production-followon-off-v2','production-release-runner-v2','production-followon-capability-v2']]
common_names = ['admission.mjs','preflight.mjs','run-core.mjs','run-allocator.mjs','run-allocator-gc.mjs','runners/allocator.mjs','runners/allocator-gc.mjs']
for name in common_names:
    assert (common/name).read_bytes() == (old_common/name).read_bytes()
for name in ['sync','runtime','late','callbacks','stream-web']:
    path = 'runners/'+name+'.mjs'
    assert (off/path).read_text().replace('production-regression-candidate-v5','production-regression-candidate-v4') == (old_off/path).read_text()
for row in read(release/'runner-transformations.json')['files']:
    assert (release/row['generated']).read_bytes() == (old_release/row['generated']).read_bytes()
for name in ['serial.mjs','historical-controls.json','runner-transformations.json','run-release.mjs','run-optional.mjs']:
    assert (release/name).read_bytes() == (old_release/name).read_bytes()
plan = (release/'job-plan.mjs').read_text().replace('production-regression-candidate-v5','production-regression-candidate-v4').replace('production-followon-off-v3','production-followon-off-v2')
assert plan == (old_release/'job-plan.mjs').read_text()
for name in ['admission.mjs','capabilities.mjs','native-safety.mjs']:
    assert (cap/name).read_bytes() == (old_cap/name).read_bytes()
for packet in [old_common,old_off,old_release,old_cap]:
    # A byte-identical predecessor index is retained in each successor history.
    successor = {old_common:common,old_off:off,old_release:release,old_cap:cap}[packet]
    assert (packet/'index.json').read_bytes() == (successor/'history/predecessor/index.json').read_bytes()
    checked(packet/'index.json')
    for row in read(packet/'index.json')['files']:
        checked(packet/row['path'],row['sha256'],row['bytes'])
live = read(cap/'computed-io-audit.json')['correctedLiveInputs']
assert len(live) == 8
for row in live:
    path = (REPO/row['path']).resolve()
    assert path in seals[cap]
    checked(path,row['sha256'],row['bytes'])

host_reports = []
for name,count in [('common',55),('off',32),('release',49),('capability',91)]:
    path = HOST/(name+'.json')
    checked(path)
    report = read(path)
    assert report['tests'] == report['passed'] == count
    assert all(row['passed'] for row in report.get('results',report.get('checks')))
    for suffix in ['stdout','stderr']:
        checked(HOST/(name+'.'+suffix))
    host_reports.append(dict(name=name,tests=count,path=str(path),sha256=sha(path)))
positive = []
for name,label in [('common-normal','normal-off'),('common-gc','gc-off'),('cap-normal','normal-off'),('cap-runtime','normal-runtime'),('cap-gc','gc-off')]:
    path = HOST/(name+'.json')
    checked(path)
    report = read(path)
    assert report['variant'] == label and report['consumedInputsRechecked'] is True
    assert report['sourceFilesVerified'] == 306 and report['componentizerCompilerGuestOrHostExecuted'] is False
    expected = read(BASE/'production-pin-review-v1/capability-pins.json')['variants'][label]
    assert report['engineSha256'] == expected['engineSha256']
    assert report['freezeReceiptSha256'] == expected['freezeReceiptSha256']
    for suffix in ['stdout','stderr']:
        checked(HOST/(name+'.'+suffix))
    positive.append(dict(name=name,variant=label,path=str(path),sha256=sha(path),engineSha256=report['engineSha256']))
for row in list(verified.values()):
    checked(row['path'],row['sha256'],row['bytes'])
result = dict(schemaVersion=1,state='INDEPENDENT_REVIEWED_PIN_ACTIVATION_SOURCE_AND_READ_ONLY_PREFLIGHT_PASSED',reviewedAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    pinDataReviewSha256=sha(HERE/'pin-data-results.json'),trio=[dict(packet=n,indexSha256=h,indexedFiles=c,runtimeInputs=i) for n,h,c,i in trio],
    capabilityManifestSha256=sha(cap/'input-freeze.json'),capabilityManifestInputs=778,capabilityFinalIndexExists=False,httpComponentPinRemainsNull=True,
    reviewedPinCopiesByteExact=True,commonRuntimeGuardFilesUnchanged=7,offBodiesRoutingOnly=5,releaseBodiesHelpersOraclesIdentical=9,
    serialLifecycleAndCaseControlsPreserved=True,dependencyDocPrimitiveShaCapturedAndRechecked=True,parentIndicesAndHelperSealed=True,
    descendantParentClosuresRetained=True,liveAdapterListedOnceEach=True,capabilityLiveComputedInputsVerified=8,
    scratchAndSourceHostChecks=227,hostReports=host_reports,actualReadOnlyPreflights=positive,verifiedFiles=list(verified.values()),
    noConcreteActivationBlockerFound=True,guestNativeRepackOrNinjaExecuted=False,oldPacketsOrExistingProofsModified=False,
    limitations=['This permits reviewed artifact admission into the sealed OFF family; it is not a release or runtime compatibility pass.',
                 'The capability code/778-source seal and three read-only admissions are checked; final capability index and actual HTTP component pin remain absent and require a separate phase.',
                 'Five Node preflights only read/hash metadata, sources, engine/host bytes and call source admission helpers. No componentizer, guest, compiler or host runtime was executed.',
                 'Fresh serial eight-job release, allocator GC, focused Events/getter, entropy and same-byte two-host HTTP gates remain necessary.',
                 'Getter/Symbol/GC co-ownership limitations, reset/ALS/request teardown and public process/whole-Node completeness are not closed.'])
with (HERE/'activation-results.json').open('x') as stream:
    json.dump(result,stream,indent=2);stream.write('\n')
print(json.dumps(dict(state=result['state'],resultSha256=sha(HERE/'activation-results.json'),readPaths=len(verified),actualReadOnlyPreflights=5,hostChecks=227)))
