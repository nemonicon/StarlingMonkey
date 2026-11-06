// INIT: function declarations and case metadata only. All Error work is ordinary.
export const caseIds=Object.freeze(['plain-capture-descriptor','structured-callback-and-frames','throwing-callback-identity','exact-depd-getStack-and-location']);
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

export function collectStacktraceProbe(call){
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
