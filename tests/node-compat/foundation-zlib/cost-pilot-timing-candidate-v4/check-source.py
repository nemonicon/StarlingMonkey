"""Source/data/reversible-byte checks only. No owner entrypoint or workload import."""
from pathlib import Path
import ast,hashlib,json,os
D=Path(__file__).resolve().parent;Z=D.parent;checks=0
def need(v,m):
 global checks
 checks+=1
 if not v:raise AssertionError(m)
def row(p):
 p=Path(p);need(p.is_file()and not p.is_symlink(),'regular source/data')
 a=p.stat();h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 z=p.stat();need((a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)==(z.st_dev,z.st_ino,z.st_size,z.st_mtime_ns,z.st_ctime_ns),'stable hash')
 return dict(path=str(p),sha256=h.hexdigest(),bytes=z.st_size)
def load(p):return json.loads(Path(p).read_text())
def verify(d):need(row(d['path'])=={k:d[k]for k in ['path','sha256','bytes']},'exact recorded bytes')
def save(n,v):
 with(D/n).open('x')as f:json.dump(v,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
inputs=load(D/'source-inputs.json')
for d in inputs['files']:verify(d)
der=load(D/'source-derivations.json');edits=0
for record in der['files']:
 verify(record['origin']);old=Path(record['origin']['path']).read_text();current=old
 for e in record['edits']:
  need(current.count(e['before'])==1 and current.index(e['before'])==e['offsetAtEdit'],'exact unique edit offset')
  current=current[:e['offsetAtEdit']]+e['after']+current[e['offsetAtEdit']+len(e['before']):];edits+=1
 need(current==(D/record['afterimage']).read_text(),'whole afterimage exact')
 for e in reversed(record['edits']):
  at=e['offsetAtEdit'];need(current[at:at+len(e['after'])]==e['after'],'reverse exact segment');current=current[:at]+e['before']+current[at+len(e['after']):]
 need(current==old,'whole predecessor bytes recovered')
need(len(der['files'])==8,'eight explicit derived files, small bootstrap full replacement disclosed')
for n in ['run-body.mjs','run.mjs']:need((D/n).read_bytes()==(Z/'cost-pilot-timing-candidate-v3'/n).read_bytes(),'actual parent run/protocol unchanged')
for d in load(D/'protocol-preservation.json')['unchangedRuntimeDonors']:verify(d)
graph=load(D/'module-edges.json')
for d in graph['modules']:verify(d)
need(len(graph['modules'])==37 and len(graph['edges'])==146,'full literal graph37/146')
runtime=load(D/'runtime-dependencies.json');worker=load(D/'worker-dependencies.json')
need(len(runtime['files'])==28 and len(worker['files'])==20,'external runtime and worker module roles')
for d in runtime['files']+worker['files']:verify(d)
need(all(Path(d['path']).parent!=D for d in runtime['files']),'own modules protected by own family, external dependencies explicit')
for edge in graph['edges']:
 if 'target'in edge:need((Path(edge['fromPath']).parent/edge['specifier']).resolve()==Path(edge['target'])and Path(edge['target']).is_file(),'literal edge actual physical target')
for n in ['run.mjs','worker.mjs','prepare-plan.mjs']:
 text=(D/n).read_text();need(text.index('await captureSourceFamilies(')<text.index('await import('),'family auth before body import '+n)
 need('await source.recheck()'in text,'wrapper final/failure source recheck '+n)
for n in ['run-body.mjs','worker-body.mjs','prepare-plan-body.mjs']:
 text=(D/n).read_text();need('assertSourceFamilyAudit(sourceFamilyAudit,'in text and 'if(process.argv[1]'not in text,'private genuine capsule/no alternate body CLI '+n)
auth=(D/'source-families.mjs').read_text();need('families.at(-1).rows.find'in auth and 'verifiedSourceFamilies:4'in auth,'actual v4 own-index role after three fixed ancestors')
need('new WeakSet()'in auth and 'issued.has(capsule)'in auth,'auth capsule not forgeable data')
body=(D/'worker-body.mjs').read_text();entry=(D/'worker.mjs').read_text();environment=(D/'environment.mjs').read_text()
need('observedEnvironment,platformFacts,environmentObservationScope:'in body,'actual validated runtime environment retained')
need("if(!bodyFailed)markStage('wrapper-final-recheck')"in entry,'original failure stage survives successful final audit')
need('process.stderr.write(line'in entry and "event:'cost-worker-complete'"in entry,'failure stderr separated from existing stdout protocol')
need(not any(token in entry for token in ['error.name','error.message','error.stack','Object.keys(error)','Object.getPrototypeOf(error)']),'no caught error getters/enumeration/prototype reads')
need('typeof error'in entry and 'Buffer.byteLength(line)>2048'in entry,'bounded primitive/fixed-label diagnostic')
need(not any(token in environment+body+entry for token in ['delete process.env','process.env =','process.env=']),'no environment mutation')
need("platform!=='darwin'"in environment and 'uid.toString(16).toUpperCase()'in environment and "':0x0:0x0'"in environment,'finite CF uid/zero/zero')
boundary=load(D/'evidence/boundaries.stdout.json');source=load(D/'evidence/source-families.stdout.json');syntax=load(D/'evidence/syntax.json')
need(boundary['checks']==97 and boundary['errorPropertyReads']==boundary['environmentGetterReads']==0,'97 pure checks and hostile getter boundaries')
need(boundary['workerCalled']is False and boundary['loaderCalled']is False and boundary['guestOrCodecOrPreflightInvoked']is False,'no worker/provider/helper operation in pure tests')
need(source['checks']==25 and [r['indexedMembers']for r in source['inherited']]==[85,26,50],'three real inherited families plus scratch negatives')
need(source['sourceHelperScratchFilesNeverImportedOrExecuted']is True,'scratch modules only DATA')
need(len(syntax)==11 and all(d['rawExitCode']==0 and d['stdout']==d['stderr']==''for d in syntax),'11 parser-only commands')
for n in ['boundaries','source-families']:
 t=load(D/'evidence'/f'{n}.terminal.json');need(t['rawExitCode']==0 and t['runWorkerOrRunPhaseOrPreparePlanCalled']is False,'real source/pure terminal0')
 need((D/'evidence'/f'{n}.stderr.log').read_bytes()==b'','complete pure-test stderr empty')
scratch=Path(source['scratch']);captured=[]
for p in sorted(scratch.rglob('*')):
 need(not p.is_symlink(),'scratch DATA no symlink')
 if p.is_file():
  target=D/'evidence/scratch'/p.relative_to(scratch);target.parent.mkdir(parents=True,exist_ok=True)
  with target.open('xb')as f:f.write(p.read_bytes())
  original=row(p);actual=row(target);need(actual['sha256']==original['sha256']and actual['bytes']==original['bytes'],'captured scratch actual bytes')
  captured.append(dict(original=original,copy=str(target.relative_to(D))))
save('scratch-evidence.json',dict(schemaVersion=1,copies=captured,fixtureSourceNeverImported=True))
for n in ['future-authority.template.json','future-plan-authority.template.json']:
 v=load(D/n);need(v['sourceIndexSha256']is None and v['sourceIndependentReview']is None,'null source/action fields')
 need(v.get('actionAllowed',False)is False and v.get('dataPublicationAllowed',False)is False,'no actual phase permission')
 for field in ['preparedPlan','phaseAuthority','quietWindowAuthority','warmNPlan','warmNMatchedPlan','globalBudgetMs']:
  if field in v:need(v[field]is None,'null future '+field)
for root in ['zlib-cost-pilot-v4','zlib-cost-timing-v4','zlib-cost-measurement-plan-v4']:
 need(not(Path('/private/tmp/starling-node-compat')/root).exists(),'no actual v4 output '+root)
for p in D.glob('*.py'):ast.parse(p.read_text())
save('source-checks.json',dict(schemaVersion=1,state='V4_FINITE_ENVIRONMENT_DIAGNOSTIC_SOURCE_CHECKS_PASSED',checks=checks,externalInputFiles=len(inputs['files']),derivedFiles=8,exactEdits=edits,pureBoundaryChecks=97,sourceFamilyScratchChecks=25,syntaxFiles=11,runtimeModules=37,literalEdges=146,externalRuntimeDependencies=28,workerStaticDependencies=20,originalInheritedFamilies=[85,26,50],sourceOnly=True,workerLoaderPreflightGuestCodecNativeRuntimeInvoked=False))
print(json.dumps(load(D/'source-checks.json')))
