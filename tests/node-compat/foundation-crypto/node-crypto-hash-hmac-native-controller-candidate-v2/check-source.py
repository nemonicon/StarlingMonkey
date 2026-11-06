"""Own Source/pure/AST checks only. Never calls authorize/main/phase/owner helpers."""
from pathlib import Path
import ast,copy,hashlib,importlib.util,io,json,os,stat
OWN=Path(__file__).resolve().parent

def load(name):
 s=importlib.util.spec_from_file_location('source_only357_'+name.replace('.','_'),OWN/name);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def save(name,v):(OWN/name).write_text(json.dumps(v,indent=2)+'\n')
io_guard=load('io_guard.py');controller=load('controller.py');models=load('models.py');body=load('build_body.py');checks=[]
def need(value,label):assert value,label;checks.append(label)
def fails(fn,label):
 try:fn()
 except(AssertionError,ValueError,KeyError,TypeError):checks.append(label);return
 raise AssertionError('Accepted '+label)
refs=json.loads((OWN/'references.json').read_bytes());source=json.loads((OWN/'source-inputs.json').read_bytes());cap=io_guard.Capture()
for r in source['files']:cap.add(r)
for ix in source['families']:cap.family(ix)
need(len(source['files'])==len({r['path']for r in source['files']}),'unique declared original inputs')
stage=io_guard.read(refs['actualStageReview']['result']);models.failure(io_guard.read(refs['failedBuildReview']['result']),refs);cap.proof(refs['failedBuildReview'],refs['failedBuildContract'],'INDEPENDENT_NODE_CRYPTO_HASH_HMAC357_BUILD_V2_ROOT_PREFLIGHT_AND_FAILURE_REVIEW_PASSED_V1')
models.stage(stage,refs);checks.append('actual C stage model/full357/12/1642+3/no-action wire')
_,contract=cap.proof(refs['actualStageReview'],refs['actualStageContract'],models.STAGE_STATE);checks.append('actual complete stage contract fixed/descriptors/properties/coverage')
journal=io_guard.read(refs['stageJournal']);need(len(journal['copies'])==1642 and len(journal['embeddingDataCompleted'])==3,'actual stage role counts')
for r in journal['copies']:
 d=dict(path=str(controller.SOURCE/r['path']),sha256=r['sha256'],bytes=r['bytes']);cap.add(d);s=io_guard.checked(d).stat();need(stat.S_IMODE(s.st_mode)==0o600 and s.st_nlink==1,'live staged copy '+r['path'])
for r in journal['embeddingDataCompleted']:cap.add(r['target'])
need(controller.OWN==OWN and Path(controller.__file__).resolve().parent==OWN,'genuine actual module constants')
need(controller.SOURCE==Path(refs['configuredSourceRoot'])and controller.WORK==Path(refs['workRoot'])and controller.FREEZE==Path(refs['freezeRoot']),'new original contexts no global rebinding')
need(not controller.WORK.exists()and not controller.FREEZE.exists(),'new WORK/FREEZE absent; Source checks do not create outputs')
for r in refs['hostTools']:
 selected=__import__('shutil').which(r['name'],path=refs['hostPath']);need(selected is not None and str(Path(selected).resolve())==r['executable']['path'],'actual command alias '+r['name']);cap.add(r['executable'])
