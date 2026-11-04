from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent
OWNER=HERE.with_name('cost-component-candidate-v1')
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def put(name,value):
    with(HERE/name).open('x')as stream:json.dump(value,stream,indent=2);stream.write('\n')
assert not(HERE/'index.json').exists()
source_sha='a2fa62b3ab63a6aca044aec9a83c1ff5a09edaa208eb615226a13845bf1522f9'
assert sha(OWNER/'index.json')==source_sha
result=json.loads((HERE/'results.json').read_bytes())
assert result['state']=='INDEPENDENT_ZLIB_COST_COMPONENT_SOURCE_REVIEW_PASSED_V1'and result['sourceReviewPassed']is True and result['ownerActionsInvoked']is False
put('review-receipt.json',{'schemaVersion':1,'state':'INDEPENDENT_ZLIB_COST_COMPONENT_SOURCE_REVIEW_PASSED_V1','componentSourceIndexSha256':source_sha,'sourceOnly':True,'sourceReviewPassed':True,'ownerActionsInvoked':False,'sourceAndDataChecks':23,'indexedFiles':25,'preparationRows':294,'baseSourceFiles':286,'copiedMechanisms':5,'lexicalPaths':334,'actual53512AdapterAndWit7Verified':True,'remainingConcreteSourceBlockers':[],'actualComponentOrAbiOrOrdinaryGuestProof':None,'operationalAdmission':False,'metadataProjection':False,'result':{'path':'results.json','sha256':sha(HERE/'results.json'),'bytes':(HERE/'results.json').stat().st_size}})
files=[]
for path in sorted(HERE.rglob('*')):
    if path.is_file()and '__pycache__'not in path.parts and path.name!='index.json':files.append({'path':str(path.relative_to(HERE)),'sha256':sha(path),'bytes':path.stat().st_size})
put('index.json',{'schemaVersion':1,'state':'SEALED_INDEPENDENT_COST_COMPONENT_SOURCE_REVIEW_PASS','files':files,'sourceOnly':True,'ownerActionsInvoked':False})
print(json.dumps({'indexSha256':sha(HERE/'index.json'),'files':len(files),'receiptSha256':sha(HERE/'review-receipt.json'),'resultsSha256':sha(HERE/'results.json')}))
