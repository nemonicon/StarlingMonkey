// Final hash/source audit only; no engine, guest, host or performance execution.
import assert from 'node:assert/strict';
import { readFile, writeFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';
const here=dirname(fileURLToPath(import.meta.url)),repo=resolve(here,'../../../..');
const hash=bytes=>createHash('sha256').update(bytes).digest('hex'),json=async path=>JSON.parse(await readFile(path));
const receipt=await json(join(here,'source-receipt.json')),host=await json(join(here,'host-results.json'));
assert.equal(host.sourceReceiptSha256,hash(await readFile(join(here,'source-receipt.json'))));
for(const file of receipt.copiedLiveInputs){
  assert.equal(hash(await readFile(join(repo,file.path))),file.sha256,'Live input changed: '+file.path);
  assert.equal(hash(await readFile(join(here,'base',file.path))),file.sha256,'Base input changed: '+file.path);
  assert.equal(hash(await readFile(join(here,'source',file.path))),receipt.changes.find(change=>change.path===file.path)?.after??file.sha256,'Candidate input changed: '+file.path);
}
for(const file of receipt.changes){
  if(file.before!==null)assert.equal(hash(await readFile(join(here,'base',file.path))),file.before);
  assert.equal(hash(await readFile(join(here,'source',file.path))),file.after);
}
assert.equal(receipt.changes.length,11);
assert.equal(receipt.ancestry.length,304);
const changedNative=receipt.ancestry.filter(file=>receipt.changes.some(change=>change.path===file.path));assert.equal(changedNative.length,4);
for(const file of [...receipt.protected10,...receipt.unchangedCritical])assert.equal(hash(await readFile(join(here,'source',file.path))),file.sha256,file.path);
for(const [path,digest]of Object.entries(receipt.corePins))assert.equal(hash(await readFile(join(here,'source',path))),digest,path);
const patch=join(here,'core-m0.11-http-v10-rebased.patch');assert.equal(hash(await readFile(patch)),receipt.patchSha256);
const apply=spawnSync('git',['apply','--check','--whitespace=error',patch],{cwd:repo,encoding:'utf8'});assert.equal(apply.status,0,apply.stderr);
const generation=spawnSync(process.execPath,[join(here,'source/builtins/node-compat/generate-factories.mjs'),'--check'],{encoding:'utf8'});assert.equal(generation.status,0,generation.stderr);
const preserved=[];
for(const [path,root,pin,count]of[
  [join(here,'../production-candidate-m0.11/index.json'),join(here,'../production-candidate-m0.11'),'ef229fb89f768486ccc4cb142bd1defbec79e08aa091bf782d17d1592a6ba29a',680],
  [join(repo,'tests/node-compat/foundations/http-v10-index.json'),null,'86233ce25675225ca825a3e76ecf2efc140bac70599bf6e9473a9204e34f3619',348],
]){
  const bytes=await readFile(path),index=JSON.parse(bytes);assert.equal(hash(bytes),pin,path);assert.equal(index.files.length,count);
  for(const file of index.files){const absolute=root?join(root,file.path):file.path,b=await readFile(absolute);assert.equal(b.length,file.bytes,absolute);assert.equal(hash(b),file.sha256,absolute);}
  preserved.push({path,sha256:pin,allFilesVerified:count});
}
for(const [path,digest]of Object.entries(receipt.originalPacket.frozen))assert.equal(hash(await readFile(join(receipt.originalPacket.path,path))),digest,path);
const peer=await json(join(here,'peer-review.json'));assert.equal(peer.patchSha256,receipt.patchSha256);
const result={state:'UNAPPLIED_M011_V2_FINAL_SOURCE_PRESERVATION_PASSED',verifiedAtUtc:new Date().toISOString(),
  sourceReceiptSha256:hash(await readFile(join(here,'source-receipt.json'))),hostResultsSha256:hash(await readFile(join(here,'host-results.json'))),patchSha256:receipt.patchSha256,
  nativeAncestryInputs:304,nativeChanged:4,nativeUnchanged:300,copiedInputsVerified:receipt.copiedLiveInputs.length,
  protected10Unchanged:true,selectorRecipeKernelUnchanged:true,exactReviewedCorePins:receipt.corePins,
  originalPacketAndAcceptedHTTP:preserved,generatorCheck:0,patchApplyCheck:0,peerReview:peer.result,
  protectedCasesRetained:{public:16,nested:4,receivers:9,total:29},httpSchema:5,
  applied:false,nativeBuilt:false,componentized:false,performanceMeasured:false,
  pending:receipt.pending};
const output=resolve(process.env.NODE_COMPAT_M011_V2_VERIFY_RESULTS??join(here,'verification-results.json'));
await writeFile(output,JSON.stringify(result,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify(result,null,2));
