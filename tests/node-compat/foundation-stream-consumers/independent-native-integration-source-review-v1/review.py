"""Independent read/hash/AST review only. Does not import owner modules."""
from pathlib import Path
import ast
import hashlib
import json

HERE=Path(__file__).resolve().parent
OWNER=HERE.parent/'native-integration-candidate-v1'
REPO=HERE.parents[3]
EXPECTED='ab88215a4d1348f4928ae83cc95a234c570b6a3d1809f622e3202eb370f88e25'
POST=Path('/tmp/starling-node-compat/consumers355-postseal-source-collection-v1.json')
POST_SHA='00ecfdabc6dd88539429c2e68ceab8f9c7c3c1175b436e78bb74f8ab1e15f742'
verified={}
def sha(data):return hashlib.sha256(data).hexdigest()
def checked(path,digest=None,size=None):
    path=Path(path);assert path.is_file()and not path.is_symlink(),path
    h=hashlib.sha256()
    with path.open('rb')as source:
        for block in iter(lambda:source.read(1024*1024),b''):h.update(block)
    value=h.hexdigest();length=path.stat().st_size
    if digest is not None:assert value==digest,path
    if size is not None:assert length==size,path
    previous=verified.setdefault(str(path),{'path':str(path),'sha256':value,'bytes':length});assert previous['sha256']==value
    return path.read_bytes()
def doc(path,digest=None):return json.loads(checked(path,digest))
def write(name,value):
    with(HERE/name).open('x')as out:json.dump(value,out,indent=2);out.write('\n')
index=doc(OWNER/'index.json',EXPECTED);assert len(index['files'])==53
for row in index['files']:checked(OWNER/row['path'],row['sha256'],row['bytes'])
freeze=doc(OWNER/'input-freeze.json');assert len(freeze['inputs'])==3357
for row in freeze['inputs']:
    checked(row['path'],row['sha256'],row['bytes']);assert str(Path(row['path']).resolve())==row['realpath']
transforms=doc(OWNER/'tool-transformations.json')['records'];assert len(transforms)==8
derivations=[]
for record in transforms:
    before=checked(record['origin'],record['beforeSha256']).decode();after=checked(OWNER/record['path'],record['afterSha256']).decode();value=before
    for edit in record['edits']:
        assert value.count(edit['old'])==edit['count'];value=value.replace(edit['old'],edit['new'])
    assert value==after
    for edit in reversed(record['edits']):
        for offset in reversed(edit['afterOffsets']):
            assert value[offset:offset+len(edit['new'])]==edit['new'];value=value[:offset]+edit['old']+value[offset+len(edit['new']):]
    assert value==before;derivations.append({'path':record['path'],'beforeSha256':record['beforeSha256'],'afterSha256':record['afterSha256'],'edits':len(record['edits']),'forwardAndOffsetReverseExact':True})
def definitions(text):
    lines=text.splitlines(keepends=True)
    return{node.name:''.join(lines[node.lineno-1:node.end_lineno])for node in ast.parse(text).body if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef))}
launcher=next(row for row in transforms if row['path']=='artifact-tools/build-one.py')
old_defs=definitions(Path(launcher['origin']).read_bytes().decode());new_defs=definitions((OWNER/launcher['path']).read_bytes().decode())
lifecycle=['error_record','ExternalTermination','OwnedSession','monitor_owned_command','prepare_output','publish_result','finalize_status']
for name in lifecycle:assert old_defs[name]==new_defs[name],name
policy=doc(OWNER/'policy.json');native=policy['expectedNativeSourceManifest'];assert len(native)==355 and len({r['path']for r in native})==355
consumer=REPO/'tests/node-compat/foundation-stream-consumers/production-text-json-candidate-v2'
assert checked(OWNER/'policy.json')==checked(consumer/'policy.json')
assert checked(OWNER/'layer-policy.py')==checked(consumer/'layer-policy.py')
assert checked(OWNER/'admission-pins.json')==checked(consumer/'admission-pins.json')
parent=REPO/'tests/node-compat/foundation-zlib/native-integration-candidate-v4'
before={r['path']:r['sha256']for r in doc(parent/'policy.json')['expectedNativeSourceManifest']};after={r['path']:r['sha256']for r in native}
assert len(before)==350 and sum(before[p]==after[p]for p in before)==348
assert len(set(after)-set(before))==5
origins=doc(OWNER/'tool-origins.json')['files'];tools=doc(OWNER/'artifact-tools/tool-pins.json');assert len(origins)==len(tools['toolDependencies'])==767
assert {r['path']:(r['sha256'],r['bytes'])for r in origins}=={r['path']:(r['sha256'],r['bytes'])for r in tools['toolDependencies']}
planned={}
for row in origins:
    checked(row['original'],row['sha256'],row['bytes']);planned[row['path']]={**row,'roles':['TOOL']}
