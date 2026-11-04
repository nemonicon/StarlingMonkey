// Shared ordinary public-API workload. No clocks, host services or private state.
export const scenarioIds=Object.freeze(['pipeline-view-64','pipeline-copy-64','pipeline-view-524288','pipeline-copy-524288','fragmented-utf8','object-backpressure','handled-cancellation','checksum-input-only','byte-input-and-copy-construction-only','stream-construction-and-clean-close-only']);
const seed=2166136261,step=(hash,value)=>Math.imul(hash^(value>>>0),16777619)>>>0;
function requireValue(value,message){if(!value)throw new Error(message);}
function bytesHash(hash,bytes){for(let i=0;i<bytes.length;i++)hash=step(hash,bytes[i]);return hash;}
function stringHash(hash,value){for(let i=0;i<value.length;i++)hash=step(hash,value.charCodeAt(i));return hash;}
export function createWorkload(provider){
 const {stream,promises,dependencies}=provider,{Buffer,StringDecoder,nextTick}=dependencies;
 requireValue(typeof Buffer.from==='function'&&typeof nextTick==='function'&&typeof promises.pipeline==='function','Finite provider contract missing');
 let input;
 function setup(id){
  requireValue(scenarioIds.includes(id),'Unknown finite scenario');
  const size=id.includes('524288')||id==='byte-input-and-copy-construction-only'?524288:64;
  const backing=new ArrayBuffer(size+16),view=new Uint8Array(backing,8,size);
  for(let i=0;i<size;i++)view[i]=(i*17+3)&255;
  const buffer=Buffer.from(backing,8,size);
  requireValue(buffer.byteOffset===8&&buffer.byteLength===size&&buffer.buffer===backing,'Expected fixed attached unshared offset window');
  const text=Buffer.from('A¢€😀Z'.repeat(8),'utf8'),fragments=[];
  let offset=0;for(let i=0;i<64;i++){const length=i<24?2:1;fragments.push(new Uint8Array(text.buffer,text.byteOffset+offset,length));offset+=length;}
  requireValue(offset===text.byteLength,'Complete valid fragmented input');
  input={id,view,buffer,fragments,objects:Array.from({length:64},(_,i)=>({value:i})),size};
  return bytesHash(seed,view)|0;
 }
 async function run(iterations,{trace=false}={}){
  requireValue(input&&Number.isInteger(iterations)&&iterations>=1&&iterations<=16,'Use setup plus finite1..16 iterations');
  const records=[];let aggregate=seed,totalUnits=0,scheduledCallbacks=0;
  for(let iteration=0;iteration<iterations;iteration++){
   const events=[],counts={finish:0,end:0,error:0,close:0},returns=[];
   let checksum=seed,units=0,callbacks=0;
   const emit=(...args)=>{if(trace){requireValue(events.length<4096,'Ordinary per-iteration trace exceeded4096 records');events.push(args);}};
   const tick=callback=>{scheduledCallbacks++;nextTick(callback);};
   function observe(target,name){for(const event of ['finish','end','error','close'])target.on(event,function(...args){counts[event]++;emit('event',name,event,this===target,args.length,event==='error'?args[0]?.code??args[0]?.name:null);});}
   function consume(chunk){if(typeof chunk==='string'){checksum=stringHash(checksum,chunk);units+=chunk.length;emit('output-string',chunk);}else if(typeof chunk==='object'&&chunk!==null&&'value'in chunk){checksum=step(checksum,chunk.value);units++;emit('output-object',chunk.value);}else{checksum=bytesHash(checksum,chunk);units+=chunk.byteLength;emit('output-bytes',chunk.byteLength,bytesHash(seed,chunk));}}
   function write(chunk,encoding,callback){callbacks++;emit('write-callback',this instanceof stream.Writable,arguments.length,encoding,typeof chunk);consume(chunk);callback();}
   const id=input.id;
   if(id.startsWith('pipeline-')||id==='fragmented-utf8'){
    const fragmented=id==='fragmented-utf8',chunks=fragmented?64:input.size===64?128:8;
    let index=0;
    const source=new stream.Readable({highWaterMark:fragmented?8:input.size,read(){
     while(index<chunks){const chunk=fragmented?input.fragments[index]:id.includes('-copy-')?Buffer.from(input.buffer):input.view;index++;
      const accepted=this.push(chunk);emit('push',index,accepted);if(!accepted)return;}
     emit('push-eof');this.push(null);
    }});
    const decoder=fragmented?new StringDecoder('utf8'):null;
    const pass=fragmented?new stream.Transform({readableObjectMode:true,transform(chunk,encoding,callback){emit('decode',chunk.byteLength);callback(null,decoder.write(chunk));},flush(callback){const tail=decoder.end();emit('flush',tail);if(tail)this.push(tail);callback();}}):new stream.PassThrough({highWaterMark:input.size});
    const sink=new stream.Writable({objectMode:fragmented,highWaterMark:fragmented?2:input.size,write});
    observe(source,'source');observe(pass,'pass');observe(sink,'sink');
    const originalWrite=sink.write;sink.write=function(...args){const accepted=Reflect.apply(originalWrite,this,args);returns.push(accepted);emit('write-return',accepted);return accepted;};
    emit('pipeline-before');const completion=promises.pipeline(source,pass,sink);emit('pipeline-registered');await completion;emit('pipeline-resolved');
    await new Promise(resolve=>tick(resolve));emit('selected-tick-checkpoint');
    requireValue(source.readableEnded&&sink.writableFinished,'EOF/finish required');
    emit('terminal',source.readableEnded,sink.writableFinished,source.destroyed,pass.destroyed,sink.destroyed);
   }else if(id==='object-backpressure'){
    const sink=new stream.Writable({objectMode:true,highWaterMark:2,write(chunk,encoding,callback){callbacks++;consume(chunk);emit('write-callback',this===sink,arguments.length,encoding);tick(callback);}});
    observe(sink,'sink');
    for(const value of input.objects){const accepted=sink.write(value);returns.push(accepted);emit('write-return',accepted);if(!accepted){await new Promise(resolve=>sink.once('drain',function(...args){emit('drain',this===sink,args.length);resolve();}));}}
    const completion=promises.finished(sink);emit('finished-pending');sink.end();await completion;emit('finished-resolved');
    await new Promise(resolve=>tick(resolve));requireValue(sink.writableFinished&&sink.destroyed,'Clean object writer required');
   }else if(id==='handled-cancellation'){
    const controller=new AbortController(),reason=new Error('ordinary benchmark cancellation');let next=0;
    const source=new stream.Readable({objectMode:true,highWaterMark:1,read(){if(next<16)this.push({value:next++});else this.push(null);}});
    const sink=new stream.Writable({objectMode:true,highWaterMark:1,write(chunk,encoding,callback){callbacks++;consume(chunk);emit('write-callback',this===sink,arguments.length,encoding);tick(()=>{if(callbacks===4){emit('abort');controller.abort(reason);}callback();});}});
    observe(source,'source');observe(sink,'sink');
    emit('pipeline-before');const completion=promises.pipeline(source,sink,{signal:controller.signal}).then(()=>({resolved:true}),error=>({name:error.name,code:error.code,cause:error.cause===reason}));emit('pipeline-registered');
    const result=await completion;emit('handled-rejection',result);await new Promise(resolve=>tick(resolve));
    requireValue(result.name==='AbortError'&&result.code==='ABORT_ERR'&&source.destroyed&&sink.destroyed&&callbacks===4,'Bounded handled cancellation required');
    emit('terminal',source.destroyed,sink.destroyed,controller.signal.aborted);
   }else if(id==='checksum-input-only'||id==='byte-input-and-copy-construction-only'){
    const count=id==='checksum-input-only'?128:8;
    for(let i=0;i<count;i++)consume(id==='checksum-input-only'?input.view:Buffer.from(input.buffer));
    emit('raw-control',id,count);
   }else{
    const source=new stream.Readable({read(){this.push(null);}}),pass=new stream.PassThrough(),sink=new stream.Writable({write});
    observe(source,'source');observe(pass,'pass');observe(sink,'sink');
    emit('pipeline-before');const completion=promises.pipeline(source,pass,sink);emit('pipeline-registered');await completion;emit('pipeline-resolved');
    await new Promise(resolve=>tick(resolve));requireValue(source.readableEnded&&sink.writableFinished,'Clean constructor-only pipeline required');
    emit('terminal',source.destroyed,pass.destroyed,sink.destroyed);
   }
   aggregate=step(aggregate,checksum);aggregate=step(aggregate,units);totalUnits+=units;
   if(trace)records.push({iteration,checksum,units,callbacks,returns,counts,events});
  }
  return{scenario:input.id,iterations,checksum:aggregate|0,unsignedChecksum:aggregate>>>0,totalUnits,scheduledCallbacks,records};
 }
 return Object.freeze({setup,run});
}
