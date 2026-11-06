// UNCOMPILED native-stream facade. Persistent state stays in guest zlib.
export function createStreamingZlibModule(dependencies) {
 'use strict';
 const {base,kernel,Buffer,Transform,nextTick}=dependencies;
 const apply=Reflect.apply,own=Object.hasOwn,descriptors=Object.getOwnPropertyDescriptors;
 const define=Object.defineProperty,Create=Object.create,proto=Object.getPrototypeOf;
 const U8=Uint8Array,typed=proto(U8.prototype),getter=(p,n)=>Object.getOwnPropertyDescriptor(p,n)?.get;
 const name=getter(typed,Symbol.toStringTag),length=getter(typed,'byteLength'),backing=getter(typed,'buffer'),offset=getter(typed,'byteOffset');
 const abLength=getter(ArrayBuffer.prototype,'byteLength'),resizable=getter(ArrayBuffer.prototype,'resizable'),detached=getter(ArrayBuffer.prototype,'detached');
 const subarray=Function.prototype.call.bind(U8.prototype.subarray),bufferFrom=Buffer.from.bind(Buffer);
 const states=new WeakMap(),markers=new WeakMap();
 const NO=0,SYNC=2,FULL=3,FINISH=4;
 function failure(code,op,message){const e=new Error(message||op);e.code=code;e.module='node:zlib';e.operation=op;return e;}
 function unsupported(op){throw failure('ERR_SM_NODE_UNSUPPORTED',op);}
 function streamError(value){if(value instanceof Error)return value;const e=failure('ERR_SM_ZLIB_NONERROR_THROW','stream callback');e.cause=value;return e;}
 function number(v,key,min,max,fallback){if(v===undefined||v===null)return fallback;if(typeof v!=='number')throw failure('ERR_INVALID_ARG_TYPE',key);if(!Number.isInteger(v)||v<min||v>max)throw failure('ERR_OUT_OF_RANGE',key);return v;}
 function options(value,format){
  if(value===undefined||value===null)value={};
  if(typeof value!=='object'||(proto(value)!==Object.prototype&&proto(value)!==null))throw failure('ERR_INVALID_ARG_TYPE','options');
  const fields=descriptors(value),read=key=>{const d=fields[key];if(!d)return undefined;if(!own(d,'value'))unsupported('accessor option:'+key);return d.value;};
  for(const key of ['dictionary','objectMode','readableObjectMode','writableObjectMode','transform','flush','finishFlush','write','read','destroy','construct','encoding']){
   const v=read(key);if(v!==undefined&&!(key==='flush'&&v===NO)&&!(key==='finishFlush'&&v===FINISH))unsupported('option:'+key);
  }
  // Node ignores unrelated middleware options such as threshold/filter. Only
  // explicitly selected codec/stream fields are read; no arbitrary getter run.
  const high=read('highWaterMark');
  return {level:number(read('level'),'level',-1,9,-1),window:number(read('windowBits'),'windowBits',format?9:8,15,15),mem:number(read('memLevel'),'memLevel',1,9,8),strategy:number(read('strategy'),'strategy',0,4,0),chunk:number(read('chunkSize'),'chunkSize',64,65536,16384),readHigh:number(read('readableHighWaterMark')??high,'readableHighWaterMark',1,65536,65536),writeHigh:number(read('writableHighWaterMark')??high,'writableHighWaterMark',1,1048576,65536)};
 }
 function bytes(value){let n,b;try{if(apply(name,value,[])!=='Uint8Array')throw 0;n=apply(length,value,[]);b=apply(backing,value,[]);apply(abLength,b,[]);}catch{throw failure('ERR_INVALID_ARG_TYPE','chunk');}if(resizable&&apply(resizable,b,[]))unsupported('resizable input');if(detached&&apply(detached,b,[]))unsupported('detached input');if(!detached&&n===0)try{new U8(b,0,0);}catch{unsupported('detached input');}if(n>16777216)throw failure('ERR_SM_ZLIB_STREAM_LIMIT','write chunk');return {value,n};}
 function output(value){const r=bytes(value);if(r.n>65536)throw failure('ERR_SM_ZLIB_INTERNAL','output chunk');return bufferFrom(apply(backing,value,[]),apply(offset,value,[]),r.n);}
 function schedule(stream){const s=states.get(stream);if(s.scheduled||s.closed||s.waitingRead)return;s.scheduled=true;try{nextTick(()=>{s.scheduled=false;pump(stream);});}catch(e){s.scheduled=false;stream.destroy(streamError(e));}}
 function complete(stream,job){const s=states.get(stream);if(s.job!==job)return;s.job=null;s.waitingRead=false;job.callback();}
 function pump(stream){
  const s=states.get(stream),job=s.job;if(s.closed||stream.destroyed||!job||s.waitingRead)return;
  try{
   if(stream.readableLength>=stream.readableHighWaterMark){s.waitingRead=true;return;}
   if(!s.active){
    const end=Math.min(job.offset+65536,job.source.n);
    const part=subarray(job.source.value,job.offset,end);
    kernel.feed(s.handle,part,job.flush);s.pendingBytes=end-job.offset;job.offset=end;s.active=true;
   }
   const r=kernel.pull(s.handle);
   if(!r||typeof r.actionDone!=='boolean'||typeof r.ended!=='boolean')throw failure('ERR_SM_ZLIB_INTERNAL','pull record');
   if(r.ended&&!r.actionDone)throw failure('ERR_SM_ZLIB_INTERNAL','ended action');
   const chunk=output(r.bytes);if(r.actionDone){s.active=false;s.bytesWritten+=s.pendingBytes;s.pendingBytes=0;}if(r.ended)s.ended=true;
   let more=true;if(chunk.byteLength)more=stream.push(chunk);
   // push may synchronously run an application data listener that destroys us.
   if(s.closed||stream.destroyed||s.job!==job)return;
   if(r.actionDone&&job.offset===job.source.n){if(job.flush===FINISH&&!r.ended)throw failure('ERR_SM_ZLIB_INTERNAL','finish did not end');complete(stream,job);return;}
   if(!more){s.waitingRead=true;return;}schedule(stream);
  }catch(e){stream.destroy(streamError(e));}
 }
 class Compressor extends Transform {
  constructor(format,opt){kernel.checkPhase();const o=options(opt,format);super({readableHighWaterMark:o.readHigh,writableHighWaterMark:o.writeHigh,autoDestroy:true,emitClose:true,decodeStrings:true});const handle=kernel.open(format,o.level,o.window,o.mem,o.strategy,o.chunk);states.set(this,{handle,active:false,job:null,scheduled:false,waitingRead:false,closed:false,ended:false,bytesWritten:0,pendingBytes:0});}
  get bytesWritten(){return states.get(this).bytesWritten;}
  _transform(chunk,encoding,callback){const s=states.get(this);try{if(s.closed||s.ended)throw failure('ERR_STREAM_DESTROYED','write');if(s.job)throw failure('ERR_SM_ZLIB_INTERNAL','overlapping transform');const source=bytes(chunk),flush=markers.has(chunk)?markers.get(chunk):NO;s.job={source,offset:0,flush,callback};schedule(this);}catch(e){callback(e);}}
  _flush(callback){const s=states.get(this);if(s.closed){callback(failure('ERR_STREAM_DESTROYED','finish'));return;}if(s.job){callback(failure('ERR_SM_ZLIB_INTERNAL','overlapping finish'));return;}s.job={source:{value:new U8(0),n:0},offset:0,flush:FINISH,callback};schedule(this);}
  _read(size){super._read(size);const s=states.get(this);if(s?.waitingRead){s.waitingRead=false;schedule(this);}}
  _destroy(primary,callback){const s=states.get(this);if(!s){callback(primary);return;}s.closed=true;s.waitingRead=false;let closeError,closeFailed=false;try{kernel.close(s.handle);}catch(e){closeFailed=true;closeError=e;}const job=s.job;s.job=null;if(job)nextTick(job.callback,primary??failure('ERR_STREAM_DESTROYED','destroy'));callback(primary??(closeFailed?streamError(closeError):undefined));}
  flush(kind,callback){kernel.checkPhase();if(typeof kind==='function'){callback=kind;kind=FULL;}else if(kind===undefined)kind=FULL;if(callback!==undefined&&typeof callback!=='function')throw failure('ERR_INVALID_ARG_TYPE','flush callback');if(![NO,SYNC,FULL].includes(kind))unsupported('flush kind');if(this.writableFinished){if(callback)nextTick(callback);return;}if(this.writableEnded){if(callback)this.once('end',callback);return;}const marker=Buffer.alloc(0);markers.set(marker,kind);this.write(marker,callback);}
  close(callback){if(callback!==undefined&&typeof callback!=='function')throw failure('ERR_INVALID_ARG_TYPE','close callback');if(callback){if(this.closed)nextTick(callback);else this.once('close',callback);}this.destroy();}
  params(){unsupported('params');}reset(){unsupported('reset');}
 }
 class GzipImpl extends Compressor{constructor(o){super(1,o);}}
 class DeflateImpl extends Compressor{constructor(o){super(0,o);}}
 function Gzip(o){return new GzipImpl(o);}function Deflate(o){return new DeflateImpl(o);}
 for(const [fn,impl]of [[Gzip,GzipImpl],[Deflate,DeflateImpl]]){fn.prototype=impl.prototype;define(fn.prototype,'constructor',{value:fn,writable:true,configurable:true});Object.setPrototypeOf(fn,Transform);}
 function createGzip(o){return new Gzip(o);}function createDeflate(o){return new Deflate(o);}
 const replacements={Gzip,Deflate,createGzip,createDeflate};
 const rootDescriptors=descriptors(base.default);for(const [key,value]of Object.entries(replacements))rootDescriptors[key].value=value;
 const root=Object.freeze(Create(proto(base.default),rootDescriptors));
 const recordDescriptors=descriptors(base);recordDescriptors.default.value=root;for(const [key,value]of Object.entries(replacements))recordDescriptors[key].value=value;
 return Object.freeze(Create(proto(base),recordDescriptors));
}