edits=doc(consumer/'native-derivations.json');proposed=set(edits['addedSources']+[r['path']for r in edits['changes']])
for row in native:
    original=consumer/'proposed'/row['path']if row['path']in proposed else Path('/tmp/starling-node-compat/zlib-source-v4')/row['path']
    data=checked(original,row['sha256']);old=planned.get(row['path'])
    if old:assert(old['sha256'],old['bytes'])==(row['sha256'],len(data));old['roles'].append('NATIVE');old['original']=str(original)
    else:planned[row['path']]={**row,'bytes':len(data),'original':str(original),'roles':['NATIVE']}
assert len(planned)==1119
five=['builtins/node-compat/classic-streams/classic-core.generated.mjs','builtins/node-compat/classic-streams/transformation-receipt.json','builtins/node-compat/classic-streams/factories.generated.h','tests/node-compat/build-engine.sh','tests/node-compat/classic-streams-admission.mjs']
for p in five:assert Path(planned[p]['original']).resolve()!=(REPO/p).resolve()
assert planned['tests/node-compat/build-engine.sh']['sha256']=='3a5fa8cd58d3948c373b59ff486eae5792ae7ec1b51ed47f43f4edc5b39b4c68'
post=doc(POST,POST_SHA);assert post['sourceIndexSha256']==EXPECTED and post['stageMainExecuted']is False and post['artifactHelperExecuted']is False
collection=post['sourceCollection'];assert collection['nativeRows']==355 and collection['toolRows']==767 and collection['stageCreated']is False
assert len(collection['files'])==1167 and collection['originalRootFivePreparationHits']==[]
post_rows={row['path']:row for row in collection['files']};assert len(post_rows)==1167
for relative,row in planned.items():
    actual=post_rows[relative];assert(actual['sha256'],actual['bytes'])==(row['sha256'],row['bytes']);assert Path(actual['original']).resolve()==Path(row['original']).resolve()
prefix=str(OWNER.relative_to(REPO))
extra=[{'path':'index.json','sha256':EXPECTED,'bytes':(OWNER/'index.json').stat().st_size}]+index['files']
for row in extra:
    actual=post_rows[prefix+'/'+row['path']];assert(actual['sha256'],actual['bytes'])==(row['sha256'],row['bytes']);assert Path(actual['original']).resolve()==(OWNER/row['path']).resolve()
assert set(post_rows)==set(planned)|{prefix+'/'+row['path']for row in extra}
for row in collection['files']:checked(row['original'],row['sha256'],row['bytes'])
families=collection['families'];assert [r['role']for r in families]==['PREPARATION','PREPARATION','INDEXED_ONLY','INDEXED_ONLY']
assert [r['preparationRowsReadOnlyAtOriginalRoot']for r in families]==[2261,506,0,0]
for family in families:
    root=Path(family['root']);idx=doc(root/'index.json',family['indexSha256'])
    for row in idx['files']:checked(root/row['path'],row['sha256'],row['bytes'])
    if family['role']=='PREPARATION':
        manifest=doc(root/family['preparationManifest']);rows=manifest['inputs'if family['preparationManifest']=='input-freeze.json'else'files']
        for row in rows:
            path=Path(row['path']);path=path if path.is_absolute()else root/path;checked(path,row['sha256'],row['bytes'])
    else:assert family['preparationManifest']is None
for filename in ['runtime-pins.json','bootstrap-pins.json']:
    pins=doc(OWNER/filename);assert all(v is None for v in pins['variants'].values())and pins['operationalAdmission']is False
