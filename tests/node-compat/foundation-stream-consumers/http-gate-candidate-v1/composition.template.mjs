// UNEXECUTED request-fixture composition only; no Request/WASI body adapter.
// A future finite bundler redirect must bind the exact original handler import.
import {runConsumerHttpProbe} from './consumer-probes.template.mjs';
export function createConsumersHTTPComposer(originalCreateIncomingHandler,runClassic19){
 return function createIncomingHandler(runBaseline){
  return originalCreateIncomingHandler(async()=>{
   const baseline=JSON.parse(await runBaseline());
   if(baseline.failure)return JSON.stringify({consumerCombinedSchema:1,joint:{combinedSchema:1,baseline,classic:null,failure:baseline.failure},consumers:null,failure:baseline.failure});
   const classic=await runClassic19(),consumers=await runConsumerHttpProbe();
   return JSON.stringify({consumerCombinedSchema:1,joint:{combinedSchema:1,baseline,classic},consumers});
  });
 };
}
// No generator/reader/stream/request/host handle is constructed at INIT.
// Calls are source fixture counters, not physical-instance reuse evidence.
