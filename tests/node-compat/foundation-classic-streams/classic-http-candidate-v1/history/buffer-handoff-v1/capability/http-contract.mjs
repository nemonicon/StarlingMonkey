// Component-phase review is external; this sealed candidate's null pin is immutable.
import assert from 'node:assert/strict';
import {readFile,lstat} from 'node:fs/promises';
import {dirname,join,relative,resolve,isAbsolute,sep} from 'node:path';
import {fileURLToPath} from 'node:url';
import {verifyProductionTicks,hash} from './preflight.mjs';
import {validateHTTPInterfaces} from './capabilities.mjs';
const here=dirname(fileURLToPath(import.meta.url));
const SHA=/^[0-9a-f]{64}$/;
async function file(root,path,expected){
  const name=relative(root,path);assert(name&&name!=='..'&&!name.startsWith('..'+sep)&&!isAbsolute(name));
  let cursor=path;while(cursor!==root){const stat=await lstat(cursor);assert(!stat.isSymbolicLink());cursor=dirname(cursor);}
  assert((await lstat(path)).isFile());const data=await readFile(path);assert.equal(hash(data),expected,path);return data;
}
export async function verifyHTTPReady(){
  const admission=await verifyProductionTicks();
  const pinPath=resolve(process.env.NODE_COMPAT_CLASSIC_HTTP_COMPONENT_PINS??join(here,'component-pins.json'));
  const raw=await readFile(pinPath),pinSha=hash(raw);
  if(process.env.NODE_COMPAT_CLASSIC_HTTP_COMPONENT_PINS_SHA256)assert.equal(pinSha,process.env.NODE_COMPAT_CLASSIC_HTTP_COMPONENT_PINS_SHA256);
  const document=JSON.parse(raw);
  assert.equal(document.state,'ROOT_REVIEWED_CLASSIC_COMBINED_HTTP_COMPONENT_V1','Combined HTTP component pin remains null/unreviewed');
  assert(SHA.test(process.env.NODE_COMPAT_CLASSIC_HTTP_COMPONENT_PINS_SHA256??''),'Root must supply the exact reviewed phase digest');
  const pin=document.component;assert.equal(pin.state,'reviewed-classic-combined-http-component');
  assert.equal(pin.engineSha256,admission.pin.engineSha256);assert.equal(pin.engineReceiptSha256,admission.pin.receiptSha256);
  const root=resolve(pin.root);assert.equal(root,pin.root);assert((await lstat(root)).isDirectory()&&!(await lstat(root)).isSymbolicLink());
  for(const key of ['componentSha256','auditSha256','applicationBundleSha256','inputsSha256'])assert(SHA.test(pin[key]));
  const checks=[[pin.componentPath,pin.componentSha256],[pin.auditPath,pin.auditSha256],[pin.bundlePath,pin.applicationBundleSha256],[pin.inputsPath,pin.inputsSha256]];
  const values=[];for(const[path,expected]of checks)values.push(await file(root,path,expected));
  const audit=JSON.parse(values[1]);assert.equal(audit.componentSha256,pin.componentSha256);assert.equal(audit.componentBytes,values[0].length);
  assert.equal(audit.engineSha256,admission.pin.engineSha256);assert.equal(audit.applicationBundleSha256,pin.applicationBundleSha256);
  assert.equal(audit.httpEntry,join(here,'http-component.mjs'));assert.equal(audit.classicCombinedHTTP.ordinaryGroups,19);validateHTTPInterfaces(audit);
  const frozenChecks=checks.map(row=>[...row]),nativeRecheck=admission.recheck;
  async function recheck(){assert.equal(hash(await readFile(pinPath)),pinSha);await nativeRecheck();for(const[path,expected]of frozenChecks)await file(root,path,expected);}
  await recheck();return{admission,pin:structuredClone(pin),audit,recheck};
}
