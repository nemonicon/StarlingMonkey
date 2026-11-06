// TEST ONLY deterministic provider + actual Node22 API shape differentials.
// No guest/native provider, key, OpenSSL context or target entropy is invoked.
import assert from 'node:assert/strict';
import * as nodeCrypto from 'node:crypto';
import {Buffer as B} from 'node:buffer';
import {AsyncLocalStorage} from 'node:async_hooks';
import {createRandomOperations} from './after/builtins/node-compat/crypto-rng.mjs';
import {createCryptoModule} from './after/builtins/node-compat/crypto-facade.mjs';
assert.equal(process.version,'v22.14.0');
let deployed=false,draws=0,throwValue,shouldThrow=false;
const fail=()=>{const e=new Error('TEST ONLY not deployed');e.code='ERR_SM_ENTROPY_INITIALIZATION';throw e;};
const rng={check(){if(!deployed)fail();},bytes(n){this;draws++;if(shouldThrow)throw throwValue;return Uint8Array.from({length:n},(_,i)=>(i+11)&255);},fill(v,o,n){draws++;for(let i=0;i<n;i++)v[o+i]=(i+11)&255;return v;},uuid(){draws++;return'00112233-4455-4677-8899-aabbccddeeff';}};
const web={getRandomValues(v){draws++;return v;}};
const r=createRandomOperations({rng,Buffer:B,webcrypto:web,nextTick:process.nextTick});const cases=[];
function test(name,fn){fn();cases.push({name,passed:true});}
function shape(f){try{const v=f();return{type:typeof v,buffer:B.isBuffer(v),bytes:v?.byteLength,length:v?.length};}catch(e){return{threw:e.name,code:e.code??null};}}
function diff(name,run){const n=shape(()=>run(nodeCrypto)),v=shape(()=>run(r));assert.deepEqual(v,n,name);cases.push({name,passed:true,node:n});}
test('INIT guard before any draw',()=>{const n=draws;for(const f of[()=>r.randomBytes(0),()=>r.randomBytes(8),()=>r.randomUUID(),()=>r.randomFillSync(new Uint8Array(2)),()=>r.getRandomValues(new Uint8Array(2))])assert.throws(f,{code:'ERR_SM_ENTROPY_INITIALIZATION'});assert.equal(draws,n);});deployed=true;
for(const n of [0,1,8,16,32,64,1.5])diff('randomBytes shape '+n,c=>c.randomBytes(n));
for(const n of [-1,NaN,Infinity,'2',null,{},1n])diff('randomBytes invalid '+String(n),c=>c.randomBytes(n));
for(const cb of [3,{},null])diff('invalid callback '+String(cb),c=>c.randomBytes(2,cb));
for(const options of [undefined,{}, {disableEntropyCache:false},{disableEntropyCache:true},[],null,3,{disableEntropyCache:7}])diff('UUID options '+JSON.stringify(options),c=>c.randomUUID(options));
test('UUID option getter read once',()=>{let n=0;const options={get disableEntropyCache(){n++;return true;}};r.randomUUID(options);assert.equal(n,1);});
test('UUID canonical v4 format',()=>assert.match(r.randomUUID(),/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/));
for(const args of [[],[1],[1,2],[-1],[8],[0,99],[0,-1],[0,1.5]])diff('fill range '+JSON.stringify(args),c=>c.randomFillSync(new Uint8Array(6),...args));
test('fill visible offset window and same object',()=>{const whole=new Uint8Array(9).fill(90),v=whole.subarray(2,7);assert.equal(r.randomFillSync(v,1,2),v);assert.deepEqual([...whole],[90,90,90,11,12,90,90,90,90]);});
test('fill ArrayBuffer returns original',()=>{const ab=new ArrayBuffer(5);assert.equal(r.randomFillSync(ab,1,2),ab);assert.deepEqual([...new Uint8Array(ab)],[0,11,12,0,0]);});
test('bytes wrapped as genuine Buffer visible storage',()=>{const v=r.randomBytes(3);assert(B.isBuffer(v));assert.deepEqual([...v],[11,12,13]);assert.equal(v.byteOffset,0);});
test('shared/resizable/detached refused',()=>{assert.throws(()=>r.randomFillSync(new Uint8Array(new SharedArrayBuffer(2))),{code:'ERR_SM_NODE_UNSUPPORTED'});assert.throws(()=>r.randomFillSync(new Uint8Array(new ArrayBuffer(2,{maxByteLength:8}))),{code:'ERR_SM_NODE_UNSUPPORTED'});const a=new ArrayBuffer(2);structuredClone(a,{transfer:[a]});assert.throws(()=>r.randomFillSync(a),{code:'ERR_SM_NODE_UNSUPPORTED'});});
test('callback zero-size is synchronous Node behavior',()=>{let n=0;r.randomBytes(0,(e,b)=>{assert.equal(e,null);assert.equal(b.length,0);n++;});assert.equal(n,1);let expected=0;nodeCrypto.randomBytes(0,()=>expected++);assert.equal(expected,1);});
await new Promise((resolve,reject)=>{let sync=true;r.randomBytes(8,(e,b)=>{try{assert.equal(sync,false);assert.equal(e,null);assert.equal(b.length,8);cases.push({name:'nonzero callback queued',passed:true});resolve();}catch(x){reject(x);}});sync=false;});
const als=new AsyncLocalStorage();await new Promise((resolve,reject)=>{als.run('registration',()=>r.randomBytes(8,()=>{try{assert.equal(als.getStore(),'registration');cases.push({name:'TEST host nextTick retains registration ALS',passed:true});resolve();}catch(e){reject(e);}}));});
await new Promise((resolve,reject)=>{shouldThrow=true;throwValue=0;r.randomBytes(8,function(error){try{assert.equal(error,0);assert.equal(arguments.length,1);cases.push({name:'falsy provider error retained for callback',passed:true});resolve();}catch(e){reject(e);}});shouldThrow=false;});
test('web getRandomValues follows actual mutable webcrypto method',()=>{let n=0;const before=web.getRandomValues;web.getRandomValues=function(v){n++;return before.call(this,v);};const a=new Uint8Array(2);assert.equal(r.getRandomValues(a),a);assert.equal(n,1);web.getRandomValues=before;});
test('full crypto namespace/default + Next wrapper mutation',()=>{const m=createCryptoModule({kernel:{constants:{OPENSSL_VERSION_NUMBER:805306640}},rng,nextTick:process.nextTick,Buffer:B,webcrypto:web,subtle:{}});assert.deepEqual(Object.keys(m).sort(),Object.keys(nodeCrypto).sort());assert.equal(m.default.randomBytes,m.randomBytes);assert.equal(m.default.rng,m.randomBytes);const original=m.default.randomBytes;let n=0;m.default.randomBytes=function(...a){n++;return original(...a);};assert.equal(m.default.randomBytes(8).length,8);assert.equal(n,1);assert.equal(m.randomBytes,original);assert(Object.isFrozen(m));assert(!Object.isFrozen(m.default));assert.equal(typeof m.createHash,'function');assert.throws(()=>m.randomInt(),{code:'ERR_SM_NODE_UNSUPPORTED'});});
console.log(JSON.stringify({schemaVersion:1,checks:cases.length,cases,testOnlyDeterministicProvider:true,hostNodeCryptoAPIShapeObserved:true,nativeRngExecuted:false,guestExecuted:false,hostNodeRandomnessExecuted:true,targetCryptoProviderExecuted:false,keyOperationsExecuted:false}));
