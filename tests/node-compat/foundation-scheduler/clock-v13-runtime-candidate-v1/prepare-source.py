"""Read/hash/source preparation only; no Jco/shim/native/API/CLI operation."""
from pathlib import Path
import hashlib,json,sys
P=Path(__file__).resolve().parent;S=P.parent;R=P.parents[3];B=S/'clock-v13-component-candidate-v1';A=S/'independent-clock-v13-component-results-review-v1'
def load(p):return json.loads(Path(p).read_bytes())
def d(p):
    p=Path(p);h=hashlib.sha256()
    with p.open('rb')as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    return dict(path=str(p),sha256=h.hexdigest(),bytes=p.stat().st_size)
def wr(n,v):(P/n).write_text(json.dumps(v,indent=2)+'\n')
def pair(p):return dict(index=d(p/'index.json'),result=d(p/'results.json'))
proof=load(A/'results.json');assert d(A/'index.json')['sha256']=='b07378f3915407eb35ac398fe55e58b3e2cfdb03a4978dcfc490538a1e7e29cf';assert proof['artifacts']==load(A/'result-contract.json')['artifacts']
refs=load(P/'references.DRAFT.json');refs.update(state='CLOCK_V13_REACTDOM_RUNTIME_SOURCE_REFERENCES_NOT_AUTHORITY_V1',actualArtifactReview=pair(A),actualArtifactContract=d(A/'result-contract.json'),componentSourceIndex=proof['sourceIndex'],componentSourcePeer=proof['sourcePeer'],component=proof['artifacts']['component'],artifacts=proof['artifacts'],generatedFiles=proof['generatedFiles'],inlineCoreModules=[dict(sha256=r['sha256'],bytes=r['bytes'])for r in proof['loadingProtocol']['inlineCoreModules']],monitorIndex=d(R/'tests/node-compat/foundation-crypto/ownership-gc-build-controller-candidate-v1/index.json'),monitorEntry=d(R/'tests/node-compat/foundation-crypto/ownership-gc-build-controller-candidate-v1/monitor.py'),pythonExecutable=d(Path(sys.executable).resolve()))
base=Path(refs['loaderPackageRoot'])/'node_modules'
for k in ['jcoApi','shimClocks','shimIo']:refs[k]=d(Path(refs[k]))
refs.update(shimClocksUrl=Path(refs['shimClocks']['path']).as_uri(),shimIoUrl=Path(refs['shimIo']['path']).as_uri(),parser=d(base/'acorn/dist/acorn.mjs'),packageInventory=load(refs['loaderReferences']['path'])['packageInventory'],wasmtime=dict(path='/private/tmp/starling-node-compat/bin/wasmtime-v42.0.1-aarch64-macos/wasmtime',sha256='a85dec9fcbbad23d0e038e5a99604114dbe9aa77bc784e4bce0f33013eb33c1c',bytes=50820352))
report=R/'tests/node-compat/frameworks/package-bundler-execution-v1/results-post-push-v2/results.json';v=load(report);case=next(r for r in v['cases']if r['id']=='react-dom-edge');command=next(r for r in v['commands']if r['name']=='node-react-dom-edge')
assert isinstance(v['finished'],str)and v['finished'].endswith('Z')and v['observationsComplete']is True and case['nodeControl']['status']=='passed'and command['status']==0 and command['ownedGroupGone']is True
raw=Path(command['stdout']['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==command['stdout']['sha256'];assert json.loads(raw)==case['nodeControl']
refs['oracleValue']=case['nodeControl']['value'];refs['oracleEvidence']=dict(report=d(report),command=command,nodeControl=case['nodeControl'],stdout=command['stdout'],stderr=command['stderr'],oldPureProfileWorker=case['worker'],rerunRequired=False)
first=S/'independent-clock-v13-first-wasmtime-render-results-review-v1'
refs['initialStockWasmtimeObservationData']=dict(review=pair(first),scope='One fresh stock WT only; no transfer to the new full differential schedule or Jco/mapped readiness',grantsAnyAuthority=False)
wr('references.json',refs)
inputs=load(B/'source-inputs.json');files={r['path']:r for r in inputs['files']};families={r['path']:r for r in inputs['families']}
def add(r):
    r={k:r[k]for k in ['path','sha256','bytes']}
    if r['path']in files:assert files[r['path']]==r
    files[r['path']]=r
for origin in [B,A,first,Path(refs['componentSourcePeer']['index']['path']).parent,R/'tests/node-compat/foundation-crypto/ownership-gc-build-controller-candidate-v1']:
    ix=d(origin/'index.json');add(ix);families[ix['path']]=ix
    for r in load(ix['path'])['files']:add(dict(path=str(origin/r['path']),sha256=r['sha256'],bytes=r['bytes']))
for r in [*proof['artifacts'].values(),*proof['generatedFiles'].values(),refs['wasmtime'],refs['pythonExecutable'],d(report),command['stdout'],command['stderr'],refs['parser'],refs['jcoApi'],refs['shimClocks'],refs['shimIo'],d(R/'tests/node-compat/foundation-zlib/cost-wasmtime-transport-candidate-v1/scalar-transport.mjs'),d(S/'combined-native-build-controller-candidate-v2/controller.py')]:add(r)
for p in ['authority.mjs','durable.mjs','durable-host.mjs']:add(d(R/'tests/node-compat/foundation-crypto/ownership-component-candidate-v1'/p))
actualRoot=Path('/private/tmp/starling-node-compat/clock-v13-component-v1')
for r in load(actualRoot/'index.json')['files']:add(dict(path=str(actualRoot/r['path']),sha256=r['sha256'],bytes=r['bytes']))
add(d(actualRoot/'index.json'));add(d(actualRoot/'completion.json'))
wr('source-inputs.json',dict(schemaVersion=1,files=sorted(files.values(),key=lambda r:r['path']),families=sorted(families.values(),key=lambda r:r['path']),sourceAndNativeAndActualArtifactsProtected=True,noToolTreeCopied=True))
root=dict(schemaVersion=1,state='UNISSUED_CLOCK_V13_REACTDOM_ROOT_V1',phase=None,sourceIndex=None,entry=None,externalController=None,sourceIndependentReview=None,variant='normal-off',actualArtifactReview=refs['actualArtifactReview'],actualArtifactContract=refs['actualArtifactContract'],componentSha256=refs['component']['sha256'],outputRoot=None,externalOutputRoot=None,selectedInterfaces=refs['selectedInterfaces'],mappingOptions=refs['mappingOptions'],mappedTranspileAllowed=False,jcoCompilerWasmHelpersAllowed=False,generatedApplicationImportAllowed=False,ordinaryRunAllowed=False,stockWasmtimeAllowed=False,nativeReadOnlyPreflightAllowed=False,standardShimWorkerThreadsAllowed=False,ownedWorkerDeadlineMs=180000,requiredExternalParentDeadlineSeconds=1200,monitorIndex=refs['monitorIndex'],monitorEntry=refs['monitorEntry'],actualMappedOutputReview=None)
for k in ['customHostServicesAllowed','componentConstructionAllowed','nativeBuildAllowed','engineReplacementAllowed','adapterPromotionAllowed','defaultPackagerReplacementAllowed','otherGuestAllowed','resourceSevenCaseProfileAccepted','clockProfilePromotionAllowed','dateTimerSnapshotTeardownAccepted','resetOrReuseAllowed','operationalAdmission','runtimeAcceptanceClaim','timingAllowed']:root[k]=False
wr('future-root-authority.template.json',root);wr('future-config.template.json',dict(schemaVersion=1,state='CLOCK_V13_REACTDOM_CONFIG_V1',sourceIndex=None,rootAuthority=None))
wr('future-source-review-contract.json',dict(schemaVersion=1,requiredState='INDEPENDENT_CLOCK_V13_REACTDOM_RUNTIME_SOURCE_REVIEW_PASSED_V1',requiredOwnIndexField='sourceIndexSha256',requiredFixedValues=dict(schemaVersion=1,sourceOnly=True,sourceReviewPassed=True,ownerActionsInvoked=False,hostActionsInvoked=False,runtimeActionsInvoked=False),actualPeer=None,grantsAnyPhase=False))
wr('future-mapped-output-review.template.json',dict(schemaVersion=1,state='UNISSUED_CLOCK_V13_MAPPED_OUTPUT_REVIEW_V1',verifiedPassed=False,requiredIssuedState='ROOT_REVIEWED_CLOCK_V13_MAPPED_OUTPUT_V1',sourceIndexSha256=None,component=refs['component'],mappingOptions=refs['mappingOptions'],mappingResult=None,index=None,completion=None,mappingRootAuthority=None,mappingConfig=None,externalParentTerminal=None,applicationGeneratedModuleImported=False,ordinaryApplicationExportsInvoked=False,allFourActualCoreBytesUnchangedRequired=True,allNewGeneratedFilesAndStaticBindingsRequired=True,fullClockProfileAcceptance=False))
print(json.dumps(dict(files=len(files),families=len(families),logicalBytes=sum(r['bytes']for r in files.values()),actualArtifactReview=refs['actualArtifactReview'],allActionsUnissued=True)))
