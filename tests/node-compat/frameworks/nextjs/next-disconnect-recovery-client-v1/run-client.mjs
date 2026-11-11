// Host-only fixed nineteen-cycle recovery probe. No browser or guest shim.
import assert from 'node:assert/strict';
import {readFile,lstat,realpath,mkdir} from 'node:fs/promises';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {collectCall,publish,hash,errorData} from './http-call.mjs';
const here=dirname(fileURLToPath(import.meta.url)),suite='NEXT_DISCONNECT_RECOVERY_CLIENT_V1';
const json=value=>Buffer.from(JSON.stringify(value,null,2)+'\n');
async function refRead(ref){
 assert(ref&&Object.keys(ref).sort().join(',')==='bytes,path,sha256');assert.equal(resolve(ref.path),ref.path);assert.equal(await realpath(ref.path),ref.path);
 const a=await lstat(ref.path);assert(a.isFile()&&!a.isSymbolicLink()&&a.nlink===1&&a.size<=1048576);
 const data=await readFile(ref.path),b=await lstat(ref.path);for(const k of ['dev','ino','mode','nlink','size','mtimeMs','ctimeMs'])assert.equal(a[k],b[k]);
 assert.equal(data.length,ref.bytes);assert.equal(hash(data),ref.sha256);return data;
}
async function main(){
 assert.equal(process.version,'v22.14.0');assert.equal(process.argv.length,6);
 const [originValue,output,unusedTools,runId]=process.argv.slice(2),origin=new URL(originValue);
 assert.equal(origin.origin,originValue);assert.equal(origin.protocol,'http:');assert.equal(origin.hostname,'127.0.0.1');assert(origin.port&&origin.username===''&&origin.password==='');
 assert.equal(typeof unusedTools,'string');assert(unusedTools.length>0); // Reserved; never opened or imported.
 const plan=JSON.parse(await readFile(join(here,'plan.json'),'utf8'));assert.equal(plan.suite,suite);assert.equal(plan.warmupCycles,3);assert.equal(plan.measuredCycles,16);
 const arm=['wasmtime','cloud','stock'].find(name=>runId==='disconnect-recovery-'+name+'-first');assert(arm);
 const expected='/private/tmp/starling-node-compat/next-disconnect-recovery-'+arm+'-v1-'+runId+'/client';assert.equal(output,expected);assert.equal(resolve(output),output);
 assert.equal(await realpath(dirname(output)),dirname(output));
 assert.deepEqual(plan.limits,{httpTimeoutMs:20000,cleanupTimeoutMs:2000,bodyLimitBytes:4194304,chunkLimit:65536,metadataLimitBytes:262144,resultBytes:16777216,clientTimeoutMs:180000});
 assert.equal(plan.cycles.length,19);
 for(let i=0;i<19;i++){const suffix=String(i).padStart(3,'0');assert.deepEqual(plan.cycles[i],{index:i,phase:i<3?'warmup':'measured',label:(i<3?'warmup-':'measured-')+suffix,cookie:'alpha-'+suffix,probe:'probe-value-'+suffix});}
 assert.deepEqual(Object.keys(plan.sourceRequirements),['fixtureContract']);const contract=JSON.parse(await refRead(plan.sourceRequirements.fixtureContract));
 const fsExpected=contract.requests.find(x=>x.id==='fs-crypto-probe').json;
 assert.deepEqual(fsExpected,{marker:'NEXT_FS_CRYPTO',text:'nextjs-runtime-fixture\n',sha256:'6bb4bb9103d951dce4f9ff0ebaeee7e91d610226c5661630d59824f0d958b928'});
 await mkdir(output,{mode:0o700});await mkdir(join(output,'calls'),{mode:0o700});
 const result={schemaVersion:1,suite,controlOnly:true,fullOriginalContractExecuted:false,fullNextAccepted:false,origin:originValue,runId,
  sourceRequirements:plan.sourceRequirements,limits:plan.limits,warmupCycles:3,measuredCycles:16,plannedCalls:114,probeExecuted:false,collectionComplete:false,cleanupComplete:false,passed:false,
  cycles:[],calls:[],callRecords:[],collectionErrors:[],validationErrors:[],errors:[],unattemptedCalls:114,
  scope:{sameHostProcessSelectedByParent:true,sameStoreOrInstanceReuseProved:false,resourceRetirementProved:false,guestCancellationObserved:false,
   intentionalClose:'Local request.destroy after first actual body Buffer; final HTTP complete and guest propagation are independent observations',
   warmupMeaning:'Three fixed complete cycles before sixteen fixed measured cycles; no adaptation or resource/performance threshold'}};
 let stopped=false;const clientStarted=process.hrtime.bigint(),clientDeadline=clientStarted+BigInt(plan.limits.clientTimeoutMs)*1000000n;
 for(const cycle of plan.cycles){
  const specs=[{id:'stream-complete',method:'GET',path:'/stream'},
   {id:'stream-disconnect',method:'GET',path:'/stream',intentionalDisconnect:true},
   {id:'json-malformed',method:'POST',path:'/api/json',headers:{'content-type':'application/json'},body:'{bad'},
   {id:'context-set',method:'GET',path:'/api/context',headers:{cookie:'fixture_token='+cycle.cookie,'x-fixture-probe':cycle.probe}},
   {id:'context-empty',method:'GET',path:'/api/context'},
   {id:'fs-crypto',method:'GET',path:'/api/fs-crypto'}];
  const summary={...cycle,callIds:[],collectionComplete:false,passed:false};result.cycles.push(summary);
  for(const spec of specs){
   if(process.hrtime.bigint()>=clientDeadline){result.collectionErrors.push({stage:'declared-client-deadline',message:'Fixed180s client budget exhausted; suffix unattempted'});stopped=true;break;}
   const id=cycle.label+'-'+spec.id;let call;
   try{
    const remainingMs=Math.max(1,Number((clientDeadline-process.hrtime.bigint()+999999n)/1000000n));
    call=await collectCall({origin:originValue,spec:{...spec,id},bodyPath:join(output,'calls',id+'.body'),...plan.limits,httpTimeoutMs:Math.min(plan.limits.httpTimeoutMs,remainingMs)});
    call.caseId=spec.id;call.cycleIndex=cycle.index;call.phase=cycle.phase;call.validationErrors=[];
    const check=(ok,message)=>{if(ok!==true)call.validationErrors.push(message);};
    check(call.request.finishObserved,'request finish observed; no peer-acknowledgment claim');
    const body=call.body?await readFile(call.body.path):Buffer.alloc(0);if(call.body){assert.equal(body.length,call.body.bytes);assert.equal(hash(body),call.body.sha256);}
    check(call.response.statusCode===(spec.id==='json-malformed'?400:200),'expected response status');
    check(!Object.hasOwn(call.response.headers??{},'content-encoding'),'expected absent response Content-Encoding; no decoder used');
    if(spec.intentionalDisconnect){
     const intent=call.intentionalDisconnect,errors=[...call.request.errors,...call.response.errors,...call.connection.errors];
     check(intent.triggered&&intent.localDestroyInvoked&&intent.firstChunkBytes>0,'actual first-body close was invoked');
     check(errors.every(e=>e.sequence>intent.intentSequence&&['ECONNRESET','ERR_STREAM_PREMATURE_CLOSE','ERR_STREAM_DESTROYED','ERR_SOCKET_CLOSED'].includes(e.code)),'no pre-intent or unrelated transport errors');
     // A response already parsed at this local boundary is recorded, not called
     // a proved partial peer/guest cancellation or silently rewritten as one.
     call.intentionalDisconnect.httpIncompleteAtIntent=intent.completeAtIntent===false&&intent.endObservedAtIntent===false;
    }else{
     check(call.httpComplete,'normal request requires parsed complete HTTP entity and consumer end');
     if(spec.id==='stream-complete'){
      let text='',shell=-1,ready=-1;const decoder=new TextDecoder();
      for(let i=0;i<call.capture.chunks.length;i++){const c=call.capture.chunks[i],part=body.subarray(c.offset,c.offset+c.bytes);assert.equal(hash(part),c.sha256);text+=decoder.decode(part,{stream:true});if(shell<0&&text.includes('NEXT_STREAM_SHELL'))shell=i;if(ready<0&&text.includes('NEXT_STREAM_READY'))ready=i;}
      text+=decoder.decode();call.streaming={chunks:call.capture.chunks.length,shellChunk:shell,readyChunk:ready,shellPosition:text.indexOf('NEXT_STREAM_SHELL'),readyPosition:text.indexOf('NEXT_STREAM_READY'),incrementalDeliveryObserved:ready>shell&&shell>=0};
      check(call.streaming.shellPosition>=0&&call.streaming.readyPosition>call.streaming.shellPosition,'SHELL before READY markers');
      check(call.streaming.incrementalDeliveryObserved,'SHELL observed in an earlier client body event than READY');
     }else{
      let value;try{value=JSON.parse(new TextDecoder('utf8',{fatal:true}).decode(body));}catch(error){check(false,'complete UTF8 JSON expected');}
      const expectedValue=spec.id==='json-malformed'?{marker:'NEXT_JSON_BAD_INPUT'}:spec.id==='fs-crypto'?fsExpected:{marker:'NEXT_CONTEXT',cookie:spec.id==='context-set'?cycle.cookie:null,header:spec.id==='context-set'?cycle.probe:null};
      check(value!==null&&typeof value==='object'&&!Array.isArray(value)&&JSON.stringify(Object.keys(value).sort())===JSON.stringify(Object.keys(expectedValue).sort())&&Object.entries(expectedValue).every(([key,v])=>JSON.stringify(value[key])===JSON.stringify(v)),'exact expected JSON keys and values');
      if(spec.id.startsWith('context-')){check(call.response.headers?.['x-fixture-response']==='context-ok','context response header');const cookie=call.response.headers?.['set-cookie'];check(Array.isArray(cookie)&&cookie.some(x=>['fixture_reply=set','HttpOnly','SameSite=lax'].every(v=>x.includes(v))),'context response cookie');}
     }
    }
    call.passed=call.collectionComplete&&call.validationErrors.length===0;
    const bytes=json(call);assert(bytes.length<=1048576);const stored=await publish(join(output,'calls',id+'.json'),bytes);
    result.callRecords.push({id,result:stored.ref,publication:stored.evidence});result.calls.push(call);summary.callIds.push(id);
    result.probeExecuted||=call.request.created;result.unattemptedCalls--;
    if(!call.passed)result.validationErrors.push({id,errors:call.validationErrors});
    if(!call.collectionComplete){result.collectionErrors.push({id,errors:call.collectionErrors,reason:'Request/capture/cleanup collection not complete'});stopped=true;break;}
   }catch(error){result.collectionErrors.push({id,...errorData(error)});stopped=true;break;}
  }
  const calls=result.calls.filter(x=>x.cycleIndex===cycle.index);summary.collectionComplete=calls.length===6&&calls.every(x=>x.collectionComplete);summary.passed=summary.collectionComplete&&calls.every(x=>x.passed);
  if(stopped)break;
 }
 try{await refRead(plan.sourceRequirements.fixtureContract);}catch(error){result.collectionErrors.push({stage:'source-final',...errorData(error)});}
 result.collectionComplete=result.calls.length===114&&result.cycles.length===19&&result.cycles.every(x=>x.collectionComplete)&&result.collectionErrors.length===0;
 result.cleanupComplete=result.calls.length>0&&result.calls.every(x=>x.connection.cleanupCompleted);result.elapsedNs=(process.hrtime.bigint()-clientStarted).toString();
 result.passed=result.collectionComplete&&result.calls.every(x=>x.passed);result.errors=[...result.collectionErrors];
 const bytes=json(result);assert(bytes.length<=plan.limits.resultBytes);const stored=await publish(join(output,'result.json'),bytes);
 const receipt={schemaVersion:1,state:'NEXT_DISCONNECT_RECOVERY_CLIENT_PUBLICATION_V1',suite,probeExecuted:result.probeExecuted,collectionComplete:result.collectionComplete,cleanupComplete:result.cleanupComplete,passed:result.passed,
  controlOnly:true,fullOriginalContractExecuted:false,fullNextAccepted:false,result:stored.ref,resultPublication:stored.evidence,calls:result.callRecords};
 const publication=await publish(join(output,'publication.json'),json(receipt));
 process.stdout.write(JSON.stringify({suite,probeExecuted:result.probeExecuted,collectionComplete:result.collectionComplete,cleanupComplete:result.cleanupComplete,passed:result.passed,result:stored.ref,publication:publication.ref,errors:result.errors.length})+'\n');
 process.exitCode=result.passed?0:1;
}
main().catch(error=>{process.stdout.write(JSON.stringify({suite,passed:false,collectionComplete:false,publicationFailedOrPreflightRefused:true,error:errorData(error)})+'\n');process.exitCode=1;});
