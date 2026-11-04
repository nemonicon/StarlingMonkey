// Host-only exact diagnostic gate. Never bundled into the guest.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFile,lstat,realpath} from 'node:fs/promises';
import {dirname,basename,join,resolve,relative,isAbsolute} from 'node:path';
import {fileURLToPath} from 'node:url';
import {consumerPins,producerPins,validateLinkMetadata,validateFrozenVariant,verifyFrozenLinkEvidence} from './link-evidence.mjs';
const here=dirname(fileURLToPath(import.meta.url));
export const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
const pins=producerPins;
const policyBytes=await readFile(join(here,'../integration-candidate-v1/policy.json'));
assert.equal(hash(policyBytes),pins.productionPolicySha256);
const policy=JSON.parse(policyBytes);
function entries(value,count){
 assert(Array.isArray(value)&&value.length===count);
 const seen=new Set();
 for(const row of value){
  assert.deepEqual(Object.keys(row).sort(),['path','sha256']);
  assert.equal(typeof row.path,'string');assert(!row.path.includes('\0')&&!isAbsolute(row.path));
  assert(!row.path.split(/[\\/]/).some(x=>x==='..'||x==='.'||x===''));
  assert.match(row.sha256,/^[0-9a-f]{64}$/);assert(!seen.has(row.path));seen.add(row.path);
 }
 return [...value].sort((a,b)=>a.path.localeCompare(b.path,'en'));
}
function words(command){
 // Producer commands use fixed compiler paths and a source-root path with no
 // whitespace. Fail closed rather than claim a general shell grammar parser.
 assert.equal(typeof command,'string');return command.split(/\s+/);
}
export function validateDiagnosticMetadata(metadata){
 assert.equal(metadata.diagnosticOnly,true,'Private diagnostic engine required; production receipts are rejected');
 assert.equal(metadata.profileEnabled,true);assert.equal(metadata.internalTicksEnabled,true);
 assert.equal(metadata.observedCMakeOptions.CMAKE_BUILD_TYPE,'Release');
 assert.equal(metadata.observedCMakeOptions.NODE_COMPAT_INTERNAL_TICKS,'ON');
 assert.equal(metadata.observedCMakeOptions.NODE_COMPAT_OOM_TESTING,'OFF');assert.equal(metadata.oomTesting,false);
 assert.equal(metadata.debuggerEnabled,false);assert.equal(metadata.entropyPolicy,'off');
 assert.equal(metadata.buildRecipeSha256,pins.diagnosticRecipeSha256);
 validateLinkMetadata(metadata);
 assert.equal(metadata.sourceInputsCapturedBeforeBuild,true);assert.equal(metadata.componentizeSourcesCapturedBeforeBuild,true);
 assert.equal(metadata.buildRecipeCheckedBeforeAndAfterBuild,true);
 const native=entries(metadata.sourceManifest,306),expected=entries(policy.expectedNativeSourceManifest,306);
 assert.deepEqual(native,expected);
 const base=metadata.internalTickPolicy,diag=metadata.internalTickDiagnosticPolicy;
 assert.equal(base.version,pins.sourcePolicyVersion);assert.equal(base.enabled,true);assert.equal(base.sourcePolicyInstalled,true);
 assert.equal(base.policyFileSha256,pins.productionPolicySha256);assert.equal(base.helperSha256,pins.productionHelperSha256);
 assert.deepEqual(base.sourceLayer,policy.sourceLayer);assert.equal(base.embeddingAfterSha256,policy.embedding.afterSha256);
 assert.equal(base.parentRecipeSha256,policy.parentRecipeSha256);assert.equal(base.nativePatchSha256,policy.nativePatchSha256);
 assert.equal(base.embeddingPatchSha256,policy.embedding.patchSha256);assert.deepEqual(base.limits,policy.limits);
 assert.equal(metadata.componentizeSourceManifest.find(x=>x.path==='embedding/embedding.cpp')?.sha256,policy.embedding.afterSha256);
 assert.equal(diag.version,pins.diagnosticVersion);assert.equal(diag.parentProductionRecipeSha256,pins.parentProductionRecipeSha256);
 assert.equal(diag.productionSourceInputs,306);assert.equal(diag.diagnosticSourceInputs,2);assert.equal(diag.totalDeclaredNativeAndBuildInputs,308);
 assert.equal(diag.sourceInputsCheckedBeforeAfter,true);assert.equal(diag.generatedInstallCheckedBeforeAfter,true);
 assert.deepEqual(entries(diag.sourceManifest,2),entries(pins.extraSources,2));
 assert.deepEqual(diag.testModuleIds,pins.testModuleIds);
 const configured=diag.configuredSourceRoot;assert.equal(typeof configured,'string');assert(isAbsolute(configured));
 assert(!/[\s\0]/.test(configured),'Diagnostic command preflight requires a whitespace-free configured source path');
 assert.equal(diag.observedCMake.ENABLE_BUILTIN_DIAGNOSTICS_INTERNAL_TICKS,'ON');
 assert.equal(diag.observedCMake.CMAKE_PROJECT_ComponentizeJS_INCLUDE,join(configured,'tests/node-compat/foundation-scheduler/diagnostic-candidate-v1/diagnostic.cmake'));
 for(const[key,value]of Object.entries(diag.observedCMake))assert.equal(metadata.observedCMakeOptions[key],value);
 const include=diag.generatedBuiltinInclude;assert.equal(hash(Buffer.from(include.contents)),include.sha256);
 assert.equal(include.contents.split(/\r?\n/).filter(x=>x==='NS_DEF(diagnostics::internal_ticks)').length,1);
 assert(Array.isArray(diag.actualCompileCommands)&&diag.actualCompileCommands.length===1);
 assert(diag.actualCompileCommands[0].includes(join(configured,pins.extraSources[0].path)));
 const compile=base.actualLayoutCompileCommands.concat(base.actualEmbeddingCompileCommands,diag.actualCompileCommands);
 assert.equal(base.actualLayoutCompileCommands.length,61);assert.equal(base.actualEmbeddingCompileCommands.length,1);
 for(const feature of ['pathEnabled','eventsEnabled','stringDecoderEnabled','assertEnabled','querystringEnabled','utilEnabled','streamWebEnabled'])assert.equal(metadata[feature],true);
 for(const command of compile){
  const args=words(command);assert(args.includes('-c')&&!args.includes('-fsyntax-only'));
  for(const flag of ['NODE_COMPAT_INTERNAL_TICKS','NODE_COMPAT_STRICT_INITIALIZATION','NODE_COMPAT_ENTROPY_POLICY'])assert(args.includes('-D'+flag+'=1'));
  assert(!args.includes('-DDEBUG'));
  assert.equal(args.includes('-DNODE_COMPAT_EVENTS_ADD_ABORT_LISTENER=1'),metadata.eventsEnabled===true);
 }
 assert.equal(base.actualQueueCompileCommands.length,1);
 assert(base.actualQueueCompileCommands[0].includes(join(configured,'runtime/node_tick_queue.cpp')));
 assert.equal(metadata.gcStress,metadata.observedCMakeOptions.NODE_COMPAT_GC_STRESS==='ON');
 const kernels=base.actualLayoutCompileCommands.filter(c=>c.includes('/builtins/node-compat/buffer.cpp'));
 assert(kernels.length===1);assert.equal(words(kernels[0]).includes('-DNODE_COMPAT_GC_STRESS=1'),metadata.gcStress);
 // Exact finite new policy names; diagnostic receipt never gets projected into
 // the production selector, which must continue to reject this private variant.
 const strict=metadata.strictEventExceptionPolicy,protectedPolicy=metadata.protectedAbortListenerPolicy;
 assert.equal(strict.version,policy.strictPolicyVersion);assert.equal(protectedPolicy.version,policy.protectedPolicyVersion);
 const sourceMap=new Map(expected.map(x=>[x.path,x.sha256]));
 const strictKeys=['builtins/web/event/event-target.cpp','runtime/engine.cpp','runtime/event_loop.cpp','runtime/event_loop.h','runtime/node_tick_queue.cpp','runtime/node_tick_queue.h'];
 assert.deepEqual(strict.nativeSourceSha256,Object.fromEntries(strictKeys.map(p=>[p,sourceMap.get(p)])));
 const protectedKeys=['builtins/web/event/event-target.h','builtins/web/event/event-target.cpp','builtins/node-compat/register.cpp','builtins/node-compat/events.mjs','builtins/node-compat/events-add-abort-listener.mjs','builtins/node-compat/events-factories.generated.h','builtins/node-compat/generate-events-factory.mjs','builtins/node-compat/generate-factories.mjs','builtins/node-compat/export-manifest.events.node-v22.14.0.json','cmake/builtins.cmake'];
 assert.deepEqual(protectedPolicy.sourceSha256,Object.fromEntries(protectedKeys.map(p=>[p,sourceMap.get(p)])));
 assert.equal(strict.parentSourcePolicy.version,policy.parentStrictPolicyVersion);
 assert.equal(protectedPolicy.parentSourcePolicy.version,policy.parentProtectedPolicyVersion);
 assert.equal(strict.patchSha256,'9b2e54c9527a5c078221ad49f67f7354c9fb1df00eb99f0720b3d7874402603a');
 assert.equal(strict.embeddingBoundaryPatchSha256,'84a91c1f74dbdcf653ef7ced5fa2876abffc32d5da591a1ca2df4a4908406ad2');
 assert.equal(protectedPolicy.patchSha256,'0d314f14e1eba2ed5ff1eed592697d5f6fab2be37d9568281ffec43864e2c3a1');
 return {productionNativeSources:306,additionalDiagnosticSources:2,totalDeclaredSourceInputs:308,
         diagnosticCompileCommands:1,layoutCompileCommands:compile.length,gcStress:metadata.gcStress};
}
async function sourceFile(root,path,digest){
 const file=resolve(root,path);assert(!relative(root,file).startsWith('..'));
 let cursor=file;while(cursor!==root){assert(!(await lstat(cursor)).isSymbolicLink());cursor=dirname(cursor);}
 assert((await lstat(file)).isFile());assert.equal(hash(await readFile(file)),digest,path);
}
async function frozenConfiguration(engine,sourceRoot,metadata,metadataBytes){
 const freezeRoot=consumerPins.freezeRoot;
 assert.equal(resolve(dirname(engine)),freezeRoot,'Use the explicit v2 frozen engine, never mutable build paths');
 const match=basename(engine).match(/^(diagnostic-release|diagnostic-gc)\.engine\.wasm$/);assert(match);
 const label=match[1],receiptPath=join(freezeRoot,label+'-freeze-receipt.json');
 validateFrozenVariant(label,metadata);
 const receiptBytes=await readFile(receiptPath),receipt=JSON.parse(receiptBytes);
 assert.equal(receipt.schemaVersion,3);assert.equal(receipt.consumerVersion,consumerPins.version);assert.equal(receipt.label,label);assert.equal(receipt.metadataSha256,hash(metadataBytes));
 assert.equal(receipt.engineSha256,metadata.engineSha256);assert.equal(receipt.recipeSha256,pins.diagnosticRecipeSha256);
 assert.equal(receipt.actualLayoutCompileCommands,61);assert.equal(receipt.actualEmbeddingCompileCommands,1);assert.equal(receipt.actualDiagnosticCompileCommands,1);
 assert.deepEqual(receipt.sourcePartitions,[306,2]);assert.equal(sourceRoot,await realpath(join(freezeRoot,'source')));
 // Never dereference mutable original paths from metadata. Authenticate only
 // regular files copied BELOW the fixed v2 freeze root.
 assert(Array.isArray(receipt.copies));const seen=new Set();
 for(const row of receipt.copies){
  assert.equal(typeof row.path,'string');const file=resolve(row.path),rel=relative(freezeRoot,file);
  assert(rel&&!rel.startsWith('..')&&!isAbsolute(rel));assert(!seen.has(rel));seen.add(rel);
  await sourceFile(freezeRoot,rel,row.sha256);assert.equal((await lstat(file)).size,row.bytes);
 }
 const cacheFile=join(freezeRoot,label+'-CMakeCache.txt'),dbFile=join(freezeRoot,label+'-compile_commands.json');
 const cacheBytes=await readFile(cacheFile),dbBytes=await readFile(dbFile);
 assert.equal(hash(cacheBytes),metadata.cmakeCacheSha256);assert.equal(hash(dbBytes),metadata.compileCommandsSha256);
 const cache=new Map();for(const line of cacheBytes.toString().split(/\r?\n/)){
  const colon=line.indexOf(':'),equals=line.indexOf('=');if(colon>0&&equals>colon)cache.set(line.slice(0,colon),line.slice(equals+1));
 }
 for(const[key,value]of Object.entries(metadata.requestedCMakeOptions))assert.equal(cache.get(key),value,key);
 for(const[key,value]of Object.entries(metadata.observedCMakeOptions))assert.equal(cache.get(key),value,key);
 const configured=metadata.internalTickDiagnosticPolicy.configuredSourceRoot,db=JSON.parse(dbBytes);
 const cpp=new Set(metadata.sourceManifest.filter(x=>x.path.endsWith('.cpp')&&/^(builtins|runtime)\//.test(x.path)).map(x=>resolve(configured,x.path)));
 const layout=db.filter(row=>cpp.has(resolve(row.file))).map(row=>row.command);
 assert.equal(layout.length,61);assert.deepEqual(layout,metadata.internalTickPolicy.actualLayoutCompileCommands);
 assert.deepEqual(layout,metadata.protectedAbortListenerPolicy.actualLayoutCompileCommands);
 const queue=db.filter(row=>resolve(row.file)===resolve(configured,'runtime/node_tick_queue.cpp')).map(row=>row.command);
 assert.equal(queue.length,1);assert.deepEqual(queue,metadata.internalTickPolicy.actualQueueCompileCommands);
 const strictPaths=new Set(['builtins/web/event/event-target.cpp','runtime/engine.cpp','runtime/event_loop.cpp'].map(path=>resolve(configured,path)));
 const strict=db.filter(row=>strictPaths.has(resolve(row.file))).map(row=>row.command).concat(queue);
 assert.equal(strict.length,4);assert.deepEqual(strict,metadata.strictEventExceptionPolicy.actualNativeCompileCommands);
 const diag=metadata.internalTickDiagnosticPolicy,ev=diag.parentTargetCommandEvidence;
 assert.equal(ev.version,pins.parentTargetEvidenceVersion);assert.equal(ev.exactBytesUnchanged,true);assert.deepEqual(receipt.parentTargetCommandEvidence,ev);
 assert.deepEqual(ev.collectionCommand,['ninja','-C',ev.buildDirectory,'-t','commands','builtin_componentize_embedding','builtin_diagnostics_internal_ticks']);
 assert.equal(ev.buildDirectory,dirname(metadata.compileCommandsPath));
 const before=await readFile(join(freezeRoot,label+'-parent-targets.before.commands.txt'));
 const after=await readFile(join(freezeRoot,label+'-parent-targets.after.commands.txt'));
 assert.equal(hash(before),ev.before.sha256);assert.equal(hash(after),ev.after.sha256);assert(before.equals(after));
 assert.equal(before.length,ev.before.bytes);assert.equal(after.length,ev.after.bytes);
 // These two parent TUs are authenticated FROM RAW NINJA, not projected into
 // the directory-local native compile_commands database. Configured paths are
 // whitespace-free; fail closed on quoting in the selected compile lines.
 for(const key of ['embedding','diagnostic']){
  const target=ev.targets[key];assert.equal(target.target,key==='embedding'?'builtin_componentize_embedding':'builtin_diagnostics_internal_ticks');
  const selected=after.toString().split(/\r?\n/).filter(line=>{
   const args=words(line);const index=args.indexOf('-c');return index>=0&&args[index+1]===target.sourcePath;
  });
  assert.equal(selected.length,1);assert(!/['"]/.test(selected[0]),'Quoted selected parent command requires an explicit parser extension');
  assert.deepEqual(selected,target.compileCommands);
  assert.deepEqual(selected,key==='embedding'?metadata.actualEmbeddingCompileCommands:diag.actualCompileCommands);
 }
 assert.deepEqual(metadata.actualEmbeddingCompileCommands,metadata.internalTickPolicy.actualEmbeddingCompileCommands);
 assert.equal(ev.targets.embedding.sourcePath,join(cache.get('CMAKE_HOME_DIRECTORY'),'embedding/embedding.cpp'));
 assert.equal(ev.targets.diagnostic.sourcePath,join(configured,pins.extraSources[0].path));
 const beforeCache=await readFile(join(freezeRoot,label+'-CMakeCache.before.txt'));
 const beforeDb=await readFile(join(freezeRoot,label+'-compile_commands.before.json'));
 assert.equal(ev.configuration.cmakeCache.exactBytesUnchanged,true);assert.equal(ev.configuration.compileCommands.exactBytesUnchanged,true);
 assert(beforeCache.equals(cacheBytes));assert(beforeDb.equals(dbBytes));
 assert.equal(hash(beforeCache),ev.configuration.cmakeCache.before.sha256);assert.equal(hash(cacheBytes),ev.configuration.cmakeCache.after.sha256);
 assert.equal(hash(beforeDb),ev.configuration.compileCommands.before.sha256);assert.equal(hash(dbBytes),ev.configuration.compileCommands.after.sha256);
 assert.equal(beforeCache.length,ev.configuration.cmakeCache.before.bytes);assert.equal(cacheBytes.length,ev.configuration.cmakeCache.after.bytes);
 assert.equal(beforeDb.length,ev.configuration.compileCommands.before.bytes);assert.equal(dbBytes.length,ev.configuration.compileCommands.after.bytes);
 const external=entries(metadata.componentizeSourceManifest,3);
 assert.deepEqual(external.map(x=>x.path).sort(),['CMakeLists.txt','embedding/embedding.cpp','embedding/embedding.h']);
 for(const row of external)await sourceFile(join(freezeRoot,'componentize-source'),row.path,row.sha256);
 const install=await readFile(join(freezeRoot,label+'-builtins.incl'));assert.equal(hash(install),diag.generatedBuiltinInclude.sha256);assert.equal(install.toString(),diag.generatedBuiltinInclude.contents);
 await sourceFile(freezeRoot,'build-diagnostic-engine.sh',pins.diagnosticRecipeSha256);
 assert.equal(hash(await readFile(join(freezeRoot,'diagnostic-pins.json'))),consumerPins.producerPinsSha256);
 await sourceFile(freezeRoot,'consumer-pins.json','d56e14625e6bff5ed586450e3ebf828ae45ac175c2a6658a35ca4c4b638d54d1');
 const link=await verifyFrozenLinkEvidence(metadata,receipt,freezeRoot,label,sourceFile);
 return {label,receiptPath,receiptSha256:hash(receiptBytes),copiesVerified:receipt.copies.length,
  nativeDatabaseCommands:61,queueDatabaseCommands:1,parentNinjaCommands:[1,1],externalEmbeddingInputs:3,
  frozenCacheSha256:hash(cacheBytes),frozenCompileCommandsSha256:hash(dbBytes),parentRawSha256:hash(after),link};
}
export async function diagnosticPreflight(){
 assert.equal(process.version,'v22.14.0');
 assert(process.env.NODE_COMPAT_ENGINE&&process.env.NODE_COMPAT_ENGINE_SOURCE_ROOT);
 const engine=resolve(process.env.NODE_COMPAT_ENGINE),sourceRoot=await realpath(process.env.NODE_COMPAT_ENGINE_SOURCE_ROOT);
 const metadataBytes=await readFile(engine+'.build.json'),metadata=JSON.parse(metadataBytes);
 const checked=validateDiagnosticMetadata(metadata); // Reject old/production before any Wasm instantiation.
 assert.equal(hash(await readFile(engine)),metadata.engineSha256);
 const declared=metadata.sourceManifest.concat(metadata.internalTickDiagnosticPolicy.sourceManifest);
 assert.equal(new Set(declared.map(x=>x.path)).size,308);
 for(const row of declared)await sourceFile(sourceRoot,row.path,row.sha256);
 const frozen=await frozenConfiguration(engine,sourceRoot,metadata,metadataBytes);
 return {frozen,engine,sourceRoot,metadata,pins,checked,metadataSha256:hash(metadataBytes),preflightSha256:hash(await readFile(fileURLToPath(import.meta.url)))};
}
