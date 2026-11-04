// Implemented preparation only. Actual pins.json is deliberately UNCONFIGURED.
// No package/toolchain/guest import occurs before fixed production admission.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFile,lstat,writeFile} from 'node:fs/promises';
import {dirname,join,resolve,relative,isAbsolute} from 'node:path';
import {fileURLToPath} from 'node:url';
import {selectActualPin,validateProductionMetadata,RECIPE} from './admission.mjs';
const here=dirname(fileURLToPath(import.meta.url));
export const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
async function bytes(path,expected){const data=await readFile(path);if(expected)assert.equal(hash(data),expected,path);return data;}
async function below(root,path,expected,size){
  const rel=relative(root,path);assert(rel&&!rel.startsWith('..')&&!isAbsolute(rel));
  let cursor=path;while(cursor!==root){assert(!(await lstat(cursor)).isSymbolicLink(),cursor);cursor=dirname(cursor);}
  assert((await lstat(path)).isFile());const data=await bytes(path,expected);if(size!==undefined)assert.equal(data.length,size);return data;
}
export async function verifyInputClosure(){
  const document=JSON.parse(await readFile(join(here,'input-freeze.json')));assert.equal(document.schemaVersion,1);
  const seen=new Set();for(const row of document.inputs){assert(!seen.has(row.path));seen.add(row.path);
    const path=resolve(here,row.path);assert((await lstat(path)).isFile()&&!(await lstat(path)).isSymbolicLink());
    assert.equal(hash(await readFile(path)),row.sha256,row.path);}
  return{path:join(here,'input-freeze.json'),sha256:hash(await readFile(join(here,'input-freeze.json'))),files:seen.size};
}
export async function verifyProductionTicks({gcStress=false}={}){
  assert.equal(process.version,'v22.14.0');assert.deepEqual(process.execArgv,[]);assert(!process.env.NODE_OPTIONS);
  const pinsPath=join(here,'pins.json'),pinBytes=await readFile(pinsPath);
  const pin=selectActualPin(JSON.parse(pinBytes),{gcStress}); // FIRST gate; null cannot reach a loader.
  const inputClosure=await verifyInputClosure();
  assert((await lstat(pin.freezeRoot)).isDirectory()&&!(await lstat(pin.freezeRoot)).isSymbolicLink());
  assert(process.env.NODE_COMPAT_ENGINE&&process.env.NODE_COMPAT_ENGINE_SOURCE_ROOT&&process.env.NODE_COMPAT_WASMTIME);
  const engine=resolve(process.env.NODE_COMPAT_ENGINE),sourceRoot=resolve(process.env.NODE_COMPAT_ENGINE_SOURCE_ROOT);
  assert.equal(engine,pin.enginePath);assert.equal(sourceRoot,pin.sourceRoot);
  if(process.env.NODE_COMPAT_ENGINE_METADATA)assert.equal(resolve(process.env.NODE_COMPAT_ENGINE_METADATA),engine+'.build.json');
  const metadataBytes=await below(pin.freezeRoot,engine+'.build.json',pin.receiptSha256),metadata=JSON.parse(metadataBytes);
  const policyBytes=await readFile(join(here,'../integration-candidate-v1/policy.json'));
  assert.equal(hash(policyBytes),'98e80d36b8eb9b7ac99de54832288bd8eec148fa1b9fe0b27b3bada4d12b2cd0');
  const policy=JSON.parse(policyBytes);
  const external=[{path:'embedding/embedding.cpp',sha256:policy.embedding.afterSha256},
    {path:'embedding/embedding.h',sha256:'de2c1ae6c7f881902675d79e4bedaeece6953e70e1eac8291165ad0d5cd0eb0e'},
    {path:'CMakeLists.txt',sha256:'4bd9bb94f5b79a2c9eb8ef7d98bc4b712e7b9cc2702467436a87e1845240c5e8'}];
  validateProductionMetadata(metadata,{gcStress,expectedSources:policy.expectedNativeSourceManifest,expectedExternal:external});
  assert.equal(metadata.engineSha256,pin.engineSha256);assert.equal(metadata.engineBytes,pin.engineBytes);
  await below(pin.freezeRoot,engine,pin.engineSha256,pin.engineBytes);
  const copies=new Map();for(const row of pin.frozenFiles){await below(pin.freezeRoot,row.path,row.sha256,row.bytes);copies.set(row.path,row.sha256);}
  for(const row of metadata.sourceManifest){const path=join(sourceRoot,row.path);assert.equal(copies.get(path),row.sha256,'Source absent from frozen copy inventory');await below(pin.freezeRoot,path,row.sha256);}
  for(const row of metadata.componentizeSourceManifest){const path=join(pin.componentizeSourceRoot,row.path);assert.equal(copies.get(path),row.sha256);await below(pin.freezeRoot,path,row.sha256);}
  await below(pin.freezeRoot,pin.recipePath,RECIPE);
  const cacheBytes=await below(pin.freezeRoot,pin.cachePath,pin.cmakeCacheSha256),dbBytes=await below(pin.freezeRoot,pin.commandsPath,pin.compileCommandsSha256);
  assert.equal(hash(cacheBytes),metadata.cmakeCacheSha256);assert.equal(hash(dbBytes),metadata.compileCommandsSha256);
  const cache=new Map();for(const line of cacheBytes.toString().split(/\r?\n/)){const c=line.indexOf(':'),e=line.indexOf('=');if(c>0&&e>c)cache.set(line.slice(0,c),line.slice(e+1));}
  for(const options of [metadata.requestedCMakeOptions,metadata.observedCMakeOptions])for(const[key,value]of Object.entries(options))assert.equal(cache.get(key),value,key);
  const db=JSON.parse(dbBytes),expectedCpp=new Set(metadata.sourceManifest.filter(row=>row.path.endsWith('.cpp')&&/^(runtime|builtins)\//.test(row.path)).map(row=>row.path));
  const layout=db.filter(row=>[...expectedCpp].some(path=>row.file.endsWith('/'+path))).map(row=>row.command);
  assert.equal(layout.length,61);assert.deepEqual(layout,metadata.internalTickPolicy.actualLayoutCompileCommands);
  const queue=db.filter(row=>row.file.endsWith('/runtime/node_tick_queue.cpp')).map(row=>row.command);assert.equal(queue.length,1);assert.deepEqual(queue,metadata.internalTickPolicy.actualQueueCompileCommands);
  const strictPaths=['builtins/web/event/event-target.cpp','runtime/engine.cpp','runtime/event_loop.cpp','runtime/node_tick_queue.cpp'];
  const strict=db.filter(row=>strictPaths.some(path=>row.file.endsWith('/'+path))).map(row=>row.command);
  assert.equal(strict.length,4);assert.deepEqual([...strict].sort(),[...metadata.strictEventExceptionPolicy.actualNativeCompileCommands].sort());
  const embedding=metadata.actualEmbeddingCompileCommands;assert.equal(embedding.length,1);assert(!db.some(row=>row.file.endsWith('/embedding/embedding.cpp')),'Parent target is not a native-JSON row');
  // Exact existing producer collects this parent command with ninja -t commands.
  // This recipe does not provide diagnostic-v2 raw before/after Ninja witnesses.
  for(const command of layout.concat(embedding)){
    assert(!/['";|&<>]/.test(command),'This fixed host harness requires unquoted captured paths');const args=command.trim().split(/\s+/);
    assert(args.includes('-c')&&args.includes('-O3')&&args.includes('-DNDEBUG')&&!args.includes('-fsyntax-only')&&!args.includes('-DDEBUG'));
    for(const macro of ['NODE_COMPAT_INTERNAL_TICKS','NODE_COMPAT_STRICT_INITIALIZATION','NODE_COMPAT_EVENTS_ADD_ABORT_LISTENER','NODE_COMPAT_ENTROPY_POLICY'])assert(args.includes('-D'+macro+'=1'));
  }
  const kernel=db.filter(row=>row.file.endsWith('/builtins/node-compat/buffer.cpp'));assert.equal(kernel.length,1);
  assert.equal(kernel[0].command.split(/\s+/).includes('-DNODE_COMPAT_GC_STRESS=1'),gcStress);
  const freeze=JSON.parse(await below(pin.freezeRoot,pin.freezeReceiptPath,pin.freezeReceiptSha256));
  assert.equal(freeze.schema,1);assert.equal(freeze.state,'immutable-release-engine-frozen');
  for(const[key,value]of Object.entries({engineSha256:pin.engineSha256,receiptSha256:pin.receiptSha256,recipeSha256:RECIPE,nativeInputsVerified:306,externalEmbeddingInputsVerified:3,actualLayoutCompileCommands:61,actualEmbeddingCompileCommands:1}))assert.equal(freeze[key],value,key);
  const hashes=new Set(pin.frozenFiles.map(row=>row.sha256));
  for(const value of [metadata.generatedRustProject.manifestSha256,metadata.generatedRustProject.lockSha256,metadata.openssl.receiptSha256,metadata.openssl.completeSourceAudit.beforeReportSha256])assert(hashes.has(value),'Missing frozen Rust/OpenSSL evidence');
  assert.equal(metadata.openssl.completeSourceAudit.sourceFilesVerified,4650);assert.equal(metadata.openssl.completeSourceAudit.beforeAndAfterBuild,true);
  // Full finite ancestry/patch/layout policy and existing native guard checks.
  // Both are actual existing helpers, imported only after fixed pins/files passed.
  const {selectedManifestsForEngine}=await import('../../module-selection.mjs');
  selectedManifestsForEngine(metadata,{sourceRoot});
  const {nativePreflight}=await import('../../foundation-stream-web/production-candidate/native-preflight.mjs');
  const safety=await nativePreflight({streamWebEnabled:true});assert.equal(safety.metadata.engineSha256,pin.engineSha256);
  const {selectCoreExpectations}=await import('../../core-expectations.mjs');const core=selectCoreExpectations(metadata,{sourceRoot});
  assert.equal(core.coreVersion,'sm-node-22.14.0-m0.11');assert.equal(core.allocUnsafePolicy,'zeroed-no-pool-direct-u8-v1');assert.deepEqual(pin.coreSources,core.sourceHashes);
  const host=resolve(process.env.NODE_COMPAT_WASMTIME);assert.equal(hash(await readFile(host)),'a85dec9fcbbad23d0e038e5a99604114dbe9aa77bc784e4bce0f33013eb33c1c');
  async function recheck(){await verifyInputClosure();await below(pin.freezeRoot,engine,pin.engineSha256,pin.engineBytes);await below(pin.freezeRoot,engine+'.build.json',pin.receiptSha256);
    for(const row of pin.frozenFiles)await below(pin.freezeRoot,row.path,row.sha256,row.bytes);}
  return{engine,sourceRoot,metadata,pin,pinsPath,pinBytes,sourceFilesVerified:306,engineSha256:pin.engineSha256,recheck,
    report:{state:'fixed-production-private-ticks-preflight-passed',engineSha256:pin.engineSha256,commandsPath:pin.commandsPath,sourceFilesVerified:306,recipeSha256:RECIPE,freezeReceiptSha256:pin.freezeReceiptSha256,inputClosure,gcStress,scope:'Read-only admission; no runtime/scheduler/reset/ALS proof'}};
}
export async function requireFreshOutput(variable){assert(process.env[variable],'Explicit fresh output is required: '+variable);const output=resolve(process.env[variable]);
  try{await lstat(output);assert.fail('Choose a nonexistent fresh output: '+output);}catch(error){if(error.code!=='ENOENT')throw error;}return output;}
export async function completeRegression(variable,admission){await admission.recheck();
  const output=resolve(process.env[variable]);await writeFile(join(output,'production-admission-complete.json'),JSON.stringify({...admission.report,consumedInputsRecheckedAfterRun:true},null,2)+'\n',{flag:'wx'});}
