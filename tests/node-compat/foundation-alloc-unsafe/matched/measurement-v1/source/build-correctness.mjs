// Correctness/artifact-size only. No host timing/RSS/grow measurements here.
import assert from 'node:assert/strict';
import {Buffer as NodeBuffer} from 'node:buffer';
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {dirname,join} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {spawnSync} from 'node:child_process';
import {nativeHarness,hash} from '../../foundations/native-scalar-harness.mjs';
import {selectCoreExpectations} from '../../core-expectations.mjs';
import {loadToolchain} from '../../toolchain.mjs';
import {loadComponentizer} from '../../componentizer.mjs';
import {createWorkload,operations,sizes,iterationsFor} from './workload.mjs';
import {loadCompiled} from './instantiate.mjs';
const here=dirname(fileURLToPath(import.meta.url));
assert.equal(process.env.NODE_COMPAT_ALLOC_UNSAFE_MEASURE,undefined,'Correctness script does not run measurements');
const h=await nativeHarness({kind:'allocation-matched',here,enabledField:'profileEnabled',option:'ENABLE_BUILTIN_NODE_COMPAT',outputVariable:'NODE_COMPAT_ALLOC_UNSAFE_MATCHED_OUTPUT'});
assert.equal(h.evidence.engineSha256,'e16c19fc567753517d7b61b65372dd7dc86de8f839e7acab959b5cf5eaf294c9');
assert.equal(h.metadata.sourceManifest.length,293);assert.equal(h.metadata.strictInitialization,true);
assert.equal(h.metadata.observedCMakeOptions.CMAKE_BUILD_TYPE,'Release');assert.equal(h.metadata.observedCMakeOptions.WEVAL,'OFF');
for(const key of ['oomTesting','wptSupportEnabled'])assert.equal(h.metadata[key],false);
const corePolicy=selectCoreExpectations(h.metadata,{sourceRoot:h.evidence.sourceRoot});assert.equal(corePolicy.coreVersion,'sm-node-22.14.0-m0.8');
const tc=await loadToolchain(),packaging=await loadComponentizer(tc);
const{componentWit,transpile}=await import(pathToFileURL(tc.require.resolve('@bytecodealliance/jco')));
const adapterPath=join(dirname(tc.require.resolve('@bytecodealliance/jco')),'node-builtins/buffer.js');
const{createBufferBuiltin}=await import(pathToFileURL(adapterPath));
const adapter=createBufferBuiltin({options:{}}),adapterId=adapter.resolveId('node:buffer'),coreId='\0jco-node-builtin:unenv-buffer-core';
const generatedAdapter=adapter.load(adapterId),generatedCore=adapter.load(coreId);
assert(generatedCore.includes('globalThis.Buffer = Buffer;'));assert(!/\bwasi:|jco-std|node:crypto/.test(generatedCore));
for(const[name,text]of[['jco-generated-adapter.mjs',generatedAdapter],['jco-generated-core.mjs',generatedCore]])await writeFile(join(h.output,name),text);
const unenvPackage=JSON.parse(await readFile(tc.require.resolve('unenv/package.json')));assert.equal(unenvPackage.version,'2.0.0-rc.24');
const unenvCore=tc.require.resolve('unenv/node/internal/buffer/buffer'),unenvSource=await readFile(unenvCore,'utf8');
assert.match(unenvSource,/const buf = new Uint8Array\(length\)/);assert.match(unenvSource,/return createBuffer\(size < 0 \? 0 : checked\(size\) \| 0\)/);
const nodeOracle=createWorkload(NodeBuffer),correctnessCases=[];
// No Node unsafe-byte inspection: only fully written fingerprint positions.
for(const operation of operations)for(const size of sizes)for(const iterations of [0,1,3])correctnessCases.push({operation:operation.id,size,iterations,expected:nodeOracle.batch(operation.id,size,iterations)});
const scenarios=operations.flatMap(operation=>sizes.map(size=>({operation:operation.id,name:operation.name,size,iterations:iterationsFor(size)})));
// Closed-form checksum using deterministic length/written bytes, not allocations.
for(const scenario of scenarios){let sum=0x811c9dc5;for(let i=0;i<scenario.iterations;i++)sum=Math.imul(sum^(scenario.size+(i&255)+((i*17+3)&255)),16777619)>>>0;scenario.expected=sum;}
const sourceNames=['workload.mjs','benchmark.wit','instantiate.mjs','build-correctness.mjs','measure.mjs','README.md'];
const sourceFiles=[];await mkdir(join(h.output,'source'),{recursive:true});
for(const name of sourceNames){const bytes=await readFile(join(here,name));sourceFiles.push({name,sha256:hash(bytes)});await writeFile(join(h.output,'source',name),bytes);}
const wit=await readFile(join(here,'benchmark.wit'),'utf8'),records=[];
for(const arm of ['native','jco-js']){
  const entry=join(here,arm+'.virtual-entry.mjs'),entrySource=`import {Buffer as Selected} from 'allocation:selected';
import {Buffer as Installed} from 'allocation:installed';
import {createWorkload} from './workload.mjs';
if ((Selected===Installed)!==${arm==='native'}) throw new Error('Wrong allocation implementation');
if (globalThis.Buffer!==Selected) throw new Error('Global Buffer contamination');
if (Selected.isEncoding('base64')!==${arm==='jco-js'}) throw new Error('Wrong allocation encoding marker');
export const batch=createWorkload(Selected).batch;`;
  const build=await tc.rolldown({input:entry,platform:'neutral',treeshake:true,transform:{target:'es2016'},plugins:[{
    name:'actual-jco-allocation-comparison',resolveId(id){if(id===entry)return id;if(id==='allocation:installed')return{id:'node:buffer',external:true};
      if(id==='allocation:selected')return arm==='native'?{id:'node:buffer',external:true}:adapterId;
      if(arm==='jco-js')return adapter.resolveId(id);return null;},load(id){if(id===entry)return entrySource;if(arm==='jco-js')return adapter.load(id);return null;}}]});
  let chunk;try{const result=await build.generate({format:'esm',codeSplitting:false});assert.equal(result.output.length,1);chunk=result.output[0];}finally{await build.close();}
  assert.deepEqual(chunk.imports,['node:buffer']);assert(!/reference-kernel|createAllocUnsafeCandidate|temporarilyPatch/.test(chunk.code));
  const moduleIds=Object.keys(chunk.modules);assert.equal(moduleIds.includes(unenvCore),arm==='jco-js');
  const directory=join(h.output,arm);await mkdir(directory,{recursive:true});await writeFile(join(directory,'application.bundle.mjs'),chunk.code);
  const{component,interfaceAudit}=await packaging.componentize(chunk.code,{engine:process.env.NODE_COMPAT_ENGINE,
    preview2Adapter:h.evidence.adapter.path,witWorld:wit,worldName:'comparison',selectedInterfaces:[],disableFeatures:['stdio','random','clocks','http','fetch-event']});
  assert.deepEqual(interfaceAudit.emittedImports,[]);const emittedWit=await componentWit(component);
  assert.equal(emittedWit.replace(/\s+/g,' ').trim(),'package root:component; world root { export batch: func(operation: u32, size: u32, iterations: u32) -> u32; }');
  const componentPath=join(directory,'allocation.component.wasm');await writeFile(componentPath,component);await writeFile(join(directory,'component.wit'),emittedWit);
  const{files}=await transpile(component,{name:'allocation',instantiation:'async'});for(const[name,bytes]of Object.entries(files)){await mkdir(dirname(join(directory,name)),{recursive:true});await writeFile(join(directory,name),bytes);}
  const record={arm,componentPath,componentSha256:hash(component),componentBytes:component.length,emittedImports:[],emittedWit,interfaceAudit,
    modulePath:join(directory,'allocation.js'),coreFiles:Object.keys(files).filter(name=>name.endsWith('.wasm')),
    transpiledFiles:Object.entries(files).map(([name,bytes])=>({name,sha256:hash(bytes)})),
    bundleSha256:hash(chunk.code),bundleBytes:Buffer.byteLength(chunk.code),bundleImports:chunk.imports,moduleIds,
    sourceManifest:await Promise.all(moduleIds.filter(id=>id.startsWith('/')&&id!==entry).map(async path=>({path,sha256:hash(await readFile(path))}))),
    entrySource,entrySourceSha256:hash(entrySource)};
  const instantiate=await loadCompiled(record),instances=[];
  for(let fresh=0;fresh<2;fresh++){
    const instance=await instantiate(),observed=[];
    for(const test of correctnessCases){const actual=instance.exports.batch(test.operation,test.size,test.iterations);assert.equal(actual,test.expected,arm+' '+JSON.stringify(test));observed.push(actual);}
    for(const size of sizes)assert.equal(instance.exports.batch(4,size,1),(size^0x71c9a32d)>>>0);
    // Repeat after all cases: guest has no hidden per-operation carried state.
    assert.equal(instance.exports.batch(0,64,3),correctnessCases.find(test=>test.operation===0&&test.size===64&&test.iterations===3).expected);
    instances.push({freshInstance:fresh,cases:observed.length,checksums:observed,zeroingNoPoolSizes:sizes,repeatAfterAllCases:true});
  }
  const hostCases=[];
  for(const operation of operations)for(const size of sizes){
    const expected=correctnessCases.find(test=>test.operation===operation.id&&test.size===size&&test.iterations===3).expected;
    const result=spawnSync(h.evidence.host.path,['run','--invoke',`batch(${operation.id},${size},3)`,componentPath],{encoding:'utf8',timeout:120000});
    assert.equal(result.status,0,result.error?.message??result.stderr);assert.equal(Number(result.stdout.trim()),expected);
    hostCases.push({operation:operation.id,size,iterations:3,expected,stdoutSha256:hash(result.stdout),stderr:result.stderr});
  }
  record.correctness={retainedCasesPerInstance:correctnessCases.length,freshJcoInstances:instances,freshWasmtimeCases:hostCases,measurementsExecuted:false};records.push(record);
}
for(const item of h.metadata.sourceManifest)assert.equal(hash(await readFile(join(h.evidence.sourceRoot,item.path))),item.sha256,item.path);
for(const item of sourceFiles)assert.equal(hash(await readFile(join(here,item.name))),item.sha256,item.name);
assert.equal(hash(await readFile(process.env.NODE_COMPAT_ENGINE)),h.evidence.engineSha256);
const report={schema:1,state:'matched-allocation-correctness-only-passed',atUtc:new Date().toISOString(),...h.evidence,corePolicy,node:process.version,
  nodeExecutableSha256:hash(await readFile(process.execPath)),sourceFiles,worldSha256:hash(wit),records,correctnessCases,scenarios,
  adapter:{path:adapterPath,sha256:hash(await readFile(adapterPath)),packageVersion:'1.40.0',generatedAdapterSha256:hash(generatedAdapter),generatedCoreSha256:hash(generatedCore),
    generatorSources:await Promise.all(['buffer.js','shared.js','unenv.js'].map(async name=>{const path=join(dirname(adapterPath),name);return{path,sha256:hash(await readFile(path))};})),
    unenvVersion:unenvPackage.version,unenvCore,unenvCoreSha256:hash(unenvSource),lockSha256:hash(await readFile(join(tc.directory,'package-lock.json'))),
    globalBufferReplacement:true,portableGuestOnly:true,hostImportEvidence:'Actual adapter bundle has only native-registry node:buffer import; final component imports[]'},
  artifactByteDelta:records[1].componentBytes-records[0].componentBytes,measurementsExecuted:false,
  limitations:['Both arms retain identical installed profile engine; delta is extra bundled adapter overhead, not profile-free engine saving',
    'Jco adapter uses newer Node-facing shape and broader permissive validation; only fixed common integer allocations compared',
    'Both selected implementations zero fresh no-pool backing; actual Node22 slab/uninitialized behavior is not a timed comparator',
    'No previous performance observations transferred; no time/RSS/linear memory/grow data collected by this correctness build',
    'Later Jco public Memory byteLength samples observe boundary changes only; hidden in-Wasm grow counts/failures are unavailable']};
await writeFile(join(h.output,'correctness-results.json'),JSON.stringify(report,null,2)+'\n');await writeFile(join(here,'correctness-results.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({state:report.state,output:h.output,artifactByteDelta:report.artifactByteDelta,arms:records.map(({arm,componentBytes,componentSha256})=>({arm,componentBytes,componentSha256})),measurementsExecuted:false}));
