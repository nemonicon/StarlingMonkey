// Read-only receipt/source admission for the separately built production v8
// OFF engine. This module does not load a componentizer or execute a component.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFile,writeFile} from 'node:fs/promises';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const here=dirname(fileURLToPath(import.meta.url)),hash=x=>createHash('sha256').update(x).digest('hex');
export const PRODUCTION_V8_PINS=Object.freeze({
 engineSha256:'e16c19fc567753517d7b61b65372dd7dc86de8f839e7acab959b5cf5eaf294c9',
 receiptSha256:'857dde83661919ac0c494b17be1cfd7bb2d5b4724067b6cffb433b7c252d9dad',
 coreManifestSha256:'0e482334c46240f1cc4a20e97530a2339e14339f29dc14c27e025f1e6d218439',
 nativePatchSha256:'9b2e54c9527a5c078221ad49f67f7354c9fb1df00eb99f0720b3d7874402603a',
 boundaryPatchSha256:'84a91c1f74dbdcf653ef7ced5fa2876abffc32d5da591a1ca2df4a4908406ad2',
 embeddingSourceSha256:'9a7c30bad8b9e69257ed5a4c132d46b9c0ddc48924edb3dfe288e9b565766977',
 recipeSha256:'af5b0e8cd34aae6923dacf32bfaf80f8c05c8f12edf014a3ae3c77d58ed2226f',
 nativeSourceSha256:Object.freeze({
  'builtins/web/event/event-target.cpp':'431267539ab361832094fd212af3b3605241ea0f2ad196b132c6df78e33896d5',
  'runtime/engine.cpp':'2e85b4305f64757c172a3ee1723cfafe4666708fa192cafd2535563a200074bb',
  'runtime/event_loop.cpp':'7eabda627c0627281fda4cede3ca79d71d9a262d170f34ca835ee2f877924cf8',
  'runtime/event_loop.h':'e61fff76b41a5709099b94e0735b87bcf302df5b6521e348a77b662be0fad9d9',
 }),
});
export async function verifyProductionV8(){
 assert.equal(process.version,'v22.14.0');assert(process.env.NODE_COMPAT_ENGINE&&process.env.NODE_COMPAT_ENGINE_SOURCE_ROOT);
 const engine=resolve(process.env.NODE_COMPAT_ENGINE),sourceRoot=resolve(process.env.NODE_COMPAT_ENGINE_SOURCE_ROOT),receiptBytes=await readFile(engine+'.build.json'),metadata=JSON.parse(receiptBytes),pins=PRODUCTION_V8_PINS;
 assert.equal(hash(await readFile(engine)),pins.engineSha256);assert.equal(metadata.engineSha256,pins.engineSha256);assert.equal(hash(receiptBytes),pins.receiptSha256);assert.equal(metadata.engineBytes,9724864);
 assert.equal(metadata.entropyPolicy,'off');assert.equal(metadata.profileEnabled,true);assert.equal(metadata.strictInitialization,true);assert.equal(metadata.debuggerEnabled,false);assert.equal(metadata.wptSupportEnabled,false);assert.equal(metadata.gcStress,false);assert.equal(metadata.oomTesting,false);assert.equal(metadata.abiFixEnabled,true);assert.equal(metadata.bigIntFixEnabled,true);assert.equal(metadata.hostApi,'wasi-0.2.10');
 const requested={CMAKE_BUILD_TYPE:'Release',WEVAL:'OFF',USE_WASM_OPT:'ON',ENABLE_BUILTIN_NODE_COMPAT:'ON',ENABLE_JS_DEBUGGER:'OFF',ENABLE_BUILTIN_WPT_SUPPORT:'OFF',NODE_COMPAT_LOCKED_RUST:'ON',NODE_COMPAT_ENTROPY_MODE:'OFF',NODE_COMPAT_GC_STRESS:'OFF',NODE_COMPAT_OOM_TESTING:'OFF',NODE_COMPAT_PATH:'ON',NODE_COMPAT_EVENTS:'ON',NODE_COMPAT_STRING_DECODER:'ON',NODE_COMPAT_ASSERT:'ON',NODE_COMPAT_QUERYSTRING:'ON',NODE_COMPAT_UTIL:'ON'};
 for(const[key,value]of Object.entries(requested))assert.equal(metadata.observedCMakeOptions[key],value,key);
 assert.equal(metadata.sourceInputsCapturedBeforeBuild,true);assert.equal(metadata.componentizeSourcesCapturedBeforeBuild,true);assert.equal(metadata.buildRecipeCheckedBeforeAndAfterBuild,true);assert.equal(metadata.buildRecipeSha256,pins.recipeSha256);assert.equal(metadata.generatedRustProject.cargoBuildLocked,true);
 assert.equal(metadata.sourceManifest.length,293);for(const item of metadata.sourceManifest){assert(!item.path.startsWith('/')&&!item.path.split('/').includes('..'));assert.equal(hash(await readFile(join(sourceRoot,item.path))),item.sha256,item.path);}
 const core=metadata.selectedModuleManifests.find(x=>x.path==='builtins/node-compat/export-manifest.node-v22.14.0.json');assert(core);assert.equal(core.profileVersion,'sm-node-22.14.0-m0.8');assert.equal(core.sha256,pins.coreManifestSha256);assert.equal(hash(await readFile(join(sourceRoot,core.path))),core.sha256);
 const policy=metadata.strictEventExceptionPolicy;assert.equal(policy.version,'sm-uncaught-event-v3');assert.equal(policy.patchSha256,pins.nativePatchSha256);assert.equal(policy.embeddingBoundaryPatchSha256,pins.boundaryPatchSha256);assert.equal(policy.deployedUnhandledRejections,'fatal-after-drained-jobs-before-result-marshalling');assert.deepEqual(policy.nativeSourceSha256,pins.nativeSourceSha256);
 for(const[path,expected]of Object.entries(pins.nativeSourceSha256))assert.equal(metadata.sourceManifest.find(x=>x.path===path)?.sha256,expected,path);
 assert.equal(hash(await readFile(join(here,'strict-event-v3.patch'))),pins.nativePatchSha256);assert.equal(hash(await readFile(join(here,'componentize-strict-event-boundary-v2.patch'))),pins.boundaryPatchSha256);
 assert.equal(metadata.componentizeSourceManifest.find(x=>x.path==='embedding/embedding.cpp')?.sha256,pins.embeddingSourceSha256);
 assert.equal(policy.actualNativeCompileCommands.length,3);for(const path of Object.keys(pins.nativeSourceSha256).filter(x=>x.endsWith('.cpp'))){const commands=policy.actualNativeCompileCommands.filter(x=>x.endsWith('/'+path));assert.equal(commands.length,1,path);assert(commands[0].split(/\s+/).includes('-DNODE_COMPAT_STRICT_INITIALIZATION=1'));}
 assert(metadata.actualEmbeddingCompileCommands.length>0);assert(metadata.actualEmbeddingCompileCommands.every(x=>x.split(/\s+/).includes('-DNODE_COMPAT_STRICT_INITIALIZATION=1')));
 // Verify immutable copies rather than a later configured build directory.
 const frozenDirectory=dirname(engine),cache=await readFile(join(frozenDirectory,'off-CMakeCache.txt')),commands=await readFile(join(frozenDirectory,'off-compile_commands.json'));
 assert.equal(hash(cache),metadata.cmakeCacheSha256);assert.equal(hash(commands),metadata.compileCommandsSha256);
 return {schemaVersion:1,state:'production-v8-off-receipt-and-source-preflight-passed',checkedAtUtc:new Date().toISOString(),engine,engineSha256:pins.engineSha256,receiptSha256:pins.receiptSha256,sourceRoot,sourceFilesVerified:293,coreProfile:core.profileVersion,coreManifestSha256:core.sha256,nativePatchSha256:pins.nativePatchSha256,boundaryPatchSha256:pins.boundaryPatchSha256,embeddingSourceSha256:pins.embeddingSourceSha256,recipeSha256:pins.recipeSha256,nativeStrictTranslationUnits:3,embeddingStrictTranslationUnits:metadata.actualEmbeddingCompileCommands.length,frozenConfigurationDigestsVerified:true,scope:'Read-only engine/receipt/source admission; this function executes no component and claims no new runtime result.'};
}
if(process.argv[1]&&import.meta.url===pathToFileURL(resolve(process.argv[1])).href){const report=await verifyProductionV8();await writeFile(join(here,'production-v8-preflight-results.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));}
