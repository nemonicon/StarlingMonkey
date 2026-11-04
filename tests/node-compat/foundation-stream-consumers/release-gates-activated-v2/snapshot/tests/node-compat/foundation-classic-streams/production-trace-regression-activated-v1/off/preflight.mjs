import {writeFile} from 'node:fs/promises';
import {join,resolve} from 'node:path';
import {verifyProductionTicks,requireFreshOutput} from '../common/preflight.mjs';
export {requireFreshOutput};
export async function verifyFollowonOff(){const production=await verifyProductionTicks({gcStress:false});return{production,report:{state:'consumers355-validation-off-followon-admission-passed',production:production.report,runtimeProof:false},recheck:production.recheck};}
export async function completeFollowon(variable,admission){await admission.recheck();await writeFile(join(resolve(process.env[variable]),'followon-admission-complete.json'),JSON.stringify({...admission.report,consumedInputsRecheckedAfterRun:true},null,2)+'\n',{flag:'wx'});}
