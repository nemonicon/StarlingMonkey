// Genuine full355 validation-only bridge; no metadata projection or operational admission.
import assert from 'node:assert/strict';
import {writeFile,lstat} from 'node:fs/promises';
import {join,resolve} from 'node:path';
import {validationPreflight,verifyFamily,assertActionContext,hash} from "../../../../../../native-preflight.mjs";
export {hash};
export async function verifyInputClosure(){return verifyFamily();}
export async function verifyProductionTicks({gcStress=false,entropyPolicy='off'}={}){
 assert.equal(typeof gcStress,'boolean');assert(['off','runtime-only'].includes(entropyPolicy));assert(!(gcStress&&entropyPolicy==='runtime-only'));
 const variant=entropyPolicy==='runtime-only'?'normal-runtime':gcStress?'gc-off':'normal-off';
 await assertActionContext({variant});
 const native=await validationPreflight({variant});
 process.env.NODE_COMPAT_ENGINE=native.enginePath;process.env.NODE_COMPAT_ENGINE_SOURCE_ROOT=native.sourceRoot;
 const inputClosure=await verifyFamily();
 const report={state:'genuine-consumers355-validation-only-admission-passed',variant,engineSha256:native.pin.engineSha256,
  sourceFilesVerified:355,recipeSha256:native.pin.recipeSha256,freezeReceiptSha256:native.pin.freezeReceiptSha256,
  entropyPolicy,gcStress,inputClosure,validationBootstrapOnly:true,operationalAdmission:false,
  scope:'Actual full355 build/source/config admission only; no runtime result or source projection'};
 return{...native,engine:native.enginePath,engineSha256:native.pin.engineSha256,sourceFilesVerified:355,report};
}
export async function requireFreshOutput(variable){assert(process.env[variable],'Choose a fresh output: '+variable);const output=resolve(process.env[variable]);try{await lstat(output);assert.fail('Output exists: '+output);}catch(error){if(error.code!=='ENOENT')throw error;}return output;}
export async function completeRegression(variable,admission){await admission.recheck();await writeFile(join(resolve(process.env[variable]),'production-admission-complete.json'),JSON.stringify({...admission.report,consumedInputsRecheckedAfterRun:true},null,2)+'\n',{flag:'wx'});}