plan=io_guard.read(refs['cachePlan']);models.cache_plan(plan,refs);checks.append('four cache copies/new private homes/no SDK tree or object reuse')
need(sum(r['source']['bytes']for r in plan['copies'])==plan['totalCopyBytes'],'cache finite byte count')
for r in plan['copies']:need(stat.S_IMODE(io_guard.checked(r['source']).stat().st_mode)==r['sourceMode'],'cache original mode '+r['target'])
original={'HOME':'/test/home','home':'lower','CODEX_HOME':'/test/codex','BASH_FUNC_cmake%%':'malicious','BASH_FUNC_x()':'x','BASH_ENV':'start','ENV':'start','SHELLOPTS':'x','BASHOPTS':'x','CDPATH':'x','GLOBIGNORE':'*','SAFE':'yes'}
clean,names=controller.clean_environment(original);need(set(names)==set(original)-{'HOME','home','CODEX_HOME','SAFE'}and clean=={k:original[k]for k in ['HOME','home','CODEX_HOME','SAFE']},'function prefixes and exact startup entries removed; homes preserved')
need(controller.clean_environment(clean)==(clean,[]),'already-clean policy stable')
child=body.build_environment({**original,'CARGO_TARGET_DIR':'old','RUSTC_WRAPPER':'old','NODE_OPTIONS':'old','GIT_CONFIG_COUNT':'9','CXX':'old','NODE_CRYPTO_AUDITED_BORROW':'1'},refs)
need(child['NODE_CRYPTO_AUDITED_BORROW']=='0'and child['NODE_COMPAT_CRYPTO_HASH_HMAC']=='1'and'CXX'not in child and'NODE_OPTIONS'not in child and'RUSTC_WRAPPER'not in child and'CARGO_TARGET_DIR'not in child,'new COPY-only flags overwrite overrides without creating compiler launcher')
need(child['GIT_CONFIG_COUNT']=='0'and child['GIT_CONFIG_GLOBAL']==child['GIT_CONFIG_SYSTEM']=='/dev/null'and child['GIT_OPTIONAL_LOCKS']=='0','metadata Git is read-only configured checkout, isolated config')
for n in ['HOME','home','CODEX_HOME']:need(child[n]==original[n],'preserved '+n)
for data in [b'',b'abc',b'x'*(1048576+19)]:
 target=io.BytesIO();observed=body.stream_copy(io.BytesIO(data),target);need(target.getvalue()==data and observed==dict(sha256=hashlib.sha256(data).hexdigest(),bytes=len(data)),'stream-copy whole bytes '+str(len(data)))
class Short:
 def write(self,data):return max(0,len(data)-1)
fails(lambda:body.stream_copy(io.BytesIO(b'ab'),Short()),'short stream write refused')
for n in ['relative','/a/../b','//double','/a/./b','/a\\b']:
 fails(lambda n=n:io_guard.descriptor(dict(path=n,sha256='0'*64,bytes=0)),'canonical descriptor rejects '+n)
for field,value in [('nativeSourceFiles',355),('selectedManifestCount',11),('sourceIndexSha256','0'*64),('engineExecuted',True),('reachableBaselineCommits',2),('actualNewEngine',{'fake':True})]:
 bad=copy.deepcopy(stage);bad[field]=value;fails(lambda bad=bad:models.stage(bad,refs),'stage refuses '+field)
# Genuine future wire pure DATA only. No actual Root, proof or engine created.
own=dict(path=str(OWN/'index.json'),sha256='1'*64,bytes=1)
root=dict(schemaVersion=1,state='ROOT_REVIEWED_NODE_CRYPTO_HASH_HMAC357_NATIVE_PHASE_V2',phase='build',variant='normal-off',controllerIndex=own,controllerEntry=dict(path=refs['controllerEntryPath'],sha256='2'*64,bytes=1),integrationSourceIndex=refs['integrationSourceIndex'],actualStageReview=refs['actualStageReview'],rootEnvironmentPolicy=controller.ENV_POLICY,rootLauncherRequired=True,buildEnvironment=refs['buildEnvironment'],cachePlan=refs['cachePlan'],recipe=refs['recipe'],helper=refs['helper'],policy=refs['policy'],monitorEntry=refs['monitorEntry'],lifecycleEntry=refs['lifecycleEntry'],parallelBuilds=1,requiredStartFreeBytes=2147483648,stopBelowFreeBytes=838860800,nativeBuildAllowed=True,freezeAllowed=False,readOnlySourceAdmissionAllowed=False,postBuildNinjaListingAllowed=False,externalParentDeadlineSeconds=7200,externalOutputRoot=refs['buildExternalRoot'],buildOutputRoot=refs['buildOutputRoot'],rootObserverOutputRoot=refs['observerBase']+'-build',hashHmacEnabled=True,auditedBorrowEnabled=False,entropyPolicy='off',defaultCopyOnly=True,actualBuildReview=None,actualBuildContract=None)
for k in ['configuredSourceRoot','workRoot','freezeRoot']:root[k]=refs[k]
for k in ['nativeSourceFiles','externalEmbeddingSources','selectedManifestCount','rawMetadataFields']:root[k]=models.COUNTS[k]
for k in ['debugAllowed','gcAllowed','oomAllowed','borrowAllowed','engineExecutionAllowed','keyOrCryptoAllowed','guestAllowed','componentAllowed','exportAllowed','bootstrapAllowed','globalMutationAllowed','metadataProjectionAllowed','liveEvpSnapshotAdmission','operationalAdmission','runtimeAcceptanceClaim','timingAllowed']:root[k]=False
for k in ['actualFreezeResult','actualFreezeReview','reviewedPins','bootstrapFrame','runtimeAuthority']:root[k]=None
root.update(stageDeclaredWorkRoot=refs['stageDeclaredWorkRoot'],stageDeclaredFreezeRoot=refs['stageDeclaredFreezeRoot'],failedBuildReview=refs['failedBuildReview'],producerRole=refs['producerRole'])
models.root(root,own,refs,controller.ENV_POLICY);checks.append('prospective synthetic build-only wire accepted without invoking anything')
for field,value in [('rawMetadataFields',80),('nativeSourceFiles',355),('auditedBorrowEnabled',True),('liveEvpSnapshotAdmission',True),('externalParentDeadlineSeconds',2400),('freezeAllowed',True),('recipe',None)]:
 bad=copy.deepcopy(root);bad[field]=value;fails(lambda bad=bad:models.root(bad,own,refs,controller.ENV_POLICY),'root refuses '+field)
