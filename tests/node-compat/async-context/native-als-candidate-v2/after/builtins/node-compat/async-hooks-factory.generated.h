// Generated Source-only ALS factory; no compiled/runtime proof.
// Canonical source SHA-256: 7247c5dae6784dd94851b5929b9a1bc267bfcd7a362164950da8ed40e15746cb
static constexpr const char kAsyncLocalStorageFactorySource[] = R"SM_NODE_ALS((kernel=>{
'use strict';
// SOURCE-ONLY DRAFT. All context/resource operations use the native kernel;
// this facade never wraps Promise.then or substitutes a JavaScript async stack.
function createAsyncLocalStorage(kernel) {
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
function createAsyncHooksModule(kernel,providers) {
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

return createAsyncHooksModule(kernel,{"NONE":0,"DIRHANDLE":1,"DNSCHANNEL":2,"ELDHISTOGRAM":3,"FILEHANDLE":4,"FILEHANDLECLOSEREQ":5,"BLOBREADER":6,"FSEVENTWRAP":7,"FSREQCALLBACK":8,"FSREQPROMISE":9,"GETADDRINFOREQWRAP":10,"GETNAMEINFOREQWRAP":11,"HEAPSNAPSHOT":12,"HTTP2SESSION":13,"HTTP2STREAM":14,"HTTP2PING":15,"HTTP2SETTINGS":16,"HTTPINCOMINGMESSAGE":17,"HTTPCLIENTREQUEST":18,"JSSTREAM":19,"JSUDPWRAP":20,"MESSAGEPORT":21,"PIPECONNECTWRAP":22,"PIPESERVERWRAP":23,"PIPEWRAP":24,"PROCESSWRAP":25,"PROMISE":26,"QUERYWRAP":27,"QUIC_ENDPOINT":28,"QUIC_LOGSTREAM":29,"QUIC_PACKET":30,"QUIC_SESSION":31,"QUIC_STREAM":32,"QUIC_UDP":33,"SHUTDOWNWRAP":34,"SIGNALWRAP":35,"STATWATCHER":36,"STREAMPIPE":37,"TCPCONNECTWRAP":38,"TCPSERVERWRAP":39,"TCPWRAP":40,"TTYWRAP":41,"UDPSENDWRAP":42,"UDPWRAP":43,"SIGINTWATCHDOG":44,"WORKER":45,"WORKERHEAPSNAPSHOT":46,"WRITEWRAP":47,"ZLIB":48,"CHECKPRIMEREQUEST":49,"PBKDF2REQUEST":50,"KEYPAIRGENREQUEST":51,"KEYGENREQUEST":52,"KEYEXPORTREQUEST":53,"CIPHERREQUEST":54,"DERIVEBITSREQUEST":55,"HASHREQUEST":56,"RANDOMBYTESREQUEST":57,"RANDOMPRIMEREQUEST":58,"SCRYPTREQUEST":59,"SIGNREQUEST":60,"TLSWRAP":61,"VERIFYREQUEST":62});
}))SM_NODE_ALS";
