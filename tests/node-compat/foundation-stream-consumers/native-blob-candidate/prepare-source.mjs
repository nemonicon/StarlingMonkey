// Copy only four existing native files from the immutable v7 source control.
// No production/native build, test, CMake or manifest edit is performed.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {mkdir,readFile,writeFile,stat} from 'node:fs/promises';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
assert.equal(process.version,'v22.14.0');
const here=dirname(fileURLToPath(import.meta.url)),repository=resolve(here,'../../../..');
const frozen='/tmp/starling-node-compat/foundations-v7/native-freeze',source=join(frozen,'source');
const hash=value=>createHash('sha256').update(value).digest('hex');
const receiptBytes=await readFile(join(frozen,'off-foundations.engine.wasm.build.json')),receipt=JSON.parse(receiptBytes);
assert.equal(receipt.engineSha256,'ee92d5d451c16eb7ce83e0306e8dab6920f4aacd9f2c4bb9d6e5e4af2c20ea09');
assert.equal(hash(await readFile(join(frozen,'off-foundations.engine.wasm'))),receipt.engineSha256);
assert.equal(receipt.sourceManifest.length,293);
try{await stat(join(here,'source'));throw new Error('Isolated source already exists; preserve it rather than overwriting');}catch(error){if(error.code!=='ENOENT')throw error;}
const files=[];
for(const path of ['builtins/web/blob.cpp','builtins/web/blob.h','builtins/web/file.cpp','builtins/web/file.h']){
  const bytes=await readFile(join(source,path)),sha256=hash(bytes);
  assert.equal(receipt.sourceManifest.find(e=>e.path===path)?.sha256,sha256);
  assert.equal(hash(await readFile(join(repository,path))),sha256,'Production must match preserved v7 base: '+path);
  for(const side of ['base','source']){await mkdir(dirname(join(here,side,path)),{recursive:true});await writeFile(join(here,side,path),bytes);}
  files.push({path,sha256});
}
const sourceIndex=await readFile(join(here,'../index.json')),componentIndex=await readFile(join(here,'../component-index.json'));
await writeFile(join(here,'base-receipt.json'),JSON.stringify({schema:1,candidateVersion:'native-blob-owned-copy-v1',compiled:false,nativeTestsRun:false,
  engineSha256:receipt.engineSha256,engineReceiptSha256:hash(receiptBytes),sourceInputs:293,frozenSourceRoot:source,files,
  consumerSourceFreezeSha256:hash(sourceIndex),consumerComponentFreezeSha256:hash(componentIndex),productionInstalled:false},null,2)+'\n');
console.log(JSON.stringify({files:files.length,compiled:false,nativeTestsRun:false,productionInstalled:false}));
