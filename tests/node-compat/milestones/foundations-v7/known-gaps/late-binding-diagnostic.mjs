// Ordinary public object getter reached while ComponentizeJS binds a valid
// exported WIT interface. Preserves baseline acceptance as a known policy gap.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFile,writeFile,mkdir,symlink} from 'node:fs/promises';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {loadToolchain} from '../toolchain.mjs';
import {loadComponentizer} from '../componentizer.mjs';
const hash=x=>createHash('sha256').update(x).digest('hex');
const here=dirname(fileURLToPath(import.meta.url));
const engine=resolve(process.env.NODE_COMPAT_ENGINE),sourceRoot=resolve(process.env.NODE_COMPAT_ENGINE_SOURCE_ROOT),output=resolve(process.env.NODE_COMPAT_ADD_ABORT_OUTPUT);
await mkdir(output,{recursive:true});await writeFile(join(output,'package.json'),'{"type":"module"}\n');
const metadata=JSON.parse(await readFile(engine+'.build.json'));assert.equal(hash(await readFile(engine)),metadata.engineSha256);assert.equal(metadata.observedCMakeOptions.CMAKE_BUILD_TYPE,'Release');assert.equal(metadata.strictInitialization,true);assert.equal(metadata.oomTesting,false);
for(const entry of metadata.sourceManifest)assert.equal(hash(await readFile(join(sourceRoot,entry.path))),entry.sha256,entry.path);
const toolchain=await loadToolchain(),selected=await loadComponentizer(toolchain);
try{await symlink(join(toolchain.directory,'node_modules'),join(output,'node_modules'));}catch(error){if(error.code!=='EEXIST')throw error;}
const adapter=resolve(here,'../../../host-apis/wasi-0.2.0/preview1-adapter-release/wasi_snapshot_preview1.wasm');assert.equal(hash(await readFile(adapter)),'988224282d03fe0bd3c25b62344aef265b1a8e1f5804bdbc34d6442507fabcc0');
const witWorld='package test:late-event; world test { export api: interface { run: func() -> string; } }';
const source="import {spawn}from'node:child_process';let getters=0;export const api={get run(){getters++;const t=new EventTarget();t.addEventListener('test',()=>spawn());t.dispatchEvent(new Event('test'));return()=>JSON.stringify({getters,bound:true})}};";
let built,error;try{built=await selected.componentize(source,{engine,preview2Adapter:adapter,witWorld,worldName:'test',disableFeatures:['stdio','random','clocks','http','fetch-event'],selectedInterfaces:[]});}catch(failure){error=failure.message;}
const expect=process.env.NODE_COMPAT_LATE_BINDING_EXPECT??'baseline-accepted';assert(['baseline-accepted','fixed-rejected'].includes(expect));assert.equal(!!error,expect==='fixed-rejected');
const report={schemaVersion:1,state:expect==='baseline-accepted'?'late-export-getter-event-error-accepted-baseline':'late-export-getter-event-error-rejected-fixed',recordedAtUtc:new Date().toISOString(),engineSha256:metadata.engineSha256,sourceRoot,sourceFilesVerified:metadata.sourceManifest.length,source,sourceSha256:hash(source),witWorld,componentizerProvenance:selected.provenance,error};
if(built){assert.deepEqual(built.interfaceAudit.emittedImports,[]);const{transpile,componentWit}=await import(pathToFileURL(toolchain.require.resolve('@bytecodealliance/jco')));report.interfaceAudit=built.interfaceAudit;report.emittedWit=await componentWit(built.component);report.componentSha256=hash(built.component);report.componentBytes=built.component.length;await writeFile(join(output,'late-binding.component.wasm'),built.component);const{files}=await transpile(built.component,{name:'late_binding'});for(const[name,bytes]of Object.entries(files)){await mkdir(dirname(join(output,name)),{recursive:true});await writeFile(join(output,name),bytes);}const module=await import(pathToFileURL(join(output,'late_binding.js')));report.jco=JSON.parse(await module.api.run());assert.deepEqual(report.jco,{getters:1,bound:true});}
await writeFile(join(output,'late-binding-results.json'),JSON.stringify(report,null,2)+'\n');await writeFile(join(here,expect==='baseline-accepted'?'late-binding-baseline-results.json':'late-binding-fixed-results.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({state:report.state,error,componentSha256:report.componentSha256,sourceFilesVerified:report.sourceFilesVerified}));
