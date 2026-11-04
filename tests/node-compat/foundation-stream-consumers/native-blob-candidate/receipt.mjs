// Source/patch verification only. No C++ compilation or native execution.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFile,writeFile} from 'node:fs/promises';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
assert.equal(process.version,'v22.14.0');
const here=dirname(fileURLToPath(import.meta.url)),repository=resolve(here,'../../../..');
const hash=value=>createHash('sha256').update(value).digest('hex');
const base=JSON.parse(await readFile(join(here,'base-receipt.json'))),proof=JSON.parse(await readFile(join(here,'api-proof.json')));
let patch='';const files=[];
for(const item of base.files){
  const before=await readFile(join(here,'base',item.path)),after=await readFile(join(here,'source',item.path));
  assert.equal(hash(before),item.sha256);assert.equal(hash(await readFile(join(repository,item.path))),item.sha256);
  assert.notEqual(hash(after),item.sha256,'Expected coordinated hardening delta: '+item.path);
  const diff=spawnSync('diff',['-u','--label','a/'+item.path,join(here,'base',item.path),'--label','b/'+item.path,join(here,'source',item.path)],{encoding:'utf8'});
  assert.equal(diff.status,1);patch+=diff.stdout;files.push({path:item.path,before:item.sha256,after:hash(after)});
}
await writeFile(join(here,'blob-owned-copy-v1.patch'),patch);
const applicable=spawnSync('git',['apply','--check',join(here,'blob-owned-copy-v1.patch')],{cwd:repository,encoding:'utf8'});
assert.equal(applicable.status,0,applicable.stderr);
for(const item of proof.files)assert.equal(hash(await readFile(join(proof.headersRoot,item.path))),item.sha256);
assert.equal(hash(await readFile(join(here,'../index.json'))),base.consumerSourceFreezeSha256);
assert.equal(hash(await readFile(join(here,'../component-index.json'))),base.consumerComponentFreezeSha256);
const sourceIndex=JSON.parse(await readFile(join(here,'../index.json'))),componentIndex=JSON.parse(await readFile(join(here,'../component-index.json')));
for(const item of [...sourceIndex.files,...componentIndex.files])assert.equal(hash(await readFile(join(here,'..',item.path))),item.sha256);
const linkage=[];
for(const path of ['include/builtin.h','include/extension-api.h','runtime/builtin.cpp','runtime/event_loop.cpp',
  'builtins/web/streams/buf-reader.h','builtins/web/streams/buf-reader.cpp','builtins/web/streams/native-stream-source.h','builtins/web/streams/native-stream-source.cpp',
  'builtins/web/form-data/form-data.cpp','builtins/web/form-data/form-data-encoder.cpp','builtins/web/fetch/fetch-api.cpp','builtins/web/fetch/request-response.cpp',
  'builtins/web/structured-clone.cpp','builtins/web/url.cpp','cmake/builtins.cmake']){
  const bytes=await readFile(join(repository,path));linkage.push({path,sha256:hash(bytes)});
}
const before=await readFile(join(here,'base/builtins/web/blob.cpp'),'utf8'),after=await readFile(join(here,'source/builtins/web/blob.cpp'),'utf8');
for(const section of ['const JSFunctionSpec Blob::methods[] = {','const JSPropertySpec Blob::properties[] = {']){
  const extract=text=>text.slice(text.indexOf(section),text.indexOf('\n};',text.indexOf(section))+3);
  assert.equal(extract(after),extract(before),'No JS export inventory/attribute changes');
}
assert.doesNotMatch(after,/NewArrayBufferWithContents|MakeUnique<uint8_t\[\]>|value_to_buffer\(/,'No old ownership transfer/raw helper path');
assert.equal((after.match(/DEFINE_BLOB_PROMISE_METHOD\((?:arrayBuffer|bytes|text)\)/g)??[]).length,3);
const report={schema:1,candidateVersion:base.candidateVersion,compiled:false,nativeTestsRun:false,productionInstalled:false,
  engineControl:{engineSha256:base.engineSha256,sourceInputs:base.sourceInputs,sourceRoot:base.frozenSourceRoot},
  files,patchSha256:hash(patch),patchApplyCheck:true,apiProofSha256:hash(await readFile(join(here,'api-proof.json'))),
  existingLinkageSourcesUnchanged:linkage,consumerSourceAndComponentRecordsUnchanged:true,jsExportInventoryUnchanged:true,
  scope:'Unapplied native source candidate only. Source/API/patch applicability checks do not prove compilation, runtime behavior, GC stress, allocation failure or compatibility.'};
await writeFile(join(here,'source-receipt.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({changedFiles:files.length,apiHeaders:proof.files.length,apiDeclarations:proof.apis.length,patchApplyCheck:true,compiled:false,nativeTestsRun:false,productionInstalled:false}));
