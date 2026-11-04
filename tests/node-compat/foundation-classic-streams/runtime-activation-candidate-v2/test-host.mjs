// Owned tiny-text integrity tests only. No actual package, engine or guest load.
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { mkdtemp, mkdir, readFile, writeFile, readdir, lstat, symlink, unlink, realpath } from 'node:fs/promises';
import { dirname, join, relative } from 'node:path';
import { fileURLToPath } from 'node:url';
import { verifyConsumedSeal } from './consumed.mjs';
assert.equal(process.version, 'v22.14.0');
const hash = data => createHash('sha256').update(data).digest('hex');
const HERE = dirname(fileURLToPath(import.meta.url));
const root = await mkdtemp('/tmp/starling-node-compat/classic-activation-host-v1-');
const cases = [];
async function check(name, fn) { await fn(); cases.push(name); }
const input = join(root, 'owned.txt'); await writeFile(input, 'original owned text');
const row = {path:input,sha256:hash(await readFile(input)),bytes:(await readFile(input)).length};
const base = {schemaVersion:1, inputs:[row], toolTrees:[], toolLinks:[]};
async function manifest(document) { const data=JSON.stringify(document);await writeFile(join(root,'input-freeze.json'),data);return hash(data); }
let expected = await manifest(base);
await check('original owned text passes',async()=>assert.equal(await verifyConsumedSeal(root,expected,null,{invocation:false}),1));
await check('listed file tamper is rejected',async()=>{
  await writeFile(input,'changed');await assert.rejects(verifyConsumedSeal(root,expected,null,{invocation:false}));await writeFile(input,'original owned text');
});
await check('replacement manifest plus replacement file fails original digest before rows',async()=>{
  await writeFile(input,'replacement');await manifest({...base,inputs:[{path:join(root,'must-not-be-opened'),sha256:hash('replacement'),bytes:11}]});
  await assert.rejects(verifyConsumedSeal(root,expected,null,{invocation:false}),/Consumed-input manifest changed/);
  await writeFile(input,'original owned text');await manifest(base);
});
await check('malformed replacement JSON fails digest before parsing',async()=>{
  await writeFile(join(root,'input-freeze.json'),'{broken');await assert.rejects(verifyConsumedSeal(root,expected,null,{invocation:false}),/Consumed-input manifest changed/);await manifest(base);
});
await check('symlink ordinary input is refused',async()=>{
  const path=join(root,'alias');await symlink(input,path);const sha=await manifest({...base,inputs:[{...row,path}]});
  await assert.rejects(verifyConsumedSeal(root,sha,null,{invocation:false}));await unlink(path);await manifest(base);
});
await check('protected source boundary rejects a symlinked parent',async()=>{
  const target=join(root,'owned-other');await mkdir(target);await writeFile(join(target,'data.txt'),'owned');
  const alias=join(root,'parent-alias');await symlink(target,alias);
  const sha=await manifest({...base,inputs:[{path:join(alias,'data.txt'),sha256:hash('owned'),bytes:5,boundary:root}]});
  await assert.rejects(verifyConsumedSeal(root,sha,null,{invocation:false}));await unlink(alias);await manifest(base);
});
const treeRoot=join(root,'tools');await mkdir(treeRoot);await writeFile(join(treeRoot,'tool.txt'),'owned tool');
const link=join(treeRoot,'tool-link');await symlink('tool.txt',link);
const toolRow={path:join(treeRoot,'tool.txt'),sha256:hash('owned tool'),bytes:10};
const treeDoc={schemaVersion:1,inputs:[toolRow],toolTrees:[{path:treeRoot,realPath:await realpath(treeRoot),entries:[{path:'tool-link',kind:'symlink'},{path:'tool.txt',kind:'file'}]}],
  toolLinks:[{path:link,linkText:'tool.txt',resolvedTarget:await realpath(join(treeRoot,'tool.txt')),targetKind:'file',targetSha256:hash('owned tool'),targetBytes:10}]};
expected=await manifest(treeDoc);
await check('known internal file link passes exact text target and hash',async()=>assert.equal(await verifyConsumedSeal(root,expected,null,{invocation:false}),1));
await check('changed link text refused even if target bytes identical',async()=>{
  await unlink(link);await symlink('./tool.txt',link);await assert.rejects(verifyConsumedSeal(root,expected,null,{invocation:false}));await unlink(link);await symlink('tool.txt',link);
});
await check('new tool file is not silently excluded',async()=>{
  const path=join(treeRoot,'cache.txt');await writeFile(path,'new');await assert.rejects(verifyConsumedSeal(root,expected,null,{invocation:false}),/Tool-root membership changed/);await unlink(path);
});
await check('new empty tool directory is not silently excluded',async()=>{
  const path=join(treeRoot,'empty-cache');await mkdir(path);await assert.rejects(verifyConsumedSeal(root,expected,null,{invocation:false}),/Tool-root membership changed/);
  const {rmdir}=await import('node:fs/promises');await rmdir(path);
});
await check('compiled preflight is checked from captured template bytes',async()=>{
  const template="const x='@VALUE@';\n",compiled="const x='owned';\n";
  await writeFile(join(root,'runtime-preflight.template.mjs'),template);await writeFile(join(root,'runtime-preflight.mjs'),compiled);
  const sha=await manifest({...base,inputs:[{path:'runtime-preflight.template.mjs',sha256:hash(template),bytes:Buffer.byteLength(template)}]});
  assert.equal(await verifyConsumedSeal(root,sha,{VALUE:'owned'},{invocation:false}),1);
  await writeFile(join(root,'runtime-preflight.mjs'),'changed');await assert.rejects(verifyConsumedSeal(root,sha,{VALUE:'owned'},{invocation:false}),/Compiled preflight differs/);
});
await check('all five inherited source placeholders remain explicitly wired',async()=>{
  const source=await readFile(join(HERE,'runtime-preflight.template.mjs'),'utf8');
  const names=[...source.matchAll(/@([A-Z_]+)@/g)].map(x=>x[1]).sort();
  assert.deepEqual(names,['ADMISSION_SHA','INPUTS_SHA','PINS_SHA','RECIPE_SHA','SELECTOR_SHA']);
  assert(source.includes('{PINS_SHA,INPUTS_SHA,RECIPE_SHA,SELECTOR_SHA,ADMISSION_SHA}'));
});
const result={schemaVersion:1,state:'OWNED_TEXT_CONSUMED_SEAL_CHECKS_PASSED',passed:cases.length,failures:0,cases,output:root,
  actualEnginePinsUsed:false,packageLoaderInvoked:false,producerInvoked:false,guestOrTargetHostExecuted:false};
await writeFile(join(root,'results.json'),JSON.stringify(result,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify(result));
