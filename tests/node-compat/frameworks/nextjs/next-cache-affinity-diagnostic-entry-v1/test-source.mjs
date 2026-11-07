// Actual helper text, ordinary inert byte-fill/logger callbacks only. No real RNG/WASI/actor.
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {dirname, join} from 'node:path';
import {recordCacheAffinityAdmission as observe} from './cache-affinity.mjs';

const here = dirname(fileURLToPath(import.meta.url));
const slot = '__STARLING_NEXT_CACHE_AFFINITY_DIAGNOSTIC_V1__';
let checks = 0;
const check = (predicate, message) => { assert(predicate, message); checks++; };
function sameThrow(callback, value, message) {
  let thrown = false, actual;
  try { callback(); } catch (error) { thrown = true; actual = error; }
  check(thrown && Object.is(actual, value), message);
}
function refuses(callback, message) { let thrown=false; try {callback();} catch {thrown=true;} check(thrown,message); }
function fixture(offset=0) {
  const target={}, lines=[];
  let fills=0;
  const bindings={target, fill(seed) { fills++; check(seed instanceof Uint8Array && seed.length===16,'exact 16-byte view');
    for(let i=0;i<seed.length;i++)seed[i]=(offset+i)&255; return seed; }, write(line) { lines.push(line); }};
  return {target,lines,bindings,get fills(){return fills;},get state(){return Object.getOwnPropertyDescriptor(target,slot)?.value;}};
}
check(!Object.hasOwn(globalThis,slot),'import installs no global state');
const a=fixture();
check(!Object.hasOwn(a.target,slot)&&a.fills===0,'fresh inert state absent');
observe('GET','http://fixture.test/fixture.txt',a.bindings);
check(a.fills===1&&a.lines.length===0&&a.state.ordinal===1,'first unlogged deployed admission creates state lazily');
observe('GET','http://fixture.test/api/cache',a.bindings);
observe('GET','http://fixture.test/api/cache?candidate=1',a.bindings);
observe('POST','http://fixture.test/api/revalidate',a.bindings);
observe('GET','http://fixture.test/api/cache',a.bindings);
check(a.fills===1&&a.state.ordinal===5,'one fill across five admissions');
const records=a.lines.map(JSON.parse);
assert.deepEqual(records.map(r=>r.ordinal),[2,3,4,5]);checks++;
check(records.every(r=>r.nonce==='000102030405060708090a0b0c0d0e0f'),'same 128-bit formatted inert token');
check(records.every(r=>r.schemaVersion===1&&r.marker==='NEXT_CACHE_AFFINITY_V1'&&r.phase==='request-admission'&&r.identityScope==='js-global-state-epoch'),'exact bounded record grammar');
check(a.lines.every(line=>line.length<=512&&!line.includes('\n')),'single bounded JSON line');
check(records[2].method==='POST'&&records[2].pathname==='/api/revalidate','invalidation exact method/path');
for(const [method,path]of [['POST','/api/cache'],['GET','/api/revalidate'],['GET','/api/cache-other'],['get','/api/cache']])
  observe(method,'http://fixture.test'+path,a.bindings);
