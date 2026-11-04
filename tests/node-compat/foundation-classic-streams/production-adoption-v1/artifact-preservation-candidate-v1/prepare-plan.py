"""Source/data preparation only: never creates the private archive root."""
from pathlib import Path
import hashlib,json
from plan_builder import build
HERE=Path(__file__).resolve().parent
if __name__=='__main__':
    plan=build()
    with(HERE/'copy-plan.json').open('x')as out:json.dump(plan,out,indent=2);out.write('\n')
    rows=plan['objects'];logical=sum(r['bytes']for r in rows)
    summary={'schemaVersion':1,'state':'SOURCE_COPY_PLAN_PREPARED_NOT_EXECUTED','protectedOriginalDescriptors':plan['protectedOriginalDescriptors'],'unavailableInspectionDescriptors':len(plan['omissions']),'separateStatusSnapshots':len(plan['separateStatusSnapshots']),'copyObjects':len(rows),'logicalCopyBytesBeforeSourceAndAuthorityCapsules':logical,'minimumInitialFreeBytesBeforeCapsules':2*logical+1024**3,'externalReferenceOccurrences':sum(r['kind']=='reference'for r in plan['originalInputs']),'contextCounts':{'classic':8,'zlibOldFive':12},'mappedSelectedTuples':sum(len(r['rows'])for r in plan['contextMap']['contexts']),'referenceContextRows':len(plan['unmappedContextRows']),'lateMemoryIndependentProof':plan['lateMemoryIndependentProof'],'RootCopyAuthority':None,'privateRootCreated':False,'sourcePromotionIssued':False,'acceptanceIssued':False,'copyPlanSha256':hashlib.sha256((HERE/'copy-plan.json').read_bytes()).hexdigest()}
    with(HERE/'plan-summary.json').open('x')as out:json.dump(summary,out,indent=2);out.write('\n')
    print(json.dumps(summary))
