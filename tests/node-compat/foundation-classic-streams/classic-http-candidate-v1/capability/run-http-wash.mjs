import assert from 'node:assert/strict';
import {join,resolve} from 'node:path';
import {verifyHTTPReady} from './http-contract.mjs';
import {requireFreshOutput,completeRegression} from './preflight.mjs';
const ready=await verifyHTTPReady(),{pin}=ready;
for(const[key,value]of Object.entries({NODE_COMPAT_HTTP_AUDIT:pin.auditPath,NODE_COMPAT_HTTP_COMPONENT:pin.componentPath,
  NODE_COMPAT_WASMCLOUD_OUTPUT:join(pin.root,'wash'),NODE_COMPAT_WASMCLOUD_RESULTS:join(pin.root,'http-joint-wasmcloud-results.json')})){
  if(process.env[key])assert.equal(resolve(process.env[key]),value);process.env[key]=value;
}
await requireFreshOutput('NODE_COMPAT_WASMCLOUD_OUTPUT');await requireFreshOutput('NODE_COMPAT_WASMCLOUD_RESULTS');
await import('./hosts/run-host.mjs');await ready.recheck();await completeRegression('NODE_COMPAT_WASMCLOUD_OUTPUT',ready.admission);
