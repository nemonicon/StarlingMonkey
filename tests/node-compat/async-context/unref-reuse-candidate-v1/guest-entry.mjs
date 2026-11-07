// Raw isolated ordinary-call unref control. INIT creates no ALS or timer.
import {bootstrap} from 'starling:node-startup';
import {runFreshRequest,runNeutralServer} from 'starling:node-http';
import {AsyncLocalStorage as UnrefAsyncLocalStorage} from 'node:async_hooks';
import {setTimeout as unrefTimeout,clearTimeout as unrefClearTimeout} from 'node:timers';
import * as types from 'wasi:http/types@0.2.10';
// Standard WASI HTTP resource ownership -> ordinary Web Request/Response.
// `types` is the actual wasi:http/types@0.2.10 namespace in guest-entry.mjs.
const drop = value => { if (value) value[Symbol.dispose](); };
function text(bytes) {
  let out = '';
  for (const byte of bytes) out += String.fromCharCode(byte);
  return out;
}
function bytes(value) {
  const result = new Uint8Array(value.length);
  for (let i = 0; i < value.length; i++) {
    const code = value.charCodeAt(i);
    if (code > 255) throw new TypeError('HTTP header values must be ByteStrings');
    result[i] = code;
  }
  return result;
}
// js-component-bindgen throws ComponentError with an own DATA payload.
// Only these explicit WIT stream-error records are interpreted. Unknown throws
// (including falsy values) keep their original identity; no message coercion.
function ownData(value,key) {
  if(value===null || (typeof value!=='object' && typeof value!=='function'))return undefined;
  const descriptor=Object.getOwnPropertyDescriptor(value,key);
  return descriptor && Object.prototype.hasOwnProperty.call(descriptor,'value')?descriptor.value:undefined;
}
function streamError(value) {
  const payload=ownData(value,'payload');
  const variant=payload===undefined?value:payload;
  const tag=ownData(variant,'tag');
  if(tag==='closed')return {tag};
  if(tag==='last-operation-failed') {
    const resource=ownData(variant,'val');
    if(resource!==null && (typeof resource==='object' || typeof resource==='function'))return {tag,val:resource};
  }
  return undefined;
}
function diagnosticMethod(resource,name) {
  for(let object=resource,depth=0;object!==null && depth<4;object=Object.getPrototypeOf(object),depth++) {
    const descriptor=Object.getOwnPropertyDescriptor(object,name);
    if(descriptor) {
      if(Object.prototype.hasOwnProperty.call(descriptor,'value') && typeof descriptor.value==='function')return descriptor.value;
      throw new TypeError('WASI diagnostic method must be a DATA function');
    }
  }
  throw new TypeError('WASI diagnostic method missing');
}
function streamFailure(value) {
  const variant=streamError(value);
  if(variant?.tag==='last-operation-failed') {
    const resource=variant.val;
    let message;
    try {
      message=Reflect.apply(diagnosticMethod(resource,'toDebugString'),resource,[]);
      if(typeof message!=='string')throw new TypeError('WASI diagnostic must return a synchronous string');
    } finally {drop(resource);}
    const error=new Error(message);
    Object.defineProperty(error,'cause',{value,configurable:true,writable:true});
    return error;
  }
  return value;
}

