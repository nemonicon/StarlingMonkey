"""Independent read/hash/AST review only. Does not import owner modules."""
from pathlib import Path
import ast
import hashlib
import json

HERE=Path(__file__).resolve().parent
OWNER=HERE.parent/'native-integration-candidate-v2'
REPO=HERE.parents[3]
EXPECTED='9edf31c16af401ac688a4ab9bfe2a01f0338739a6554fc12caa3b2f8ba03a378'
POST=Path('/tmp/starling-node-compat/consumers355-v2-postseal-source-collection-v1.json')
POST_SHA='ac2070797f1330a2f2e921e428f4333246889cbbee0cfe9f843133cc2d69eec1'
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
index=doc(OWNER/'index.json',EXPECTED);assert len(index['files'])==59
for row in index['files']:checked(OWNER/row['path'],row['sha256'],row['bytes'])
freeze=doc(OWNER/'input-freeze.json');assert len(freeze['inputs'])==3420
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
assert len(collection['files'])==1173 and collection['originalRootFivePreparationHits']==[]
post_rows={row['path']:row for row in collection['files']};assert len(post_rows)==1173
for relative,row in planned.items():
    actual=post_rows[relative];assert(actual['sha256'],actual['bytes'])==(row['sha256'],row['bytes']);assert Path(actual['original']).resolve()==Path(row['original']).resolve()
prefix=str(OWNER.relative_to(REPO))
extra=[{'path':'index.json','sha256':EXPECTED,'bytes':(OWNER/'index.json').stat().st_size}]+index['files']
for row in extra:
    actual=post_rows[prefix+'/'+row['path']];assert(actual['sha256'],actual['bytes'])==(row['sha256'],row['bytes']);assert Path(actual['original']).resolve()==(OWNER/row['path']).resolve()
assert set(post_rows)==set(planned)|{prefix+'/'+row['path']for row in extra}
for row in collection['files']:checked(row['original'],row['sha256'],row['bytes'])
families=collection['families'];assert [r['role']for r in families]==['PREPARATION','PREPARATION','INDEXED_ONLY','INDEXED_ONLY','INDEXED_ONLY','INDEXED_ONLY']
assert [r['preparationRowsReadOnlyAtOriginalRoot']for r in families]==[2261,506,0,0,0,0]
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
OLD=OWNER.with_name('native-integration-candidate-v1')
old_index=doc(OLD/'index.json','ab88215a4d1348f4928ae83cc95a234c570b6a3d1809f622e3202eb370f88e25')
for row in old_index['files']:checked(OLD/row['path'],row['sha256'],row['bytes'])
hold=HERE.with_name('independent-native-integration-source-review-v1')
hold_index=doc(hold/'index.json','6e24de20da9c6940d8d213b1f21a2cc4bd149195010d391befb459fba5f6c5bc')
for row in hold_index['files']:checked(hold/row['path'],row['sha256'],row['bytes'])
successor=doc(OWNER/'successor-derivations.json');assert len(successor['edits'])==7
for path in {r['path']for r in successor['edits']}:
    before=checked(OLD/path).decode();after=checked(OWNER/path).decode();value=before
    edits=[r for r in successor['edits']if r['path']==path]
    for edit in edits:assert value.count(edit['old'])==edit['count'];value=value.replace(edit['old'],edit['new'])
    assert value==after
    for edit in reversed(edits):
        for offset in reversed(edit['afterOffsets']):assert value[offset:offset+len(edit['new'])]==edit['new'];value=value[:offset]+edit['old']+value[offset+len(edit['new']):]
    assert value==before
old_tools=doc(OLD/'artifact-tools/tool-pins.json');assert sha(checked(OWNER/'artifact-tools/tool-pins.json'))=='7ee0303e21e32da5b85bb7a6f2476a20f74a91c3cfef988274acc26f8fc5d9fe'
old_prefix=str(OLD.relative_to(REPO));new_prefix=str(OWNER.relative_to(REPO));old_rows={r['path']:r for r in old_tools['toolDependencies']};new_rows={r['path']:r for r in tools['toolDependencies']}
removed=set(old_rows)-set(new_rows);added=set(new_rows)-set(old_rows);assert len(removed)==len(added)==6
for name in removed:
    assert name.startswith(old_prefix+'/');new_name=new_prefix+name[len(old_prefix):];assert new_name in added
    assert {k:v for k,v in old_rows[name].items()if k!='path'}=={k:v for k,v in new_rows[new_name].items()if k!='path'}
