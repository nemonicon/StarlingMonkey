"""Inert actual Source module contracts only; never bootstrap/run/admit/recheck."""
from pathlib import Path
import ast,copy,hashlib,importlib.util,io,json,sys
P=Path(__file__).resolve().parent;S=P.parent/'node-crypto-hash-hmac-native-controller-candidate-v1';checks=[]
assert __debug__ and sys.dont_write_bytecode
summary=json.loads((P/'intake-summary.json').read_bytes());assert summary['passed']
def row(p):b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
ix=json.loads((S/'index.json').read_bytes());assert row(S/'index.json')==summary['sourceIndex']
for x in ix['files']:assert row(S/x['path'])==dict(x,path=str(S/x['path']))
def load(name):
 sp=importlib.util.spec_from_file_location('independent_inert_native357_'+name.replace('.','_'),S/name);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);assert Path(m.__file__).resolve()==S/name;return m
def yes(v,label):assert v,label;checks.append(label)
def refuses(fn,label):
 try:fn()
 except(AssertionError,ValueError,TypeError,KeyError):checks.append(label);return
 raise AssertionError('Unexpected acceptance '+label)
controller=load('controller.py');models=load('models.py');guard=load('io_guard.py');body=load('build_body.py')
refs=json.loads((S/'references.json').read_bytes());stage=json.loads(Path(refs['actualStageReview']['result']['path']).read_bytes());plan=json.loads(Path(refs['cachePlan']['path']).read_bytes());contract=json.loads((S/'future-source-review-contract.json').read_bytes())
yes(controller.OWN==S and Path(controller.__file__).resolve().parent==S,'actual own module context, no globals overridden')
for field,key in [('SOURCE','configuredSourceRoot'),('WORK','workRoot'),('FREEZE','freezeRoot')]:yes(getattr(controller,field)==Path(refs[key]),'actual literal '+field)
yes(controller.ENV_POLICY==contract['requiredFixedValues']['requiredRootEnvironmentPolicy'],'whole genuine environment contract')
models.stage(stage,refs);checks.append('unmodified actual7df full357 stage result accepted')
for key,value in [('state','old-source'),('schemaVersion',2),('sourceIndexSha256','0'*64),('controllerSourceIndexSha256','0'*64),('nativeSourceFiles',355),('selectedManifestCount',11),('reachableBaselineCommits',2),('actualNewEngine',{}),('engineExecuted',True),('nativeBuildExecuted',True),('grantsBuildOrAnyActionAuthority',True)]:
 bad=copy.deepcopy(stage);bad[key]=value;refuses(lambda bad=bad:models.stage(bad,refs),'stage refuses '+key)
for key,value in [('copiedSourceFiles',1641),('copiedEmbeddingReferenceFiles',4)]:
 bad=copy.deepcopy(stage);bad['coverage'][key]=value;refuses(lambda bad=bad:models.stage(bad,refs),'stage coverage refuses '+key)
models.cache_plan(plan,refs);checks.append('actual finite private cache plan accepted')
for mutate,label in [(lambda x:x.update(workRoot='/wrong'),'workRoot'),(lambda x:x['copies'].pop(),'missingseed'),(lambda x:x['copies'][0].update(target='../escape'),'target'),(lambda x:x.update(globalRustupCargoMutationAllowed=True),'globalmutation'),(lambda x:x.update(sdkTreeOrBuildObjectsReused=True),'objectreuse')]:
 bad=copy.deepcopy(plan);mutate(bad);refuses(lambda bad=bad:models.cache_plan(bad,refs),'cache refuses '+label)
for homes in [{},{'HOME':'','home':'lower','CODEX_HOME':'/kept'}]:
 parent={**homes,'SAFE':'yes','BASH_FUNC_a%%':'bad','BASH_FUNC_x()':'bad','BASH_ENV':'bad','ENV':'bad','SHELLOPTS':'bad','BASHOPTS':'bad','CDPATH':'bad','GLOBIGNORE':'bad'};original=copy.deepcopy(parent);clean,removed=controller.clean_environment(parent)
 yes(parent==original,'parent environment untouched');yes(clean=={**homes,'SAFE':'yes'},'only known startup fields removed');yes(set(removed)==set(parent)-set(clean),'removed names complete');yes(controller.clean_environment(clean)==(clean,[]),'clean entry stable')
 for key in ['HOME','home','CODEX_HOME']:yes((key in clean)==(key in parent)and clean.get(key)==parent.get(key),'preserve '+key)
 child=body.build_environment({**parent,'CMAKE_TOOLCHAIN_FILE':'bad','NODE_COMPAT_CRYPTO_HASH_HMAC':'0','NODE_CRYPTO_AUDITED_BORROW':'1','CARGO_TARGET_DIR':'bad','RUSTC_WRAPPER':'bad','NODE_OPTIONS':'bad','GIT_OPTIONAL_LOCKS':'1','CXX':'bad','LD_PRELOAD':'bad'},refs)
 yes(child['NODE_COMPAT_CRYPTO_HASH_HMAC']=='1'and child['NODE_CRYPTO_AUDITED_BORROW']=='0','HASHON/COPY/BORROWOFF actualenv');yes(child['NODE_COMPAT_ENTROPY_MODE']=='OFF'and child['NODE_COMPAT_GC_STRESS']==child['NODE_COMPAT_OOM_TESTING']=='0','OFF/noGC/OOM env');yes(child['GIT_OPTIONAL_LOCKS']=='0'and child['GIT_CONFIG_GLOBAL']==child['GIT_CONFIG_SYSTEM']=='/dev/null','staged Git metadata reads isolated/nonlocking');yes(not set(child)&{'CMAKE_TOOLCHAIN_FILE','CARGO_TARGET_DIR','RUSTC_WRAPPER','NODE_OPTIONS','CXX','LD_PRELOAD'},'override fields absent')
 for key in ['HOME','home','CODEX_HOME']:yes((key in child)==(key in parent)and child.get(key)==parent.get(key),'build preserve '+key)
