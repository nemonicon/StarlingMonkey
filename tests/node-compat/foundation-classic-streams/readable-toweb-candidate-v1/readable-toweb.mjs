// Finite JS bridge to the ACTUAL existing guest ReadableStream constructor.
// No host Node adapter, new native service or codec is used in guest code.
export function installReadableToWeb(graph, WebReadableStream) {
 'use strict';
 if(typeof WebReadableStream!=='function')throw new TypeError('Actual native ReadableStream is required');
 const define=Object.defineProperty,descriptors=Object.getOwnPropertyDescriptors,proto=Object.getPrototypeOf,apply=Reflect.apply;
 const U8=Uint8Array,AB=ArrayBuffer,typed=proto(U8.prototype),get=(p,k)=>Object.getOwnPropertyDescriptor(p,k)?.get;
 const typedName=get(typed,Symbol.toStringTag),typedBuffer=get(typed,'buffer'),typedLength=get(typed,'byteLength');
 const abLength=get(AB.prototype,'byteLength'),resizable=get(AB.prototype,'resizable'),detached=get(AB.prototype,'detached');
 const leases=new WeakSet(),lateErrorProtected=new WeakSet();let active=0;
 const MAX_CHUNK=16777216,MAX_TOTAL=67108864,MAX_CHUNKS=65536,MAX_ADAPTERS=16,MAX_HWM=1048576;
 function error(code,message,Type=Error){const e=new Type(message);Object.assign(e,{code,module:'node:stream',operation:'Readable.toWeb',profile:'sm-node-22.14.0-m0.23'});return e;}
 function unsupported(message){throw error('ERR_SM_NODE_UNSUPPORTED',message);}
 function limit(message){return error('ERR_SM_NODE_STREAM_LIMIT',message,RangeError);}
 function lateErrorIgnored(){} // No controller/source/owner captured after retirement.
 function ownRecord(value,operation){const out=Object.create(null);if(value===undefined||value===null)return out;if(typeof value!=='object'||(proto(value)!==Object.prototype&&proto(value)!==null))throw error('ERR_INVALID_ARG_TYPE',operation,TypeError);const ds=descriptors(value);for(const key of Reflect.ownKeys(ds)){if(typeof key!=='string')unsupported(operation+' symbol');const d=ds[key];if(!Object.hasOwn(d,'value'))unsupported(operation+' accessor');out[key]=d.value;}return out;}
 function highWaterMark(value){if(typeof value!=='number'||!Number.isFinite(value)||!Number.isInteger(value)||value<0||value>MAX_HWM)throw error('ERR_OUT_OF_RANGE','Byte highWaterMark must be integer0..1048576',RangeError);return value;}
 function translated(reason){
  // Explicit error-event presence is retained even for null/undefined/falsy.
  let code;try{const d=reason&&Object.getOwnPropertyDescriptor(reason,'code');if(d&&Object.hasOwn(d,'value'))code=d.value;}catch{}
  if(code==='ERR_STREAM_PREMATURE_CLOSE'){const e=new Error('The operation was aborted',{cause:reason});e.name='AbortError';e.code='ABORT_ERR';return e;}
  if(['Z_ERRNO','Z_STREAM_ERROR','Z_DATA_ERROR','Z_MEM_ERROR','Z_BUF_ERROR','Z_VERSION_ERROR','Z_NEED_DICT'].includes(code)){const e=new TypeError(undefined,{cause:reason});e.code=code;return e;}
  return reason;
 }
 function copy(chunk){
  let n,b;
  try{if(apply(typedName,chunk,[])!=='Uint8Array')throw 0;n=apply(typedLength,chunk,[]);b=apply(typedBuffer,chunk,[]);apply(abLength,b,[]);}catch{throw error('ERR_INVALID_ARG_TYPE','Byte-mode toWeb requires Uint8Array/Buffer chunks',TypeError);}
  if(resizable&&apply(resizable,b,[]))unsupported('Resizable toWeb chunk');
  if(detached&&apply(detached,b,[]))unsupported('Detached toWeb chunk');
  if(!detached&&n===0)try{new U8(b,0,0);}catch{unsupported('Detached toWeb chunk');}
  if(n>MAX_CHUNK)throw limit('toWeb chunk exceeds16MiB');
  // Genuine fixed typed-array copy. Visible byte offset is respected; no
  // caller-owned/pool backing is exposed after its write callback can run.
  return new U8(chunk);
 }
 function toWeb(readable,options){
  if(!readable||typeof readable!=='object'||typeof readable._readableState!=='object')throw error('ERR_INVALID_ARG_TYPE','streamReadable must be Node Readable-compatible',TypeError);
  if(readable.destroyed||readable.readable===false||readable.readableEnded)return new WebReadableStream({start(c){c.close();}});
  if(readable.readableObjectMode)unsupported('Object-mode toWeb is outside this byte profile');
  if(readable.readableEncoding!=null)unsupported('Decoded string toWeb is outside this byte profile');
  const o=ownRecord(options,'toWeb options');for(const key of Object.keys(o))if(key!=='strategy')unsupported('toWeb option:'+key);
  const strategy=ownRecord(o.strategy,'toWeb strategy');for(const key of Object.keys(strategy))if(key!=='highWaterMark')unsupported('toWeb strategy:'+key);
  const hwm=highWaterMark(strategy.highWaterMark===undefined?readable.readableHighWaterMark:strategy.highWaterMark);
  if(leases.has(readable))unsupported('Readable already has an active toWeb owner');
  if(active===MAX_ADAPTERS)throw limit('Too many active toWeb adapters');
  let source=readable;readable=null;
  let methods={};for(const name of ['on','removeListener','pause','resume','destroy']){const f=source[name];if(typeof f!=='function')throw error('ERR_INVALID_ARG_TYPE','Missing Readable method '+name,TypeError);methods[name]=f;}
  let controller=null,state='active',count=0,total=0,acquired=false;
  const invoke=(name,args=[])=>apply(methods[name],source,args);
  function cleanup(){
   if(!acquired)return [];
   const r=source,m=methods;acquired=false;leases.delete(r);active--;
   // Remove only this adapter's listeners; keep no closures that retain the
   // retired controller. A single shared no-op protects against late errors.
   const errors=[];
   for(const [event,fn]of [['data',onData],['end',onEnd],['error',onError],['close',onClose]])try{apply(m.removeListener,r,[event,fn]);}catch(e){errors.push(e);}
   if(!lateErrorProtected.has(r))try{apply(m.on,r,['error',lateErrorIgnored]);lateErrorProtected.add(r);}catch(e){errors.push(e);}
   controller=null;source=null;methods=null;
   return errors;
  }
  const combined=(primary,errors)=>errors.length?new AggregateError([primary,...errors],'Readable.toWeb primary and cleanup failures',{cause:primary}):primary;
  function fail(reason,destroy){
   if(state!=='active')return;state='errored';const c=controller,r=source,d=methods.destroy;
   const errors=cleanup();if(destroy)try{apply(d,r,[reason]);}catch(e){errors.push(e);}c.error(combined(translated(reason),errors));
  }
  function onError(reason){fail(reason,false);}
  function onClose(){if(state==='active')fail(error('ERR_STREAM_PREMATURE_CLOSE','Premature close'),false);}
  function onEnd(){if(state!=='active')return;state='closed';const c=controller,errors=cleanup();if(errors.length)c.error(new AggregateError(errors,'Readable.toWeb cleanup failed'));else c.close();}
  function onData(chunk){if(state!=='active')return;try{const owned=copy(chunk);if(count===MAX_CHUNKS||owned.byteLength>MAX_TOTAL-total)throw limit('toWeb cumulative data limit');count++;total+=owned.byteLength;controller.enqueue(owned);if(state==='active'&&controller.desiredSize<=0)invoke('pause');}catch(e){fail(e,true);}}
  leases.add(source);active++;acquired=true;
  try{return new WebReadableStream({
   start(c){controller=c;invoke('pause');for(const [event,fn]of [['error',onError],['end',onEnd],['close',onClose],['data',onData]])invoke('on',[event,fn]);},
   pull(){if(state==='active')try{invoke('resume');}catch(e){fail(e,true);}},
   cancel(reason){if(state!=='active')return;state='canceled';const r=source,d=methods.destroy,errors=cleanup();try{apply(d,r,[reason]);}catch(e){errors.push(e);}if(errors.length)throw new AggregateError(errors,'Readable.toWeb cancellation cleanup failed');},
  },{highWaterMark:hwm,size(value){return apply(typedLength,value,[]);}});}catch(e){if(state==='active'){state='construction-failed';const r=source,d=methods.destroy,errors=cleanup();try{apply(d,r,[e]);}catch(secondary){errors.push(secondary);}throw combined(e,errors);}throw e;}
 }
 const original=Object.getOwnPropertyDescriptor(graph.root.Readable,'toWeb');
 if(!original||!Object.hasOwn(original,'value'))throw error('ERR_SM_NODE_PROFILE_INITIALIZATION','Missing classic toWeb slot');
 define(graph.root.Readable,'toWeb',{...original,value:toWeb});
 return graph;
}
