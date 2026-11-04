export async function capturedIntrinsicCases(record){
  const P=Promise,then=P.prototype.then,resolve=P.resolve;
  const read=record.ReadableStreamDefaultReader.prototype.read,cancel=record.ReadableStreamDefaultReader.prototype.cancel;
  const release=record.ReadableStreamDefaultReader.prototype.releaseLock;
  const enqueue=record.ReadableStreamDefaultController.prototype.enqueue,close=record.ReadableStreamDefaultController.prototype.close;
  const apply=Reflect.apply,setPrototype=Object.setPrototypeOf;
  const savedGlobal={Promise,TypeError};let replacements=0,values=[],stopped,error;
  function replaced(){replacements++;throw Error('Replaced intrinsic invoked');}
  try{
    globalThis.Promise=globalThis.TypeError=replaced;
    // Async-from-sync uses a native async-generator bridge, like Node22.
    // Its promise assimilation may observe Promise.prototype.then. Do not
    // claim to remove those user-observable protocol lookups.
    P.resolve=replaced;Reflect.apply=Object.setPrototypeOf=replaced;
    record.ReadableStreamDefaultReader.prototype.read=record.ReadableStreamDefaultReader.prototype.cancel=
      record.ReadableStreamDefaultReader.prototype.releaseLock=replaced;
    record.ReadableStreamDefaultController.prototype.enqueue=record.ReadableStreamDefaultController.prototype.close=replaced;
    const stream=record.ReadableStream.from([1,2]),iterator=stream.values();
    values.push((await iterator.next()).value);values.push((await iterator.next()).value);
    stopped=await iterator.return('stop');
    try{record.ReadableStream.prototype.values.call({});}catch(caught){error=caught;}
  }finally{
    globalThis.Promise=savedGlobal.Promise;globalThis.TypeError=savedGlobal.TypeError;
    P.prototype.then=then;P.resolve=resolve;Reflect.apply=apply;Object.setPrototypeOf=setPrototype;
    record.ReadableStreamDefaultReader.prototype.read=read;record.ReadableStreamDefaultReader.prototype.cancel=cancel;
    record.ReadableStreamDefaultReader.prototype.releaseLock=release;
    record.ReadableStreamDefaultController.prototype.enqueue=enqueue;record.ReadableStreamDefaultController.prototype.close=close;
  }
  if(replacements!==0||JSON.stringify(values)!=='[1,2]'||!stopped?.done||stopped.value!=='stop'||error?.code!=='ERR_INVALID_THIS')
    throw{replacements,values,stopped,errorCode:error?.code};
  return{replacementInvocations:replacements,values,stopped,errorCode:error.code};
}
