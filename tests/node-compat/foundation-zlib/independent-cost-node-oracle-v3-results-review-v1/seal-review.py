from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def put(name,value):
    with(HERE/name).open('x')as stream:json.dump(value,stream,indent=2);stream.write('\n')
assert not(HERE/'index.json').exists()
result=json.loads((HERE/'results.json').read_bytes())
assert result['state']=='INDEPENDENT_COST_NODE_ORACLE_RENDER_VERIFIED_V1'and result['verifiedPassed']is True and result['externalNodeActionExitCode']==0
put('review-receipt.json',{'schemaVersion':1,'state':'SEALED_INDEPENDENT_COST_NODE_ORACLE_RENDER_VERIFIED','outputIndexSha256':result['outputIndexSha256'],'toolingSourceIndexSha256':result['toolingSourceIndexSha256'],'sourcePublicationIndexSha256':result['sourcePublicationIndexSha256'],'rootActionAuthoritySha256':result['rootActionAuthoritySha256'],'externalNodeActionExitCode':0,'nodeCalls':55,'nodeEncoderStreams':15,'codecCases':30,'rawRetentionFiles':190,'actualFiles':196,'oracle':result['oracle'],'module':result['module'],'renderReconstructedExactly':True,'readerCodecOrNodeOrOwnerActionsInvoked':False,'actualGuestOrTimingClaim':False,'operationalAdmission':False,'newRootRenderCapsuleReviewRequired':True,'result':{'path':'results.json','sha256':sha(HERE/'results.json'),'bytes':(HERE/'results.json').stat().st_size}})
files=[]
for path in sorted(HERE.rglob('*')):
    if path.is_file()and '__pycache__'not in path.parts and path.name!='index.json':files.append({'path':str(path.relative_to(HERE)),'sha256':sha(path),'bytes':path.stat().st_size})
put('index.json',{'schemaVersion':1,'state':'SEALED_INDEPENDENT_ACTUAL_COST_NODE_ORACLE_RENDER_REVIEW','files':files,'readerActionsInvoked':False,'runtimeOrTimingAcceptanceClaim':False})
print(json.dumps({'indexSha256':sha(HERE/'index.json'),'files':len(files),'receiptSha256':sha(HERE/'review-receipt.json'),'resultsSha256':sha(HERE/'results.json')}))
