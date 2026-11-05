// Benign Node child with the actual launcher's explicit environment; no worker.
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {MEASUREMENT_ENV,MEASUREMENT_CWD} from '../cost-pilot-timing-candidate-v1/lifecycle-policy.mjs';
const result=spawnSync(process.execPath,[fileURLToPath(new URL('environment.mjs',import.meta.url))],
  {env:{...MEASUREMENT_ENV},cwd:MEASUREMENT_CWD,timeout:30000,maxBuffer:65536,encoding:'utf8'});
console.log(JSON.stringify({schemaVersion:1,executable:process.execPath,args:['environment.mjs'],
  exactEnvironmentPassed:MEASUREMENT_ENV,status:result.status,signal:result.signal,
  error:result.error?String(result.error):null,stdout:result.stdout,stderr:result.stderr,
  childObservation:result.status===0?JSON.parse(result.stdout):null,
  workerCalled:false,loaderCalled:false,guestInvoked:false}));
