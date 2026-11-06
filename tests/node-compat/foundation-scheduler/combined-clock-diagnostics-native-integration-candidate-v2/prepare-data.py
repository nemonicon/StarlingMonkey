"""Assemble finite Source descriptors, never populate stage/cache/work roots."""
from pathlib import Path
import hashlib,json,stat
OWN=Path(__file__).resolve().parent
S=OWN.parent;REPO=OWN.parents[3]
def row(p):
 p=Path(p);b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def read(p):return json.loads(Path(p).read_bytes())
def save(name,v):(OWN/name).write_text(json.dumps(v,indent=2)+'\n')
def main():
 parent=S/'combined-native-build-controller-candidate-v2';refs=read(parent/'references.json')
 tooling=read(S/'combined-native-artifact-tooling-candidate-v1/references.json')
 inventory=read(S/'combined-clock-diagnostics-candidate-v2/proposed-source-inventory.json')
 contexts=read(OWN/'contexts.json');source=contexts['sourceRoot'];work=contexts['workRoot'];freeze=contexts['freezeRoot']
 plan=[]
 for r in inventory['native']:
  p=Path(r['origin']['path']);plan.append(dict(path=r['path'],origin=r['origin'],sha256=r['origin']['sha256'],bytes=r['origin']['bytes'],mode=stat.S_IMODE(p.stat().st_mode),role='native'))
 for r in read(S/'combined-native-integration-candidate-v1/tool-origins.json')['files']:
  p=Path(r['original']);plan.append(dict(path=r['path'],origin=dict(path=r['original'],sha256=r['sha256'],bytes=r['bytes']),sha256=r['sha256'],bytes=r['bytes'],mode=stat.S_IMODE(p.stat().st_mode),role='tool'))
 plan.sort(key=lambda r:r['path']);assert len(plan)==len({r['path']for r in plan})==1583
 save('stage-copy-plan.json',dict(schemaVersion=1,files=plan,nativeFiles=357,toolFiles=1226,embeddingFilesCopied=0,embeddingReference=inventory['externalEmbedding'],activeProducerContext=str(OWN),stagedToolsRole='Recipe dependencies and ancestry DATA; active own producer remains original Source context'))
 cache=read(parent/'cache-plan.json');cache.update(state='FINITE_CLOCK_DIAGNOSTIC357_PRIVATE_IMMUTABLE_CACHE_PLAN_V2',workRoot=work,privateRustupHome=work+'/rustup-home',privateCargoHome=work+'/cargo-home');save('cache-plan.json',cache)
 diagnostics=S/'combined-clock-diagnostics-candidate-v2'
 ledger_refs=[row(parent/'source-inputs.json'),tooling['reviewedBuildInputLedger'],row(diagnostics/'input-hashes.json')]
 aliases=read(tooling['referenceAliasWitness']['path'])
 additional=[r['origin']for r in inventory['native']+inventory['externalEmbedding']]
 for key in ['engine','metadata','freezeReceipt','rootFreezeObservation']:additional.append(tooling[key])
 hashreview=read(REPO/'tests/node-compat/foundation-crypto/independent-node-crypto-hash-hmac-artifact-revalidation-v2-results-review-v2/results.json')
 additional.extend([hashreview['engine'],hashreview['metadata']])
 additional.extend(r['source']for r in cache['copies']);additional.append(cache['sdkArchiveReferenceOnly'])
 mode_rows=[dict(file=r['origin'],mode=r['mode'])for r in plan]
 save('protected-inputs.json',dict(schemaVersion=1,fileLedgers=ledger_refs,frozenCopyInventory=tooling['frozenCopyInventory'],files=additional,modeRows=mode_rows,aliases=aliases['symlinks'],archiveHardlinks=aliases['archiveHardlinks'],scope='Full existing parent build ledgers and frozen originals/copies by reference; native357 and external3 origins; explicit parent355/Hash357 artifact bytes. No historical trees copied into this Source family. Mutable new configured Git index is excluded and independently validated using retained preimages, full baseline742 entries, flags/extensions and original mode.'))
 families={r['path']:r for r in tooling['inheritedFamilies']}
 for path in [diagnostics,S/'independent-combined-clock-diagnostics-v2-source-review-v1',S/'combined-clock-diagnostics-sdk-syntax-v2',S/'combined-clock-diagnostics-native-integration-candidate-v1',parent,Path(refs['monitorIndex']['path']).parent,Path(refs['lifecycleIndex']['path']).parent]:
  r=row(path/'index.json');families[r['path']]=r
 families[tooling['actualFrozenReview']['index']['path']]=tooling['actualFrozenReview']['index']
 env=dict(refs['buildEnvironment'])
 old=read(parent/'contexts.json')if(parent/'contexts.json').exists()else{'workRoot':'/private/tmp/starling-node-compat/combined-native355-v2-build'}
 for k,v in list(env.items()):env[k]=v.replace('/private/tmp/starling-node-compat/combined-native355-v2-build',work)
 env['NODE_COMPAT_ARTIFACT_TAG']='clockdiag357v2';env['GIT_OPTIONAL_LOCKS']='0'
 artifact='starlingmonkey_embedding.abi-i32-i64-v1.clock-diagnostic357-v2.OFF.p1.e1.d1.a1.q1.u1.w1.t1.c1.z1.s1.clockdiag357v2.wasm'
 git=next(r['executable']for r in refs['hostTools']if r['name']=='git')
 value=dict(schemaVersion=1,state='CLOCK_DIAGNOSTIC357_RUNNABLE_PRODUCER_SOURCE_V2',
  contexts=dict(sourceRoot=source,workRoot=work,freezeRoot=freeze,stageOutputRoot='/private/tmp/starling-node-compat/combined-clock-diagnostic357-v2-stage-external-root',stageJournal='/private/tmp/starling-node-compat/combined-clock-diagnostic357-v2-stage.json',buildOutputRoot='/private/tmp/starling-node-compat/combined-clock-diagnostic357-v2-build-external-root',buildResultRoot='/private/tmp/starling-node-compat/combined-clock-diagnostic357-v2-build-result'),
  controller=row(OWN/'controller.py'),recipe=row(OWN/'build-engine.sh'),helper=row(OWN/'layer-policy.py'),policy=row(OWN/'policy.json'),metadataModel=row(OWN/'native-admission-model.py'),copyPlan=row(OWN/'stage-copy-plan.json'),cachePlan=row(OWN/'cache-plan.json'),protectedInputs=row(OWN/'protected-inputs.json'),
  diagnosticSourceIndex=row(diagnostics/'index.json'),diagnosticSourcePeerIndex=row(S/'independent-combined-clock-diagnostics-v2-source-review-v1/index.json'),diagnosticSdkSyntaxIndex=row(S/'combined-clock-diagnostics-sdk-syntax-v2/index.json'),
  monitorIndex=refs['monitorIndex'],monitorEntry=refs['monitorEntry'],lifecycleIndex=refs['lifecycleIndex'],lifecycleEntry=refs['lifecycleEntry'],pythonExecutable=refs['pythonExecutable'],bash=refs['bash'],git=git,node=refs['node'],sdkArchive=refs['sdkArchive'],hostTools=refs['hostTools'],hostPath=refs['hostPath'],buildEnvironment=env,artifactBasename=artifact,families=list(families.values()),
  actualStageReview=None,actualStageResult=None,sourcePeer=None,rootAuthority=None,actualBuild=None,actualArtifact=None,freezer=None,pins=None,bootstrap=None,runtime=None,operationalAdmission=False)
 save('references.json',value)
 save('config.template.json',dict(schemaVersion=1,state='CLOCK_DIAGNOSTIC357_CONFIG_V2',sourceIndex=None,phase=None,rootAuthority=None))
 root=dict(schemaVersion=1,state='ROOT_REVIEWED_CLOCK_DIAGNOSTIC357_PHASE_V2',phase=None,sourceIndex=None,sourceReview=None,entry=value['controller'],contexts=value['contexts'],nativeSourceFiles=357,externalEmbeddingSources=3,selectedWholeManifests=11,rawMetadataFields=82,sourceStageAllowed=None,nativeBuildAllowed=None,monitorIndex=value['monitorIndex'],monitorEntry=value['monitorEntry'],lifecycleIndex=value['lifecycleIndex'],lifecycleEntry=value['lifecycleEntry'],environmentPolicy={'removePrefixes':['BASH_FUNC_'],'removeExactNames':['BASH_ENV','ENV','SHELLOPTS','BASHOPTS','CDPATH','GLOBIGNORE'],'preserveExactNames':['HOME','home','CODEX_HOME'],'mustRunBeforeFirstControllerOrBash':True,'recordNamesOnly':True},cleanEnvironmentRequiredBeforeEntry=True,deadlineSeconds=None,startFreeBytes=2*1024**3,stopFreeBytes=800*1024**2,initialVariant='diagnostic-normal-off',releaseOnly=True,allSharedDiagnosticMacrosOn=True,buildEnvironment=env,cachePlan=value['cachePlan'],actualStageReview=None,actualStageResult=None,actualBuild=None,actualFreeze=None,actualArtifact=None,reviewedPins=None,runtimeAuthority=None)
 for k in ['freezeAllowed','exportAllowed','pinsAllowed','bootstrapAllowed','engineExecutionAllowed','componentAllowed','guestAllowed','clockRuntimeAllowed','cryptoAllowed','gcAllowed','oomAllowed','debugAllowed','resetAllowed','normalMutationAllowed','operationalAdmission','sourcePromotionAllowed','allSeventeenGatesAccepted']:root[k]=False
 save('root-authority.template.json',root)
 save('future-source-review-contract.json',dict(schemaVersion=1,requiredReviewState='INDEPENDENT_CLOCK_DIAGNOSTIC357_NATIVE_INTEGRATION_SOURCE_REVIEW_PASSED_V2',requiredFixedValues=dict(schemaVersion=1,sourceOnly=True,sourceReviewPassed=True,nativeSourceFiles=357,externalEmbeddingSources=3,rawMetadataFields=82,selectedWholeManifests=11,ownerActionsInvoked=False,hostActionsInvoked=False,nativeBuildOrStageActionsInvoked=False,runtimeActionsInvoked=False),sourceIndexSha256=None,sourceReviewGrantsActionAuthority=False))
 print(json.dumps(dict(copyPlan=row(OWN/'stage-copy-plan.json'),protectedInputs=row(OWN/'protected-inputs.json'),families=len(families),reference=row(OWN/'references.json'))))
if __name__=='__main__':main()
