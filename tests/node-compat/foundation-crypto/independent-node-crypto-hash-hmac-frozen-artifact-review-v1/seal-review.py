"""Compact publication of completed DATA checks; never reruns an owner action."""
from pathlib import Path
import ast,hashlib,json
OWN=Path(__file__).resolve().parent
K=OWN.parent
SOURCE=K/'node-crypto-hash-hmac-freezer-candidate-v1'
FREEZE=Path('/private/tmp/starling-node-compat/node-crypto-hash-hmac-v3-freeze')
def desc(p):
 p=Path(p);b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def read(p):return json.loads(Path(p).read_bytes())
def save(n,v):(OWN/n).write_text(json.dumps(v,indent=2)+'\n')
assert not(OWN/'index.json').exists()
r=read(OWN/'reader-results.json');assert r['checks']==80672 and r['uniqueRehashedFiles']==23724 and r['frozenCopies']==1893 and r['rawOwnedEventRows']==303
assert(OWN/'reader.stderr.log').read_bytes()==b''
root=read(r['rootObservation']['path']);refs=read(SOURCE/'references.json');receipt=read(r['freezeReceipt']['path']);authority=read(root['rootAuthority']['path'])
outer=read(root['ownedTerminal']['path']);inner_path=Path(refs['externalRoot'])/'terminal.json';inner=read(inner_path)
assert desc(r['rootObservation']['path'])==r['rootObservation']and desc(r['freezeReceipt']['path'])==r['freezeReceipt']
copy_sources=[r['rootObservation'],root['rootAuthority'],root['rootConfig'],root['invocation'],r['freezeReceipt'],root['metadata'],receipt['freshProducerAdmission'],receipt['control'],receipt['admissionAttempt']]
invocation=read(root['invocation']['path'])
if isinstance(invocation.get('launcher'),dict):copy_sources.append(invocation['launcher'])
for folder in [Path(outer['stdout']['path']).parent,Path(inner['stdout']['path']).parent]:
 for p in sorted(folder.rglob('*')):
  if p.is_file():copy_sources.append(desc(p))
copy_map=[];seen=set()
for n,d in enumerate(copy_sources):
 if d['path']in seen:continue
 seen.add(d['path']);p=Path(d['path']);assert desc(p)==d
 if p.is_relative_to(FREEZE):name='freeze/'+p.relative_to(FREEZE).as_posix()
 elif p.parent==K:name='root/'+p.name
 elif 'root-monitor'in str(p):name='outer/'+p.relative_to(Path(outer['stdout']['path']).parent).as_posix()
 elif p.is_relative_to(Path(refs['externalRoot'])):name='inner/'+p.relative_to(refs['externalRoot']).as_posix()
 else:name='other/'+str(n)+'-'+p.name
 target=OWN/'evidence'/name;target.parent.mkdir(parents=True,exist_ok=True);assert not target.exists();target.write_bytes(p.read_bytes());assert desc(target)['sha256']==d['sha256'];copy_map.append(dict(original=d,copy=desc(target)))
