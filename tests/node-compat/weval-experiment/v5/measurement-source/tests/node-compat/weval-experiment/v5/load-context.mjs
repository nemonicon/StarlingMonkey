import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFile} from 'node:fs/promises';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {loadToolchain} from '../../toolchain.mjs';
import {loadComponentizer} from '../../componentizer.mjs';
import {selectedManifestsForEngine} from '../../module-selection.mjs';

const here=dirname(fileURLToPath(import.meta.url)),hash=bytes=>createHash('sha256').update(bytes).digest('hex');
export async function loadWevalContext(){
  assert.equal(process.version,'v22.14.0');assert(process.env.NODE_COMPAT_ENGINE,'Explicit Weval engine required');
  const engine=resolve(process.env.NODE_COMPAT_ENGINE),metadataBytes=await readFile(engine+'.build.json'),metadata=JSON.parse(metadataBytes);
  const receipt=JSON.parse(await readFile(join(here,'build-receipt.json'))),pins=JSON.parse(await readFile(join(here,'pins.json')));
  assert.equal(hash(await readFile(engine)),receipt.engine.sha256);assert.equal(metadata.engineSha256,receipt.engine.sha256);
  assert.equal(hash(metadataBytes),receipt.files.find(entry=>entry.path.endsWith('/engine.build.json')).sha256);
  assert.equal(metadata.wevalExperiment.baseline,'foundations-v5');assert.equal(metadata.strictInitialization,true);
  for(const[field,value]of Object.entries(pins.buildOptions))assert.equal(metadata.observedCMakeOptions[field],value,field);
  for(const field of ['gcStress','oomTesting','debuggerEnabled','wptSupportEnabled'])assert.equal(metadata[field],false);
  const sourceRoot=metadata.wevalExperiment.sourceRoot,cache=metadata.wevalExperiment.cache;
  assert.equal(cache.generatedFromRawEngineSha256,metadata.engineSha256);assert.equal(cache.sha256,receipt.cache.sha256);
  const tools=metadata.wevalExperiment.tools;
  for(const entry of tools)assert.equal(entry.sha256,pins.cachedHostTools[entry.name].sha256,entry.name);
  const preview2Adapter=join(sourceRoot,'host-apis/wasi-0.2.0/preview1-adapter-release/wasi_snapshot_preview1.wasm');
  const preview1AdapterSha256='988224282d03fe0bd3c25b62344aef265b1a8e1f5804bdbc34d6442507fabcc0';
  const verify=async()=>{
    assert.equal(hash(await readFile(engine)),metadata.engineSha256);
    assert.equal(hash(await readFile(engine+'.build.json')),hash(metadataBytes));
    assert.equal(hash(await readFile(cache.path)),cache.sha256);
    for(const entry of tools)assert.equal(hash(await readFile(entry.path)),entry.sha256,entry.name);
    for(const entry of metadata.sourceManifest)assert.equal(hash(await readFile(join(sourceRoot,entry.path))),entry.sha256,entry.path);
    assert.equal(hash(await readFile(preview2Adapter)),preview1AdapterSha256);
  };
  await verify();
  const toolchain=await loadToolchain(),selected=await loadComponentizer(toolchain);
  assert.equal(selected.provenance.selection,'patched-import-i32-clock-v2');
  const options={engine,enableAot:true,aotCache:cache.path,wevalBin:tools.find(entry=>entry.name==='weval').path,aotMinStackSizeBytes:67108864,env:{RAYON_NUM_THREADS:'4'},disableFeatures:['stdio','random','clocks','http','fetch-event'],selectedInterfaces:[],preview2Adapter};
  return {engine,metadata,sourceRoot,toolchain,manifests:selectedManifestsForEngine(metadata,{sourceRoot}),verify,
    componentize:(source,other)=>selected.componentize(source,{...other,...options}),
    provenance:{engineSha256:metadata.engineSha256,engineMetadataSha256:hash(metadataBytes),cache,tools,options,preview1AdapterSha256,packaging:selected.provenance,scope:'Exact frozen-v5 Release Weval engine/cache/tools, explicit audited v2 guest splicer and feature-OFF selection. No implicit engine/cache/tool fallback.'}};
}
