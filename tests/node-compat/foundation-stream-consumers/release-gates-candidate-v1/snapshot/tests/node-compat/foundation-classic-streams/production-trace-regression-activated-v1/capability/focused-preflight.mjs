import {selectedManifestsForValidation} from "../../../../../../native-preflight.mjs";
// Host-only exact production admission before any protected receiver fixture.
import assert from 'node:assert/strict';
import {verifyProductionTicks,hash} from './preflight.mjs';
export {hash};
export async function preflight({gcStress=false,entropyPolicy='off'}={}){
 const admitted=await verifyProductionTicks({gcStress,entropyPolicy});
 const{engine,sourceRoot,metadata,pin}=admitted;
 assert.equal(metadata.eventsEnabled,true);assert.equal(metadata.protectedAbortListenerEnabled,true);
 assert.equal(metadata.protectedAbortListenerPolicy.enabled,true);
 const builtinManifests=selectedManifestsForValidation(metadata,{sourceRoot});
 assert.equal(builtinManifests.find(x=>x.modules['node:events'])?.profileVersion,'sm-node-22.14.0-m0.10');
 return{...admitted,builtinManifests,report:{...admitted.report,engine,sourceRoot,
  engineMetadataSha256:pin.receiptSha256,entropyPolicy,gcStress,guardNegativesAllowed:true,
  scope:'Only genuine consumers355 Events-ON with actual layered macro/source/config proof; never Events-OFF or historical guard-absent receivers.'}};
}
