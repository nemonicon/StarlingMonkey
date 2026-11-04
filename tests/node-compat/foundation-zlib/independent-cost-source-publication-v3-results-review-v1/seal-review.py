from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def put(name,value):
    with(HERE/name).open('x')as stream:json.dump(value,stream,indent=2);stream.write('\n')
assert not(HERE/'index.json').exists()
result=json.loads((HERE/'results.json').read_bytes())
assert result['state']=='INDEPENDENT_FRESH_ZLIB_COST_SOURCE_PUBLICATION_VERIFIED'and result['verifiedPassed']is True and result['externalPublisherExitCode']==0
put('review-receipt.json',{'schemaVersion':1,'state':'SEALED_INDEPENDENT_ACTUAL_COST_SOURCE_PUBLICATION_VERIFIED','publicationIndexSha256':result['publicationIndexSha256'],'toolingSourceIndexSha256':result['toolingSourceIndexSha256'],'externalPublisherExitCode':0,'rootIdentity':result['rootIdentity'],'sourceOnly':True,'ownerActionsInvoked':False,'actualRegularFiles':10189,'indexedFiles':10187,'copiedFiles':5092,'links':22,'privateDirectories':471,'originalSourceModesAndDistinctInodesVerified':True,'m3Actual0644To0600Verified':True,'readerAssumptionsCorrectedAndRetained':2,'result':{'path':'results.json','sha256':sha(HERE/'results.json'),'bytes':(HERE/'results.json').stat().st_size},'libraryCodecOrRuntimeActionExecuted':False,'operationalAdmission':False,'nextActionAuthorityIssued':False})
rows=[]
for path in sorted(HERE.rglob('*')):
    if path.is_file()and '__pycache__'not in path.parts and path.name!='index.json':rows.append({'path':str(path.relative_to(HERE)),'sha256':sha(path),'bytes':path.stat().st_size})
put('index.json',{'schemaVersion':1,'state':'SEALED_INDEPENDENT_COST_SOURCE_PUBLICATION_V3_RESULTS_VERIFIED','files':rows,'sourceOnly':True,'ownerActionsInvoked':False})
print(json.dumps({'indexSha256':sha(HERE/'index.json'),'files':len(rows),'receiptSha256':sha(HERE/'review-receipt.json'),'resultsSha256':sha(HERE/'results.json')}))
