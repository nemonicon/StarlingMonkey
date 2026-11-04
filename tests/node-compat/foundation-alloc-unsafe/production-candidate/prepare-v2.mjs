// Isolated unreleased m0.8 revision. Preserve the complete accepted v1 stage.
import assert from 'node:assert/strict';
import {cp,mkdir,readFile,readdir,writeFile,stat} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {dirname,join,relative,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
assert.equal(process.version,'v22.14.0');
const here=dirname(fileURLToPath(import.meta.url)),v2=join(here,'v2'),hash=v=>createHash('sha256').update(v).digest('hex');
const v1IndexBytes=await readFile(join(here,'index.json')),v1=JSON.parse(v1IndexBytes);
for(const item of v1.files)assert.equal(hash(await readFile(join(here,item.path))),item.sha256);
try{await stat(v2);throw new Error('v2 exists; preserve and inspect');}catch(error){if(error.code!=='ENOENT')throw error;}
await mkdir(v2,{recursive:true});
for(const name of ['base','source','harness/base','harness/source'])await cp(join(here,name),join(v2,name),{recursive:true});
const root=join(v2,'source/builtins/node-compat');
const helper=`// No host capability is consulted, including at snapshot time.
export const PROFILE_VERSION = 'sm-node-22.14.0-m0.8';

// Capture trusted installation-time constructors/intrinsics before application
// code can replace them. Own data descriptors bypass inherited field hooks.
const ProfileError = Error;
const DefineErrorProperty = Object.defineProperty;

export function unsupported(module, operation) {
  const error = new ProfileError(\x60\x24{module}.\x24{operation} is unavailable in \x24{PROFILE_VERSION}\x60);
  DefineErrorProperty(error, 'code', { __proto__: null, value: 'ERR_SM_NODE_UNSUPPORTED', writable: true, enumerable: true, configurable: true });
  DefineErrorProperty(error, 'module', { __proto__: null, value: module, writable: true, enumerable: true, configurable: true });
  DefineErrorProperty(error, 'operation', { __proto__: null, value: operation, writable: true, enumerable: true, configurable: true });
  DefineErrorProperty(error, 'profile', { __proto__: null, value: PROFILE_VERSION, writable: true, enumerable: true, configurable: true });
  throw error;
}

export function unavailable(module, operation) {
  // Ordinary functions throw on both invocation and construction. No Proxy,
  // getters, then member, or host operation is involved.
  return function unavailableOperation() { unsupported(module, operation); };
}
`;
await writeFile(join(root,'unsupported.mjs'),helper);
const generated=spawnSync(process.execPath,[join(root,'generate-factories.mjs')],{encoding:'utf8'});assert.equal(generated.status,0,generated.stderr);
const checked=spawnSync(process.execPath,[join(root,'generate-factories.mjs'),'--check'],{encoding:'utf8'});assert.equal(checked.status,0,checked.stderr);
async function paths(directory){const result=[];for(const entry of await readdir(directory,{withFileTypes:true})){const path=join(directory,entry.name);if(entry.isDirectory())result.push(...await paths(path));else result.push(path);}return result.sort();}
const changed=[],unchanged=[],deltaV1=[];
for(const path of await paths(join(v2,'base/builtins/node-compat'))){
  const name=relative(join(v2,'base/builtins/node-compat'),path),before=hash(await readFile(path)),after=hash(await readFile(join(root,name)));
  (before===after?unchanged:changed).push({path:'builtins/node-compat/'+name,before,after});
  const prior=hash(await readFile(join(here,'source/builtins/node-compat',name)));
  if(prior!==after)deltaV1.push({path:'builtins/node-compat/'+name,before:prior,after});
}
assert.deepEqual(deltaV1.map(e=>e.path),['builtins/node-compat/factories.generated.h','builtins/node-compat/unsupported.mjs']);
let patch='';
for(const item of changed){const path=item.path.slice('builtins/node-compat/'.length);const diff=spawnSync('diff',['-u','--label','a/'+item.path,join(v2,'base/builtins/node-compat',path),'--label','b/'+item.path,join(root,path)],{encoding:'utf8'});assert.equal(diff.status,1);patch+=diff.stdout;}
await writeFile(join(v2,'core-m0.8.patch'),patch);
const sourceReceipt={schema:1,proposalVersion:'buffer-allocunsafe-zeroed-production-v2',productionInstalled:false,baseCoreVersion:'sm-node-22.14.0-m0.1',candidateCoreVersion:'sm-node-22.14.0-m0.8',
  changed,unchanged,deltaFromV1:deltaV1,v1IndexSha256:hash(v1IndexBytes),patchSha256:hash(patch),generatorCheck:checked.stdout.trim(),nativeBufferCppUnchanged:true,
  scope:'Uninstalled revision of the reserved unreleased m0.8 proposal. Only helper/header differ from v1; no genuine OOM or native/component proof.'};
await writeFile(join(v2,'source-receipt.json'),JSON.stringify(sourceReceipt,null,2)+'\n');
const helperPath=join(v2,'harness/source/tests/node-compat/core-expectations.mjs');let testHelper=await readFile(helperPath,'utf8');
for(const item of deltaV1){assert.equal(testHelper.split(item.before).length,2);testHelper=testHelper.replace(item.before,item.after);}
await writeFile(helperPath,testHelper);
const oldHarness=JSON.parse(await readFile(join(here,'harness-receipt.json'))),harnessChanges=[];let harnessPatch='';
for(const item of oldHarness.changes){const bytes=await readFile(join(v2,'harness/source',item.path)),before=item.before?join(v2,'harness/base',item.path):'/dev/null';
  const diff=spawnSync('diff',['-u','--label',item.before?'a/'+item.path:'/dev/null',before,'--label','b/'+item.path,join(v2,'harness/source',item.path)],{encoding:'utf8'});assert.equal(diff.status,1);harnessPatch+=diff.stdout;
  harnessChanges.push({...item,after:hash(bytes)});}
await writeFile(join(v2,'harness-m0.8.patch'),harnessPatch);
await writeFile(join(v2,'harness-receipt.json'),JSON.stringify({...oldHarness,sourceReceiptSha256:hash(await readFile(join(v2,'source-receipt.json'))),patchSha256:hash(harnessPatch),changes:harnessChanges,
  v1IndexSha256:hash(v1IndexBytes),scope:'Unapplied v2 helper/header hash pins; same exact m0.1 controls and unreleased m0.8 support contract.'},null,2)+'\n');
for(const name of ['run-host.mjs','run-harness-tests.mjs']){
  let text=await readFile(join(here,name),'utf8');
  text=text.replace("resolve(here, '../../../..')","resolve(here, '../../../../..')");
  text=text.replaceAll("../../../../docs/node-compat/templates/reference-kernel.mjs","../../../../../docs/node-compat/templates/reference-kernel.mjs");
  text=text.replaceAll("../checks.mjs","../../checks.mjs");
  if(name==='run-host.mjs')text=text.replace("'prepare.mjs'","'../prepare-v2.mjs'");
  await writeFile(join(v2,name),text);
}
console.log(JSON.stringify({sourceChanged:changed.length,v1Delta:deltaV1.map(e=>e.path),harnessChanged:harnessChanges.length,profile:sourceReceipt.candidateCoreVersion,v1Preserved:true,installed:false}));
