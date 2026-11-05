"""Derive dormant Source v2 only. Never imports owner or package APIs."""
from pathlib import Path
import hashlib,json
P=Path(__file__).resolve().parent;OLD=P.parent/'clock-package-loader-candidate-v1';HOLD=P.parent/'independent-clock-package-loader-source-review-v1'
assert not(P/'index.json').exists()
def read(p):return json.loads(Path(p).read_bytes())
def row(p):
 p=Path(p);b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def write(n,v):(P/n).write_text(json.dumps(v,indent=2)+'\n')
oldix=row(OLD/'index.json');assert oldix['sha256']=='21b9f3063de6995b555400b2afd6deb3fdf0a6191fb1a540a6673ddb59dc060c'
for base in [OLD,HOLD]:
 for m in read(base/'index.json')['files']:assert row(base/m['path'])==dict(m,path=str(base/m['path']))
edits=[]
def change(text,before,after,label):
 assert text.count(before)==1,(label,text.count(before));edits.append(dict(label=label,before=before,after=after));return text.replace(before,after)
code=(OLD/'loader.mjs').read_text()
gate='''function createLoadGate(){
  let issued=false,retainedRecheck=null;
  return Object.freeze({
    retain(recheck){assert(typeof recheck==='function');retainedRecheck=recheck;},
    run:async(load)=>{
      try{
        assert(!issued,'One helper load per fresh owned process');issued=true;
        return await load();
      }finally{if(retainedRecheck)await retainedRecheck();}
    }
  });
}
const loadGate=createLoadGate();'''
code=change(code,'let handleIssued=false;',gate,'Pure one-load gate retains latest actual partial/full recheck')
code=change(code,str(OLD),str(P),'Own physical Source context')
code=change(code,"ROOT_REVIEWED_EXPERIMENTAL_CLOCK_PACKAGE_CONSTRUCTION_V1","ROOT_REVIEWED_EXPERIMENTAL_CLOCK_PACKAGE_CONSTRUCTION_V2",'New explicit Root phase')
code=change(code,"CLOCK_PACKAGE_LOADER_CONFIG_V1","CLOCK_PACKAGE_LOADER_CONFIG_V2",'New config kind')
code=change(code,"INDEPENDENT_CLOCK_PACKAGE_LOADER_SOURCE_REVIEW_PASSED_V1","INDEPENDENT_CLOCK_PACKAGE_LOADER_SOURCE_REVIEW_PASSED_V2",'New independent Source peer')
code=change(code,"kind:'experimental-clock-package-v1'","kind:'experimental-clock-package-v2'",'Honest distinct tooling provenance')
code=change(code,"export async function loadExperimentalClockPackage({configDescriptor}){\n  const configRow=descriptor(configDescriptor);assert(!handleIssued,'One helper load per fresh owned process');handleIssued=true;", "export async function loadExperimentalClockPackage(input={}){\n  return loadGate.run(async()=>{\n  const configRow=descriptor(input?.configDescriptor);",'Gate before input capture; invalid repeated config never inspected')
code=change(code,'  const c=new Capture();','  const c=new Capture();loadGate.retain(()=>c.recheck());','Retain genuine partial capture immediately')
needle='  try{\n    await recheck();\n    const capability='
code=change(code,needle,'  loadGate.retain(recheck);\n'+needle,'Retain genuine complete native/package/TMP/environment check before imports')
code=change(code,'  }finally{await c.recheck();}\n}\n\nasync function fingerprint','  }finally{await c.recheck();}\n  });\n}\n\nasync function fingerprint','All load outcomes and forbidden repeats pass gate finally')
(P/'loader.mjs').write_text(code)
reverse=code
for e in reversed(edits):assert reverse.count(e['after'])==1;reverse=reverse.replace(e['after'],e['before'])
assert reverse==(OLD/'loader.mjs').read_text()
test=(OLD/'test-pure.mjs').read_text().replace('ROOT_REVIEWED_EXPERIMENTAL_CLOCK_PACKAGE_CONSTRUCTION_V1','ROOT_REVIEWED_EXPERIMENTAL_CLOCK_PACKAGE_CONSTRUCTION_V2')
# Add tests before original final JSON summary. Only inert helper/pure functions
# are imported; actual package, load API and componentize are never executed.
needle="console.log(JSON.stringify("
at=test.index(needle)
extra='''// Genuine shared load gate and actual exported-call seam, with pure rechecks.
const gateStart=allText.indexOf('function createLoadGate(){'),gateEnd=allText.indexOf('const loadGate=createLoadGate();',gateStart);
const gateFactory=vm.runInNewContext(allText.slice(gateStart,gateEnd)+'\\ncreateLoadGate;',{assert,Object});
{
  const gate=gateFactory(),events=[];let bodies=0;
  assert.equal(await gate.run(async()=>{bodies++;gate.retain(async()=>events.push('partial'));gate.retain(async()=>events.push('complete'));return 9;}),9);
  assert.deepEqual(events,['complete']);checks++;
  await assert.rejects(()=>gate.run(async()=>{bodies++;throw new Error('unreachable');}));
  assert.equal(bodies,1);assert.deepEqual(events,['complete','complete']);checks++;
  const loadStart=allText.indexOf('export async function loadExperimentalClockPackage('),loadEnd=allText.indexOf('\\n\\nasync function fingerprint',loadStart);
  const realLoad=vm.runInNewContext(allText.slice(loadStart,loadEnd).replace('export async function','async function')+'\\nloadExperimentalClockPackage;',{loadGate:gate});
  let reads=0;const poison={get configDescriptor(){reads++;throw new Error('must not read repeated config');}};
  await assert.rejects(()=>realLoad(poison));assert.equal(reads,0);assert.equal(events.length,3);checks++;
  for(const invalid of [undefined,null,1,{}]){await assert.rejects(()=>realLoad(invalid));assert.equal(reads,0);}assert.equal(events.length,7);checks++;
}
{
  const gate=gateFactory();let bodies=0,rechecks=0;
  await assert.rejects(()=>gate.run(async()=>{bodies++;gate.retain(async()=>{rechecks++;});throw new Error('partial Source failure');}),/partial Source failure/);
  assert.equal(rechecks,1);checks++;
  await assert.rejects(()=>gate.run(async()=>{bodies++;}));assert.equal(bodies,1);assert.equal(rechecks,2);checks++;
}
{
  const gate=gateFactory();let rechecks=0,bodies=0;
  await assert.rejects(()=>gate.run(async()=>{bodies++;gate.retain(async()=>{rechecks++;throw new Error('retained protection failure');});}),/retained protection failure/);
  await assert.rejects(()=>gate.run(async()=>{bodies++;}),/retained protection failure/);
  assert.equal(bodies,1);assert.equal(rechecks,2);checks++;
}
{
  const gate=gateFactory();let n=0;
  await assert.rejects(()=>gate.run(async()=>{n++;throw new Error('before capture');}),/before capture/);
  await assert.rejects(()=>gate.run(async()=>{n++;}));assert.equal(n,1);checks++;
}
'''
test=test[:at]+extra+test[at:];(P/'test-pure.mjs').write_text(test)
refs=read(OLD/'references.json');refs['state']='EXPERIMENTAL_CLOCK_PACKAGE_SOURCE_FACTS_ONLY_V2';refs['predecessorSourceIndex']=oldix;refs['predecessorHeldReview']=dict(index=row(HOLD/'index.json'),result=row(HOLD/'results.json'));refs['requiredCorrectionContract']=row(HOLD/'required-correction-contract.json');write('references.json',refs)
for name in ['package-links.json','caller-contract.json','root-authority.template.json','config.template.json','future-source-review-contract.json']:
 value=read(OLD/name)
 if name=='config.template.json':value['state']='CLOCK_PACKAGE_LOADER_CONFIG_V2'
 if name=='future-source-review-contract.json':value['requiredState']='INDEPENDENT_CLOCK_PACKAGE_LOADER_SOURCE_REVIEW_PASSED_V2'
 if name=='caller-contract.json':value['state']='FUTURE_DISTINCT_EXPERIMENTAL_CLOCK_PACKAGE_CALLER_CONTRACT_V2';value['loadBookend']='The genuine partial capture recheck is retained once Capture exists; the full original recheck replaces it before imports. Every forbidden subsequent load refuses without reading repeated input or entering the body and runs the latest retained check in finally. Calls that fail before any Capture exists cannot claim a captured closure.'
 write(name,value)
inputs=read(OLD/'source-inputs.json');rows={r['path']:r for r in inputs['files']}
for base in [OLD,HOLD]:
 rows[str(base/'index.json')]=row(base/'index.json')
 for m in read(base/'index.json')['files']:r=dict(m,path=str(base/m['path']));rows[r['path']]=r
inputs['files']=sorted(rows.values(),key=lambda r:r['path']);inputs['families'] += [oldix,row(HOLD/'index.json')];inputs['scope']='Complete v2 executable dependency scope plus immutable v1 and formal HOLD DATA; no package or native action'
write('source-inputs.json',inputs)
write('derivations.json',dict(schemaVersion=1,predecessorSourceIndex=oldix,predecessorLoader=row(OLD/'loader.mjs'),newLoader=row(P/'loader.mjs'),exactReversibleEdits=edits,wholeReversePassed=True,unchangedPackageLinks=(P/'package-links.json').read_bytes()==(OLD/'package-links.json').read_bytes(),allNativePackageArtifactBytesUnchanged=True,ownerActionsInvoked=False))
print(json.dumps(dict(loader=row(P/'loader.mjs'),reversibleEdits=len(edits),inputRows=len(inputs['files']),families=len(inputs['families']),actions=0)))
