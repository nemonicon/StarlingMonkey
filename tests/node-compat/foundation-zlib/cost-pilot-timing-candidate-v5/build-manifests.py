"""Finite literal source graph and exact external DATA descriptors; no imports/actions."""
from pathlib import Path
import hashlib
import json
import re
D=Path(__file__).resolve().parent
Z=D.parent
OLD=Z/'cost-pilot-timing-candidate-v4'
assert not(D/'index.json').exists()
def row(p):
 p=Path(p);assert p.is_absolute()and p.is_file()and not p.is_symlink();a=p.stat();h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 z=p.stat();assert(a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)==(z.st_dev,z.st_ino,z.st_size,z.st_mtime_ns,z.st_ctime_ns)
 return dict(path=str(p),sha256=h.hexdigest(),bytes=z.st_size)
def save(name,value):
 (D/name).write_text(json.dumps(value,indent=2)+'\n')
def specs(text):
 values=[]
 for m in re.finditer(r'(?:import|export)\s+(?:[^;]*?)\sfrom\s+[\'"]([^\'"]+)[\'"]',text):values.append(('static',m[1]))
 for m in re.finditer(r'import\(\s*[\'"]([^\'"]+)[\'"]\s*\)',text):values.append(('literal-dynamic',m[1]))
 return values
modules={};edges=[]
def visit(p):
 p=p.resolve()
 if str(p)in modules:return
 modules[str(p)]=row(p)
 for kind,spec in specs(p.read_text()):
  edge=dict(fromPath=str(p),specifier=spec,kind=kind)
  if spec.startswith('node:'):edge['role']='standard Node API'
  else:
   assert spec.startswith('.'),(p,spec)
   target=(p.parent/spec).resolve();assert target.is_file()and target.suffix=='.mjs';edge['target']=str(target);visit(target)
  edges.append(edge)
for name in('run.mjs','worker.mjs','prepare-plan.mjs'):visit(D/name)
external=[r for p,r in modules.items()if Path(p).parent!=D]
save('module-edges.json',dict(schemaVersion=1,modules=[modules[p]for p in sorted(modules)],edges=edges,finitePinnedSourceRegexNotGeneralParser=True,completeLiteralCustomClosureBeforeBodyImport=True,nonliteralDynamicImports='Unchanged genuine prerequisite/parser/generated-loader APIs remain separately authenticated; never executed in source preparation.'))
save('runtime-dependencies.json',dict(schemaVersion=1,state='COMPLETE_V5_PARENT_WORKER_LITERAL_CUSTOM_IMPORT_CLOSURE',includesParentAndWorkerImports=True,files=sorted(external,key=lambda r:r['path'])))
worker=set()
def static_visit(p):
 p=p.resolve()
 if p in worker:return
 worker.add(p)
 for kind,spec in specs(p.read_text()):
  if kind=='static'and spec.startswith('.'):static_visit(p.parent/spec)
static_visit(D/'worker-body.mjs')
worker_external=[row(p)for p in sorted(worker)if p.parent!=D]
save('worker-dependencies.json',dict(schemaVersion=1,state='COMPLETE_V5_WORKER_STATIC_IMPORT_CLOSURE',files=worker_external,completeParentClosureAdditionallyCheckedBySourceFamilyCapsule=True,largeProofDataNotWorkerSource=True))
inputs={}
def capture(d):
 actual=row(d['path']);assert actual=={k:d[k]for k in('path','sha256','bytes')};assert inputs.setdefault(actual['path'],actual)==actual
for d in json.loads((OLD/'source-inputs.json').read_bytes())['files']:capture(d)
capture(row(OLD/'index.json'))
for d in json.loads((OLD/'index.json').read_bytes())['files']:capture(dict(d,path=str(OLD/d['path'])))
for d in external:capture(d)
refs=json.loads((D/'references.json').read_bytes())
for name in('actualPilotRootObservation','actualPilotIndex','actualPilotResults','actualMatchedPlan'):capture(refs[name])
if refs['actualCalibrationReview']is not None:
 proof=refs['actualCalibrationReview'];capture(proof['index']);root=Path(proof['index']['path']).parent
 for d in json.loads(Path(proof['index']['path']).read_bytes())['files']:capture(dict(d,path=str(root/d['path'])))
 capture(proof['result']);capture(proof['contract'])
save('source-inputs.json',dict(schemaVersion=1,files=sorted(inputs.values(),key=lambda r:r['path']),allPriorSourceFailureAndDiagnosticBytesRetained=True,inputContextsNotRelocated=True,originalPilotReviewDataSeparateFromTimingSource=True,largePilotProofMembersNotCopiedIntoWorkerSource=True,workerOrLoaderOrCodecOrRuntimeActionsInvoked=False))
runtime_names=['planner.mjs','collector.mjs','worker.template.mjs','loading.mjs','owned-lifecycle.mjs','result-collector.mjs','public-call-channel.mjs','lifecycle-policy.mjs']
save('protocol-preservation.json',dict(schemaVersion=1,unchangedRuntimeDonors=[row(Z/'cost-pilot-timing-candidate-v1'/n)for n in runtime_names],originalCases=30,comparisons=2,timingWorkers=360,timingCodecBatchCalls=3600,rawN1ControlOperations=2160,warmups=3,timedSamples=7,geometricTargetMs=50,caseOmission=False,controlSubtraction=False,limitsOrMatchedNProtocolChanged=False,newPilotLaunchAllowed=False))
print(json.dumps(dict(sourceModules=len(modules),literalEdges=len(edges),externalRuntimeDependencies=len(external),workerStaticDependencies=len(worker_external),externalInputDescriptors=len(inputs),pilotProofBound=refs['actualCalibrationReview']is not None,sourceOnly=True)))
