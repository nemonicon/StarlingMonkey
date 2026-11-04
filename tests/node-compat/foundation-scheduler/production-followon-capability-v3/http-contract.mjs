import assert from 'node:assert/strict';
import {readFile,lstat} from 'node:fs/promises';
import {dirname,join,resolve,relative,isAbsolute} from 'node:path';
import {fileURLToPath} from 'node:url';
import {verifyProductionTicks,hash} from './preflight.mjs';
import {validateHTTPInterfaces} from './capabilities.mjs';
import {validatePinBoundary} from './admission.mjs';
import {LIVE_COMPUTED_INPUTS} from './computed-inputs.mjs';
const here=dirname(fileURLToPath(import.meta.url));
const digest=value=>typeof value==='string'&&/^[0-9a-f]{64}$/.test(value)&&value!=='0'.repeat(64);
export function selectHTTPPin(document,productionPin){
 assert.equal(document.schemaVersion,1);assert.equal(document.state,'REVIEWED_REAL_HTTP_COMPONENT_V1','Actual HTTP component pins are unconfigured');
 const pin=document.component;assert(pin&&typeof pin==='object'&&!Array.isArray(pin));
 validatePinBoundary(pin.root);
 assert.equal(pin.state,'reviewed-real-runtime-http-component');
 assert.equal(pin.engineSha256,productionPin.engineSha256);assert.equal(pin.engineReceiptSha256,productionPin.receiptSha256);
 for(const key of ['componentSha256','auditSha256','applicationBundleSha256','inputsSha256','engineSha256','engineReceiptSha256'])assert(digest(pin[key]),key);
 assert(digest(productionPin.engineSha256)&&digest(productionPin.receiptSha256));
 assert(Number.isSafeInteger(pin.componentBytes)&&pin.componentBytes>0);assert(isAbsolute(pin.root));
 validatePinBoundary(pin.root,['componentPath','auditPath','bundlePath','inputsPath'].map(key=>pin[key]));
 assert.equal(pin.componentPath,join(pin.root,'http-joint/native-profile-http.component.wasm'));
 assert.equal(pin.auditPath,join(pin.root,'http-joint/component-audit.json'));
 assert.equal(pin.bundlePath,join(pin.root,'http-joint/http.bundle.mjs'));assert.equal(pin.inputsPath,join(pin.root,'http-inputs.json'));
 return Object.freeze({...pin});
}
async function file(root,path,expected){
 validatePinBoundary(root,[path]);
 let cursor=path;while(cursor!==root){assert(!(await lstat(cursor)).isSymbolicLink());const parent=dirname(cursor);assert.notEqual(parent,cursor,'Pin root boundary was not reached');cursor=parent;}
 assert((await lstat(path)).isFile());const bytes=await readFile(path);assert.equal(hash(bytes),expected,path);return bytes;
}
export async function verifyHTTPReady(){
 const admission=await verifyProductionTicks({entropyPolicy:'runtime-only'});
 const pinsPath=join(here,'http-component-pins.json'),pinBytes=await readFile(pinsPath),pinsSha256=hash(pinBytes);
 const pin=selectHTTPPin(JSON.parse(pinBytes),admission.pin); // Before reading any component/host configuration.
 assert((await lstat(pin.root)).isDirectory()&&!(await lstat(pin.root)).isSymbolicLink());
 const auditBytes=await file(pin.root,pin.auditPath,pin.auditSha256),audit=JSON.parse(auditBytes);
 const component=await file(pin.root,pin.componentPath,pin.componentSha256);assert.equal(component.length,pin.componentBytes);
 await file(pin.root,pin.bundlePath,pin.applicationBundleSha256);const inputs=JSON.parse(await file(pin.root,pin.inputsPath,pin.inputsSha256));
 assert.equal(inputs.state,'PRODUCTION306_HTTP_INPUTS_FROZEN_BEFORE_PACKAGING');assert.equal(inputs.nativeAdmission.engineSha256,admission.pin.engineSha256);
 assert.equal(audit.componentSha256,pin.componentSha256);assert.equal(audit.componentBytes,pin.componentBytes);assert.equal(audit.componentPath,pin.componentPath);
 assert.equal(audit.engineSha256,admission.pin.engineSha256);assert.equal(audit.applicationBundleSha256,pin.applicationBundleSha256);
 assert.equal(audit.httpEntry,join(here,'http-component.mjs'));assert.equal(audit.protectedAbortFoundationsFixture,true);
 assert.deepEqual(audit.allowedImports,audit.selectedInterfaces);validateHTTPInterfaces(audit);
 const copied=audit.computedLiveInputChecks;assert.deepEqual(copied.beforeCopy,copied.afterCopy);
 assert.equal(copied.beforeCopy.state,'EXACT_EIGHT_LIVE_HTTP_INPUTS_MATCH_SEAL');assert.equal(copied.beforeCopy.files,8);assert.equal(copied.beforeCopy.witFiles,7);assert.equal(copied.beforeCopy.adapterFiles,1);
 assert.deepEqual(copied.beforeCopy.inputs.map(x=>x.name),LIVE_COMPUTED_INPUTS);
 async function recheck(){assert.equal(hash(await readFile(pinsPath)),pinsSha256);await admission.recheck();
  await file(pin.root,pin.componentPath,pin.componentSha256);await file(pin.root,pin.auditPath,pin.auditSha256);await file(pin.root,pin.bundlePath,pin.applicationBundleSha256);await file(pin.root,pin.inputsPath,pin.inputsSha256);}
 return{admission,pin,audit,inputs,recheck};
}
