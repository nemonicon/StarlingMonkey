// Called before trace driver/tool loading; the full runtime seal owns these bytes.
import {createHash} from 'node:crypto';
import {classicPreflight} from '../runtime-preflight.mjs';
export const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
export async function tracePreflight(){
 const native=await classicPreflight({variant:'normal-off'});
 const nativeRecheck=native.recheck;
 await nativeRecheck();
 return Object.freeze({...native,recheck:nativeRecheck,traceSourceAdmission:Object.freeze({
  state:'REVIEWED_CORRECTED_TRACE_SOURCE_ACTUAL_CLASSIC342_NORMAL_OFF_NOT_EXECUTED',
  sourceFilesVerified:342,sourceContractVersion:'sm-classic-trace-source-v1',
  note:'Fresh pinned Node11 parity required; historical host model is only a counterexample control.'})});
}