function createWasiHttpHandler(webHandler, types, runFreshRequest) {
  if (typeof runFreshRequest !== "function") throw new TypeError("Native request entry is required");
  const {Fields, IncomingBody, OutgoingBody, OutgoingResponse, ResponseOutparam} = types;
  async function handleResources(incoming, outparam) {
      let inputBody, inputStream, outgoingResponse, outputBody, outputStream, responseReader;
      let incomingEnded = false, responseSet = false, outputFinished = false;
      function releaseInput() {
        const stream = inputStream; inputStream = undefined;
        drop(stream);
        const body = inputBody; inputBody = undefined;
        if (body) {
          if (incomingEnded) drop(IncomingBody.finish(body));
          else drop(body);
        }
      }
      try {
        const fieldResource = incoming.headers();
        const headers = new Headers();
        try { for (const [name, value] of fieldResource.entries()) headers.append(name, text(value)); }
        finally { drop(fieldResource); }
        const scheme = incoming.scheme();
        const protocol = scheme?.tag === 'other' ? scheme.val : scheme?.tag ?? 'http';
        const authority = incoming.authority() ?? headers.get('host') ?? 'localhost';
        const methodValue = incoming.method();
        const method = methodValue.tag === 'other' ? methodValue.val : methodValue.tag.toUpperCase();
        const url = protocol + '://' + authority + (incoming.pathWithQuery() ?? '/');
        inputBody = incoming.consume();
        let body;
        if (!['GET', 'HEAD'].includes(method)) {
          inputStream = inputBody.stream();
          body = new ReadableStream({
            pull(controller) {
              try {
                const chunk = inputStream.blockingRead(64n * 1024n);
                if (chunk.length) controller.enqueue(chunk);
              } catch (error) {
                if (streamError(error)?.tag === 'closed') {
                  incomingEnded = true;
                  releaseInput();
                  controller.close();
                } else {
                  releaseInput();
                  controller.error(streamFailure(error));
                }
              }
            },
            cancel() { releaseInput(); },
          });
        }
        const request = new Request(url, {method, headers, ...(body ? {body, duplex: 'half'} : {})});
        const response = await webHandler(request);
        const fields = [];
        for (const [name, value] of response.headers) if (name !== 'set-cookie') fields.push([name, bytes(value)]);
        const cookies = response.headers.getSetCookie?.() ?? (response.headers.get('set-cookie') ? [response.headers.get('set-cookie')] : []);
        for (const value of cookies) fields.push(['set-cookie', bytes(value)]);
        outgoingResponse = new OutgoingResponse(Fields.fromList(fields));
        outgoingResponse.setStatusCode(response.status);
        outputBody = outgoingResponse.body();
        const outgoing = outgoingResponse; outgoingResponse = undefined;
        responseSet = true;
        ResponseOutparam.set(outparam, {tag: 'ok', val: outgoing});
        outputStream = outputBody.write();
        if (response.body) {
          responseReader = response.body.getReader();
          for (;;) {
            const part = await responseReader.read();
            if (part.done) break;
            for (let offset = 0; offset < part.value.byteLength; offset += 4096) {
              outputStream.blockingWriteAndFlush(part.value.subarray(offset, offset + 4096));
            }
          }
        }
        const stream = outputStream; outputStream = undefined;
        drop(stream);
        outputFinished = true;
        OutgoingBody.finish(outputBody, undefined);
      } catch (error) {
        if (responseReader) try { await responseReader.cancel(error); } catch {}
        throw streamFailure(error);
      } finally {
        releaseInput();
        drop(outputStream);
        if (outputBody && !outputFinished) drop(outputBody);
        drop(outgoingResponse);
        if (!responseSet) drop(outparam);
        drop(incoming);
      }
  }
  return {
    handle(incoming, outparam) {
      let entered=false;
      try {
        return runFreshRequest((...args)=>{
          entered=true;
          return handleResources(...args);
        },undefined,incoming,outparam);
      } catch(error) {
        if(!entered)disposeBeforeEntry(incoming,outparam);
        throw error;
      }
    },
  };
}

// The caller still owns incoming/outparam until native callback entry. Always
// attempt both drops, preserving the original pre-entry error even if cleanup
// itself refuses. Cleanup failure is diagnostic and cannot turn into success.
function disposeBeforeEntry(incoming,outparam) {
  let failures=0;
  for(const value of [incoming,outparam])try{drop(value);}catch{failures++;}
  if(failures)try{console.error('NEXT_COMPONENT_PRE_ENTRY_DISPOSAL_FAILURE',failures);}catch{}
}

