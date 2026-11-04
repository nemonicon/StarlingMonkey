import assert from 'node:assert/strict';
import {mkdir,writeFile} from 'node:fs/promises';
import {join} from 'node:path';
import {verifyProductionTicks,requireFreshOutput} from './preflight.mjs';
const admission=await verifyProductionTicks();
const root=await requireFreshOutput('NODE_COMPAT_PRODUCTION_HTTP_ROOT');await mkdir(root,{recursive:false});
const report={state:'CLASSIC342_HTTP_INPUTS_FROZEN_BEFORE_PACKAGING',root,nativeAdmission:admission.report,
  sourceInputClosure:admission.report.inputClosure,classicOrdinaryGroups:19,
  scope:'Baseline schema5/protected29 plus ordinary classic19; packaging/hosts not yet performed'};
await admission.recheck();await writeFile(join(root,'http-inputs.json'),JSON.stringify(report,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({root,packaged:false}));
