// Serialization only; no timers, HTTP, application or retained helper import.
if(process.version!=='v22.14.0')throw Error('Pinned Node22.14 required');
const errorData=e=>({thrownType:typeof e,name:e?.name??null,message:e?.message??String(e),code:e?.code??null,stack:e?.stack??null});
const cases=['AbortError','TimeoutError'].map(name=>({name,error:errorData(new DOMException('Retained serialization DATA only',name))}));
console.log(JSON.stringify({schemaVersion:1,node:process.version,serializationOnly:true,timerOrNetworkStarted:false,cases}));
