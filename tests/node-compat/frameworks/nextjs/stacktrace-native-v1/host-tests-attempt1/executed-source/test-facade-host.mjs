// Host Node22 semantic tests only. No target native/guest or host-operation call.
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {EventEmitter} from 'node:events';
import {URL,URLSearchParams} from 'node:url';
import * as querystring from 'node:querystring';
import path from 'node:path';
import {Buffer} from 'node:buffer';
import {createStartupFacade} from './after/startup-core.mjs';
import {collectStacktraceProbe} from '../stacktrace-probe-v1/cases.mjs';
import {compare} from '../stacktrace-wasmtime-collector-v1/comparison.mjs';

assert.equal(process.version,'v22.14.0');
const NodeError=globalThis.Error;
const globalErrorDescriptor=Object.getOwnPropertyDescriptor(globalThis,'Error');
const keys=['captureStackTrace','prepareStackTrace','stackTraceLimit'];
const original=Object.fromEntries(keys.map(k=>[k,Object.getOwnPropertyDescriptor(NodeError,k)]));
const originalCapture=original.captureStackTrace.value;
const inventoryUrl=new URL('../../../foundation-startup/next-startup-candidate-v2/startup-builtin-inventory.node-v22.14.0.json',import.meta.url);
const inventoryBytes=readFileSync(inventoryUrl);
assert.equal(createHash('sha256').update(inventoryBytes).digest('hex'),'bb897ff3e9c3fd3203cc80d55069ea602dd7780f7637b9265b417221d91dd5c0');
const inventory=JSON.parse(inventoryBytes).modules;
const result={schemaVersion:1,scope:'Host Node22 original CallSites injected into actual startup factory; no target native proof',node:process.version,v8:process.versions.v8,cases:[],hostOperations:[],providerCalls:0,applicationImported:false,targetNativeOrGuestExecuted:false};
const sourceUrls=['./after/startup-core.mjs','./stacktrace-facade.fragment.js','../stacktrace-probe-v1/cases.mjs','../stacktrace-wasmtime-collector-v1/comparison.mjs'];
function digest(url){const raw=readFileSync(new URL(url,import.meta.url));return {path:new URL(url,import.meta.url).pathname,bytes:raw.length,sha256:createHash('sha256').update(raw).digest('hex')};}
result.inputsBefore=sourceUrls.map(digest);
function restore(key,d){if(d)Object.defineProperty(NodeError,key,d);else delete NodeError[key];}
function setting(key,value){Object.defineProperty(NodeError,key,{value,writable:true,enumerable:true,configurable:true});}
function globalsFinally(fn){const p=Object.getOwnPropertyDescriptor(NodeError,'prepareStackTrace'),l=Object.getOwnPropertyDescriptor(NodeError,'stackTraceLimit');try{return fn();}finally{restore('prepareStackTrace',p);restore('stackTraceLimit',l);}}
function sameDescriptor(a,b){return a===undefined?b===undefined:b!==undefined&&Reflect.ownKeys(a).length===Reflect.ownKeys(b).length&&Reflect.ownKeys(a).every(k=>Object.is(a[k],b[k]));}
function thrown(action){let caught=false,value;try{action();}catch(e){caught=true;value=e;}assert(caught,'Expected a throw');return value;}
function code(action,expected){const e=thrown(action);assert.equal(e?.code,expected);return e;}
function test(name,fn){try{const value=globalsFinally(fn);result.cases.push({name,passed:true,...(value===undefined?{}:{value})});}catch(e){result.cases.push({name,passed:false,error:{type:typeof e,name:e?.name??null,message:e?.message??null,code:e?.code??null}});}finally{activeProvider=nodeProvider;}}

// This oracle uses V8's real CallSite getters, especially isEval(). It does not
// infer provenance from a source filename, stack string or anonymous function.
function nodeProvider(limit,startAfter){
  result.providerCalls++;
  return globalsFinally(()=>{
    setting('prepareStackTrace',(_error,frames)=>frames);
    setting('stackTraceLimit',limit);
    const target={};Reflect.apply(originalCapture,NodeError,[target,startAfter]);
    const frames=target.stack;assert(Array.isArray(frames));
    return frames.map(f=>({source:f.getFileName()??'',functionName:f.getFunctionName(),line:f.getLineNumber()??0,column:f.getColumnNumber()??0,isEval:f.isEval()}));
  });
}
let activeProvider=nodeProvider;
const forbidden=name=>(..._args)=>{result.hostOperations.push(name);throw new NodeError('Forbidden host operation: '+name);};
const kernel={captureFrames(...args){return activeProvider(...args);},errnoConstants:{}};
for(const name of ['checkDeployed','initial','startPerformance','cwd','chdir','monotonic','write','getBuiltin'])kernel[name]=forbidden(name);
function factory(k=kernel){return createStartupFacade({kernel:k,EventEmitter,URL,URLSearchParams,querystring,paths:path.posix,Buffer,nextTick:forbidden('nextTick'),inventory});}
function framesTarget(){setting('prepareStackTrace',(_error,frames)=>frames);const target={};NodeError.captureStackTrace(target);return {target,frames:target.stack};}
const validRecord={source:'test-source.js',functionName:'known',line:4,column:8,isEval:false};

