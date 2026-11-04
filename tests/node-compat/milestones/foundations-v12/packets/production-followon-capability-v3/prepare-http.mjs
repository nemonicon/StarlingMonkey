// Input-only preparation; null production pins refuse before source/engine reads.
import assert from 'node:assert/strict';
import {mkdir,writeFile} from 'node:fs/promises';
import {join,resolve} from 'node:path';
import {verifyProductionTicks,requireFreshOutput} from './preflight.mjs';
const admission=await verifyProductionTicks({entropyPolicy:'runtime-only'});
const root=await requireFreshOutput('NODE_COMPAT_PRODUCTION_HTTP_ROOT');await mkdir(root,{recursive:false});
const report={state:'PRODUCTION306_HTTP_INPUTS_FROZEN_BEFORE_PACKAGING',recordedAtUtc:new Date().toISOString(),root,
 nativeAdmission:admission.report,sourceInputClosure:admission.report.inputClosure,
 capabilityPolicy:'RuntimeOnly scalar=random@0.2.10; HTTP=exact-six@0.2.10 with duration-only monotonic clock',
 scope:'Input admission only; standard HTTP transport, not node:http, no guest/host/performance/reuse proof'};
await admission.recheck();await writeFile(join(root,'http-inputs.json'),JSON.stringify(report,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({state:report.state,root,packaged:false}));
