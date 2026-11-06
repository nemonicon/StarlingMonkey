// Authoring preparation only: private temporary copies; no ALS/native execution.
import assert from 'node:assert/strict';
import {mkdtemp,readFile,writeFile,mkdir,readdir} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {spawnSync} from 'node:child_process';
import {createHash} from 'node:crypto';
assert.equal(process.version,'v22.14.0');
const here=new URL('./',import.meta.url), refs=JSON.parse(await readFile(new URL('references.json',here)));
const digest=b=>createHash('sha256').update(b).digest('hex');
for(const row of [refs.oldGenerator,refs.pinnedNode,...refs.installedInputs]) {
  const bytes=await readFile(row.path);assert.equal(bytes.length,row.bytes);assert.equal(digest(bytes),row.sha256);
}
assert.equal(process.execPath,refs.pinnedNode.path);
const root=await mkdtemp(join(tmpdir(),'als-v4-installed-generator-'));
const target=join(root,'installation','builtins','node-compat');await mkdir(target,{recursive:true});
for(const name of await readdir(new URL('after/builtins/node-compat/',here)))
  await writeFile(join(target,name),await readFile(new URL('after/builtins/node-compat/'+name,here)));
const generator=join(target,'generate-async-hooks-factory.mjs');
const outcomes=[];let checks=0;
async function run(id,expected,needle) {
  const r=spawnSync(process.execPath,[generator,'--check'],{cwd:root,encoding:'utf8',timeout:10000,env:{PATH:process.env.PATH}});
  assert.equal(r.error,undefined);assert.equal(r.signal,null);assert.equal(r.status,expected);checks+=3;
  if(needle){assert((r.stdout+r.stderr).includes(needle));checks++;}
  outcomes.push({id,argv:[process.execPath,generator,'--check'],cwd:root,rawExitCode:r.status,signal:r.signal,stdout:r.stdout,stderr:r.stderr});
}
const current=await readFile(generator,'utf8');
await writeFile(generator,await readFile(refs.oldGenerator.path));await run('old-installed-layout-refuses-missing-external-inventory',1,'node22-surface.json');
await writeFile(generator,current);await run('same-sibling-installed-layout-check-passes',0,'canonicalSourceSha256');
const inventory=join(target,'async-hooks-node22-surface.json'), original=await readFile(inventory);
await writeFile(inventory,'{}\n');await run('corrupt-inventory-refuses',1,'AssertionError');
await writeFile(inventory,original);const manifest=join(target,'export-manifest.async-hooks.node-v22.14.0.json'), m=await readFile(manifest,'utf8');
await writeFile(manifest,m.replace('sm-node-22.14.0-m1.0','invalid-profile'));await run('mismatched-manifest-refuses',1,'AssertionError');
await writeFile(manifest,m);await run('restored-installed-layout-check-passes',0,'canonicalSourceSha256');
assert.equal(await readFile(join(target,'async-hooks-factory.generated.h'),'utf8'),await readFile(refs.unchangedHeader.path,'utf8'));checks++;
const result={schemaVersion:1,sourceOnly:true,checks,outcomes,nativeOrAlsWorkloadExecuted:false,privateTemporaryRoot:root};
await writeFile(new URL('installed-generator-test-results.json',here),JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify({checks,cases:outcomes.length,nativeOrAlsWorkloadExecuted:false}));
