// Ordinary PRIVATE TextDecoder candidate only. Never edits production sources.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFile,writeFile,mkdir,copyFile,symlink,access,readdir} from 'node:fs/promises';
import {dirname,join,resolve,relative} from 'node:path';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
const here=dirname(fileURLToPath(import.meta.url)),repo=resolve(here,'../../..');
const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
const freeze=resolve(process.env.NODE_COMPAT_DECODER_FREEZE??'/tmp/starling-node-compat/foundations-v4/native-freeze');
const root=resolve(process.env.NODE_COMPAT_DECODER_BUILD_ROOT??'/tmp/starling-node-compat/text-decoder-private/release-v1');
assert(root!==repo&&relative(repo,root).startsWith('..'),'Private source/build must be outside checkout');
const pins=JSON.parse(await readFile(join(here,'private-build-pins.json')));
const candidatePins=JSON.parse(await readFile(join(here,'text-decoder-candidate-pins.json')));
const basePath=join(freeze,'off-path-events.engine.wasm'),base=JSON.parse(await readFile(basePath+'.build.json'));
assert.equal(hash(await readFile(basePath)),pins.baseEngineSha256);
assert.equal(base.engineSha256,pins.baseEngineSha256);
assert.equal(hash(await readFile(basePath+'.build.json')),pins.baseReceiptSha256);
assert.equal(base.sourceManifest.length,271);
const codec='builtins/web/text-codec/text-decoder.cpp';
assert.equal(base.sourceManifest.find(entry=>entry.path===codec).sha256,candidatePins.baseSha256);
for(const entry of base.sourceManifest)assert.equal(hash(await readFile(join(freeze,'source',entry.path))),entry.sha256,entry.path);
const recipe=await readFile(join(freeze,'build-engine.sh'));
assert.equal(hash(recipe),pins.baseRecipeSha256);
assert.equal(hash(await readFile(join(here,'text-decoder.private-candidate.cpp'))),candidatePins.candidateSha256);
assert.equal(hash(await readFile(join(here,'text-decoder-ownership.private.patch'))),candidatePins.patchSha256);
if(process.argv.includes('--plan')){
  console.log(JSON.stringify({freeze,root,baseEngineSha256:base.engineSha256,sourceDelta:[codec],nativeInputs:271,
    flags:base.observedCMakeOptions,scope:'PRIVATE ordinary API safety candidate; no fault hooks, no production edits, no timing'},null,2));
  process.exit(0);
}
assert.equal(process.version,'v22.14.0');
try{await access(join(root,'build-started.json'));throw Error('Choose a fresh NODE_COMPAT_DECODER_BUILD_ROOT; preserve prior artifacts');}
catch(error){if(error.code!=='ENOENT')throw error;}
await mkdir(root,{recursive:true});
await writeFile(join(root,'build-started.json'),JSON.stringify({freeze,...pins,candidateSha256:candidatePins.candidateSha256},null,2)+'\n');
function command(program,args,options={}){
  const result=spawnSync(program,args,{stdio:'inherit',...options});
  assert.equal(result.status,0,`${program} failed (${result.status}): ${result.error?.message??''}`);
}
const source=join(root,'source');
command('git',['clone','--shared','--no-checkout',repo,source]);
command('git',['-C',source,'checkout','--detach',base.starlingMonkeyRevision]);
for(const entry of base.sourceManifest){
  const target=join(source,entry.path);await mkdir(dirname(target),{recursive:true});
  await copyFile(join(freeze,'source',entry.path),target);
}
for(const entry of pins.helpers){
  const input=entry.path.endsWith('openssl-source-audit.py')?join(freeze,'openssl-source-audit.py'):join(repo,entry.path);
  assert.equal(hash(await readFile(input)),entry.sha256,entry.path);
  const target=join(source,entry.path);await mkdir(dirname(target),{recursive:true});await copyFile(input,target);
}
const privateRecipe=join(source,'tests/node-compat/build-engine.sh');
await writeFile(privateRecipe,recipe,{mode:0o755});
command('patch',['-p1','-d',source],{input:await readFile(join(here,'text-decoder-ownership.private.patch')),stdio:['pipe','inherit','inherit']});
assert.equal(hash(await readFile(join(source,codec))),candidatePins.candidateSha256);
const work=join(root,'build'),shared=resolve(process.env.NODE_COMPAT_CACHE_ROOT??'/tmp/starling-node-compat/improved-build');
await mkdir(work,{recursive:true});
for(const directory of ['cache','tools'])await symlink(join(shared,directory),join(work,directory),'dir');
const env={...process.env,NODE_COMPAT_NODE:process.execPath,NODE_COMPAT_BUILD_ROOT:work,NODE_COMPAT_BUILD_TYPE:'Release',
  NODE_COMPAT_GC_STRESS:'0',NODE_COMPAT_OOM_TESTING:'0',NODE_COMPAT_ENTROPY_MODE:'OFF',NODE_COMPAT_PATH:'1',NODE_COMPAT_EVENTS:'1',
  NODE_COMPAT_ARTIFACT_TAG:'text-decoder-private-v1',CXXFLAGS:''};
