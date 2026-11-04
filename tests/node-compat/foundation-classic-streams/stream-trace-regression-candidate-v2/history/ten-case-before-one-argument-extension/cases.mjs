// Finite public valid-API cases shared by Node, the labelled host model, and guest.
export function makeInput(Buffer){const bytes=Buffer.alloc(64);for(let i=0;i<bytes.length;i++)bytes[i]=(i*17+3)&255;return bytes;}
export function checksum(bytes){let value=2166136261;for(const byte of bytes)value=Math.imul(value^byte,16777619)>>>0;return value;}
function check(value,message){if(!value)throw new Error(message);}
function boundedTrace(){const events=[];return{events,push(...row){check(events.length<128,'Trace exceeds128 records');check(row.every(value=>typeof value==='string'||typeof value==='number'||typeof value==='boolean'),'Trace primitives must survive JSON exactly');events.push(row);}};}
export async function runCases({stream,Buffer,input,queueMicrotask}){
 check(input.length===64,'Fixed64byte input required');const expected=checksum(input),results=[];
 for(const deferred of [false,true])for(const highWaterMark of [65,64,63]){
  const trace=boundedTrace();let writeCalls=0,callbackCalls=0,bytes=0,hash=2166136261,finish=0,close=0,accepted;
  let resolveClosed,rejectClosed;const closed=new Promise((resolve,reject)=>{resolveClosed=resolve;rejectClosed=reject;});
  const sink=new stream.Writable({highWaterMark,write(chunk,encoding,callback){writeCalls++;trace.push('write-enter',chunk.length);
   for(let i=0;i<chunk.length;i++){check(chunk[i]===input[i],'Written byte mismatch');hash=Math.imul(hash^chunk[i],16777619)>>>0;}bytes+=chunk.length;
   const complete=()=>{trace.push('write-complete');callback();};if(deferred)queueMicrotask(complete);else complete();}});
  sink.on('error',rejectClosed);sink.on('drain',()=>trace.push('drain'));sink.on('finish',()=>{finish++;trace.push('finish');});sink.on('close',()=>{close++;trace.push('close');resolveClosed();});
  trace.push('before-write');accepted=sink.write(Buffer.from(input),error=>{if(error){rejectClosed(error);return;}callbackCalls++;trace.push('user-write-callback');});trace.push('write-return',accepted);
  sink.end();trace.push('after-end');await closed;
  check(writeCalls===1&&callbackCalls===1&&bytes===64&&hash===expected&&finish===1&&close===1,'Writable valid-operation invariants failed');
  results.push({id:'writable-'+(deferred?'microtask':'sync')+'-hwm'+highWaterMark,kind:'writable',callbackMode:deferred?'queueMicrotask':'synchronous',highWaterMark,inputBytes:64,
   accepted,writeCalls,callbackCalls,bytes,checksum:hash,finish,close,events:trace.events});
 }
 for(const deferred of [false,true]){
  const trace=boundedTrace();let bytes=0,hash=2166136261,writeCalls=0,callbackCalls=0;const counts={sourceEnd:0,sourceFinish:0,sourceClose:0,passEnd:0,passFinish:0,passClose:0,sinkFinish:0,sinkClose:0};
  const source=new stream.PassThrough({highWaterMark:64}),pass=new stream.PassThrough({highWaterMark:64});
  const sink=new stream.Writable({highWaterMark:64,write(chunk,encoding,callback){writeCalls++;trace.push('sink-write',chunk.length);
   for(let i=0;i<chunk.length;i++){check(chunk[i]===input[bytes+i],'Pipeline byte mismatch');hash=Math.imul(hash^chunk[i],16777619)>>>0;}bytes+=chunk.length;
   const complete=()=>{callbackCalls++;trace.push('sink-write-complete');callback();};if(deferred)queueMicrotask(complete);else complete();}});
  const closed=[];for(const[name,target]of[['source',source],['pass',pass],['sink',sink]]){
   closed.push(new Promise((resolve,reject)=>{target.on('error',reject);target.once('close',resolve);}));
   for(const event of ['end','finish','close'])if(name!=='sink'||event!=='end')target.on(event,()=>{const key=name+event[0].toUpperCase()+event.slice(1);counts[key]++;trace.push(name,event);});
  }
  trace.push('before-pipeline');const completed=new Promise((resolve,reject)=>stream.pipeline(source,pass,sink,error=>{if(error){reject(error);return;}trace.push('pipeline-callback');resolve();}));
  trace.push('pipeline-registered');source.end(Buffer.from(input));trace.push('source-end-return');await Promise.all([...closed,completed]);
  check(writeCalls===1&&callbackCalls===1&&bytes===64&&hash===expected,'Pipeline valid-operation invariants failed');check(Object.values(counts).every(value=>value===1),'Pipeline terminal events must occur once');
  results.push({id:'passthrough-pipeline-'+(deferred?'microtask':'sync'),kind:'pipeline',callbackMode:deferred?'queueMicrotask':'synchronous',highWaterMark:64,inputBytes:64,
   writeCalls,callbackCalls,bytes,checksum:hash,counts,events:trace.events});
 }
 for(const explicitUtf8 of [false,true]){
  const trace=boundedTrace(),payload={id:1};let writeCalls=0,callbackCalls=0,finish=0,close=0,accepted,samePayload=false,valueId,encoding;
  let resolveClosed,rejectClosed;const closed=new Promise((resolve,reject)=>{resolveClosed=resolve;rejectClosed=reject;});
  const sink=new stream.Writable({objectMode:true,write(value,suppliedEncoding,callback){writeCalls++;samePayload=value===payload;valueId=value.id;
   encoding=suppliedEncoding===undefined?{type:'undefined'}:{type:typeof suppliedEncoding,value:suppliedEncoding};
   trace.push('object-write',samePayload,typeof suppliedEncoding);callback();}});
  sink.on('error',rejectClosed);sink.on('finish',()=>{finish++;trace.push('finish');});sink.on('close',()=>{close++;trace.push('close');resolveClosed();});
  const callback=error=>{if(error){rejectClosed(error);return;}callbackCalls++;trace.push('user-write-callback');};trace.push('before-write');
  accepted=explicitUtf8?sink.write(payload,'utf8',callback):sink.write(payload,callback);trace.push('write-return',accepted);sink.end();trace.push('after-end');await closed;
  check(writeCalls===1&&callbackCalls===1&&samePayload&&valueId===1&&finish===1&&close===1,'Object-mode valid-operation invariants failed');
  check(encoding.type==='undefined'||encoding.type==='string'||(encoding.type==='object'&&encoding.value===null),'Finite encoding carrier expected');
  results.push({id:'object-'+(explicitUtf8?'explicit-utf8':'default-encoding'),kind:'object-writable',explicitUtf8,accepted,writeCalls,callbackCalls,samePayload,valueId,payloadKeys:Object.keys(payload),encoding,finish,close,events:trace.events});
 }
 return results;
}
