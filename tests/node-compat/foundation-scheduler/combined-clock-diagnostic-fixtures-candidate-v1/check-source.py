"""Source/data, pinned host grammar and synthetic models only; writes OWN."""
from pathlib import Path
import ast,hashlib,json,os,subprocess,time
OWN=Path(__file__).resolve().parent

def desc(p):
 p=Path(p);h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return dict(path=str(p),sha256=h.hexdigest(),bytes=p.stat().st_size)
def save(n,v):(OWN/n).write_text(json.dumps(v,indent=2)+'\n')
inputs=json.loads((OWN/'input-hashes.json').read_bytes());refs=json.loads((OWN/'references.json').read_bytes());checks=0
for row in inputs['files']:
 assert desc(row['path'])==row and not Path(row['path']).is_symlink();checks+=1
for ix in inputs['families']:
 p=Path(ix['path']).parent;v=json.loads(Path(ix['path']).read_bytes());assert{r['path']for r in v['files']}|{'index.json'}=={q.relative_to(p).as_posix()for q in p.rglob('*')if q.is_file()};checks+=1
catalogue=json.loads((OWN/'fixture-catalogue.json').read_bytes());assert len(catalogue['fixtures'])==3
for row in catalogue['fixtures']:
 for key in ['source','wit']:assert desc(row[key]['path'])==row[key];checks+=1
 assert row['selectedInterfaces']==['wasi:clocks/wall-clock@0.2.10','wasi:clocks/monotonic-clock@0.2.10','wasi:io/poll@0.2.10'];checks+=1
 assert row['sameComponentObserverRequired']is True and row['initDiagnosticSnapshotCalled']is False;checks+=1
for p in OWN.glob('*.py'):ast.parse(p.read_bytes(),filename=str(p));checks+=1
node=refs['node'];assert desc(node['path'])==node;commands=[];evidence=OWN/'evidence';evidence.mkdir(exist_ok=True)
for role,args in [('synthetic-models',[str(OWN/'test-models.mjs')]),*[(p.stem+'-grammar',['--check',str(p)])for p in sorted([OWN/'collectors.mjs',OWN/'test-models.mjs',*(OWN/'fixtures').glob('*.mjs')])]]:
 argv=[node['path'],*args];started=time.monotonic();result=subprocess.run(argv,cwd=OWN,env={k:v for k,v in os.environ.items()if k not in ['NODE_OPTIONS','NODE_PATH']},capture_output=True,timeout=30,check=False)
 (evidence/(role+'.stdout.log')).write_bytes(result.stdout);(evidence/(role+'.stderr.log')).write_bytes(result.stderr)
 record=dict(schemaVersion=1,role=role,argv=argv,cwd=str(OWN),rawExitCode=result.returncode,stdout=desc(evidence/(role+'.stdout.log')),stderr=desc(evidence/(role+'.stderr.log')),timeoutSeconds=30,wallSecondsOperationalOnly=time.monotonic()-started,hostSourceOnly=True,fixtureImported=False,privateNativeApiInvoked=False,compilerInvoked=False,guestExecuted=False,ownedGroupObservationClaim=False);save('evidence/'+role+'.terminal.json',record);commands.append(record)
 assert result.returncode==0 and result.stderr==b'';checks+=1
for row in inputs['files']:assert desc(row['path'])==row;checks+=1
assert desc(node['path'])==node
save('source-check-results.json',dict(schemaVersion=1,state='SOURCE_DATA_HOST_PURE_GRAMMAR_CHECKS_PASSED_V1',checks=checks,currentDirectInputs=len(inputs['files']),fullSourceFamilies=len(inputs['families']),hostCommands=len(commands),syntheticResult=json.loads((evidence/'synthetic-models.stdout.log').read_bytes()),ownerApiInvoked=False,fixtureOrGuestImported=False,compilerInvoked=False,nativeClockOrTaskInvoked=False))
print(json.dumps(dict(state='SOURCE_DATA_HOST_PURE_GRAMMAR_CHECKS_PASSED_V1',checks=checks,inputs=len(inputs['files']),hostCommands=len(commands),noGuestOrNativeAction=True)))
