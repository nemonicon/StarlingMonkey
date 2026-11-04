// Read-only admission. Must complete BEFORE any component/source with native
// prototype negatives is built. Events-OFF and every old engine are refused.
import assert from 'node:assert/strict';
import {readFile,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {resolve,join,dirname,basename} from 'node:path';
import {fileURLToPath} from 'node:url';
import {selectedManifestsForEngine} from '../../module-selection.mjs';
export const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
const here=dirname(fileURLToPath(import.meta.url));
const policyPins=JSON.parse(await readFile(join(here,'../integration-candidate-m0.10/new-policy-pins.json')));
const recipeSha='354cbc8c5317bf14f022fd14a9687e382b99c2141135629b56bb541ef6308754';
export async function preflight({gcStress=false}={}){
 assert.equal(process.version,'v22.14.0');assert(process.env.NODE_COMPAT_ENGINE&&process.env.NODE_COMPAT_ENGINE_SOURCE_ROOT);
 const engine=resolve(process.env.NODE_COMPAT_ENGINE),sourceRoot=resolve(process.env.NODE_COMPAT_ENGINE_SOURCE_ROOT),metadataBytes=await readFile(engine+'.build.json'),metadata=JSON.parse(metadataBytes);
 assert.equal(hash(await readFile(engine)),metadata.engineSha256);assert.equal(metadata.eventsEnabled,true,'NEVER execute guard negatives on Events-OFF');
 assert.equal(metadata.protectedAbortListenerEnabled,true);assert.equal(metadata.protectedAbortListenerPolicy?.enabled,true);
 assert.equal(metadata.strictEventExceptionPolicy?.version,policyPins.policyVersion);
 assert.equal(metadata.protectedAbortListenerPolicy.version,policyPins.extensionVersion);
 assert.equal(metadata.protectedAbortListenerPolicy.patchSha256,policyPins.nativePatchSha256);
 assert.deepEqual(metadata.protectedAbortListenerPolicy.sourceSha256,policyPins.sourceSha256);
 assert.equal(metadata.buildRecipeSha256,recipeSha);assert.equal(metadata.sourceManifest.length,304);
 for(const[key,value]of Object.entries({profileEnabled:true,strictInitialization:true,debuggerEnabled:false,wptSupportEnabled:false,gcStress,oomTesting:false,sourceInputsCapturedBeforeBuild:true,componentizeSourcesCapturedBeforeBuild:true,buildRecipeCheckedBeforeAndAfterBuild:true}))assert.equal(metadata[key],value,key);
 assert(['off','runtime-only'].includes(metadata.entropyPolicy));
 const expected={CMAKE_BUILD_TYPE:'Release',WEVAL:'OFF',USE_WASM_OPT:'ON',ENABLE_BUILTIN_NODE_COMPAT:'ON',ENABLE_JS_DEBUGGER:'OFF',ENABLE_BUILTIN_WPT_SUPPORT:'OFF',NODE_COMPAT_LOCKED_RUST:'ON',NODE_COMPAT_GC_STRESS:gcStress?'ON':'OFF',NODE_COMPAT_OOM_TESTING:'OFF',NODE_COMPAT_ENTROPY_MODE:metadata.entropyPolicy==='off'?'OFF':'RUNTIME_ONLY',NODE_COMPAT_PATH:'ON',NODE_COMPAT_EVENTS:'ON',NODE_COMPAT_STRING_DECODER:'ON',NODE_COMPAT_ASSERT:'ON',NODE_COMPAT_QUERYSTRING:'ON',NODE_COMPAT_UTIL:'ON',NODE_COMPAT_STREAM_WEB:'ON'};
 for(const[key,value]of Object.entries(expected))assert.equal(metadata.observedCMakeOptions[key],value,key);
 for(const item of metadata.sourceManifest){assert(!item.path.startsWith('/')&&!item.path.split('/').includes('..'));assert.equal(hash(await readFile(join(sourceRoot,item.path))),item.sha256,item.path);}
 for(const[path,value]of Object.entries(policyPins.sourceSha256))assert.equal(metadata.sourceManifest.find(item=>item.path===path)?.sha256,value,path);
 const label=basename(engine).replace(/\.engine\.wasm$/,''),configurationRoot=resolve(process.env.NODE_COMPAT_ENGINE_CONFIGURATION_ROOT??dirname(engine));
 const cachePath=join(configurationRoot,label+'-CMakeCache.txt'),commandsPath=join(configurationRoot,label+'-compile_commands.json');
 const cacheBytes=await readFile(cachePath),commandsBytes=await readFile(commandsPath);assert.equal(hash(cacheBytes),metadata.cmakeCacheSha256);assert.equal(hash(commandsBytes),metadata.compileCommandsSha256);
 const commands=JSON.parse(commandsBytes),cppPaths=metadata.sourceManifest.filter(item=>item.path.endsWith('.cpp')&&/^(builtins|runtime)\//.test(item.path)).map(item=>item.path);
 const actual=commands.filter(item=>cppPaths.some(path=>item.file.endsWith('/'+path))).map(item=>item.command);
 assert(actual.length>20);assert.deepEqual(actual,metadata.protectedAbortListenerPolicy.actualLayoutCompileCommands);
 for(const command of actual)assert(command.split(/\s+/).includes('-DNODE_COMPAT_EVENTS_ADD_ABORT_LISTENER=1'));
 for(const suffix of ['/builtins/web/event/event-target.cpp','/builtins/web/abort/abort-signal.cpp','/builtins/web/event/global-event-target.cpp','/builtins/node-compat/register.cpp'])assert(actual.some(command=>command.includes(suffix)),suffix);
 assert(metadata.actualEmbeddingCompileCommands.length);assert.deepEqual(metadata.protectedAbortListenerPolicy.actualEmbeddingCompileCommands,metadata.actualEmbeddingCompileCommands);
 for(const command of metadata.actualEmbeddingCompileCommands){assert(command.split(/\s+/).includes('-DNODE_COMPAT_EVENTS_ADD_ABORT_LISTENER=1'));assert(command.split(/\s+/).includes('-DNODE_COMPAT_STRICT_INITIALIZATION=1'));}
 assert.deepEqual(metadata.protectedAbortListenerPolicy.prerequisiteCMakeOptions,{ENABLE_BUILTIN_WEB_EVENT:'ON',ENABLE_BUILTIN_WEB_ABORT:'ON',ENABLE_BUILTIN_WEB_QUEUE_MICROTASK:'ON'});
 assert.equal(metadata.componentizeSourceManifest.find(item=>item.path==='embedding/embedding.cpp')?.sha256,'9a7c30bad8b9e69257ed5a4c132d46b9c0ddc48924edb3dfe288e9b565766977');
 assert.equal(metadata.generatedRustProject.cargoBuildLocked,true);
 const builtinManifests=selectedManifestsForEngine(metadata,{sourceRoot});assert.equal(builtinManifests.find(item=>item.modules['node:events'])?.profileVersion,'sm-node-22.14.0-m0.10');
 const report={engine,engineSha256:metadata.engineSha256,engineMetadataSha256:hash(metadataBytes),sourceRoot,sourceFilesVerified:304,recipeSha256:recipeSha,
  policyVersion:policyPins.policyVersion,nativePatchSha256:policyPins.nativePatchSha256,entropyPolicy:metadata.entropyPolicy,
  cachePath,cacheSha256:hash(cacheBytes),commandsPath,commandsSha256:hash(commandsBytes),actualLayoutCompileCommands:actual.length,actualEmbeddingCompileCommands:metadata.actualEmbeddingCompileCommands.length,
  gcStress,guardNegativesAllowed:true,scope:'ONLY new exact-source Release Events-ON; no Events-OFF or guard-absent negatives. GC-stress uses existing valid Buffer boundaries only.'};
 return{engine,sourceRoot,metadata,metadataBytes,builtinManifests,report};
}
if(process.argv[1]===fileURLToPath(import.meta.url)){const value=await preflight();if(process.env.NODE_COMPAT_ADD_ABORT_PREFLIGHT)await writeFile(process.env.NODE_COMPAT_ADD_ABORT_PREFLIGHT,JSON.stringify(value.report,null,2)+'\n');console.log(JSON.stringify(value.report,null,2));}
