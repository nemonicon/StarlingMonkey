// External reviewed component phase: checked-in null data is never activated.
import assert from 'node:assert/strict';
import {readFile,lstat} from 'node:fs/promises';
import {dirname,join,relative,resolve,isAbsolute,sep} from 'node:path';
import {fileURLToPath} from 'node:url';
import {verifyProductionTicks,hash} from './preflight.mjs';
import {validateHTTPInterfaces} from './capabilities.mjs';
import {LIVE_COMPUTED_INPUTS} from './computed-inputs.mjs';
import {BASELINE_ENTRY,CLASSIC_ORDINARY,CLASSIC_CHECKS,COMPOSER_SOURCE} from './composer-plugin.mjs';
const here=dirname(fileURLToPath(import.meta.url));
const digest=value=>typeof value==='string'&&/^[0-9a-f]{64}$/.test(value)&&value!=='0'.repeat(64);
export function selectCombinedHTTPPin(document,productionPin,sourceSha){
  assert.equal(document.schemaVersion,1);
  assert.equal(document.state,'ROOT_REVIEWED_CLASSIC_TRACE_COMBINED_HTTP_COMPONENT_V1','Combined HTTP component pin remains null/unreviewed');
  const pin=document.component;assert(pin&&typeof pin==='object'&&!Array.isArray(pin));
  assert.equal(pin.state,'reviewed-classic-trace-combined-http-component');
  assert.equal(pin.engineSha256,productionPin.engineSha256);assert.equal(pin.engineReceiptSha256,productionPin.receiptSha256);
  assert.equal(pin.sourceInputSha256,sourceSha);
  for(const key of ['componentSha256','auditSha256','applicationBundleSha256','inputsSha256','engineSha256','engineReceiptSha256','sourceInputSha256'])assert(digest(pin[key]),key);
  assert(Number.isSafeInteger(pin.componentBytes)&&pin.componentBytes>0);
  assert(typeof pin.root==='string'&&isAbsolute(pin.root)&&resolve(pin.root)===pin.root&&!pin.root.includes('\0'));
  for(const[key,name]of Object.entries({componentPath:'http-joint/native-profile-http.component.wasm',auditPath:'http-joint/component-audit.json',bundlePath:'http-joint/http.bundle.mjs',inputsPath:'http-inputs.json'}))assert.equal(pin[key],join(pin.root,name),key);
  assert.equal(pin.sourceEntryPath,join(here,'http-component.mjs'),'Preserve the actual build source entry; no relocation/relabeling');
  return structuredClone(pin);
}
async function file(root,path,expected){
  const name=relative(root,path);assert(name&&name!=='..'&&!name.startsWith('..'+sep)&&!isAbsolute(name));
  let cursor=path;while(cursor!==root){const stat=await lstat(cursor);assert(!stat.isSymbolicLink());cursor=dirname(cursor);}
  assert((await lstat(path)).isFile());const data=await readFile(path);assert.equal(hash(data),expected,path);return data;
}
export async function verifyHTTPReady(){
  const admission=await verifyProductionTicks();
  assert(process.env.NODE_COMPAT_CLASSIC_HTTP_COMPONENT_PINS&&digest(process.env.NODE_COMPAT_CLASSIC_HTTP_COMPONENT_PINS_SHA256),
    'Root must supply an external reviewed component phase path and exact digest; local component pin stays null');
  const pinPath=resolve(process.env.NODE_COMPAT_CLASSIC_HTTP_COMPONENT_PINS),expectedPinSha=process.env.NODE_COMPAT_CLASSIC_HTTP_COMPONENT_PINS_SHA256;
  const pinStat=await lstat(pinPath);assert(pinStat.isFile()&&!pinStat.isSymbolicLink());
  const raw=await readFile(pinPath);assert.equal(hash(raw),expectedPinSha,'Component phase changed before JSON parsing');
  const pin=selectCombinedHTTPPin(JSON.parse(raw),admission.pin,admission.report.inputClosure.sha256);
  const root=pin.root;assert((await lstat(root)).isDirectory()&&!(await lstat(root)).isSymbolicLink());
  const checks=[[pin.componentPath,pin.componentSha256],[pin.auditPath,pin.auditSha256],[pin.bundlePath,pin.applicationBundleSha256],[pin.inputsPath,pin.inputsSha256]];
  const values=[];for(const[path,expected]of checks)values.push(await file(root,path,expected));
  const audit=JSON.parse(values[1]),inputs=JSON.parse(values[3]);
  assert.equal(pin.componentBytes,values[0].length);assert.equal(audit.componentSha256,pin.componentSha256);assert.equal(audit.componentBytes,values[0].length);
  assert.equal(audit.componentPath,pin.componentPath);assert.equal(audit.engineSha256,admission.pin.engineSha256);assert.equal(audit.applicationBundleSha256,pin.applicationBundleSha256);
  assert.equal(audit.httpEntry,pin.sourceEntryPath);assert.equal(audit.protectedAbortFoundationsFixture,true);
  assert.equal(audit.currentProductionAdmission.inputClosure.sha256,pin.sourceInputSha256);
  assert.equal(inputs.state,'CLASSIC342_HTTP_INPUTS_FROZEN_BEFORE_PACKAGING');assert.equal(inputs.nativeAdmission.engineSha256,admission.pin.engineSha256);
  assert.equal(inputs.sourceInputClosure.sha256,pin.sourceInputSha256);assert.equal(inputs.classicOrdinaryGroups,19);
  const combined=audit.classicCombinedHTTP;
  assert.equal(combined.schema,1);assert.equal(combined.ordinaryGroups,19);assert.equal(combined.baselineEntry,BASELINE_ENTRY);
  assert.equal(combined.nodeOracleSha256,'88bd20781a396e6fd178d3b014a98495fec848eb28adb81c80e7dc838f4686ce');
  assert.equal(combined.composerSha256,hash(COMPOSER_SOURCE));
  for(const[path,key]of [[BASELINE_ENTRY,'baselineSha256'],[CLASSIC_ORDINARY,'ordinarySourceSha256'],[CLASSIC_CHECKS,'checksSourceSha256']])assert.equal(hash(await readFile(path)),combined[key]);
  validateHTTPInterfaces(audit);
  const copied=audit.computedLiveInputChecks;assert.deepEqual(copied.beforeCopy,copied.afterCopy);
  assert.equal(copied.beforeCopy.state,'EXACT_EIGHT_LIVE_HTTP_INPUTS_MATCH_SEAL');assert.equal(copied.beforeCopy.files,8);
  assert.deepEqual(copied.beforeCopy.inputs.map(row=>row.name),LIVE_COMPUTED_INPUTS);
  const frozenChecks=checks.map(row=>[...row]),nativeRecheck=admission.recheck;
  async function recheck(){const stat=await lstat(pinPath);assert(stat.isFile()&&!stat.isSymbolicLink());assert.equal(hash(await readFile(pinPath)),expectedPinSha);await nativeRecheck();for(const[path,expected]of frozenChecks)await file(root,path,expected);}
  await recheck();return{admission,pin,audit,inputs,recheck};
}
