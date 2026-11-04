"""Source-only seal. Executes pure models, source readers and parser checks."""
import ast,hashlib,json,os,subprocess
from pathlib import Path
HERE=Path(__file__).parent.resolve();NODE='/private/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def write(name,value):
    p=HERE/name;p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x')as f:json.dump(value,f,indent=2);f.write('\n')
def raw(name,value):
    p=HERE/name;p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('xb')as f:f.write(value)
assert not(HERE/'index.json').exists()
env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'};env.pop('PYTHONOPTIMIZE',None);reports={}
for name,argv in[('pure',[NODE,str(HERE/'test-pure.mjs')]),('source',['python3',str(HERE/'check-source.py')])]:
    r=subprocess.run(argv,capture_output=True,env=env);raw('evidence/'+name+'.stdout.log',r.stdout);raw('evidence/'+name+'.stderr.log',r.stderr);assert r.returncode==0,(name,r.stderr.decode());reports[name]=json.loads(r.stdout);write('evidence/'+name+'-results.json',{'command':argv,'returncode':r.returncode,'report':reports[name]})
syntax=[]
for p in sorted(HERE.iterdir()):
    if p.suffix=='.mjs':
        r=subprocess.run([NODE,'--check',str(p)],capture_output=True);assert r.returncode==0,r.stderr.decode();syntax.append({'path':p.name,'nodeCheckExitCode':r.returncode})
    elif p.suffix=='.py':ast.parse(p.read_text());syntax.append({'path':p.name,'ASTParsed':True})
write('evidence/syntax-results.json',{'state':'SOURCE_PARSE_ONLY_PASSED','checks':len(syntax),'files':syntax})
inputs={}
def capture(p,expected=None):
    p=Path(p);b=p.read_bytes();assert expected is None or sha(b)==expected;inputs[str(p.resolve())]={'path':str(p.resolve()),'sha256':sha(b),'bytes':len(b)}
base=HERE.with_name('cost-tooling-candidate-v3');capture(base/'index.json','ff208e72d0b87933aa75cdeb7c1ae16f29aa6ae94c357318a9d6676af04b36b8')
for r in json.loads((base/'index.json').read_text())['files']:capture(base/r['path'],r['sha256'])
for r in json.loads((HERE/'copied-mechanisms.json').read_text())['files']:capture(r['path'],r['sha256'])
for p in[HERE.parent/'cost-guest-oracle-candidate-v2/index.json',HERE.parent/'cost-source-protocol-amendment-root-decision-v2.json',Path('/private/tmp/starling-node-compat/import-abi-clock-v2-build/package/src/componentize.js'),Path('/private/tmp/starling-node-compat/native-toolchain-lock/node_modules/@bytecodealliance/jco/dist/cmd/transpile.d.ts'),Path('/private/tmp/starling-node-compat/zlib-cost-source-v3/index.json')]:capture(p)
write('input-freeze.json',{'schemaVersion':1,'state':'SOURCE_PREPARATION_REFERENCES_NOT_EXECUTABLE_CONSUMED_CONTEXT','files':list(inputs.values()),'oldPreparationRowsFollowedAsRuntimeContext':False})
write('source-receipt.json',{'schemaVersion':1,'state':'ZLIB_COST_COMPONENT_SOURCE_IMPLEMENTED_UNREVIEWED','toolingSourceIndexSha256':'ff208e72d0b87933aa75cdeb7c1ae16f29aa6ae94c357318a9d6676af04b36b8','guestSourceIndexSha256':'ebe8fa901a3516358539c0458b09cad822308f9a3b0c76db33015ff378a8eae8','publicationIndexSha256':'4621f7e72b4fb0555a5df630b1aedd4d2a04743b0db9188fc50099779f07387b','pureChecks':reports['pure']['checks'],'sourceChecks':reports['source']['checks'],'parseChecks':len(syntax),'sourceOnly':True,'ownerActionMainsInvoked':False,'codecLibraryBundleComponentizerTranspilerWasmGuestNativeHostPilotTimingOrOwnedProcessInvoked':False,'ordinaryGuestCorrectnessImplemented':False,'pilotTimingImplemented':False,'operationalAdmission':False,'metadataProjection':False,'actualComponentOrABI':None})
files=[]
for p in sorted(HERE.rglob('*')):
    if p.is_dir():continue
    assert p.is_file()and not p.is_symlink()and '__pycache__'not in p.parts;b=p.read_bytes();files.append({'path':str(p.relative_to(HERE)),'sha256':sha(b),'bytes':len(b)})
write('index.json',{'schemaVersion':1,'state':'ZLIB_COST_COMPONENT_SOURCE_ONLY_NOT_ACTION_AUTHORITY','files':files,'sourceOnly':True,'actionsAllowed':False,'operationalAdmission':False})
print(json.dumps({'indexSha256':sha((HERE/'index.json').read_bytes()),'files':len(files),'inputRows':len(inputs),'sourceOnly':True,'actionsInvoked':False}))
