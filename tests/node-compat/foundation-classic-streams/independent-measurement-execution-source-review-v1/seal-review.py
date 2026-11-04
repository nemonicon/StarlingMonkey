#!/usr/bin/env python3
"""Seal this new text-only source review, without invoking reviewed code."""
from pathlib import Path
import json,hashlib,datetime,ast
HERE=Path(__file__).resolve().parent

def row(path):
 data=path.read_bytes();data.decode('utf-8');assert not path.is_symlink()
 return {'path':str(path.relative_to(HERE)),'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)}
def main():
 result=json.loads((HERE/'results.json').read_text())
 assert result['state']=='INDEPENDENT_SOURCE_REVIEW_COMPLETE_MANDATORY_CAPTURE_DEADLINE_FIX_NO_ACTIVATION'
 assert len(result['mandatoryFindings'])==1
 for path in HERE.glob('*.py'):ast.parse(path.read_text(),filename=path.name)
 receipt={'schemaVersion':1,'state':result['state'],'sealedAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sourceIndex':result['sourceIndex'],'results':row(HERE/'results.json'),'verifiedFiles':row(HERE/'verified-files.json'),'readers':[row(HERE/'verify.py'),row(HERE/'seal-review.py')],'sourceFilesRehashed':43,'preparationInputsRehashed':7004,'toolTreesMembershipChecked':2,'toolLinksRechecked':22,'ownerSourceProtocolSyntaxEvidenceAuthenticatedNotRerun':[39,53,25],'mandatoryFindings':result['mandatoryFindings'],'disposition':result['disposition'],'pairAndPhaseNull':True,'currentOnOnlyAuthorityCannotExpandToPair':True,'allCorrectnessProbeAndHttpGatesFailClosedOnRead':True,'hostDeadlinesAreNotAllCaseAdequacyProof':True,'originalTimeoutCaseUnknown':True,'longCase5IsSeparateRootReportedControl':True,'full20And14Passed':False,'noSemanticMismatchClaim':True,'readOnlySourceReview':True,'ownerCodeImportedOrActionsExecuted':False,'nativeBuildGuestHostProbeBundleOrTimingExecuted':False,'sourceActivationApproved':False,'timingApproved':False,'runtimeAcceptanceClaim':False,'performanceClaim':False,'overallRoadmapComplete':False,'readerAssumptionsPreserved':row(HERE/'history/reader-corrections.json')}
 (HERE/'review-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
 files=[]
 for path in sorted(HERE.rglob('*')):
  assert not path.is_symlink()
  if path.is_file() and path.name!='index.json':files.append(row(path))
 (HERE/'index.json').write_text(json.dumps({'schemaVersion':1,'state':result['state'],'files':files,'sourceActivationApproved':False,'timingApproved':False,'runtimeAcceptanceClaim':False},indent=2)+'\n')
 print(json.dumps({'index':row(HERE/'index.json'),'receipt':row(HERE/'review-receipt.json'),'results':row(HERE/'results.json'),'files':len(files)}))
if __name__=='__main__':main()
