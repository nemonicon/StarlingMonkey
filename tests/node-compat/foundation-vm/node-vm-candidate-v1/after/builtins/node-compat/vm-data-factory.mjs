// Native realm/evaluation is mandatory. This is not a JS VM or context fallback.
export function createVmModule(kernel) {
  const Define=Object.defineProperty,Descriptors=Object.getOwnPropertyDescriptors;
  const Keys=Reflect.ownKeys,Delete=Reflect.deleteProperty,Create=Object.create;
  const Entries=Object.entries,HasOwn=Object.hasOwn;
  const ErrorCtor=Error,TypeErrorCtor=TypeError;
  const profile='sm-node-22.14.0-m1.1';
  function unsupported(operation){const error=new ErrorCtor(`node:vm.${operation} is deferred in ${profile}`);
    for(const [key,value]of Entries({code:'ERR_SM_NODE_VM_UNSUPPORTED',module:'node:vm',operation,profile}))
      Define(error,key,{__proto__:null,value,writable:true,configurable:true,enumerable:true});
    throw error;}
  function runInNewContext(code,context,options){
    if(context===constants.DONT_CONTEXTIFY)return unsupported('runInNewContext.DONT_CONTEXTIFY');
    if(context===undefined)context=Create(null);
    const result=kernel.run(code,context,options);
    let commitError;
    if(!result.copyOutFailed){
      try{
        const before=Descriptors(context),after=Descriptors(result.context);
        for(const key of Keys(before))if(!HasOwn(after,key)&&!Delete(context,key))throw new TypeErrorCtor('VM copy-out deletion failed');
        for(const key of Keys(after))Define(context,key,after[key]);
      }catch(error){commitError={error};}
    }
    // Primitive/frozen throws keep ORIGINAL identity even if copy-out failed.
    if(result.threw)throw result.value;
    if(commitError)throw commitError.error;
    if(result.copyOutFailed)throw result.copyOutError;
    return result.value;
  }
  const root={runInNewContext};
  const signatures={Script:1,createContext:0,createScript:2,runInContext:3,runInThisContext:2,isContext:1,compileFunction:2,measureMemory:0};
  for(const [name,length]of Entries(signatures)){
    const fn=function(){return unsupported(name);};
    Define(fn,'name',{__proto__:null,value:name,configurable:true});
    Define(fn,'length',{__proto__:null,value:length,configurable:true});root[name]=fn;
  }
  for(const name of ['runInContext','runInNewContext','runInThisContext','createCachedData'])
    Define(root.Script.prototype,name,{__proto__:null,value:function(){return unsupported('Script.'+name);},writable:true,configurable:true});
  const constants={};
  Define(constants,'USE_MAIN_CONTEXT_DEFAULT_LOADER',{__proto__:null,value:Symbol('vm_dynamic_import_main_context_default'),enumerable:true});
  Define(constants,'DONT_CONTEXTIFY',{__proto__:null,value:Symbol('vm_context_no_contextify'),enumerable:true});
  root.constants=constants;
  return {...root,default:root};
}
