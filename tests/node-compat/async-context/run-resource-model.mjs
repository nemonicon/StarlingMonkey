import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {spawnSync} from 'node:child_process';
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {loadToolchain} from '../toolchain.mjs';
import {loadComponentizer} from '../componentizer.mjs';
const here=dirname(fileURLToPath(import.meta.url)),hash=value=>createHash('sha256').update(value).digest('hex');
assert.equal(process.version,'v22.14.0');assert(process.env.NODE_COMPAT_ENGINE,'Select the separate resource-model engine explicitly');
const engine=resolve(process.env.NODE_COMPAT_ENGINE),metadata=JSON.parse(await readFile(engine+'.build.json'));
assert.equal(hash(await readFile(engine)),metadata.engineSha256);
assert.equal(metadata.observedCMakeOptions.CMAKE_BUILD_TYPE,'Release');
const nativeSource=await readFile(join(here,'resource-model-v3.cpp'));
assert.equal(metadata.sourceManifest.find(e=>e.path==='tests/node-compat/async-context/probe.cpp').sha256,hash(nativeSource));
for(const entry of metadata.sourceManifest)assert.equal(hash(await readFile(join(metadata.sourceRoot,entry.path))),entry.sha256,entry.path);
const tc=await loadToolchain(),selected=await loadComponentizer(tc);
const{componentWit,transpile}=await import(pathToFileURL(tc.require.resolve('@bytecodealliance/jco')));
const{rolldown}=await import(pathToFileURL(tc.require.resolve('rolldown')));
const build=await rolldown({input:join(here,'resource-model.mjs'),platform:'neutral'});
let bundled;try{const{output}=await build.generate({format:'esm',codeSplitting:false});assert.equal(output.length,1);bundled=output[0].code;}finally{await build.close();}
const world=await readFile(join(here,'probe.wit'),'utf8');
const output=resolve(process.env.NODE_COMPAT_ASYNC_PROBE_OUTPUT??'/tmp/starling-node-compat/async-context-resource-v3/component');
await mkdir(output,{recursive:true});await writeFile(join(output,'package.json'),'{"type":"module"}\n');await writeFile(join(output,'bundled.mjs'),bundled);
const{component}=await selected.componentize(bundled,{engine,witWorld:world,worldName:'profile',disableFeatures:['stdio','random','clocks','http','fetch-event']});
const componentPath=join(output,'resource-model.wasm');await writeFile(componentPath,component);
const emittedWit=await componentWit(component);assert.deepEqual(emittedWit.split('\n').filter(line=>/^\s*import /.test(line)),[]);
const{files}=await transpile(component,{name:'resource-model'});
for(const[name,bytes]of Object.entries(files)){const path=join(output,name);await mkdir(dirname(path),{recursive:true});await writeFile(path,bytes);}
function validate(report,expectedCall){assert(!report.failure,JSON.stringify(report));assert.equal(report.calls,expectedCall);assert.equal(report.caseCount,19);assert.equal(report.observationCount,63);assert.equal(report.edges.caseCount,9);assert.equal(report.edges.observationCount,44);assert(report.cases.every(test=>test.passed));assert(report.edges.cases.every(test=>test.passed));assert(report.stats.privateNonPromiseCapabilities>0);assert(report.extras.movingGC);assert.equal(report.extras.nativeReactions,2);}
const guest=await import(pathToFileURL(join(output,'resource-model.js'))),reports=[];
for(let i=1;i<=3;i++){const report=JSON.parse(await guest.run());reports.push(report);await writeFile(join(output,'progress.json'),JSON.stringify(reports,null,2)+'\n');validate(report,i);}
const wasmtime=resolve(process.env.NODE_COMPAT_WASMTIME??'/tmp/starling-node-compat/bin/wasmtime-v42.0.1-aarch64-macos/wasmtime');
const host=spawnSync(wasmtime,['run','--invoke','run()',componentPath],{encoding:'utf8',timeout:120000,maxBuffer:1024*1024});assert.equal(host.status,0,host.error?.message??host.stderr);
const wave=host.stdout.trim().replace(/\\u\{([0-9a-fA-F]+)\}/g,(_,number)=>String.fromCodePoint(parseInt(number,16)));const hostReport=JSON.parse(JSON.parse(wave));validate(hostReport,1);
const sourceFiles=await Promise.all(['resource-model-v3.cpp','resource-model.mjs','resource-model-cases.mjs','resource-model-edge-cases.mjs','run-resource-model.mjs','probe.wit'].map(async path=>({path,sha256:hash(await readFile(join(here,path)))})));
const result={schemaVersion:1,atUtc:new Date().toISOString(),node:process.version,engine,engineSha256:metadata.engineSha256,metadata,packaging:selected.provenance,sourceFiles,bundledSha256:hash(bundled),worldSha256:hash(world),componentPath,componentSha256:hash(component),componentBytes:component.length,emittedImports:[],emittedWit,reports,wasmtime:hostReport,comparisonScope:'Store/receiver/argument/error identity and resource mutation only. Guest timer/repetition/I/O cases use pure guest AsyncTask completion, not actual clocks/filesystem or HTTP. Async IDs/createHook/destroy hooks and Promise executionAsyncResource identity are excluded.'};
const resultPath=join(here,'resource-model-results.json');await writeFile(resultPath,JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify({engineSha256:metadata.engineSha256,componentSha256:result.componentSha256,emittedImports:[],calls:reports.length,casesPerCall:reports.map(r=>[r.caseCount,r.observationCount,r.edges.caseCount,r.edges.observationCount,r.extras.checks]),resultPath},null,2));
