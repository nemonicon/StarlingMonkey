from pathlib import Path
import hashlib,json,shutil
OWN=Path(__file__).resolve().parent;ROOT=Path('/private/tmp/starling-node-compat/next-startup-v2-sdk-syntax-v1')
def d(p):
 p=Path(p);b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def read(p):return json.loads(Path(p).read_bytes())
def save(n,v):(OWN/n).write_text(json.dumps(v,indent=2)+'\n')
assert not(OWN/'index.json').exists();r=read(ROOT/'result.json');dep=read(OWN/'dependency-reconciliation.json');assert dep['allRetainedDependencyPathsAuthenticated']is True
raw=OWN/'raw';raw.mkdir(exist_ok=True);copies=[];units=[]
for u in r['units']:
 folder=raw/u['id'];folder.mkdir(exist_ok=True);ext=ROOT/'commands'/u['id'];t=read(ext/'terminal.json');owned_clean=t['parentOwnedGroupGone']and t['allObservedOwnedGroupsGone']and not t['timeout']and not t['forcedCleanup']and all(not t[k]for k in ['errors','signals','interruptedSignals','remainingObservedPids'])
 for p in [ext/'stdout.log',ext/'stderr.log',ext/'terminal.json',ROOT/'commands'/(u['id']+'.d')]:
  if p.exists():q=folder/p.name;shutil.copyfile(p,q);copies.append(dict(original=d(p),copy=d(q)))
 units.append(dict(id=u['id'],argv=u['argv'],rawExitCode=t['rawExitCode'],ownedClean=owned_clean,stderr=d(ext/'stderr.log'),depfile=u['dependencies'],dependencyReaderOriginalErrors=len(u['dependencyErrors']),dependencyReconciliationErrors=next(len(x['errors'])for x in dep['units']if x['id']==u['id'])))
assert [u['rawExitCode']for u in units]==[0,1,1,0,1,0];assert all(u['ownedClean']for u in units);assert r['finalProtection']['unchanged']and r['privateCopiesUnchanged']
shutil.copyfile(ROOT/'root-authorization.json',raw/'root-authorization.json');copies.append(dict(original=d(ROOT/'root-authorization.json'),copy=d(raw/'root-authorization.json')))
save('raw-copy-map.json',dict(schemaVersion=1,files=copies,originalWholeResult=d(ROOT/'result.json'),originalStart=d(ROOT/'start.json'),originalVFS=d(ROOT/'overlay.json')))
save('results.json',dict(schemaVersion=1,state='NEXT_STARTUP_V2_SDK_SYNTAX_PARTIAL_RESULTS_RETAINED_V1',originalPhasePassed=False,originalResult=d(ROOT/'result.json'),plan=r['plan'],sourceIndex=r['sourceIndex'],units=units,successfulActualCpp=['buffer','rng','performance'],failedIntendedInputPlan=['module-p2','startup','registration'],allOwnedGroupsGone=True,originalsProtection=r['finalProtection'],private68CopiesUnchanged=r['privateCopiesUnchanged'],dependencyReconciliation=d(OWN/'dependency-reconciliation.json'),dependencyDataReadOnlyReconciliationPassed=True,compilerInvocations=6,compilerReruns=0,objectOrLinkOrEngineOrGuestExecuted=False,fullSourceOrAbiAdmission=False))
files=[]
for p in sorted(OWN.rglob('*')):
 assert not p.is_symlink()
 if p.is_file():files.append(dict(d(p),path=p.relative_to(OWN).as_posix()))
save('index.json',dict(schemaVersion=1,state='SEALED_PARTIAL_SDK_RESULTS_NOT_NATIVE_ADMISSION_V1',files=files))
for n in ['index.json','results.json']:print(json.dumps(d(OWN/n)))
