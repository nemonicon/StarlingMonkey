// Root-review entry only. No fixture, toolchain, componentizer, guest or host runs.
import assert from 'node:assert/strict';
import {writeFile} from 'node:fs/promises';
import {resolve} from 'node:path';
import {verifyProductionTicks} from './preflight.mjs';
const [variant,output,...rest]=process.argv.slice(2);
assert(!rest.length&&['normal-off','normal-runtime','gc-off'].includes(variant)&&output,
  'Usage after Root reviews actual pins: preflight-only.mjs normal-off|normal-runtime|gc-off FRESH_REPORT_JSON');
const admission=await verifyProductionTicks({gcStress:variant==='gc-off',entropyPolicy:variant==='normal-runtime'?'runtime-only':'off'});
await admission.recheck();
const report={...admission.report,variant,consumedInputsRechecked:true,
  componentizerCompilerGuestOrHostExecuted:false,scope:'Actual fixed-artifact read-only admission only; not a runtime pass'};
await writeFile(resolve(output),JSON.stringify(report,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({state:report.state,variant,runtimeProof:false}));
