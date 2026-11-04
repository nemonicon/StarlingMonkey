// FUTURE COMPONENT TEMPLATE — never executed by the Node-only oracle.
// Real registered module imports only; no bundled candidate implementation.
import * as stream from 'node:stream';
import * as streamAlias from 'stream';
import * as promises from 'node:stream/promises';
import * as promisesAlias from 'stream/promises';
import { Buffer } from 'node:buffer';
import { EventEmitter, addAbortListener } from 'node:events';
import { promisify } from 'node:util';
import { checks } from './checks.mjs';

// These four literal calls are the selected bundler's static CJS contract.
// No public runtime require() is installed or used after bundling.
const cjs = require('node:stream');
const cjsAlias = require('stream');
const cjsPromises = require('node:stream/promises');
const cjsPromisesAlias = require('stream/promises');
const rootKeys = ['Duplex','PassThrough','Readable','Stream','Transform','Writable',
  '_isArrayBufferView','_isUint8Array','_uint8ArrayToBuffer','addAbortSignal','compose',
  'default','destroy','duplexPair','finished','getDefaultHighWaterMark','isDestroyed',
  'isDisturbed','isErrored','isReadable','isWritable','pipeline','promises','setDefaultHighWaterMark'].sort();
const promiseKeys = ['default','finished','pipeline'];
const equal = (a,b,label) => { if (JSON.stringify(a)!==JSON.stringify(b)) throw new Error('CLASSIC_CHECK: '+label); };
const check = (value,label) => { if (!value) throw new Error('CLASSIC_CHECK: '+label); };
let calls = 0;
// Pure guest state created during snapshot initialization. No pending read or I/O.
const snapshotToken = { marker: 342 };
const snapshotSource = new stream.Readable({ objectMode: true, read() {} });
const snapshotDefaults = [stream.getDefaultHighWaterMark(false), stream.getDefaultHighWaterMark(true)];
const snapshotHex = Buffer.from('cafe','hex');

function moduleGraph() {
  equal(Object.keys(stream).sort(),rootKeys,'exact root namespace');
  equal(Object.keys(promises).sort(),promiseKeys,'exact promise namespace');
  check(stream===streamAlias && promises===promisesAlias,'ESM alias namespaces');
  check(cjs===stream.default && cjsAlias===cjs,'static CommonJS root defaults');
  check(cjsPromises===promises.default && cjsPromisesAlias===cjsPromises,'static CommonJS promise defaults');
  check(stream.default===stream.Stream && stream.Stream.Stream===stream.Stream,'callable Stream graph');
  check(stream.Stream.prototype instanceof EventEmitter,'installed EventEmitter ancestry');
  check(stream.promises===promises.default && cjs.promises===promises.default,'shared promises graph');
  check(Object.getPrototypeOf(stream)===null && !Object.isExtensible(stream),'real finite ESM namespace');
  check(Object.getPrototypeOf(promises)===null && !Object.isExtensible(promises),'real promises ESM namespace');
  check(stream[Symbol.toStringTag]==='Module' && promises[Symbol.toStringTag]==='Module','namespace brands');
  check(!Object.hasOwn(stream,'then') && !Object.hasOwn(promises,'then') && stream.then===undefined && promises.then===undefined,'safe inspection');
  const mutations=[];
  for (const name of ['pipeline','finished']) {
    const callback=stream[name], named=promises[name], original=promises.default[name];
    check(callback[promisify.custom]===named && promisify(callback)===named,'custom promisify '+name);
    const descriptor=Object.getOwnPropertyDescriptor(callback,promisify.custom);
    check(typeof descriptor.get==='function' && descriptor.enumerable && !descriptor.configurable,'custom getter descriptor '+name);
    const replacement=function replacement(){};
    try {
      promises.default[name]=replacement;
      check(callback[promisify.custom]===replacement && promises[name]===named,'default mutation/named snapshot '+name);
      mutations.push(name);
    } finally { promises.default[name]=original; }
  }
  const original=stream.default.Readable;
  try { stream.default.Readable=function replacement(){}; check(stream.Readable===original,'root named export snapshot'); }
  finally { stream.default.Readable=original; }
  return { rootKeys, promiseKeys, aliases:true, staticCommonJS:true, customPromisify:mutations, namedBindingSnapshots:true };
}

