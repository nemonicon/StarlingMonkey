// Private CLI TCB: stdlib + source authenticator only before custom body import.
import {resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {readSmallJson,captureSourceFamilies,primitiveDescriptor} from './source-families.mjs';
export const BOOTSTRAP_STAGES=Object.freeze(['cli-descriptor','descriptor-read','root-read','root-source-binding','source-authentication','body-import','body-entry','descriptor-model','root-model','namespace-relations','execution-environment','source-intake','node-identity','prepared-plan','phase-window','pre-output-recheck','job-output-create','job-started-record','reviewed-loader','owned-runtime-body','worker-final-recheck','wrapper-final-recheck']);
export function bootstrapFailureLine(stage,sourceAuthenticated,error){
 // Never inspect a caught object's properties, prototype, name, stack or then.
 // The stage is a fixed source label, not a unique-cause or guest observation.
 if(!BOOTSTRAP_STAGES.includes(stage)||typeof sourceAuthenticated!=='boolean')throw Error('finite diagnostic primitives');
 const line=JSON.stringify({schemaVersion:1,state:'CODEC_WORKER_BOOTSTRAP_OR_BODY_FAILED_UNACCEPTED_V1',stage,sourceAuthenticated,thrownType:typeof error,exceptionPropertiesRead:false,fullExceptionValueCaptured:false,uniqueFailureCauseProven:false,rawParentCollectorDurabilityRequired:true,runtimeAcceptanceClaim:false})+'\n';
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
  process.stdout.write(JSON.stringify({event:'cost-worker-complete',...result})+'\n');
 }catch(error){
  // The unchanged owned parent captures and fsyncs complete stderr + terminal
  // BEFORE rejecting. Invalid descriptors need no unauthenticated output path.
  const line=bootstrapFailureLine(stage,sourceAuthenticated,error);
  await new Promise(done=>process.stderr.write(line,()=>done()));process.exitCode=1;
 }
}
