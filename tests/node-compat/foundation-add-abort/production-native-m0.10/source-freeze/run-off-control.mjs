// Actual Events-OFF module admission only. NO native receiver/prototype calls
// and no public-cases/receiver fixture import is permitted in this control.
import assert from 'node:assert/strict';
import {readFile,writeFile,mkdir,symlink} from 'node:fs/promises';
import {resolve,join,dirname} from 'node:path';
import {pathToFileURL,fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
import {loadToolchain} from '../../toolchain.mjs';
import {loadComponentizer} from '../../componentizer.mjs';
import {bundleProfile} from '../../profile-bundler.mjs';
import {selectedManifestsForEngine} from '../../module-selection.mjs';
import {hash} from './preflight.mjs';
assert.equal(process.version,'v22.14.0');
const engine=resolve(process.env.NODE_COMPAT_ENGINE),root=resolve(process.env.NODE_COMPAT_ENGINE_SOURCE_ROOT),metadataBytes=await readFile(engine+'.build.json'),metadata=JSON.parse(metadataBytes);
assert.equal(hash(await readFile(engine)),metadata.engineSha256);assert.equal(metadata.eventsEnabled,false);assert.equal(metadata.protectedAbortListenerEnabled,false);assert.equal(metadata.observedCMakeOptions.NODE_COMPAT_EVENTS,'OFF');assert.equal(metadata.observedCMakeOptions.CMAKE_BUILD_TYPE,'Release');assert.equal(metadata.gcStress,false);assert.equal(metadata.oomTesting,false);assert.equal(metadata.entropyPolicy,'off');assert.equal(metadata.sourceManifest.length,304);
for(const entry of metadata.sourceManifest)assert.equal(hash(await readFile(join(root,entry.path))),entry.sha256,entry.path);
for(const command of metadata.protectedAbortListenerPolicy.actualLayoutCompileCommands.concat(metadata.protectedAbortListenerPolicy.actualEmbeddingCompileCommands))assert(!command.split(/\s+/).includes('-DNODE_COMPAT_EVENTS_ADD_ABORT_LISTENER=1'));
const manifests=selectedManifestsForEngine(metadata,{sourceRoot:root}),toolchain=await loadToolchain(),selected=await loadComponentizer(toolchain);
const output=resolve(process.env.NODE_COMPAT_ADD_ABORT_OUTPUT??'/tmp/starling-node-compat/foundations-v10/events-off-admission');await mkdir(output,{recursive:true});await writeFile(join(output,'started.json'),'{}\n',{flag:'wx'});await writeFile(join(output,'package.json'),'{"type":"module"}\n');
await symlink(join(toolchain.directory,'node_modules'),join(output,'node_modules'));
const adapter=join(root,'host-apis/wasi-0.2.0/preview1-adapter-release/wasi_snapshot_preview1.wasm');assert.equal(hash(await readFile(adapter)),'988224282d03fe0bd3c25b62344aef265b1a8e1f5804bdbc34d6442507fabcc0');
const options={engine,preview2Adapter:adapter,witWorld:'package starling:abort-off-control; world profile { export run: func() -> string; }',worldName:'profile',disableFeatures:['stdio','random','clocks','http','fetch-event'],selectedInterfaces:[]};
const failures=[];
for(const id of ['node:events','events']){
 const source=`import*as events from${JSON.stringify(id)};export function run(){return'unreachable'}`,input=join(output,id.replace(':','-')+'.mjs');await writeFile(input,source);
 let bundled;try{await bundleProfile({...toolchain,input,builtinManifests:manifests});}catch(error){bundled=error.message;}assert.match(bundled??'',/not admitted/);
 let native;try{await selected.componentize(source,options);}catch(error){native=error.message;}assert.match(native??'',/events|module/i);
 failures.push({id,sourceSha256:hash(source),bundler:bundled,nativeComponentization:native});
}
const{component,interfaceAudit}=await selected.componentize("export function run(){return'EVENTS_OFF_OK'}",options);assert.deepEqual(interfaceAudit.emittedImports,[]);
const componentPath=join(output,'off-control.component.wasm');await writeFile(componentPath,component);const{transpile}=await import(pathToFileURL(toolchain.require.resolve('@bytecodealliance/jco'))),{files}=await transpile(component,{name:'off_control'});
for(const[name,bytes]of Object.entries(files)){await mkdir(dirname(join(output,name)),{recursive:true});await writeFile(join(output,name),bytes);}const instance=await import(pathToFileURL(join(output,'off_control.js')));assert.equal(instance.run(),'EVENTS_OFF_OK');
const host=resolve(process.env.NODE_COMPAT_WASMTIME??'/tmp/starling-node-compat/bin/wasmtime-v42.0.1-aarch64-macos/wasmtime'),fresh=spawnSync(host,['run','--invoke','run()',componentPath],{encoding:'utf8',timeout:120000});assert.equal(fresh.status,0,fresh.stderr);assert.equal(JSON.parse(fresh.stdout.trim()),'EVENTS_OFF_OK');
const report={state:'M10_ACTUAL_EVENTS_OFF_ADMISSION_PASSED',engineSha256:metadata.engineSha256,engineReceiptSha256:hash(metadataBytes),sourceRoot:root,sourceFilesVerified:304,actualLayoutMacro:'ABSENT',failures,positive:{componentSha256:hash(component),componentBytes:component.length,interfaceAudit,jco:'EVENTS_OFF_OK',wasmtime:{status:fresh.status,stdout:fresh.stdout,stderr:fresh.stderr}},packaging:selected.provenance,runnerSha256:hash(await readFile(fileURLToPath(import.meta.url))),scope:'Only absent optional module/raw import and benign export controls. NO EventTarget/AbortSignal prototype/receiver negative executed on guard-absent engine.'};
await writeFile(join(output,'results.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({state:report.state,emittedImports:[],output},null,2));