function deferredOperations() {
  check(typeof Symbol.asyncDispose==='symbol','actual installed asyncDispose symbol required');
  const operations=[['compose',stream.compose],['duplexPair',stream.duplexPair],
    ...['Readable','Writable','Duplex'].flatMap(name=>['fromWeb','toWeb'].map(method=>[name+'.'+method,stream[name][method]])),
    ['Duplex.from',stream.Duplex.from],
    ...['compose','map','filter','forEach','toArray','some','find','every','flatMap','drop','take','reduce','iterator'].map(name=>['Readable.prototype.'+name,stream.Readable.prototype[name]]),
    ...['Readable','Writable'].map(name=>[name+'.prototype[Symbol.asyncDispose]',stream[name].prototype[Symbol.asyncDispose]])];
  const observed=[];
  for(const [operation,fn] of operations) for(const construct of [false,true]) {
    let error;
    try { if(construct) Reflect.construct(fn,[]); else Reflect.apply(fn,undefined,[]); } catch(caught) { error=caught; }
    check(error?.code==='ERR_SM_NODE_UNSUPPORTED' && error.module==='node:stream' && error.operation===operation && error.profile==='sm-node-22.14.0-m0.12','deferred '+operation);
    for(const key of ['code','module','operation','profile']) check(Object.hasOwn(error,key),'own error property '+key);
    observed.push({operation,construct,code:error.code});
  }
  check(stream.Readable.prototype.asIndexedPairs===undefined,'Node22 absent historical method');
  return observed;
}

function deferredOverloads() {
  const observed=[];
  function unsupported(name,invoke) {
    let error;try{invoke();}catch(caught){error=caught;}
    check(error?.code==='ERR_SM_NODE_UNSUPPORTED' && error.module==='node:stream','deferred overload '+name);
    observed.push({name,code:error.code,operation:error.operation});
  }
  for(const [shape,value] of [['readable',{getReader(){}}],['writable',{getWriter(){}}],['transform-pair',{readable:{},writable:{}}]]) {
    for(const [name,invoke] of [
      ['callback-pipeline',()=>stream.pipeline(value,new stream.Writable({write(value,encoding,callback){callback();}}),()=>{})],
      ['promise-pipeline',()=>promises.pipeline(value,new stream.Writable({write(value,encoding,callback){callback();}}))],
      ['callback-finished',()=>stream.finished(value,()=>{})],
      ['promise-finished',()=>promises.finished(value)],
      ['addAbortSignal',()=>stream.addAbortSignal(new AbortController().signal,value)]]) unsupported(shape+'-'+name,invoke);
  }
  unsupported('callback-function-stage',()=>stream.pipeline(function stage(){},new stream.Writable({write(value,encoding,callback){callback();}}),()=>{}));
  unsupported('promise-function-stage',()=>promises.pipeline(function stage(){},new stream.Writable({write(value,encoding,callback){callback();}})));
  return observed;
}

async function logicalLimits() {
  const observed=[];
  async function limited(name,source,fill,overflow,expectedLength) {
    source.on('error',()=>{});
    fill();
    equal(source.readableLength??source.writableLength,expectedLength,name+' accepted boundary');
    let error;
    try { overflow(); } catch(caught) { error=caught; }
    check(error?.code==='ERR_SM_NODE_STREAM_LIMIT' && error.module==='node:stream','logical limit '+name);
    check(Object.hasOwn(error,'code') && Object.hasOwn(error,'operation'),'own logical-limit error');
    observed.push({name,boundary:expectedLength,code:error.code,operation:error.operation});
    // Profile contract: discard a stream after a limit error. No rollback claim.
    source.destroy();
    await promises.finished(source).catch(()=>{});
  }
  const objects=new stream.Writable({objectMode:true,write(value,encoding,callback){callback();}});
  objects.cork();
  await limited('writable object units',objects,()=>{for(let i=0;i<4096;i++)objects.write(i);},()=>objects.write(4096),4096);
  const chunks=new stream.Readable({read(){}}),byte=new Uint8Array([1]);
  await limited('readable byte chunks',chunks,()=>{for(let i=0;i<4096;i++)chunks.push(byte);},()=>chunks.push(byte),4096);
  const bytes=new stream.Readable({read(){}}),block=new Uint8Array(1048576);
  await limited('readable byte units',bytes,()=>{for(let i=0;i<16;i++)bytes.push(block);},()=>bytes.push(byte),16777216);
  return observed;
}

