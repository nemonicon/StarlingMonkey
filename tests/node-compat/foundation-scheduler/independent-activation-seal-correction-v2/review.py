"""Read-only source/seal review. Execute no compiler, package loader or guest.

The separately invoked Node host checks use fresh owned external outputs only.
This reviewer writes exclusively to its own new review packet.
"""
from pathlib import Path
import datetime
import hashlib
import json
import re
import sys

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
REPO = HERE.parents[3]
HOST = Path('/tmp/starling-node-compat/independent-activation-correction-v2-host-20261103')
ADAPTER = REPO/'host-apis/wasi-0.2.0/preview1-adapter-release/wasi_snapshot_preview1.wasm'
ADAPTER_SHA = '988224282d03fe0bd3c25b62344aef265b1a8e1f5804bdbc34d6442507fabcc0'
EXPECTED = [
    ('production-regression-candidate-v3','3064605fbf043c26e3d1bc85378b91d68c98be4034f4b6c5cf0f30f964ac61a2',22),
    ('production-followon-off-v1','a4812fe2e5429562b11f3e7ce1dbaf8cb7cb498726998ad5b473b16f05c61bbe',24),
    ('production-release-runner-v1','aa499593d97b718bd442e71d9325527a91ba38b199c9921aac6df834646512dc',36),
    ('production-regression-candidate-v4','d0411aafee83a0ab238d456a722cf753ba850a4aaf9f55bc820827d0746491a9',23),
    ('production-followon-off-v2','48117ef405f4861ead8c8d6abfd3623efa67596d20f8db755a50082111794376',24),
    ('production-release-runner-v2','820ca678e30905bbfcfccb358ff9198240b0fd9cc483cbf765e03dce992babe8',37),
    ('activation-seal-correction-v2','5bca72b50b2d9dfb8bd35969f3686ec8cb1232e6aa913a3a7d93caa21896f9b6',2),
]
verified = {}


def sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024*1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def read(path):
    return json.loads(path.read_bytes())


def checked(path, expected=None, size=None):
    path = Path(path).absolute()
    assert path.is_file() and not path.is_symlink(), path
    value = sha(path)
    assert expected is None or value == expected, path
    assert size is None or path.stat().st_size == size, path
    verified[str(path)] = {'path':str(path),'sha256':value,'bytes':path.stat().st_size}
    return value


def publish(name, value):
    with (HERE/name).open('x') as stream:
        json.dump(value,stream,indent=2)
        stream.write('\n')


assert sys.argv[1:] in [['before'],['after']]
phase = sys.argv[1]
for name,digest,count in EXPECTED:
    packet = BASE/name
    checked(packet/'index.json',digest)
    rows = read(packet/'index.json')['files']
    assert len(rows) == count and len({row['path'] for row in rows}) == count
    for row in rows:
        checked(packet/row['path'],row['sha256'],row['bytes'])

common = BASE/'production-regression-candidate-v4'
off = BASE/'production-followon-off-v2'
release = BASE/'production-release-runner-v2'
old_common = BASE/'production-regression-candidate-v3'
old_off = BASE/'production-followon-off-v1'
old_release = BASE/'production-release-runner-v1'
assert read(common/'pins.json') == read(old_common/'pins.json')
assert read(common/'pins.json')['variants'] == {'normal-off':None,'gc-off':None}

seals = {}
for packet,count in [(common,666),(off,733),(release,1409)]:
    document = read(packet/'input-freeze.json')
    rows = document['inputs']
    assert len(rows) == count and len({row['path'] for row in rows}) == count
    by_path = {}
    for row in rows:
        path = (packet/row['path']).resolve()
        checked(path,row['sha256'],row['bytes'])
        assert path not in by_path
        by_path[path] = row
    assert ADAPTER.resolve() in by_path
    assert by_path[ADAPTER.resolve()]['sha256'] == ADAPTER_SHA
    seals[packet] = by_path
