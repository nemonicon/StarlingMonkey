// Recompute the UNAPPLIED proposal receipt/patch after source-only harness work.
import assert from 'node:assert/strict';
import {readFile,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
const here=dirname(fileURLToPath(import.meta.url)),repo=resolve(here,'../../../..'),hash=bytes=>createHash('sha256').update(bytes).digest('hex');
const receipt=JSON.parse(await readFile(join(here,'source-receipt.json')));
for(const file of receipt.ancestry)assert.equal(hash(await readFile(join(repo,file.path))),file.sha256,'Live native ancestry changed: '+file.path);
for(const file of[...receipt.protected10,...receipt.unchangedCritical]){
  assert.equal(hash(await readFile(join(repo,file.path))),file.sha256,file.path);
  assert.equal(hash(await readFile(join(here,'source',file.path))),file.sha256,file.path);
}
let patch='';
for(const change of receipt.changes){
  change.after=hash(await readFile(join(here,'source',change.path)));
  const before=change.before===null?'/dev/null':join(here,'base',change.path);
  const diff=spawnSync('diff',['-u','-L',change.before===null?'/dev/null':'a/'+change.path,'-L','b/'+change.path,before,join(here,'source',change.path)],{encoding:'utf8'});
  assert.equal(diff.status,1,diff.stderr);patch+=diff.stdout;
}
await writeFile(join(here,'core-m0.11-rebased.patch'),patch);
const result=spawnSync('git',['apply','--check',join(here,'core-m0.11-rebased.patch')],{cwd:repo,encoding:'utf8'});
assert.equal(result.status,0,result.stderr);
receipt.patchSha256=hash(patch);receipt.patchApplyCheck=0;receipt.refreshedAtUtc=new Date().toISOString();
receipt.futureRebaseRequired=['Root forthcoming HTTP-v10 positive/handled protected-abort corpus and its builder recognition must be additively rebased before application/promotion',
  'Combined current m0.10 protected ABI + core m0.11 native/GC/fullcore/strict/HTTP target-host proof remains required; private v8 experiment does not substitute'];
await writeFile(join(here,'source-receipt.json'),JSON.stringify(receipt,null,2)+'\n');
console.log(JSON.stringify({state:receipt.state,patchSha256:receipt.patchSha256,nativeAncestry:304,changedFiles:receipt.changes.length,applyCheck:0,protected10Unchanged:true,applied:false}));
