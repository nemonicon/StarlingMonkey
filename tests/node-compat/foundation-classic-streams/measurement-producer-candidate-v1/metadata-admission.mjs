// Raw diagnostic metadata admission/rejection proof only. No engine/tool loaders.
import assert from 'node:assert/strict';
import {readFile,lstat} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const here=dirname(fileURLToPath(import.meta.url));
export const contract=JSON.parse(await readFile(join(here,'contract.json')));
const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
export function classify(metadata,label){
 assert(contract.labels.includes(label));assert(metadata&&typeof metadata==='object'&&!Array.isArray(metadata));
 assert.equal(metadata.diagnosticOnly,true,'Need distinct benchmark diagnostic metadata');
 assert.equal(metadata.syntheticMetadataOnly??false,false);
 assert.equal(metadata.buildRecipeSha256,contract.recipeSha256);
 assert.equal(metadata.classicStreamsEnabled,label==='benchmark-classic-on');
 for(const key of ['profileEnabled','pathEnabled','eventsEnabled','stringDecoderEnabled','assertEnabled','querystringEnabled','utilEnabled','streamWebEnabled','internalTicksEnabled','strictInitialization','abiFixEnabled','bigIntFixEnabled'])assert.equal(metadata[key],true,key);
 for(const key of ['gcStress','oomTesting','debuggerEnabled','wptSupportEnabled'])assert.equal(metadata[key],false,key);
 assert.equal(metadata.entropyPolicy,'off');assert(!Object.hasOwn(metadata,'internalTickDiagnosticPolicy'));
 const policy=metadata.classicBenchmarkDiagnosticPolicy;
 assert.equal(policy.version,contract.diagnosticVersion);assert.equal(policy.moduleId,contract.moduleId);
 assert.deepEqual(policy.exports,contract.exports);assert.deepEqual(policy.addonSources,contract.addonSources);
 assert.equal(policy.nativeInputs,342);assert.equal(policy.addonInputs,2);assert.equal(policy.totalDeclaredNativeAndBuildInputs,344);assert.equal(policy.externalEmbeddingInputs,3);
 return {classicStreamsEnabled:metadata.classicStreamsEnabled,label};
}
export async function proveProductionRefusal(metadata,label,sourceRoot){
 const result=classify(metadata,label);sourceRoot=resolve(sourceRoot);
 const tools=JSON.parse(await readFile(join(here,'ancestry/tool-pins.json')));
 for(const row of tools.toolDependencies){const path=join(sourceRoot,row.path);assert((await lstat(path)).isFile()&&!(await lstat(path)).isSymbolicLink());assert.equal(hash(await readFile(path)),row.sha256);}
 const {selectedManifestsForEngine}=await import(pathToFileURL(join(sourceRoot,'tests/node-compat/module-selection.mjs')));
 assert.throws(()=>selectedManifestsForEngine(metadata,{sourceRoot}),/Diagnostic engines are never classic production/);
 return{schemaVersion:1,state:'RAW_BENCHMARK_METADATA_CLASSIFIED_PRODUCTION_SELECTOR_REFUSED',...result,
  productionSelectorRefused:true,metadataProjected:false,engineBytesRead:false,guestExecuted:false};
}
export async function rawBuiltinManifests(metadata,label,sourceRoot){
 const choice=classify(metadata,label);sourceRoot=resolve(sourceRoot);
 const names=['export-manifest.node-v22.14.0.json','export-manifest.path.node-v22.14.0.json','export-manifest.events.node-v22.14.0.json',
  'export-manifest.string-decoder.node-v22.14.0.json','export-manifest.assert.node-v22.14.0.json','export-manifest.querystring.node-v22.14.0.json',
  'export-manifest.util.node-v22.14.0.json','export-manifest.stream-web.node-v22.14.0.json',
  ...(choice.classicStreamsEnabled?['classic-streams/export-manifest.classic-streams.node-v22.14.0.json']:[])];
 const expected=names.map(name=>'builtins/node-compat/'+name),rows=metadata.selectedModuleManifests;
 assert.deepEqual(rows.map(row=>row.path),expected);assert.equal(new Set(rows.map(row=>row.path)).size,rows.length);
 assert.equal(metadata.sourceManifest.length,342);assert.equal(new Set(metadata.sourceManifest.map(row=>row.path)).size,342);
 const sources=new Map(metadata.sourceManifest.map(row=>[row.path,row.sha256]));
 const schemaPath='builtins/node-compat/manifest.schema.json',schemaBytes=await readFile(join(sourceRoot,schemaPath));assert.equal(hash(schemaBytes),sources.get(schemaPath));
 const validatorPath=resolve(here,'../../../../builtins/node-compat/validate-manifest.mjs');
 const tools=JSON.parse(await readFile(join(here,'ancestry/tool-pins.json'))),validator=tools.toolDependencies.find(row=>row.path==='builtins/node-compat/validate-manifest.mjs');
 assert(validator);assert.equal(hash(await readFile(validatorPath)),validator.sha256);
 const {validateManifest}=await import(pathToFileURL(validatorPath));
 const result=[];
 for(const row of rows){assert.equal(row.sha256,sources.get(row.path));const path=join(sourceRoot,row.path);assert((await lstat(path)).isFile()&&!(await lstat(path)).isSymbolicLink());
  const bytes=await readFile(path);assert.equal(hash(bytes),row.sha256);const manifest=validateManifest(JSON.parse(bytes),JSON.parse(schemaBytes));
  assert.equal(manifest.profileVersion,row.profileVersion);result.push(manifest);}
 return result;
}
if(process.argv[1]===fileURLToPath(import.meta.url)){
 assert.equal(process.version,'v22.14.0');assert.equal(process.argv.length,5);
 console.log(JSON.stringify(await proveProductionRefusal(JSON.parse(await readFile(process.argv[2])),process.argv[3],process.argv[4])));
}
