// Read-only source/artifact admission; never loads a componentizer or guest.
import assert from 'node:assert/strict';
import {readFile,writeFile,lstat} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {dirname,join,resolve} from 'node:path';
const here=dirname(fileURLToPath(import.meta.url));
const family=process.argv[3]??'production-runtime-activated-v1';
assert(['production-runtime-activated-v1','production-runtime-activated-v2','production-runtime-activated-v3'].includes(family));
const root=resolve(here,'..',family);
const expected=process.argv[2];
assert(/^[0-9a-f]{64}$/.test(expected));
const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
async function verifyIndex(){
  const raw=await readFile(join(root,'index.json'));
  assert.equal(hash(raw),expected);
  const document=JSON.parse(raw);
  for(const row of document.files){
    assert(!row.path.startsWith('/')&&!row.path.split('/').includes('..'));
    const path=join(root,row.path),stat=await lstat(path);
    assert(stat.isFile()&&!stat.isSymbolicLink());
    const data=await readFile(path);assert.equal(hash(data),row.sha256,path);assert.equal(data.length,row.bytes,path);
  }
  return document.files.length;
}
const files=await verifyIndex();
const {classicPreflight}=await import(pathToFileURL(join(root,'runtime-preflight.mjs')));
const variants=[];
for(const variant of ['normal-off','normal-runtime','gc-off','disabled-off']){
  const admission=await classicPreflight({variant});
  assert.equal(admission.variant,variant);
  const pin=admission.pin;
  // The returned descriptive copy cannot redirect the recheck's private roots.
  const original=pin.freezeRoot;
  pin.freezeRoot='/tmp/starling-node-compat/MUST_NOT_FOLLOW_PUBLIC_PIN_MUTATION';
  await admission.recheck();
  pin.freezeRoot=original;
  variants.push({variant,engineSha256:admission.metadata.engineSha256,
    sourceFiles:admission.metadata.sourceManifest.length,publicPinMutationCannotRedirectRecheck:true});
}
await verifyIndex();
const result={schemaVersion:1,state:'ROOT_FOUR_ACTUAL_CLASSIC_PREFLIGHTS_PASSED',
  activatedIndexSha256:expected,activatedSourceFiles:files,variants,
  componentizerInvoked:false,guestInvoked:false,runtimeSupportAccepted:false};
const output=family.endsWith('-v3')?'activated-preflight-v3-results.json':family.endsWith('-v2')?'activated-preflight-v2-results.json':'activated-preflight-results.json';
await writeFile(join(here,output),JSON.stringify(result,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify(result));
