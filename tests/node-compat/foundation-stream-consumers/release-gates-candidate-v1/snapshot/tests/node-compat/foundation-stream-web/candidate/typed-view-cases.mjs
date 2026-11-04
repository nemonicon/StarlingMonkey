// Ordinary fixed/unshared, unmodified standard typed views only. No Buffer,
// subclass, shared/RAB, Proxy or detached-input native read is attempted.
export async function typedViewCases(web,track=(reader)=>reader){
  const results=[];
  for(const Type of [Int8Array,Uint8Array,Uint8ClampedArray,Int16Array,Uint16Array,Int32Array,Uint32Array,
    Float32Array,Float64Array,BigInt64Array,BigUint64Array,DataView]){
    const source=new web.ReadableStream({type:'bytes',start(controller){
      const bytes=new Uint8Array(16);for(let i=0;i<bytes.length;i++)bytes[i]=i;
      controller.enqueue(bytes);controller.close();
    }});
    const buffer=new ArrayBuffer(32),view=Type===DataView?new Type(buffer,8,16):new Type(buffer,8,16/Type.BYTES_PER_ELEMENT);
    const reader=track(source.getReader({mode:'byob'}));
    const closed=reader.closed.catch(()=>{});
    try{
      const result=await reader.read(view,{min:1}),value=result.value;
      results.push({name:Type.name,bytes:[...new Uint8Array(value.buffer,value.byteOffset,value.byteLength)],
        returnedType:value.constructor.name,prototypeIdentity:Object.getPrototypeOf(value)===Type.prototype,
        byteOffset:value.byteOffset,byteLength:value.byteLength,bufferLength:value.buffer.byteLength,
        oldBufferLength:buffer.byteLength,separateBuffer:value.buffer!==buffer,done:result.done});
    }catch(error){
      const item={name:Type.name,error:{name:error.name,code:error.code},oldBufferLength:buffer.byteLength};
      // Only the new explicit guard is expected here. Never repeat the known
      // old-native DataView call once its null-constructor gap is identified.
      if(error.code==='ERR_SM_NODE_UNSUPPORTED'){
        const recovery=await reader.read(new Uint8Array(16));item.recovery=[...recovery.value];
      }
      results.push(item);
    }
    await reader.cancel();await closed;reader.releaseLock();
  }
  return results;
}
