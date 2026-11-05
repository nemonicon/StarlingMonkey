"""Seal completed bounded independent controller SOURCE review; no actions."""
from pathlib import Path
import hashlib,json
P=Path(__file__).resolve().parent
def row(p):
 p=Path(p);b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def save(n,v):(P/n).write_text(json.dumps(v,indent=2)+'\n')
d=json.loads((P/'data-results.json').read_bytes());assert d['sourceDataReviewPassed']and d['pureCases']==62
fixed=dict(schemaVersion=1,state='INDEPENDENT_CRYPTO_OWNER355_GC_BUILD_CONTROLLER_SOURCE_REVIEW_PASSED_V1',
 controllerSourceIndexSha256=d['sourceIndex']['sha256'],nativeSourceIndexSha256=d['nativeSourceIndexSha256'],
 sourceOnly=True,sourceReviewPassed=True,ownerActionsInvoked=False,hostActionsInvoked=False,nativeBuildActionsInvoked=False)
result=dict(d,**{k:v for k,v in fixed.items()if k not in d},verifiedPassed=True,
 pureDataReview=row(P/'pure-data-review.json'),inputClosure=row(P/'rehashed-inputs.json'),
 sourceIndexSha256=d['sourceIndex']['sha256'],externalParentDeadlineSeconds=7200,
 fullOwnDonorNativeSourcePeerAndActualStageProofsAuthenticatedBeforeCustomImport=True,
 actualMonitorArgvUsesGenuineBuildPyAndConfigDescriptor=True,normalNative355RecipePolicyAndSourceContextsUnchanged=True,
 rawStreamsAndCorrectedProcessGroupSemanticsInheritedUnchanged=True,rootStageProofRemainsDataOnly=True,
 newRootBuildAuthority=None,actualBuildResult=None,actualBuildExternalTerminal=None,
 actualNativePin=None,actualFreezeResult=None,guestOrGcResult=None,
 grantsBuildOrOtherActionAuthority=False,operationalAdmission=False,runtimeAcceptanceClaim=False,timingAllowed=False,sourcePromotionAllowed=False,
 limitations=['This is a source readiness result for the dormant7200-second external build controller. It does not establish or authorize a native build, freeze, bootstrap, engine, component, key, crypto or GC result.',
 'The previously accepted actual stage proof is authenticated as DATA only. A fresh explicit Root build-only authority, config and operational execution remain required.',
 'Only actual pure validators and first deadline assertions were evaluated under private synthetic DATA. No controller/monitor main, custom module import, helper, process or workload was invoked.',
 'The corrected monitor is byte-identical to reviewed71b7 except one API ceiling assertion. Its process sampling/accounting/cleanup semantics and existing benign evidence remain inherited; no lifecycle action or deadline feasibility result was rerun.',
 'A sampled monitor may miss a descendant created and orphaned wholly between observations. Unknown identities remain un-signallable and cannot establish complete cleanup.',
 'Source/family membership is rechecked before import/launch and after success/failure; PYTHONDONTWRITEBYTECODE must be enabled so those sources do not become bytecode caches.'])
# Required existing d fields already have exact false values; no aliases are fabricated.
for k,v in fixed.items():assert result[k]==v
save('results.json',result)
save('result-contract.json',dict(schemaVersion=1,state='CRYPTO_OWNER355_GC_BUILD_CONTROLLER_SOURCE_CONTRACT_V1',requiredReviewState=fixed['state'],requiredFixedValues=fixed,reviewResult=row(P/'results.json'),controllerSourceIndex=d['sourceIndex'],requiredActualStageReview=d['actualStageProofBoundAsData'],requiredActualStageJournal=d['actualStageJournal'],actualConfiguredSourceRoot=d['actualConfiguredSourceRoot'],actualWorkRoot=d['workRoot'],externalParentDeadlineSeconds=7200,newRootBuildAuthority=None,grantsActionAuthority=False))
(P/'README.md').write_text('''Independent GC build-controller SOURCE review passed. The [result](results.json) supplies the exact prospective peer fields required by the caller; the [contract](result-contract.json) grants no action authority.

All twenty source members,79 input rows and six complete inherited source/proof families were rehashed. The standalone monitor reverses byte-for-byte to the reviewed71b7 source through one change: its API deadline ceiling becomes7,200 seconds. The inherited HTTP-specific main remains2,400 seconds and is not called. Process accounting, signal ownership, raw capture and cleanup code are unchanged.

The caller binds the genuine nativev2/build.py and exact config descriptor. Complete own/native/donor/source-peer/actual-stage/controller-peer authentication and full family membership checks precede dynamic monitor import. It requires a fresh build-only Root phase, actualdbf stage proof, fixed355 configured/work/freeze roots and a7,200-second bound. Other phases, key/guest/component/GC actions and later artifact/pin fields stay closed. Existing work/result/output roots refuse. HOME and CODEX_HOME are preserved; the genuine native builder still owns its selected environment, single-job Release/no-OOM and disk guards.

The independent reader performed62 private pure DATA cases using extracted actual root/stage/peer validators and only the monitor's first deadline assertion. Unknown or wrong phase/context/peer/artifact fields and an unissued template reject. These synthetic shapes are not actual authority. No action module was imported; no monitor/controller/native/helper/process was run. Seven Python AST modules and stored owner899source/77pure/7AST evidence were checked as data.

The success/failure path rechecks complete source/proof families and requires raw zero, observed groups/PIDs gone, no errors, timeout, interruption or forced cleanup. A separate Root build-only phase and actual external/native outcome are still required. This establishes no build feasibility, native artifact, freeze, bootstrap, guest, key/GC behavior, performance, capacity or operational admission.
''')
save('review-receipt.json',dict(schemaVersion=1,state=fixed['state'],sourceIndex=d['sourceIndex'],result=row(P/'results.json'),contract=row(P/'result-contract.json'),sourceOnly=True,sourceReviewPassed=True,ownerActionsInvoked=False,hostActionsInvoked=False,nativeBuildActionsInvoked=False,actionAuthorityIssued=False))
files=[]
for p in sorted(P.rglob('*')):
 if p.is_file()and p.name!='index.json':
  r=row(p);r['path']=str(p.relative_to(P));files.append(r)
save('index.json',dict(schemaVersion=1,state='SEALED_INDEPENDENT_GC_BUILD_CONTROLLER_SOURCE_REVIEW_V1',files=files))
print(json.dumps({n:row(P/n)for n in ['index.json','results.json','result-contract.json']}))
