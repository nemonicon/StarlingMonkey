// Propose an actual-output seal for later review; never edits checked-in null pins.
import assert from 'node:assert/strict';
import {readFile,writeFile} from 'node:fs/promises';
import {join,resolve} from 'node:path';
import {verifyProductionTicks,hash} from './preflight.mjs';
import {validateHTTPInterfaces} from './capabilities.mjs';
const admission=await verifyProductionTicks({entropyPolicy:'runtime-only'});
assert(process.env.NODE_COMPAT_PRODUCTION_HTTP_ROOT);const root=resolve(process.env.NODE_COMPAT_PRODUCTION_HTTP_ROOT);
const auditPath=join(root,'http-joint/component-audit.json'),auditBytes=await readFile(auditPath),audit=JSON.parse(auditBytes);
const componentPath=join(root,'http-joint/native-profile-http.component.wasm'),component=await readFile(componentPath);
const bundlePath=join(root,'http-joint/http.bundle.mjs'),bundle=await readFile(bundlePath),inputsPath=join(root,'http-inputs.json'),inputsBytes=await readFile(inputsPath),inputs=JSON.parse(inputsBytes);
assert.equal(inputs.state,'CLASSIC342_HTTP_INPUTS_FROZEN_BEFORE_PACKAGING');assert.equal(inputs.nativeAdmission.engineSha256,admission.pin.engineSha256);
assert.equal(audit.componentPath,componentPath);assert.equal(audit.componentSha256,hash(component));assert.equal(audit.componentBytes,component.length);
assert.equal(audit.engineSha256,admission.pin.engineSha256);assert.equal(audit.applicationBundleSha256,hash(bundle));validateHTTPInterfaces(audit);
await admission.recheck();
const candidate={schemaVersion:1,state:'OBSERVED_HTTP_COMPONENT_SEAL_REQUIRES_REVIEW_NOT_HOST_ADMISSION',component:{state:'observed-runtime-http-component-not-admitted',root,
 componentPath,componentSha256:hash(component),componentBytes:component.length,auditPath,auditSha256:hash(auditBytes),bundlePath,applicationBundleSha256:hash(bundle),inputsPath,inputsSha256:hash(inputsBytes),engineSha256:admission.pin.engineSha256,engineReceiptSha256:admission.pin.receiptSha256}};
await writeFile(join(root,'observed-http-component-seal.json'),JSON.stringify(candidate,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({state:candidate.state,componentSha256:hash(component),hostAdmitted:false}));
