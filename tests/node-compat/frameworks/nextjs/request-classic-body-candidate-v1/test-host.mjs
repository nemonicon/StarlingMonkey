// HOST ONLY. Actual selected classic JS + ToWeb; TEST host byte kernel/Node Web APIs.
// SMBodyContract below is a named Source-contract model, never native proof.
import assert from 'node:assert/strict';
import {Readable as NodeReadable} from 'node:stream';
import {createBufferModule} from '/private/tmp/starling-node-compat/next-native-intl-build-v1/native-source/builtins/node-compat/buffer-facade.mjs';
import {createEventsFacade} from '/private/tmp/starling-node-compat/next-native-intl-build-v1/native-source/builtins/node-compat/events.mjs';
import {createStringDecoderModule} from '/private/tmp/starling-node-compat/next-native-intl-build-v1/native-source/builtins/node-compat/string-decoder.mjs';
import {createClassicStreams} from '/private/tmp/starling-node-compat/next-native-intl-build-v1/native-source/builtins/node-compat/classic-streams/classic-streams.mjs';
import {hostKernel} from '../../../buffer-next-candidate-v1/host-kernel.mjs';
import {installReadableToWeb} from '../../../foundation-classic-streams/readable-toweb-candidate-v1/readable-toweb.mjs';
import {POST} from '../app-fixture/app/api/json/route.js';
import {installClassicRequestBody} from './request-classic-body.mjs';
assert.equal(process.version,'v22.14.0');
const NativeRequest=globalThis.Request,prototypeConstructor=Object.getOwnPropertyDescriptor(NativeRequest.prototype,'constructor');
const ByteBuffer=createBufferModule(hostKernel).Buffer,events=createEventsFacade(Symbol('TEST abort'));
const decoder=createStringDecoderModule(ByteBuffer);
const graph=createClassicStreams({Buffer:ByteBuffer,events,StringDecoder:decoder.StringDecoder,nextTick:process.nextTick,AbortSignal,AbortController,disposeSymbol:Symbol.dispose,asyncDisposeSymbol:Symbol.asyncDispose});
installReadableToWeb(graph,ReadableStream);
const Readable=graph.root.Readable,enc=new TextEncoder(),rows=[];
const source=(R,chunks,extra={})=>{let i=0;return new R({objectMode:false,...extra,read(){this.push(i<chunks.length?chunks[i++]:null);}});};
const tick=()=>new Promise(r=>setImmediate(r));
function SMBodyContract(){throw Error('construct only');}
// Actual C++ extract_body does not recognize async iterables and encodes other
// objects as strings. This model limits that rule to our known classic body.
SMBodyContract=new Proxy(NativeRequest,{construct(native,args,newTarget){
 const [input,init]=args;
 const view=init&&typeof init==='object'?new Proxy(Object.create(null),{get(_t,k){const v=Reflect.get(init,k,init);return k==='body'&&v instanceof Readable?String(v):v;}}):init;
 return Reflect.construct(native,args.length<2?args:[input,view],newTarget);
}});
const world={Request:SMBodyContract,ReadableStream,Promise};
const bodyInit=body=>({method:'POST',body,duplex:'half',headers:{'content-type':'application/json'}});
const responseData=async request=>{const r=await POST(request);return {status:r.status,json:await r.json()};};
async function test(name,fn){await fn();rows.push({name,passed:true});}
let installed;
const timer=setTimeout(()=>{console.error('Host Request differential timed out');process.exit(1);},15000);
try{
 await test('unfixed Source-contract model reproduces JSON_BAD_INPUT',async()=>{const r=new SMBodyContract('http://fixture/api/json',bodyInit(source(Readable,[enc.encode('{"value":"posted"}')])));assert.equal(await r.text(),'[object Object]');const q=new SMBodyContract('http://fixture/api/json',bodyInit(source(Readable,[enc.encode('{"value":"posted"}')])));assert.deepEqual(await responseData(q),{status:400,json:{marker:'NEXT_JSON_BAD_INPUT'}});});
 installed=installClassicRequestBody(Readable,world);
 await test('constructor name/length/prototype/own descriptors preserved',()=>{assert.equal(world.Request.name,NativeRequest.name);assert.equal(world.Request.length,NativeRequest.length);assert.equal(world.Request.prototype,NativeRequest.prototype);assert.deepEqual(Reflect.ownKeys(world.Request),Reflect.ownKeys(NativeRequest));assert.equal(world.Request.prototype.constructor,world.Request);assert.equal(Object.hasOwn(world.Request,'then'),false);assert.throws(()=>world.Request('http://fixture'),TypeError);});
 for(const value of ['posted','€é😀',''])await test('actual fixture POST Node differential '+JSON.stringify(value),async()=>{const bytes=enc.encode(JSON.stringify({value}));const expected=await responseData(new NativeRequest('http://fixture/api/json',bodyInit(source(NodeReadable,[bytes]))));const actual=await responseData(new world.Request('http://fixture/api/json',bodyInit(source(Readable,[bytes]))));assert.deepEqual(actual,expected);assert.equal(actual.status,200);assert.equal(actual.json.value,value);});
 await test('split UTF8 and nonzero visible window',async()=>{const bytes=enc.encode('{"value":"€"}'),window=new Uint8Array(bytes.length+2);window.set(bytes,1);const chunks=[window.subarray(1,12),window.subarray(12,14),window.subarray(14,bytes.length+1)];const q=new world.Request('http://fixture/api/json',bodyInit(source(Readable,chunks)));assert.equal((await responseData(q)).json.value,'€');});
 await test('invalid JSON remains fixture400',async()=>{const q=new world.Request('http://fixture/api/json',bodyInit(source(Readable,[enc.encode('{bad')])));assert.deepEqual(await responseData(q),{status:400,json:{marker:'NEXT_JSON_BAD_INPUT'}});});
 await test('plain string body delegates',async()=>{const q=new world.Request('http://fixture/api/json',bodyInit('{"value":"string"}'));assert.equal((await responseData(q)).json.value,'string');});
 await test('typed array body delegates',async()=>{const q=new world.Request('http://fixture/api/json',bodyInit(enc.encode('{"value":"bytes"}')));assert.equal((await responseData(q)).json.value,'bytes');});
 await test('native Web ReadableStream body delegates',async()=>{const body=new ReadableStream({start(c){c.enqueue(enc.encode('{"value":"web"}'));c.close();}});const q=new world.Request('http://fixture/api/json',bodyInit(body));assert.equal((await responseData(q)).json.value,'web');});
 await test('native clone keeps public instance and constructor identity',async()=>{const q=new world.Request('http://fixture/api/json',bodyInit(source(Readable,[enc.encode('clone')]))),clone=q.clone();assert(q instanceof world.Request);assert(clone instanceof world.Request);assert.equal(clone.constructor,world.Request);assert.deepEqual(await Promise.all([q.text(),clone.text()]),['clone','clone']);});
 await test('NextRequest-like subclass preserves new.target/prototype',async()=>{class NextRequest extends world.Request{constructor(input,init){super(input,init);this.marker=1;}}const q=new NextRequest('http://fixture/api/json',bodyInit(source(Readable,[enc.encode('subclass')])));assert(q instanceof NextRequest);assert(q instanceof world.Request);assert.equal(Object.getPrototypeOf(q),NextRequest.prototype);assert.equal(q.marker,1);assert.equal(await q.text(),'subclass');});
 await test('frozen nonconfigurable init body does not violate Proxy invariants',async()=>{const init=Object.freeze(bodyInit(source(Readable,[enc.encode('frozen')])));assert.equal(await new world.Request('http://fixture',init).text(),'frozen');});
 await test('nonenumerable inherited init fields preserved',async()=>{const init=Object.create({method:'POST',duplex:'half'});Object.defineProperty(init,'body',{value:source(Readable,[enc.encode('inherited')])});assert.equal(await new world.Request('http://fixture',init).text(),'inherited');});
 await test('body getter receiver and read once',async()=>{let reads=0;const original=bodyInit(undefined),body=source(Readable,[enc.encode('getter')]);Object.defineProperty(original,'body',{get(){assert.equal(this,original);reads++;return body;}});assert.equal(await new world.Request('http://fixture',original).text(),'getter');assert.equal(reads,1);});
 await test('primitive0 getter exception retains identity before stream acquisition',()=>{let caught=false;try{new world.Request('http://fixture',{method:'POST',get body(){throw 0;}});}catch(e){caught=true;assert.equal(e,0);}assert(caught);});
 await test('getter order follows underlying constructor with same receivers',()=>{function init(log,body){const o={};for(const [key,value]of Object.entries({method:'POST',headers:{},body,signal:undefined,duplex:'half'}))Object.defineProperty(o,key,{get(){assert.equal(this,o);log.push(key);return value;}});return o;}const expected=[],actual=[];new NativeRequest('http://fixture',init(expected,'literal'));new world.Request('http://fixture',init(actual,'literal'));assert.deepEqual(actual,expected);});
 await test('native constructor refusal retires toWeb owner',async()=>{let destroyed=0;const r=source(Readable,[],{destroy(e,cb){destroyed++;cb();}});assert.throws(()=>new world.Request('http://fixture',{method:'GET',body:r,duplex:'half'}),TypeError);await tick();assert.equal(destroyed,1);assert(r.destroyed);assert.equal(r.listenerCount('data'),0);assert.equal(r.listenerCount('end'),0);});
 await test('body cancellation preserves reason and destroys once',async()=>{let count=0,matched=false;const marker={cancel:true},r=new Readable({read(){},destroy(e,cb){count++;matched=e===marker;cb();}}),q=new world.Request('http://fixture',bodyInit(r));await q.body.cancel(marker);await tick();assert.equal(count,1);assert(matched);assert(r.destroyed);});
 await test('source stream error reaches Request.text unchanged',async()=>{const marker=Error('stream marker'),r=new Readable({read(){}}),q=new world.Request('http://fixture',bodyInit(r));const pending=q.text();r.destroy(marker);await assert.rejects(pending,e=>e===marker);});
 await test('generic async iterable remains outside selected conversion',async()=>{const body={async *[Symbol.asyncIterator](){yield enc.encode('generic');}};let calls=0;const Fake=new Proxy(NativeRequest,{construct(n,args,target){calls++;assert.equal(args[1].body,body);return Reflect.construct(n,args,target);}}),w={Request:Fake,ReadableStream,Promise},lease=installClassicRequestBody(Readable,w);try{assert.equal(await new w.Request('http://fixture',bodyInit(body)).text(),'generic');assert.equal(calls,1);}finally{lease.restore();}});
 installed.restore();installed=null;
 await test('restoration and no global Request constructor patch',()=>{assert.equal(globalThis.Request,NativeRequest);assert.deepEqual(Object.getOwnPropertyDescriptor(NativeRequest.prototype,'constructor'),prototypeConstructor);assert.equal(world.Request,SMBodyContract);});
 console.log(JSON.stringify({schemaVersion:1,node:process.version,cases:rows.length,passed:rows.length,rows,actualGuestExecuted:false,nativeRequestImplemented:false,testUsesActualSelectedClassicJs:true,testUsesHostByteKernelAndWebStreams:true,smBodyContractIsSourceModel:true,actualFailingGuestTextObserved:false}));
}finally{clearTimeout(timer);installed?.restore();Object.defineProperty(NativeRequest.prototype,'constructor',prototypeConstructor);}