save('raw-copy-map.json',dict(schemaVersion=1,scope='Current actual Root/receipt/raw83/P3-return/control and complete two monitor evidence trees only; no historical source/tool tree replication.',files=copy_map))
files={item['copy']['path']:item['copy']for item in read(OWN/'copy-inventory.json')['files']};files[r['freezeReceipt']['path']]=r['freezeReceipt']
for item in copy_map:files[item['original']['path']]=item['original']
families={ix['path']:ix for ix in read(refs['sourceInputs']['path'])['families']}
for ix in [root['sourceIndex'],root['sourceReview']['index']]:families[ix['path']]=ix
save('input-hashes.json',dict(schemaVersion=1,scope='Current1894 frozen files plus current phase/raw evidence descriptors. Original current closure is referenced by its genuine ledger and family descriptors, not recopied.',files=sorted(files.values(),key=lambda d:d['path']),reviewedCurrentArtifactLedger=refs['artifactLedger'],reviewedHistoricalCurrentLedgerFiles=21451,reviewedSourceInputBoundary=refs['sourceInputs'],reviewedInheritedFamilyIndices=list(families.values()),currentReviewUniqueRehashedFiles=23724,completeLiveTreesRehashed=11,uncopiedReferenceDistributionsClaimedFrozen=False))
future=read(SOURCE/'future-frozen-artifact-review-contract.json');value=dict(future['requiredFixedValues'])
value.update(state=future['requiredReviewState'],freezerSourceIndexSha256=root['sourceIndex']['sha256'],freezerSourceIndex=root['sourceIndex'],producerSourceIndexSha256=refs['producerIndex']['sha256'],integrationSourceIndexSha256=refs['integrationIndex']['sha256'],variant='normal-off',freezeReceipt=r['freezeReceipt'],frozenEngine=root['engine'],frozenMetadata=root['metadata'],engineSha256=root['engine']['sha256'],metadataSha256=root['metadata']['sha256'],rootObservation=r['rootObservation'],rootAuthority=root['rootAuthority'],rootConfig=root['rootConfig'],rootInvocation=root['invocation'],externalParentTerminal=root['ownedTerminal'],innerParentTerminal=desc(inner_path),freezerSourceReview=root['sourceReview'],currentArtifactReview=refs['artifactReview'],currentArtifactContract=refs['artifactContract'],copyPlan=receipt['copyPlan'],freezerControl=receipt['control'],freshProducerAdmission=receipt['freshProducerAdmission'],frozenCopyInventory=desc(OWN/'copy-inventory.json'),inputHashes=desc(OWN/'input-hashes.json'),rawCopyMap=desc(OWN/'raw-copy-map.json'),reader=desc(OWN/'reader-results.json'),frozenCopies=1893,physicalFrozenFiles=1894,plannedOriginalCopyRows=1889,generatedControlRows=4,uniqueOriginalCopyPaths=1887,sourceAndToolCopies=1642,configuredExternalSourceCopies=3,historicalEmbeddingReferenceCopies=3,workWitnessCopies=169,compileDatabaseRows=69,policyCpp=63,strictCpp=4,privateCpp=7,separateEmbeddingCpp=1,independentCurrentFilesRehashed=23724,independentFamiliesRehashed=32,currentReferenceTreesRehashed=11,symlinkAliasesChecked=35,archiveHardlinksChecked=1,allCopyHashesModesUniqueSingleLinkAndOriginalDistinctInodesVerified=True,wholeFreshP3ReturnEqual=True,singleAdmissionCallEvidenceScope='Retained whole return/attempt/control plus authentic source/process control flow; no invented individual API terminal.',rawParentExitCodes=[0,0],outerJsonlRecords=2,innerJsonlRecords=1,ownedEventRecords=303,allOwnedGroupsGone=True,observedFrozenOnlyVerifierReturnRetained=True,independentFrozenOnlyVerifierRerun=False,filesystemReadSandboxOrHiddenOriginalExperimentPerformed=False,uncopiedSdkReferenceDistributionsFrozen=False,currentIndexBaseline742Equal=True,originalIndexPreimageRetained=False,indexStatOnlyDeltaProved=False,exactIndexWriterProved=False,reviewerOperationalActionsInvoked=False,grantsAnyActionAuthority=False,pinsOrBootstrapOrComponentOrRuntimeAuthorityGranted=False,publicProfileAdmission=False,namespaceFixRuntimeObserved=False,qualifications=['The old BUILD remains recipe0/parents1+1/preservationfalse/buildAcceptedfalse; this is a distinct actual revalidated-artifact freeze proof.','Raw83 metadata and all original path strings remain byte-exact; frozen physical roles are separate.','Current original distribution references were rehashed, but uncopied SDK/source trees are historical capsule DATA rather than frozen offline physical closure.','Frozen verifier role confinement is source/actual-return evidence, not a hidden-originals or OS sandbox experiment.','Actual fresh API call count is source/process coupled; its whole unchanged return is retained.','Initial reviewer stdout helper typo is preserved; corrected reader alone reran read/hash/model work, no owner action.','Active verifier self-authentication, live EVP snapshot barriers, erasure/finalizers, namespace identity fix, reuse, security/cost and adoption remain separate.'])
save('results.json',value)
fixed=dict(future['requiredFixedValues']);fixed.update(state=future['requiredReviewState'],freezerSourceIndexSha256=root['sourceIndex']['sha256'],producerSourceIndexSha256=refs['producerIndex']['sha256'],integrationSourceIndexSha256=refs['integrationIndex']['sha256'],engineSha256=root['engine']['sha256'],metadataSha256=root['metadata']['sha256'],frozenCopies=1893,physicalFrozenFiles=1894,rawParentExitCodes=[0,0],allOwnedGroupsGone=True,grantsAnyActionAuthority=False,independentFrozenOnlyVerifierRerun=False,uncopiedSdkReferenceDistributionsFrozen=False)
roles={k:value[k]for k in ['freezeReceipt','frozenEngine','frozenMetadata','rootObservation','rootAuthority','rootConfig','rootInvocation','externalParentTerminal','innerParentTerminal','freezerSourceIndex','freezerSourceReview','currentArtifactReview','currentArtifactContract','copyPlan','freezerControl','freshProducerAdmission','frozenCopyInventory','inputHashes','rawCopyMap']}
coverage=dict(frozenCopies=1893,physicalFrozenFiles=1894,plannedOriginalCopyRows=1889,generatedControlRows=4,sourceAndToolCopies=1642,configuredExternalSourceCopies=3,historicalEmbeddingReferenceCopies=3,workWitnessCopies=169,rawMetadataFields=83,nativeSourceFiles=357,externalEmbeddingSources=3,selectedWholeManifests=12,currentReferenceTrees=11,originalCurrentLedgerFiles=21451,independentlyRehashedFiles=23724,rawOwnedEvents=303,outerJsonlRecords=2,innerJsonlRecords=1)
# Genuine publication: the whole consumer coverage appears in BOTH artifacts.
value['coverage']=coverage;save('results.json',value)
save('result-contract.json',dict(schemaVersion=1,requiredReviewState=future['requiredReviewState'],requiredFixedValues=fixed,requiredExactDescriptors=roles,requiredCoverage=coverage,grantsAnyActionAuthority=False))
save('source-receipt.json',dict(schemaVersion=1,result=desc(OWN/'results.json'),contract=desc(OWN/'result-contract.json'),reader=desc(OWN/'reader-results.json'),readerStdout=desc(OWN/'reader.stdout.json'),readerStderr=desc(OWN/'reader.stderr.log'),allReviewerOperationalActionsInvoked=False))
for p in OWN.glob('*.py'):ast.parse(p.read_bytes())
rows=[]
for p in sorted(OWN.rglob('*')):
 assert not p.is_symlink()
 if p.is_file():d=desc(p);d['path']=p.relative_to(OWN).as_posix();rows.append(d)
save('index.json',dict(schemaVersion=1,state='SEALED_INDEPENDENT_REVALIDATED_FROZEN_ARTIFACT_DATA_REVIEW_V1',files=rows))
assert {d['path']for d in rows}|{'index.json'}=={p.relative_to(OWN).as_posix()for p in OWN.rglob('*')if p.is_file()}
for n in ['index.json','results.json','result-contract.json']:print(json.dumps(desc(OWN/n)))
