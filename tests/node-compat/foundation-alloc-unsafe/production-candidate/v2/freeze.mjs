import assert from 'node:assert/strict';
import {readFile,writeFile} from 'node:fs/promises';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
assert.equal(process.version,'v22.14.0');
const here=dirname(fileURLToPath(import.meta.url)),v1=resolve(here,'..'),repository=resolve(here,'../../../../..'),hash=v=>createHash('sha256').update(v).digest('hex');
const v1IndexBytes=await readFile(join(v1,'index.json')),v1Index=JSON.parse(v1IndexBytes);
for(const file of v1Index.files)assert.equal(hash(await readFile(join(v1,file.path))),file.sha256);
for(const file of v1Index.preserved)assert.equal(hash(await readFile(join(v1,file.path))),file.sha256);
const source=JSON.parse(await readFile(join(here,'source-receipt.json'))),harness=JSON.parse(await readFile(join(here,'harness-receipt.json')));
for(const file of [...source.changed,...source.unchanged]){
  const path=file.path.slice('builtins/node-compat/'.length);
  assert.equal(hash(await readFile(join(here,'base/builtins/node-compat',path))),file.before);
  assert.equal(hash(await readFile(join(here,'source/builtins/node-compat',path))),file.after);
  assert.equal(hash(await readFile(join(repository,file.path))),file.before);
}
for(const file of harness.changes){
  assert.equal(hash(await readFile(join(here,'harness/source',file.path))),file.after);
  if(file.before){assert.equal(hash(await readFile(join(here,'harness/base',file.path))),file.before);assert.equal(hash(await readFile(join(repository,file.path))),file.before);}
}
const poison=JSON.parse(await readFile(join(here,'stub-hardening-results.json')));
assert.equal(poison.testSha256,hash(await readFile(join(here,'check-stub-hardening.mjs'))));
for(const variant of poison.variants){assert.equal(variant.operations,240);assert.equal(variant.prototypeFunctions,91);assert.deepEqual(variant.counts,{globalError:0,publicDefineProperty:0,inheritedGets:0,inheritedSets:0});}
const names=['README.md','../prepare-v2.mjs','run-host.mjs','run-harness-tests.mjs','check-stub-hardening.mjs','freeze.mjs','source-receipt.json','harness-receipt.json','host-results.json','harness-host-results.json','stub-hardening-results.json','core-m0.8.patch','harness-m0.8.patch'];
const files=await Promise.all(names.map(async path=>{const bytes=await readFile(join(here,path));return{path,sha256:hash(bytes),bytes:bytes.length};}));
const index={schema:1,proposalVersion:source.proposalVersion,coreVersion:source.candidateCoreVersion,installed:false,v1Preserved:true,v1IndexSha256:hash(v1IndexBytes),
  changedProductionInputs:source.changed.length,deltaFromV1:source.deltaFromV1,sourcePatchSha256:source.patchSha256,harnessPatchSha256:harness.patchSha256,
  hostChecks:{allocationDifferentialGroupsPerForm:10,allocationPolicyGroupsPerForm:5,receiptCases:46,refusalPoisonChecksPerForm:240,prototypeFunctions:91,forms:2},
  productionAndActiveHarnessUnchanged:true,files,
  scope:'Uninstalled source/strict-factory/host proof only. No m0.8 engine/component or genuine OOM. Poison tests call only pure-JS candidate refusal functions.'};
await writeFile(join(here,'index.json'),JSON.stringify(index,null,2)+'\n');
console.log(JSON.stringify({coreVersion:index.coreVersion,files:files.length,sourcePatchSha256:source.patchSha256,harnessPatchSha256:harness.patchSha256,v1Preserved:true,installed:false}));
