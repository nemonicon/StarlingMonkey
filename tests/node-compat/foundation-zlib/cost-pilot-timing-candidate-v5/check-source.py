"""Read/hash, exact derivations and source checks only. No action imports."""
from pathlib import Path
import ast
import hashlib
import json
import re
D=Path(__file__).resolve().parent
OLD=D.parent/'cost-pilot-timing-candidate-v4'
checks=0
def need(v,m):
 global checks
 checks+=1
 assert v,m
def row(p):
 p=Path(p);need(p.is_absolute()and p.is_file()and not p.is_symlink(),'absolute ordinary file');a=p.stat();h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 z=p.stat();need((a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)==(z.st_dev,z.st_ino,z.st_size,z.st_mtime_ns,z.st_ctime_ns),'stable source bytes');return dict(path=str(p),sha256=h.hexdigest(),bytes=z.st_size)
def load(p):return json.loads(Path(p).read_bytes())
def verify(d):need(row(d['path'])=={k:d[k]for k in('path','sha256','bytes')},'exact declared bytes')
inputs=load(D/'source-inputs.json')
for r in inputs['files']:verify(r)
der=load(D/'source-derivations.json');edit_count=0;copies=0
for record in der['files']:
 verify(record['donor']);original=Path(record['donor']['path']).read_text();text=original
 for e in record['edits']:
  need(text.count(e['before'])==e['count'],'forward count');text=text.replace(e['before'],e['after']);edit_count+=1
 need(text==(D/record['afterimage']).read_text(),'whole exact afterimage')
 for e in reversed(record['edits']):need(text.count(e['after'])==e['count'],'reverse count');text=text.replace(e['after'],e['before'])
 need(text==original,'exact donor recovered')
 if not record['edits']:copies+=1
need(len(der['files'])==9 and edit_count==26 and copies==3,'nine explicit files/26 edits/three exact copies')
for record in der['templates']:
 verify(record['donor']);need(load(record['donor']['path'])==record['donorValue']and load(D/record['afterimage'])==record['afterValue'],'exact template DATA derivation')
 expected=dict(record['donorValue'])
 if record['afterimage']=='future-authority.template.json':expected['calibrationSourceIndex']=None
 if record['afterimage']=='future-plan-authority.template.json':expected['outputRoot']='/private/tmp/starling-node-compat/zlib-cost-measurement-plan-v5'
 need(expected==record['afterValue']and record['dataOnlyUnissued']is True,'only declared template field changes')
graph=load(D/'module-edges.json');runtime=load(D/'runtime-dependencies.json');worker=load(D/'worker-dependencies.json')
for r in graph['modules']+runtime['files']+worker['files']:verify(r)
need(len(graph['modules'])==38 and len(graph['edges'])==151,'complete actual literal graph38/151')
need(len(runtime['files'])==28 and len(worker['files'])==20,'unchanged external runtime and worker-static roles')
for e in graph['edges']:
 if 'target'in e:need((Path(e['fromPath']).parent/e['specifier']).resolve()==Path(e['target']),'actual physical literal edge')
for r in load(D/'protocol-preservation.json')['unchangedRuntimeDonors']:verify(r)
for name in('run.mjs','worker.mjs','prepare-plan.mjs'):
 text=(D/name).read_text();need(text.index('await captureSourceFamilies(')<text.index('await import('),'full source auth before body '+name);need('await source.recheck()'in text,'final/failure auth '+name)
for name in('run-body.mjs','worker-body.mjs','prepare-plan-body.mjs'):
 text=(D/name).read_text();need('assertSourceFamilyAudit(sourceFamilyAudit,'in text and 'if(process.argv[1]'not in text,'private genuine capsule '+name)
