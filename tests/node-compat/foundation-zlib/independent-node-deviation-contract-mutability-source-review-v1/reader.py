"""Finite independent read/hash/data review, no owner checker or runtime calls."""
import difflib
import hashlib
import json
import stat
from pathlib import Path

P=Path(__file__).resolve().parent
Z=P.parent
C=Z/'node-deviation-contract-mutability-amendment-v1'
B=Z/'node-deviation-contract-candidate-v1'
H=Z/'independent-node-deviation-contract-source-review-v1'
seen={}
def need(value,message):
 if not value:raise AssertionError(message)
def row(path,expected=None):
 path=Path(path);raw=path.read_bytes();need(stat.S_ISREG(path.lstat().st_mode),'ordinary file')
 result=dict(path=str(path),sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw))
 if expected:need(all(result[k]==expected[k]for k in ('sha256','bytes')),'tuple '+str(path))
 seen[str(path)]=result;return result
def data(path):return json.loads(Path(path).read_bytes())
def index(root,pin):
 need(row(root/'index.json')['sha256']==pin,'exact source index');d=data(root/'index.json')
 for r in d['files']:row(root/r['path'],r)
 return d
def write(n,d):(P/n).write_text(json.dumps(d,indent=2)+'\n')
def main():
 own=index(C,'b8ec1f65316eb3ebac3d2fa582eb09cea2c568e1507f4dc9bb54ddccf659413a');need(len(own['files'])==7,'7 amendment files')
 index(B,'de59758c44bf45638c7c1b620068da519d88b847ea72a0c03f029dc2e33d1469')
 index(H,'8ccd5a15a4a6ac065e2f0df688738e2637582c71163042189051316ac6828100')
 inputs=data(C/'source-inputs.json');need(len(inputs['files'])==8 and inputs['parentConsumedManifestRowsFollowed']is False,'finite8 input refs, no parent-manifest rebasing')
 for r in inputs['files']:row(r['path'],r)
 proof=data(C/'derivations.json');need(len(proof['files'])==2,'exact two proposed afterimages')
 for r in proof['files']:
  before=''.join(difflib.restore(r['ndiff'],1)).encode();after=''.join(difflib.restore(r['ndiff'],2)).encode()
  need(before==(B/r['path']).read_bytes()and after==(C/'proposed'/r['path']).read_bytes(),'exact forward and reverse actual bytes')
  need(hashlib.sha256(before).hexdigest()==r['beforeSha256']and hashlib.sha256(after).hexdigest()==r['afterSha256'],'exact derivation digests')
 old=data(B/'contract.proposal.json');new=data(C/'proposed/contract.proposal.json')
 need(old['contractVersion']=='zlib-m0.13-node-deviations-proposal-v1'and new['contractVersion']=='zlib-m0.13-node-deviations-proposal-v2','explicit corrected proposed version2')
 copy=json.loads(json.dumps(new));copy['contractVersion']=old['contractVersion'];copy['domain']['namespace']=old['domain']['namespace'];need(copy==old,'only contractVersion/domain.namespace change, every other JSON value exact')
 need(new['rows']==old['rows']and len(new['rows'])==22,'22 full typed observations/citations unchanged')
 need(new['groups']==old['groups']and new['counts']==old['counts']and new['comparisonBoundary']==old['comparisonBoundary']and new['constantDeviation']==old['constantDeviation'],'groups/counts/comparison boundary/VERNUM limitation preserved')
 text=(Z/'source-freeze/node/lib/zlib.js').read_text();need(text.splitlines()[921].strip()=='value: ObjectFreeze(codes),','pinned actual Node22 line922 freezes codes')
 need('Pinned Node22 also freezes codes, so codes frozen status is not a deviation.'in new['domain']['namespace'],'false codes-freeze difference withdrawn')
 need('Node default/constants mutability and prototype/descriptor differences are not established'in new['domain']['namespace'],'uncaptured mutability/descriptor claims withdrawn')
 readme=(C/'proposed/README.md').read_text();need('Frozen default/constants/codes also differ from Node mutability.'not in readme and 'Pinned Node22 also freezes codes'in readme,'README agrees with corrected source claim')
 need(all(new[k]is False for k in ('actionsExecuted','operationalAdmission','sourcePromotionIssued','runtimeAcceptanceClaim','performanceClaim','errorParityClaim')),'all runtime/acceptance/parity/action booleans remain false')
 need(all(new[k]is None for k in ('actionAuthority','approvedDecision','enginePins')),'positive authority/decision/engine pins remain null')
 result=dict(schemaVersion=1,state='INDEPENDENT_NODE_DEVIATION_MUTABILITY_WORDING_SOURCE_REVIEW_PASSED_V1',sourceIndexSha256=row(C/'index.json')['sha256'],sourceOnly=True,sourceReviewPassed=True,dataIntegrityPassed=True,
  resolvedFinding='Original8ccd M1 unsupported broad Node mutability difference claim',parentSourceIndexSha256=row(B/'index.json')['sha256'],parentHoldIndexSha256=row(H/'index.json')['sha256'],originalProposalAndHoldUnmodified=True,
  amendmentFilesRehashed=7,inputRowsRehashed=8,uniqueInputsRehashed=len(seen),exactReversibleAfterimages=2,changedContractLeaves=['contractVersion','domain.namespace'],unchangedObservationRows=22,unchangedOriginalNullLabels=11,
  nodeCodesWitness=dict(path=str(Z/'source-freeze/node/lib/zlib.js'),line=922,sha256=row(Z/'source-freeze/node/lib/zlib.js')['sha256'],source='value: ObjectFreeze(codes),'),
  inheritedActualErrorDataReview=dict(indexSha256=row(H/'index.json')['sha256'],scope='Exact unchanged parent observations:100 guest error records and22 recorded Node records; no new runtime decoding or checker run here.'),
  comparisonLimits=['Recorded Node errno undefined type/value does not establish own-property absence.','Guest messages and other uncaptured descriptors/mutability are not inferred.','Original22 error observations remain unapproved proposals; no Node error parity or policy acceptance.','4880/4865 stays separate source-coupled inference, not private backend proof.'],
  oldCheckerCommandDisposition='Historical original observation-data command only; not executed and not claimed to validate corrected afterimages.',ownerActionsInvoked=False,nodeCodecHelperGuestNativeExecuted=False,operationalAdmission=False,approvedDecision=None,runtimeAcceptanceClaim=False,performanceClaim=False)
 write('rehashed-inputs.json',[seen[k]for k in sorted(seen)]);write('results.json',result)
 print(json.dumps(dict(state=result['state'],uniqueInputs=len(seen),unchangedRows=22)))
if __name__=='__main__':main()
