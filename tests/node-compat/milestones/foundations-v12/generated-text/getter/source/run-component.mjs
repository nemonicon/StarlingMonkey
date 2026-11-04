import assert from 'node:assert/strict';
import {readFile,writeFile} from 'node:fs/promises';
import {join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {harness} from './harness.mjs';
import {hash} from './preflight.mjs';

const h=await harness(),oracleBytes=await readFile(new URL('./node-results.json',import.meta.url)),oracle=JSON.parse(oracleBytes);
assert.equal(hash(await readFile(join(h.here,'public-cases.mjs'))),oracle.sourceSha256);
const bundle=await h.bundle(join(h.here,'component.mjs'),['node:events']);
const main=await h.build('abort_m11_main',bundle.code);
const expectedNames=['EventEmitter','EventEmitterAsyncResource','addAbortListener','captureRejectionSymbol','captureRejections','default','defaultMaxListeners','errorMonitor','getEventListeners','getMaxListeners','init','listenerCount','on','once','setMaxListeners','usingDomains'];
function validate(report,count){
 assert(!report.failure,JSON.stringify(report.failure));assert.equal(report.calls,count);
 assert.deepEqual(report.publicCases,oracle.publicCases);assert.deepEqual(report.nestedOnceCases,oracle.nestedOnceCases);assert.deepEqual(report.receiverCases,oracle.receiverCases);
 assert.deepEqual(report.namespace,{names:expectedNames,defaultNamed:true,canonicalCached:true,aliasValues:true,defaultAlias:true,then:'undefined',errorMonitorType:'symbol',captureRejectionSymbol:true,defaultMaxListeners:10,captureRejections:false,usingDomains:false});
 assert.deepEqual(report.commonJS,{same:true,constructorAlias:true,defaultProperty:'undefined',addAbortListenerType:'function',errorMonitorType:'symbol',rejectedCall:'ERR_SM_NODE_UNSUPPORTED',rejectedConstruction:'ERR_SM_NODE_UNSUPPORTED'});
 assert.equal(report.profileErrors.hooks,0);assert.equal(report.profileErrors.ambient,0);assert.equal(report.profileErrors.errors.length,7);
 for(const error of report.profileErrors.errors){assert.equal(error.profile,'sm-node-22.14.0-m0.10');assert.equal(error.module,'node:events');assert.equal(error.own,true);assert.equal(error.code,error.name==='invalid-signal'?'ERR_INVALID_ARG_TYPE':'ERR_SM_NODE_UNSUPPORTED');}
 assert.deepEqual(report.snapshot,{before:count===1?0:1,after:1,signalThis:true,currentTarget:true,aborted:false});
 assert.deepEqual(report.symbol.descriptor,{enumerable:false,writable:false,configurable:false});
}
const instance=await h.importFixture(main),calls=[];
for(let count=1;count<=3;count++){const value=JSON.parse(await instance.run());validate(value,count);calls.push(value);await writeFile(join(h.output,'main-progress.json'),JSON.stringify(calls,null,2)+'\n');}
const fresh=h.freshHost(main);validate(fresh.observed,1);

// Actual raw specifiers exercise separate native registration/cache entries;
// the bundled main deliberately canonicalizes bare imports before packaging.
const aliasSource=`import root,*as a from'node:events';import bare,*as b from'events';import*as again from'node:events';import*as bareAgain from'events';let calls=0;export function run(){const saved=root.defaultMaxListeners;root.defaultMaxListeners=19;const shared=bare.defaultMaxListeners;root.defaultMaxListeners=saved;return JSON.stringify({calls:++calls,names:Object.getOwnPropertyNames(a).sort(),canonicalCached:a===again,bareCached:b===bareAgain,aliasValues:Object.keys(a).every(name=>a[name]===b[name]),sameDefaults:root===bare&&root===a.EventEmitter,sharedDefault:shared,namedSnapshot:a.defaultMaxListeners,then:typeof a.then,aliasNamespacesSame:a===b});}`;
const aliases=await h.build('abort_m11_aliases',aliasSource),aliasInstance=await h.importFixture(aliases),aliasCalls=[];
function checkAlias(value,count){assert.equal(value.calls,count);assert.deepEqual(value.names,expectedNames);for(const key of ['canonicalCached','bareCached','aliasValues','sameDefaults'])assert.equal(value[key],true,key);assert.equal(value.sharedDefault,19);assert.equal(value.namedSnapshot,10);assert.equal(value.then,'undefined');}
for(let count=1;count<=3;count++){const value=JSON.parse(await aliasInstance.run());checkAlias(value,count);aliasCalls.push(value);}const aliasFresh=h.freshHost(aliases);checkAlias(aliasFresh.observed,1);

const prefix="import{addAbortListener}from'node:events';import{spawn}from'node:child_process';";
const initializers=[];
for(const[name,body,marker]of[
 ['fresh-sync',"const c=new AbortController();addAbortListener(c.signal,()=>spawn());try{c.abort()}catch{}",/child_process\.spawn/],
 ['already-sync',"const c=new AbortController();c.abort();addAbortListener(c.signal,()=>spawn());",/child_process\.spawn|ERR_SM_NODE_INITIALIZATION_REJECTION/],
 ['fresh-async',"const c=new AbortController();addAbortListener(c.signal,async()=>spawn());c.abort();",/child_process\.spawn|ERR_SM_NODE_INITIALIZATION_REJECTION/],
 ['already-async',"const c=new AbortController();c.abort();addAbortListener(c.signal,async()=>spawn());",/child_process\.spawn|ERR_SM_NODE_INITIALIZATION_REJECTION/],
 ['first-error-continues',"const c=new AbortController();let seen=0;addAbortListener(c.signal,()=>{seen++;throw{toString(){return'PROTECTED_FIRST_AFTER_'+seen}}});addAbortListener(c.signal,()=>{seen++});c.abort();",/PROTECTED_FIRST_AFTER_2/],
 ['undefined',"const c=new AbortController();addAbortListener(c.signal,()=>{throw undefined});c.abort();",/undefined/],
 ['number',"const c=new AbortController();addAbortListener(c.signal,()=>{throw 73519});c.abort();",/73519/],
 ['unsupported-new',"import{once}from'node:events';new once();",/ERR_SM_NODE_UNSUPPORTED|node:events\.once/],
]){initializers.push(await h.expectInitialization('init_'+name,prefix+body+"export function run(){return'must-not-return'}",marker));console.log(JSON.stringify({initializer:name,rejected:true}));}

const benignSource=prefix+`let calls=0;export async function run(){let caught=[],thenReads=0;const c=new AbortController();addAbortListener(c.signal,()=>{try{spawn()}catch(error){caught.push(error.code)}});c.abort();const already=new AbortController();already.abort();addAbortListener(already.signal,()=>{try{spawn()}catch(error){caught.push(error.code)}return{get then(){thenReads++;throw Error('must ignore returned thenable')}}});const rejection=Promise.reject(Error('HANDLED_LATER'));queueMicrotask(()=>rejection.catch(()=>{}));await Promise.resolve();return JSON.stringify({calls:++calls,caught,thenReads});}`;
const benign=await h.build('abort_m11_handled_reuse',benignSource),benignInstance=await h.importFixture(benign),benignCalls=[];
const checkBenign=(value,count)=>assert.deepEqual(value,{calls:count,caught:['ERR_SM_NODE_UNSUPPORTED','ERR_SM_NODE_UNSUPPORTED'],thenReads:0});
for(let count=1;count<=3;count++){const value=JSON.parse(await benignInstance.run());checkBenign(value,count);benignCalls.push(value);}const benignFresh=h.freshHost(benign);checkBenign(benignFresh.observed,1);

const fatal=[];
for(const[name,body]of[
 ['fresh_sync',"const c=new AbortController();addAbortListener(c.signal,()=>spawn());try{c.abort()}catch{}"],
 ['queued_sync',"const c=new AbortController();c.abort();addAbortListener(c.signal,()=>spawn());"],
 ['fresh_async',"const c=new AbortController();addAbortListener(c.signal,async()=>spawn());c.abort();"],
 ['queued_async',"const c=new AbortController();c.abort();addAbortListener(c.signal,async()=>spawn());"],
 ['primitive_undefined',"const c=new AbortController();addAbortListener(c.signal,()=>{throw undefined});c.abort();"],
]){fatal.push(await h.fatal('abort_m11_fatal_'+name,prefix+`export function run(){${body}return'must-not-return'}`));console.log(JSON.stringify({fatal:name,rejectedOnBoth:true}));}
await h.finish();
const report={state:'NEW_PRODUCTION306_ORDINARY_NATIVE_ADD_ABORT_LISTENER_PASSED',recordedAtUtc:new Date().toISOString(),...h.evidence,
 runnerSha256:hash(await readFile(fileURLToPath(import.meta.url))),nodeOracleSha256:hash(oracleBytes),publicNodeGroups:oracle.passed,
 main:{fixture:main,calls,freshWasmtime:fresh},aliases:{fixture:aliases,calls:aliasCalls,freshWasmtime:aliasFresh},initializers,
 benign:{fixture:benign,calls:benignCalls,freshWasmtime:benignFresh},fatal,
 targetSymbolIdentity:{node:oracle.targetSymbolInfo,target:calls[0].symbol,scope:'Target disposal uses its actual well-known Symbol; Node registry identity is measured, not rewritten or claimed compatible.'},
 limits:['Exact new source and actual derived macro ON admitted before any prototype negatives. No Events-OFF/old path was executed.','29 Node public groups plus namespace/CJS, own error and snapshot/reuse profile checks; no complete Node EventTarget/stream/process compatibility.','Detailed invalid-value messages and target Symbol.dispose registry identity remain explicit bounded differences.','Current ALS/AsyncResource/process error-handler semantics are not implemented; original Node dispatch/registration oracle remains separate.','Fatal initialized/deployed failures require instance discard; handled retained calls are separate successful controls.','Capture-failure/reset/general AbortSignal/Terminator/request teardown are not proved.','Ordinary Release only; no DEBUG/OOM/fault/private memory or malformed ABI calls. No performance claim.']};
await h.save(report);console.log(JSON.stringify({state:report.state,engineSha256:report.engineSha256,entropy:h.metadata.entropyPolicy,publicGroups:29,initializationFailures:initializers.length,deployedFatalCases:fatal.length,retainedCalls:9,freshSuccessfulWasmtime:3,emittedImports:main.emittedImports,output:h.output},null,2));