bad=copy.deepcopy(root);bad.update(phase='freeze',nativeBuildAllowed=False,freezeAllowed=True,readOnlySourceAdmissionAllowed=True,postBuildNinjaListingAllowed=True,externalParentDeadlineSeconds=2400,externalOutputRoot=refs['freezeExternalRoot'],rootObserverOutputRoot=refs['observerBase']+'-freeze');fails(lambda:models.root(bad,own,refs,controller.ENV_POLICY),'freeze refuses absent actual357 BUILD proof')
proof=dict(schemaVersion=1,state=models.BUILD_STATE,verifiedPassed=True,sourceIndexSha256=models.SOURCE_SHA,controllerSourceIndexSha256=own['sha256'],nativeSourceFiles=357,externalEmbeddingSources=3,selectedManifestCount=12,rawMetadataFields=83,configuredSourceRoot=refs['configuredSourceRoot'],workRoot=refs['workRoot'],variant='normal-off',actualBuildResult=dict(path=refs['buildOutputRoot']+'/result.json',sha256='2'*64,bytes=1),engine=dict(path=refs['enginePath'],sha256='3'*64,bytes=1),metadata=dict(path=refs['enginePath']+'.build.json',sha256='4'*64,bytes=1),engineSha256='3'*64,metadataSha256='4'*64,inputHashes={'synthetic':True},referenceAliases={'synthetic':True},allOwnedProcessesRawZeroAndGone=True,engineExecuted=False,guestExecuted=False,cryptoOperationsInvoked=False,operationalAdmission=False,runtimeAcceptanceClaim=False,freezeAuthorityGranted=False)
models.build_proof(proof,{},own,refs);checks.append('prospective BUILD-only proof pure DATA wire')
for field,value in [('state','old-build-pass'),('sourceIndexSha256','0'*64),('controllerSourceIndexSha256','0'*64),('nativeSourceFiles',355),('selectedManifestCount',11),('rawMetadataFields',80),('allOwnedProcessesRawZeroAndGone',False),('cryptoOperationsInvoked',True),('freezeAuthorityGranted',True)]:
 bad=copy.deepcopy(proof);bad[field]=value;fails(lambda bad=bad:models.build_proof(bad,{},own,refs),'future BUILD proof refuses '+field)
for name,donor in json.loads((OWN/'api-provenance.json').read_bytes())['byteExactCopies'].items():need(hashlib.sha256((OWN/name).read_bytes()).hexdigest()==donor['sha256']and(OWN/name).stat().st_size==donor['bytes'],'exact pure/generic code ancestry '+name)
asts=[]
for p in sorted(OWN.rglob('*.py')):
 tree=ast.parse(p.read_bytes(),filename=str(p));asts.append(p.name)
 for n in ast.walk(tree):
  if isinstance(n,ast.Call)and isinstance(n.func,ast.Name):need(n.func.id not in ['exec','eval'],'no dynamic code eval '+p.name)
