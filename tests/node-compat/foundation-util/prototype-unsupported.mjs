// Test-only ordinary functions deliberately fail for both call and construction.
export function unsupported(module,operation){
  const fn=function(){
    const error=new Error(`${module}.${operation} is deferred in the util prototype`);
    Object.assign(error,{code:'ERR_SM_NODE_UNSUPPORTED',module,operation,profile:'sm-node-22.14.0-util-prototype.v1'});
    throw error;
  };
  Object.defineProperty(fn,'name',{value:operation,configurable:true});
  return fn;
}
