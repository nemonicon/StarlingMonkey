// Real Node22 differential for the facade. The JS kernel below is TEST ONLY;
// it does not validate the uncompiled C++ memcpy/GC implementation.
import assert from 'node:assert/strict';
import {Buffer as NodeBuffer} from 'node:buffer';
import {createBufferModule} from './native/builtins/node-compat/buffer-facade.mjs';
import {createBufferModule as beforeModule} from '../../../builtins/node-compat/buffer-facade.mjs';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';
assert.equal(process.version,'v22.14.0');
const MAX=16777216;let kernelCalls=0;
const set=Function.prototype.call.bind(Uint8Array.prototype.set);
const kernel={
 hexDecode:s=>new Uint8Array(NodeBuffer.from(s,'hex')),
 hexEncode:b=>NodeBuffer.from(b).toString('hex'),
 concat(list,length){kernelCalls++;const out=new Uint8Array(length);let pos=0;for(const value of list){const n=Math.min(value.byteLength,length-pos);if(n)set(out,value.subarray(0,n),pos);pos+=n;}return out;}
};
const B=createBufferModule(kernel).Buffer,before=beforeModule(kernel).Buffer;
const cases=[];function test(name,fn){fn();cases.push({name,passed:true});}
function observe(C,run){try{return{status:'returned',value:run(C)};}catch(e){return{status:'threw',name:e.name,code:e.code??null};}}
function differential(name,run){const expected=observe(NodeBuffer,run),actual=observe(B,run);assert.deepEqual(actual,expected,name);cases.push({name,passed:true,node:expected,actual});}
const bytes=v=>Array.from(v);
for(const [name,run]of [
 ['empty ignores omitted length',C=>bytes(C.concat([]))],
 ['empty ignores positive length',C=>bytes(C.concat([],10))],
 ['empty ignores negative length',C=>bytes(C.concat([],-1))],
 ['empty ignores object length',C=>bytes(C.concat([],{}))],
 ['empty ignores BigInt length',C=>bytes(C.concat([],1n))],
 ['mixed buffers and Uint8Array',C=>bytes(C.concat([C.from(new Uint8Array([1,2])),new Uint8Array([3,4])]))],
 ['visible offset windows',C=>{const b=new Uint8Array([90,1,2,3,91]);return bytes(C.concat([b.subarray(1,3),b.subarray(3,4)]));}],
 ['repeated source views',C=>{const b=new Uint8Array([7,8]);return bytes(C.concat([b,b,b]));}],
 ['zero-length inputs',C=>bytes(C.concat([new Uint8Array(0),new Uint8Array([5]),new Uint8Array(0)]))],
 ['truncate inside first chunk',C=>bytes(C.concat([new Uint8Array([1,2,3]),new Uint8Array([4])],2))],
 ['truncate at boundary',C=>bytes(C.concat([new Uint8Array([1,2]),new Uint8Array([3,4])],2))],
 ['truncate inside second chunk',C=>bytes(C.concat([new Uint8Array([1,2]),new Uint8Array([3,4])],3))],
 ['zero fill requested tail',C=>bytes(C.concat([new Uint8Array([1,2]),new Uint8Array([3])],6))],
 ['zero total length still validates',C=>bytes(C.concat([new Uint8Array([1]),4],0))],
 ['copy independence both directions',C=>{const a=new Uint8Array([1,2]),b=new Uint8Array([3]);const out=C.concat([a,b]);a[0]=99;const old=bytes(out);out[1]=88;return{old,source:bytes(a),other:bytes(b)};}],
 ['Uint8 subclass visible bytes',C=>{class V extends Uint8Array{};return bytes(C.concat([new V([8,9])]))}],
 ['wrong list null',C=>C.concat(null)],['wrong list object',C=>C.concat({0:new Uint8Array([1]),length:1})],
 ['wrong list Uint8Array',C=>C.concat(new Uint8Array([1]))],
 ['invalid item number omitted',C=>C.concat([7])],['invalid item number explicit',C=>C.concat([7],0)],
 ['invalid item null omitted',C=>C.concat([null])],['invalid item undefined omitted',C=>C.concat([undefined])],
 ['invalid item null explicit',C=>C.concat([null],1)],['invalid item Uint16Array',C=>C.concat([new Uint16Array([7])])],
 ['invalid item DataView',C=>C.concat([new DataView(new ArrayBuffer(2))])],
 ...[-1,NaN,Infinity,-Infinity,1.5,'2',null,1n,{}].map((value,i)=>['invalid nonempty length '+i,C=>C.concat([new Uint8Array([1])],value)]),
 ['length negative zero',C=>bytes(C.concat([new Uint8Array([1])],-0))],
 ['concat function metadata',C=>({name:C.concat.name,length:C.concat.length,enumerable:Object.getOwnPropertyDescriptor(C,'concat').enumerable,writable:Object.getOwnPropertyDescriptor(C,'concat').writable,configurable:Object.getOwnPropertyDescriptor(C,'concat').configurable})],
 ['construction returns actual buffer',C=>{const result=new C.concat([new Uint8Array([4,5])]);return{bytes:bytes(result),buffer:C.isBuffer(result)};}]
])differential(name,run);
test('existing concat constructor slot/order preserved',()=>{assert.deepEqual(Reflect.ownKeys(B),Reflect.ownKeys(before));assert.equal(Reflect.ownKeys(B).indexOf('concat'),Reflect.ownKeys(before).indexOf('concat'));assert.throws(()=>before.concat([]),{code:'ERR_SM_NODE_UNSUPPORTED'});});
test('fresh exact zeroed backing/pool-independent',()=>{B.poolSize=8192;const a=B.concat([new Uint8Array([1])],5),b=B.concat([]);assert.equal(a.byteOffset,0);assert.equal(a.buffer.byteLength,5);assert.deepEqual(bytes(a),[1,0,0,0,0]);assert.notEqual(a.buffer,b.buffer);assert(B.isBuffer(a));});
test('16MiB output cap exact/over-cap refuses before kernel',()=>{const n=kernelCalls,out=B.concat([new Uint8Array([9])],MAX);assert.equal(out.length,MAX);assert.equal(out[0],9);assert.equal(out[MAX-1],0);assert.equal(kernelCalls,n+1);assert.throws(()=>B.concat([new Uint8Array(0)],MAX+1),{code:'ERR_OUT_OF_RANGE'});assert.equal(kernelCalls,n+1);});
test('omitted total sum checked before output allocation',()=>{const a=new Uint8Array(MAX),n=kernelCalls;assert.throws(()=>B.concat([a,new Uint8Array(1)]),{code:'ERR_OUT_OF_RANGE'});assert.equal(kernelCalls,n);});
test('chunk count bound before kernel',()=>{const n=kernelCalls;assert.throws(()=>B.concat(new Array(65537).fill(new Uint8Array(0))),{code:'ERR_SM_NODE_LIMIT'});assert.equal(kernelCalls,n);});
test('sparse/accessor inputs explicitly refuse without invoking getter',()=>{assert.throws(()=>B.concat(new Array(1)),{code:'ERR_SM_NODE_UNSUPPORTED'});let calls=0;const list=[];Object.defineProperty(list,0,{get(){calls++;return new Uint8Array([1]);}});assert.throws(()=>B.concat(list),{code:'ERR_SM_NODE_UNSUPPORTED'});assert.equal(calls,0);});
test('shadowed metadata explicitly refuses',()=>{const v=new Uint8Array([1]);Object.defineProperty(v,'length',{value:7});assert.throws(()=>B.concat([v]),{code:'ERR_SM_NODE_UNSUPPORTED'});});
test('shared backing explicitly refuses',()=>{if(typeof SharedArrayBuffer==='function')assert.throws(()=>B.concat([new Uint8Array(new SharedArrayBuffer(4))]),{code:'ERR_SM_NODE_UNSUPPORTED'});});
test('resizable backing explicitly refuses',()=>{const ab=new ArrayBuffer(4,{maxByteLength:8});assert.throws(()=>B.concat([new Uint8Array(ab)]),{code:'ERR_SM_NODE_UNSUPPORTED'});});
test('detached backing explicitly refuses',()=>{const ab=new ArrayBuffer(4),v=new Uint8Array(ab);structuredClone(ab,{transfer:[ab]});assert.throws(()=>B.concat([v]),{code:'ERR_SM_NODE_UNSUPPORTED'});});
test('captured kernel ignores user allocUnsafe replacement',()=>{B.allocUnsafe=()=>{throw new Error('not called');};assert.deepEqual(bytes(B.concat([new Uint8Array([6])])),[6]);});
test('existing factory regenerated with genuine core-only generator',()=>{const h=readFileSync(new URL('./native/builtins/node-compat/factories.generated.h',import.meta.url),'utf8');const marker='kBufferFactorySource[] = R"SM_NODE_PROFILE(';const source=h.slice(h.indexOf(marker)+marker.length,h.indexOf(')SM_NODE_PROFILE";',h.indexOf(marker)));const generated=vm.runInThisContext(source,{filename:'<actual-generated-buffer-factory>'})(kernel).Buffer;assert.deepEqual(bytes(generated.concat([new Uint8Array([1]),new Uint8Array([2])],4)),[1,2,0,0]);});
console.log(JSON.stringify({schemaVersion:1,state:'BUFFER_CONCAT_HOST_FACADE_DIFFERENTIAL_PASSED',checks:cases.length,cases,nativeKernelExecuted:false,kernelProvider:'TEST-ONLY JS typed-byte-copy model',nativeCppCompiled:false,guestExecuted:false}));
