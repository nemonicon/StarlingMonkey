// PRIVATE sequential build/freeze controller. --verify is source-only now.
// --build requires a separate explicit coordinator authorization, then uses
// the byte-identical archived v8 recipe. Never changes the live repository.
import assert from 'node:assert/strict';
import {readFile,writeFile,mkdir,copyFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {dirname,join} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {spawnSync} from 'node:child_process';
const here=dirname(fileURLToPath(import.meta.url)),previous=dirname(here);
const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
const prepBytes=await readFile(join(here,'preparation-results.json')),prep=JSON.parse(prepBytes);
assert.equal(process.version,'v22.14.0');
async function verifyProject(arm){
  assert(['baseline','candidate'].includes(arm));
  for(const file of prep.sourceMapProof[arm])assert.equal(hash(await readFile(join(prep.project,file.path))),file.sha256,file.path);
  for(const file of [...prep.inputs,...prep.supportInputs])assert.equal(hash(await readFile(join(prep.project,file.path))),file.sha256,file.path);
  for(const file of prep.archives)assert.equal(hash(await readFile(file.path)),file.sha256,file.path);
  assert.equal(hash(await readFile(prep.recipe.path)),prep.recipe.sha256);
}
async function verifyFrozen(arm){
  const root=join(prep.experiment,'frozen',arm),freeze=JSON.parse(await readFile(join(root,'freeze.json')));
  for(const file of freeze.archivedFiles)assert.equal(hash(await readFile(join(root,file.path))),file.sha256,file.path);
  assert.equal(freeze.preparationSha256,hash(prepBytes));
  const metadata=JSON.parse(await readFile(join(root,'engine.wasm.build.json')));
  assert.equal(hash(await readFile(join(root,'engine.wasm'))),metadata.engineSha256);assert.equal(metadata.engineSha256,freeze.engineSha256);
  assert.deepEqual(metadata.sourceManifest,prep.sourceMapProof[arm]);
  assert.deepEqual(metadata.requestedCMakeOptions,prep.requestedCMakeOptions);assert.deepEqual(metadata.observedCMakeOptions,prep.requestedCMakeOptions);
  assert.equal(metadata.buildRecipeSha256,prep.recipe.sha256);assert.equal(metadata.sourceInputsCapturedBeforeBuild,true);
  assert.equal(metadata.buildRecipeCheckedBeforeAndAfterBuild,true);assert.equal(metadata.componentizeSourcesCapturedBeforeBuild,true);
  assert.equal(metadata.entropyPolicy,'off');assert.equal(metadata.strictInitialization,true);assert.equal(metadata.gcStress,false);assert.equal(metadata.oomTesting,false);
  for(const file of metadata.sourceManifest)assert.equal(hash(await readFile(join(root,'source',file.path))),file.sha256,file.path);
  return{root,freeze,metadata};
}
// This deliberately imports an unchanged archived v8 selector, NOT the live
// m0.9 selector. No new observedOFF field is invented or inserted anywhere.
export async function admitFrozenEngine(arm){
  const frozen=await verifyFrozen(arm);
  const{selectedManifestsForEngine}=await import(pathToFileURL(join(prep.project,'tests/node-compat/module-selection.mjs')));
  const manifests=selectedManifestsForEngine(frozen.metadata,{sourceRoot:join(frozen.root,'source')});
  assert.equal(manifests[0].profileVersion,'sm-node-22.14.0-m0.11');
  return{...frozen,manifests,engine:join(frozen.root,'engine.wasm'),sourceRoot:join(frozen.root,'source'),archivedSelectorSha256:prep.oldSelector.sha256,
    scope:'Private exact293-input arm admission with unchanged archived-v8 six-optional-module schema; no live guard bypass or fabricated new observed flags'};
}
function query(args,cwd){const result=spawnSync(args[0],args.slice(1),{cwd,encoding:'utf8',maxBuffer:64*1024*1024});assert.equal(result.status,0,result.stderr||result.stdout);return result.stdout;}
function linkedLibraries(){
  // Read the public Ninja command graph as text. Hash archive files mentioned
  // in link commands; do not execute those commands or inspect any Wasm memory.
  const script=`import hashlib,json,pathlib,shlex,subprocess,sys
root=pathlib.Path(sys.argv[1]);text=subprocess.check_output(['ninja','-C',str(root),'-t','commands','starlingmonkey_embedding'],text=True)
paths=set()
for line in text.splitlines():
 for word in shlex.split(line):
  if word.endswith('.a'):
   p=pathlib.Path(word)
   if not p.is_absolute():p=root/p
   if p.is_file():paths.add(p.resolve())
assert len(paths)>=4, 'Expected multiple actual linked static archives'
print(json.dumps([{'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size,'role':'changed-profile-code' if p.name=='libbuiltin_node_compat.a' else 'held-constant-linked-archive'} for p in sorted(paths)]))`;
  return JSON.parse(query(['python3','-c',script,prep.buildDir],prep.project));
}
function sdkInputs(){
  // Include implicit SDK -l/runtime archives as well as explicit link inputs.
  const script=`import hashlib,json,pathlib,sys
root=pathlib.Path(sys.argv[1]);paths=set(p.resolve() for p in root.rglob('*.a') if p.is_file())
for name in ['clang++','wasm-ld','llvm-ar','llvm-ranlib']:
 p=root/'bin'/name
 assert p.is_file(),str(p)
 paths.add(p.resolve())
print(json.dumps([{'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size} for p in sorted(paths)]))`;
  return JSON.parse(query(['python3','-c',script,join(prep.work,'cache/wasi-sdk/85e6')],prep.project));
}
async function freezeBuild(arm,artifact){
  const metadataBytes=await readFile(artifact+'.build.json'),metadata=JSON.parse(metadataBytes);
  assert.deepEqual(metadata.sourceManifest,prep.sourceMapProof[arm]);assert.equal(hash(await readFile(artifact)),metadata.engineSha256);
  assert.deepEqual(metadata.observedCMakeOptions,prep.requestedCMakeOptions);
  const root=join(prep.experiment,'frozen',arm);await mkdir(root,{recursive:true});
  const archivedFiles=[];
  async function archive(source,path){const bytes=await readFile(source);await mkdir(dirname(join(root,path)),{recursive:true});await writeFile(join(root,path),bytes,{flag:'wx'});archivedFiles.push({path,sha256:hash(bytes),bytes:bytes.length});}
  await archive(artifact,'engine.wasm');await archive(artifact+'.build.json','engine.wasm.build.json');
  for(const file of metadata.sourceManifest)await archive(join(prep.project,file.path),'source/'+file.path);
  for(const file of [...prep.inputs,...prep.supportInputs])await archive(join(prep.project,file.path),'source/'+file.path);
  for(const file of ['CMakeCache.txt','compile_commands.json','build.ninja','CMakeFiles/rules.ninja','cxx-wrapper'])await archive(join(prep.buildDir,file),'configuration/'+file);
  for(const file of metadata.componentizeSourceManifest)await archive(join(prep.sourceDir,file.path),'componentize-source/'+file.path);
  const commands=query(['ninja','-C',prep.buildDir,'-t','commands','starlingmonkey_embedding'],prep.project);
  await writeFile(join(root,'configuration/ninja-commands.txt'),commands,{flag:'wx'});archivedFiles.push({path:'configuration/ninja-commands.txt',sha256:hash(commands),bytes:Buffer.byteLength(commands)});
  const libraries=linkedLibraries(),toolchainInputs=sdkInputs();
  assert.equal(libraries.filter(file=>file.role==='changed-profile-code').length,1);
  const receipt={schema:1,arm,atUtc:new Date().toISOString(),engineSha256:metadata.engineSha256,engineBytes:metadata.engineBytes,
    preparationSha256:hash(prepBytes),project:prep.project,sourceDir:prep.sourceDir,buildDir:prep.buildDir,recipeSha256:prep.recipe.sha256,
    libraries,toolchainInputs,archivedFiles,sourceFrozenBeforeCandidateSwitch:arm==='baseline',privateOnly:true};
  await writeFile(join(root,'freeze.json'),JSON.stringify(receipt,null,2)+'\n',{flag:'wx'});await verifyFrozen(arm);return receipt;
}
async function build(arm){
  assert.equal(process.env.NODE_COMPAT_M011_BUILD_APPROVED,'1','Separate root build authorization required; no heavy build is authorized by preparation');
  assert(['baseline','candidate'].includes(arm));
  const statePath=join(prep.experiment,'state.json'),state=JSON.parse(await readFile(statePath));assert.equal(state.preparationSha256,hash(prepBytes));
  const environmentKeys=['PATH','CC','CXX','CFLAGS','CXXFLAGS','CPPFLAGS','LDFLAGS','RUSTFLAGS','CARGO_BUILD_TARGET','RUSTUP_TOOLCHAIN'];
  const environment=Object.fromEntries(environmentKeys.map(key=>[key,process.env[key]??null]));
  if(arm==='candidate')assert.deepEqual(environment,state.environment,'Parent toolchain/flag environment changed between same-path builds');
  if(arm==='baseline'){assert.equal(state.phase,'baseline-prepared');await verifyProject('baseline');}
  else{
    assert.equal(state.phase,'baseline-frozen');const baseline=await admitFrozenEngine('baseline');await verifyProject('baseline');
    assert.equal(baseline.freeze.sourceFrozenBeforeCandidateSwitch,true);
    for(const file of baseline.freeze.libraries)assert.equal(hash(await readFile(file.path)),file.sha256,'Baseline linked library changed before candidate: '+file.path);
    for(const file of baseline.freeze.toolchainInputs)assert.equal(hash(await readFile(file.path)),file.sha256,'SDK input changed before candidate: '+file.path);
    // Only now, after complete baseline engine/source/configuration archive.
    const sourceReceipt=JSON.parse(await readFile(join(previous,'source-receipt.json')));
    for(const path of sourceReceipt.pairChanged)await copyFile(join(previous,'candidate',path),join(prep.project,path));
    await verifyProject('candidate');
  }
  const artifactTag='m011-'+arm,artifactName='starlingmonkey_embedding.abi-i32-i64-v1.entropy-entry-v1-strict-callback-v3.OFF.path-1.events-1.string-decoder-1.assert-1.querystring-1.util-1.'+artifactTag+'.wasm';
  await writeFile(statePath,JSON.stringify({...state,phase:arm+'-building',environment},null,2)+'\n');
  const result=spawnSync('bash',[prep.recipe.path],{cwd:prep.project,env:{...process.env,...prep.buildEnvironment,NODE_COMPAT_ARTIFACT_TAG:artifactTag},stdio:'inherit'});
  assert.equal(result.status,0,'Native build failed; preserve partial state/logs for review');
  await verifyProject(arm);
  const freeze=await freezeBuild(arm,join(prep.work,'artifacts',artifactName));
  if(arm==='candidate'){
    const baseline=await verifyFrozen('baseline'),candidate=await verifyFrozen('candidate');
    assert.deepEqual(freeze.libraries.filter(file=>file.role==='held-constant-linked-archive'),baseline.freeze.libraries.filter(file=>file.role==='held-constant-linked-archive'),'Held-constant linked archives changed across pair');
    assert.deepEqual(freeze.toolchainInputs,baseline.freeze.toolchainInputs,'SDK archives/compiler/archive tools changed across pair');
    for(const key of ['cmakeCacheSha256','compileCommandsSha256','actualEmbeddingCompileCommands','actualRegistrationCompileCommands','archivePins','componentizeSourceManifest'])
      assert.deepEqual(candidate.metadata[key],baseline.metadata[key],key+' differs across pair');
    assert.equal(candidate.metadata.generatedRustProject.manifestSha256,baseline.metadata.generatedRustProject.manifestSha256);
    assert.equal(candidate.metadata.generatedRustProject.lockSha256,baseline.metadata.generatedRustProject.lockSha256);
    await writeFile(join(prep.experiment,'pair-results.json'),JSON.stringify({schema:1,state:'same-path-private-pair-built-source-config-library-matched',
      baselineEngineSha256:baseline.metadata.engineSha256,candidateEngineSha256:candidate.metadata.engineSha256,preparationSha256:hash(prepBytes),
      sameProject:prep.project,sameBuildDirectory:prep.buildDir,onlySourceDifferences:prep.sourceMapProof.difference,libraries:freeze.libraries,toolchainInputs:freeze.toolchainInputs,
      componentGatePassed:false,performanceMeasured:false},null,2)+'\n',{flag:'wx'});
  }
  await writeFile(statePath,JSON.stringify({schema:1,phase:arm+'-frozen',preparationSha256:hash(prepBytes),engineSha256:freeze.engineSha256,environment},null,2)+'\n');
  console.log(JSON.stringify({state:arm+'-built-and-frozen',engineSha256:freeze.engineSha256,sourceAndBuildPathsUnchanged:true,componentTested:false}));
}
if(process.argv[1]===fileURLToPath(import.meta.url)){
  if(process.argv[2]==='--build')await build(process.argv[3]);
  else{await verifyProject('baseline');console.log(JSON.stringify({state:'single-project-baseline-source-and-helper-verified',nativeSources:293,buildExecuted:false,liveSelectorModified:false}));}
}
