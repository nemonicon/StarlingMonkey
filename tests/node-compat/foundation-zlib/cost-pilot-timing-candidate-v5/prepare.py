"""Finite source derivation only. No helper/preflight/worker/loader/codec action."""
from pathlib import Path
import hashlib
import json

D=Path(__file__).resolve().parent
Z=D.parent
OLD=Z/'cost-pilot-timing-candidate-v4'
assert D==Path('/Users/dan/dev/StarlingMonkey/tests/node-compat/foundation-zlib/cost-pilot-timing-candidate-v5')and not(D/'index.json').exists()
def row(path):
 p=Path(path);b=p.read_bytes();assert p.is_file()and not p.is_symlink();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def write(name,value):
 p=D/name;p.parent.mkdir(parents=True,exist_ok=True)
 if isinstance(value,(dict,list)):value=json.dumps(value,indent=2)+'\n'
 p.write_text(value)
old_index=row(OLD/'index.json');assert old_index['sha256']=='b5b4c9e9279022f63dc72f20bf9a44c831ba277017d9dc72867eafd6a24f89d1'and old_index['bytes']==9952
for r in json.loads((OLD/'index.json').read_bytes())['files']:assert row(OLD/r['path'])==dict(r,path=str(OLD/r['path']))
proof=[]
def derive(name,edits):
 original=(OLD/name).read_text();text=original;records=[]
 for before,after in edits:
  count=text.count(before);assert count>0 and before!=after,(name,before[:70]);text=text.replace(before,after);records.append(dict(before=before,after=after,count=count))
 back=text
 for edit in reversed(records):assert back.count(edit['after'])==edit['count'];back=back.replace(edit['after'],edit['before'])
 assert back==original
 write(name,text);proof.append(dict(donor=row(OLD/name),afterimage=name,edits=records))
derive('source-families.mjs',[
 ("bytes:8574})\n]);","bytes:8574}),\n Object.freeze({path:join(HERE,'../cost-pilot-timing-candidate-v4/index.json'),sha256:'b5b4c9e9279022f63dc72f20bf9a44c831ba277017d9dc72867eafd6a24f89d1',bytes:9952})\n]);"),
 ('actual v4 own source index','actual v5 own timing source index'),('verifiedSourceFamilies:4','verifiedSourceFamilies:5')])
derive('run.mjs',[])
derive('prepare-plan.mjs',[('zlib-cost-measurement-plan-v4','zlib-cost-measurement-plan-v5')])
derive('worker.mjs',[])
derive('environment.mjs',[])
derive('parent-guard.template.mjs',[
 ("import {captureSourceFamilies} from './source-families.mjs';","import {captureSourceFamilies} from './source-families.mjs';\nimport {ORIGINAL_PILOT_SOURCE_INDEX,ORIGINAL_MATCHED_PLAN,actualIndexLimit,assertCompleteIndexCount,calibrationRoleModel,calibrationResultModel} from './calibration-model.mjs';"),
 ("export const outputRoot=phase=>'/private/tmp/starling-node-compat/zlib-cost-'+(phase==='timing'?'timing':'pilot')+'-v4';","export const outputRoot=phase=>{need(phase==='timing','V5 has no pilot launch action');return '/private/tmp/starling-node-compat/zlib-cost-timing-v5';};"),
 ("&&['pilot-candidate','timing'].includes(v.phase)","&&v.phase==='timing'"),
 (" need(v.calibrationDecisionSha256===CALIBRATION_DECISION,'Root selected fresh paired calibration source design');"," need(v.calibrationDecisionSha256===CALIBRATION_DECISION,'Root selected original paired calibration design');calibrationRoleModel(v);"),
 ("need(index.schemaVersion===1&&Array.isArray(index.files)&&index.files.length>0&&index.files.length<=16384,'bounded actual output index');","need(index.schemaVersion===1&&Array.isArray(index.files),'actual output index schema');assertCompleteIndexCount(index.files.length,actualIndexLimit(expectedState,v));"),
 (" const recheck=async()=>{await inheritedFamilies.recheck();", " const calibration=await contractedProof(refs.actualCalibrationReview,'INDEPENDENT_ZLIB_COST_PILOT_RESULTS_REVIEW_PASSED_V1');\n calibrationResultModel(calibration.data,calibration.contract,{components:Object.fromEntries(Object.entries(artifacts).map(([arm,a])=>[arm,a.component])),cases:refs.cases,calibrationDecisionSha256:CALIBRATION_DECISION});\n const recheck=async()=>{await calibration.recheck();await inheritedFamilies.recheck();"),
 ('return Object.freeze({frame,own,refs,expected,artifacts,recheck});','return Object.freeze({frame,own,refs,expected,artifacts,calibration,recheck});'),
 (" const planRow=descriptor(root.preparedPlan)"," need(same(root.warmNPlan,admitted.refs.actualCalibrationReview),'Root binds the exact original independently reviewed b5 calibration');\n const planRow=descriptor(root.preparedPlan)"),
 (" need(same(plan.expected,admitted.expected)&&same(plan.artifacts,admitted.artifacts),'entire compact plan matches parent full proof admission');"," need(same(plan.expected,admitted.expected)&&same(plan.artifacts,admitted.artifacts),'entire compact plan matches parent full proof admission');\n need(same(plan.calibrationSourceIndex,ORIGINAL_PILOT_SOURCE_INDEX)&&same(plan.calibrationReview,admitted.refs.actualCalibrationReview)&&same(plan.calibrationMatchedPlan,ORIGINAL_MATCHED_PLAN),'New genuine plan keeps original calibration DATA roles');"),
 ("&&same(phase.preparedPlan,planRow)","&&same(phase.calibrationSourceIndex,root.calibrationSourceIndex)&&same(phase.preparedPlan,planRow)")])