check(a.lines.length===4&&a.state.ordinal===9,'nonselected methods/routes count but emit no cache record');
const descriptor=Object.getOwnPropertyDescriptor(a.target,slot);
check(descriptor.enumerable===false&&descriptor.writable===false&&descriptor.configurable===false,'ordinary own nonenumerable immutable slot');
check(Object.keys(a.target).length===0&&!Object.isExtensible(a.state),'state does not widen enumerable main globals');
refuses(()=>{a.state.nonce='forged';},'nonce immutable');
check(a.state.nonce==='000102030405060708090a0b0c0d0e0f','nonce unchanged');
const b=fixture(32);observe('GET','http://fixture.test/api/cache',b.bindings);
check(b.state.ordinal===1&&b.state.nonce!==a.state.nonce&&a.state.ordinal===9,'independent inert global states (not real heap/Store proof)');
let getters=0;
for(const shape of ['getter','writable','extra-state','accessor-state']) {
  const c=fixture();
  if(shape==='getter')Object.defineProperty(c.target,slot,{get(){getters++;throw false;}});
  else if(shape==='writable')Object.defineProperty(c.target,slot,{value:{},writable:true});
  else {
    const state={};Object.defineProperties(state,{nonce:shape==='accessor-state'?{get(){getters++;throw 0;},enumerable:true}:{value:'0'.repeat(32),enumerable:true},ordinal:{value:0,enumerable:true,writable:true}});
    if(shape==='extra-state')Object.defineProperty(state,'extra',{value:true});
    Object.preventExtensions(state);Object.defineProperty(c.target,slot,{value:state});
  }
  refuses(()=>observe('GET','http://fixture.test/api/cache',c.bindings),'conflicting '+shape+' refuses');
  check(c.fills===0&&c.lines.length===0,'conflict has no entropy or output');
}
check(getters===0,'unexpected data getters never read');
for(const value of [undefined,null,false,0,'']) {
  const c=fixture();c.bindings.fill=()=>{throw value;};
  sameThrow(()=>observe('GET','http://fixture.test/api/cache',c.bindings),value,'falsy entropy failure identity');
  check(!Object.hasOwn(c.target,slot)&&c.lines.length===0,'failed fill publishes no global state/output');
  const d=fixture();d.bindings.write=()=>{throw value;};
  sameThrow(()=>observe('GET','http://fixture.test/api/cache',d.bindings),value,'falsy logger failure identity');
  check(d.fills===1&&d.state.ordinal===1,'logger failure retains admitted ordinal, never fabricates a record');
  d.bindings.write=line=>d.lines.push(line);observe('GET','http://fixture.test/api/cache',d.bindings);
  check(d.fills===1&&JSON.parse(d.lines[0]).ordinal===2,'later inert call keeps token, missing ordinal stays observable');
}
const bad=fixture();bad.bindings.fill=()=>new Uint8Array(16);
refuses(()=>observe('GET','http://fixture.test/api/cache',bad.bindings),'nonidentical fill return refuses');
check(!Object.hasOwn(bad.target,slot),'invalid entropy result not published');
for(const ordinal of [-1,0.5,NaN,Number.MAX_SAFE_INTEGER]) {
  const c=fixture();observe('GET','http://fixture.test/fixture.txt',c.bindings);c.state.ordinal=ordinal;
  refuses(()=>observe('GET','http://fixture.test/api/cache',c.bindings),'invalid/overflow ordinal refuses');
  check(c.lines.length===0,'invalid ordinal creates no misleading log');
}
const helper=readFileSync(join(here,'cache-affinity.mjs'),'utf8');
const entry=readFileSync(join(here,'guest-entry.mjs'),'utf8');
const base=readFileSync(join(here,'../next-component-entry-fixes-v5/guest-entry.mjs'),'utf8');
const declaration=helper.replace('export function ','function ')+'\n';
const call='      recordCacheAffinityAdmission(method,url);\n';
check(entry.split(call).length===2&&entry.split(declaration).length===2,'exact one private helper and two-argument call');
check(entry.replace(declaration,'').replace(call,'')===base,'complete original entry restored byte-for-byte after removing only diagnostic additions');
const needle="      request=new Request(url,{method,headers,signal:ioAbort.signal,...(body?{body,duplex:'half'}:{})});\n";
check(entry.includes(needle+call+'      const response=await webHandler(request);'),'call after real Request and before unmodified app dispatch');
check(!Object.hasOwn(globalThis,slot),'tests never call genuine global RNG/default branch');
console.log(JSON.stringify({sourceOnly:true,inertChecks:checks,ordinaryFillCallbacksOnly:true,actualEntropyInvoked:false,rawEntryEvaluated:false,wasiResourcesOrActorInvoked:false,guestOrHeapAffinityProven:false}));
