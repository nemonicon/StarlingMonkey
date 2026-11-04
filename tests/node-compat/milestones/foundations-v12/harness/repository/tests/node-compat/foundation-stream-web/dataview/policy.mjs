function ensure(value,message){if(!value)throw Error(message);}
export async function policyCases(web,track){
  const checks=[];
  async function reject(name,view,options,wanted){
    const stream=new web.ReadableStream({type:'bytes',start(c){c.enqueue(Uint8Array.of(7,8));c.close();}}),reader=track(stream.getReader({mode:'byob'}));
    let error;const buffer=view.buffer,before=buffer.byteLength;
    try{await reader.read(view,options);}catch(caught){error=caught;}
    ensure(error?.code===wanted,name+' error');ensure(buffer.byteLength===before,name+' input not transferred');
    const entry=await reader.read(new DataView(new ArrayBuffer(8),1,4));
    ensure(JSON.stringify([...new Uint8Array(entry.value.buffer,entry.value.byteOffset,entry.value.byteLength)])==='[7,8]',name+' queue preserved');
    await reader.closed;reader.releaseLock();checks.push(name);
  }
  await reject('min-two',new DataView(new ArrayBuffer(16),2,8),{min:2},'ERR_SM_NODE_UNSUPPORTED');
  await reject('over-limit',new DataView(new ArrayBuffer(16777217)),undefined,'ERR_SM_NODE_LIMIT');
  await reject('resizable',new DataView(new ArrayBuffer(8,{maxByteLength:16})),undefined,'ERR_SM_NODE_UNSUPPORTED');
  class Subclass extends DataView{}
  await reject('subclass',new Subclass(new ArrayBuffer(8)),undefined,'ERR_SM_NODE_UNSUPPORTED');
  let layoutGets=0;const shadowed=new DataView(new ArrayBuffer(8));
  Object.defineProperty(shadowed,'constructor',{get(){layoutGets++;throw Error();}});
  await reject('own-constructor',shadowed,undefined,'ERR_SM_NODE_UNSUPPORTED');ensure(layoutGets===0,'no own layout callbacks');
  const define=Object.defineProperty,original=Object.getOwnPropertyDescriptor(Error.prototype,'code');let gets=0,sets=0;
  try{
    define(Error.prototype,'code',{configurable:true,get(){gets++;throw Error('getter');},set(){sets++;throw Error('setter');}});
    await reject('inherited-code-setter',new DataView(new ArrayBuffer(8)),{min:0},'ERR_INVALID_ARG_VALUE');
  }finally{if(original)define(Error.prototype,'code',original);else delete Error.prototype.code;}
  ensure(gets===0&&sets===0,'own coded properties');
  return{checks,layoutGetterCalls:layoutGets,inheritedCodeGets:gets,inheritedCodeSets:sets};
}
export async function capturedIntrinsicCases(web,track){
  const DV=DataView,U8=Uint8Array,apply=Reflect.apply,isView=ArrayBuffer.isView,isInteger=Number.isInteger;
  const oldRead=web.ReadableStreamBYOBReader.prototype.read;
  const stream=new web.ReadableStream({type:'bytes',start(c){c.enqueue(U8.of(3,4));c.close();}}),reader=track(stream.getReader({mode:'byob'}));
  const view=new DV(new ArrayBuffer(16),3,8);let replacements=0,entry;
  function replaced(){replacements++;throw Error('replaced intrinsic');}
  try{
    globalThis.DataView=globalThis.Uint8Array=replaced;Reflect.apply=ArrayBuffer.isView=Number.isInteger=replaced;
    entry=await oldRead.call(reader,view);
  }finally{globalThis.DataView=DV;globalThis.Uint8Array=U8;Reflect.apply=apply;ArrayBuffer.isView=isView;Number.isInteger=isInteger;}
  await reader.closed;reader.releaseLock();
  ensure(replacements===0&&entry.value instanceof DV&&entry.value.byteOffset===3&&entry.value.byteLength===2,'captured adapter operations');
  return{replacementInvocations:replacements,bytes:[...new U8(entry.value.buffer,entry.value.byteOffset,entry.value.byteLength)]};
}