// Pure orchestration, inlined unchanged into each raw guest entry.
function createNeutralReadyHandler({runNeutralServer,prepareServer,disposeBeforeEntry}) {
  let readiness;
  return Object.freeze({
    handle(incoming,outparam) {
      let enteredNeutral=false;
      try {
        return runNeutralServer(async () => {
          enteredNeutral=true;
          let handler;
          try {
            // Both promise allocation and all preparation happen neutrally.
            // One sticky promise per component instance: concurrent first
            // requests share success or the original rejection, never retry.
            readiness ??= Promise.resolve().then(prepareServer);
            handler=await readiness;
            if(!handler||typeof handler.handle!=='function')
              throw new TypeError('Preparation must return the real WASI handler');
          } catch(error) {
            disposeBeforeEntry(incoming,outparam);
            throw error;
          }
          // The adapter owns both resources from here. It enters native fresh
          // request context BEFORE constructing headers, body or Web Request.
          return handler.handle(incoming,outparam);
        },undefined);
      } catch(error) {
        if(!enteredNeutral)disposeBeforeEntry(incoming,outparam);
        throw error;
      }
    },
  });
}


// Ordinary-only shared factory. Import creates no ALS, handles, timers or work.
const UNREF_DELAYS=Object.freeze({oldCallbackMs:100,cancelCandidateMs:1000,bReferenceFenceMs:1100,cReferenceFenceMs:100});
const phases=['A','B','C'];
const dataError=e=>({type:e===null?'null':typeof e,name:typeof e?.name==='string'?e.name:null,message:typeof e?.message==='string'?e.message:String(e),code:typeof e?.code==='string'?e.code:null});
const clone=x=>JSON.parse(JSON.stringify(x));
const mark=label=>Object.freeze({label});
function label(value){const d=value!==null&&typeof value==='object'?Object.getOwnPropertyDescriptor(value,'label'):null;return d&&Object.hasOwn(d,'value')&&typeof d.value==='string'?d.value:value===undefined?'undefined':'other';}
function createUnrefReuseState(backend){
 const first=new backend.AsyncLocalStorage(),second=new backend.AsyncLocalStorage(),stores=[first,second];
 for(let i=0;i<stores.length;i++)stores[i].run(mark('enable-'+i),()=>{});
 const boundaries=backend.boundaries(stores);
 const state={ordinal:0,firstHostCase:null,origin:null,phase:'created',failed:false,closed:false,
  oldCallbacks:0,candidateCallbacks:0,bRefCallbacks:0,cRefCallbacks:0,earlyOld:false,callbackChecks:[],observations:[],handles:[],peakPlannedHandles:0,clearAttempts:0,clearErrors:[]};
 let activeChecks=null,oldHandle,candidateHandle,inFlight=false;
 const check=(id,value,target=activeChecks)=>{const row={id,passed:value===true};target.push(row);if(!row.passed)state.failed=true;};
 const observe=(id,wantFirst,wantSecond,target=activeChecks)=>{
  const a=first.getStore(),b=second.getStore();
  state.observations.push({sequence:state.observations.length+1,id,phase:state.phase,ordinal:state.ordinal,firstLabel:label(a),secondLabel:label(b),firstIdentity:a===wantFirst,secondIdentity:b===wantSecond});
  check(id+':first-identity',a===wantFirst,target);check(id+':second-identity',b===wantSecond,target);
 };
 function pending(){return state.handles.filter(r=>r.pending).length;}
 function schedule(kind,callback,delay,unref){
  if(pending()>=8)throw new Error('UNREF_REUSE_EIGHT_PLANNED_HANDLES_LIMIT');
  const row={kind,pending:true,handle:null};
  const wrapped=()=>{
   row.pending=false;
   // Never throw into the event loop. Preserve all callback failures in DATA.
   try{callback();}catch(error){state.failed=true;state.observations.push({sequence:state.observations.length+1,id:kind+':callback-threw',phase:state.phase,ordinal:state.ordinal,error:dataError(error)});}
  };
  row.handle=backend.setTimeout(wrapped,delay);state.handles.push(row);state.peakPlannedHandles=Math.max(state.peakPlannedHandles,pending());
  if(unref){check(kind+':unref-returns-same',row.handle.unref()===row.handle);check(kind+':hasRef-false-at-arm',row.handle.hasRef()===false);}
  else{check(kind+':ref-returns-same',row.handle.ref()===row.handle);check(kind+':hasRef-true-at-arm',row.handle.hasRef()===true);}
  return row.handle;
 }
 function clear(handle){
  if(!handle)return;state.clearAttempts++;
  try{backend.clearTimeout(handle);const r=state.handles.find(x=>x.handle===handle);if(r)r.pending=false;}
  catch(error){state.failed=true;state.clearErrors.push(dataError(error));}
 }
 function clearAll(){for(const r of state.handles)clear(r.handle);}
 function refWait(kind,delay,wantFirst,wantSecond){
  return new Promise(resolve=>{
   schedule(kind,()=>{
    try{if(kind==='B-reference')state.bRefCallbacks++;else state.cRefCallbacks++;observe(kind+':callback',wantFirst,wantSecond,state.callbackChecks);}
    finally{resolve();}
   },delay,false);
  });
 }
 const snapshot=(phase,requestedCase,checks,coverage)=>({schemaVersion:1,suite:'UNREF_ACROSS_ORDINARY_CALLS_V1',phase,ordinal:state.ordinal,
  firstHostCase:state.firstHostCase,requestedHostCase:requestedCase,policy:'preserve-old-unref-tasks',boundaryMode:backend.boundaryMode,
  delays:{...UNREF_DELAYS},coverage,passed:!state.failed&&coverage==='complete',checks:clone(checks),callbackChecks:clone(state.callbackChecks),observations:clone(state.observations),
  counts:{old:state.oldCallbacks,candidate:state.candidateCallbacks,bReference:state.bRefCallbacks,cReference:state.cRefCallbacks},
  plannedHandles:{pending:pending(),peak:state.peakPlannedHandles,totalScheduled:state.handles.length,clearAttempts:state.clearAttempts,clearErrors:clone(state.clearErrors)},
  sameTagAndOrdinalContinuityOnly:true,asyncResourceIdsUsed:false,physicalStoreOrNativeOwnerIdentityProved:false,nativeQueueOrRetirementProved:false,exactTimerAccuracyOrPerformanceClaimed:false});
 async function handle(phase,hostCase){
  if(inFlight)throw new Error('UNREF_REUSE_CONCURRENT_CALL_MUST_DISCARD');
  inFlight=true;
  const checks=[];activeChecks=checks;let coverage='complete';state.ordinal++;
  try{
   if(phase==='B'&&(state.earlyOld||state.oldCallbacks!==0||state.candidateCallbacks!==0))coverage='inconclusive-callback-before-B-entry';
   if(state.closed||state.failed)throw new Error('UNREF_REUSE_FAILED_OR_CLOSED_STATE_MUST_DISCARD');
   if(typeof hostCase!=='string'||!/^[A-Za-z0-9._-]{1,96}$/.test(hostCase))throw new TypeError('UNREF_REUSE_EXACT_FIRST_HOST_CASE_REQUIRED');
   check('phase-matches-ordinal',phases[state.ordinal-1]===phase);if(state.failed)throw new Error('UNREF_REUSE_STATE_CONTINUITY_MISSING');
   if(phase==='A'){state.firstHostCase=hostCase;state.origin=Object.freeze({firstHostCase:hostCase});}
   check('same-first-host-case',state.firstHostCase===hostCase);observe(phase+':fresh-entry',undefined,undefined);
   if(state.failed)throw new Error('UNREF_REUSE_BOUNDARY_OR_TAG_MISMATCH');
   const a=mark(phase+':first'),b=mark(phase+':second');state.phase=phase+'-active';
   if(phase==='A'){
    first.run(a,()=>second.run(b,()=>{
     const origin=state.origin,tag=state.firstHostCase;
     oldHandle=schedule('A-old',()=>{
      state.oldCallbacks++;if(state.phase!=='B-active')state.earlyOld=true;
      check('A-old:exactly-once',state.oldCallbacks===1,state.callbackChecks);
      check('A-old:during-B-interest',state.phase==='B-active',state.callbackChecks);
      check('A-old:origin-object-and-case-retained',state.origin===origin&&state.firstHostCase===tag,state.callbackChecks);
      observe('A-old:captured-context',a,b,state.callbackChecks);
     },UNREF_DELAYS.oldCallbackMs,true);
     candidateHandle=schedule('A-cancel-candidate',()=>{state.candidateCallbacks++;check('A-cancel-candidate:must-not-deliver',false,state.callbackChecks);observe('A-cancel-candidate:captured-context',a,b,state.callbackChecks);},UNREF_DELAYS.cancelCandidateMs,true);
     observe('A:after-arms',a,b);check('A:no-callback-before-return',state.oldCallbacks===0&&state.candidateCallbacks===0);
    }));
    observe('A:caller-restored',undefined,undefined);state.phase='A-returned';
   }else if(phase==='B'){
    if(state.oldCallbacks!==0||state.candidateCallbacks!==0){coverage='inconclusive-callback-before-B-entry';state.failed=true;check('B:both-A-callbacks-still-pending-at-entry',false);throw new Error('UNREF_REUSE_EARLY_DELIVERY_COVERAGE_INCONCLUSIVE');}
    await first.run(a,()=>second.run(b,async()=>{
     observe('B:before-referenced-interest',a,b);
     // Real referenced interest exists BEFORE cancellation and first await.
     const fence=refWait('B-reference',UNREF_DELAYS.bReferenceFenceMs,a,b);
     observe('B:before-cross-call-clear',a,b);clear(candidateHandle);observe('B:after-cross-call-clear',a,b);
     await fence;
     observe('B:continuation-restored',a,b);
     check('B:old-A-delivered-once-during-B',state.oldCallbacks===1&&!state.earlyOld);
     check('B:cancelled-candidate-not-delivered',state.candidateCallbacks===0);check('B:referenced-callback-once',state.bRefCallbacks===1);
     check('B:all-callback-context-observations-pass',state.callbackChecks.every(x=>x.passed===true));
    }));
    observe('B:caller-restored',undefined,undefined);state.phase='B-returned';
   }else{
    await first.run(a,()=>second.run(b,async()=>{
     observe('C:before-normal-grace',a,b);await refWait('C-reference',UNREF_DELAYS.cReferenceFenceMs,a,b);observe('C:continuation-restored',a,b);
     check('C:old-A-still-exactly-once',state.oldCallbacks===1&&!state.earlyOld);check('C:cancelled-candidate-still-zero',state.candidateCallbacks===0);
     check('C:both-referenced-fences-once',state.bRefCallbacks===1&&state.cRefCallbacks===1);check('C:all-callback-observations-pass',state.callbackChecks.every(x=>x.passed===true));
    }));
    observe('C:caller-restored',undefined,undefined);clearAll();check('C:local-planned-handles-settled-or-cleared',pending()===0);check('C:clear-operations-did-not-throw',state.clearErrors.length===0);state.phase='C-returned';
   }
  }catch(error){state.failed=true;if(coverage==='complete')coverage='failed';checks.push({id:'ordinary-call-completed-without-exception',passed:false,error:dataError(error)});clearAll();}
  finally{activeChecks=null;inFlight=false;}
  return snapshot(phase,hostCase,checks,coverage);
 }
 function dispose(){clearAll();for(const store of stores)try{store.disable();}catch(error){state.failed=true;state.clearErrors.push(dataError(error));}state.closed=true;return{workloadClearAttempts:state.clearAttempts,workloadPendingAfterClear:pending(),storesDisableCalls:2,errors:clone(state.clearErrors),nativeQueueOrRootReleaseProved:false};}
 return{
  handle,dispose,
  // HOST-reference entry only. Native HTTP already enters genuine fresh scope
  // before Request conversion and calls handle directly, without a nested owner.
  referenceCall(phase,hostCase){if(backend.boundaryMode!=='node-public-empty-store-projection'||state.closed)throw new Error('REFERENCE_BOUNDARY_REQUIRES_ENABLED_HOST_STATE');return boundaries.runFreshRequest(()=>handle(phase,hostCase),undefined);},
 };
}
function unrefPublicProjection(value){
 if(value.schemaVersion!==1||value.suite!=='UNREF_ACROSS_ORDINARY_CALLS_V1'||value.passed!==true||value.coverage!=='complete'||value.policy!=='preserve-old-unref-tasks')throw new Error('UNREF_REUSE_INCOMPLETE_OBSERVATION');
 if(value.checks.some(x=>x.passed!==true)||value.callbackChecks.some(x=>x.passed!==true))throw new Error('UNREF_REUSE_FALSE_OBSERVATION');
 return{schemaVersion:1,phase:value.phase,ordinal:value.ordinal,policy:value.policy,checks:[...value.checks].sort((a,b)=>a.id<b.id?-1:a.id>b.id?1:0),callbackChecks:[...value.callbackChecks].sort((a,b)=>a.id<b.id?-1:a.id>b.id?1:0),counts:value.counts,observations:value.observations,delays:value.delays,plannedPending:value.plannedHandles.pending,plannedPeak:value.plannedHandles.peak};
}

