from pathlib import Path
import json,hashlib
HERE=Path(__file__).resolve().parent
OWNER=HERE.with_name('cost-tooling-candidate-v1')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(name,value):
 with(HERE/name).open('x')as f:json.dump(value,f,indent=2);f.write('\n')
assert not(HERE/'index.json').exists()
assert sha(OWNER/'index.json')=='f5f13bfa0256a3e89d87827ea40d12dfbf617a23c304ba3b8335167c02bc3049'
result=json.loads((HERE/'results.json').read_bytes());assert result['sourceReviewPassed']is False and result['ownerActionsInvoked']is False
put('review-receipt.json',{'schemaVersion':1,'state':'INDEPENDENT_ZLIB_COST_TOOLING_SOURCE_REVIEW_HELD','toolingSourceIndexSha256':result['toolingSourceIndexSha256'],'sourceOnly':True,'sourceReviewPassed':False,'ownerActionsInvoked':False,'indexedOwnerFiles':224,'preparationRows':5089,'plannedCopyObjects':5047,'toolFiles':4890,'toolLinks':22,'frozenRowsPerVariant':1024,'lexicalPaths':6362,'physicalContentHashReads':6360,'sourceAndDataChecks':9,'findings':['COST-TOOLING-M1','COST-TOOLING-M2'],'result':{'path':'results.json','sha256':sha(HERE/'results.json'),'bytes':(HERE/'results.json').stat().st_size},'runtimeOrReadinessOrAcceptanceClaim':False})
rows=[]
for p in sorted(HERE.rglob('*')):
 if p.is_file()and '__pycache__'not in p.parts and p.name!='index.json':rows.append({'path':str(p.relative_to(HERE)),'sha256':sha(p),'bytes':p.stat().st_size})
put('index.json',{'schemaVersion':1,'state':'SEALED_INDEPENDENT_COST_TOOLING_V1_SOURCE_HOLD','files':rows,'sourceOnly':True,'ownerActionsInvoked':False})
print(json.dumps({'indexSha256':sha(HERE/'index.json'),'files':len(rows),'receiptSha256':sha(HERE/'review-receipt.json'),'resultsSha256':sha(HERE/'results.json')}))
