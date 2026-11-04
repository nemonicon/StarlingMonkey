import assert from 'node:assert/strict';
import {join,resolve} from 'node:path';
import {verifyHTTPReady} from './http-contract.mjs';
import {requireFreshOutput,completeRegression} from './preflight.mjs';
assert.notEqual(process.env.NODE_COMPAT_HTTP_REQUIRE_INTRINSICS,'1','This fixed combined fixture has no optional native.intrinsics field');
const ready=await verifyHTTPReady(),{pin}=ready;
for(const[key,value]of Object.entries({NODE_COMPAT_HTTP_AUDIT:pin.auditPath,NODE_COMPAT_HTTP_COMPONENT:pin.componentPath,NODE_COMPAT_HTTP_OUTPUT:join(pin.root,'http-joint/wasmtime-v1')})){
  if(process.env[key])assert.equal(resolve(process.env[key]),value);process.env[key]=value;
}
await requireFreshOutput('NODE_COMPAT_HTTP_OUTPUT');await import('./hosts/test-wasmtime-http.mjs');await ready.recheck();
await completeRegression('NODE_COMPAT_HTTP_OUTPUT',ready.admission);
