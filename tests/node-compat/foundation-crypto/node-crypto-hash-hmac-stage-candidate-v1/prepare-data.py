"""Read/hash Source preparation. No stage/controller phase/monitor/Git action."""
import hashlib,importlib.util,json,stat,sys
from pathlib import Path
sys.dont_write_bytecode=True
OWN=Path(__file__).resolve().parent;ROOT=OWN.parents[3];assert not (OWN/'index.json').exists()
SOURCE=OWN.parent/'node-crypto-hash-hmac-native-integration-candidate-v1'
PEER=OWN.parent/'independent-node-crypto-hash-hmac-native-integration-source-review-v1'
MONITOR=OWN.parent/'ownership-gc-build-controller-candidate-v1'
DONOR=ROOT/'tests/node-compat/foundation-scheduler/combined-native-stage-controller-candidate-v1'
def d(p):
 p=Path(p).absolute();s=p.stat();assert stat.S_ISREG(p.lstat().st_mode);return dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=s.st_size)
def j(p):return json.loads(Path(p).read_bytes())
def w(n,v):(OWN/n).write_text(json.dumps(v,indent=2)+'\n')
spec=importlib.util.spec_from_file_location('actual_new_stage_inert_source_only',OWN/'controller.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
assert m.OWN==OWN and m.SOURCE_FAMILY==SOURCE
source_rows=[d(SOURCE/'index.json')]+[dict(r,path=str(SOURCE/r['path']))for r in j(SOURCE/'index.json')['files']]
native=j(SOURCE/'native-origins.json')['files'];tools=j(SOURCE/'tool-origins.json')['files'];copies=m.expected_plan(native,tools,source_rows)
embedding=[dict(row,sourceMode=stat.S_IMODE(Path(row['original']).stat().st_mode),targetMode=0o600)for row in j(SOURCE/'embedding-origins.json')['files']]
assert len(copies)==1642 and len(embedding)==3
w('stage-copy-plan.json',dict(schemaVersion=1,state='UNEXECUTED_HASH_HMAC357_STAGE_PLAN',files=copies,embeddingData=embedding,physicalSourceDestinations=1642,physicalEmbeddingDataDestinations=3,totalPhysicalCopies=1645,overlapDestinations=[],dedupPolicy='Only byte/origin/mode-identical rows with unioned explicit roles',baselineOverlay='Checked actual Git blob preimage from fresh clone, unlink only owned baseline file, then exclusive600 copy; never protected original',activeProducerContext=str(SOURCE),stagedSourceFamilyRole='DATA_ONLY_NOT_EXECUTION_CONTEXT'))
indices=[d(SOURCE/'index.json'),d(PEER/'index.json'),d(MONITOR/'index.json'),d(DONOR/'index.json')]+j(SOURCE/'references.json')['familyIndices'];byindex={r['path']:r for r in indices};rows={}
def add(row):
 actual=d(row['path']);assert actual==row
 if row['path']in rows:assert rows[row['path']]==row
 rows[row['path']]=row
for row in j(SOURCE/'input-hashes.json')['files']:add(row)
for ix in byindex.values():
 add(ix)
 for row in j(ix['path'])['files']:add(dict(row,path=str(Path(ix['path']).parent/row['path'])))
for row in copies+embedding:add(dict(path=row['original'],sha256=row['sha256'],bytes=row['bytes']))
refs=dict(schemaVersion=1,integrationIndex=d(SOURCE/'index.json'),actualIntegrationSourceReview=dict(index=d(PEER/'index.json'),result=d(PEER/'results.json')),actualIntegrationSourceReviewContract=d(PEER/'result-contract.json'),monitorIndex=d(MONITOR/'index.json'),monitorEntry=d(MONITOR/'monitor.py'),monitorApi='monitor(argv,cwd,environment,output,timeout_seconds,authority)',deadlineSeconds=600,declaredCurrentInputRows=len(rows),sourceOriginalInputRows=2622,basePlanRows=1584,integrationFamilyRows=58,physicalSourceCopies=1642,embeddingReferenceCopies=3,documentationLinks={'docs/src/ADOPTERS.md':'../../ADOPTERS.md','docs/src/CODE_OF_CONDUCT.md':'../../CODE_OF_CONDUCT.md','docs/src/README.md':'../../README.md'},documentationLinkProof='Future real ls-tree BASE+cat-file blob raw bytes, exact symlink blob ID/target; unconsumed metadata only',activeProducerOriginal=str(SOURCE/'build-engine.sh'),activeHelperOriginal=str(SOURCE/'layer-policy.py'),stagedSourceFamily='DATA_ONLY',baselineRevision=m.BASE,configuredSourceRoot=str(m.DEST),workRoot=str(m.WORK),freezeRoot=str(m.FREEZE),externalOutputRoot=str(m.OUT),stageJournal=str(m.JOURNAL),stageControllerReview=None,rootAuthority=None,actualStage=None,actualStageReview=None,actualNewEngine=None,actualNewMetadata=None,admission=None,freezer=None,pins=None,bootstrap=None,runtime=None,operationalAdmission=False)
w('references.json',refs);w('input-hashes.json',dict(schemaVersion=1,scope='Full declared2622 integration Source boundary plus complete named Source/peer/monitor/donor families; no historical BUILD ledger recursion',files=[rows[k]for k in sorted(rows)],families=[byindex[k]for k in sorted(byindex)]))
root=dict(schemaVersion=1,state='UNISSUED_NODE_CRYPTO_HASH_HMAC357_SOURCE_STAGE_V1',requiredIssuedState='ROOT_REVIEWED_NODE_CRYPTO_HASH_HMAC357_SOURCE_STAGE_V1',phase='source-stage-only',sourceStageAllowed=False,sourceIndex=refs['integrationIndex'],stageControllerIndex=None,stageControllerEntry=None,integrationSourceReview=refs['actualIntegrationSourceReview'],stageControllerReview=None,configuredSourceRoot=str(m.DEST),workRoot=str(m.WORK),freezeRoot=str(m.FREEZE),externalOutputRoot=str(m.OUT),stageJournal=str(m.JOURNAL),baselineRevision=m.BASE,externalParentDeadlineSeconds=600,nativeSourceFiles=357,retainedParentNativeFiles=353,changedParentNativeFiles=2,newNativeFiles=2,externalEmbeddingSources=3,selectedManifestCount=12,initialVariant='normal-off',basePlanRows=1584,integrationFamilyRows=58,expectedSourceCopies=1642,expectedEmbeddingDataCopies=3,genericMonitorIndex=refs['monitorIndex'],genericMonitorEntry=refs['monitorEntry'],gitBinary=None,pythonExecutable=None)
for key in ['nativeBuildAllowed','freezeAllowed','exportAllowed','bootstrapAllowed','engineExecutionAllowed','keyOperationsAllowed','cryptoOperationsAllowed','guestAllowed','gcAllowed','borrowAllowed','timingAllowed','normalMutationAllowed','metadataProjectionAllowed','privateBackendEvidenceHookEnabled','pinsAdopted','operationalAdmission','runtimeAcceptanceClaim']:root[key]=False
for key in ['actualStageResult','actualStageReview','actualBuildResult','reviewedNativePins','runtimeAuthority']:root[key]=None
w('root-authority.template.json',root)
w('config.template.json',dict(schemaVersion=1,state='UNISSUED_NODE_CRYPTO_HASH_HMAC357_STAGE_CONFIG_V1',requiredIssuedState='NODE_CRYPTO_HASH_HMAC357_STAGE_CONFIG_V1',rootAuthority=None,sourceIndex=refs['integrationIndex'],controllerIndex=None))
w('future-source-review-contract.json',dict(schemaVersion=1,requiredState='INDEPENDENT_NODE_CRYPTO_HASH_HMAC357_STAGE_SOURCE_REVIEW_PASSED_V1',controllerSourceIndexSha256=None,integrationSourceIndexSha256=m.SOURCE_SHA,genericMonitorSourceIndexSha256=m.MONITOR_SHA,sourceOnly=True,sourceReviewPassed=True,ownerActionsInvoked=False,hostActionsInvoked=False,sourceStageActionsInvoked=False,nativeBuildActionsInvoked=False,cryptoOperationsInvoked=False,actualStage=None,grantsAnyActionAuthority=False))
print(json.dumps(dict(state='SOURCE_PLAN_ONLY',currentInputs=len(rows),families=len(byindex),sourceCopies=len(copies),embeddingReferenceCopies=3,stageExecuted=False)))
