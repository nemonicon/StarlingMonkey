// Ordinary retained-constructor operations only, separate from eleven-case gate.
export async function observeConstructors(web){
  function attempt(callback){try{callback();return {returned:true};}catch(error){return {name:error.name,code:error.code};}}
  let controller;
  const source=new web.WritableStream({start(value){controller=value;}}),original=source.getWriter();
  const Writer=Object.getPrototypeOf(original).constructor;
  const abandonedClosed=original.closed.catch(error=>error.name);
  original.releaseLock();await abandonedClosed;await source.abort();
  const trace=[];
  const target=new web.WritableStream({write(chunk){trace.push(chunk);},close(){trace.push('closed');}});
  const writer=new Writer(target);
  const writerResult={name:Writer.name,length:Writer.length,function:typeof Writer==='function',
    prototypeIdentity:Object.getPrototypeOf(writer)===Writer.prototype,instanceIdentity:writer instanceof Writer,
    locked:target.locked};
  await writer.ready;await writer.write('x');await writer.close();await writer.closed;writer.releaseLock();
  writerResult.trace=trace;writerResult.unlocked=!target.locked;
  const plainStream=new web.WritableStream();
  writerResult.plainCall=attempt(()=>Writer(plainStream));await plainStream.abort();
  writerResult.invalidInput=attempt(()=>new Writer({}));
  const lockedStream=new web.WritableStream(),lock=lockedStream.getWriter();
  writerResult.lockedInput=attempt(()=>new Writer(lockedStream));await lock.close();await lock.closed;lock.releaseLock();
  const WritableController=Object.getPrototypeOf(controller).constructor;
  let transformController;
  const transform=new web.TransformStream({start(value){transformController=value;}});
  const TransformController=Object.getPrototypeOf(transformController).constructor;
  const tw=transform.writable.getWriter(),tr=transform.readable.getReader(),closing=tw.close();
  await tr.read();await closing;await tw.closed;await tr.closed;tw.releaseLock();tr.releaseLock();
  const controllers={};
  for(const[name,Ctor,instance]of [['WritableStreamDefaultController',WritableController,controller],
    ['TransformStreamDefaultController',TransformController,transformController]]){
    controllers[name]={name:Ctor.name,length:Ctor.length,function:typeof Ctor==='function',
      prototypeIdentity:Object.getPrototypeOf(instance)===Ctor.prototype,instanceIdentity:instance instanceof Ctor,
      call:attempt(()=>Ctor()),construct:attempt(()=>new Ctor())};
  }
  return{writer:writerResult,controllers};
}
