import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFile,writeFile} from 'node:fs/promises';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
const here=dirname(fileURLToPath(import.meta.url)),hash=data=>createHash('sha256').update(data).digest('hex');
export async function auditBuild({sidecar,variant,source,extensionPath}){
  const pins=JSON.parse(await readFile(join(here,'pins.json'))),freeze=process.env.NODE_COMPAT_UTF8_FREEZE??'/tmp/starling-node-compat/foundations-v3/native-freeze';
  const base=JSON.parse(await readFile(join(freeze,'off-path.engine.wasm.build.json'))),metadata=JSON.parse(await readFile(sidecar));
  const codec='builtins/web/text-codec/text-encoder.cpp',header='builtins/web/text-codec/text-encoder-direct-testing.h',testing=variant==='gc'||variant==='oom';
  assert.equal(hash(await readFile(metadata.enginePath)),metadata.engineSha256);
  for(const entry of metadata.sourceManifest)assert.equal(hash(await readFile(join(source,entry.path))),entry.sha256,entry.path);
  for(const entry of base.sourceManifest)if(entry.path!==codec)assert.equal(metadata.sourceManifest.find(current=>current.path===entry.path)?.sha256,entry.sha256,entry.path);
  assert.equal(metadata.sourceManifest.length,base.sourceManifest.length+1);
  assert.equal(metadata.sourceManifest.find(entry=>entry.path===codec).sha256,variant==='control'?pins.baseTextEncoderSha256:pins.patchedTextEncoderSha256);
  assert.equal(metadata.sourceManifest.find(entry=>entry.path===header).sha256,pins.testingHeaderSha256);
  assert.deepEqual(metadata.componentizeSourceManifest,base.componentizeSourceManifest);
  const build=dirname(metadata.cmakeCachePath),actual=spawnSync('ninja',['-C',build,'-t','commands','builtin_web_text_codec'],{encoding:'utf8',maxBuffer:8*1024*1024});assert.equal(actual.status,0);
  const compile=actual.stdout.split('\n').find(line=>line.includes(' -c ')&&line.endsWith('/text-encoder.cpp'));assert(compile);
  assert.equal(compile.includes('-DSTARLING_UTF8_DIRECT_GC_STRESS=1'),testing);assert.equal(compile.includes('-DSTARLING_UTF8_DIRECT_OOM_TESTING=1'),variant==='oom');
  const cache=await readFile(metadata.cmakeCachePath,'utf8'),flagLine=cache.split('\n').find(line=>line.startsWith('CMAKE_CXX_FLAGS:STRING='));assert(flagLine);assert.equal(flagLine.slice(flagLine.indexOf('=')+1),'');
  const privateRecipe=join(source,'tests/node-compat/build-engine.sh');assert.equal(hash(await readFile(privateRecipe)),metadata.buildRecipeSha256);
  metadata.utf8DirectExperiment={schemaVersion:1,variant,sourceRoot:source,baseEngineSha256:base.engineSha256,baseSourceManifestSha256:hash(JSON.stringify(base.sourceManifest)),sameNativeAndEmbeddingSourcesExcept:[codec,header],patchSha256:pins.patchSha256,testingHeaderSha256:pins.testingHeaderSha256,recipeSha256:metadata.buildRecipeSha256,baselineRecipeSha256:pins.baseRecipeSha256,...(extensionPath?{privateCMakeExtension:{path:extensionPath,sha256:hash(await readFile(extensionPath))}}:{}),actualTextEncoderCompileCommand:compile,actualCMakeCxxFlags:'',webCodecGCStress:testing,webCodecOOMTesting:variant==='oom',faultScopeLifecycle:'Fixture-bounded EngineState::Initialized guard; not a universal deployed-entry barrier. No late encode getters permitted in the dedicated fault fixture.',scope:'PRIVATE existing TextEncoder encode implementation experiment; Buffer facade/kernel, production checkout and host runtimes unchanged'};
  await writeFile(sidecar,JSON.stringify(metadata,null,2)+'\n');return metadata;
}
if(process.argv[1]&&resolve(process.argv[1])===fileURLToPath(import.meta.url)){
  const[sidecar,variant,source,extensionPath]=process.argv.slice(2);assert(sidecar&&variant&&source);
  const metadata=await auditBuild({sidecar,variant,source,extensionPath});console.log(JSON.stringify({engine:metadata.enginePath,engineSha256:metadata.engineSha256,variant,sourceRoot:source},null,2));
}
