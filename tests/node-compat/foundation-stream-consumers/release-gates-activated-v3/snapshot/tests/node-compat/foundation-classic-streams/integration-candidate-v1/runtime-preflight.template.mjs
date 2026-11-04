// Source-only future gate. Fixed reviewed artifact pins must precede all loaders.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFile,lstat} from 'node:fs/promises';
import {dirname,join,resolve,relative,isAbsolute} from 'node:path';
import {fileURLToPath} from 'node:url';
import {selectClassicPin} from './runtime-contract.mjs';
const HERE=dirname(fileURLToPath(import.meta.url));
const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
const PINS_SHA='@PINS_SHA@',INPUTS_SHA='@INPUTS_SHA@',RECIPE_SHA='@RECIPE_SHA@';
const SELECTOR_SHA='@SELECTOR_SHA@',ADMISSION_SHA='@ADMISSION_SHA@';
async function regular(path,sha,bytes){const stat=await lstat(path);assert(stat.isFile()&&!stat.isSymbolicLink(),path);const data=await readFile(path);assert.equal(hash(data),sha,path);if(bytes!==undefined)assert.equal(data.length,bytes);return data;}
async function below(root,path,sha,bytes){assert.equal(resolve(root),root);assert.equal(resolve(path),path);const rel=relative(root,path);assert(rel&&!rel.startsWith('..')&&!isAbsolute(rel));
 let cursor=path;while(cursor!==root){assert(!(await lstat(cursor)).isSymbolicLink());const parent=dirname(cursor);assert.notEqual(parent,cursor);cursor=parent;}return regular(path,sha,bytes);}
