"""Read/hash/source preparation. No runtime/preflight/helper/controller action."""
from pathlib import Path
import hashlib,json,stat,sys
P=Path(__file__).resolve().parent;K=P.parent;R=P.parents[3];C=K/'ownership-secret-component-candidate-v2';A=K/'independent-ownership-secret-component-v2-results-review-v1'
def d(p):
    p=Path(p);h=hashlib.sha256()
    with p.open('rb')as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    return dict(path=str(p),sha256=h.hexdigest(),bytes=p.stat().st_size)
def load(p):return json.loads(Path(p).read_bytes())
def wr(n,v):(P/n).write_text(json.dumps(v,indent=2)+'\n')
def pair(p):return dict(index=d(p/'index.json'),result=d(p/'results.json'))
proof=load(A/'results.json');contract=load(A/'result-contract.json');assert proof['artifacts']==contract['artifacts']and d(A/'index.json')['sha256']=='28bc2f472ae5422dc92386a7f496b26cd3919602cde15b7a01e04d78ab6b0c29'
refs=load(C/'references.json');refs.update(state='ACTUAL_SECRET355_ORDINARY_RUNTIME_SOURCE_REFERENCES_NOT_AUTHORITY_V1',originalRoot=str(P),componentSourceIndex=proof['sourceIndex'],componentSourcePeer=proof['sourcePeer'],actualArtifactReview=pair(A),actualArtifactContract=d(A/'result-contract.json'),artifacts=proof['artifacts'],monitorIndex=d(K/'ownership-gc-build-controller-candidate-v1/index.json'),monitorEntry=refs['monitor'],pythonExecutable=d(Path(sys.executable).resolve()),outputRoot='/private/tmp/starling-node-compat/crypto-owner355-secret-runtime-v1',externalOutputRoot='/private/tmp/starling-node-compat/crypto-owner355-secret-runtime-v1-external-root',runtimeSourcePeer=None,rootAuthority=None,actualRuntimeResults=None)
refs.pop('externalRoot',None);refs['actualComponent']=proof['artifacts']['component'];refs['actualRuntimeAuthority']=None
wr('references.json',refs)
base=load(C/'source-inputs.json');files={r['path']:r for r in base['files']};families={r['path']:r for r in base['families']}
def add(r):
    r={k:r[k]for k in ['path','sha256','bytes']}
    if r['path']in files:assert files[r['path']]==r
    files[r['path']]=r
for source in [C,A,K/'ownership-runtime-candidate-v1',Path(proof['sourcePeer']['index']['path']).parent]:
    ix=d(source/'index.json');families[ix['path']]=ix;add(ix)
    for r in load(ix['path'])['files']:add(dict(path=str(source/r['path']),sha256=r['sha256'],bytes=r['bytes']))
for r in proof['artifacts'].values():add(r)
for key in ['engine','metadata','freezeReceipt','rootResult','enclosingRootResult','innerTerminal','outerTerminal','constructionConfig','rootAuthority','actualIndex','actualCompletion','actualResult']:
    if isinstance(proof.get(key),dict)and set(proof[key])=={'path','sha256','bytes'}:add(proof[key])
for r in load('/private/tmp/starling-node-compat/crypto-owner355-secret-component-v2/index.json')['files']:
    add(dict(path=str(Path('/private/tmp/starling-node-compat/crypto-owner355-secret-component-v2')/r['path']),sha256=r['sha256'],bytes=r['bytes']))
