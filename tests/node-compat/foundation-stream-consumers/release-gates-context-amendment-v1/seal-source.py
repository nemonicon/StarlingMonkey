"""Source-only sealing; no publisher/preflight/admit/selector action."""
from pathlib import Path
import ast,hashlib,json,os,subprocess
HERE=Path(__file__).parent.resolve();NODE='/private/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node'
def h(raw):return hashlib.sha256(raw).hexdigest()
def write(name,value):
    p=HERE/name;p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x')as f:json.dump(value,f,indent=2);f.write('\n')
assert not(HERE/'index.json').exists();env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'};env.pop('PYTHONOPTIMIZE',None);reports={}
for label,argv in[('contexts',[NODE,str(HERE/'test-contexts.mjs')]),('source',['python3',str(HERE/'check-source.py')])]:
    r=subprocess.run(argv,capture_output=True,env=env)
    for name,raw in[('stdout',r.stdout),('stderr',r.stderr)]:
        p=HERE/'evidence'/(label+'.'+name+'.log');p.parent.mkdir(exist_ok=True)
        with p.open('xb')as f:f.write(raw)
    assert r.returncode==0,r.stderr.decode();reports[label]=json.loads(r.stdout);write('evidence/'+label+'-results.json',{'command':argv,'exitCode':r.returncode,'report':reports[label]})
syntax=[]
for p in sorted(HERE.iterdir()):
    if p.suffix=='.mjs':r=subprocess.run([NODE,'--check',str(p)],capture_output=True);assert r.returncode==0,r.stderr.decode();syntax.append({'path':p.name,'nodeCheckExitCode':r.returncode})
    elif p.suffix=='.py':ast.parse(p.read_text());syntax.append({'path':p.name,'ASTParsed':True})
write('evidence/syntax-results.json',{'state':'SOURCE_PARSE_ONLY_PASSED','files':syntax,'checks':len(syntax)})
inputs={r['path']:r for r in json.loads((HERE/'source-check-inputs.json').read_text())['files']}
for family,expected in[('independent-release-gates-preflight-v1-results-review-v1','ffafa4739d7b39292c2752f802704791a3b1b37440b492a1dd48ad9923629600')]:
    root=HERE.parent/family;raw=(root/'index.json').read_bytes();assert h(raw)==expected;ix=json.loads(raw)
    for r in ix['files']+[{'path':'index.json','sha256':expected,'bytes':len(raw)}]:
        p=root/r['path'];b=p.read_bytes();assert h(b)==r['sha256']and len(b)==r['bytes'];inputs[str(p)]={'path':str(p),'sha256':h(b),'bytes':len(b)}
write('input-freeze.json',{'schemaVersion':1,'state':'SOURCE_CONTEXT_CORRECTION_REFERENCES_NOT_RUNTIME_AUTHORITY','files':list(inputs.values()),'oldContextFailurePreserved':True,'ownerHelperActionsInvoked':False})
write('source-receipt.json',{'schemaVersion':1,'state':'CONSUMERS355_CONTEXT_M1_SOURCE_CORRECTION_UNREVIEWED','parentSourceIndexSha256':'a74dc603f7e42384892c9f4b69a2ba131a87a80daa38da19e91bbc2c099e5372','failedGeneratedSourceIndexSha256':'10d6df0205a17394343be49864f4ed82847292397732b5f821090ec78d94289b','failureReviewIndexSha256':'ffafa4739d7b39292c2752f802704791a3b1b37440b492a1dd48ad9923629600','contextChecks':reports['contexts']['checks'],'sourceDataChecks':reports['source']['checks'],'parseChecks':len(syntax),'configuredAndFrozenNativeSourcesEach':355,'configuredToolDependenciesDataChecked':767,'templateReversibleEdits':5,'actualGenuineAdmitOrPreflightInvoked':False,'publisherMainInvoked':False,'nativeGuestHostCompilerOrTimingInvoked':False,'nativeMetadataProjected':False,'guestOracleCaseAndNativeBytesChanged':False,'runtimeAcceptanceClaim':False})
rows=[]
for p in sorted(HERE.rglob('*')):
    if p.is_dir():continue
    assert p.is_file()and not p.is_symlink();b=p.read_bytes();rows.append({'path':str(p.relative_to(HERE)),'sha256':h(b),'bytes':len(b)})
write('index.json',{'schemaVersion':1,'state':'CONSUMERS355_CONTEXT_AMENDMENT_SOURCE_ONLY','files':rows,'sourceOnly':True,'actionsAllowed':False})
print(json.dumps({'indexSha256':h((HERE/'index.json').read_bytes()),'files':len(rows),'inputRows':len(inputs),'sourceOnly':True}))
