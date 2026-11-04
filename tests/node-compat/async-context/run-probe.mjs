import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {spawnSync} from 'node:child_process';
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {loadToolchain} from '../toolchain.mjs';
import {loadComponentizer} from '../componentizer.mjs';
const here=dirname(fileURLToPath(import.meta.url));
assert(process.env.NODE_COMPAT_ENGINE,'Select the separate diagnostic engine explicitly');
const engine=resolve(process.env.NODE_COMPAT_ENGINE),metadata=JSON.parse(await readFile(engine+'.build.json'));
const hash=value=>createHash('sha256').update(value).digest('hex');
assert.equal(hash(await readFile(engine)),metadata.engineSha256);
assert.equal(metadata.observedCMakeOptions.CMAKE_BUILD_TYPE,'Release');
assert(metadata.sourceManifest.some(e=>e.path==='tests/node-compat/async-context/probe.cpp'));
for(const e of metadata.sourceManifest)assert.equal(hash(await readFile(join(metadata.sourceRoot,e.path))),e.sha256,e.path);
const tc=await loadToolchain(),selected=await loadComponentizer(tc);
const{componentWit,transpile}=await import(pathToFileURL(tc.require.resolve('@bytecodealliance/jco')));
const output=resolve(process.env.NODE_COMPAT_ASYNC_PROBE_OUTPUT??'/tmp/starling-node-compat/async-context/component');
await mkdir(output,{recursive:true});await writeFile(join(output,'package.json'),'{"type":"module"}\n');
const source=await readFile(join(here,'probe.mjs'),'utf8'),world=await readFile(join(here,'probe.wit'),'utf8');
const{component}=await selected.componentize(source,{engine,witWorld:world,worldName:'profile',disableFeatures:['stdio','random','clocks','http','fetch-event']});
const componentPath=join(output,'context-probe.wasm');await writeFile(componentPath,component);
const emittedWit=await componentWit(component);assert.deepEqual(emittedWit.split('\n').filter(l=>/^\s*import /.test(l)),[]);
const{files}=await transpile(component,{name:'context-probe'});for(const[name,bytes]of Object.entries(files)){const path=join(output,name);await mkdir(dirname(path),{recursive:true});await writeFile(path,bytes);}
const guest=await import(pathToFileURL(join(output,'context-probe.js')));const reports=[];
for(let i=1;i<=3;i++){const report=JSON.parse(guest.run());reports.push(report);await writeFile(join(output,'progress.json'),JSON.stringify(reports,null,2)+'\n');assert(!report.failure,JSON.stringify(report));assert.equal(report.calls,i);assert.equal(report.stats.originalNativeMicrotaskQueue,1);assert.equal(report.stats.nativeMicrotaskQueueNow,0);assert(report.stats.captures>0);assert(report.stats.creationChoices>0);assert(report.stats.fallbacks>0);}
const wasmtime=resolve(process.env.NODE_COMPAT_WASMTIME??'/tmp/starling-node-compat/bin/wasmtime-v42.0.1-aarch64-macos/wasmtime');
const host=spawnSync(wasmtime,['run','--invoke','run()',componentPath],{encoding:'utf8',timeout:120000,maxBuffer:1024*1024});assert.equal(host.status,0,host.error?.message??host.stderr);const wave=host.stdout.trim().replace(/\\u\{([0-9a-fA-F]+)\}/g,(_,n)=>String.fromCodePoint(parseInt(n,16)));const hostReport=JSON.parse(JSON.parse(wave));assert(!hostReport.failure,JSON.stringify(hostReport));assert.equal(hostReport.calls,1);
const privateRecordProbe=metadata.sourceManifest.find(e=>e.path==='tests/node-compat/async-context/probe.cpp').sha256===hash(await readFile(join(here,'probe-private-v2.cpp')));
if(privateRecordProbe){for(const report of [...reports,hostReport]){assert(report.stats.privateReactionRecords>0);assert(report.stats.privateNonPromiseCapabilities>0);assert(report.knownGaps.every(gap=>gap.matchesNode));}}
const result={schemaVersion:1,atUtc:new Date().toISOString(),node:process.version,engine,engineSha256:metadata.engineSha256,metadata,packaging:selected.provenance,sourceSha256:hash(source),worldSha256:hash(world),componentPath,componentSha256:hash(component),componentBytes:component.length,emittedImports:[],emittedWit,reports,wasmtime:hostReport,privateRecordProbe,sourceFiles:await Promise.all(['probe.cpp','probe.cmake','probe.mjs','probe.wit','run-probe.mjs'].map(async name=>({path:name,sha256:hash(await readFile(name==='probe.cpp'||name==='probe.cmake'?join(metadata.sourceRoot,'tests/node-compat/async-context',name):join(here,name)))}))),scope:'Separate experimental guest native queue/context extension, not production AsyncLocalStorage. Actual Promise registration and creation hooks, awaited continuations/native reactions/GC/pure guest event-loop tasks; no new external host capability. The private-record variant is tied to the validated SpiderMonkey 147 reaction layout; the public-hook variant reports its species mismatch.'};
const resultPath=resolve(process.env.NODE_COMPAT_ASYNC_PROBE_RESULTS??join(here,'probe-results.json'));
await writeFile(resultPath,JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify({engineSha256:metadata.engineSha256,componentSha256:result.componentSha256,emittedImports:[],calls:reports.length,checksPerCall:reports.map(r=>r.observations.length),optimizedAwait:reports[0].observations.find(x=>x.name==='optimizedAwaitMetric'),knownGaps:reports[0].knownGaps,privateRecordProbe,resultPath},null,2));
