// Private source copies/patches only. Never writes production/native build files.
import assert from 'node:assert/strict';
import {readFile,writeFile,readdir,mkdir,copyFile,cp} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
assert.equal(process.version,'v22.14.0');
const here=dirname(fileURLToPath(import.meta.url)),frozen='/tmp/starling-node-compat/foundations-v8/native-freeze';
const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
const metadataBytes=await readFile(join(frozen,'off-foundations.engine.wasm.build.json')),metadata=JSON.parse(metadataBytes);
assert.equal(metadata.engineSha256,'e16c19fc567753517d7b61b65372dd7dc86de8f839e7acab959b5cf5eaf294c9');
assert.equal(hash(await readFile(join(frozen,'off-foundations.engine.wasm'))),metadata.engineSha256);
assert.equal(metadata.sourceManifest.length,293);
for(const file of metadata.sourceManifest)assert.equal(hash(await readFile(join(frozen,'source',file.path))),file.sha256,file.path);
async function files(root,prefix=''){
  const result=[];for(const entry of await readdir(join(root,prefix),{withFileTypes:true})){
    const path=join(prefix,entry.name);if(entry.isDirectory())result.push(...await files(root,path));else result.push(path);
  }return result.sort();
}
if(process.argv.includes('--check')){
  const receipt=JSON.parse(await readFile(join(here,'source-receipt.json')));
  for(const variant of ['ancestry','baseline','candidate'])for(const file of receipt.files)
    assert.equal(hash(await readFile(join(here,variant,file.path))),file[variant],variant+'/'+file.path);
  for(const patch of receipt.patches)assert.equal(hash(await readFile(join(here,patch.name))),patch.sha256,patch.name);
  console.log(JSON.stringify({state:'private-source-pair-receipt-verified',files:receipt.files.length,productionApplied:false}));process.exit(0);
}
await writeFile(join(here,'staging-started.json'),JSON.stringify({atUtc:new Date().toISOString(),ancestryEngineSha256:metadata.engineSha256})+'\n',{flag:'wx'});
const relative='builtins/node-compat',source=join(frozen,'source',relative),names=await files(source);
for(const variant of ['ancestry','baseline','candidate'])for(const name of names){const target=join(here,variant,relative,name);await mkdir(dirname(target),{recursive:true});await copyFile(join(source,name),target);}
const roots=Object.fromEntries(['ancestry','baseline','candidate'].map(variant=>[variant,join(here,variant,relative)]));
for(const variant of ['baseline','candidate']){
  const manifestPath=join(roots[variant],'export-manifest.node-v22.14.0.json'),manifest=JSON.parse(await readFile(manifestPath));
  assert.equal(manifest.profileVersion,'sm-node-22.14.0-m0.8');manifest.profileVersion='sm-node-22.14.0-m0.11';
  await writeFile(manifestPath,JSON.stringify(manifest,null,2)+'\n');
  const helperPath=join(roots[variant],'unsupported.mjs'),helper=await readFile(helperPath,'utf8');
  assert.equal((helper.match(/sm-node-22\.14\.0-m0\.8/g)??[]).length,1);
  await writeFile(helperPath,helper.replace('sm-node-22.14.0-m0.8','sm-node-22.14.0-m0.11'));
}
const facadePath=join(roots.candidate,'buffer-facade.mjs'),facade=await readFile(facadePath,'utf8');
const before='return unsafeApply(unsafeAlloc, Buffer, [unsafeTrunc(length)]);',after='return tagTrusted(new U8(unsafeTrunc(length)));';
assert.equal(facade.split(before).length,2);await writeFile(facadePath,facade.replace(before,after));
const generator=[];
for(const variant of ['baseline','candidate'])for(const check of [false,true]){
  const command=spawnSync(process.execPath,[join(roots[variant],'generate-factories.mjs'),...(check?['--check']:[])],{encoding:'utf8'});
  assert.equal(command.status,0,command.stderr||command.stdout);generator.push({variant,check,exitCode:command.status,stdout:command.stdout,stderr:command.stderr});
}
const records=[];
for(const name of names){const path=join(relative,name),entry={path};for(const variant of ['ancestry','baseline','candidate'])entry[variant]=hash(await readFile(join(roots[variant],name)));records.push(entry);}
const pairChanged=records.filter(file=>file.baseline!==file.candidate).map(file=>file.path);
assert.deepEqual(pairChanged,['builtins/node-compat/buffer-facade.mjs','builtins/node-compat/factories.generated.h']);
assert.equal(hash(await readFile(join(roots.baseline,'buffer.cpp'))),metadata.sourceManifest.find(file=>file.path==='builtins/node-compat/buffer.cpp').sha256);
const patches=[];
for(const[name,from,to]of[['common-m0.11-from-v8.patch','ancestry','baseline'],['direct-from-common.patch','baseline','candidate'],['candidate-m0.11-from-v8.patch','ancestry','candidate']]){
  let text='';for(const file of records.filter(file=>file[from]!==file[to])){
    const diff=spawnSync('diff',['-u','-L','a/'+file.path,'-L','b/'+file.path,join(here,from,file.path),join(here,to,file.path)],{encoding:'utf8'});
    assert.equal(diff.status,1,diff.stderr);text+=diff.stdout;
  }await writeFile(join(here,name),text);patches.push({name,from,to,sha256:hash(text),files:records.filter(file=>file[from]!==file[to]).map(file=>file.path)});
}
const patchChecks=[];
for(const patch of patches){
  const scratch=join('/tmp/starling-node-compat/allocunsafe-m0.11-source-check',patch.from+'-'+patch.to);
  await mkdir(scratch,{recursive:true});await cp(join(here,patch.from),scratch,{recursive:true});
  const command=spawnSync('git',['apply','--check',resolve(here,patch.name)],{cwd:scratch,encoding:'utf8'});assert.equal(command.status,0,command.stderr);
  patchChecks.push({patch:patch.name,exitCode:command.status,stderr:command.stderr});
}
await mkdir(join(here,'proof'),{recursive:true});const header='/tmp/starling-node-compat/improved-build/spidermonkey-dist-release/include/js/experimental/TypedData.h';
await copyFile(header,join(here,'proof/TypedData.h'));
const receipt={schema:1,state:'unapplied-private-source-pair-prepared',atUtc:new Date().toISOString(),productionApplied:false,
  ancestryEngineSha256:metadata.engineSha256,ancestryMetadataSha256:hash(metadataBytes),ancestrySourceRoot:join(frozen,'source'),ancestrySourceManifest:metadata.sourceManifest,
  profileVersion:'sm-node-22.14.0-m0.11',baseCoreVersion:'sm-node-22.14.0-m0.8',files:records,pairChanged,patches,generator,patchChecks,
  expression:{before,after},proofHeader:{originalPath:header,sha256:hash(await readFile(header))},
  ownership:'JS-owned captured Uint8Array -> existing tagTrusted private prototype/WeakSet; no C++/raw borrow/allocator transfer',
  engineBuilt:false,componentTested:false,measured:false,
  rebasePolicy:'Private frozen-v8 ancestry only; separately reconcile/re-receipt any common m0.9 additions in BOTH arms before production promotion'};
await writeFile(join(here,'source-receipt.json'),JSON.stringify(receipt,null,2)+'\n');
console.log(JSON.stringify({state:receipt.state,files:records.length,pairChanged,patches:patches.map(patch=>({name:patch.name,sha256:patch.sha256})),productionApplied:false,engineBuilt:false}));