benign=json.loads((OWN/'benign-copy-test-results.json').read_bytes());need(benign['state']=='BENIGN_OWNED_COPY_MODE_REGRESSIONS_PASSED_V2'and len(benign['cases'])==5,'real benign old-fail/new644+755 and partial-failure evidence')
need(benign['actualNativeCacheCopiesInvoked']is False and benign['actualBenignFilesystemCopiesInvoked']is True,'benign filesystem operation scope distinct from native phase')
newpolicy=io_guard.read(refs['policy']);oldpolicy=io_guard.read(json.loads((OWN.parent/'node-crypto-hash-hmac-native-controller-candidate-v1/references.json').read_bytes())['policy'])
need(newpolicy['expectedNativeSourceManifest']==oldpolicy['expectedNativeSourceManifest']and newpolicy['selectedModuleManifests']==oldpolicy['selectedModuleManifests'],'native357 and12 manifests unchanged; only real host producer contexts amended')
need(newpolicy['contexts']==dict(configuredSourceRoot=refs['configuredSourceRoot'],workRoot=refs['workRoot'],freezeRoot=refs['freezeRoot']),'actual new policy binds genuine new WORK/FREEZE')
need(stage['workRoot']==refs['stageDeclaredWorkRoot']and stage['freezeRoot']==refs['stageDeclaredFreezeRoot']and stage['workRoot']!=refs['workRoot'],'actual stage declared historical v1 roots are not rewritten')
recipe=io_guard.checked(refs['recipe']).read_text();helper=io_guard.checked(refs['helper']).read_text()
need(('[[ \"$work_root\" == \"'+refs['workRoot']+'\" ]]')in recipe,'new real recipe hardguard matches new WORK')
need('consumers_layer_root=\"'+str(OWN/'producer')+'\"'in recipe and str(OWN/'producer/build-engine.sh')in recipe,'new recipe actual context and helper caller')
need("POLICY_SHA256='"+refs['policy']['sha256']+"'"in helper and str(OWN/'producer')in helper,'new helper genuine HERE and coupled policy digest')
need(str(controller.SOURCE)in helper and "REPO=Path('/private/tmp/starling-node-compat/node-crypto-hash-hmac-v1-source')"in helper,'new helper preserves staged SOURCE context')
grammar=json.loads((OWN/'producer-grammar.json').read_bytes());need(grammar['rawExitCode']==0 and grammar['grammarOnly']is True and grammar['scriptCommandsExecuted']is False,'pinned Bash grammar only, no recipe command execution')
for k in ['stdout','stderr']:io_guard.checked(grammar[k]);need(grammar[k]['bytes']==0,'empty grammar '+k)
need(grammar['producerRecipe']==refs['recipe'],'grammar binds final actual producer recipe')
expected_policy=copy.deepcopy(oldpolicy);expected_policy['contexts']=dict(newpolicy['contexts']);need(expected_policy==newpolicy,'producer policy changes only explicit fresh WORK/FREEZE contexts')
for r in json.loads((OWN/'derivations.json').read_bytes())['files']:
 before=io_guard.checked(r['donor']).read_text();after=io_guard.checked(r['after']).read_text();value=before
 for op in reversed(r['edits']):
  a=op['beforeOffset'];need(value[a:a+len(op['before'])]==op['before'],'exact forward preimage '+r['output']);value=value[:a]+op['after']+value[a+len(op['before']):]
 need(value==after,'exact forward '+r['output'])
 for op in reversed(r['edits']):
  a=op['afterOffset'];need(value[a:a+len(op['after'])]==op['after'],'exact inverse preimage '+r['output']);value=value[:a]+op['before']+value[a+len(op['after']):]
 need(value==before,'exact inverse '+r['output'])
# Never import actual configured native helper/model or call a Source main.
checkframe=dict(capture=cap,stage=journal,refs=refs,configuredTree=json.loads((OWN/'configured-tree.json').read_bytes()),failedV1Protection=json.loads((OWN/'failed-v1-protection.json').read_bytes()),originalModes={r['path']:stat.S_IMODE(io_guard.checked(r).stat().st_mode)for r in source['files']})
controller.recheck(checkframe);checks.append('actual full live-data recheck branch without bootstrap or operational action')
cap.recheck();save('source-check-results.json',dict(schemaVersion=1,state='SOURCE_DATA_PURE_AST_CHECKS_PASSED_V2',checks=len(checks),declaredOriginalRows=len(source['files']),completeExternalFamilies=len(source['families']),uniqueRehashedInputs=len(cap.files),pythonAstFiles=asts,actualStageReview=refs['actualStageReview'],ownerHelperInvoked=False,authorizeInvoked=False,monitorInvoked=False,cacheCopyInvoked=False,nativeOrGuestOrCryptoExecuted=False,checkLabels=checks))
print(json.dumps(dict(state='SOURCE_DATA_PURE_AST_CHECKS_PASSED_V2',checks=len(checks),inputs=len(cap.files),families=len(source['families']),pythonAstFiles=len(asts),noNativeActions=True)))