derive('prepare-plan-body.mjs',[
 ("import {same} from '../cost-pilot-timing-candidate-v1/proof-model.mjs';","import {same} from '../cost-pilot-timing-candidate-v1/proof-model.mjs';\nimport {ORIGINAL_PILOT_SOURCE_INDEX,ORIGINAL_MATCHED_PLAN} from './calibration-model.mjs';"),
 ('zlib-cost-measurement-plan-v4','zlib-cost-measurement-plan-v5'),
 ('calibrationDecisionSha256:CALIBRATION_DECISION,expected:admitted.expected,artifacts:admitted.artifacts,','calibrationDecisionSha256:CALIBRATION_DECISION,calibrationSourceIndex:ORIGINAL_PILOT_SOURCE_INDEX,calibrationReview:admitted.refs.actualCalibrationReview,calibrationMatchedPlan:ORIGINAL_MATCHED_PLAN,expected:admitted.expected,artifacts:admitted.artifacts,')])
old_run=(OLD/'run-body.mjs').read_text();start=old_run.index("  if(root.phase==='pilot-candidate'){");end=old_run.index('   for(const spec of timingSchedule()){',start)
old_pilot_prefix=old_run[start:end]
derive('run-body.mjs',[
 ("import {need,COMPARISONS,candidateNs,chooseMatchedN,matchedPlan,timingSchedule} from '../cost-pilot-timing-candidate-v1/planner.mjs';","import {need,matchedPlan,timingSchedule} from '../cost-pilot-timing-candidate-v1/planner.mjs';\nimport {ORIGINAL_PILOT_SOURCE_INDEX,INDEX_BOUNDS,calibrationResultModel,assertCompleteIndexCount} from './calibration-model.mjs';"),
 ("  need(warm.data.sourceIndexSha256===options.sourceIndex.sha256&&warm.data.calibrationDecisionSha256===CALIBRATION_DECISION&&warm.data.allMatchedNReviewed===true&&warm.data.allOwnedWorkersRawZeroClean===true&&warm.data.pilotOnly===true&&warm.data.timingAllowed===false,'separate actual pilot review with complete60case calibration');","  calibrationResultModel(warm.data,warm.contract,{components:Object.fromEntries(Object.entries(admitted.artifacts).map(([arm,a])=>[arm,a.component])),cases:admitted.refs.cases,calibrationDecisionSha256:CALIBRATION_DECISION});\n  need(same(root.calibrationSourceIndex,ORIGINAL_PILOT_SOURCE_INDEX),'Original pilot source is distinct from new timing source');"),
 ('rootAuthority:admitted.rootAction,sourceIndependentReviewIndex:','calibrationSourceIndex:root.calibrationSourceIndex,rootAuthority:admitted.rootAction,sourceIndependentReviewIndex:'),
 (old_pilot_prefix,'  {\n'),
 ('phase:root.phase,sourceIndexSha256:options.sourceIndex.sha256,calibrationDecisionSha256:','phase:root.phase,sourceIndexSha256:options.sourceIndex.sha256,calibrationSourceIndex:ORIGINAL_PILOT_SOURCE_INDEX,actualCalibrationReview:root.warmNPlan,actualMatchedPlan:root.warmNMatchedPlan,calibrationDecisionSha256:'),
 ("  const index=await write('index.json'","  assertCompleteIndexCount(output.rows.size,INDEX_BOUNDS.timing);\n  const index=await write('index.json'")])
