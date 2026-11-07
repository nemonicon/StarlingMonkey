// Source only: bootstrap and all ALS/timer creation are deferred to neutral readiness.
async function prepareUnrefServer(){
 const process=bootstrap();
 if(globalThis.process!==process)throw new Error('Actual native process identity mismatch');
 const state=createUnrefReuseState({AsyncLocalStorage:UnrefAsyncLocalStorage,
  boundaryMode:'actual-native-private-boundaries',boundaries(){return{runFreshRequest,runNeutralServer};},
  setTimeout:unrefTimeout,clearTimeout:unrefClearTimeout});
 const handler=async request=>{
  let collection,finalCleanup;
  try{
   if(request.method!=='GET')throw new TypeError('UNREF_REUSE_GET_ONLY');
   const url=new URL(request.url),phase=url.searchParams.get('phase'),hostCase=url.searchParams.get('case');
   // createWasiHttpHandler already entered the real fresh native owner before conversion.
   collection=await state.handle(phase,hostCase);
   if(phase==='C'||collection.passed!==true){finalCleanup=state.dispose();collection.finalCleanup=finalCleanup;}
   return new Response(JSON.stringify({schemaVersion:1,marker:'NEXT_NATIVE_UNREF_REUSE_V1',call:collection.ordinal,
    method:request.method,collection}),{status:collection.passed?200:500,
    headers:{'content-type':'application/json; charset=utf-8','cache-control':'no-store'}});
  }catch(error){
   finalCleanup??=state.dispose();
   return new Response(JSON.stringify({schemaVersion:1,marker:'NEXT_NATIVE_UNREF_REUSE_V1',passed:false,
    error:dataError(error),collection:collection??null,finalCleanup}),{status:500,
    headers:{'content-type':'application/json; charset=utf-8','cache-control':'no-store'}});
  }
 };
 return createWasiHttpHandler(handler,types,runFreshRequest);
}
export const incomingHandler=createNeutralReadyHandler({runNeutralServer,prepareServer:prepareUnrefServer,disposeBeforeEntry});
