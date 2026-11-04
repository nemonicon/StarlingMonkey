"""Small source/data seal. No parser/tool/owner/component/guest actions."""
import ast,difflib,hashlib,json,os,subprocess
from pathlib import Path
HERE=Path(__file__).parent.resolve();BASE=HERE.with_name('cost-component-candidate-v1');PARSER=HERE.with_name('cost-component-wit-parameter-parser-regression-root-v1');NODE='/private/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node'
def h(raw):return hashlib.sha256(raw).hexdigest()
def write(name,value):
    p=HERE/name;p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x')as f:json.dump(value,f,indent=2);f.write('\n')
inputs={}
def capture(path,sha=None):
    p=Path(path);b=p.read_bytes();assert p.is_file()and not p.is_symlink()and(sha is None or h(b)==sha);inputs[str(p.resolve())]={'path':str(p.resolve()),'sha256':h(b),'bytes':len(b)};return b
assert not(HERE/'index.json').exists();ix=capture(BASE/'index.json','a2fa62b3ab63a6aca044aec9a83c1ff5a09edaa208eb615226a13845bf1522f9')
for r in json.loads(ix)['files']:assert len(capture(BASE/r['path'],r['sha256']))==r['bytes']
parser_ix=capture(PARSER/'index.json','5fe4a9a5d10941d78f63ff6ce0f7da13871f927663ee69e68f7d452ada7abb4b')
for r in json.loads(parser_ix)['files']:assert len(capture(PARSER/r['path'],r['sha256']))==r['bytes']
parser=json.loads(capture(PARSER/'results.json'));assert [r['rawExitCode']for r in parser['records']]==[1,0];assert capture(HERE/'public-abi.wit')==capture(PARSER/'corrected.wit');assert len(capture(parser['records'][1]['dummyOutput']['path'],parser['records'][1]['dummyOutput']['sha256']))==797
changes=[]
for name in['guard.mjs','build.mjs','build-worker.mjs','public-abi.wit']:
    old=capture(BASE/name);new=capture(HERE/name);delta=list(difflib.ndiff(old.decode().splitlines(keepends=True),new.decode().splitlines(keepends=True)));assert ''.join(difflib.restore(delta,1)).encode()==old and ''.join(difflib.restore(delta,2)).encode()==new;changes.append({'path':name,'beforeSha256':h(old),'afterSha256':h(new),'exactReverse':True,'ndiff':delta})
assert capture(HERE/'build-worker.mjs')==capture(BASE/'build-worker.mjs')
guard=(HERE/'guard.mjs').read_text();assert "sourceIndex(join(HERE,'../cost-component-candidate-v1/index.json'),COMPONENT_BASE_SHA)"in guard and 'await donor.recheck()'in guard
build=(HERE/'build.mjs').read_text();assert "'control/'"in build and "'../cost-component-candidate-v1',name"in build
for name in['authority.mjs','abi.mjs','collector.mjs','proofs.mjs','durable.mjs','durable-host.mjs']:
    assert(HERE/name).read_text()=="// Immutable donor mechanism; complete donor source/critical closure is verified.\nexport * from '../cost-component-candidate-v1/"+name+"';\n";capture(BASE/name)
    assert "'"+name+"'"in build
for p in[HERE.with_name('cost-component-native-on-v1-failure-root-results.json')]:capture(p,'15bae01c512e37c283fe2ec1ab3c7ecbfc1a60b7506cb678f4e8ce2784f9a65d')
env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'};env.pop('PYTHONOPTIMIZE',None);r=subprocess.run([NODE,str(HERE/'test-pure.mjs')],capture_output=True,env=env)
for n,b in[('stdout.log',r.stdout),('stderr.log',r.stderr)]:
    p=HERE/'evidence'/n;p.parent.mkdir(exist_ok=True)
    with p.open('xb')as f:f.write(b)
assert r.returncode==0,r.stderr.decode();pure=json.loads(r.stdout)
syntax=[]
for p in sorted(HERE.iterdir()):
    if p.suffix=='.mjs':s=subprocess.run([NODE,'--check',str(p)],capture_output=True);assert s.returncode==0,s.stderr.decode();syntax.append({'path':p.name,'nodeCheckExitCode':0})
    elif p.suffix=='.py':ast.parse(p.read_text());syntax.append({'path':p.name,'ASTParsed':True})
write('derivations.json',{'schemaVersion':1,'files':changes,'parameterNameChanges':2,'typeArityWireProtocolUnchanged':True,'workerBodyByteIdentical':True,'ownDonorAndToolSourceIndicesDistinct':True})
write('input-freeze.json',{'schemaVersion':1,'files':list(inputs.values()),'preparationReferencesOnly':True,'ownerHelpersInvoked':False})
write('source-receipt.json',{'schemaVersion':1,'state':'COMPONENT_RESERVED_WIT_PARAMETER_SOURCE_CORRECTION_UNREVIEWED','baseComponentSourceIndexSha256':h(ix),'parserRegressionIndexSha256':h(parser_ix),'correctedWitSha256':h((HERE/'public-abi.wit').read_bytes()),'pureChecks':pure['checks'],'parseChecks':len(syntax),'parentObservedParserExitCodes':[1,0],'authorParserToolOrComponentOrGuestActionsInvoked':False,'runtimeAcceptanceClaim':False,'ownSourceRootRequired':True,'newOutputNamespace':'zlib-cost-component-v2','metadataProjection':False})
write('evidence/syntax-results.json',{'checks':len(syntax),'files':syntax,'parserOrOwnerActionsInvoked':False})
rows=[]
for p in sorted(HERE.rglob('*')):
    if p.is_dir():continue
    assert p.is_file()and not p.is_symlink();b=p.read_bytes();rows.append({'path':str(p.relative_to(HERE)),'sha256':h(b),'bytes':len(b)})
write('index.json',{'schemaVersion':1,'state':'SMALL_COMPONENT_WIT_PARAMETER_SOURCE_AMENDMENT_ONLY','files':rows,'sourceOnly':True,'actionsAllowed':False});print(json.dumps({'indexSha256':h((HERE/'index.json').read_bytes()),'files':len(rows),'inputRows':len(inputs),'sourceOnly':True}))
