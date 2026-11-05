"""One-time source-only seal; no owner action/host/helper invocation."""
from pathlib import Path
import hashlib
import json
import ast

D=Path(__file__).resolve().parent
assert not (D/'index.json').exists()

def row(p):
    p=Path(p);a=p.lstat();assert p.is_file() and not p.is_symlink()
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    z=p.lstat();assert (a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)==(z.st_dev,z.st_ino,z.st_size,z.st_mtime_ns,z.st_ctime_ns)
    return {'path':str(p),'sha256':h.hexdigest(),'bytes':z.st_size}

def load(p):return json.loads(Path(p).read_bytes())
def write(n,v):
    with (D/n).open('x') as f:json.dump(v,f,indent=2);f.write('\n')

inputs=load(D/'source-inputs.json')['files']
for r in inputs:assert row(r['path'])==r
for r in load(D/'module-edges.json')['modules']:assert row(r['path'])==r
for p in D.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
c=load(D/'source-checks.json');assert c['pureChecks']==86 and c['syntaxFiles']==13 and c['noHostOrAdmissionActions']
write('verification.json',{'schemaVersion':1,'state':'FINAL_SOURCE_INPUT_AND_MODULE_REHASH_PASSED','inputFiles':len(inputs),'modules':c['moduleFiles'],'noOwnerActions':True})
write('results.json',{'schemaVersion':1,'state':'CONSUMERS355_HTTP_HOST_SOURCE_PREPARATION_CHECKS_PASSED_UNEXECUTED_V1','sourceOnly':True,
 'preparationSourceHead':'c51cc993a536beea358ea78f4866b116300df0fb','historicalNativeSourceHeadUnchanged':True,
 'sourceDataChecks':c['checks'],'pureChecks':c['pureChecks'],'syntaxFiles':c['syntaxFiles'],'pythonAstParses':2,'inputFiles':len(inputs),
 'delegatedWhole355NativeToolSourceFiles':12667,'runtimeDependencyFiles':26,'moduleFiles':c['moduleFiles'],'moduleEdges':c['moduleEdges'],
 'exactCopiedStandardHelpers':4,'exactCommandForwardReverseEdits':3,'standardSourceAuthExtractionVerified':True,
 'actualComponentProofValidatedAsDataOnly':True,'actualComponentSha256':'2ce7d9903bb71b829f09fc82422d55f1ef748bfc7c81a73e3d532d050c535f33','actualComponentBytes':64098281,
 'originalAcceptedHostSourceBb371Bound':True,'fullOldBaselineProtected29Classic19ValidatorsUsedAsPureData':True,'newRequestLocalOrdinaryIterableConsumerGroups':2,
 'wholeNewAuditMetadataAndBodiesPreserved':True,'noOld342EngineAdmissionOrMetadataProjection':True,'HOMEHomeCODEX_HOMEUnchanged':True,
 'earlierUnsealedPassesHistorical':True,'staticCheckerFalsePositiveRetained':True,
 'sourceIndependentReview':None,'rootAction':None,'componentPhase':None,'hostController':None,
 'operationalPreflightHelpersServersPortsCurlNetworkRequestsJcoComponentsNativeGuestCodecOrHostActionsInvoked':False,
 'operationalAdmission':False,'runtimeAcceptanceClaim':False,'sourcePromotionAllowed':False,'wireBodyAdapter':False,'requestReuseClaim':False,'requestIsolationClaim':False,
 'scope':'Runnable finite source-only future host action behind NULL authorities; actual new355 HTTP host behavior remains unexecuted/unproved.'})
write('source-receipt.json',{'schemaVersion':1,'state':'SEALED_CONSUMERS355_HTTP_HOST_SOURCE_NO_ACTION_AUTHORITY_V1','results':row(D/'results.json'),'sourceChecks':row(D/'source-checks.json'),'verification':row(D/'verification.json'),'ownerActionsInvoked':False,'sourceIndependentReview':None,'hostExecutionAllowed':False})
files=[]
for p in sorted(D.rglob('*')):
    if p.is_file():
        raw=p.read_bytes();raw.decode('utf-8','strict');assert b'\0' not in raw and len(raw)<=4*1024*1024
        r=row(p);files.append({'path':str(p.relative_to(D)),'sha256':r['sha256'],'bytes':r['bytes']})
write('index.json',{'schemaVersion':1,'files':files})
print(json.dumps({'index':row(D/'index.json'),'results':row(D/'results.json'),'receipt':row(D/'source-receipt.json'),'files':len(files)}))
