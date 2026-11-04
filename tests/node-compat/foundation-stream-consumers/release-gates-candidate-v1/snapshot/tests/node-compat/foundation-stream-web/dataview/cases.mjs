function errorValue(error){return{name:error?.name,...(error?.code!==undefined?{code:error.code}:{})};}
async function outcome(invoke){try{return{value:await invoke()};}catch(error){return{error:errorValue(error)};}}
function describe(entry){
  if(entry.value===undefined)return{done:entry.done,undefinedValue:true};
  const view=entry.value;
  return{done:entry.done,constructor:view.constructor.name,dataView:view instanceof DataView,
    offset:view.byteOffset,length:view.byteLength,bufferLength:view.buffer.byteLength,
    bytes:[...new Uint8Array(view.buffer,view.byteOffset,view.byteLength)]};
}
export async function dataViewCases(web,track=value=>value){
  const S=web.ReadableStream,cases=[];
  async function test(name,run){cases.push({name,...await outcome(run)});}
  for(const[offset,length]of [[0,8],[4,8],[8,16]])await test('queued-offset-'+offset,async()=>{
    const stream=new S({type:'bytes',start(c){c.enqueue(Uint8Array.of(2,3,4));c.close();}}),reader=track(stream.getReader({mode:'byob'}));
    const buffer=new ArrayBuffer(32),view=new DataView(buffer,offset,length),result=await reader.read(view);
    const first=describe(result),oldBytes=buffer.byteLength,resultDistinct=result.value.buffer!==buffer;
    const last=describe(await reader.read(new DataView(new ArrayBuffer(16),2,8)));
    await reader.closed;reader.releaseLock();return{first,last,oldBytes,resultDistinct,locked:stream.locked};
  });
  await test('closed-empty-view-result',async()=>{
    const stream=new S({type:'bytes',start(c){c.close();}}),reader=track(stream.getReader({mode:'byob'}));
    const buffer=new ArrayBuffer(16),entry=await reader.read(new DataView(buffer,4,8));
    const result={entry:describe(entry),oldBytes:buffer.byteLength};await reader.closed;reader.releaseLock();return result;
  });
  await test('byob-request-respond',async()=>{
    const trace=[];const stream=new S({type:'bytes',pull(c){const request=c.byobRequest;
      trace.push({constructor:request.view.constructor.name,length:request.view.byteLength,offset:request.view.byteOffset});
      request.view.set([6,7]);request.respond(2);c.close();}}),reader=track(stream.getReader({mode:'byob'}));
    const buffer=new ArrayBuffer(24),entry=await reader.read(new DataView(buffer,5,8));
    await reader.closed;reader.releaseLock();return{trace,entry:describe(entry),oldBytes:buffer.byteLength};
  });
  await test('partial-queue-remains',async()=>{
    const stream=new S({type:'bytes',start(c){c.enqueue(Uint8Array.from([0,1,2,3,4,5]));c.close();}}),reader=track(stream.getReader({mode:'byob'}));
    const entries=[];for(const length of [2,8,8])entries.push(describe(await reader.read(new DataView(new ArrayBuffer(16),3,length))));
    await reader.closed;reader.releaseLock();return entries;
  });
  await test('pending-cancel-undefined-result',async()=>{
    let cancelReason;const reason={tag:'cancel'},stream=new S({type:'bytes',cancel(value){cancelReason=value;}}),reader=track(stream.getReader({mode:'byob'}));
    const buffer=new ArrayBuffer(16),pending=reader.read(new DataView(buffer,4,8));
    const detachedBeforeCancel=buffer.byteLength===0;await reader.cancel(reason);const entry=describe(await pending);
    await reader.closed;reader.releaseLock();return{entry,detachedBeforeCancel,reasonSame:cancelReason===reason,locked:stream.locked};
  });
  await test('pending-error-identity',async()=>{
    let control;const reason={},stream=new S({type:'bytes',start(c){control=c;}}),reader=track(stream.getReader({mode:'byob'}));
    const handled=reader.closed.catch(error=>error===reason),buffer=new ArrayBuffer(16),pending=reader.read(new DataView(buffer,2,8));
    control.error(reason);let same=false;try{await pending;}catch(error){same=error===reason;}const closedSame=await handled;reader.releaseLock();return{same,closedSame,oldBytes:buffer.byteLength,locked:stream.locked};
  });
  await test('already-errored-no-transfer',async()=>{
    const reason={},stream=new S({type:'bytes',start(c){c.error(reason);}}),reader=track(stream.getReader({mode:'byob'}));
    const handled=reader.closed.catch(()=>{}),buffer=new ArrayBuffer(16);let same=false;try{await reader.read(new DataView(buffer,3,8));}catch(error){same=error===reason;}
    await handled;reader.releaseLock();return{same,oldBytes:buffer.byteLength,locked:stream.locked};
  });
  await test('released-reader-rejects-before-transfer',async()=>{
    const stream=new S({type:'bytes'}),reader=track(stream.getReader({mode:'byob'}));reader.closed.catch(()=>{});reader.releaseLock();
    const buffer=new ArrayBuffer(16),result=await outcome(()=>reader.read(new DataView(buffer,2,8)));await stream.cancel();return{result,oldBytes:buffer.byteLength};
  });
  await test('concurrent-reads',async()=>{
    const stream=new S({type:'bytes',start(c){c.enqueue(Uint8Array.of(1,2,3,4));c.close();}}),reader=track(stream.getReader({mode:'byob'}));
    const buffers=[new ArrayBuffer(16),new ArrayBuffer(16),new ArrayBuffer(16)];
    const entries=await Promise.all(buffers.map(buffer=>reader.read(new DataView(buffer,2,2)).then(describe)));
    await reader.closed;reader.releaseLock();return{entries,oldBytes:buffers.map(buffer=>buffer.byteLength)};
  });
  for(const min of [undefined,null,1,0,-1,1.5,'1',9])await test('min-'+String(min),async()=>{
    const trace=[],stream=new S({type:'bytes',start(c){c.enqueue(Uint8Array.of(1));c.close();}}),reader=track(stream.getReader({mode:'byob'}));
    const buffer=new ArrayBuffer(16),result=await outcome(async()=>describe(await reader.read(new DataView(buffer,2,8),{get min(){trace.push('min');return min;}})));
    await reader.cancel();await reader.closed;reader.releaseLock();return{result,trace,oldBytes:buffer.byteLength};
  });
  for(const length of [0])await test('empty-view-before-min',async()=>{
    let gets=0;const stream=new S({type:'bytes'}),reader=track(stream.getReader({mode:'byob'})),buffer=new ArrayBuffer(16);
    const result=await outcome(()=>reader.read(new DataView(buffer,2,length),{get min(){gets++;return 1;}}));
    await reader.cancel();reader.releaseLock();return{result,gets,oldBytes:buffer.byteLength};
  });
  await test('detached-by-min-getter',async()=>{
    const stream=new S({type:'bytes'}),reader=track(stream.getReader({mode:'byob'})),buffer=new ArrayBuffer(16),view=new DataView(buffer,2,8);
    const result=await outcome(()=>reader.read(view,{get min(){buffer.transfer();return 1;}}));
    await reader.cancel();reader.releaseLock();return{result,oldBytes:buffer.byteLength};
  });
  await test('throwing-min-queue-preserved',async()=>{
    const reason={},stream=new S({type:'bytes',start(c){c.enqueue(Uint8Array.of(7,8));c.close();}}),reader=track(stream.getReader({mode:'byob'}));
    const buffer=new ArrayBuffer(16),view=new DataView(buffer,2,8);let same=false;
    try{await reader.read(view,{get min(){throw reason;}});}catch(error){same=error===reason;}
    const before=buffer.byteLength,result=describe(await reader.read(view));await reader.closed;reader.releaseLock();return{same,before,result};
  });
  await test('untouched-backing-outside-view',async()=>{
    const stream=new S({type:'bytes',start(c){c.enqueue(Uint8Array.of(1,2,3));c.close();}}),reader=track(stream.getReader({mode:'byob'}));
    const buffer=new ArrayBuffer(24);new Uint8Array(buffer).fill(0xa5);const entry=await reader.read(new DataView(buffer,5,8));
    const result={entry:describe(entry),allBytes:[...new Uint8Array(entry.value.buffer)],oldBytes:buffer.byteLength};
    await reader.closed;reader.releaseLock();return result;
  });
  await test('close-pending-with-zero-response',async()=>{
    const stream=new S({type:'bytes',pull(c){const request=c.byobRequest;c.close();request.respond(0);}}),reader=track(stream.getReader({mode:'byob'}));
    const buffer=new ArrayBuffer(16),entry=await reader.read(new DataView(buffer,2,8));
    await reader.closed;reader.releaseLock();return{entry:describe(entry),oldBytes:buffer.byteLength};
  });
  await test('source-type-error-identity',async()=>{
    const reason=new TypeError('application'),stream=new S({type:'bytes',start(c){c.error(reason);}}),reader=track(stream.getReader({mode:'byob'}));
    reader.closed.catch(()=>{});let same=false;try{await reader.read(new DataView(new ArrayBuffer(16),2,8));}catch(error){same=error===reason;}
    reader.releaseLock();return{same};
  });
  await test('cancel-rejection-pending-result',async()=>{
    const reason={},stream=new S({type:'bytes',cancel(){throw reason;}}),reader=track(stream.getReader({mode:'byob'}));
    const buffer=new ArrayBuffer(16),pending=reader.read(new DataView(buffer,2,8));let same=false;
    try{await reader.cancel();}catch(error){same=error===reason;}const entry=describe(await pending);await reader.closed;reader.releaseLock();return{same,entry,oldBytes:buffer.byteLength};
  });
  return cases;
}