for raw in [b'',b'x',bytes(range(256))*4097]:
 out=io.BytesIO();v=body.stream_copy(io.BytesIO(raw),out);yes(out.getvalue()==raw and v==dict(sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw)),'whole memory streaming '+str(len(raw)))
class Short:
 def write(self,b):return len(b)-1
refuses(lambda:body.stream_copy(io.BytesIO(b'ab'),Short()),'memory short-write refuses')
for name in ['relative','//double','/a/../b','/a/./b','/a\\b','/a\0b']:refuses(lambda name=name:guard.descriptor(dict(path=name,sha256='0'*64,bytes=0)),'descriptor rejects '+repr(name))
# Model input only: these prospective shapes are never Root authorities, file outputs or operational frames.
own=summary['sourceIndex'];build=json.loads((S/'future-build-root-authority.template.json').read_bytes());build.update(controllerIndex=own,controllerEntry=row(S/'controller.py'),nativeBuildAllowed=True,freezeAllowed=False,readOnlySourceAdmissionAllowed=False,postBuildNinjaListingAllowed=False)
models.root(build,own,refs,controller.ENV_POLICY);checks.append('unissued build template pure in-memory shape accepted')
for key,value in [('nativeSourceFiles',355),('rawMetadataFields',80),('selectedManifestCount',11),('auditedBorrowEnabled',True),('liveEvpSnapshotAdmission',True),('externalParentDeadlineSeconds',2400),('freezeAllowed',True),('readOnlySourceAdmissionAllowed',True),('postBuildNinjaListingAllowed',True)]:
 bad=copy.deepcopy(build);bad[key]=value;refuses(lambda bad=bad:models.root(bad,own,refs,controller.ENV_POLICY),'build shape refuses '+key)
freeze=json.loads((S/'future-freeze-root-authority.template.json').read_bytes());freeze.update(controllerIndex=own,controllerEntry=row(S/'controller.py'),nativeBuildAllowed=False,freezeAllowed=True,readOnlySourceAdmissionAllowed=True,postBuildNinjaListingAllowed=True)
refuses(lambda:models.root(freeze,own,refs,controller.ENV_POLICY),'freeze refuses absent actual BUILD proof')
proof=dict(schemaVersion=1,state=models.BUILD_STATE,verifiedPassed=True,sourceIndexSha256=models.SOURCE_SHA,controllerSourceIndexSha256=own['sha256'],nativeSourceFiles=357,externalEmbeddingSources=3,selectedManifestCount=12,rawMetadataFields=83,configuredSourceRoot=refs['configuredSourceRoot'],workRoot=refs['workRoot'],variant='normal-off',actualBuildResult=dict(path=refs['buildOutputRoot']+'/result.json',sha256='0'*64,bytes=0),engine=dict(path=refs['enginePath'],sha256='1'*64,bytes=0),metadata=dict(path=refs['enginePath']+'.build.json',sha256='2'*64,bytes=0),engineSha256='1'*64,metadataSha256='2'*64,inputHashes=dict(shapeOnly=True),referenceAliases=dict(shapeOnly=True),allOwnedProcessesRawZeroAndGone=True,engineExecuted=False,guestExecuted=False,cryptoOperationsInvoked=False,operationalAdmission=False,runtimeAcceptanceClaim=False,freezeAuthorityGranted=False)
models.build_proof(proof,{},own,refs);checks.append('future proof MODEL only, no actual83 metadata or action frame fabricated')
for key,value in [('state','old80'),('sourceIndexSha256','0'*64),('controllerSourceIndexSha256','0'*64),('nativeSourceFiles',355),('rawMetadataFields',80),('selectedManifestCount',11),('engineSha256','2'*64),('metadataSha256','1'*64),('allOwnedProcessesRawZeroAndGone',False),('cryptoOperationsInvoked',True),('freezeAuthorityGranted',True)]:
 bad=copy.deepcopy(proof);bad[key]=value;refuses(lambda bad=bad:models.build_proof(bad,{},own,refs),'future build shape refuses '+key)
# Compare real function signatures from authenticated source; do not import native producer/lifecycle/monitor.
provenance=json.loads((S/'api-provenance.json').read_bytes());calls=[]
for path,name,count in [(refs['monitorEntry']['path'],'monitor',6),(refs['lifecycleEntry']['path'],'monitor_owned_command',5),(refs['metadataModel']['path'],'validate_metadata',7),(refs['hashModel']['path'],'validate_hash_hmac_commands',5),(refs['hashModel']['path'],'validate_selected_manifests',3)]:
 t=ast.parse(Path(path).read_bytes());f=next(n for n in t.body if isinstance(n,ast.FunctionDef)and n.name==name);yes(len(f.args.posonlyargs+f.args.args)==count,'actual existing '+name+' signature');calls.append(dict(path=path,name=name,args=count))
result=dict(schemaVersion=1,passed=True,checks=len(checks),labels=checks,actualStageDataUsedUnmodified=True,actualModuleConstantsVerified=True,modelsImportedInOriginalOwnContext=True,sourceGlobalsOrNamespacesRebound=False,prospectiveRootAndProofModelsOnly=True,actualCompiled357MetadataObserved=False,actualRootOrPhaseAuthorityIssued=False,actualApiSignatures=calls,ownerAuthorizeBootstrapRunAdmitRecheckInvoked=False,nativeProducerHelperOrMonitorImported=False,cacheBuildFreezeEngineGuestCryptoActions=False)
(P/'pure-check-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(passed=True,checks=len(checks),operationalActions=False)))
