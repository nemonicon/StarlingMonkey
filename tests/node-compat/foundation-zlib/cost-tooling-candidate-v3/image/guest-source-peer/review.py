"""Finite source/data review. Only audited pure checks and parsing execute."""
from pathlib import Path
import hashlib,json,os,subprocess,time,ast
HERE=Path(__file__).resolve().parent
SOURCE=HERE.with_name('cost-guest-oracle-candidate-v2')
NODE='/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node'
PIN='ebe8fa901a3516358539c0458b09cad822308f9a3b0c76db33015ff378a8eae8'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def desc(path):
    raw=path.read_bytes();return dict(path=str(path),sha256=sha(raw),bytes=len(raw))
def save(name,value):
    with (HERE/name).open('x') as f:json.dump(value,f,indent=2);f.write('\n')
index=json.loads((SOURCE/'index.json').read_bytes());assert sha((SOURCE/'index.json').read_bytes())==PIN
inputs=json.loads((SOURCE/'source-inputs.json').read_bytes())['files']
source_rows=[dict(path=str(SOURCE/r['path']),sha256=r['sha256'],bytes=r['bytes'])for r in index['files']]
def recheck():
    for row in source_rows+inputs:
        p=Path(row['path']);assert p.is_file()and not p.is_symlink()
        actual=desc(p);assert actual['sha256']==row['sha256']and actual['bytes']==row['bytes'],str(p)
recheck();assert len(source_rows)==38 and len(inputs)==199
save('original-input-context.json',dict(sourceIndex=desc(SOURCE/'index.json'),indexedSource=source_rows,consumedPreparation=inputs,nestedPreparationManifestsFollowed=False))
gold=json.loads((SOURCE/'raw-fixture-oracle.json').read_bytes())['fixtures'];fixture_results=[]
for i,(name,size,pattern)in enumerate([('empty',0,'empty'),('small-repeat',64,'repeat'),('small-prng',64,'prng'),('large-repeat',524288,'repeat'),('large-prng',524288,'prng')]):
    state=0x6d2b79f5;raw=bytearray();fnv=2166136261
    for j in range(size):
        if pattern=='repeat':value=b'abc123'[j%6]
        else:
            state^=(state<<13)&0xffffffff;state^=state>>17;state^=(state<<5)&0xffffffff;state&=0xffffffff;value=state&255
        raw.append(value);fnv=((fnv^value)*16777619)&0xffffffff
    row=gold[i];assert row['id']==name and row['bytes']==size and row['rawSha256']==sha(raw)and row['rawFNV1aU32']==fnv
    fixture_results.append(dict(id=name,bytes=size,sha256=sha(raw),fnv1aU32=fnv))
parent=json.loads((SOURCE/'parent-protocol.json').read_bytes())
case_text=(SOURCE/'cases.generated.mjs').read_text();case_rows=json.loads(case_text.split('Object.freeze(',1)[1].rsplit('.map(Object.freeze));',1)[0])
assert case_rows==[dict(index=i,**row)for i,row in enumerate(parent['cases'])]and len(case_rows)==30
save('independent-fixture-and-case-results.json',dict(fixtureResults=fixture_results,wholeThirtyRowsExact=True,codecCalls=0))
for path in SOURCE.glob('*.py'):ast.parse(path.read_bytes())
env={k:v for k,v in os.environ.items()if k not in('NODE_OPTIONS','NODE_PATH')};env['PYTHONDONTWRITEBYTECODE']='1';env['CODEC_COST_PURE_RESULTS']=str(HERE/'pure-results.json')
commands=[('pure',[NODE,str(SOURCE/'test-pure.mjs')]),('source',['python3',str(SOURCE/'check-source.py'),str(HERE/'source-results.json')]),('generator',['python3',str(SOURCE/'generate-cases.py'),'--check']),('counterexample',[NODE,str(HERE/'counterexample.mjs'),str(HERE/'counterexample-results.json')])]
commands += [('parse-'+p.stem,[NODE,'--check',str(p)])for p in sorted(SOURCE.glob('*.mjs'))]
terminals=[]
for name,argv in commands:
    start=time.monotonic()
    with (HERE/(name+'.stdout.log')).open('xb')as out,(HERE/(name+'.stderr.log')).open('xb')as err:
        child=subprocess.run(argv,stdout=out,stderr=err,env=env)
    terminal=dict(name=name,argv=argv,rawExitCode=child.returncode,elapsedOperationalSeconds=time.monotonic()-start,stdout=desc(HERE/(name+'.stdout.log')),stderr=desc(HERE/(name+'.stderr.log')))
    terminals.append(terminal);assert child.returncode==0,terminal
save('terminals.json',terminals)
pure=json.loads((HERE/'pure-results.json').read_bytes());checks=json.loads((HERE/'source-results.json').read_bytes());example=json.loads((HERE/'counterexample-results.json').read_bytes())
assert pure['passed']==116 and pure['forbiddenProviderCalls']==0 and checks['passed']==32 and len(example['records'])==3
recheck()
save('results.json',dict(schemaVersion=1,state='INDEPENDENT_CODEC_GUEST_V2_SOURCE_REVIEW_PASSED_V1',sourceIndexSha256=PIN,indexedSourceFiles=38,preparationReferences=199,independentRawFixtures=5,wholeCaseRows=30,pureChecks=116,sourceChecks=32,parseOnlyChecks=len(list(SOURCE.glob('*.mjs'))),counterexamples=3,blockers=[],closedBlockers=['COST-GUEST-M1'],auditedPureAndParseChecksExecuted=True,codecProviderOraclePublisherPreflightBundleNativeGuestHostPilotOrTimingExecuted=False,positiveActionsApproved=False,operationalAdmission=False,allSourceAndInputHashesStillMatch=True))
print(json.dumps(dict(state='SOURCE_PASS',closedBlocker='COST-GUEST-M1',indexed=38,inputs=199,pure=116,regressions=3,codecCalls=0)))