checked(ADAPTER,ADAPTER_SHA)
old_rows = read(old_common/'input-freeze.json')['inputs']
new_rows = read(common/'input-freeze.json')['inputs']
assert [row for row in new_rows if (common/row['path']).resolve() != ADAPTER.resolve()] == old_rows
for parent,child in [(common,off),(common,release),(off,release)]:
    assert set(seals[parent]) <= set(seals[child]), (parent,child)

# Runtime guard/call bodies are unchanged. Preparation metadata is reviewed
# separately; it is not allowed to silently substitute different runner bodies.
common_equal = read(common/'source-receipt.json')['byteIdenticalRuntimeAndGuardFiles']
for row in common_equal:
    assert (common/row['path']).read_bytes() == (old_common/row['path']).read_bytes()
off_transformations = read(off/'runner-transformations.json')['runners']
assert len(off_transformations) == 5
for row in off_transformations:
    current = (off/row['generated']).read_text()
    previous = (old_off/row['generated']).read_text()
    assert current.replace('production-regression-candidate-v4','production-regression-candidate-v3') == previous
    restored = current
    for edit in reversed(row['changes']):
        assert restored.count(edit['after']) == edit['count']
        restored = restored.replace(edit['after'],edit['before'])
    original = REPO/row['original']
    checked(original,row['originalSha256'])
    assert restored.encode() == original.read_bytes()
release_transformations = read(release/'runner-transformations.json')['files']
assert len(release_transformations) == 9
for row in release_transformations:
    assert (release/row['generated']).read_bytes() == (old_release/row['generated']).read_bytes()
    restored = (release/row['generated']).read_text()
    for edit in reversed(row['changes']):
        assert restored.count(edit['after']) == edit['count']
        restored = restored.replace(edit['after'],edit['before'])
    original = REPO/row['original']
    checked(original,row['originalSha256'])
    assert restored.encode() == original.read_bytes()
for name in ['serial.mjs','historical-controls.json','runner-transformations.json']:
    assert (release/name).read_bytes() == (old_release/name).read_bytes()
assert (off/'entry-contract.json').read_bytes() == (old_off/'entry-contract.json').read_bytes()

# Check actual literal relative imports in new runtime siblings, including their
# copied bodies. This does not pretend to parse npm packages or generated text.
import_checks = []
for packet in [common,off,release]:
    files = list(packet.glob('run-*.mjs'))
    files += [packet/name for name in ['preflight.mjs','admission.mjs','job-plan.mjs','serial.mjs'] if (packet/name).exists()]
    for directory in ['runners','helpers','oracles']:
        files += list((packet/directory).glob('*.mjs'))
    for path in files:
        source = path.read_text()
        for spec in re.findall(r"(?:\bfrom\s*|\bimport\(\s*|\brequire\(\s*)['\"](\.[^'\"]+)['\"]",source):
            target = (path.parent/spec).resolve()
            assert target.is_file(), (path,spec)
            assert target in seals[packet], (path,spec,'not sealed')
            import_checks.append({'source':str(path.relative_to(REPO)),'literal':spec,'resolvedPath':str(target)})
assert "../production-regression-candidate-v4/preflight.mjs" in (off/'preflight.mjs').read_text()
assert "../production-regression-candidate-v4/preflight.mjs" in (release/'preflight.mjs').read_text()
assert 'production-followon-off-v1' not in (release/'job-plan.mjs').read_text()
assert 'production-followon-off-v2' in (release/'job-plan.mjs').read_text()
assert 'd0411aafee83a0ab238d456a722cf753ba850a4aaf9f55bc820827d0746491a9' in (off/'preflight.mjs').read_text()
for value in ['d0411aafee83a0ab238d456a722cf753ba850a4aaf9f55bc820827d0746491a9','48117ef405f4861ead8c8d6abfd3623efa67596d20f8db755a50082111794376']:
    assert value in (release/'preflight.mjs').read_text()
policy = read(BASE/'integration-candidate-v1/policy.json')
assert len(policy['expectedNativeSourceManifest']) == 306
for row in policy['expectedNativeSourceManifest']:
    checked(REPO/row['path'],row['sha256'])