export async function classicPreflight({variant='normal-off'}={}){
 const pinsPath=join(HERE,'runtime-pins.json'),pinsBytes=await regular(pinsPath,PINS_SHA);
 const pin=selectClassicPin(JSON.parse(pinsBytes),{variant,recipeSha256:RECIPE_SHA}); // Null pins stop here, before source/engine/loader reads.
 assert.equal(process.version,'v22.14.0');assert.deepEqual(process.execArgv,[]);assert(!process.env.NODE_OPTIONS);
 async function seal(){const document=JSON.parse(await regular(join(HERE,'input-freeze.json'),INPUTS_SHA));assert.equal(document.schemaVersion,1);const seen=new Set();
  for(const row of document.inputs){assert(typeof row.path==='string'&&!row.path.includes('\0')&&!seen.has(row.path));seen.add(row.path);await regular(resolve(HERE,row.path),row.sha256,row.bytes);}return document.inputs.length;}
 await seal();
 assert((await lstat(pin.freezeRoot)).isDirectory()&&!(await lstat(pin.freezeRoot)).isSymbolicLink());
 if(process.env.NODE_COMPAT_ENGINE)assert.equal(resolve(process.env.NODE_COMPAT_ENGINE),pin.enginePath);
 if(process.env.NODE_COMPAT_ENGINE_SOURCE_ROOT)assert.equal(resolve(process.env.NODE_COMPAT_ENGINE_SOURCE_ROOT),pin.sourceRoot);
 if(process.env.NODE_COMPAT_ENGINE_METADATA)assert.equal(resolve(process.env.NODE_COMPAT_ENGINE_METADATA),pin.enginePath+'.build.json');
 const metadata=JSON.parse(await below(pin.freezeRoot,pin.enginePath+'.build.json',pin.receiptSha256));
 assert.equal(metadata.syntheticMetadataOnly,undefined,'Synthetic models never authorize engine use');
 assert.equal(metadata.engineSha256,pin.engineSha256);assert.equal(metadata.engineBytes,pin.engineBytes);assert.equal(metadata.buildRecipeSha256,RECIPE_SHA);
 for(const[field,value]of Object.entries({profileEnabled:true,strictInitialization:true,oomTesting:false,debuggerEnabled:false,wptSupportEnabled:false,
  pathEnabled:true,eventsEnabled:true,stringDecoderEnabled:true,assertEnabled:true,querystringEnabled:true,utilEnabled:true,streamWebEnabled:true,internalTicksEnabled:true,
  classicStreamsEnabled:variant!=='disabled-off',gcStress:variant==='gc-off',entropyPolicy:variant==='normal-runtime'?'runtime-only':'off'}))assert.equal(metadata[field],value,field);
 const checks=pin.frozenFiles.map(row=>({...row})),copies=new Map();
 for(const row of checks){await below(pin.freezeRoot,row.path,row.sha256,row.bytes);copies.set(row.path,row.sha256);}
 for(const[name,sha]of [[pin.enginePath,pin.engineSha256],[pin.enginePath+'.build.json',pin.receiptSha256],[pin.recipePath,RECIPE_SHA],[pin.cachePath,pin.cmakeCacheSha256],[pin.commandsPath,pin.compileCommandsSha256]])assert.equal(copies.get(name),sha);
 assert.equal(metadata.cmakeCacheSha256,pin.cmakeCacheSha256);assert.equal(metadata.compileCommandsSha256,pin.compileCommandsSha256);
 for(const row of metadata.sourceManifest??[]){assert.equal(copies.get(join(pin.sourceRoot,row.path)),row.sha256);}
 for(const row of metadata.componentizeSourceManifest??[]){assert.equal(copies.get(join(pin.componentizeSourceRoot,row.path)),row.sha256);}
 assert.equal(metadata.sourceManifest.length,342);assert.equal(metadata.componentizeSourceManifest.length,3);
 const cache=new Map();for(const line of(await below(pin.freezeRoot,pin.cachePath,pin.cmakeCacheSha256)).toString().split(/\r?\n/)){const c=line.indexOf(':'),e=line.indexOf('=');if(c>0&&e>c)cache.set(line.slice(0,c),line.slice(e+1));}
 for(const map of [metadata.requestedCMakeOptions,metadata.observedCMakeOptions])for(const[key,value]of Object.entries(map))assert.equal(cache.get(key),value,key);
 const db=JSON.parse(await below(pin.freezeRoot,pin.commandsPath,pin.compileCommandsSha256));
 const cpp=metadata.sourceManifest.filter(row=>row.path.endsWith('.cpp')&&/^(builtins|runtime)\//.test(row.path)).map(row=>row.path);
 const native=db.filter(row=>cpp.some(path=>row.file.endsWith('/'+path))).map(row=>row.command);assert.equal(native.length,61);assert.deepEqual(native,metadata.internalTickPolicy.actualLayoutCompileCommands);
 const parentText=(await below(pin.freezeRoot,pin.parentEmbeddingCommandPath,pin.parentEmbeddingCommandSha256)).toString();
 const parent=parentText.split(/\r?\n/).filter(line=>/\s-c\s+\S*\/embedding\/embedding\.cpp(?:\s|$)/.test(line));
 assert.equal(parent.length,1);assert.deepEqual(parent,metadata.actualEmbeddingCompileCommands);assert(!db.some(row=>row.file.endsWith('/embedding/embedding.cpp')));
 const freeze=JSON.parse(await below(pin.freezeRoot,pin.freezeReceiptPath,pin.freezeReceiptSha256));
 assert.equal(freeze.schema,1);assert.equal(freeze.state,'immutable-release-engine-frozen');
 for(const[key,value]of Object.entries({engineSha256:pin.engineSha256,receiptSha256:pin.receiptSha256,recipeSha256:RECIPE_SHA,nativeInputsVerified:342,externalEmbeddingInputsVerified:3,actualLayoutCompileCommands:61,actualEmbeddingCompileCommands:1}))assert.equal(freeze[key],value,key);
 // Only real future installed code may pass this call. No 306-to342 projection.
 const liveSelector=resolve(HERE,'../../module-selection.mjs'),liveAdmission=resolve(HERE,'../../classic-streams-admission.mjs');
 await regular(liveSelector,SELECTOR_SHA);await regular(liveAdmission,ADMISSION_SHA);
 const {selectedManifestsForEngine}=await import('../../module-selection.mjs');const selected=selectedManifestsForEngine(metadata,{sourceRoot:pin.sourceRoot});
 const manifests=selected.flatMap(value=>Object.keys(value.modules));assert.equal(manifests.includes('node:stream'),variant!=='disabled-off');assert.equal(manifests.includes('node:stream/promises'),variant!=='disabled-off');
 const {selectCoreExpectations}=await import('../../core-expectations.mjs');const core=selectCoreExpectations(metadata,{sourceRoot:pin.sourceRoot});assert.equal(core.coreVersion,'sm-node-22.14.0-m0.11');
 const evidence=new Set(checks.map(row=>row.sha256));for(const value of [metadata.generatedRustProject.manifestSha256,metadata.generatedRustProject.lockSha256,metadata.openssl.receiptSha256,metadata.openssl.completeSourceAudit.beforeReportSha256])assert(evidence.has(value));
 assert.equal(metadata.openssl.completeSourceAudit.sourceFilesVerified,4650);assert.equal(metadata.openssl.completeSourceAudit.beforeAndAfterBuild,true);
 const frozenPin=structuredClone(pin),privateRoot=pin.freezeRoot,privateFreezePath=pin.freezeReceiptPath,privateFreezeSha=pin.freezeReceiptSha256;
 async function recheck(){await regular(pinsPath,PINS_SHA);await seal();await regular(liveSelector,SELECTOR_SHA);await regular(liveAdmission,ADMISSION_SHA);await below(privateRoot,privateFreezePath,privateFreezeSha);
  for(const row of checks)await below(privateRoot,row.path,row.sha256,row.bytes);}
 await recheck();return Object.freeze({enginePath:pin.enginePath,sourceRoot:pin.sourceRoot,metadata,pin:frozenPin,variant,recheck});
}
