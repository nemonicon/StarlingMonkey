// Ordinary host tests for canonical m0.4 source. No old-native decoder calls,
// raw-memory observers, fault injection or production registry are involved.
import assert from 'node:assert/strict';
import {Buffer as NodeBuffer} from 'node:buffer';
import {readFile,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import vm from 'node:vm';
import {createStringDecoderModule} from '../../../builtins/node-compat/string-decoder.mjs';
import {createBufferModule} from '../../../builtins/node-compat/buffer-facade.mjs';
import * as referenceKernel from '../../../docs/node-compat/templates/reference-kernel.mjs';
assert.equal(process.version,'v22.14.0');
const corpus=JSON.parse(await readFile(new URL('./component-corpus.json',import.meta.url)));
const profileBuffer=createBufferModule(referenceKernel).Buffer;
const results=[];
function state(decoder){return {need:decoder.lastNeed,total:decoder.lastTotal,char:[...decoder.lastChar]};}
for(const [dependency,Buffer]of [['Node22 Buffer',NodeBuffer],['M0 Buffer facade with JS reference kernel',profileBuffer]]){
  const module=createStringDecoderModule(Buffer),StringDecoder=module.StringDecoder;
  assert.deepEqual(Object.keys(module),['StringDecoder','default']);
  assert.deepEqual(Object.keys(module.default),['StringDecoder']);
  assert.equal(module.default.StringDecoder,StringDecoder);
  assert.equal(StringDecoder.name,'StringDecoder');assert.equal(StringDecoder.length,1);
  let sequences=0,writes=0;
  for(const vector of corpus.sequences){
    const decoder=new StringDecoder(vector.encoding);
    for(let index=0;index<vector.chunks.length;index++){
      const bytes=Uint8Array.from(vector.chunks[index]);
      assert.deepEqual({output:decoder.write(index%2?new DataView(bytes.buffer):bytes),state:state(decoder)},vector.expected[index]);writes++;
    }
    assert.deepEqual({output:decoder.end(),state:state(decoder)},vector.end);
    assert.equal(decoder.end(Uint8Array.of(97)),vector.encoding==='hex'?'61':'a');sequences++;
  }
  for(const label of ['ascii','latin1','binary','base64','base64url','utf16le','utf-16le','ucs2','ucs-2']){
    assert.throws(()=>new StringDecoder(label),error=>error.code==='ERR_SM_NODE_UNSUPPORTED'&&error.profile==='sm-node-22.14.0-m0.4');
  }
  const typed=Object.getPrototypeOf(Uint8Array.prototype),length=Object.getOwnPropertyDescriptor(typed,'length');
  const originals={Error:globalThis.Error,TypeError:globalThis.TypeError,RangeError:globalThis.RangeError,
    weakGet:WeakMap.prototype.get,weakSet:WeakMap.prototype.set,alloc:Buffer.alloc,from:Buffer.from,
    toString:Buffer.prototype.toString,subarray:Buffer.prototype.subarray};
  let replacedCalls=0;
  const replaced=()=>{replacedCalls++;throw new originals.Error('replaced intrinsic');};
  try{
    // The selected M0 Buffer dependency captures byte-length access. Node's
    // Buffer control has its own mutable .length lookups and is not the
    // dependency whose intrinsic-isolation contract this facade can promise.
    if(Buffer===profileBuffer)Object.defineProperty(typed,'length',{get:replaced,configurable:true});
    globalThis.Error=globalThis.TypeError=globalThis.RangeError=replaced;
    WeakMap.prototype.get=WeakMap.prototype.set=replaced;
    Buffer.alloc=Buffer.from=Buffer.prototype.toString=Buffer.prototype.subarray=replaced;
    const decoder=new StringDecoder();
    assert.equal(decoder.write(Uint8Array.of(0xe2)), '');
    assert.equal(decoder.write(Uint8Array.of(0x82,0xac)), '€');
    assert.equal(decoder.lastNeed,0);
    assert.equal(decoder.lastChar.byteLength,4);
    assert.throws(()=>new StringDecoder('ascii'),error=>error.code==='ERR_SM_NODE_UNSUPPORTED'&&error instanceof originals.Error);
    assert.throws(()=>new StringDecoder('rot13'),error=>error.code==='ERR_UNKNOWN_ENCODING'&&error instanceof originals.TypeError);
  }finally{
    Object.defineProperty(typed,'length',length);
    globalThis.Error=originals.Error;globalThis.TypeError=originals.TypeError;globalThis.RangeError=originals.RangeError;
    WeakMap.prototype.get=originals.weakGet;WeakMap.prototype.set=originals.weakSet;
    Buffer.alloc=originals.alloc;Buffer.from=originals.from;
    Buffer.prototype.toString=originals.toString;Buffer.prototype.subarray=originals.subarray;
  }
  assert.equal(replacedCalls,0);
  const detached=new StringDecoder();
  detached.lastChar.buffer.transfer();
  for(const action of [()=>detached.lastChar,()=>detached.lastNeed,()=>detached.lastTotal,()=>detached.write(Uint8Array.of(97)),()=>detached.end()]){
    assert.throws(action,error=>error.code==='ERR_SM_NODE_DECODER_STATE'&&error instanceof TypeError);
  }
  const invalid=new StringDecoder();invalid[Object.getOwnPropertySymbols(invalid)[0]][4]=5;
  assert.throws(()=>invalid.end(),error=>error.code==='ERR_SM_NODE_DECODER_STATE');
  results.push({dependency,sequences,writes,primordialReplacementCalls:replacedCalls,detachedInternalStateChecks:5});
}
const source=await readFile(new URL('../../../builtins/node-compat/string-decoder.mjs',import.meta.url));
const header=await readFile(new URL('../../../builtins/node-compat/string-decoder-factories.generated.h',import.meta.url),'utf8');
const literal=header.match(/R"SM_NODE_PROFILE\(([\s\S]*)\)SM_NODE_PROFILE";/)?.[1];
assert(literal,'Generated factory literal');
const context=vm.createContext({});
// Match native evaluate_factory's CompileOptions::setForceStrictMode(). The
// literal is unchanged; canonical ESM source semantics require strict script.
const factory=vm.runInContext('"use strict";\n'+literal,context);
const generated=factory(NodeBuffer),Ctor=generated.StringDecoder;
const keysBefore=Reflect.ownKeys(context);
assert.throws(()=>Ctor(),error=>error.name==='TypeError');
const write=Ctor.prototype.write,end=Ctor.prototype.end,text=Ctor.prototype.text;
assert.equal(write('literal'),'literal');
for(const action of [()=>write(Uint8Array.of(97)),()=>end(),()=>text(Uint8Array.of(97),0),
  ()=>Object.getOwnPropertyDescriptor(Ctor.prototype,'lastChar').get.call(undefined)]){
  assert.throws(action,error=>error.name==='TypeError');
}
assert.deepEqual(Reflect.ownKeys(context),keysBefore,'Plain calls must not initialize global encoding/state');
assert(!Object.hasOwn(context,'encoding'));
const helper=await readFile(new URL('../../../builtins/node-compat/register.cpp',import.meta.url));
assert(helper.toString().includes('options.setForceStrictMode();'),'Native helper must force canonical strict semantics');
const report={node:process.version,scope:'Host-only canonical source tests; no native integration claim',
  sourceSha256:createHash('sha256').update(source).digest('hex'),results,
  strictFactory:{headerSha256:createHash('sha256').update(header).digest('hex'),plainCallRejected:true,detachedMethodsRejected:4,noGlobalPollution:true,
    nativeHelper:{path:'builtins/node-compat/register.cpp',sha256:createHash('sha256').update(helper).digest('hex'),symbol:'CompileOptions::setForceStrictMode'}}};
await writeFile(new URL('./production-contract-results.json',import.meta.url),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report));