if phase == 'before':
    publish('before.json',{'state':'SOURCE_AND_SEALS_CHECKED_BEFORE_HOST_TESTS','verifiedFiles':list(verified.values()),'literalRelativeImportChecks':import_checks,'runtimeInputs':[666,733,1409]})
    print(json.dumps({'phase':phase,'readPaths':len(verified),'importEdges':len(import_checks),'runtimeInputs':[666,733,1409]}))
else:
    before = read(HERE/'before.json')
    for row in before['verifiedFiles']:
        checked(Path(row['path']),row['sha256'],row['bytes'])
    host_checks = []
    for name,count in [('common',45),('off',28),('release',54),('unreviewed',6)]:
        path = HOST/(name+'.json')
        checked(path)
        report = read(path)
        assert report['tests'] == count
        if 'passed' in report:
            assert report['passed'] == count
        rows = report.get('results',report.get('checks'))
        assert len(rows) == count and all(row['passed'] for row in rows)
        for suffix in ['stdout','stderr']:
            checked(HOST/(name+'.'+suffix))
        host_checks.append({'name':name,'tests':count,'reportPath':str(path),'sha256':sha(path)})
    result = {'schemaVersion':1,'state':'INDEPENDENT_SOURCE_ONLY_ACTIVATION_SEAL_CORRECTION_V2_REVIEW_PASSED',
        'reviewedAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'packetIndices':[{'packet':name,'sha256':digest,'indexedEntries':count} for name,digest,count in EXPECTED],
        'preservedIndexedEntries':82,'newSiblingIndexedEntries':84,'summaryIndexedEntries':2,
        'runtimeInputCounts':[666,733,1409],'liveAdapterSha256':ADAPTER_SHA,'liveAdapterResolvedPath':str(ADAPTER.resolve()),
        'liveAdapterListedOnceInEachSeal':True,'descendantsContainFullParentInputSets':True,
        'oldCommon665ManifestRowsIdentical':True,'commonGuardAndRuntimeFilesIdentical':len(common_equal),
        'offRunnerDifferencesOnlyCommonImportWiring':5,'releaseBodyHelperOracleCopiesIdentical':9,
        'reverseEditsRestoreOriginalSourceBytes':14,'serialLifecycleAndHistoricalControlsUnchanged':True,
        'literalRelativeImportChecks':import_checks,'nativeSourceInputsUnchanged':306,
        'hostChecks':host_checks,'hostChecksTotal':133,
        'actualPinsRemainNull':True,'unreviewedPinOuterAndInnerStatesRejected':True,
        'oldPacketsAndTrackedInputsUnchangedAfterHostTests':True,'verifiedFiles':list(verified.values()),
        'limitations':[
            'This is source, byte-closure and host-only rejection/oracle evidence, not a positive artifact admission or runtime pass.',
            'The existing three host suites run no compiler, native builder, componentizer, Wasmtime or guest; the release host suite runs only redirected ordinary Node Path oracles.',
            'The extra six unreviewed-state tests use synthetic rejection shapes only; they do not fabricate a positive engine receipt or mutate checked-in pins.',
            'Input coverage is the finite reviewed local closure plus the existing checked package/toolchain contracts, not an independent whole-npm-tree archive or general JavaScript import parser.',
            'Real production freezes, independent fixed-artifact review and a newly reviewed pin/wiring/seal activation are still required.',
            'No public process/ALS/reset/classic-stream completeness, new host capability, GC-root isolation, performance or resource-benefit claim follows.'
        ],'nativeBuildGuestRepackOrHostExecutionByReview':False}
    publish('results.json',result)
    names = ['review.py','check-unreviewed.mjs','before.json','results.json','README.md']
    publish('index.json',{'state':'FROZEN_INDEPENDENT_SOURCE_ONLY_ACTIVATION_CORRECTION_V2_REVIEW','files':[{'path':name,'sha256':sha(HERE/name),'bytes':(HERE/name).stat().st_size} for name in names]})
    print(json.dumps({'state':result['state'],'hostChecks':133,'resultSha256':sha(HERE/'results.json'),'indexSha256':sha(HERE/'index.json')}))
