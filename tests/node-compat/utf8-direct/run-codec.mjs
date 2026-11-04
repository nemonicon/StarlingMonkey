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
assert.equal(process.version,'v22.14.0');assert(process.env.NODE_COMPAT_ENGINE,'Select candidate or exact preserved control explicitly');
const engine=resolve(process.env.NODE_COMPAT_ENGINE),metadata=JSON.parse(await readFile(engine+'.build.json'));
assert.equal(hash(await readFile(engine)),metadata.engineSha256);assert.equal(metadata.observedCMakeOptions.CMAKE_BUILD_TYPE,'Release');
const control=['3d106756f65c6dd18b590ba3f41b4cc760635c27fb738b678ead8bccd8a21897','0bb5743ba97dbbc8d2c7636fe1ae35ad37e135ea523f9c8939004198fc4c21f8'].includes(metadata.engineSha256);
assert(control||metadata.utf8DirectExperiment,'Require a known preserved v3 control or explicitly identified private candidate');
const sourceRoot=resolve(process.env.NODE_COMPAT_ENGINE_SOURCE_ROOT??metadata.utf8DirectExperiment?.sourceRoot??'/tmp/starling-node-compat/foundations-v3/native-freeze/source');
for(const entry of metadata.sourceManifest)assert.equal(hash(await readFile(join(sourceRoot,entry.path))),entry.sha256,entry.path);
const oracle=JSON.parse(await readFile(join(here,'node-oracle-results.json')));
assert.equal(hash(await readFile(join(here,'codec-cases.mjs'))),oracle.sharedCasesSha256);
const tc=await loadToolchain(),selected=await loadComponentizer(tc),manifests=selectedManifestsForEngine(metadata,{sourceRoot});
const bundle=await bundleProfile({rolldown:tc.rolldown,parseAst:tc.parseAst,input:join(here,'codec-component.mjs'),builtinManifests:manifests});assert.deepEqual(bundle.imports,['node:buffer']);
const world=await readFile(join(here,'profile.wit'),'utf8'),output=resolve(process.env.NODE_COMPAT_UTF8_OUTPUT??`/tmp/starling-node-compat/utf8-direct/codec-${metadata.utf8DirectExperiment?.variant??'control'}`);await mkdir(output,{recursive:true});await writeFile(join(output,'package.json'),'{"type":"module"}\n');await writeFile(join(output,'bundle.mjs'),bundle.code);
const{component,interfaceAudit}=await selected.componentize(bundle.code,{engine,witWorld:world,worldName:'profile',disableFeatures:['stdio','random','clocks','http','fetch-event'],selectedInterfaces:[],preview2Adapter:join(sourceRoot,'host-apis/wasi-0.2.0/preview1-adapter-release/wasi_snapshot_preview1.wasm')});
const componentPath=join(output,'codec.component.wasm');await writeFile(componentPath,component);
const{componentWit,transpile}=await import(pathToFileURL(tc.require.resolve('@bytecodealliance/jco'))),wit=await componentWit(component);assert.deepEqual(wit.split('\n').filter(line=>/^\s*import /.test(line)),[]);
const{files}=await transpile(component,{name:'codec'});for(const[name,data]of Object.entries(files)){const path=join(output,name);await mkdir(dirname(path),{recursive:true});await writeFile(path,data);}
const guest=await import(pathToFileURL(join(output,'codec.js'))),reports=[];
function validate(report,call){
  assert.equal(report.calls,call);
  if(report.failure)return false;
  assert.equal(report.caseCount,oracle.caseCount);assert.equal(report.observationCount,oracle.observationCount);
  assert.deepEqual(report.cases.map(test=>({name:test.name,passed:test.passed,observations:test.observations})),oracle.cases.map(test=>({name:test.name,passed:test.passed,observations:test.observations})));
  assert(report.cases.every(test=>test.passed));return true;
}
for(let i=1;i<=3;i++){const report=JSON.parse(guest.run());reports.push(report);await writeFile(join(output,'progress.json'),JSON.stringify(reports,null,2)+'\n');if(!validate(report,i))break;}
const wasmtime=resolve(process.env.NODE_COMPAT_WASMTIME??'/tmp/starling-node-compat/bin/wasmtime-v42.0.1-aarch64-macos/wasmtime');
const host=spawnSync(wasmtime,['run','--invoke','run()',componentPath],{encoding:'utf8',timeout:120000,maxBuffer:2*1024*1024});assert.equal(host.status,0,host.error?.message??host.stderr);
const wave=host.stdout.trim().replace(/\\u\{([0-9a-fA-F]+)\}/g,(_,number)=>String.fromCodePoint(parseInt(number,16))),hostReport=JSON.parse(JSON.parse(wave));const hostPass=validate(hostReport,1),passed=reports.length===3&&reports.every((report,index)=>validate(report,index+1))&&hostPass;
const report={schemaVersion:1,atUtc:new Date().toISOString(),engine,engineSha256:metadata.engineSha256,metadata,control,sourceRoot,packaging:selected.provenance,bundleSha256:hash(bundle.code),worldSha256:hash(world),componentPath,componentBytes:component.length,componentSha256:hash(component),emittedImports:[],emittedWit:wit,interfaceAudit,oracleReceiptSha256:hash(await readFile(join(here,'node-oracle-results.json'))),sourceFiles:await Promise.all(['codec-cases.mjs','codec-component.mjs','profile.wit','run-codec.mjs'].map(async path=>({path,sha256:hash(await readFile(join(here,path)))}))),reports,wasmtime:hostReport,passed,scope:'Bounded shared Node Web TextEncoder semantics plus supported Buffer UTF8 bytes. Candidate GC is private automatic native collection at rooted boundaries; no JS GC/fault control or custom host capability is exposed.'};
await writeFile(join(output,'results.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({engineSha256:metadata.engineSha256,componentSha256:report.componentSha256,control,passed,caseCounts:reports.map(value=>[value.caseCount,value.assertionCount,value.observationCount]),failure:reports.find(value=>value.failure)?.failure,output},null,2));
assert(passed||control,'Private candidate must pass all shared codec observations');
