"""Exclusive source preparation only. No helper/preflight/worker/loader or workload."""
from pathlib import Path
import hashlib,json

D=Path(__file__).resolve().parent;Z=D.parent;OLD=Z/'cost-pilot-timing-candidate-v3'
def row(p):
 p=Path(p);b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def save(name,v):
 p=D/name;p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x')as f:f.write(v if isinstance(v,str)else json.dumps(v,indent=2)+'\n')
derivations=[]
def derive(name,edits):
 p=OLD/name;text=p.read_text();proof=[]
 for before,after in edits:
  assert text.count(before)==1,(name,before)
  offset=text.index(before);text=text[:offset]+after+text[offset+len(before):]
  proof.append(dict(before=before,after=after,offsetAtEdit=offset))
 save(name,text);derivations.append(dict(origin=row(p),afterimage=name,edits=proof,afterSha256=row(D/name)['sha256']))

derive('source-families.mjs',[
 (" Object.freeze({path:join(HERE,'../cost-pilot-timing-candidate-v2/index.json'),sha256:'1a294044a4f2414d35fdd817dae95598c2e079aa64a9044737f4791aefe630a2',bytes:4460})",
  " Object.freeze({path:join(HERE,'../cost-pilot-timing-candidate-v2/index.json'),sha256:'1a294044a4f2414d35fdd817dae95598c2e079aa64a9044737f4791aefe630a2',bytes:4460}),\n Object.freeze({path:join(HERE,'../cost-pilot-timing-candidate-v3/index.json'),sha256:'c2ce5f08134d0cd05b9d3f10fe5bf1b49f124b1d32c49bff977d7ddb7ab064e9',bytes:8574})"),
 ("'only actual v3 own source index'","'only actual v4 own source index'"),
 ("const runtimeRow=families[2].rows.find(","const runtimeRow=families.at(-1).rows.find("),
 ("verifiedSourceFamilies:3","verifiedSourceFamilies:4")])
for name in ['run.mjs']:
 derive(name,[])
derive('parent-guard.template.mjs',[("+'-v3';","+'-v4';")])
derive('run-body.mjs',[])
for name in ['prepare-plan.mjs','prepare-plan-body.mjs']:
 derive(name,[("/zlib-cost-measurement-plan-v3'","/zlib-cost-measurement-plan-v4'")])
derive('worker-body.mjs',[
 ("import {assertSourceFamilyAudit} from './source-families.mjs';","import {assertSourceFamilyAudit} from './source-families.mjs';\nimport {measurementEnvironmentModel} from './environment.mjs';"),
 ("export async function runWorker(input,sourceFamilyAudit){","export async function runWorker(input,sourceFamilyAudit,markStage=()=>{}){\n markStage('descriptor-model');"),
 (" const rootRow=descriptor(v.rootAuthority)"," markStage('root-model');\n const rootRow=descriptor(v.rootAuthority)"),
 (" need(v.parentOutputRoot===root.outputRoot", " markStage('namespace-relations');\n need(v.parentOutputRoot===root.outputRoot"),
 (" need(process.version==='v22.14.0'&&process.execArgv.length===0&&same(Object.fromEntries(Object.entries(process.env).sort()),Object.fromEntries(Object.entries(MEASUREMENT_ENV).sort())),'exact pinned plain Node/environment, no inherited overrides');",
  " markStage('execution-environment');\n const observedEnvironment=Object.freeze({...process.env}),platformFacts=Object.freeze({platform:process.platform,uid:process.getuid?.()??null});\n need(process.version==='v22.14.0'&&process.execArgv.length===0&&measurementEnvironmentModel(observedEnvironment,platformFacts),'pinned plain Node and finite platform environment');"),
 (" const ownIx=descriptor(v.sourceIndex)"," markStage('source-intake');\n const ownIx=descriptor(v.sourceIndex)"),
 (" const refsRow=rows.find("," markStage('node-identity');\n const refsRow=rows.find("),
 (" const planRow=descriptor(v.preparedPlan)"," markStage('prepared-plan');\n const planRow=descriptor(v.preparedPlan)"),
 (" const phase=JSON.parse("," markStage('phase-window');\n const phase=JSON.parse("),
 (" const recheck=async()=>{await sourceFamilyAudit.recheck();", " const recheck=async()=>{need(measurementEnvironmentModel({...process.env},platformFacts)&&same({...process.env},observedEnvironment),'observed worker environment unchanged');await sourceFamilyAudit.recheck();"),
 (" await recheck();const output=await DurableOutput.create(v.outputRoot);", " markStage('pre-output-recheck');\n await recheck();markStage('job-output-create');const output=await DurableOutput.create(v.outputRoot);"),
 ("  await output.write('started.json',{schemaVersion:1,jobId:v.jobId,phase:v.phase,sourceIndex:ownIx,rootAuthority:rootRow,expected:v.expected,artifact:v.artifact,partial:true},{json:true});",
  "  markStage('job-started-record');\n  await output.write('started.json',{schemaVersion:1,jobId:v.jobId,phase:v.phase,sourceIndex:ownIx,rootAuthority:rootRow,expected:v.expected,artifact:v.artifact,observedEnvironment,platformFacts,environmentObservationScope:'actual validated runtime map after platform initialization; requested spawn map remains separate',partial:true},{json:true});"),
 ("  resource('after-source-authentication-before-loader');", "  markStage('reviewed-loader');\n  resource('after-source-authentication-before-loader');"),
 ("  const row=await injectedWorker(","  markStage('owned-runtime-body');\n  const row=await injectedWorker("),
 ("  await session.recheck();await recheck();await output.recheck();", "  markStage('worker-final-recheck');\n  await session.recheck();await recheck();await output.recheck();")])