for path in OWNER.rglob('*.py'):ast.parse(path.read_bytes())
common=(OWNER/'artifact-tools/artifact_common.py').read_text();bootstrap=(OWNER/'artifact-tools/bootstrap-classifier.py').read_text()
common_start=common.index('def verify_frozen_variant(');common_body=common[common_start:]
codec_import=common_body.index("spec_from_file_location('frozen_zlib_codec_evidence'")
layer_import=common_body.index("spec_from_file_location('frozen_zlib_source_layer'")
assert codec_import<layer_import
assert 'tool_dependencies('not in common_body[:codec_import]
assert bootstrap.index('common.verify_frozen_variant(')<bootstrap.index('metadata-admission.mjs')
finding={'id':'C355-M1','severity':'source-authentication-order-blocker-before-bootstrap','file':'artifact-tools/artifact_common.py','symbol':'verify_frozen_variant',
 'configuredImport':'REPO/tests/node-compat/foundation-zlib/native-integration-candidate-v4/codec-evidence.py',
 'observation':'Current configured codec code is imported and validate_witness executes before any current-REPO tool_dependencies check on bootstrap/exporter direct frozen-verifier paths. Frozen767 copies are checked, which does not authenticate the separate configured path. Child layer later authenticates parent85, after codec execution.',
 'caller':'artifact-tools/bootstrap-classifier.py bootstrap() calls common.verify_frozen_variant before metadata-admission current767 checks; exporter candidate() calls it directly.',
 'boundedScope':'Build-one and freezer paths call tool_dependencies before this point. This finding concerns the new355 bootstrap/direct frozen-verifier path; no prior350 accepted evidence is relabelled.',
 'minimalSuccessor':'Before any configured helper import, authenticate the current selected codec path against its exact767 tool-pins row, or call existing common.tool_dependencies(REPO) early in verify_frozen_variant. Preserve sealedab882 and prove refusal before import with a pure stub/source test in a new successor.'}
write('derivation-results.json',{'schemaVersion':1,'records':derivations,'unchangedLifecycleDefinitions':lifecycle,'ownerActionsInvoked':False})
write('verified-inputs.json',{'schemaVersion':1,'files':sorted(verified.values(),key=lambda r:r['path']),'ownerActionsInvoked':False})
write('results.json',{'schemaVersion':1,'state':'INDEPENDENT_CONSUMERS355_NATIVE_SOURCE_REVIEW_HOLD','sourceIndexSha256':EXPECTED,'indexedFiles':53,'preparationInputs':3357,'nativeSources':355,'unchangedParentSources':348,'newSources':5,'parentReplacements':2,'nativeCpp':62,'nodePrivateCpp':6,'strictCpp':4,'separateEmbeddingCpp':1,'toolRows':767,'initialPlannedPaths':1119,'postSealPlannedPaths':1167,'postSealCollectionSha256':POST_SHA,'families':families,'forwardOffsetReverseFiles':8,'unchangedLifecycleDefinitions':len(lifecycle),'allFuturePinsNull':True,'operationalAdmission':False,'findings':[finding], 'otherCriticalReadNotes':['Native355 admission calls the actual355 helper; no old350 metadata projection observed.','Consumer OFF keeps zlibON and62/private6; RuntimeOnly remains null/unbuilt.','Source clone is local --no-local/--no-checkout, detached54b, without alternates/hardlinks, and permits only declared overlays; publisher remains unexecuted.','Original2261+506 preparation rows are interpreted only at their original contexts. Peer/SDK are indexed only.','Forced selected js-confdefs and compound-link codec contracts, complete Rust/OpenSSL, after-only embedding and actual textcodec-before-Node NS_DEF witnesses are inherited as source gates, not new runtime proof.','767 is native artifact framework closure, not component packaging closure.'], 'verifiedUniquePaths':len(verified),'ownerHelperFactoryCodecStageBuildFreezerBootstrapVerifierBundleGuestHostActionsInvoked':False,'runtimeAcceptanceClaim':False})
print(json.dumps({'state':'HOLD','files':53,'inputs':3357,'verifiedUniquePaths':len(verified),'derivations':8,'findings':1}))
