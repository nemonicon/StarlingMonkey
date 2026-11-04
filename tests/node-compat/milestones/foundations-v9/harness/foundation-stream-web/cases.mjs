// Bounded ordinary public API observations. No native compression transforms,
// detached/shared/RAB lifetime probes, forced GC, faults, timers or host I/O.
export async function observeStreams(web){
  const results=[];
  async function probe(name,callback){
    try{results.push({name,value:await callback()});}
    catch(error){results.push({name,error:{name:error.name,code:error.code}});}
  }
  const ctor=value=>{
    const prototype=Object.getPrototypeOf(value),constructor=prototype?.constructor;
    return {name:constructor?.name,isFunction:typeof constructor==='function',
      prototypeIdentity:constructor?.prototype===prototype,
      instanceIdentity:typeof constructor==='function'&&value instanceof constructor,
      prototypeNames:Object.getOwnPropertyNames(prototype).sort()};
  };
  await probe('readable-basic',async()=>{
    let controller;
    const stream=new web.ReadableStream({start(value){controller=value;value.enqueue('a');value.close();}});
    const reader=stream.getReader();
    const result={locked:stream.locked,reader:ctor(reader),controller:ctor(controller),values:[await reader.read(),await reader.read()]};
    await reader.closed;reader.releaseLock();result.unlocked=!stream.locked;return result;
  });
  await probe('writable-basic',async()=>{
    let controller;const trace=[];
    const stream=new web.WritableStream({start(value){controller=value;},write(value){trace.push(value);},close(){trace.push('closed');}});
    const writer=stream.getWriter();
    const result={locked:stream.locked,writer:ctor(writer),controller:ctor(controller),desiredSize:writer.desiredSize,
      controllerSignal:typeof controller.signal};
    await writer.ready;await writer.write('a');await writer.close();await writer.closed;writer.releaseLock();
    result.trace=trace;result.unlocked=!stream.locked;return result;
  });
  await probe('readable-cancel',async()=>{
    const reason={why:'cancel'},trace=[];
    const stream=new web.ReadableStream({cancel(value){trace.push(value===reason);}});
    const reader=stream.getReader();await reader.cancel(reason);await reader.closed;reader.releaseLock();
    return {trace,unlocked:!stream.locked};
  });
  await probe('writable-abort',async()=>{
    const reason={why:'abort'},trace=[];
    const stream=new web.WritableStream({abort(value){trace.push(value===reason);}});
    const writer=stream.getWriter();const closed=writer.closed.catch(value=>value===reason);
    await writer.abort(reason);const rejectedWithReason=await closed;writer.releaseLock();
    return {trace,rejectedWithReason,unlocked:!stream.locked};
  });
  await probe('writable-backpressure',async()=>{
    let release;const trace=[];
    const stream=new web.WritableStream({write(value){trace.push(value);return new Promise(resolve=>{release=resolve;});}},
      {highWaterMark:1,size(){return 1;}});
    const writer=stream.getWriter();await writer.ready;
    const pending=writer.write('a');const desiredDuring=writer.desiredSize;
    let ready=false;const readiness=writer.ready.then(()=>{ready=true;});
    for(let index=0;index<8&&!release;index++)await Promise.resolve();
    if(!release)throw Error('write callback did not run within bounded promise turns');
    const readyDuring=ready;release();await pending;await readiness;
    const desiredAfter=writer.desiredSize;await writer.close();await writer.closed;writer.releaseLock();
    return {trace,desiredDuring,readyDuring,desiredAfter,readyAfter:ready};
  });
  await probe('transform-basic',async()=>{
    let controller;
    const stream=new web.TransformStream({start(value){controller=value;},transform(value,control){control.enqueue(value+'!');}});
    const writer=stream.writable.getWriter(),reader=stream.readable.getReader();
    const pending=writer.write('a'),first=await reader.read();await pending;
    const closing=writer.close(),last=await reader.read();await closing;await writer.closed;await reader.closed;
    writer.releaseLock();reader.releaseLock();return {controller:ctor(controller),first,last};
  });
  await probe('pipe-to',async()=>{
    const trace=[];
    const source=new web.ReadableStream({start(controller){controller.enqueue('a');controller.enqueue('b');controller.close();}});
    const target=new web.WritableStream({write(value){trace.push(value);},close(){trace.push('close');}});
    await source.pipeTo(target);return {trace,sourceUnlocked:!source.locked,targetUnlocked:!target.locked};
  });
  await probe('tee',async()=>{
    const chunk={value:1};
    const source=new web.ReadableStream({start(controller){controller.enqueue(chunk);controller.close();}});
    const [a,b]=source.tee(),ra=a.getReader(),rb=b.getReader();
    const va=await ra.read(),vb=await rb.read();const result={sameChunk:va.value===vb.value,value:va.value.value,
      closed:[(await ra.read()).done,(await rb.read()).done]};
    await ra.closed;await rb.closed;ra.releaseLock();rb.releaseLock();return result;
  });
  await probe('byob-basic',async()=>{
    let controller,request;
    const source=new web.ReadableStream({type:'bytes',pull(value){
      controller=value;request=value.byobRequest;
      request.view[0]=7;request.view[1]=8;request.respond(2);value.close();
    }});
    const reader=source.getReader({mode:'byob'}),input=new Uint8Array(8);
    const result=await reader.read(input);await reader.closed;reader.releaseLock();
    return {bytes:[...result.value],done:result.done,inputByteLength:input.byteLength,returnedByteLength:result.value.byteLength,
      reader:ctor(reader),controller:ctor(controller),request:ctor(request),unlocked:!source.locked};
  });
  await probe('byob-minimum',async()=>{
    let count=0;
    const source=new web.ReadableStream({type:'bytes',pull(controller){
      controller.byobRequest.view[0]=++count;controller.byobRequest.respond(1);if(count===2)controller.close();
    }});
    const reader=source.getReader({mode:'byob'});
    const first=await reader.read(new Uint8Array(4),{min:2});
    const second=await reader.read(new Uint8Array(4));
    if(!second.done)await reader.read(new Uint8Array(4));
    await reader.closed;reader.releaseLock();
    return {first:[...first.value],firstDone:first.done,second:[...second.value],secondDone:second.done,pulls:count};
  });
  await probe('queuing-strategies',async()=>{
    const count=new web.CountQueuingStrategy({highWaterMark:3}),bytes=new web.ByteLengthQueuingStrategy({highWaterMark:8});
    return {countHWM:count.highWaterMark,countSize:count.size('a'),bytesHWM:bytes.highWaterMark,bytesSize:bytes.size(new Uint8Array(4)),
      countPrototype:Object.getOwnPropertyNames(Object.getPrototypeOf(count)).sort(),bytePrototype:Object.getOwnPropertyNames(Object.getPrototypeOf(bytes)).sort()};
  });
  return results;
}