derive('worker-body.mjs',[
 ("same(v.preparedPlan,root.preparedPlan)&&same(v.warmNPlan,root.warmNMatchedPlan)","same(v.preparedPlan,root.preparedPlan)&&same(v.calibrationSourceIndex,root.calibrationSourceIndex)&&same(v.warmNPlan,root.warmNMatchedPlan)"),
 ("need(plan.sourceIndexSha256===ownIx.sha256&&plan.state==='PREPARED_COMPACT_CODEC_MEASUREMENT_PLAN_DATA_ONLY_V1','actual parent-prepared compact DATA');","need(plan.sourceIndexSha256===ownIx.sha256&&plan.state==='PREPARED_COMPACT_CODEC_MEASUREMENT_PLAN_DATA_ONLY_V1','actual parent-prepared compact DATA');\n need(same(plan.calibrationSourceIndex,root.calibrationSourceIndex)&&same(plan.calibrationReview,root.warmNPlan)&&same(plan.calibrationMatchedPlan,root.warmNMatchedPlan),'Original calibration roles in new timing plan');"),
 ("&&same(phase.preparedPlan,planRow)","&&same(phase.calibrationSourceIndex,root.calibrationSourceIndex)&&same(phase.preparedPlan,planRow)")])
refs=json.loads((OLD/'references.json').read_bytes());refs['originalPilotSourceIndex']=old_index
refs['actualPilotRootObservation']=row(Z/'cost-pilot-v4-root-results.json')
actual=json.loads((Z/'cost-pilot-v4-root-results.json').read_bytes());assert actual['sourceIndexSha256']==old_index['sha256']and actual['indexedFilesRehashed']==33066
refs['actualPilotIndex']=actual['actualIndex'];refs['actualPilotResults']=actual['actualResults'];refs['actualMatchedPlan']=actual['matchedNPlan']
data=D/'actual-pilot-review.DATA.json'
refs['actualCalibrationReview']=json.loads(data.read_bytes())if data.exists()else None
write('references.json',refs)
write('source-derivations.json',dict(schemaVersion=1,donorIndex=old_index,files=proof,oldActualCalibrationUnchanged=True,oldCalibrationSourceNotRelabelled=True,newScope='read-only-plan-and-timing-only'))
future=json.loads((OLD/'future-authority.template.json').read_bytes());future['state']='ROOT_REVIEWED_ZLIB_COST_PILOT_TIMING_PHASE_V1';future['calibrationSourceIndex']=None
write('future-authority.template.json',future)
write('future-plan-authority.template.json',json.loads((OLD/'future-plan-authority.template.json').read_bytes()))
write('future-source-review-contract.json',json.loads((OLD/'future-source-review-contract.json').read_bytes()))
write('preparation-history.json',dict(schemaVersion=1,oldSourceAndActualRecordsUnchanged=True,oldDefects=['Actual33066 pilot output rows exceed the old contractedProof cap16384.','Old timing run body incorrectly demanded calibration proof sourceIndexSha256 equal the new own source SHA.'],sourceOnly=True,helperOrPreflightOrWorkerOrLoaderOrGuestOrMeasurementInvoked=False))
print(json.dumps(dict(derivedFiles=len(proof),edits=sum(len(p['edits'])for p in proof),pilotReviewDataBound=refs['actualCalibrationReview']is not None,sourceOnly=True)))
