// Node-host algorithm/reference-facade tests only. No native guest or component.
import assert from 'node:assert/strict';
import * as nativeStream from 'node:stream';
import * as nativePromises from 'node:stream/promises';
import * as nativeEvents from 'node:events';
import {StringDecoder} from 'node:string_decoder';
import {promisify} from 'node:util';
import {writeFile,readFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {createClassicStreams} from './classic-streams.mjs';
import {checks} from './checks.mjs';
import {createBufferModule} from '../../../../builtins/node-compat/buffer-facade.mjs';
import {createEventsFacade} from '../../../../builtins/node-compat/events.mjs';
import {createStringDecoderModule} from '../../../../builtins/node-compat/string-decoder.mjs';
import * as referenceKernel from '../../../../docs/node-compat/templates/reference-kernel.mjs';
assert.equal(process.version,'v22.14.0');assert.deepEqual(process.execArgv,[]);assert(!process.env.NODE_OPTIONS);
const scheduler=process.nextTick;
function dependencies(Buffer,events,Decoder){return{Buffer,events,StringDecoder:Decoder,nextTick:scheduler,AbortSignal,AbortController,disposeSymbol:Symbol.dispose,asyncDisposeSymbol:Symbol.asyncDispose}}
const expected=await checks(nativeStream,nativePromises,Buffer);
const host=createClassicStreams(dependencies(Buffer,nativeEvents,StringDecoder));
const observed=await checks(host.root,host.promises,Buffer);
assert.deepEqual(observed,expected);
const boundedBuffer=createBufferModule(referenceKernel).Buffer;
const boundedEvents=createEventsFacade(Symbol('host-only-not-native-resistance-key'));
const boundedDecoder=createStringDecoderModule(boundedBuffer).StringDecoder;
const reference=createClassicStreams(dependencies(boundedBuffer,boundedEvents,boundedDecoder));
const referenceObserved=await checks(reference.root,reference.promises,boundedBuffer);
assert.deepEqual(referenceObserved,expected);
assert.deepEqual(Object.keys(host.root).sort(),Object.keys(nativeStream).sort());
assert.deepEqual(Object.keys(host.promises).sort(),Object.keys(nativePromises).sort());
assert.equal(host.root.Stream.prototype instanceof nativeEvents.EventEmitter,true);
assert.equal(reference.root.Stream.prototype instanceof boundedEvents.EventEmitter,true);
assert.equal(host.root.pipeline[promisify.custom],host.promises.pipeline);
assert.equal(host.root.finished[promisify.custom],host.promises.finished);
assert.equal(host.root.then,undefined);assert.equal(host.promises.then,undefined);
assert.equal(host.root.Readable.prototype.asIndexedPairs,undefined);
const unsupported=[];
const operations=[['compose',host.root.compose],['duplexPair',host.root.duplexPair],
 ...['Readable','Writable','Duplex'].flatMap(name=>['fromWeb','toWeb'].map(method=>[name+'.'+method,host.root[name][method]])),
 ['Duplex.from',host.root.Duplex.from],...['compose','map','filter','forEach','toArray','some','find','every','flatMap','drop','take','reduce','iterator'].map(name=>['Readable.prototype.'+name,host.root.Readable.prototype[name]]),
 ...['Readable','Writable'].map(name=>[name+'.prototype[Symbol.asyncDispose]',host.root[name].prototype[Symbol.asyncDispose]])];
for(const [operation,fn]of operations)for(const construct of[false,true]){let error;try{if(construct)new fn();else fn()}catch(caught){error=caught}
 assert.equal(error?.code,'ERR_SM_NODE_UNSUPPORTED');assert.equal(error.operation,operation);assert.equal(error.module,'node:stream');assert.equal(error.profile,'sm-node-22.14.0-m0.12');
 for(const key of['code','module','operation','profile'])assert(Object.hasOwn(error,key));unsupported.push({operation,construct,code:error.code});}
const limited=new reference.root.Writable({objectMode:true,write(x,e,cb){cb()}});limited.cork();for(let i=0;i<4096;i++)limited.write(i);
assert.throws(()=>limited.write(4096),error=>error.code==='ERR_SM_NODE_STREAM_LIMIT');limited.on('error',()=>{});limited.destroy();
const output=process.env.NODE_COMPAT_CLASSIC_HOST_OUTPUT??new URL('./node-results.json',import.meta.url);
const hash=b=>createHash('sha256').update(b).digest('hex');
await writeFile(output,JSON.stringify({state:'UNAPPLIED_CLASSIC_JS_HOST_ALGORITHMS_PASSED',node:process.version,
 nodeExecutableSha256:hash(await readFile(process.execPath)),groups:expected.length,expected,hostDependencies:observed,productionFacadesReferenceKernel:referenceObserved,
 unsupportedChecks:unsupported,rootExports:Object.keys(host.root).sort(),promiseExports:Object.keys(host.promises).sort(),
 namespaceGraphs:true,sharedEventEmitterIdentity:true,logicalWritableChunkLimit:true,
 nativeKernelExecuted:false,privateGuestSchedulerExecuted:false,protectedNativeAbortResistanceTested:false,componentOrHostRuntimeExecuted:false,
 limits:'Pure Node reference scheduling and a JS reference hex kernel are not native guest or component evidence. Abort checks have no stopImmediatePropagation listener.'},null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({groups:expected.length,arms:2,unsupportedChecks:unsupported.length,output:String(output),nativeGuest:false}));
