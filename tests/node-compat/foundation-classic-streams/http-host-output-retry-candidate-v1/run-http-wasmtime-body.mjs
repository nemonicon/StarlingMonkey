import assert from 'node:assert/strict';
import {join,resolve} from 'node:path';
import {verifyHTTPReady} from '../classic-http-candidate-v1/capability/http-contract.mjs';
import {requireFreshOutput,completeRegression} from '../classic-http-candidate-v1/capability/preflight.mjs';
const ready=await verifyHTTPReady(),{pin}=ready;
for(const[key,value]of Object.entries({NODE_COMPAT_HTTP_AUDIT:pin.auditPath,NODE_COMPAT_HTTP_COMPONENT:pin.componentPath,NODE_COMPAT_HTTP_OUTPUT:join(pin.root,'http-joint/wasmtime-v2')})){
  if(process.env[key])assert.equal(resolve(process.env[key]),value);process.env[key]=value;
}
await requireFreshOutput('NODE_COMPAT_HTTP_OUTPUT');await import('../classic-http-candidate-v1/capability/hosts/test-wasmtime-http.mjs');await ready.recheck();
await completeRegression('NODE_COMPAT_HTTP_OUTPUT',ready.admission);
