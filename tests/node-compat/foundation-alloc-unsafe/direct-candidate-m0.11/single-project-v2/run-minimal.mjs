// Prepared private installed baseline/candidate minimal correctness builder.
// No host timers/RSS/memory-byte-length observations or timing path.
import assert from 'node:assert/strict';
import {Buffer as NodeBuffer} from 'node:buffer';
import {readFile,writeFile,mkdir,symlink,statfs} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {dirname,join} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {spawnSync} from 'node:child_process';
import {admitFrozenEngine} from './experiment.mjs';
import {createWorkload,operations,sizes,iterationsFor} from '../../matched/workload.mjs';
import {loadCompiled} from '../../matched/instantiate.mjs';
const here=dirname(fileURLToPath(import.meta.url)),hash=bytes=>createHash('sha256').update(bytes).digest('hex');
assert.equal(process.version,'v22.14.0');assert.equal(process.env.NODE_COMPAT_M011_MEASURE,undefined);
const prep=JSON.parse(await readFile(join(here,'preparation-results.json'))),root=process.env.NODE_COMPAT_M011_MINIMAL_OUTPUT??join(prep.experiment,'minimal-correctness-v2');
const preview2Adapter=join(prep.project,'host-apis/wasi-0.2.0/preview1-adapter-release/wasi_snapshot_preview1.wasm');
const preview2AdapterSha256=hash(await readFile(preview2Adapter));assert.equal(preview2AdapterSha256,'988224282d03fe0bd3c25b62344aef265b1a8e1f5804bdbc34d6442507fabcc0');
// Both complete installed receipts are required before minimal pairing.
if(!process.argv.includes('--source-preflight'))for(const arm of['baseline','candidate'])assert.equal(JSON.parse(await readFile(join(here,'installed-'+arm+'-results.json'))).state,'private-installed-m011-corpus-passed');
const{loadToolchain}=await import(pathToFileURL(join(prep.project,'tests/node-compat/toolchain.mjs'))),tc=await loadToolchain();
const{loadComponentizer}=await import(pathToFileURL(join(prep.project,'tests/node-compat/componentizer.mjs'))),selected=await loadComponentizer(tc);
const{createProfilePlugin}=await import(pathToFileURL(join(prep.project,'tests/node-compat/profile-bundler.mjs')));
const{transpile,componentWit}=await import(pathToFileURL(tc.require.resolve('@bytecodealliance/jco')));
const old=JSON.parse(await readFile(join(here,'../../matched/correctness-results.json')));
const workload=await readFile(join(here,'../../matched/workload.mjs'),'utf8'),wit=await readFile(join(here,'../../matched/benchmark.wit'),'utf8');
assert.equal(hash(workload),old.sourceFiles.find(file=>file.name==='workload.mjs').sha256);assert.equal(hash(wit),old.worldSha256);
const oracle=createWorkload(NodeBuffer),cases=[];
for(const operation of operations)for(const size of sizes)for(const iterations of[0,1,3])cases.push({operation:operation.id,size,iterations,expected:oracle.batch(operation.id,size,iterations)});
const scenarios=operations.flatMap(operation=>sizes.map(size=>({operation:operation.id,name:operation.name,size,iterations:iterationsFor(size)})));
for(const scenario of scenarios){let value=0x811c9dc5;for(let i=0;i<scenario.iterations;i++)value=Math.imul(value^(scenario.size+(i&255)+((i*17+3)&255)),16777619)>>>0;scenario.expected=value;}
await mkdir(root,{recursive:true});await writeFile(join(root,'package.json'),'{"type":"module"}\n');
try{await symlink(join(tc.directory,'node_modules'),join(root,'node_modules'));}catch(error){if(error.code!=='EEXIST')throw error;}
const entry=`import {Buffer} from 'node:buffer';
import {createWorkload} from 'allocation:private-workload';
if(globalThis.Buffer!==Buffer)throw new Error('Private installed Buffer/global identity');
if(Buffer.isEncoding('base64'))throw new Error('Unexpected JS adapter');
export const batch=createWorkload(Buffer).batch;`;
if(process.argv.includes('--source-preflight')){
  const names=['export-manifest.node-v22.14.0.json','export-manifest.path.node-v22.14.0.json','export-manifest.events.node-v22.14.0.json',
    'export-manifest.string-decoder.node-v22.14.0.json','export-manifest.assert.node-v22.14.0.json','export-manifest.querystring.node-v22.14.0.json','export-manifest.util.node-v22.14.0.json'];
  const manifests=await Promise.all(names.map(async name=>JSON.parse(await readFile(join(prep.project,'builtins/node-compat',name)))));
  const build=await tc.rolldown({input:'allocation:private-entry',platform:'neutral',treeshake:true,transform:{target:'es2016'},
    plugins:[createProfilePlugin(tc.parseAst,{builtinManifests:manifests,virtualModules:{'allocation:private-entry':entry,'allocation:private-workload':workload}})]});
  let chunk;try{const result=await build.generate({format:'esm',codeSplitting:false});assert.equal(result.output.length,1);chunk=result.output[0];}finally{await build.close();}
  assert.deepEqual(chunk.imports,['node:buffer']);assert(!/createBufferModule|reference-kernel|buffer-facade\.mjs|createAllocUnsafeCandidate/.test(chunk.code));
  const report={schema:1,state:'private-minimal-harness-source-preflight-passed',bundleSha256:hash(chunk.code),imports:chunk.imports,
    sourceNodeOracleCases:cases,scenarios,worldSha256:hash(wit),workloadSha256:hash(workload),componentized:false,nativeEngineAdmitted:false,measurementsExecuted:false};
  await writeFile(join(root,'source-preflight.bundle.mjs'),chunk.code);await writeFile(join(here,'minimal-harness-preflight-results.json'),JSON.stringify(report,null,2)+'\n');
  console.log(JSON.stringify({state:report.state,NodeOracleCases:cases.length,preparedTimingScenarios:scenarios.length,componentized:false,measurementsExecuted:false}));process.exit(0);
}
const records=[];let commonBundleSha256;
await writeFile(join(root,'started.json'),JSON.stringify({atUtc:new Date().toISOString(),preview2Adapter,preview2AdapterSha256})+'\n',{flag:'wx'});
for(const arm of['baseline','candidate']){
  const disk=await statfs(root);assert(disk.bavail*disk.bsize>1.5*1024*1024*1024,'Below root1.5GiB cutoff; preserve completed output and request disk plan');
  const admitted=await admitFrozenEngine(arm),directory=join(root,arm);await mkdir(directory,{recursive:true});
  assert.equal(JSON.parse(await readFile(join(here,'installed-'+arm+'-results.json'))).engineSha256,admitted.metadata.engineSha256);
  const build=await tc.rolldown({input:'allocation:private-entry',platform:'neutral',treeshake:true,transform:{target:'es2016'},
    plugins:[createProfilePlugin(tc.parseAst,{builtinManifests:admitted.manifests,virtualModules:{'allocation:private-entry':entry,'allocation:private-workload':workload}})]});
  let chunk;try{const result=await build.generate({format:'esm',codeSplitting:false});assert.equal(result.output.length,1);chunk=result.output[0];}finally{await build.close();}
  assert.deepEqual(chunk.imports,['node:buffer']);assert(!/createBufferModule|reference-kernel|buffer-facade\.mjs|createAllocUnsafeCandidate/.test(chunk.code));
  if(commonBundleSha256)assert.equal(hash(chunk.code),commonBundleSha256,'Same exact guest source in both engine arms');else commonBundleSha256=hash(chunk.code);
  await writeFile(join(directory,'application.bundle.mjs'),chunk.code);
  const{component,interfaceAudit}=await selected.componentize(chunk.code,{engine:admitted.engine,preview2Adapter,witWorld:wit,worldName:'comparison',
    selectedInterfaces:[],disableFeatures:['stdio','random','clocks','http','fetch-event']});
  assert.deepEqual(interfaceAudit.emittedImports,[]);const emittedWit=await componentWit(component);
  assert.equal(emittedWit.replace(/\s+/g,' ').trim(),'package root:component; world root { export batch: func(operation: u32, size: u32, iterations: u32) -> u32; }');
  const componentPath=join(directory,'allocation.component.wasm');await writeFile(componentPath,component);await writeFile(join(directory,'component.wit'),emittedWit);
  const{files}=await transpile(component,{name:'allocation',instantiation:'async'});for(const[name,bytes]of Object.entries(files)){await mkdir(dirname(join(directory,name)),{recursive:true});await writeFile(join(directory,name),bytes);}
  const record={arm,engineSha256:admitted.metadata.engineSha256,sourceRoot:admitted.sourceRoot,componentPath,componentSha256:hash(component),componentBytes:component.length,
    modulePath:join(directory,'allocation.js'),coreFiles:Object.keys(files).filter(name=>name.endsWith('.wasm')),
    transpiledFiles:Object.entries(files).map(([name,bytes])=>({name,sha256:hash(bytes)})),
    bundleSha256:hash(chunk.code),bundleBytes:Buffer.byteLength(chunk.code),bundleImports:chunk.imports,emittedWit,interfaceAudit,emittedImports:[]};
  const instantiate=await loadCompiled(record),instances=[];
  for(let fresh=0;fresh<2;fresh++){
    const instance=await instantiate(),observed=[];
    for(const test of cases){const actual=instance.exports.batch(test.operation,test.size,test.iterations);assert.equal(actual,test.expected);observed.push(actual);}
    for(const size of sizes)assert.equal(instance.exports.batch(4,size,1),(size^0x71c9a32d)>>>0);
    assert.equal(instance.exports.batch(0,64,3),cases.find(test=>test.operation===0&&test.size===64&&test.iterations===3).expected);
    instances.push({freshInstance:fresh,caseCount:observed.length,checksums:observed,zeroNoPoolSizes:sizes,repeatAfterCorpus:true});
  }
  const wasmtime=[];
  for(const operation of operations)for(const size of sizes){
    const test=cases.find(test=>test.operation===operation.id&&test.size===size&&test.iterations===3);
    const result=spawnSync(process.env.NODE_COMPAT_WASMTIME,['run','--invoke',`batch(${operation.id},${size},3)`,componentPath],{encoding:'utf8',timeout:120000});
    assert.equal(result.status,0,result.error?.message??result.stderr);assert.equal(Number(result.stdout.trim()),test.expected);
    wasmtime.push({...test,stdoutSha256:hash(result.stdout),stderr:result.stderr});
  }
  record.correctness={freshJcoInstances:instances,freshWasmtimeCases:wasmtime,measurementsExecuted:false};await admitFrozenEngine(arm);records.push(record);
}
const report={schema:1,state:'private-m011-minimal-pair-correctness-passed',atUtc:new Date().toISOString(),preparationSha256:hash(await readFile(join(here,'preparation-results.json'))),
  records,cases,scenarios,worldSha256:hash(wit),workloadSha256:hash(workload),commonBundleSha256,packaging:selected.provenance,preview2Adapter:{path:preview2Adapter,sha256:preview2AdapterSha256},
  sourceHashes:{runner:hash(await readFile(fileURLToPath(import.meta.url))),workload:hash(workload),publicInstantiationHelper:hash(await readFile(join(here,'../../matched/instantiate.mjs')))},
  sameSourceWorldToolchainCaseInputs:true,nativeModuleRegistration:true,newCppAllocatorKernel:false,measurementsExecuted:false,
  scope:'Private installed JS-facade return-expression pair on matched same-path native builds. Both complete installed corpora required. Public Jco instantiation only; no timing/RSS/memory-length/private access or old timing transfer.'};
await writeFile(join(root,'correctness-results.json'),JSON.stringify(report,null,2)+'\n');await writeFile(join(here,'minimal-pair-results.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({state:report.state,records:records.map(({arm,engineSha256,componentSha256,componentBytes})=>({arm,engineSha256,componentSha256,componentBytes})),emittedImports:[],measurementsExecuted:false}));
