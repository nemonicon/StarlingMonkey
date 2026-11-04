// Freeze only source candidates and read-only proof; never compile/run/apply.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFile,writeFile} from 'node:fs/promises';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
assert.equal(process.version,'v22.14.0');
const here=dirname(fileURLToPath(import.meta.url)),repository=resolve(here,'../../../..'),hash=v=>createHash('sha256').update(v).digest('hex');
const receipt=JSON.parse(await readFile(join(here,'source-receipt.json'))),base=JSON.parse(await readFile(join(here,'base-receipt.json')));
assert.equal(hash(await readFile(join(here,'blob-owned-copy-v1.patch'))),receipt.patchSha256);
assert.equal(hash(await readFile(join(here,'api-proof.json'))),receipt.apiProofSha256);
assert.equal(receipt.compiled,false);assert.equal(receipt.nativeTestsRun,false);assert.equal(receipt.productionInstalled,false);
for(const file of receipt.files){
  assert.equal(hash(await readFile(join(here,'base',file.path))),file.before);
  assert.equal(hash(await readFile(join(here,'source',file.path))),file.after);
  assert.equal(hash(await readFile(join(repository,file.path))),file.before);
}
for(const item of receipt.existingLinkageSourcesUnchanged)assert.equal(hash(await readFile(join(repository,item.path))),item.sha256);
assert.equal(hash(await readFile(join(here,'../index.json'))),base.consumerSourceFreezeSha256);
assert.equal(hash(await readFile(join(here,'../component-index.json'))),base.consumerComponentFreezeSha256);
for(const indexName of ['../index.json','../component-index.json']){
  const index=JSON.parse(await readFile(join(here,indexName)));
  for(const item of index.files)assert.equal(hash(await readFile(join(here,'..',item.path))),item.sha256);
}
const names=['README.md','api-proof.mjs','api-proof.json','prepare-source.mjs','base-receipt.json','receipt.mjs','source-receipt.json','blob-owned-copy-v1.patch','freeze.mjs',
  ...receipt.files.flatMap(file=>['base/'+file.path,'source/'+file.path])];
const files=await Promise.all(names.map(async path=>{const bytes=await readFile(join(here,path));return{path,sha256:hash(bytes),bytes:bytes.length};}));
const index={schema:1,candidateVersion:receipt.candidateVersion,compiled:false,nativeTestsRun:false,productionInstalled:false,
  selectedProductionProfileVersion:null,newHostInterfaces:[],patchSha256:receipt.patchSha256,
  engineSourceControl:receipt.engineControl,consumerRecordsUnchanged:true,productionAndLinkageSourcesUnchanged:true,files,
  scope:'Unapplied four-file native source candidate and exact header/ownership proof only. No compiler/runtime/GC/OOM/compatibility or performance pass is claimed.'};
await writeFile(join(here,'index.json'),JSON.stringify(index,null,2)+'\n');
console.log(JSON.stringify({files:files.length,patchSha256:receipt.patchSha256,compiled:false,nativeTestsRun:false,productionInstalled:false}));
