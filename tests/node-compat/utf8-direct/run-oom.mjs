import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {spawnSync} from 'node:child_process';
import {loadToolchain} from '../toolchain.mjs';
import {loadComponentizer} from '../componentizer.mjs';
import {bundleProfile} from '../profile-bundler.mjs';
import {selectedManifestsForEngine} from '../module-selection.mjs';
const here=dirname(fileURLToPath(import.meta.url)),hash=data=>createHash('sha256').update(data).digest('hex');
assert.equal(process.version,'v22.14.0');assert(process.env.NODE_COMPAT_ENGINE);
const engine=resolve(process.env.NODE_COMPAT_ENGINE),metadata=JSON.parse(await readFile(engine+'.build.json'));
assert.equal(hash(await readFile(engine)),metadata.engineSha256);assert.equal(metadata.observedCMakeOptions.CMAKE_BUILD_TYPE,'Debug');assert.equal(metadata.oomTesting,true);assert.equal(metadata.gcStress,true);
assert.equal(metadata.utf8DirectExperiment?.webCodecOOMTesting,true);assert.equal(metadata.utf8DirectExperiment?.webCodecGCStress,true);
const sourceRoot=metadata.utf8DirectExperiment.sourceRoot;
for(const entry of metadata.sourceManifest)assert.equal(hash(await readFile(join(sourceRoot,entry.path))),entry.sha256,entry.path);
const tc=await loadToolchain(),selected=await loadComponentizer(tc,{debugScalarOOMDiagnostic:true});
const bundle=await bundleProfile({rolldown:tc.rolldown,parseAst:tc.parseAst,input:join(here,'oom-component.mjs'),builtinManifests:selectedManifestsForEngine(metadata,{sourceRoot})});assert.deepEqual([...bundle.imports].sort(),['node:buffer','node:child_process']);
const world=await readFile(join(here,'../oom/profile.wit'),'utf8');assert.equal(hash(world),'2384f23573d9f9264940b5f2e574ca06d43ad3a43587beb53f2fc308cd3ebb84');
const output=resolve(process.env.NODE_COMPAT_UTF8_OOM_OUTPUT??'/tmp/starling-node-compat/utf8-direct/oom-result');await mkdir(output,{recursive:true});await writeFile(join(output,'package.json'),'{"type":"module"}\n');await writeFile(join(output,'bundle.mjs'),bundle.code);
const{component,debugDiagnosticAudit}=await selected.componentize(bundle.code,{engine,witWorld:world,worldName:'profile',disableFeatures:['stdio','random','clocks','http','fetch-event'],selectedInterfaces:[]});assert(debugDiagnosticAudit);
const componentPath=join(output,'codec-oom.component.wasm');await writeFile(componentPath,component);
const{componentWit,transpile}=await import(pathToFileURL(tc.require.resolve('@bytecodealliance/jco'))),wit=await componentWit(component);assert.deepEqual(wit.split('\n').filter(line=>/^\s*import /.test(line)),[]);
const{files}=await transpile(component,{name:'codec-oom'});for(const[name,data]of Object.entries(files)){const path=join(output,name);await mkdir(dirname(path),{recursive:true});await writeFile(path,data);}
const guest=await import(pathToFileURL(join(output,'codec-oom.js'))),statuses=[];
function check(status,call){assert.equal(status,(call<<16)|0x7fff,`OOM stage ${status<0?-status:'mask/call'} failed`);return status;}
for(let call=1;call<=3;call++){const status=guest.run();statuses.push(status);await writeFile(join(output,'progress.json'),JSON.stringify(statuses)+'\n');check(status,call);}
const wasmtime=process.env.NODE_COMPAT_WASMTIME??'/tmp/starling-node-compat/bin/wasmtime-v42.0.1-aarch64-macos/wasmtime';
const host=spawnSync(wasmtime,['run','--invoke','run()',componentPath],{encoding:'utf8',timeout:180000,maxBuffer:1024*1024});assert.equal(host.status,0,host.error?.message??host.stderr);const hostStatus=check(Number(host.stdout.trim()),1);
const report={schemaVersion:1,atUtc:new Date().toISOString(),engine,engineSha256:metadata.engineSha256,metadata,sourceRoot,packaging:selected.provenance,debugDiagnosticAudit,bundleSha256:hash(bundle.code),componentPath,componentBytes:component.length,componentSha256:hash(component),emittedImports:[],emittedWit:wit,statuses,wasmtimeStatus:hostStatus,faults:['four unchanged Buffer allocation scopes','TextEncoder JS_EnsureLinearString on an actually non-linear input','TextEncoder JS_NewUint8Array'],recovery:{pairs:32,codecCallsPerCall:64,backingAndOffsets:true,exceptionIdentity:true,snapshotOwners:true},sourceFiles:await Promise.all(['oom-component.mjs','run-oom.mjs','../oom/component.mjs','../oom/profile.wit'].map(async path=>({path,sha256:hash(await readFile(join(here,path)))}))),limitations:['Fixture-bounded EngineState guard: finish_pre_initialization precedes bindExports; this fixture exports a plain run function, has no late encode getters, and uses only the exact scalar diagnostic WIT.','Six selected API allocation checkpoints, not exhaustive engine-wide OOM. No JS fault controls or synthetic exceptions.','No general DEBUG indirect Component Model binding support is claimed.','Dedicated debug/GC/fault artifact is not a performance or deployment artifact.']};
await writeFile(join(output,'results.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({engineSha256:metadata.engineSha256,componentSha256:report.componentSha256,statuses,wasmtimeStatus:hostStatus,emittedImports:[]},null,2));
