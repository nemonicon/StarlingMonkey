// UNCOMPILED guest facade; secure bytes come only from the private C++ kernel.
export function createRandomOperations({rng,Buffer,webcrypto,nextTick},web=globalThis){
 const apply=Reflect.apply,define=Object.defineProperty,U8=web.Uint8Array,AB=web.ArrayBuffer;
 const proto=Object.getPrototypeOf(U8.prototype),getLength=Object.getOwnPropertyDescriptor(proto,'byteLength').get,getOffset=Object.getOwnPropertyDescriptor(proto,'byteOffset').get,getBuffer=Object.getOwnPropertyDescriptor(proto,'buffer').get,getTag=Object.getOwnPropertyDescriptor(proto,Symbol.toStringTag).get;
 const abLength=Object.getOwnPropertyDescriptor(AB.prototype,'byteLength').get,abResizable=Object.getOwnPropertyDescriptor(AB.prototype,'resizable')?.get,abDetached=Object.getOwnPropertyDescriptor(AB.prototype,'detached')?.get;
 const from=Buffer.from,kcheck=rng.check,kbytes=rng.bytes,kfill=rng.fill,kuuid=rng.uuid,nativeTick=nextTick;
 const TypeErrorCtor=TypeError,RangeErrorCtor=RangeError,finite=Number.isFinite,trunc=Math.trunc,isArray=Array.isArray;
 function fail(code,message,Ctor=TypeErrorCtor){const e=new Ctor(message);define(e,'code',{value:code,writable:true,enumerable:true,configurable:true});throw e;}
 function size(value,max=16777216,name='size'){if(typeof value!=='number')fail('ERR_INVALID_ARG_TYPE',name+' must be a number');if(!finite(value)||value<0||value>max)fail('ERR_OUT_OF_RANGE',name+' outside bounded range',RangeErrorCtor);return trunc(value);}
 function fixed(backing){let n;try{n=apply(abLength,backing,[]);}catch{fail('ERR_SM_NODE_UNSUPPORTED','Random backing must be nonshared ArrayBuffer');}if(abResizable&&apply(abResizable,backing,[])||abDetached&&apply(abDetached,backing,[]))fail('ERR_SM_NODE_UNSUPPORTED','Random backing must be fixed/live');if(!abDetached&&n===0)try{new U8(backing,0,0);}catch{fail('ERR_SM_NODE_UNSUPPORTED','Detached random backing');}return n;}
 function view(value){if(value instanceof AB)return new U8(value,0,fixed(value));let backing;try{if(apply(getTag,value,[])!=='Uint8Array')throw 0;backing=apply(getBuffer,value,[]);}catch{fail('ERR_INVALID_ARG_TYPE','Random target must be Buffer, Uint8Array or ArrayBuffer');}fixed(backing);return value;}
 function wrap(raw){const backing=apply(getBuffer,raw,[]),offset=apply(getOffset,raw,[]),length=apply(getLength,raw,[]);return apply(from,Buffer,[backing,offset,length]);}
 function randomBytes(n,callback){n=size(n);if(callback!==undefined&&typeof callback!=='function')fail('ERR_INVALID_ARG_TYPE','callback must be a function');apply(kcheck,undefined,[]);
  if(callback===undefined)return wrap(apply(kbytes,undefined,[n]));
  // Node22's zero-length callback is synchronous. Nonzero work draws entropy
  // synchronously here, then reports through the actual guest nextTick FIFO.
  if(n===0){const out=wrap(apply(kbytes,undefined,[0]));apply(callback,undefined,[null,out]);return;}
  let out,error,failed=false;try{out=wrap(apply(kbytes,undefined,[n]));}catch(e){failed=true;error=e;}
  apply(nativeTick,undefined,[()=>failed?apply(callback,undefined,[error]):apply(callback,undefined,[null,out])]);
 }
 function randomFillSync(value,offset=0,count){const target=view(value),n=apply(getLength,target,[]);if(n>16777216)fail('ERR_OUT_OF_RANGE','Random target exceeds16MiB',RangeErrorCtor);offset=size(offset,n,'offset');count=count===undefined?n-offset:size(count,n-offset,'size');apply(kcheck,undefined,[]);apply(kfill,undefined,[target,offset,count]);return value;}
 function randomUUID(options){if(options!==undefined){if(options===null||typeof options!=='object'||isArray(options))fail('ERR_INVALID_ARG_TYPE','options must be object');const disable=options.disableEntropyCache;if(disable!==undefined&&typeof disable!=='boolean')fail('ERR_INVALID_ARG_TYPE','disableEntropyCache must be boolean');}apply(kcheck,undefined,[]);return apply(kuuid,undefined,[]);}
 function getRandomValues(value){apply(kcheck,undefined,[]);return apply(webcrypto.getRandomValues,webcrypto,[value]);}
 return{randomBytes,randomFillSync,randomUUID,getRandomValues};
}
