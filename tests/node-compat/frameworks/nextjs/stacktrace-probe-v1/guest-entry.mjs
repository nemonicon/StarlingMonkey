// Source-only isolated ordinary HTTP stack diagnostic; no Next/app/FS bootstrap.
import {runFreshRequest} from 'starling:node-http';
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
function streamFailure(value) {
  if (value?.tag === 'last-operation-failed') {
    let message = 'WASI HTTP stream operation failed';
    try { message = value.val.toDebugString(); } finally { drop(value.val); }
    return new Error(message);
  }
  return value instanceof Error ? value : new Error('WASI HTTP stream failure: ' + value?.tag);
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
                if (error?.tag === 'closed') {
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


// INIT: function declarations and case metadata only. All Error work is ordinary.
const caseIds=Object.freeze(['plain-capture-descriptor','structured-callback-and-frames','throwing-callback-identity','exact-depd-getStack-and-location']);
function typed(value){return {valueType:typeof value,isNull:value===null,isArray:Array.isArray(value)};}
function errorData(value){const out=typed(value);if(value!==null&&['object','function'].includes(typeof value)){for(const key of ['name','message','code'])try{const v=value[key];out[key]=v===undefined?{type:'undefined'}:{type:typeof v,value:['string','number','boolean'].includes(typeof v)?v:null};}catch{out[key]={type:'read-threw'};}}return out;}
function descriptor(object,key){const d=Object.getOwnPropertyDescriptor(object,key);if(!d)return {own:false};return {own:true,enumerable:d.enumerable,configurable:d.configurable,data:Object.hasOwn(d,'value'),writable:d.writable??null,valueType:Object.hasOwn(d,'value')?typeof d.value:null,getType:typeof d.get,setType:typeof d.set};}
function restore(key,d){if(d)Object.defineProperty(Error,key,d);else delete Error[key];}
function protectedCase(run){const prepare=Object.getOwnPropertyDescriptor(Error,'prepareStackTrace'),limit=Object.getOwnPropertyDescriptor(Error,'stackTraceLimit');try{return run();}finally{restore('prepareStackTrace',prepare);restore('stackTraceLimit',limit);}}
function frameData(frame){const out=typed(frame);for(const name of ['getFileName','getLineNumber','getColumnNumber','getFunctionName','isEval','getEvalOrigin']){try{const method=frame?.[name];out[name]={methodType:typeof method};if(typeof method==='function'){const value=Reflect.apply(method,frame,[]);out[name].return={...typed(value),value:['string','number','boolean'].includes(typeof value)?value:null};}}catch(error){out[name]={error:errorData(error)};}}return out;}
function limitedStack(value){const out=typed(value);if(typeof value==='string'){out.stringLength=value.length;out.string=value.slice(0,16384);out.truncated=value.length>16384;}if(Array.isArray(value)){out.frameCount=value.length;out.frames=value.slice(0,16).map(frameData);out.truncated=value.length>16;}return out;}

// EXACT_DEPD_FUNCTIONS: the three following functions are copied byte for byte
// from the pinned unchanged Next16.4.5 compiled/send dependency. See derivation.
function getStack(){var e=Error.stackTraceLimit;var t={};var a=Error.prepareStackTrace;Error.prepareStackTrace=prepareObjectStackTrace;Error.stackTraceLimit=Math.max(10,e);Error.captureStackTrace(t);var i=t.stack.slice(1);Error.prepareStackTrace=a;Error.stackTraceLimit=e;return i}
function prepareObjectStackTrace(e,t){return t}
function callSiteLocation(e){var t=e.getFileName()||"<anonymous>";var a=e.getLineNumber();var i=e.getColumnNumber();if(e.isEval()){t=e.getEvalOrigin()+", "+t}var n=[t,a,i];n.callSite=e;n.name=e.getFunctionName();return n}

function collectStacktraceProbe(call){
 const records=[];const prepareBefore=Object.getOwnPropertyDescriptor(Error,'prepareStackTrace'),limitBefore=Object.getOwnPropertyDescriptor(Error,'stackTraceLimit');
 function record(id,run){try{records.push({id,completed:true,value:protectedCase(run)});}catch(error){records.push({id,completed:false,error:errorData(error)});}}
 record(caseIds[0],()=>{
  const target={};const captureDescriptor=descriptor(Error,'captureStackTrace');
  function capturePlain(){Error.captureStackTrace(target,capturePlain);}capturePlain();
  const stack=target.stack;
  return {captureStackTraceType:typeof Error.captureStackTrace,captureDescriptor,stackOwnDescriptor:descriptor(target,'stack'),stack:limitedStack(stack)};
 });
 record(caseIds[1],()=>{
  const target={},events=[];let callbackInvocations=0,callbackTargetIdentity=false,callbackFrames;
  Object.defineProperty(Error,'stackTraceLimit',{value:8,writable:true,configurable:true});
  Object.defineProperty(Error,'prepareStackTrace',{value:function(error,frames){events.push('callback');callbackInvocations++;callbackTargetIdentity=error===target;callbackFrames=limitedStack(frames);return frames;},writable:true,configurable:true});
  function stackProbeInner(){events.push('before-capture');Error.captureStackTrace(target,stackProbeInner);events.push('after-capture');}
  function stackProbeMiddle(){stackProbeInner();}stackProbeMiddle();
  events.push('before-stack-read');const stack=target.stack;events.push('after-stack-read');
  return {events,callbackInvocations,callbackTargetIdentity,callbackFrames:callbackFrames??null,stackOwnDescriptor:descriptor(target,'stack'),stack:limitedStack(stack)};
 });
 record(caseIds[2],()=>{
  const target={},sentinel={tag:'STACKTRACE_CALLBACK_SENTINEL',call},events=[];let callbackInvocations=0,captureReturned=false,stackReadReturned=false,captureThrown=null,stackReadThrown=null;
  Object.defineProperty(Error,'prepareStackTrace',{value:function(){events.push('callback');callbackInvocations++;throw sentinel;},writable:true,configurable:true});
  events.push('before-capture');try{Error.captureStackTrace(target);captureReturned=true;}catch(error){captureThrown={identity:error===sentinel,error:errorData(error)};}events.push('after-capture');
  events.push('before-stack-read');try{void target.stack;stackReadReturned=true;}catch(error){stackReadThrown={identity:error===sentinel,error:errorData(error)};}events.push('after-stack-read');
  return {events,callbackInvocations,captureReturned,stackReadReturned,captureThrown,stackReadThrown};
 });
 record(caseIds[3],()=>{
  const stack=getStack(),out={stack:limitedStack(stack)};
  // Exact depd initialization sequence, without rewriting its frame assumption.
  try{const location=callSiteLocation(stack[1]);out.depdLocationSucceeded=true;out.location={file:location[0],line:location[1],column:location[2],name:location.name};out.selectedFrame=frameData(stack[1]);}
  catch(error){out.depdLocationSucceeded=false;out.locationError=errorData(error);}return out;
 });
 const prepareAfter=Object.getOwnPropertyDescriptor(Error,'prepareStackTrace'),limitAfter=Object.getOwnPropertyDescriptor(Error,'stackTraceLimit');
 const sameDescriptor=(a,b)=>a===undefined?b===undefined:b!==undefined&&Reflect.ownKeys(a).every(k=>Object.is(a[k],b[k]))&&Reflect.ownKeys(a).length===Reflect.ownKeys(b).length;
 return {schemaVersion:1,suite:'ISOLATED_STRUCTURED_STACKTRACE_PROBE_V1',call,records,errorGlobalsRestored:sameDescriptor(prepareBefore,prepareAfter)&&sameDescriptor(limitBefore,limitAfter),applicationImported:false,applicationRewritten:false,fullNextClaim:false};
}

let calls=0;
const handler=()=>new Response(JSON.stringify(collectStacktraceProbe(++calls)),{status:200,headers:{'content-type':'application/json; charset=utf-8','cache-control':'no-store'}});
export const incomingHandler=createWasiHttpHandler(handler,types,runFreshRequest);