save('environment.mjs',"""// Pure worker environment policy. No mutation, process or provider action.
import {MEASUREMENT_ENV} from '../cost-pilot-timing-candidate-v1/lifecycle-policy.mjs';
import {same} from '../cost-pilot-timing-candidate-v1/proof-model.mjs';
export function measurementEnvironmentModel(actual,{platform,uid}={}){
 if(!actual||typeof actual!=='object'||Array.isArray(actual)||Object.getPrototypeOf(actual)!==Object.prototype)throw Error('ordinary explicit environment map');
 const descriptors=Object.getOwnPropertyDescriptors(actual);
 if(Reflect.ownKeys(actual).some(k=>typeof k!=='string'||!Object.hasOwn(descriptors[k],'value')||typeof descriptors[k].value!=='string'))throw Error('environment string data fields only');
 const extras=Object.keys(actual).filter(k=>!Object.hasOwn(MEASUREMENT_ENV,k));
 if(extras.length===0&&same(actual,MEASUREMENT_ENV))return true;
 if(platform!=='darwin'||!Number.isInteger(uid)||uid<0||uid>0xffffffff||extras.length!==1||extras[0]!=='__CF_USER_TEXT_ENCODING')throw Error('unexpected environment key/platform');
 const permitted={...MEASUREMENT_ENV,__CF_USER_TEXT_ENCODING:'0x'+uid.toString(16).toUpperCase()+':0x0:0x0'};
 if(!same(actual,permitted))throw Error('unexpected environment value');
 return true;
}
""")

