// UNEXECUTED until actual corrected native capture+guards are linked/admitted.
import defaultExport,* as namespace from 'node:stream/web';
import bareDefault,* as bareNamespace from 'stream/web';
import cjs from './native-require.cjs';
import {runNativeCorpus} from './native-checks.mjs';
import {pipeline} from '../candidate/codec-cases.mjs';
import expected from 'node-compat:stream-web-installed-oracles';
const snapshotReadable=new namespace.ReadableStream({start(controller){controller.enqueue('snapshot');controller.close();}});
const snapshotFrom=namespace.ReadableStream.from([3,4]);
const snapshotEncoder=new namespace.TextEncoderStream();
const snapshotDecoder=new namespace.TextDecoderStream();
let calls=0;
function ensure(value,message){if(!value)throw Error(message);}
async function consume(stream){const reader=stream.getReader(),values=[];try{for(;;){const entry=await reader.read();if(entry.done)break;values.push(entry.value);}}finally{reader.releaseLock();}return values;}
async function nativeIdentities(){
  const globals=['ReadableStream','ReadableStreamDefaultReader','ReadableStreamBYOBReader','ReadableStreamBYOBRequest','ReadableByteStreamController',
    'ReadableStreamDefaultController','WritableStream','ByteLengthQueuingStrategy','CountQueuingStrategy','TransformStream'];
  for(const name of globals)ensure(namespace[name]===globalThis[name],'global identity '+name);
  // Ordinary deployed instances verify the hidden constructors. Never used to
  // provide a factory argument or to recover constructors during snapshot init.
  let writableController,transformController;
  const writable=new namespace.WritableStream({start(controller){writableController=controller;}}),writer=writable.getWriter();
  ensure(writer.constructor===namespace.WritableStreamDefaultWriter&&writableController.constructor===namespace.WritableStreamDefaultController,'hidden writable identities');
  ensure(writer instanceof namespace.WritableStreamDefaultWriter&&writableController instanceof namespace.WritableStreamDefaultController,'hidden writable brands');
  await writer.close();await writer.closed;writer.releaseLock();
  const transform=new namespace.TransformStream({start(controller){transformController=controller;}}),tw=transform.writable.getWriter(),tr=transform.readable.getReader(),closed=tw.close();
  ensure(transformController.constructor===namespace.TransformStreamDefaultController&&transformController instanceof namespace.TransformStreamDefaultController,'hidden transform identity');
  await tr.read();await closed;await tw.closed;await tr.closed;tw.releaseLock();tr.releaseLock();
  ensure(typeof writableController.signal==='undefined','Writable controller signal remains an explicit gap');
  ensure(typeof globalThis.TextEncoderStream==='undefined'&&typeof globalThis.TextDecoderStream==='undefined','No accidental global codec installation');
  ensure(namespace.CompressionStream!==globalThis.CompressionStream&&namespace.DecompressionStream!==globalThis.DecompressionStream,'Compression bindings must remain explicit deferred functions');
  return{globalNativeConstructors:globals.length,hiddenNativeConstructors:3,uninstalledGlobalCodecs:true,signalMissing:true};
}
export async function run(){
  const report={calls:++calls};
  try{
    const names=Object.keys(namespace).sort();ensure(JSON.stringify(names)===JSON.stringify(expected.names),'exact finite ESM namespace');
    for(const candidate of [namespace,bareNamespace]){
      ensure(Object.getPrototypeOf(candidate)===null&&candidate.then===undefined&&candidate.missing===undefined,'safe native ESM namespace');
      ensure(await Promise.resolve(candidate)===candidate,'no accidental thenable');
      for(const name of names)if(name!=='default')ensure(candidate[name]===defaultExport[name],'named/default identity '+name);
    }
    ensure(defaultExport===namespace.default&&bareDefault===defaultExport&&bareNamespace.default===defaultExport,'alias defaults');
    ensure(cjs.canonical===defaultExport&&cjs.bare===defaultExport,'literal CommonJS default lowering');
    ensure(JSON.stringify(Object.keys(defaultExport).sort())===JSON.stringify(names.filter(name=>name!=='default')),'finite default fields');
    const saved=defaultExport.TextEncoderStream;try{defaultExport.TextEncoderStream=null;ensure(namespace.TextEncoderStream===saved,'named binding snapshot');}finally{defaultExport.TextEncoderStream=saved;}
    report.identities=await nativeIdentities();report.aliases=2;report.commonJS=true;report.names=names;
    const full=await runNativeCorpus(namespace,expected);if(full.failure)throw full.failure;Object.assign(report,full);
    if(calls===1){
      ensure(JSON.stringify(await consume(snapshotReadable))==='["snapshot"]','snapshot queued readable');
      ensure(JSON.stringify(await consume(snapshotFrom))==='[3,4]','snapshot HWM0 from iterable');
      const encoded=await pipeline(snapshotEncoder,['\ud83c','\udf0d']);
      ensure(JSON.stringify(encoded.outputs)==='[[240,159,140,141]]'&&encoded.close.fulfilled,'snapshot codec state');
      const decoded=await pipeline(snapshotDecoder,[Uint8Array.of(0xe2),Uint8Array.of(0x82,0xac)]);
      ensure(JSON.stringify(decoded.outputs)==='["€"]'&&decoded.close.fulfilled,'snapshot decoder state');
    }
    report.snapshotResumption=true;report.passed=true;
  }catch(error){report.failure=error?.actual!==undefined?error:{name:error?.name,message:error?.message,stack:error?.stack};report.passed=false;}
  return JSON.stringify(report);
}