command('bash',[privateRecipe],{env});
const artifacts=join(work,'artifacts');
const receipts=(await readdir(artifacts)).filter(name=>name.endsWith('.wasm.build.json')&&!name.endsWith('.raw.wasm.build.json'));
assert.equal(receipts.length,1);
const sidecar=join(artifacts,receipts[0]),metadata=JSON.parse(await readFile(sidecar));
assert.equal(hash(await readFile(metadata.enginePath)),metadata.engineSha256);
assert.equal(metadata.sourceManifest.length,base.sourceManifest.length);
assert.deepEqual(metadata.sourceManifest.map(entry=>entry.path),base.sourceManifest.map(entry=>entry.path));
for(const entry of metadata.sourceManifest){
  assert.equal(hash(await readFile(join(source,entry.path))),entry.sha256,entry.path);
  assert.equal(entry.sha256,entry.path===codec?candidatePins.candidateSha256:base.sourceManifest.find(other=>other.path===entry.path).sha256,entry.path);
}
for(const key of ['observedCMakeOptions','requestedCMakeOptions','componentizeSourceManifest','selectedModuleManifests','archivePins']){
  assert.deepEqual(metadata[key],base[key],key);
}
for(const key of ['sourceInputsCapturedBeforeBuild','componentizeSourcesCapturedBeforeBuild','buildRecipeCheckedBeforeAndAfterBuild'])assert.equal(metadata[key],true,key);
assert.equal(metadata.buildRecipeSha256,pins.baseRecipeSha256);
assert.equal(metadata.gcStress,false);assert.equal(metadata.oomTesting,false);
const commands=spawnSync('ninja',['-C',dirname(metadata.cmakeCachePath),'-t','commands','builtin_web_text_codec'],{encoding:'utf8',maxBuffer:8*1024*1024});
assert.equal(commands.status,0);
const compile=commands.stdout.split('\n').find(line=>line.includes(' -c ')&&line.endsWith('/text-decoder.cpp'));
assert(compile);assert(!/OOM_TESTING|UTF8_DIRECT_GC_STRESS|UTF8_DIRECT_OOM_TESTING/.test(compile));
metadata.privateTextDecoderCandidate={schemaVersion:1,sourceRoot:source,baselineEngineSha256:base.engineSha256,
  baselineReceiptSha256:pins.baseReceiptSha256,baselineRecipeSha256:pins.baseRecipeSha256,
  sameSourcePathSet:true,onlyChangedNativeSource:codec,candidateSha256:candidatePins.candidateSha256,
  patchSha256:candidatePins.patchSha256,actualDecoderCompileCommand:compile,
  scope:'PRIVATE ordinary API validation only. Production unchanged; no fault hooks or raw-memory probes; no performance claim.'};
await writeFile(sidecar,JSON.stringify(metadata,null,2)+'\n');
await writeFile(join(root,'accepted-build.json'),JSON.stringify({engine:metadata.enginePath,engineSha256:metadata.engineSha256,sidecar,sourceRoot:source},null,2)+'\n');
console.log(JSON.stringify({engine:metadata.enginePath,engineSha256:metadata.engineSha256,sidecar,sourceRoot:source},null,2));