async function rootedRoundTrips() {
  check(typeof Symbol.dispose==='symbol','actual installed dispose symbol required');
  const source=new stream.Readable({objectMode:true,read(){}}),token={marker:342};
  source.push(token);
  let callbackCalls=0,abortCalls=0,disposedCalls=0;
  function callback(value) { check(this===source && value===token,'retained stream callback/receiver');callbackCalls++; }
  source.on('retained',callback);
  const controller=new AbortController(),disposedController=new AbortController();
  const signal=controller.signal;
  const resource=addAbortListener(signal,function(event){check(this===signal && event.type==='abort','retained abort callback/receiver');abortCalls++;});
  const disposed=addAbortListener(disposedController.signal,()=>disposedCalls++);
  for(let round=0;round<8;round++) {
    // The existing native decode and encode entry points perform the opt-in
    // GC-stress collections. All owners above remain ordinary JS references.
    const bytes=Buffer.from('0001cafeff','hex');
    equal([...bytes],[0,1,202,254,255],'rooting round bytes');
    equal(bytes.toString('hex'),'0001cafeff','rooting round native encode');
  }
  const streamIdentity=source.read()===token;
  check(streamIdentity,'retained stream chunk identity');
  source.emit('retained',token);
  disposed[Symbol.dispose]();disposed[Symbol.dispose]();disposedController.abort();
  controller.abort('rooting-control');resource[Symbol.dispose]();
  equal([callbackCalls,abortCalls,disposedCalls],[1,1,0],'retained listeners/disposers');
  source.destroy();await promises.finished(source).catch(()=>{});
  return{hexRounds:8,streamIdentity,callbackCalls,abortCalls,disposedCalls};
}

export async function run() {
  const call=++calls;
  const retainedDefaultBefore=stream.getDefaultHighWaterMark(false);
  equal(retainedDefaultBefore,call===1?65536:777,'instance-retained default');
  equal(snapshotDefaults,[65536,16],'pre-snapshot defaults');
  check(snapshotHex.toString('hex')==='cafe','snapshot Buffer survives');
  let snapshotIdentity=null;
  if(call===1) {
    snapshotSource.push(snapshotToken); snapshotSource.push(null);
    snapshotIdentity=snapshotSource.read()===snapshotToken;
    check(snapshotIdentity,'snapshot stream identity');
    snapshotSource.destroy();
    await promises.finished(snapshotSource).catch(()=>{});
  }
  const graph=moduleGraph();
  check(await Promise.resolve(stream)===stream && await Promise.resolve(promises)===promises,'no accidental thenable');
  stream.setDefaultHighWaterMark(false,65536); stream.setDefaultHighWaterMark(true,16);
  const ordinary=await checks(stream,promises,Buffer);
  equal(ordinary.length,19,'ordinary group count');
  const deferred=deferredOperations();
  equal(deferred.length,48,'deferred call/new count');
  const overloads=deferredOverloads();
  equal(overloads.length,17,'deferred overload count');
  const limits=await logicalLimits();
  // Uses actual native byte-processing entry points; gc-off variant is a
  // separately pinned GC-stress engine. No guest GC export is added.
  const nativeHex=Buffer.from('00cafeff','hex').toString('hex');
  equal(nativeHex,'00cafeff','native hex control');
  const rooting=await rootedRoundTrips();
  stream.setDefaultHighWaterMark(false,777);
  return JSON.stringify({schemaVersion:1,call,retainedDefaultBefore,snapshotDefaults,snapshotIdentity,
    ordinary,graph,deferred,overloads,limits,nativeHex,rooting});
}
