// Pure guest failure behavior, including application initialization and new.
const ErrorCtor=Error,Define=Object.defineProperty,Defines=Object.defineProperties;
const PROFILE='sm-node-22.14.0-m0.7';
export function unsupported(module,operation){
  const fn=function(){
    const error=new ErrorCtor(`${module}.${operation} is deferred in ${PROFILE}`);
    const descriptor=value=>({__proto__:null,value,writable:true,enumerable:true,configurable:true});
    Defines(error,{__proto__:null,code:descriptor('ERR_SM_NODE_UNSUPPORTED'),module:descriptor(module),operation:descriptor(operation),profile:descriptor(PROFILE)});
    throw error;
  };
  Define(fn,'name',{__proto__:null,value:operation,configurable:true});
  return fn;
}
