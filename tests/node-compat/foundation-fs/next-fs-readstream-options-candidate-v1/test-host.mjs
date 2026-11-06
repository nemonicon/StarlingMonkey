import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {Buffer as NodeBuffer} from 'node:buffer';
import * as events from 'node:events';
import {StringDecoder} from 'node:string_decoder';
import {createFsModules} from './after/builtins/node-compat/fs-facade.mjs';
import {createFsModules as oldFactory} from '../next-fs-candidate-v3/after/builtins/node-compat/fs-facade.mjs';
import {createClassicStreams} from '../../../../builtins/node-compat/classic-streams/classic-streams.mjs';
import {createBufferModule} from '../../../../builtins/node-compat/buffer-facade.mjs';
import {hostProvider} from '../next-fs-candidate-v2/host-provider.mjs';
import {normalizeReadStreamOptions,installReadStreamOptionsFacade} from './readstream-options.mjs';
assert.equal(process.version,'v22.14.0');
const scratch=fs.mkdtempSync('/private/tmp/starling-fs-send-options-host-');fs.chmodSync(scratch,0o700);
const filename=path.join(scratch,'asset.txt'),data=NodeBuffer.from('hello café\n'.repeat(3000));fs.writeFileSync(filename,data);
const inventory=JSON.parse(fs.readFileSync(new URL('./after/builtins/node-compat/fs-inventory.json',import.meta.url)));
const Buffer=createBufferModule({hexEncode:v=>NodeBuffer.from(v).toString('hex'),hexDecode:v=>new Uint8Array(NodeBuffer.from(v,'hex'))}).Buffer;
const classic=createClassicStreams({Buffer,events,StringDecoder,nextTick:process.nextTick,AbortSignal,AbortController,disposeSymbol:Symbol.dispose,asyncDisposeSymbol:Symbol.asyncDispose});
const provider=hostProvider(scratch);
const dependencies={kernel:provider.kernel,Buffer,Readable:classic.root.Readable,nextTick:process.nextTick,inventory};
const graph=createFsModules(dependencies),candidate=graph.root.default;
const old=oldFactory(dependencies).root.default;
const oldNamedReadStream=old.ReadStream,oldNamedCreateReadStream=old.createReadStream;
const cases=[];let primary;
async function test(name,fn){await fn();cases.push({name,passed:true});}
async function bytes(stream){const chunks=[];for await(const c of stream)chunks.push(NodeBuffer.from(c));return NodeBuffer.concat(chunks);}
const send={root:'/unused/send-root',etag:true,cacheControl:true,maxAge:31536000000,immutable:true,lastModified:true,acceptRanges:true,dotfiles:'ignore',hidden:false,extensions:[],index:false,from:'/unused',maxage:0,start:7,end:17003,highWaterMark:19};
try {
  await test('actual old facade rejects send root before any IO',()=>{const n=provider.counts.io;assert.throws(()=>old.createReadStream(filename,send),e=>e.code==='ERR_SM_NODE_UNSUPPORTED'&&e.operation==='createReadStream.root');assert.equal(provider.counts.io,n);});
  await test('future native facade reads exact send range equal to Node',async()=>{assert.deepEqual(await bytes(candidate.createReadStream(filename,send)),await bytes(fs.createReadStream(filename,send)));assert.equal(provider.active,0);});
  await test('ignored root never changes chosen file path or adds containment policy',async()=>{const other=path.join(scratch,'other');fs.writeFileSync(other,'wrong');assert.deepEqual(await bytes(candidate.createReadStream(filename,{root:other})),data);});
  await test('all finite send-only fields are ignored by Node and candidate',async()=>{for(const key of ['root','acceptRanges','cacheControl','etag','dotfiles','hidden','extensions','immutable','index','lastModified','maxAge','maxage','from']){const opt={[key]:{unused:true},start:3,end:9};assert.deepEqual(await bytes(candidate.createReadStream(filename,opt)),await bytes(fs.createReadStream(filename,opt)));}});
  await test('normalization copies recognized fields and strips send-only fields',()=>{const n=normalizeReadStreamOptions(send);assert.equal(Object.getPrototypeOf(n),null);assert.deepEqual(Object.keys(n).sort(),['start','end','highWaterMark'].sort());assert.equal(n.start,7);});
  await test('enumerable getters execute once and returned ignored objects are not coerced',async()=>{let a=0,b=0;const value={toString(){throw Error('must not coerce');}};const opts=()=>({get root(){a++;return value;},start:2,end:4});await bytes(candidate.createReadStream(filename,opts()));b=a;assert.equal(b,1);await bytes(fs.createReadStream(filename,opts()));assert.equal(a,2);});
  await test('ignored getter thrown object or falsy primitive survives before IO',()=>{for(const reason of [null,false,0,'',new Error('root getter')]){for(const f of [candidate,fs]){const options={get root(){throw reason;}};let did=false;try{f.createReadStream(filename,options);}catch(e){did=true;assert.equal(e,reason);}assert(did);}}assert.equal(provider.active,0);});
  await test('inherited enumerable root and range follow Node copyObject',async()=>{const proto={root:'/not-used',start:4,end:17};const opts=Object.assign(Object.create(proto),{highWaterMark:3});assert.deepEqual(await bytes(candidate.createReadStream(filename,opts)),await bytes(fs.createReadStream(filename,opts)));});
  await test('nonenumerable ignored getter is not invoked',async()=>{const opt={end:1};Object.defineProperty(opt,'root',{get(){throw Error('not enumerable');}});assert.deepEqual(await bytes(candidate.createReadStream(filename,opt)),await bytes(fs.createReadStream(filename,opt)));});
  await test('prototype setter keys and unsupported hooks remain refused before IO',()=>{for(const key of ['__proto__','constructor','read','destroy','construct','autoDestroy','objectMode']){const opt=Object.create(null);Object.defineProperty(opt,key,{value:{},enumerable:true});assert.throws(()=>candidate.createReadStream(filename,opt),{code:'ERR_SM_NODE_UNSUPPORTED'});}assert.equal({}.polluted,undefined);});
  await test('meaningful unsupported fs/fd/flag/close values still refuse',()=>{for(const o of [{fs:{}},{fd:3},{flags:'r+'},{mode:0o600},{autoClose:false},{emitClose:false}])assert.throws(()=>candidate.createReadStream(filename,{root:'unused',...o}),{code:'ERR_SM_NODE_UNSUPPORTED'});});
  await test('range and highWaterMark bounds remain enforced',()=>{for(const o of [{start:-1},{end:2,start:3},{highWaterMark:0},{highWaterMark:65537}])assert.throws(()=>candidate.createReadStream(filename,{root:'unused',...o}),{code:'ERR_OUT_OF_RANGE'});});
  await test('encoding and abort still use genuine original Readable behavior',async()=>{const text=await new Promise((resolve,reject)=>{let text='';candidate.createReadStream(filename,{root:'unused',encoding:'utf8',highWaterMark:1}).on('data',c=>text+=c).on('end',()=>resolve(text)).on('error',reject);});assert.equal(text,data.toString());const controller=new AbortController();const stream=candidate.createReadStream(filename,{root:'unused',signal:controller.signal});const rejected=assert.rejects(bytes(stream),e=>e.name==='AbortError');controller.abort();await rejected;assert.equal(provider.active,0);});
  await test('INIT still refuses before backend IO for plain options',()=>{provider.setDeployed(false);const n=provider.counts.io;assert.throws(()=>candidate.createReadStream(filename,{root:'unused'}),{code:'ERR_SM_NODE_FS_INITIALIZATION'});assert.equal(provider.counts.io,n);provider.setDeployed(true);});
  await test('entry installer performs no IO and is idempotent',()=>{const n=provider.counts.io;const a=installReadStreamOptionsFacade(old);assert.equal(a,installReadStreamOptionsFacade(old));assert.equal(provider.counts.io,n);assert.equal(a.esmNamedBindingsUpdated,false);});
  await test('entry facade exercises exact normalization on unchanged old backend',async()=>{assert.deepEqual(await bytes(old.createReadStream(filename,send)),await bytes(candidate.createReadStream(filename,send)));});
  await test('entry constructor and FileReadStream aliases retain real stream ownership',async()=>{assert.equal(old.ReadStream,old.FileReadStream);const n=provider.counts.closes;const stream=old.ReadStream(filename,{root:'unused',end:3});assert(stream instanceof old.ReadStream);assert(stream instanceof oldNamedReadStream);assert(stream instanceof classic.root.Readable);assert.equal(stream.constructor,old.ReadStream);assert.deepEqual(await bytes(stream),data.subarray(0,4));assert.equal(provider.counts.closes,n+1);});
  await test('ordinary subclass retains original ReadStream state on same instance',async()=>{class Derived extends old.ReadStream{}const stream=new Derived(filename,{root:'unused',end:2});assert(stream instanceof Derived);assert.equal(stream.constructor,Derived);assert.deepEqual(await bytes(stream),data.subarray(0,3));});
  await test('entry facade preserves unsupported meaningful option refusals',()=>{assert.throws(()=>old.createReadStream(filename,{root:'unused',fd:3}),{code:'ERR_SM_NODE_UNSUPPORTED'});});
  await test('previous ESM named functions remain explicitly old',()=>{assert.notEqual(old.createReadStream,oldNamedCreateReadStream);assert.throws(()=>oldNamedCreateReadStream(filename,{root:'unused'}),{code:'ERR_SM_NODE_UNSUPPORTED'});assert.notEqual(old.ReadStream,oldNamedReadStream);});
  await test('no descriptors leak across all completed streams',()=>{assert.equal(provider.active,0);assert.equal(provider.counts.opens,provider.counts.closes);});
} catch(error){primary=error;} finally {
  if(primary)console.error(primary);
  console.log(JSON.stringify({schemaVersion:1,hostOnly:true,nativeGuestExecuted:false,testBackend:'real Node filesystem + existing Source host-provider + actual classic Readable',cases,passed:!primary,counts:provider.counts,activeHandles:provider.active}));
  fs.rmSync(scratch,{recursive:true,force:true});
}
if(primary)throw primary;
