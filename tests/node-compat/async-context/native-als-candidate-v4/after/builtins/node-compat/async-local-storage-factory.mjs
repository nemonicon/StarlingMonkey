// SOURCE-ONLY DRAFT. All context/resource operations use the native kernel;
// this facade never wraps Promise.then or substitutes a JavaScript async stack.
export function createAsyncLocalStorage(kernel) {
  const Get=Function.call.bind(WeakMap.prototype.get);
  const Set=Function.call.bind(WeakMap.prototype.set);
  const Apply=Reflect.apply,Same=Object.is,Define=Object.defineProperty;
  const TypeErrorCtor=TypeError,states=new WeakMap();
  function state(self) {
    const result=Get(states,self);
    if(result)return result;
    const error=new TypeErrorCtor('Invalid AsyncLocalStorage receiver');
    Define(error,'code',{__proto__:null,value:'ERR_INVALID_ARG_TYPE',enumerable:true,writable:true,configurable:true});
    throw error;
  }
  class AsyncLocalStorage {
    constructor() { Set(states,this,kernel.createState()); }
    getStore() { return kernel.get(state(this),false); }
    disable() { kernel.setEnabled(state(this),false); }
    enterWith(store) {
      const token=state(this);
      kernel.setEnabled(token,true);
      kernel.set(token,store);
    }
    run(store,callback,...args) {
      const token=state(this);
      if(Same(store,kernel.get(token,false)))return Apply(callback,null,args);
      kernel.setEnabled(token,true);
      const previous=kernel.get(token,true);
      kernel.set(token,store);
      try{return Apply(callback,null,args);}finally{kernel.set(token,previous);}
    }
    exit(callback,...args) {
      const token=state(this);
      if(!kernel.enabled(token))return Apply(callback,null,args);
      kernel.setEnabled(token,false);
      try{return Apply(callback,null,args);}finally{kernel.setEnabled(token,true);}
    }
    static bind(callback) {
      if(typeof callback!=='function') {
        const error=new TypeErrorCtor('callback must be a function');
        Define(error,'code',{__proto__:null,value:'ERR_INVALID_ARG_TYPE',enumerable:true,writable:true,configurable:true});
        throw error;
      }
      const resource=kernel.capture();
      const bound=function(...args){return kernel.invoke(resource,callback,this,args);};
      Define(bound,'length',{__proto__:null,value:callback.length,configurable:true});
      return bound;
    }
    static snapshot() {
      return AsyncLocalStorage.bind((callback,...args)=>Apply(callback,undefined,args));
    }
  }
  return AsyncLocalStorage;
}

// Complete release export inventory, explicit bounded ALS support and typed
// pinned provider constants. No fake lifecycle IDs/hooks/AsyncResource facade.
export function createAsyncHooksModule(kernel,providers) {
  const Define=Object.defineProperties,ErrorCtor=Error,Freeze=Object.freeze;
  const profile='sm-node-22.14.0-m1.0';
  const deferred=operation=>function(){
    const error=new ErrorCtor(`node:async_hooks.${operation} is deferred in ${profile}`);
    Define(error,{
      code:{__proto__:null,value:'ERR_SM_NODE_UNSUPPORTED',enumerable:true,writable:true,configurable:true},
      module:{__proto__:null,value:'node:async_hooks',enumerable:true,writable:true,configurable:true},
      operation:{__proto__:null,value:operation,enumerable:true,writable:true,configurable:true},
      profile:{__proto__:null,value:profile,enumerable:true,writable:true,configurable:true},
    });
    throw error;
  };
  const AsyncLocalStorage=createAsyncLocalStorage(kernel);
  const AsyncResource=deferred('AsyncResource');
  Object.defineProperty(AsyncResource,'bind',{__proto__:null,value:deferred('AsyncResource.bind'),configurable:true,writable:true});
  for(const name of ['runInAsyncScope','emitDestroy','asyncId','triggerAsyncId','bind'])
    Object.defineProperty(AsyncResource.prototype,name,{__proto__:null,value:deferred('AsyncResource.'+name),configurable:true,writable:true});
  const createHook=deferred('createHook'),executionAsyncId=deferred('executionAsyncId');
  const triggerAsyncId=deferred('triggerAsyncId'),executionAsyncResource=deferred('executionAsyncResource');
  const asyncWrapProviders=Freeze(Object.assign(Object.create(null),providers));
  const root={AsyncLocalStorage,AsyncResource,createHook,executionAsyncId,triggerAsyncId,executionAsyncResource,asyncWrapProviders};
  return {AsyncLocalStorage,AsyncResource,createHook,executionAsyncId,triggerAsyncId,executionAsyncResource,asyncWrapProviders,default:root};
}