// Source only: bootstrap and all ALS/timer creation are deferred to neutral readiness.
async function prepareUnrefServer(){
 const process=bootstrap();
 if(globalThis.process!==process)throw new Error('Actual native process identity mismatch');
 const state=createUnrefReuseState({AsyncLocalStorage:UnrefAsyncLocalStorage,
  boundaryMode:'actual-native-private-boundaries',boundaries(){return{runFreshRequest,runNeutralServer};},
  setTimeout:unrefTimeout,clearTimeout:unrefClearTimeout});
 const handler=async request=>{
  let collection,finalCleanup;
  try{
   if(request.method!=='GET')throw new TypeError('UNREF_REUSE_GET_ONLY');
   const url=new URL(request.url),phase=url.searchParams.get('phase'),hostCase=url.searchParams.get('case');
   // createWasiHttpHandler already entered the real fresh native owner before conversion.
   collection=await state.handle(phase,hostCase);
   if(phase==='C'||collection.passed!==true){finalCleanup=state.dispose();collection.finalCleanup=finalCleanup;}
   return new Response(JSON.stringify({schemaVersion:1,marker:'NEXT_NATIVE_UNREF_REUSE_V1',call:collection.ordinal,
    method:request.method,collection}),{status:collection.passed?200:500,
    headers:{'content-type':'application/json; charset=utf-8','cache-control':'no-store'}});
  }catch(error){
   finalCleanup??=state.dispose();
   return new Response(JSON.stringify({schemaVersion:1,marker:'NEXT_NATIVE_UNREF_REUSE_V1',passed:false,
    error:dataError(error),collection:collection??null,finalCleanup}),{status:500,
    headers:{'content-type':'application/json; charset=utf-8','cache-control':'no-store'}});
  }
 };
 return createWasiHttpHandler(handler,types,runFreshRequest);
}
export const incomingHandler=createNeutralReadyHandler({runNeutralServer,prepareServer:prepareUnrefServer,disposeBeforeEntry});
