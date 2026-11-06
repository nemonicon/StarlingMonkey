// Source fragment only; no body executes during INIT.
function createNativeContextBackend(process) {
  return{AsyncLocalStorage:ContextAsyncLocalStorage,AsyncResource:contextAsyncHooks.AsyncResource,
    boundaryMode:'actual-native-private-boundaries',
    boundaries(){return{runFreshRequest,runNeutralServer};},
    nextTick:callback=>process.nextTick(callback),setTimeout:contextTimeout,clearTimeout:contextClearTimeout,
    setImmediate:contextImmediate,clearImmediate:contextClearImmediate,promiseTimeout:contextPromiseTimeout};
}
let contextCalls=0;
async function prepareContextServer() {
  const process=bootstrap();
  if(globalThis.process!==process)throw new Error('Actual native process identity mismatch');
  const backend=createNativeContextBackend(process);
  const handler=async request=>{
    const call=++contextCalls;
    const collected=await collectContextInterleaving(backend,call);
    return new Response(JSON.stringify({schemaVersion:1,marker:'NEXT_NATIVE_CONTEXT_INTERLEAVING_V1',call,
      method:request.method,collection:collected}),{status:collected.passed?200:500,
      headers:{'content-type':'application/json; charset=utf-8','cache-control':'no-store'}});
  };
  return createWasiHttpHandler(handler,types,runFreshRequest);
}
export const incomingHandler=createNeutralReadyHandler({runNeutralServer,prepareServer:prepareContextServer,disposeBeforeEntry});
