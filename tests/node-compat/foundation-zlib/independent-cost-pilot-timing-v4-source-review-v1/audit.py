"""Independent read/hash/byte-derivation/literal-edge audit; no owner entry import."""
from pathlib import Path
import ast,hashlib,json,re
O=Path(__file__).resolve().parent;Z=O.parent;D=Z/'cost-pilot-timing-candidate-v4'
EXPECTED='b5b4c9e9279022f63dc72f20bf9a44c831ba277017d9dc72867eafd6a24f89d1'
verified={};checks=[]
def need(v,n):assert v,n;checks.append(n)
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 return h.hexdigest()
def verify(r):
 p=Path(r['path']);a=p.lstat();need(p.is_file()and not p.is_symlink()and p.is_absolute(),'ordinary absolute descriptor')
 need(a.st_size==r['bytes']and sha(p)==r['sha256'],'exact streamed descriptor bytes')
 b=p.lstat();need((a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)==(b.st_dev,b.st_ino,b.st_size,b.st_mtime_ns,b.st_ctime_ns),'stable streamed descriptor');verified[str(p)]={k:r[k]for k in('path','sha256','bytes')}
def load(p):return json.loads(p.read_bytes())
def family(path,expected=None):
 r=dict(path=str(path),sha256=sha(path),bytes=path.stat().st_size);verify(r)
 if expected:need(r['sha256']==expected,'pinned exact family index')
 x=load(path);names=set()
 for d in x['files']:
  name=d['path'];need(name and not name.startswith('/')and all(v not in('','.','..')for v in name.split('/'))and name not in names,'unique local source membership');names.add(name);verify(dict(d,path=str(path.parent/name)))
 need(not any(p.is_symlink()for p in path.parent.rglob('*')),'no source-family links')
 need({p.relative_to(path.parent).as_posix()for p in path.parent.rglob('*')if p.is_file()}==names|{'index.json'},'complete exact source-family membership')
 return len(names)
counts={}
for name,pin in [('cost-pilot-timing-candidate-v1','55db1fc3895a0dbd10ca07e08c59bd68da8edeb9793632c8e05cb41704c5135b'),('cost-pilot-timing-candidate-v2','1a294044a4f2414d35fdd817dae95598c2e079aa64a9044737f4791aefe630a2'),('cost-pilot-timing-candidate-v3','c2ce5f08134d0cd05b9d3f10fe5bf1b49f124b1d32c49bff977d7ddb7ab064e9'),('cost-pilot-timing-candidate-v4',EXPECTED),('independent-cost-pilot-v3-failure-review-v1','231ad9828f6e0c903df6460d3efe996590194903a8e036de04f8559ab6d33edf'),('cost-pilot-v3-worker-import-diagnosis-v1','cb9ade31f04559b1d145f3931e09bbf968ea29d73500eb72e810c992629a3063')]:counts[name]=family(Z/name/'index.json',pin)
inputs=load(D/'source-inputs.json');need(len(inputs['files'])==1020,'all1020 declared input rows')
for r in inputs['files']:verify(r)
deriv=load(D/'source-derivations.json');edits=0;reverse=[]
for r in deriv['files']:
 verify(r['origin']);original=Path(r['origin']['path']).read_bytes();current=original
 for e in r['edits']:
  before=e['before'].encode();after=e['after'].encode();at=e['offsetAtEdit'];need(current.count(before)==1 and current.index(before)==at,'actual unique byte edit offset');current=current[:at]+after+current[at+len(before):];edits+=1
 need(current==(D/r['afterimage']).read_bytes()and hashlib.sha256(current).hexdigest()==r['afterSha256'],'whole byte afterimage exact')
 for e in reversed(r['edits']):
  at=e['offsetAtEdit'];before=e['before'].encode();after=e['after'].encode();need(current[at:at+len(after)]==after,'exact reverse byte segment');current=current[:at]+before+current[at+len(after):]
 need(current==original,'whole original bytes recovered');reverse.append(r['afterimage'])
need(len(reverse)==8 and edits==23,'eight files and23 explicit reversible edits')
graph=load(D/'module-edges.json');runtime=load(D/'runtime-dependencies.json');worker=load(D/'worker-dependencies.json')
for r in graph['modules']+runtime['files']+worker['files']:verify(r)
modules={};edges=[]
def specs(text):
 out=[]
 for m in re.finditer(r'(?:import|export)\s+(?:[^;]*?)\sfrom\s+[\'"]([^\'"]+)[\'"]',text):out.append(('static',m.group(1)))
 for m in re.finditer(r'import\(\s*[\'"]([^\'"]+)[\'"]\s*\)',text):out.append(('literal-dynamic',m.group(1)))
 return out
def visit(p):
 p=p.resolve()
 if str(p)in modules:return
 modules[str(p)]=dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size)
 for kind,s in specs(p.read_text()):
  e=dict(fromPath=str(p),specifier=s,kind=kind)
  if s.startswith('node:'):e['role']='standard Node API'
  else:
   need(s.startswith('.'),'no unclassified literal package load');target=(p.parent/s).resolve();need(target.is_file()and target.suffix=='.mjs','real physical custom edge');e['target']=str(target);visit(target)
  edges.append(e)
