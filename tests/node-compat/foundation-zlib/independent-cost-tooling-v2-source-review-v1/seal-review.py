from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent
OWNER=HERE.with_name('cost-tooling-candidate-v2')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(name,value):
    with(HERE/name).open('x')as stream:json.dump(value,stream,indent=2);stream.write('\n')
assert not(HERE/'index.json').exists()
source_sha='6793721e6781bf045825f2a1c83108f97136f682fdae4d725ece4c31c750891b'
assert sha(OWNER/'index.json')==source_sha
result=json.loads((HERE/'results.json').read_bytes())
assert result['state']=='INDEPENDENT_ZLIB_COST_TOOLING_SOURCE_REVIEW_PASSED'and result['sourceReviewPassed']is True and result['ownerActionsInvoked']is False
put('review-receipt.json',{'schemaVersion':1,'state':'INDEPENDENT_ZLIB_COST_TOOLING_SOURCE_REVIEW_PASSED','toolingSourceIndexSha256':source_sha,'sourceOnly':True,'sourceReviewPassed':True,'ownerActionsInvoked':False,'sourceAndDataChecks':17,'indexedOwnerFiles':254,'preparationRows':5324,'futureCopyObjects':5058,'toolFiles':4890,'toolLinks':22,'lexicalPaths':6644,'physicalContentHashReads':6642,'closedFindings':['COST-TOOLING-M1','COST-TOOLING-M2'],'remainingConcreteSourceBlockers':[],'result':{'path':'results.json','sha256':sha(HERE/'results.json'),'bytes':(HERE/'results.json').stat().st_size},'actualActionOrRuntimeOrReadinessOrAcceptanceClaim':False})
files=[]
for p in sorted(HERE.rglob('*')):
    if p.is_file()and '__pycache__'not in p.parts and p.name!='index.json':files.append({'path':str(p.relative_to(HERE)),'sha256':sha(p),'bytes':p.stat().st_size})
put('index.json',{'schemaVersion':1,'state':'SEALED_INDEPENDENT_COST_TOOLING_V2_BOUNDED_SOURCE_PASS','files':files,'sourceOnly':True,'ownerActionsInvoked':False})
print(json.dumps({'indexSha256':sha(HERE/'index.json'),'files':len(files),'receiptSha256':sha(HERE/'review-receipt.json'),'resultsSha256':sha(HERE/'results.json')}))
