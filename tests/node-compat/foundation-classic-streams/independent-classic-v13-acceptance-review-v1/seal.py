"""Seal only this narrow independent acceptance audit. No authority is issued."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).parent
CLASSIC=HERE.parent
ACCEPT=CLASSIC/'production-acceptance-v13'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def load(path):return json.loads(Path(path).read_bytes())
def write(name,value):
    with(HERE/name).open('x')as f:json.dump(value,f,indent=2);f.write('\n')
result=load(HERE/'results.json');assert result['scopeReviewPassed']is True and len(result['checks'])==8 and result['concreteScopeOverclaims']==[]
receipt=load(ACCEPT/'acceptance-receipt.json')
assert sha((ACCEPT/'acceptance-receipt.json').read_bytes())=='86e2230a6be37639f4ecadec8900bd1238ac38711f63150ec515d1f1e49bcc2b'
assert sha((ACCEPT/'index.json').read_bytes())=='398ecd5257b09a8038edae81ec7bcb2c2c3f9233ff2d41aeb783a48cd752b8b2'
http_ref=next(r for r in receipt['references']if r['path'].endswith('/corrected-http-combined-root-results.json'))
http_raw=Path(http_ref['path']).read_bytes();assert sha(http_raw)==http_ref['sha256']
http=json.loads(http_raw)
descriptors=[]
def visit(value):
    if isinstance(value,dict):
        if all(k in value for k in ['path','sha256','bytes']):descriptors.append(value)
        for child in value.values():
            if isinstance(child,(dict,list)):visit(child)
    elif isinstance(value,list):
        for child in value:visit(child)
visit(http)
host_data=[]
for name in ['http-joint-wasmcloud-results.json','wasmtime-results.json']:
    row=next(v for v in descriptors if v['path'].endswith('/'+name))
    raw=Path(row['path']).read_bytes();assert sha(raw)==row['sha256'] and len(raw)==row['bytes']
    value=json.loads(raw)
    if name=='http-joint-wasmcloud-results.json':
        assert value['host']['version']=='2.11.0' and value['host']['embeddedWasmtimeVersion']=='48.0.7'
        version='wash2.11.0/embeddedWasmtime48.0.7'
    else:
        assert value['wasmtime'].startswith('wasmtime 42.0.1 ')
        version=value['wasmtime']
    host_data.append({'path':row['path'],'sha256':row['sha256'],'bytes':row['bytes'],'observedSavedVersion':version})
write('host-version-checks.json',{'schemaVersion':1,'state':'SAVED_HOST_VERSION_FIELDS_MATCH_BOUNDED_V13_TARGETS','records':host_data,'hostOrVersionCommandExecuted':False,'rootHttpReferenceSha256':http_ref['sha256']})
write('review-receipt.json',{'schemaVersion':1,'state':'INDEPENDENT_BOUNDED_CLASSIC_V13_ACCEPTANCE_REVIEW_COMPLETE',
    'acceptanceIndexSha256':'398ecd5257b09a8038edae81ec7bcb2c2c3f9233ff2d41aeb783a48cd752b8b2',
    'acceptanceReceiptSha256':'86e2230a6be37639f4ecadec8900bd1238ac38711f63150ec515d1f1e49bcc2b',
    'resultsSha256':sha((HERE/'results.json').read_bytes()),'proofIndicesVerified':11,'indexedProofMembersVerified':230,
    'explicitRootReferencesVerified':13,'concreteScopeOverclaims':[],'narrowScopeOnly':True,
    'oldConsumedRowsOrOwnerAuditsInvoked':False,'archiveBytesRetested':False,'newAuthorityIssued':False,
    'sourcePromotionIssued':False,'guestNativeHostBuildOrTimingActionExecuted':False,'overallRoadmapComplete':False})
rows=[]
for path in sorted(HERE.rglob('*')):
    if path.is_dir():continue
    assert not path.is_symlink()
    if path.name=='index.json':continue
    raw=path.read_bytes();assert b'\0'not in raw;raw.decode('utf-8','strict')
    rows.append({'path':str(path.relative_to(HERE)),'sha256':sha(raw),'bytes':len(raw)})
write('index.json',{'schemaVersion':1,'state':'SEALED_INDEPENDENT_BOUNDED_CLASSIC_V13_ACCEPTANCE_SCOPE_REVIEW','files':rows,'fileCount':len(rows),'bytes':sum(r['bytes']for r in rows),'newAuthorityIssued':False})
for row in rows:
    raw=(HERE/row['path']).read_bytes();assert sha(raw)==row['sha256']and len(raw)==row['bytes']
print(json.dumps({'indexSha256':sha((HERE/'index.json').read_bytes()),'indexedFiles':len(rows),'resultsSha256':sha((HERE/'results.json').read_bytes()),'receiptSha256':sha((HERE/'review-receipt.json').read_bytes())}))