for name in('run.mjs','worker.mjs','prepare-plan.mjs'):visit(D/name)
need(sorted(modules.values(),key=lambda r:r['path'])==graph['modules']and edges==graph['edges'],'literal runtime graph reconstructed37/146')
need(sorted([r for p,r in modules.items()if Path(p).parent!=D],key=lambda r:r['path'])==runtime['files'],'all28 actual external runtime dependencies covered')
static=set()
def statics(p):
 p=p.resolve()
 if p in static:return
 static.add(p)
 for kind,s in specs(p.read_text()):
  if kind=='static'and s.startswith('.'):statics(p.parent/s)
statics(D/'worker-body.mjs')
need(sorted(str(p)for p in static if p.parent!=D)==[r['path']for r in worker['files']],'actual20 external worker static dependencies covered')
for name in('run.mjs','prepare-plan.mjs','worker.mjs'):
 s=(D/name).read_text();need(s.index('await captureSourceFamilies(')<s.index('await import('),'complete families before '+name+' body import');need('await source.recheck()'in s,'always-final wrapper audit '+name)
for name in('run-body.mjs','prepare-plan-body.mjs','worker-body.mjs'):need('assertSourceFamilyAudit(sourceFamilyAudit,'in(D/name).read_text(),'private source capsule required '+name)
auth=(D/'source-families.mjs').read_text();need('new WeakSet()'in auth and 'issued.has(capsule)'in auth and 'families.at(-1)'in auth and 'verifiedSourceFamilies:4'in auth,'real private full four-family audit')
need('for(const family of families)await family.recheck()'in auth and 'await dependencies.recheck()'in auth,'full-family and actual-module rechecks')
body=(D/'worker-body.mjs').read_text();entry=(D/'worker.mjs').read_text()
need(body.count('measurementEnvironmentModel(')==2 and 'measurementEnvironmentModel(observedEnvironment,platformFacts)'in body and 'measurementEnvironmentModel({...process.env},platformFacts)'in body,'only real model inputs are fresh enumerable process.env snapshots')
need(body.index('measurementEnvironmentModel(observedEnvironment')<body.index("await output.write('started.json'")<body.index('await loadTimingSession('),'environment validated and durably observed before actual loader')
need('observedEnvironment,platformFacts,environmentObservationScope:'in body and 'same({...process.env},observedEnvironment)'in body,'actual observed environment saved and exact rechecked')
need('finally{try{await source.recheck();}catch(error)'in entry and 'if(!bodyFailed)'in entry,'diagnostic stage retained through successful failure audit')
need('typeof error'in entry and not any(x in entry for x in('error.message','error.stack','error.name','Object.keys(error)','Object.getPrototypeOf(error)')),'bounded diagnostic no exception-property reads')
preserve=load(D/'protocol-preservation.json')
for r in preserve['unchangedRuntimeDonors']:verify(r)
for name in('run.mjs','run-body.mjs'):need((D/name).read_bytes()==(Z/'cost-pilot-timing-candidate-v3'/name).read_bytes(),'actual parent caller/protocol unchanged '+name)
need([preserve[k]for k in('originalCases','comparisons','timingWorkers','timingCodecBatchCalls','rawN1ControlOperations','warmups','timedSamples')]==[30,2,360,3600,2160,3,7],'unchanged finite full schedule')
for name in('future-authority.template.json','future-plan-authority.template.json'):
 v=load(D/name);need(v['sourceIndexSha256']is None and v['sourceIndependentReview']is None,'source/peer authority NULL')
 for k in('actionAllowed','dataPublicationAllowed'):
  if k in v:need(v[k]is False,'no actual phase permission')
 for k in('preparedPlan','phaseAuthority','quietWindowAuthority','warmNPlan','warmNMatchedPlan','globalBudgetMs'):
  if k in v:need(v[k]is None,'future action DATA NULL')
for p in D.glob('*.py'):ast.parse(p.read_bytes(),filename=str(p))
for name in('boundaries','source-families'):
 t=load(D/'evidence'/f'{name}.terminal.json');need(t['rawExitCode']==0 and t['runWorkerOrRunPhaseOrPreparePlanCalled']is False,'stored author pure/read-hash terminal zero and no operational entry')
owner_syntax=load(D/'evidence/syntax.json');need(len(owner_syntax)==11 and all(r['rawExitCode']==0 for r in owner_syntax),'stored11 parser-only success records')
result=dict(schemaVersion=1,state='INDEPENDENT_V4_CODEC_SOURCE_READ_HASH_DERIVATION_AUDIT_PASSED',checks=len(checks),families=counts,uniquePaths=len(verified),inputRows=1020,derivedFiles=reverse,exactEdits=edits,literalModules=len(modules),literalEdges=len(edges),externalRuntimeDependencies=len(runtime['files']),externalWorkerDependencies=len(worker['files']),ownerModulesOrTestsOrActionsImported=False,sourceOnly=True)
with(O/'audit-results.json').open('x')as f:json.dump(result,f,indent=2);f.write('\n')
with(O/'verified-inputs.json').open('x')as f:json.dump(dict(schemaVersion=1,files=[verified[p]for p in sorted(verified)]),f,indent=2);f.write('\n')
print(json.dumps(result))