for name in set(old_rows)&set(new_rows):assert old_rows[name]==new_rows[name]
for name in ['policy.json','layer-policy.py','admission-pins.json']:assert checked(OWNER/name)==checked(OLD/name)
assert doc(OWNER/'policy.json')['expectedNativeSourceManifest']==doc(OLD/'policy.json')['expectedNativeSourceManifest']
common=(OWNER/'artifact-tools/artifact_common.py').read_bytes().decode();tree=ast.parse(common);functions={n.name:n for n in tree.body if isinstance(n,ast.FunctionDef)}
reader=functions['verify_frozen_variant'];barrier=reader.body[1];assert isinstance(reader.body[0],ast.Assert)
assert isinstance(barrier,ast.Expr)and isinstance(barrier.value,ast.Call)and isinstance(barrier.value.func,ast.Name)and barrier.value.func.id=='tool_dependencies'and len(barrier.value.args)==1 and isinstance(barrier.value.args[0],ast.Name)and barrier.value.args[0].id=='REPO'
imports=[n for n in ast.walk(reader)if isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and n.func.attr in ['spec_from_file_location','exec_module','module_from_spec']]
assert imports and all(n.lineno>barrier.lineno for n in imports)
assert barrier.lineno<next(n.lineno for n in reader.body if isinstance(n,ast.Assign))
assert set(functions)=={n.name for n in ast.parse((OLD/'artifact-tools/artifact_common.py').read_bytes()).body if isinstance(n,ast.FunctionDef)}
for name in ['sha','checked','checked_below','tool_dependencies']:
    for node in ast.walk(functions[name]):
        assert not isinstance(node,(ast.Import,ast.ImportFrom))
        if isinstance(node,ast.Call)and isinstance(node.func,ast.Name):assert node.func.id not in ['exec','eval','__import__']
bootstrap=(OWNER/'artifact-tools/bootstrap-classifier.py').read_text();exporter=(OWNER/'artifact-tools/export-pin-candidate.py').read_text()
assert 'common.verify_frozen_variant(variant,return_receipt_digest=True)'in bootstrap
assert 'verify_frozen_variant(label, output, return_receipt_digest=True)'in exporter
ordering=doc(OWNER/'evidence/ordering-tests.json');assert ordering['passed']==19 and ordering['genuineVerifierOrHelperExecuted']is False
assert doc(OWNER/'evidence/source-tests.json')['passed']==50
fresh={}
for path in ['/tmp/starling-node-compat/consumers-source-v2','/tmp/starling-node-compat/consumers-v2-build','/tmp/starling-node-compat/production-consumers-v1']:
    p=Path(path);fresh[path]=not p.exists()and not p.is_symlink();assert fresh[path]
write('derivation-results.json',{'schemaVersion':1,'parent350Records':derivations,'successorEdits':7,'successorFiles':sorted({r['path']for r in successor['edits']}),'sixRewiredToolPaths':sorted(added),'unchangedLifecycleDefinitions':lifecycle,'nativePolicyHelperRecipeAndSevenPayloadsUnchanged':True,'ownerActionsInvoked':False})
write('verified-inputs.json',{'schemaVersion':1,'files':sorted(verified.values(),key=lambda r:r['path']),'ownerActionsInvoked':False})
write('results.json',{'schemaVersion':1,'state':'INDEPENDENT_CONSUMERS355_NATIVE_V2_SOURCE_REVIEW_PASSED','sourceIndexSha256':EXPECTED,'indexedFiles':59,'preparationInputs':3420,'nativeSources':355,'unchangedParent350Sources':348,'newSources':5,'parentReplacements':2,'nativeCpp':62,'nodePrivateCpp':6,'strictCpp':4,'separateEmbeddingCpp':1,'toolRows':767,'initialPlannedPaths':1119,'postSealPlannedPaths':1173,'postSealCollectionSha256':POST_SHA,'families':families,'parent350ForwardOffsetReverseFiles':8,'successorExactEdits':7,'toolOwnRowsRebound':6,'unchangedLifecycleDefinitions':7,'resolvedFinding':'C355-M1','universalBarrierSecondStatement':True,'configuredDependenciesAuthenticatedBeforeReceiptAndHelperImports':True,'barrierCoversBootstrapExporterAndDirectReader':True,'ownerStoredSourceChecksAuthenticatedNotRerun':50,'ownerStoredScratchOrderingChecksAuthenticatedNotRerun':19,'ownerStoredNodeSyntaxChecksAuthenticatedNotRerun':3,'allFuturePinsNull':True,'operationalAdmission':False,'freshFutureDestinationsObserved':fresh,'verifiedUniquePaths':len(verified),'findings':[],'limitations':['Source/AST/data review only; no355 staging, build, freeze, runtime or cost proof','Future independent artifacts and Root bootstrap authority remain required','Native framework closure767 does not provide component packaging closure','Prior v1/HOLD and original2261/506 preparation contexts remain historical; no relocation or old350metadata projection'], 'ownerHelperFactoryCodecStageBuildFreezerBootstrapVerifierBundleGuestHostActionsInvoked':False,'runtimeAcceptanceClaim':False})
print(json.dumps({'state':'SOURCE_PASS','files':59,'inputs':3420,'verifiedUniquePaths':len(verified),'parentDerivations':8,'successorEdits':7,'findings':0}))