save('worker.mjs',"""// Private CLI TCB: stdlib + source authenticator only before custom body import.
import {resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {readSmallJson,captureSourceFamilies,primitiveDescriptor} from './source-families.mjs';
export const BOOTSTRAP_STAGES=Object.freeze(['cli-descriptor','descriptor-read','root-read','root-source-binding','source-authentication','body-import','body-entry','descriptor-model','root-model','namespace-relations','execution-environment','source-intake','node-identity','prepared-plan','phase-window','pre-output-recheck','job-output-create','job-started-record','reviewed-loader','owned-runtime-body','worker-final-recheck','wrapper-final-recheck']);
export function bootstrapFailureLine(stage,sourceAuthenticated,error){
 // Never inspect a caught object's properties, prototype, name, stack or then.
 // The stage is a fixed source label, not a unique-cause or guest observation.
 if(!BOOTSTRAP_STAGES.includes(stage)||typeof sourceAuthenticated!=='boolean')throw Error('finite diagnostic primitives');
 const line=JSON.stringify({schemaVersion:1,state:'CODEC_WORKER_BOOTSTRAP_OR_BODY_FAILED_UNACCEPTED_V1',stage,sourceAuthenticated,thrownType:typeof error,exceptionPropertiesRead:false,fullExceptionValueCaptured:false,uniqueFailureCauseProven:false,rawParentCollectorDurabilityRequired:true,runtimeAcceptanceClaim:false})+'\\n';
 if(Buffer.byteLength(line)>2048)throw Error('bounded source diagnostic');return line;
}
export async function runWorker(input,markStage=()=>{}){
 markStage('descriptor-read');const row=primitiveDescriptor(input),value=await readSmallJson(row);
 markStage('root-read');const root=await readSmallJson(value.rootAuthority);
 markStage('root-source-binding');if(value.sourceIndex?.sha256!==root.sourceIndexSha256||value.sourceIndexSha256!==root.sourceIndexSha256)throw Error('child Root/source mismatch');
 markStage('source-authentication');const source=await captureSourceFamilies(value.sourceIndex);
 let bodyFailed=false;
 try{markStage('body-import');const body=await import('./worker-body.mjs');markStage('body-entry');return await body.runWorker(row,source,markStage);}
 catch(error){bodyFailed=true;throw error;}
 finally{try{await source.recheck();}catch(error){markStage('wrapper-final-recheck');throw error;}if(!bodyFailed)markStage('wrapper-final-recheck');}
}
if(process.argv[1]&&resolve(process.argv[1])===fileURLToPath(import.meta.url)){
 let stage='cli-descriptor',sourceAuthenticated=false;
 const markStage=next=>{if(!BOOTSTRAP_STAGES.includes(next))throw Error('finite stage label');stage=next;if(next==='body-import')sourceAuthenticated=true;};
 try{
  if(process.argv.length!==3)throw Error('one private parent descriptor');
  const result=await runWorker(JSON.parse(process.argv[2]),markStage);
  process.stdout.write(JSON.stringify({event:'cost-worker-complete',...result})+'\\n');
 }catch(error){
  // The unchanged owned parent captures and fsyncs complete stderr + terminal
  // BEFORE rejecting. Invalid descriptors need no unauthenticated output path.
  const line=bootstrapFailureLine(stage,sourceAuthenticated,error);
  await new Promise(done=>process.stderr.write(line,()=>done()));process.exitCode=1;
 }
}
""")
derivations.append(dict(origin=row(OLD/'worker.mjs'),afterimage='worker.mjs',
 edits=[dict(before=(OLD/'worker.mjs').read_text(),after=(D/'worker.mjs').read_text(),offsetAtEdit=0,
             scope='Explicit whole small CLI bootstrap replacement; source-authentication mechanism and parent process API unchanged')],
 afterSha256=row(D/'worker.mjs')['sha256']))

references=json.loads((OLD/'references.json').read_text())
references.update(state='FINITE_DARWIN_ENVIRONMENT_AND_BOOTSTRAP_DIAGNOSTIC_SUCCESSOR_REFERENCES_V4',
 failedV3SourceIndex=row(OLD/'index.json'),failedV3CheckpointIndex=row(Z/'cost-pilot-v3-failure-root-checkpoint-v1/index.json'),
 failedV3ReviewIndex=row(Z/'independent-cost-pilot-v3-failure-review-v1/index.json'),
 failedV3ReviewResult=row(Z/'independent-cost-pilot-v3-failure-review-v1/results.json'),
 failureCorrectionContract=row(Z/'independent-cost-pilot-v3-failure-review-v1/required-correction-contract.json'),
 rootDiagnosisIndex=row(Z/'cost-pilot-v3-worker-import-diagnosis-v1/index.json'),originalExactWorkerExceptionCaptured=False,
 originalFailedPhaseOrPlanReused=False,newSourceIndependentReview=None,newRootAction=None,newPreparedPlan=None,newQuietWindow=None)
save('references.json',references)
for name in ['future-authority.template.json','future-plan-authority.template.json']:
 value=json.loads((OLD/name).read_text())
 if name=='future-plan-authority.template.json':value['outputRoot']='/private/tmp/starling-node-compat/zlib-cost-measurement-plan-v4'
 save(name,value)
save('source-derivations.json',dict(schemaVersion=1,fromV3=row(OLD/'index.json'),files=derivations,
 newWorkerBootstrap='worker.mjs',newPureEnvironmentPolicy='environment.mjs',protocolCapsProvidersGuestNativeLoaderCollectorOwnedLifecycleChanged=False))
save('preparation-status.json',dict(schemaVersion=1,state='UNSEALED_V4_SOURCE_DRAFT',sourceOnly=True,sourceIndependentReview=None,
 rootAction=None,preparedPlan=None,phaseAuthority=None,warmNPlan=None,quietWindowAuthority=None,globalBudgetMs=None,
 operationalAdmission=False,timingAllowed=False,workerOrLoaderOrCodecOrRuntimeActionsInvoked=False))
print(json.dumps(dict(sourceDraft=str(D),derivedFiles=len(derivations),newFiles=['worker.mjs','environment.mjs'],actionsInvoked=False)))
