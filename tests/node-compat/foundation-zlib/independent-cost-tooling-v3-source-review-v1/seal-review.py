from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent
OWNER=HERE.with_name('cost-tooling-candidate-v3')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(name,value):
    with(HERE/name).open('x')as stream:json.dump(value,stream,indent=2);stream.write('\n')
assert not(HERE/'index.json').exists()
source_sha='ff208e72d0b87933aa75cdeb7c1ae16f29aa6ae94c357318a9d6676af04b36b8'
assert sha(OWNER/'index.json')==source_sha
result=json.loads((HERE/'results.json').read_bytes())
assert result['state']=='INDEPENDENT_ZLIB_COST_TOOLING_SOURCE_REVIEW_PASSED'and result['sourceReviewPassed']is True and result['ownerActionsInvoked']is False
put('review-receipt.json',{'schemaVersion':1,'state':'INDEPENDENT_ZLIB_COST_TOOLING_SOURCE_REVIEW_PASSED','toolingSourceIndexSha256':source_sha,'sourceOnly':True,'sourceReviewPassed':True,'ownerActionsInvoked':False,'sourceAndDataChecks':20,'indexedOwnerFiles':286,'preparationRows':5357,'futureCopyObjects':5072,'toolFiles':4890,'toolLinks':22,'lexicalPaths':6710,'physicalContentHashReads':6708,'closedFindings':['COST-TOOLING-M3'],'inheritedM1M2GuardsByteIdentical':True,'remainingConcreteSourceBlockers':[],'actual0644To0600SavedTinyBytesAndModesVerified':True,'actualBulkPublisherActionInvoked':False,'result':{'path':'results.json','sha256':sha(HERE/'results.json'),'bytes':(HERE/'results.json').stat().st_size},'actualActionOrRuntimeOrReadinessOrAcceptanceClaim':False})
files=[]
for p in sorted(HERE.rglob('*')):
    if p.is_file()and '__pycache__'not in p.parts and p.name!='index.json':files.append({'path':str(p.relative_to(HERE)),'sha256':sha(p),'bytes':p.stat().st_size})
put('index.json',{'schemaVersion':1,'state':'SEALED_INDEPENDENT_COST_TOOLING_V3_FOCUSED_SOURCE_PASS','files':files,'sourceOnly':True,'ownerActionsInvoked':False})
print(json.dumps({'indexSha256':sha(HERE/'index.json'),'files':len(files),'receiptSha256':sha(HERE/'review-receipt.json'),'resultsSha256':sha(HERE/'results.json')}))