family=(D/'source-families.mjs').read_text();need('verifiedSourceFamilies:5'in family and "../cost-pilot-timing-candidate-v4/index.json"in family,'four exact ancestors plus own')
need('new WeakSet()'in family and 'issued.has(capsule)'in family,'genuine own-source capsule remains')
guard=(D/'parent-guard.template.mjs').read_text();run=(D/'run-body.mjs').read_text();wb=(D/'worker-body.mjs').read_text();plan=(D/'prepare-plan-body.mjs').read_text();model=(D/'calibration-model.mjs').read_text()
need("&&v.phase==='timing'"in guard and "phase==='timing','V5 has no pilot launch action'"in guard,'timing-only phase gate')
need("if(root.phase==='pilot-candidate')"not in run and 'candidateNs('not in run and 'chooseMatchedN('not in run,'pilot launch loop absent')
need('actualIndexLimit(expectedState,v)'in guard and 'index.files.length<=16384'not in guard,'role-bound full index cap')
need('for(const row of index.files)'in guard and 'actualNames=[...names,\'index.json\',\'completion.json\']'in guard,'all actual members, exact membership')
need('sourceIndexSha256===options.sourceIndex.sha256&&warm.'not in run,'no new-source relabelled pilot identity')
need('calibrationResultModel(warm.data,warm.contract'in run and 'matchedPlan(warm.data.calibrations)'in run,'actual original calibrations/unchanged formula')
need('same(root.warmNPlan,admitted.refs.actualCalibrationReview)'in guard,'Root pins actual calibration review')
need('same(plan.calibrationSourceIndex,ORIGINAL_PILOT_SOURCE_INDEX)'in guard and 'same(plan.calibrationReview,admitted.refs.actualCalibrationReview)'in guard,'new plan original calibration roles')
need('calibrationSourceIndex:root.calibrationSourceIndex,rootAuthority:'in run,'private descriptor carries original source role')
need('same(v.calibrationSourceIndex,root.calibrationSourceIndex)'in wb and 'same(plan.calibrationReview,root.warmNPlan)'in wb,'worker compares original roles')
need('same(phase.calibrationSourceIndex,root.calibrationSourceIndex)'in guard and 'same(phase.calibrationSourceIndex,root.calibrationSourceIndex)'in wb,'Root phase binds role')
need("assertCompleteIndexCount(output.rows.size,INDEX_BOUNDS.timing);"in run,'full timing-publication cap, no omitted files')
need('calibrationSourceIndex:ORIGINAL_PILOT_SOURCE_INDEX,calibrationReview:admitted.refs.actualCalibrationReview,calibrationMatchedPlan:ORIGINAL_MATCHED_PLAN'in plan,'fresh genuine compact DATA')
need('zlib-cost-measurement-plan-v5'in plan and 'zlib-cost-timing-v5'in guard,'fresh namespaces')
need("for(const r of['preparedPlan','phaseAuthority','quietWindowAuthority','warmNPlan','warmNMatchedPlan','globalBudgetMs'])"not in model,'no borrowed phase carrier')
need('56894'in model and '17642'in model and 'legacyProof:16384'in model,'finite explicit bounds')
refs=load(D/'references.json');need(refs['originalPilotSourceIndex']==row(OLD/'index.json'),'exact original calibration source descriptor')
for key in('actualPilotRootObservation','actualPilotIndex','actualPilotResults','actualMatchedPlan'):verify(refs[key])
actual_index=load(refs['actualPilotIndex']['path']);need(len(actual_index['files'])==33066 and len({r['path']for r in actual_index['files']})==33066,'all actual pilot index rows retained')
actual=load(refs['actualPilotResults']['path']);need(actual['sourceIndexSha256']==refs['originalPilotSourceIndex']['sha256']and len(actual['calibrations'])==60,'actual calibration keeps b5 identity/60 rows')
need(33066>16384 and 892*37+62==33066 and 1536*37+62==56894 and 360*49+2==17642,'real cap counterexample and finite source bounds')
if refs['actualCalibrationReview']is not None:
 proof=refs['actualCalibrationReview'];verify(proof['index']);verify(proof['result']);verify(proof['contract']);p=load(proof['result']['path']);c=load(proof['contract']['path'])
 need(p['schemaVersion']==1 and p['state']=='INDEPENDENT_ZLIB_COST_PILOT_RESULTS_REVIEW_PASSED_V1'and p['verifiedPassed']is True,'actual independently sealed pilot DATA')
 need(p['sourceIndex']==refs['originalPilotSourceIndex']and p['sourceIndexSha256']==refs['originalPilotSourceIndex']['sha256'],'old proof source remains b5')
 need(p['actualIndex']==refs['actualPilotIndex']and p['actualResults']==refs['actualPilotResults']and p['matchedPlan']==refs['actualMatchedPlan'],'full original output descriptors')
 need(p['cases']==refs['cases']and c['requiredExactDescriptors']['cases']==refs['cases']and c['requiredExactDescriptors']['matchedPlan']==refs['actualMatchedPlan'],'real cases/matched contract')
 need(p['calibrations']==actual['calibrations'],'all original calibration records unchanged')
 need(p['components']==c['requiredComponents'],'actual component tuples bound')
for name in('future-authority.template.json','future-plan-authority.template.json'):
 v=load(D/name);need(v['sourceIndexSha256']is None and v['sourceIndependentReview']is None,'no source/action authority')
 need(v.get('actionAllowed',False)is False and v.get('dataPublicationAllowed',False)is False,'no phase grant')
 for field in('preparedPlan','phaseAuthority','quietWindowAuthority','warmNPlan','warmNMatchedPlan','globalBudgetMs','calibrationSourceIndex'):
  if field in v:need(v[field]is None,'NULL future '+field)
need(load(D/'future-plan-authority.template.json')['outputRoot']=='/private/tmp/starling-node-compat/zlib-cost-measurement-plan-v5','corrected template path')
for n in('zlib-cost-measurement-plan-v5','zlib-cost-timing-v5'):need(not(Path('/private/tmp/starling-node-compat')/n).exists(),'no actual new output')
asts=[]
for p in D.glob('*.py'):ast.parse(p.read_bytes());asts.append(p.name)
value=dict(schemaVersion=1,state='V5_TIMING_ONLY_SOURCE_DATA_CHECKS_PASSED',checks=checks,inputDescriptors=len(inputs['files']),derivedFiles=9,reversibleEdits=edit_count,exactCopies=copies,sourceModules=38,literalEdges=151,externalRuntimeDependencies=28,workerStaticDependencies=20,actualOriginalPilotIndexRows=33066,pilotMaxIndexRows=56894,timingMaxIndexRows=17642,pilotReviewBound=refs['actualCalibrationReview']is not None,pythonAst=asts,oldSourceAndActualRecordsUnchanged=True,sourceOnly=True,helperOrPreflightOrNodeWorkloadOrWorkerOrLoaderOrGuestOrMeasurementInvoked=False)
(D/'source-checks.json').write_text(json.dumps(value,indent=2)+'\n');print(json.dumps(value))
