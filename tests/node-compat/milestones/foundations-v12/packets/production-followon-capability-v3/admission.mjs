// Pure metadata/pin-shape checks only. Acceptance is NEVER artifact/runtime proof.
import assert from 'node:assert/strict';
import {isAbsolute,relative,basename,resolve} from 'node:path';
export const RECIPE='869d188de3843b5d527d236a9e5c9af6ba1193f118dc9ad786df6266e1606173';
export const EMBEDDING='9dcb63beaf55ff6af9ca4d2019316d4a167657c02ed76a1bf246012da0bcd205';
const digest=value=>typeof value==='string'&&/^[0-9a-f]{64}$/.test(value)&&value!=='0'.repeat(64);
const object=value=>value!==null&&typeof value==='object'&&!Array.isArray(value);
const owns=(value,key)=>Object.hasOwn(value,key);
export function validatePinBoundary(root,paths=[]){
  assert.equal(typeof root,'string');assert(!root.includes('\0')&&isAbsolute(root));
  assert.equal(root,resolve(root),'Pin root must be canonical');
  for(const path of paths){assert.equal(typeof path,'string');assert(!path.includes('\0')&&isAbsolute(path));
    assert.equal(path,resolve(path),'Pin child path must be canonical');const rel=relative(root,path);assert(rel&&!rel.startsWith('..')&&!isAbsolute(rel));}
}
export function validateProductionMetadata(metadata,{gcStress,entropyPolicy='off',expectedSources,expectedExternal}={}){
  assert(object(metadata),'Production metadata must be an object');assert.equal(typeof gcStress,'boolean');assert(['off','runtime-only'].includes(entropyPolicy));assert(!(gcStress&&entropyPolicy==='runtime-only'),'No RuntimeOnly GC variant admitted');
  assert(metadata.diagnosticOnly===undefined||metadata.diagnosticOnly===false,'Diagnostic engine rejected');
  assert(!owns(metadata,'internalTickDiagnosticPolicy'),'Diagnostic policy rejected');
  assert(!owns(metadata,'syntheticMetadataOnly')||metadata.syntheticMetadataOnly===false,'Synthetic metadata cannot enter a runtime gate');
  assert.equal(metadata.buildRecipeSha256,RECIPE,'Need current production recipe');
  assert.equal(metadata.internalTicksEnabled,true);assert.equal(metadata.gcStress,gcStress);
  for(const key of ['profileEnabled','pathEnabled','eventsEnabled','stringDecoderEnabled','assertEnabled','querystringEnabled','utilEnabled','streamWebEnabled','strictInitialization','abiFixEnabled','bigIntFixEnabled'])assert.equal(metadata[key],true,key);
  for(const key of ['oomTesting','debuggerEnabled','wptSupportEnabled'])assert.equal(metadata[key],false,key);
  assert.equal(metadata.entropyPolicy,entropyPolicy);assert.equal(metadata.hostApi,'wasi-0.2.10');
  for(const [key,value]of Object.entries({CMAKE_BUILD_TYPE:'Release',WEVAL:'OFF',USE_WASM_OPT:'ON',ENABLE_BUILTIN_NODE_COMPAT:'ON',ENABLE_JS_DEBUGGER:'OFF',ENABLE_BUILTIN_WPT_SUPPORT:'OFF',NODE_COMPAT_LOCKED_RUST:'ON',NODE_COMPAT_OOM_TESTING:'OFF',NODE_COMPAT_ENTROPY_MODE:entropyPolicy==='off'?'OFF':'RUNTIME_ONLY',NODE_COMPAT_INTERNAL_TICKS:'ON',NODE_COMPAT_PATH:'ON',NODE_COMPAT_EVENTS:'ON',NODE_COMPAT_STRING_DECODER:'ON',NODE_COMPAT_ASSERT:'ON',NODE_COMPAT_QUERYSTRING:'ON',NODE_COMPAT_UTIL:'ON',NODE_COMPAT_STREAM_WEB:'ON',NODE_COMPAT_GC_STRESS:gcStress?'ON':'OFF'}))
    for(const options of ['requestedCMakeOptions','observedCMakeOptions'])assert.equal(metadata[options]?.[key],value,options+'.'+key);
  function inventory(value,count){assert(Array.isArray(value)&&value.length===count);const map=new Map();for(const entry of value){
    assert(object(entry)&&Object.keys(entry).sort().join(',')==='path,sha256');
    assert(typeof entry.path==='string'&&!entry.path.includes('\\')&&!entry.path.includes('\0')&&!isAbsolute(entry.path));
    assert(entry.path.split('/').every(x=>x&&x!=='.'&&x!=='..'));assert(digest(entry.sha256));assert(!map.has(entry.path),'Duplicate source path');map.set(entry.path,entry.sha256);
  }return [...map].sort();}
  assert.deepEqual(inventory(metadata.sourceManifest,306),inventory(expectedSources,306));
  assert.deepEqual(inventory(metadata.componentizeSourceManifest,3),inventory(expectedExternal,3));
  assert.equal(metadata.componentizeSourceManifest.find(x=>x.path==='embedding/embedding.cpp')?.sha256,EMBEDDING);
  for(const key of ['sourceInputsCapturedBeforeBuild','componentizeSourcesCapturedBeforeBuild','buildRecipeCheckedBeforeAndAfterBuild'])assert.equal(metadata[key],true,key);
  assert.equal(metadata.generatedRustProject?.cargoBuildLocked,true);
  assert.equal(metadata.generatedRustProject?.manifestAndLockCheckedBeforeAndAfterBuild,true);
  return Object.freeze({state:'pure-production-metadata-shape-checked',sourceFiles:306,gcStress,entropyPolicy,artifactProof:false,runtimeProof:false});
}
export function selectActualPin(document,{gcStress,entropyPolicy='off'}={}){
  assert.equal(typeof gcStress,'boolean');assert(['off','runtime-only'].includes(entropyPolicy));assert(!(gcStress&&entropyPolicy==='runtime-only'),'No RuntimeOnly GC variant admitted');assert(object(document)&&document.schemaVersion===1);
  assert.equal(document.state,'REVIEWED_REAL_PRODUCTION_CAPABILITY_FREEZES_V1','Actual production pins are unconfigured; require a new reviewed revision');
  const label=entropyPolicy==='runtime-only'?'normal-runtime':gcStress?'gc-off':'normal-off',pin=document.variants?.[label];assert(object(pin),'Actual production variant pins are absent');
  assert.equal(pin.state,'reviewed-real-production-freeze');assert.equal(pin.gcStress,gcStress);assert.equal(pin.entropyPolicy,entropyPolicy);assert.equal(pin.sourceFiles,306);
  assert.equal(pin.recipeSha256,RECIPE);assert(Number.isSafeInteger(pin.engineBytes)&&pin.engineBytes>0);
  for(const key of ['engineSha256','receiptSha256','cmakeCacheSha256','compileCommandsSha256','freezeReceiptSha256'])assert(digest(pin[key]),key);
  assert(typeof pin.freezeRoot==='string'&&isAbsolute(pin.freezeRoot)&&basename(pin.freezeRoot)==='native-freeze');
  validatePinBoundary(pin.freezeRoot);
  for(const key of ['enginePath','sourceRoot','componentizeSourceRoot','cachePath','commandsPath','recipePath','freezeReceiptPath']){
    const path=pin[key];assert(typeof path==='string'&&isAbsolute(path)&&!path.includes('\0'));
    const rel=relative(pin.freezeRoot,path);assert(rel&&!rel.startsWith('..')&&!isAbsolute(rel),key+' must be frozen below native-freeze');
    validatePinBoundary(pin.freezeRoot,[path]);
  }
  assert.equal(pin.sourceRoot,pin.freezeRoot+'/source');assert.equal(pin.componentizeSourceRoot,pin.freezeRoot+'/componentize-source');
  assert(Array.isArray(pin.frozenFiles)&&pin.frozenFiles.length>=314);const seen=new Set();
  for(const row of pin.frozenFiles){assert(object(row)&&typeof row.path==='string'&&isAbsolute(row.path)&&digest(row.sha256)&&Number.isSafeInteger(row.bytes)&&row.bytes>=0);
    validatePinBoundary(pin.freezeRoot,[row.path]);
    const rel=relative(pin.freezeRoot,row.path);assert(rel&&!rel.startsWith('..')&&!isAbsolute(rel));assert(!seen.has(row.path),'Duplicate frozen copy');seen.add(row.path);}
  for(const path of [pin.enginePath,pin.enginePath+'.build.json',pin.cachePath,pin.commandsPath,pin.recipePath])assert(seen.has(path),'Missing frozen required file: '+path);
  return Object.freeze({...pin,label});
}
