// No host/tool entry is imported until real engine AND component pins pass.
import assert from 'node:assert/strict';
import {join,resolve} from 'node:path';
import {verifyHTTPReady} from './http-contract.mjs';
import {requireFreshOutput,completeRegression} from './preflight.mjs';
const ready=await verifyHTTPReady(),{pin}=ready;
function fixed(name,value){if(process.env[name])assert.equal(resolve(process.env[name]),value);process.env[name]=value;}
fixed('NODE_COMPAT_HTTP_AUDIT',pin.auditPath);fixed('NODE_COMPAT_HTTP_COMPONENT',pin.componentPath);
fixed('NODE_COMPAT_HTTP_OUTPUT',join(pin.root,'http-joint/wasmtime-v1'));
await requireFreshOutput('NODE_COMPAT_HTTP_OUTPUT');
await import('../../wasmcloud/test-wasmtime-http.mjs');
await ready.recheck();
await completeRegression('NODE_COMPAT_HTTP_OUTPUT',ready.admission);
