// Real generated wrapper / C++ flags0 DATA-shape regression; host only.
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {Readable} from 'node:stream';
import {Buffer} from 'node:buffer';
import vm from 'node:vm';
assert.equal(process.version,'v22.14.0');
function factory(text,filename){
  const open='kFsFactorySource[] = R"SM_NODE_PROFILE(',close=')SM_NODE_PROFILE";';
  assert.equal(text.split(open).length,2);const begin=text.indexOf(open)+open.length,end=text.indexOf(close,begin);assert(end>begin);
  return vm.runInThisContext(text.slice(begin,end),{filename});
}
const oldText=await readFile(new URL('../next-fs-candidate-v3/after/builtins/node-compat/fs-factories.generated.h',import.meta.url),'utf8');
const newText=await readFile(new URL('./after/builtins/node-compat/fs-factories.generated.h',import.meta.url),'utf8');
const oldFactory=factory(oldText,'<preserved-generated-FS-factory>'),newFactory=factory(newText,'<corrected-generated-FS-factory>');
let phaseCalls=0,readCalls=0;const ticks=[],expected=Uint8Array.of(1,2,3),kernel={
  checkPhase(){assert.equal(this,kernel);phaseCalls++;},
  readFile(path){assert.equal(this,kernel);assert.equal(path,'/fixture');readCalls++;return {buffer:expected.buffer,byteOffset:0,byteLength:3};},
};
const nextTick=(...args)=>{ticks.push(args);};
const values={kernel,Buffer,Readable,nextTick},dependencies={};
// JS_DefineProperty(...,flags0): non-enumerable, writable/configurable DATA.
for(const [key,value]of Object.entries(values))Object.defineProperty(dependencies,key,{value,enumerable:false,writable:true,configurable:true});
const before=Object.getOwnPropertyDescriptors(dependencies),cases=[];
function test(name,fn){fn();cases.push({name,passed:true});}
test('actual native-shaped four DATA fields are non-enumerable',()=>{assert.deepEqual(Object.keys(dependencies),[]);assert.deepEqual(Reflect.ownKeys(dependencies),['kernel','Buffer','Readable','nextTick']);for(const d of Object.values(before)){assert.equal(d.enumerable,false);assert.equal(d.writable,true);assert.equal(d.configurable,true);}});
let oldError;
test('preserved actual generated spread wrapper fails class heritage before kernel IO',()=>{
  assert.throws(()=>oldFactory(dependencies),e=>{oldError={name:e.name,message:e.message,stack:e.stack};return e instanceof TypeError&&/Class extends value undefined/.test(e.message);});
  assert.equal(phaseCalls,0);assert.equal(readCalls,0);assert.equal(ticks.length,0);
});
let graph;
test('actual corrected generated wrapper constructs without kernel IO',()=>{graph=newFactory(dependencies);assert.equal(phaseCalls,0);assert.equal(readCalls,0);assert.equal(ticks.length,0);});
test('genuine supplied Readable identity and aliases are retained',()=>{assert.equal(Object.getPrototypeOf(graph.root.ReadStream),Readable);assert.equal(Object.getPrototypeOf(graph.root.ReadStream.prototype),Readable.prototype);assert.equal(graph.root.FileReadStream,graph.root.ReadStream);assert.equal(graph.root.default.ReadStream,graph.root.ReadStream);});
test('supplied kernel and Buffer are used with exact returned owned window',()=>{const b=graph.root.readFileSync('/fixture');assert(Buffer.isBuffer(b));assert.equal(b.buffer,expected.buffer);assert.deepEqual([...b],[1,2,3]);assert.equal(phaseCalls,1);assert.equal(readCalls,1);});
test('supplied nextTick identity queues callback and then uses supplied kernel',()=>{let called=0;graph.root.readFile('/fixture','hex',(error,value)=>{assert.equal(error,null);assert.equal(value,'010203');called++;});assert.equal(called,0);assert.equal(ticks.length,1);const [fn,...args]=ticks.shift();fn(...args);assert.equal(called,1);assert.equal(readCalls,2);});
test('native-shaped dependency descriptors and identities remain unchanged',()=>assert.deepEqual(Object.getOwnPropertyDescriptors(dependencies),before));
test('finite transfer does not inspect/copy an unrelated enumerable getter',()=>{let reads=0;Object.defineProperty(dependencies,'unexpected',{enumerable:true,configurable:true,get(){reads++;throw Error('must not inspect');}});newFactory(dependencies);assert.equal(reads,0);delete dependencies.unexpected;});
test('missing actual Readable still refuses rather than using a host fallback',()=>{const missing=Object.defineProperties({},before);delete missing.Readable;assert.throws(()=>newFactory(missing),TypeError);});
console.log(JSON.stringify({schemaVersion:1,state:'FS_NATIVE_SHAPED_GENERATED_FACTORY_REGRESSION_PASSED_V1',passed:true,
  cases,oldError,oldGeneratedHeaderSha256:createHash('sha256').update(oldText).digest('hex'),newGeneratedHeaderSha256:createHash('sha256').update(newText).digest('hex'),
  hostOnly:true,cppOrNativeKernelExecuted:false,guestExecuted:false,limitations:['Host Node Buffer/Readable and a finite in-memory kernel contract; proves generated argument transfer, not SpiderMonkey/WASI execution.']}));
