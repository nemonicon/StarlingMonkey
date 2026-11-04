// FIXTURE ONLY: deployed ordinary objects recover three retained constructors.
// Production must use reviewed native roots/API, not these temporary streams.
// The registry proves only fixture-registered native readers. It is NOT a
// replacement for public JS::IsReadableStreamBYOBReader in a real integration.
export async function fixtureRecord(web=globalThis){
  const define=Object.defineProperty,remove=Reflect.deleteProperty,descriptor=Object.getOwnPropertyDescriptor;
  const mutationTargets=[[web.ReadableStreamBYOBReader.prototype,'read'],[web.ReadableStream,'from'],
    [web.ReadableStream.prototype,'values'],[web.ReadableStream.prototype,Symbol.asyncIterator]];
  const originals=mutationTargets.map(([object,key])=>descriptor(object,key));
  let writableController,transformController;
  const writable=new web.WritableStream({start(controller){writableController=controller;}});
  const writer=writable.getWriter(),Writer=Object.getPrototypeOf(writer).constructor;
  const closed=writer.closed.catch(()=>{});writer.releaseLock();await closed;await writable.abort();
  const transform=new web.TransformStream({start(controller){transformController=controller;}});
  const controllerPrototype=Object.getPrototypeOf(transformController);
  for(const key of ['desiredSize','enqueue','error','terminate']){
    mutationTargets.push([controllerPrototype,key]);originals.push(descriptor(controllerPrototype,key));
  }
  const tw=transform.writable.getWriter(),tr=transform.readable.getReader(),closing=tw.close();
  await tr.read();await closing;await tw.closed;await tr.closed;tw.releaseLock();tr.releaseLock();
  const registry=new WeakSet(),add=registry.add.bind(registry),has=registry.has.bind(registry);
  const record={ReadableStream:web.ReadableStream,ReadableStreamDefaultReader:web.ReadableStreamDefaultReader,
    ReadableStreamBYOBReader:web.ReadableStreamBYOBReader,ReadableStreamBYOBRequest:web.ReadableStreamBYOBRequest,
    ReadableByteStreamController:web.ReadableByteStreamController,ReadableStreamDefaultController:web.ReadableStreamDefaultController,
    WritableStream:web.WritableStream,WritableStreamDefaultWriter:Writer,
    WritableStreamDefaultController:Object.getPrototypeOf(writableController).constructor,
    ByteLengthQueuingStrategy:web.ByteLengthQueuingStrategy,CountQueuingStrategy:web.CountQueuingStrategy,
    TransformStream:web.TransformStream,TransformStreamDefaultController:Object.getPrototypeOf(transformController).constructor,
    TextEncoder:web.TextEncoder,TextDecoder:web.TextDecoder,isReadableStreamBYOBReader:has};
  return{record,track(reader){add(reader);return reader;},restore(){
    for(let index=0;index<mutationTargets.length;index++){const[object,key]=mutationTargets[index],original=originals[index];
      if(original)define(object,key,original);else remove(object,key);
    }
    return mutationTargets.every(([object,key],index)=>{
      const current=descriptor(object,key),original=originals[index];if(!current||!original)return current===original;
      return['value','get','set','enumerable','writable','configurable'].every(field=>current[field]===original[field]);
    });
  },audit:{scope:'Fixture-registered native reader brand only; no arbitrary production/cross-realm brand proof',
    privateKeys:Object.keys(record).sort(),temporaryStreamsCleaned:true,compressionConstructorsCaptured:false}};
}
