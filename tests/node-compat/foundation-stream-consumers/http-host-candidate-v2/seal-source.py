"""One-time finite source seal; no owner/host action."""
from pathlib import Path
import hashlib,json,ast
D=Path(__file__).resolve().parent
assert not (D/'index.json').exists()
def row(p):
    p=Path(p);a=p.lstat();assert p.is_file() and not p.is_symlink();h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    z=p.lstat();assert (a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)==(z.st_dev,z.st_ino,z.st_size,z.st_mtime_ns,z.st_ctime_ns)
    return {'path':str(p),'sha256':h.hexdigest(),'bytes':z.st_size}
def load(p):return json.loads(Path(p).read_bytes())
def write(n,v):
    with (D/n).open('x') as f:json.dump(v,f,indent=2);f.write('\n')
data=load(D/'source-inputs.json')
for r in data['files']:assert row(r['path'])==r
for r in load(D/'module-edges.json')['modules']:assert row(r['path'])==r
for f in D.glob('*.py'):ast.parse(f.read_text(),filename=str(f))
c=load(D/'source-checks.json');assert c['pureChecks']==110 and c['syntaxFiles']==7 and c['exactThinEdits']==26 and c['operationalActionsInvoked'] is False
write('verification.json',{'schemaVersion':1,'state':'FINAL_HTTP_HOST_V2_INPUT_AND_SOURCE_REHASH_PASSED','inputFiles':len(data['files']),'old42AndHold10Preserved':True,'operationalActionsInvoked':False})
write('results.json',{'schemaVersion':1,'state':'HTTP_HOST_V2_SOURCE_CAPTURE_CORRECTION_CHECKS_PASSED_UNEXECUTED','sourceOnly':True,
 'preparationSourceHead':'d54d9d4b565cdd00f84cf751ac60fe5ec553f5c5','findingId':'HTTP-HOST-M1','findingCorrectedInSource':True,
 'heldV1SourceIndexSha256':'4b7c36f2d50e2c3bee831d7c4681b62bea67fb667e5da10f227125e3dd860e70','formalHoldIndexSha256':'58ec38a3f2b5b3616c27e5f8b2e40a473d70546381597647d56a0bb66577c641',
 'sourceDataChecks':c['checks'],'pureInjectedCaptureChecks':c['pureChecks'],'syntaxFiles':7,'pythonAstParses':2,'inputFiles':len(data['files']),'originalContextInputFiles':12781,
 'thinAfterimages':5,'exactForwardReverseEdits':26,'runtimeDependencyFiles':34,'moduleFiles':28,'moduleEdges':108,
 'headersDurableBeforeReaderAcquisition':True,'allObservedChunkWindowsSnapshottedAndRetainedOnFailures':True,'completePartialAndWriteFailuresDistinguished':True,'outerFailureClaimsUseActualCaptureSummaries':True,
 'inheritedCompleteFamilyAndHelperAuthenticationBeforeImportsAndFinalFailureRechecks':True,
 'guestNativeComponentOraclesValidatorsOrHostProtocolChanged':False,'oldSourceAndHoldUnchanged':True,
 'sourceIndependentReview':None,'rootAction':None,'componentPhase':None,'hostController':None,
 'fetchNetworkReaderIoServersPortsCurlPreflightGuestCodecNativeOrHostActionsInvoked':False,
 'operationalAdmission':False,'runtimeAcceptanceClaim':False,'sourcePromotionAllowed':False,
 'scope':'Source correction and pure injected transport tests only; future actual both-host execution remains unauthorized/unexecuted.'})
write('source-receipt.json',{'schemaVersion':1,'state':'SEALED_HTTP_HOST_V2_SOURCE_NO_ACTION_AUTHORITY','results':row(D/'results.json'),'sourceChecks':row(D/'source-checks.json'),'verification':row(D/'verification.json'),'ownerActionsInvoked':False,'sourceIndependentReview':None,'hostExecutionAllowed':False})
files=[]
for f in sorted(D.rglob('*')):
    if f.is_file():
        raw=f.read_bytes();raw.decode('utf-8','strict');assert b'\0' not in raw and len(raw)<=4*1024*1024
        r=row(f);files.append({'path':str(f.relative_to(D)),'sha256':r['sha256'],'bytes':r['bytes']})
write('index.json',{'schemaVersion':1,'files':files})
print(json.dumps({'index':row(D/'index.json'),'results':row(D/'results.json'),'receipt':row(D/'source-receipt.json'),'files':len(files)}))
