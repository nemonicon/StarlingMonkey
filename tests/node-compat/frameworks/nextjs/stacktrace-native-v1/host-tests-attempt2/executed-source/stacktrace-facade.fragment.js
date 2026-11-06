// Proposed bounded global Error extension; native provenance API is required.
// Creation installs only pure JS descriptors. Capture acquires no host resource.
function installStructuredStackTrace(kernel) {
  const ErrorCtor=globalThis.Error,TypeErrorCtor=globalThis.TypeError,RangeErrorCtor=globalThis.RangeError;
  const define=Object.defineProperty,apply=Reflect.apply,errorToString=ErrorCtor.prototype.toString;
  const token={},MAX_FRAMES=128,PROFILE='sm-node-error-22.14.0-v1';
  function failure(code,operation,message,Type=ErrorCtor){const e=new Type(message);Object.assign(e,{code,operation,profile:PROFILE});return e;}
  function unavailable(operation){throw failure('ERR_SM_NODE_UNSUPPORTED',operation,operation+' is outside '+PROFILE);}
  if(typeof kernel.captureFrames!=='function')throw failure('ERR_SM_NODE_STACK_PROVIDER','Error.captureStackTrace','Native SavedFrame provider is required');
  class CallSite {
    #data;
    constructor(secret,data){if(secret!==token)throw failure('ERR_INVALID_ARG_TYPE','CallSite','CallSite cannot be constructed by applications',TypeErrorCtor);this.#data=data;}
    getFileName(){return this.#data.source===''?null:this.#data.source;}
    getLineNumber(){return this.#data.line===0?null:this.#data.line;}
    getColumnNumber(){return this.#data.column===0?null:this.#data.column;}
    getFunctionName(){return this.#data.functionName;}
    isEval(){return this.#data.isEval;}
    getEvalOrigin(){if(this.#data.isEval)unavailable('CallSite.getEvalOrigin');return undefined;}
    toString(){
      if(this.#data.isEval)unavailable('CallSite.toString.eval');
      let location=this.getFileName()??'<anonymous>';
      if(this.#data.line)location+=':'+this.#data.line;
      if(this.#data.column)location+=':'+this.#data.column;
      return this.#data.functionName?this.#data.functionName+' ('+location+')':location;
    }
    getThis(){unavailable('CallSite.getThis');}
    getFunction(){unavailable('CallSite.getFunction');}
    getTypeName(){unavailable('CallSite.getTypeName');}
    getMethodName(){unavailable('CallSite.getMethodName');}
    isToplevel(){unavailable('CallSite.isToplevel');}
    isNative(){unavailable('CallSite.isNative');}
    isConstructor(){unavailable('CallSite.isConstructor');}
    isAsync(){unavailable('CallSite.isAsync');}
    isPromiseAll(){unavailable('CallSite.isPromiseAll');}
    getPromiseIndex(){unavailable('CallSite.getPromiseIndex');}
  }
  function sites(records,limit){
    if(!Array.isArray(records)||records.length>limit)throw failure('ERR_SM_NODE_STACK_PROVIDER','Error.captureStackTrace','Invalid bounded native frame array');
    const output=[];
    for(let i=0;i<records.length;i++){
      const element=Object.getOwnPropertyDescriptor(records,String(i));
      if(!element||!Object.hasOwn(element,'value')||!element.value||typeof element.value!=='object')
        throw failure('ERR_SM_NODE_STACK_PROVIDER','Error.captureStackTrace','Native frame array must have dense own data elements');
      const fields=Object.getOwnPropertyDescriptors(element.value),data={};
      for(const name of ['source','functionName','line','column','isEval']){
        if(!Object.hasOwn(fields,name))throw failure('ERR_SM_NODE_STACK_PROVIDER','Error.captureStackTrace','Native frame fields must be own data properties');
        const d=fields[name];
        if(!d||!Object.hasOwn(d,'value'))throw failure('ERR_SM_NODE_STACK_PROVIDER','Error.captureStackTrace','Native frame fields must be own data properties');
        Object.defineProperty(data,name,{value:d.value,enumerable:true});
      }
      if(typeof data.source!=='string'||!(data.functionName===null||typeof data.functionName==='string')||
         typeof data.isEval!=='boolean'||!Number.isInteger(data.line)||data.line<0||data.line>0xffffffff||!Number.isInteger(data.column)||data.column<0||data.column>0xffffffff)
        throw failure('ERR_SM_NODE_STACK_PROVIDER','Error.captureStackTrace','Native frame metadata/provenance is missing or invalid');
      output.push(new CallSite(token,data));
    }
    return output;
  }
  function defaultFormat(target,frames){const heading=apply(errorToString,target,[]);return heading+(frames.length?'\n'+frames.map(f=>'    at '+f.toString()).join('\n'):'');}
  const capture={captureStackTrace(target,constructorOpt){
    if(target===null||!['object','function'].includes(typeof target))throw failure('ERR_INVALID_ARG_TYPE','Error.captureStackTrace','Target must be an object or function',TypeErrorCtor);
    const limit=ErrorCtor.stackTraceLimit;
    if(typeof limit!=='number')throw failure('ERR_INVALID_ARG_TYPE','Error.stackTraceLimit','Stack limit must be a finite integer',TypeErrorCtor);
    if(!Number.isFinite(limit)||!Number.isInteger(limit)||limit<0||limit>MAX_FRAMES)throw failure('ERR_SM_NODE_STACK_LIMIT','Error.stackTraceLimit','Stack limit must be in 0..128',RangeErrorCtor);
    const startAfter=typeof constructorOpt==='function'?constructorOpt:capture;
    const frames=sites(limit===0?[]:kernel.captureFrames(limit,startAfter),limit);
    let computed=false,formatting=false,cached;
    const get=({get stack(){
      if(computed)return cached;
      if(formatting)return defaultFormat(target,frames);
      formatting=true;
      try{const hook=ErrorCtor.prepareStackTrace;const value=typeof hook==='function'?apply(hook,ErrorCtor,[target,frames]):defaultFormat(target,frames);cached=value;computed=true;return value;}
      finally{formatting=false;}
    }});
    const getter=Object.getOwnPropertyDescriptor(get,'stack').get;
    const setter=({set stack(value){cached=value;computed=true;}});
    define(target,'stack',{get:getter,set:Object.getOwnPropertyDescriptor(setter,'stack').set,enumerable:false,configurable:true});
    return undefined;
  }}.captureStackTrace;
  if(!Object.hasOwn(ErrorCtor,'stackTraceLimit'))define(ErrorCtor,'stackTraceLimit',{value:10,writable:true,enumerable:true,configurable:true});
  define(ErrorCtor,'captureStackTrace',{value:capture,writable:true,enumerable:false,configurable:true});
}