for p in [Path('/private/tmp/starling-node-compat/crypto-owner355-secret-component-v2/index.json'),Path('/private/tmp/starling-node-compat/crypto-owner355-secret-component-v2/completion.json'),K.parent/'foundation-zlib/cost-jco-correctness-candidate-v2/parser-tuple.mjs',Path('/private/tmp/starling-node-compat/zlib-cost-source-v3/tools/toolchain/node_modules/acorn/dist/acorn.mjs')]:add(d(p))
add(refs['pythonExecutable'])
# Historical donor added one receipt outside its old index. Preserve it separately,
# never pretend the old index sealed it, and require exact current donor membership.
donor=K/'ownership-runtime-candidate-v1';families.pop(str(donor/'index.json'))
add(d(donor/'source-receipt.json'))
donor_names=sorted(p.relative_to(donor).as_posix()for p in donor.rglob('*')if p.is_file())
expected={r['path']for r in load(donor/'index.json')['files']}|{'index.json','source-receipt.json'}
assert set(donor_names)==expected
historical_trees=[dict(root=str(donor),names=donor_names,role='Immutable copied-source donor DATA; one explicit receipt outside old index, no old operational guard imported')]
rows=sorted(files.values(),key=lambda r:r['path']);wr('source-inputs.json',dict(schemaVersion=1,files=rows,families=sorted(families.values(),key=lambda r:r['path']),modeRows=[dict(file=r,mode=stat.S_IMODE(Path(r['path']).stat().st_mode))for r in rows],historicalDonorTrees=historical_trees,completeDeclaredRuntimeIntake=True,allSourceAndProtectionBeforeFirstCustomImport=True,preparationOnly=True))
root=dict(schemaVersion=1,state='UNISSUED_SECRET355_NORMAL_RUNTIME_ROOT_AUTHORITY_V1',phase=None,sourceIndex=None,entry=None,externalController=None,sourceIndependentReview=None,variant='normal-off',runtimeWorkloadAllowed=False,nodeOracleAllowed=False,retainedReadOnlyApiAllowed=False,guardedPrototypeCase3Allowed=False,nativeSourceFiles=355,externalEmbeddingSources=3,selectedManifestCount=11,fullMetadataFields=75,engineSha256=refs['engine']['sha256'],componentSha256=refs['artifacts']['component']['sha256'],componentSourceIndex=refs['componentSourceIndex'],actualArtifactReview=refs['actualArtifactReview'],actualArtifactContract=refs['actualArtifactContract'],outputRoot=refs['outputRoot'],externalOutputRoot=refs['externalOutputRoot'],externalParentDeadlineSeconds=2400,workerTimeoutMs=600000,scenarios=['retained','fresh','wrapper'],monitorIndex=refs['monitorIndex'],monitorEntry=refs['monitorEntry'],retainedConfig=None,actualRuntimeReview=None)
for k in ['originalOneShotApiAllowed','originalHelperAllowed','historicalCallableAllowed','nativeBuildAllowed','nativeFreezeAllowed','componentBuildAllowed','gcAllowed','gcPressureAllowed','oomAllowed','faultInjectionAllowed','unsafeResetAllowed','wasmtimeAllowed','otherVariantsAllowed','metadataProjectionAllowed','operationalAdmission','runtimeAcceptanceClaim','sourcePromotionAllowed','timingAllowed']:root[k]=False
wr('future-root-authority.template.json',root)
wr('future-config.template.json',dict(schemaVersion=1,state='SECRET355_NORMAL_RUNTIME_CONFIG_V1',sourceIndex=None,rootAuthority=None))
wr('future-source-review-contract.json',dict(schemaVersion=1,requiredState='INDEPENDENT_CRYPTO_OWNER355_SECRET_RUNTIME_SOURCE_REVIEW_PASSED_V1',requiredOwnIndexField='sourceIndexSha256',requiredFixedValues=dict(schemaVersion=1,sourceOnly=True,sourceReviewPassed=True,ownerActionsInvoked=False,hostActionsInvoked=False,runtimeActionsInvoked=False),actualPeer=None,grantsRuntimeAuthority=False))
wr('schedule.json',dict(schemaVersion=1,source='Unchanged guarded guest and ordinary semantics; new current355 artifact/context only',ordinaryCases=[0,1,2,3],scenarios=dict(retained=dict(rotations=3,outerCalls=15),fresh=dict(rotations=1,outerCalls=7),wrapper=dict(rotations=1,outerCalls=1,withinOneExportOnly=True)),totalRawPublicStrings=23,totalCaseRecords=20,totalGuestKeyImports=10,totalGuestSignAttempts=55,totalGuestVerifyAttempts=50,totalSuccessfulFullGuestTagsComparedToNodeAndRfc=45,hostNodeOracle=dict(createHmacOutputs=1,webCryptoSignatures=2),allFourCasesRequired=True,gcOrOomOrFaultOrResetOrPressureAllowed=False,wasmtimeAllowed=False,actualResults=None,rootAuthority=None))
print(json.dumps(dict(sourceInputFiles=len(rows),families=len(families),logicalBytes=sum(r['bytes']for r in rows),actualArtifactReview=refs['actualArtifactReview'],runtimeActionsInvoked=False)))
