"""Source-only publication; never stage/authorize/Git/monitor/crypto."""
from pathlib import Path
import hashlib,json,ast
O=Path(__file__).resolve().parent;S=O.parent/'node-crypto-hash-hmac-stage-candidate-v1'

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def desc(p):return dict(path=str(p),sha256=digest(p),bytes=p.stat().st_size)
def read(p):return json.loads(p.read_bytes())
def write(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
def need(v,m):
 if not v:raise AssertionError(m)
need(not(O/'index.json').exists(),'fresh review own root')
ix=desc(S/'index.json');need(ix['sha256']=='2395af2c6807953fb32173cd8c7f63b4f1f379360f991e2bb39dff87153620c0'and ix['bytes']==4708,'actual sealed2395Source')
v=read(S/'index.json');names={'index.json'}
for r in v['files']:need(desc(S/r['path'])==dict(r,path=str(S/r['path'])),'final owner bytes stable');names.add(r['path'])
need({p.relative_to(S).as_posix()for p in S.rglob('*')if p.is_file()}==names and len(names)==31,'complete owner Source exact membership, no author checker writes')
for p in O.glob('*.py'):ast.parse(p.read_text())
s=read(O/'intake-summary.json');need(s['controllerSourceIndex']==ix and s['uniqueSourceDestinations']==1642 and s['sourceDestinationOverlap']==[]and s['embeddingReferenceDataCopies']==3,'real plan intake')
evidence={}
for key in ['intake-2','pure-1','environment-1']:
 base=O/'evidence'/key;t=read(base/'terminal.json');need(t['rawExitCode']==0 and(base/'stderr.log').read_bytes()==b'','final read/pure/context checks0');evidence[key]={k:desc(base/f)for k,f in [('stdout','stdout.log'),('stderr','stderr.log'),('terminal','terminal.json')]}
pure=read(O/'evidence/pure-1/stdout.log');env=read(O/'evidence/environment-1/stdout.log');need(pure['checks']==55 and pure['actualOwnModuleContext']is True and pure['globalsOrNamespaceRebound']is False and env['checks']==12 and env['gitInvoked']is env['phaseInvoked']is False,'actual pure/functions/context only')
prepared=read(S/'results.json');template=read(S/'root-authority.template.json')
for k in ['ownerActionsInvoked','hostActionsInvoked','sourceStageActionsInvoked','nativeBuildActionsInvoked','cryptoOperationsInvoked','gitInvoked','monitorInvoked','nativeHelperImported','engineExecuted','guestExecuted','operationalAdmission']:need(prepared[k]is False,'Source closed '+k)
for k in ['actualStage','actualStageReview','actualBuild','actualEngine','actualMetadata','admission','freezer','pins','bootstrap','component','runtime']:need(prepared[k]is None,'no current artifact/action '+k)
need(template['sourceStageAllowed']is False and prepared['sourceDestinationOverlap']==[],'no stage grant and exact zero overlap')
fixed=dict(schemaVersion=1,state='INDEPENDENT_NODE_CRYPTO_HASH_HMAC357_STAGE_SOURCE_REVIEW_PASSED_V1',controllerSourceIndexSha256=ix['sha256'],integrationSourceIndexSha256=s['integrationSourceIndex']['sha256'],genericMonitorSourceIndexSha256=s['genericMonitorSourceIndex']['sha256'],sourceOnly=True,sourceReviewPassed=True,ownerActionsInvoked=False,hostActionsInvoked=False,sourceStageActionsInvoked=False,nativeBuildActionsInvoked=False,cryptoOperationsInvoked=False,actualStage=None,grantsAnyActionAuthority=False)
result=dict(fixed,controllerSourceIndex=ix,integrationSourceIndex=s['integrationSourceIndex'],genericMonitorSourceIndex=s['genericMonitorSourceIndex'],sourceResult=desc(S/'results.json'),sourceReceipt=desc(S/'source-receipt.json'),sourcePeerConsumerContract=desc(S/'future-source-review-contract.json'),intake=desc(O/'intake-summary.json'),checks=s['checks'],currentFullHashFiles=s['currentFullHashFiles'],currentLogicalBytes=s['currentLogicalBytes'],currentFamilies=s['currentFamilies'],nativeSourceFiles=357,retainedParentNativeFiles=353,changedParentNativeFiles=2,newNativeFiles=2,externalEmbeddingSources=3,selectedManifestCount=12,initialVariant='normal-off',basePlanRows=1584,integrationFamilyRows=58,plannedSourceCopies=1642,plannedReferenceDataCopies=3,sourceDestinationOverlap=[],donorPrimitivesUnchanged=12,canonicalCheckedRefinement=1,pureChecks=55,gitEnvironmentPureChecks=12,actualOwnModuleContextVerified=True,namespaceOrGlobalsRebound=False,authorSelfWritingChecksInvoked=False,activeProducerAndHelperRemainOriginal=True,stagedIntegrationFamilyDataOnly=True,originalMonitorApiArguments=6,outerDeadlineSeconds=600,gitCommandTimeoutSeconds=120,cloneHistoryByteBounded=False,baselineOnlyCloneRefinementImplemented=False,universalGitConfigOrHostHermeticityClaim=False,actualCopyOrFailureLifecycleTested=False,publicCryptoInitLiveEvpSnapshotPolicyProved=False,evidence=evidence,qualifications=[s['cloneHistoryQualification'],s['gitConfigurationQualification'],'No continuous disk monitoring; only2GiB start-floor, external kill/writer failure can prevent a complete journal','No actual Git/stage/monitor/helper/native/engine/crypto/guest work by reviewer','Separate INIT/live-EVP snapshot policy, native artifact and runtime gates remain unresolved','No Source/proof/state/global context projection or current355 mutation'])
write(O/'results.json',result)
write(O/'result-contract.json',dict(schemaVersion=1,requiredReviewState=fixed['state'],requiredFixedValues={k:v for k,v in fixed.items()if k!='state'},requiredExactDescriptors={k:result[k]for k in ['controllerSourceIndex','integrationSourceIndex','genericMonitorSourceIndex','sourceResult','intake']},qualifications=result['qualifications'],scope='Qualified SOURCE-only dormant1642-source+3-reference stage controller; no action/runtime grant'))
write(O/'receipt.json',dict(schemaVersion=1,state='SEALED_INDEPENDENT_HASH_HMAC357_STAGE_SOURCE_REVIEW_V1',controllerSourceIndex=ix,result=desc(O/'results.json'),contract=desc(O/'result-contract.json'),sourceAndOriginalInputIdentityBookendsPassed=True,allSourceActionsInvoked=False,hostPureInertModuleAndAstOnly=True,onlyOwnRootIndexExcluded=True))
payloads=[p for p in sorted(O.rglob('*'))if p.is_file()and p not in [O/'index.json',O/'member-ledger.json']]
write(O/'member-ledger.json',dict(schemaVersion=1,scope='All own payload files excluding only own memberledger/rootindex; nested indices included if present',files=[dict(path=p.relative_to(O).as_posix(),sha256=digest(p),bytes=p.stat().st_size)for p in payloads]))
files=[p for p in sorted(O.rglob('*'))if p.is_file()and p!=O/'index.json'];need(not any(p.is_symlink()for p in O.rglob('*')),'ordinary own closed family');index=dict(schemaVersion=1,files=[dict(path=p.relative_to(O).as_posix(),sha256=digest(p),bytes=p.stat().st_size)for p in files]);write(O/'index.json',index)
need({p.relative_to(O).as_posix()for p in O.rglob('*')if p.is_file()}=={'index.json',*[r['path']for r in index['files']]},'whole actual own membership')
for r in index['files']:need(desc(O/r['path'])==dict(r,path=str(O/r['path'])),'every final own member exact')
print(json.dumps(dict(index=desc(O/'index.json'),result=desc(O/'results.json'),contract=desc(O/'result-contract.json'),receipt=desc(O/'receipt.json'),indexedFiles=len(files),actualFiles=len(files)+1,logicalBytes=sum(p.stat().st_size for p in O.rglob('*')if p.is_file())),indent=2))
