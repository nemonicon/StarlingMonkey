// Pure untimed byte-lifetime check. No provider/codec calls or extra guest exports.
import {base64,requireValue} from './contract.mjs';
export function captureUntimedOutput(caseId,output,baseline){
 requireValue(typeof baseline==='string'&&base64(output)===baseline,'exact prior output baseline');
 // The baseline is an immutable string, independent of the provider-owned bytes.
 return Object.freeze({caseId,output,baseline});
}
export function requirePriorOutputUnchanged(prior){
 requireValue(base64(prior.output)===prior.baseline,'full prior output changed after subsequent provider call');
}
