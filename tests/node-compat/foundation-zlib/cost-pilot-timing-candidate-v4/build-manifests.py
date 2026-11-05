"""Finite pinned-source import inventory and inherited input capture; no action import."""
from pathlib import Path
import hashlib,json,re
D=Path(__file__).resolve().parent;Z=D.parent;OLD=Z/'cost-pilot-timing-candidate-v3'
def row(p):
 p=Path(p);b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def save(n,v):
 with(D/n).open('x')as f:json.dump(v,f,indent=2);f.write('\n')
def specifiers(text):
 found=[]
 for m in re.finditer(r'(?:import|export)\s+(?:[^;]*?)\sfrom\s+[\'\"]([^\'\"]+)[\'\"]',text):found.append(('static',m.group(1)))
 for m in re.finditer(r'import\(\s*[\'\"]([^\'\"]+)[\'\"]\s*\)',text):found.append(('literal-dynamic',m.group(1)))
 return found
roots=['run.mjs','worker.mjs','prepare-plan.mjs'];modules={};edges=[]
def visit(p):
 p=p.resolve()
 if str(p)in modules:return
 modules[str(p)]=row(p)
 for kind,spec in specifiers(p.read_text()):
  edge=dict(fromPath=str(p),specifier=spec,kind=kind)
  if spec.startswith('node:'):edge['role']='standard Node API'
  else:
   assert spec.startswith('.'),('unclassified package',p,spec)
   target=(p.parent/spec).resolve();assert target.is_file()and target.suffix=='.mjs'
   edge['target']=str(target);visit(target)
  edges.append(edge)
for name in roots:visit(D/name)
external=[r for p,r in modules.items()if Path(p).parent!=D]
assert len(external)==28,(len(external),sorted(modules))
save('module-edges.json',dict(schemaVersion=1,modules=[modules[p]for p in sorted(modules)],edges=edges,
 finitePinnedSourceRegexNotGeneralParser=True,nonliteralDynamicImports='Existing reviewed parser/generated-module loaders and genuine proof guard APIs remain unchanged and separately admitted; not executed here.',
 completeLiteralCustomClosureBeforeBodyImport=True))
save('runtime-dependencies.json',dict(schemaVersion=1,state='COMPLETE_V4_PARENT_WORKER_LITERAL_CUSTOM_IMPORT_CLOSURE',includesParentAndWorkerImports=True,files=sorted(external,key=lambda r:r['path'])))
worker_modules=set()
def static_visit(p):
 p=p.resolve()
 if p in worker_modules:return
 worker_modules.add(p)
 for kind,spec in specifiers(p.read_text()):
  if kind=='static'and spec.startswith('.'):static_visit(p.parent/spec)
static_visit(D/'worker-body.mjs')
worker_external=[row(p)for p in sorted(worker_modules)if p.parent!=D]
save('worker-dependencies.json',dict(schemaVersion=1,state='COMPLETE_V4_WORKER_STATIC_IMPORT_CLOSURE',files=worker_external,
 completeParentClosureAdditionallyCheckedBySourceFamilyCapsule=True))
oldtest=(OLD/'test-source-families.mjs').read_text()
newtest=oldtest.replace('[85,26]','[85,26,50]').replace('zlib-cost-source-families-v3-','zlib-cost-source-families-v4-').replace('PASSED_V3','PASSED_V4')
with(D/'test-source-families.mjs').open('x')as f:f.write(newtest)
inputs={}
def capture(d):
 got=row(d['path']);assert got=={k:d[k]for k in ['path','sha256','bytes']};inputs[d['path']]=got
for r in json.loads((OLD/'source-inputs.json').read_text())['files']:capture(r)
for name in ['cost-pilot-timing-candidate-v3','cost-pilot-v3-failure-root-checkpoint-v1','independent-cost-pilot-v3-failure-review-v1','cost-pilot-v3-worker-import-diagnosis-v1']:
 p=Z/name/'index.json';capture(row(p))
 for r in json.loads(p.read_text())['files']:capture(dict(r,path=str(p.parent/r['path'])))
for r in external:capture(r)
save('source-inputs.json',dict(schemaVersion=1,files=[inputs[p]for p in sorted(inputs)],allPriorSourceFailureAndDiagnosticBytesRetained=True,
 inputContextsNotRelocated=True,workerOrLoaderOrCodecOrRuntimeActionsInvoked=False))
save('protocol-preservation.json',dict(schemaVersion=1,unchangedRuntimeDonors=[row(Z/'cost-pilot-timing-candidate-v1'/n)for n in ['planner.mjs','collector.mjs','worker.template.mjs','loading.mjs','owned-lifecycle.mjs','result-collector.mjs','public-call-channel.mjs','lifecycle-policy.mjs']],
 originalCases=30,comparisons=2,timingWorkers=360,timingCodecBatchCalls=3600,rawN1ControlOperations=2160,warmups=3,timedSamples=7,
 geometricTargetMs=50,caseOmission=False,controlSubtraction=False,limitsOrMatchedNProtocolChanged=False))
print(json.dumps(dict(sourceModules=len(modules),edges=len(edges),runtimeDependencies=len(external),workerStaticDependencies=len(worker_external),inheritedInputs=len(inputs),actionsInvoked=False)))