try{
  result.originalNodeProbe=collectStacktraceProbe(1);
  assert(result.originalNodeProbe.records.every(r=>r.completed));
  let facade;
  test('actual factory installs without any provider or host operation',()=>{facade=factory();assert.equal(result.providerCalls,0);assert.deepEqual(result.hostOperations,[]);assert.equal(facade.state().bootstrapped,false);return {providerCalls:0,hostOperations:0};});
  test('four original probe cases have selected Node22 parity',()=>{result.facadeProbe=collectStacktraceProbe(1);const c=compare(result.facadeProbe,result.originalNodeProbe,1);result.probeComparison=c;assert(c.nodeSelectedParity,JSON.stringify(c.differences));assert(result.facadeProbe.records.every(r=>r.completed));assert(result.facadeProbe.records[3].value.depdLocationSucceeded);return {cases:4,selectedParity:true};});
  test('limit zero bypasses provider and returns empty callback frames',()=>{setting('stackTraceLimit',0);const before=result.providerCalls;const {frames}=framesTarget();assert.deepEqual(frames,[]);assert.equal(result.providerCalls,before);});
  test('maximum128 is supported by the finite facade',()=>{setting('stackTraceLimit',128);const {frames}=framesTarget();assert(frames.length>0&&frames.length<=128);});
  for(const limit of [-1,1.5,129,NaN,Infinity,-Infinity])test('out-of-range limit '+String(limit),()=>{setting('stackTraceLimit',limit);const before=result.providerCalls;code(()=>NodeError.captureStackTrace({}),'ERR_SM_NODE_STACK_LIMIT');assert.equal(result.providerCalls,before);});
  for(const limit of ['10',undefined,null,1n])test('non-number limit '+String(limit),()=>{setting('stackTraceLimit',limit);code(()=>NodeError.captureStackTrace({}),'ERR_INVALID_ARG_TYPE');});
  test('bad target is rejected before provider',()=>{const before=result.providerCalls;for(const v of [null,undefined,0,false,'x'])code(()=>NodeError.captureStackTrace(v),'ERR_INVALID_ARG_TYPE');assert.equal(result.providerCalls,before);});
  test('function target is accepted',()=>{setting('prepareStackTrace',()=>17);function target(){}NodeError.captureStackTrace(target);assert.equal(target.stack,17);});
  test('missing provider is refused at actual factory install',()=>{code(()=>factory({...kernel,captureFrames:undefined}),'ERR_SM_NODE_STACK_PROVIDER');});
  const badProviders=[['not-array',()=>({})],['over-limit',limit=>Array.from({length:limit+1},()=>({...validRecord}))],['null-record',()=>[null]],['missing-provenance',()=>[{source:'x',functionName:null,line:1,column:1}]],['nonboolean-provenance',()=>[{...validRecord,isEval:'false'}]],['undefined-name',()=>[{...validRecord,functionName:undefined}]],['nonstring-source',()=>[{...validRecord,source:17}]],['sparse-array',()=>Array(1)],['inherited-metadata',()=>[Object.create(validRecord)]]];
  for(const field of ['line','column'])for(const value of [-1,1.5,NaN,Infinity,0x100000000])badProviders.push([field+'-'+String(value),()=>[{...validRecord,[field]:value}]]);
  for(const [name,provider]of badProviders)test('bad provider rejected: '+name,()=>{activeProvider=provider;code(()=>NodeError.captureStackTrace({}),'ERR_SM_NODE_STACK_PROVIDER');});
  test('provider metadata accessors are refused without invocation',()=>{let reads=0;const record={...validRecord};Object.defineProperty(record,'isEval',{get(){reads++;return false;},enumerable:true});activeProvider=()=>[record];code(()=>NodeError.captureStackTrace({}),'ERR_SM_NODE_STACK_PROVIDER');assert.equal(reads,0);});
  test('provider throw identity is preserved before target installation',()=>{const sentinel=Object.freeze({tag:'PROVIDER_SENTINEL'});activeProvider=()=>{throw sentinel;};const target={};assert.equal(thrown(()=>NodeError.captureStackTrace(target)),sentinel);assert.equal(Object.hasOwn(target,'stack'),false);});
  test('unknown source and zero positions remain unknown',()=>{activeProvider=()=>[{source:'',functionName:null,line:0,column:0,isEval:false}];const {frames}=framesTarget();assert.equal(frames[0].getFileName(),null);assert.equal(frames[0].getFunctionName(),null);assert.equal(frames[0].getLineNumber(),null);assert.equal(frames[0].getColumnNumber(),null);assert.equal(frames[0].isEval(),false);});
  test('ordinary filename text cannot invent eval provenance',()=>{activeProvider=()=>[{...validRecord,source:'eval at fake (anonymous.js)'}];const {frames}=framesTarget();assert.equal(frames[0].isEval(),false);});
  test('formatting is lazy, callback this/target identities are exact and result cached',()=>{let calls=0,seenThis,seenTarget;const token=Object.freeze({return:'identity'}),target={};setting('prepareStackTrace',function(e){calls++;seenThis=this;seenTarget=e;return token;});NodeError.captureStackTrace(target);assert.equal(calls,0);assert.equal(target.stack,token);assert.equal(target.stack,token);assert.equal(calls,1);assert.equal(seenThis,NodeError);assert.equal(seenTarget,target);});
  for(const sentinel of [Object.freeze({tag:'HOOK_SENTINEL'}),null,undefined,0,false])test('throwing callback identity/retry: '+String(sentinel),()=>{let calls=0;setting('prepareStackTrace',()=>{calls++;throw sentinel;});const target={};NodeError.captureStackTrace(target);for(let i=0;i<2;i++)assert(Object.is(thrown(()=>target.stack),sentinel));assert.equal(calls,2);});
  test('setter before read bypasses callback and caches arbitrary value',()=>{let calls=0;setting('prepareStackTrace',()=>{calls++;return 'unexpected';});const target={};NodeError.captureStackTrace(target);const token=Symbol('set-stack');target.stack=token;assert.equal(target.stack,token);assert.equal(target.stack,token);assert.equal(calls,0);});
  test('setter after cached read replaces the cached result',()=>{let calls=0;setting('prepareStackTrace',()=>++calls);const target={};NodeError.captureStackTrace(target);assert.equal(target.stack,1);target.stack=undefined;assert.equal(target.stack,undefined);assert.equal(calls,1);});
  test('setting stack during hook has selected original Node semantics',()=>{function scenario(capture){return globalsFinally(()=>{let calls=0;setting('prepareStackTrace',e=>{calls++;e.stack='setter-during-hook';return 'hook-return';});const target={};Reflect.apply(capture,NodeError,[target]);return {first:target.stack,second:target.stack,calls};});}const baseline=scenario(originalCapture),actual=scenario(NodeError.captureStackTrace);assert.deepEqual(actual,baseline);return {baseline,actual};});
  test('reentrant stack read formats once without recursive hook calls',()=>{let calls=0,inner;setting('prepareStackTrace',e=>{calls++;inner=e.stack;return 'outer-result';});const target={name:'Error',message:'reentry'};NodeError.captureStackTrace(target);assert.equal(target.stack,'outer-result');assert.equal(typeof inner,'string');assert.equal(calls,1);});
  test('CallSite constructor cannot be forged',()=>{const {frames}=framesTarget();assert(frames.length);code(()=>new frames[0].constructor(),'ERR_INVALID_ARG_TYPE');});
  for(const method of ['getThis','getFunction','getTypeName','getMethodName','isToplevel','isNative','isConstructor','isAsync','isPromiseAll','getPromiseIndex'])test('deferred CallSite method refuses: '+method,()=>{const {frames}=framesTarget();code(()=>frames[0][method](),'ERR_SM_NODE_UNSUPPORTED');});
  test('real eval provenance comes from original Node CallSite.isEval',()=>{setting('prepareStackTrace',(_e,frames)=>frames);const target=eval('(function dynamicStackProbe(){const target={};Error.captureStackTrace(target);return target;})()');const frames=target.stack;const frame=frames.find(f=>f.isEval());assert(frame,'Expected an actual Node eval frame');assert.equal(frame.isEval(),true);code(()=>frame.getEvalOrigin(),'ERR_SM_NODE_UNSUPPORTED');code(()=>frame.toString(),'ERR_SM_NODE_UNSUPPORTED');return {actualNodeEvalFrames:frames.filter(f=>f.isEval()).length};});
  test('ordinary getEvalOrigin returns undefined',()=>{const {frames}=framesTarget();const frame=frames.find(f=>!f.isEval());assert(frame);assert.equal(frame.getEvalOrigin(),undefined);});
  test('all forbidden host kernel methods remain uncalled',()=>{assert.deepEqual(result.hostOperations,[]);});
}finally{
  for(const key of keys)restore(key,original[key]);
  Object.defineProperty(globalThis,'Error',globalErrorDescriptor);
  result.originalErrorDescriptorsRestored=keys.every(k=>sameDescriptor(original[k],Object.getOwnPropertyDescriptor(NodeError,k)))&&sameDescriptor(globalErrorDescriptor,Object.getOwnPropertyDescriptor(globalThis,'Error'));
  result.inputsAfter=sourceUrls.map(digest);
  result.inputSourcesUnchanged=JSON.stringify(result.inputsBefore)===JSON.stringify(result.inputsAfter);
}
result.passed=result.cases.every(c=>c.passed)&&result.originalErrorDescriptorsRestored&&result.inputSourcesUnchanged&&result.hostOperations.length===0;
result.counts={cases:result.cases.length,passed:result.cases.filter(c=>c.passed).length,failed:result.cases.filter(c=>!c.passed).length};
console.log(JSON.stringify(result,null,2));
process.exitCode=result.passed?0:1;
