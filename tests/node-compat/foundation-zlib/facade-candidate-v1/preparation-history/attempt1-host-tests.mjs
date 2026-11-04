// Host-only facade model. The private kernel below is Node's codec, not C++.
import assert from 'node:assert/strict';
import * as nodeZlib from 'node:zlib';
import {readFile,writeFile} from 'node:fs/promises';
import {createZlibModule} from './zlib-facade.generated.mjs';
assert.equal(process.version,'v22.14.0');
const inventory=JSON.parse(await readFile(new URL('../inventory.node-v22.14.0.json',import.meta.url)));
const names=inventory.exports.map(row=>row.name).sort();
const implemented=['deflateSync','inflateSync','gzipSync','gunzipSync','deflateRawSync','inflateRawSync'];
const encodeNames=['deflateSync','gzipSync','deflateRawSync'];
const decodeNames=['inflateSync','gunzipSync','inflateRawSync'];
const calls=[],checks=[];
function check(name,fn){fn();checks.push(name);}
function refusal(fn){assert.throws(fn,error=>error.code==='ERR_SM_NODE_UNSUPPORTED'&&error.module==='node:zlib');}
const kernel={run(input,format,encode,limit){
  assert(input instanceof Uint8Array);
  calls.push({input,format,encode,limit});
  return new Uint8Array(nodeZlib[(encode?encodeNames:decodeNames)[format]](input,{maxOutputLength:limit}));
}};
const api=createZlibModule(kernel,Buffer);
check('exact39named+default finite binding record',()=>assert.deepEqual(Object.keys(api).sort(),names));
check('default identities and deliberately frozen record',()=>{
  assert(Object.isFrozen(api)&&Object.isFrozen(api.default));
  for(const name of names)if(name!=='default')assert.equal(api.default[name],api[name]);
  assert.equal(api.then,undefined);assert.equal(api.default.then,undefined);
});
assert.equal(await Promise.resolve(api.default),api.default);
checks.push('safe Promise assimilation and namespace inspection');
for(const kind of ['constants','codes'])check('exact '+kind+' values/types/descriptors',()=>{
  assert.deepEqual(Object.keys(api[kind]).sort(),Object.keys(inventory[kind]).sort());
  assert(Object.isFrozen(api[kind]));
  for(const[name,row]of Object.entries(inventory[kind])){
    assert.equal(api[kind][name],row.value);assert.equal(typeof api[kind][name],row.type);
    const descriptor=Object.getOwnPropertyDescriptor(api[kind],name);
    for(const key of ['writable','enumerable','configurable'])assert.equal(descriptor[key],row[key]);
  }
});
check('deprecated default numeric constants remain meaningful and nonenumerable',()=>{
  for(const[name,row]of Object.entries(inventory.constants))if(!name.startsWith('BROTLI')){
    assert.equal(api.default[name],row.value);assert.equal(typeof api.default[name],'number');
    assert.equal(Object.getOwnPropertyDescriptor(api.default,name).enumerable,false);
  }
});
for(const row of inventory.exports)if(row.type==='function'&&!implemented.includes(row.name)){
  check('deferred call/new '+row.name,()=>{assert.equal(api[row.name].name,row.name);refusal(()=>api[row.name]());refusal(()=>new api[row.name]());});
}
for(const name of implemented)check('explicit sync-construction refusal '+name,()=>refusal(()=>new api[name](new Uint8Array())));
const cases=[new Uint8Array(),new Uint8Array([0,1,127,128,255]),new Uint8Array(65537).map((_,i)=>(i*31)&255)];
for(const input of cases)for(let format=0;format<3;format++){
  const encode=encodeNames[format],decode=decodeNames[format];
  check(encode+'/'+decode+' value roundtrip '+input.length,()=>{
    const compressed=api[encode](input);
    assert(Buffer.isBuffer(compressed));
    assert.deepEqual(nodeZlib[decode](compressed),Buffer.from(input));
    assert.deepEqual(api[decode](nodeZlib[encode](input)),Buffer.from(input));
    assert.deepEqual(api[decode](compressed),Buffer.from(input));
    assert.equal(compressed.buffer,calls.at(-3).input.buffer===compressed.buffer?null:compressed.buffer);
  });
}
check('typed/DataView/ArrayBuffer byte windows use bytes rather than elements',()=>{
  const backing=new ArrayBuffer(20);new Uint8Array(backing).set([9,8,7,6,5,4,3,2],4);
  for(const input of [new Uint16Array(backing,4,4),new DataView(backing,4,8),new Uint8Array(backing,4,8),backing]){
    const expected=ArrayBuffer.isView(input)?new Uint8Array(input.buffer,input.byteOffset,input.byteLength):new Uint8Array(input);
    assert.deepEqual(nodeZlib.gunzipSync(api.gzipSync(input)),Buffer.from(expected));
  }
});
check('private result backing shared into Buffer without a second facade copy',()=>{
  const result=new Uint8Array(new ArrayBuffer(12),3,5);result.set([1,2,3,4,5]);
  const module=createZlibModule({run(){return result;}},Buffer);
  const output=module.gzipSync(new Uint8Array());
  assert(Buffer.isBuffer(output));assert.equal(output.buffer,result.buffer);
  assert.equal(output.byteOffset,3);assert.equal(output.byteLength,5);
  result[2]=42;assert.equal(output[2],42);
});
check('native staging contract preserves input until private run returns',()=>{
  const backing=new ArrayBuffer(24),input=new Uint8Array(backing,5,7);
  const module=createZlibModule({run(view,format,encode,limit){
    assert.equal(view.buffer,backing);assert.equal(view.byteOffset,5);assert.equal(view.byteLength,7);
    assert.equal(format,1);assert.equal(encode,true);assert.equal(limit,100);return new Uint8Array();
  }},Buffer);
  assert.equal(module.gzipSync(input,{maxOutputLength:100}).byteLength,0);
});
for(const value of [null,1,[],{},true])check('invalid input '+String(value),()=>{
  assert.throws(()=>api.gzipSync(value),error=>error instanceof TypeError&&error.code==='ERR_INVALID_ARG_TYPE');
  assert.throws(()=>nodeZlib.gzipSync(value),error=>error instanceof TypeError&&error.code==='ERR_INVALID_ARG_TYPE');
});
check('strings deliberately deferred',()=>refusal(()=>api.gzipSync('abc')));
check('input over cap refused before kernel',()=>{
  const count=calls.length;assert.throws(()=>api.gzipSync(new Uint8Array(1048577)),error=>error.code==='ERR_OUT_OF_RANGE');assert.equal(calls.length,count);
});
check('full1MiB input accepted by source facade',()=>assert(Buffer.isBuffer(api.gzipSync(new Uint8Array(1048576)))));
for(const value of [0,-1,1.5,NaN,Infinity,16777217])check('output range refusal '+value,()=>assert.throws(()=>api.gzipSync(cases[1],{maxOutputLength:value}),error=>error instanceof RangeError&&error.code==='ERR_OUT_OF_RANGE'));
check('output cap passed to model kernel',()=>assert.throws(()=>api.gzipSync(cases[1],{maxOutputLength:1}),error=>error.code==='ERR_BUFFER_TOO_LARGE'));
for(const option of [{level:-1},{dictionary:undefined},{info:false},{[Symbol('x')]:1}])check('unadmitted own option '+String(Reflect.ownKeys(option)[0]),()=>refusal(()=>api.gzipSync(cases[1],option)));
check('accessor options refused without invoking accessor',()=>{
  let reads=0;refusal(()=>api.gzipSync(cases[1],{get maxOutputLength(){reads++;return 10;}}));assert.equal(reads,0);
});
check('nonordinary options explicitly deferred',()=>refusal(()=>api.gzipSync(cases[1],Object.create({maxOutputLength:10}))));
check('null-prototype data options admitted',()=>assert(Buffer.isBuffer(api.gzipSync(cases[1],Object.assign(Object.create(null),{maxOutputLength:100})))));
check('shared input/backing explicitly deferred',()=>{
  const buffer=new SharedArrayBuffer(8);refusal(()=>api.gzipSync(buffer));refusal(()=>api.gzipSync(new Uint8Array(buffer)));refusal(()=>api.gzipSync(new DataView(buffer)));
});
check('resizable input/backing explicitly deferred',()=>{
  const buffer=new ArrayBuffer(8,{maxByteLength:16});refusal(()=>api.gzipSync(buffer));refusal(()=>api.gzipSync(new Uint8Array(buffer)));
});
check('detached input/backing explicitly deferred in host facade only',()=>{
  const buffer=new ArrayBuffer(8),view=new Uint8Array(buffer);structuredClone(buffer,{transfer:[buffer]});
  refusal(()=>api.gzipSync(buffer));refusal(()=>api.gzipSync(view));
});
const result={schemaVersion:1,state:'HOST_ONLY_FACADE_NODE_CODEC_MODEL_PASSED',node:process.version,
  checks:checks.length,passed:checks.length,observations:checks,privateKernel:'Node22 stand-in; C++ template not invoked',
  nativeGuestPerformed:false,componentPerformed:false,cppCompiled:false,newPerformanceEvidence:false};
await writeFile(new URL('./host-results.json',import.meta.url),JSON.stringify(result,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({state:result.state,checks:checks.length,guestPerformed:false}));
