import assert from 'node:assert/strict';
import {readFile,writeFile} from 'node:fs/promises';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import {spawnSync} from 'node:child_process';
assert.equal(process.version,'v22.14.0');
const here=dirname(fileURLToPath(import.meta.url)),v1=resolve(here,'..'),repository=resolve(v1,'../../../..'),hash=v=>createHash('sha256').update(v).digest('hex');
const v1IndexBytes=await readFile(join(v1,'index.json')),v1Index=JSON.parse(v1IndexBytes),base=JSON.parse(await readFile(join(v1,'base-receipt.json')));
for(const item of v1Index.files)assert.equal(hash(await readFile(join(v1,item.path))),item.sha256);
const syntax=JSON.parse(await readFile(join(here,'sdk-syntax-results.json'))),prep=JSON.parse(await readFile(join(here,'preparation-receipt.json')));
assert.equal(syntax.state,'sdk30-sm147-two-tu-syntax-pass');assert.deepEqual(syntax.results.map(r=>r.exitCode),[0,0]);
assert.equal(syntax.v1IndexSha256,hash(v1IndexBytes));
assert.equal(syntax.contractProofSha256,hash(await readFile(join(here,'contract-proof.json'))));
const changed=[];let patch='';
for(const item of base.files){
  assert.equal(hash(await readFile(join(repository,item.path))),item.sha256);
  const after=hash(await readFile(join(here,'source',item.path)));changed.push({path:item.path,before:item.sha256,after});
  const diff=spawnSync('diff',['-u','--label','a/'+item.path,join(v1,'base',item.path),'--label','b/'+item.path,join(here,'source',item.path)],{encoding:'utf8'});assert.equal(diff.status,1);patch+=diff.stdout;
}
await writeFile(join(here,'blob-owned-copy-v2.patch'),patch);
const applicable=spawnSync('git',['apply','--check',join(here,'blob-owned-copy-v2.patch')],{cwd:repository,encoding:'utf8'});assert.equal(applicable.status,0,applicable.stderr);
for(const result of syntax.results){
  assert.equal(hash(await readFile(result.source)),result.sourceSha256);
  for(const header of result.headers)assert.equal(hash(await readFile(header.path)),header.sha256);
}
for(const item of prep.proofSources)assert.equal(hash(await readFile(join(here,'proof-source',item.path))),item.sha256);
const names=['README.md','preparation-receipt.json','contract-proof.json','prove-contracts.mjs','check-sdk-syntax.py','sdk-syntax-results.json','blob-owned-copy-v2.patch','freeze.mjs',
  ...changed.map(item=>'source/'+item.path),...prep.proofSources.map(item=>'proof-source/'+item.path)];
const files=await Promise.all(names.map(async path=>{const bytes=await readFile(join(here,path));return{path,sha256:hash(bytes),bytes:bytes.length};}));
const index={schema:1,candidateVersion:'native-blob-owned-copy-v2',syntaxChecked:true,translationUnits:2,linked:false,nativeTestsRun:false,productionInstalled:false,
  v1IndexSha256:hash(v1IndexBytes),v1Preserved:true,patchSha256:hash(patch),patchApplyCheck:true,changed,files,
  scope:'Actual SDK Release syntax plus source/contract proof only. No linked/native/component/GC/OOM/performance pass; no production version/capability added.'};
await writeFile(join(here,'index.json'),JSON.stringify(index,null,2)+'\n');
console.log(JSON.stringify({candidateVersion:index.candidateVersion,patchSha256:index.patchSha256,syntaxChecked:true,translationUnits:2,v1Preserved:true,linked:false,nativeTestsRun:false}));
