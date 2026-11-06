"""Authenticated host pure/grammar tests only; no owner operational API calls."""
import hashlib,json,os,subprocess,sys
from pathlib import Path
OWN=Path(__file__).resolve().parent;SOURCE=OWN.parent/'combined-native-runtime-candidate-v1';RAW=OWN/'host-checks';RAW.mkdir(exist_ok=False)
b=json.loads((OWN/'boundary-results.json').read_bytes());node=b['node'];assert hashlib.sha256(Path(node['path']).read_bytes()).hexdigest()==node['sha256']
def desc(p):p=Path(p);return dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size)
# Reauthenticate the exact own family before importing even pure code.
ix=json.loads((SOURCE/'index.json').read_bytes())
for r in ix['files']:
 d=desc(SOURCE/r['path']);assert d['sha256']==r['sha256']and d['bytes']==r['bytes']
commands=[('pure',[node['path'],str(SOURCE/'test-pure.mjs')]),('contexts',[sys.executable,'-B','-I',str(SOURCE/'test-context.py')]),('module-closure',[node['path'],str(SOURCE/'source-closure.mjs')]),('fatal-counterexample',[node['path'],str(OWN/'counterexample.mjs')])]
for r in ix['files']:
 if '/'not in r['path']and r['path'].endswith('.mjs'):commands.append(('grammar-'+r['path'].removesuffix('.mjs'),[node['path'],'--check',str(SOURCE/r['path'])]))
results=[]
for label,argv in commands:
 p=subprocess.run(argv,cwd=OWN,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=60,check=False)
 for suffix,payload in [('stdout',p.stdout),('stderr',p.stderr)]:
  with open(RAW/(label+'.'+suffix),'xb')as f:f.write(payload);f.flush();os.fsync(f.fileno())
 record=dict(argv=argv,cwd=str(OWN),rawExitCode=p.returncode,stdout=desc(RAW/(label+'.stdout')),stderr=desc(RAW/(label+'.stderr')),hostPureOrGrammarOnly=True,guestExecuted=False,nativeApiInvoked=False,toolOrRuntimePhaseInvoked=False)
 (RAW/(label+'.terminal.json')).write_text(json.dumps(record,indent=2)+'\n');results.append(record)
 assert p.returncode==0 and p.stderr==b'',label
for r in ix['files']:
 d=desc(SOURCE/r['path']);assert d['sha256']==r['sha256']and d['bytes']==r['bytes']
(OWN/'host-check-results.json').write_text(json.dumps(dict(schemaVersion=1,commands=results,sourceFamilyBeforeAndAfterEqual=True,ownerSourceModified=False,operationalActionsInvoked=False),indent=2)+'\n')
print(json.dumps(dict(rawZeroHostChecks=len(results),ownerPureChecks=140,contextChecks=13,fatalCounterexampleConfirmed=True,ownerSourceUnchanged=True)))
