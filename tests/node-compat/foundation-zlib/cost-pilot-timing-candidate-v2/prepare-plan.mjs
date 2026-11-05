// Future READ-ONLY prerequisite audit + compact DATA publication only.
import {join} from 'node:path';
import {descriptor,regular} from '../cost-jco-correctness-candidate-v2/authority.mjs';
import {DurableOutput} from '../cost-jco-correctness-candidate-v2/durable.mjs';
import {auditPrerequisites,CALIBRATION_DECISION} from './parent-guard.template.mjs';
import {need} from '../cost-pilot-timing-candidate-v1/planner.mjs';
import {same} from '../cost-pilot-timing-candidate-v1/proof-model.mjs';
export const PLAN_OUTPUT='/private/tmp/starling-node-compat/zlib-cost-measurement-plan-v2';
export async function preparePlan({sourceIndex,sourceIndependentReview,planAuthority}={}){
 need(sourceIndex&&sourceIndependentReview&&planAuthority,'NULL source/peer/plan authority refuses');const authorityRow=descriptor(planAuthority),v=JSON.parse(await regular(authorityRow));
 need(v.schemaVersion===1&&v.state==='ROOT_AUTHORIZED_READ_ONLY_CODEC_MEASUREMENT_PLAN_DATA_V1'&&v.dataPublicationAllowed===true&&v.sourceIndexSha256===sourceIndex.sha256&&v.outputRoot===PLAN_OUTPUT&&v.codecGuestPilotOrTimingAllowed===false,'exact Root read-only plan DATA authority');
 need(same(v.sourceIndependentReview,sourceIndependentReview),'exact Root-bound independent source review');
 const admitted=await auditPrerequisites({sourceIndex,sourceIndependentReview});await regular(authorityRow);
 const plan={schemaVersion:1,state:'PREPARED_COMPACT_CODEC_MEASUREMENT_PLAN_DATA_ONLY_V1',sourceIndexSha256:sourceIndex.sha256,
  calibrationDecisionSha256:CALIBRATION_DECISION,expected:admitted.expected,artifacts:admitted.artifacts,operationalAdmission:false,actionAuthority:false};
 need(Buffer.byteLength(JSON.stringify(plan,null,2)+'\n')<=128*1024,'compact90case/three artifact plan, no huge oracle/proof report');
 const output=await DurableOutput.create(PLAN_OUTPUT);
 try{const result=await output.write('prepared-plan.json',plan,{json:true});await admitted.recheck();await regular(authorityRow);await output.recheck();
  const index=await output.write('index.json',{schemaVersion:1,files:[...output.rows.values()]},{json:true}),completion=await output.write('completion.json',{schemaVersion:1,state:'READ_ONLY_COMPACT_PLAN_DATA_COMPLETE_NOT_ACTION_AUTHORITY',result,index,rootAuthority:authorityRow},{json:true});await output.recheck();return{result,index,completion};}
 finally{await output.close();}
}
