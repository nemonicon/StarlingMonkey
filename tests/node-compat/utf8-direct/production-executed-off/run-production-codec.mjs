// Ordinary Release production gate. Do not use this for historical/private engines.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {dirname,join,resolve,relative} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {spawnSync} from 'node:child_process';
import {loadToolchain} from '../toolchain.mjs';
import {loadComponentizer} from '../componentizer.mjs';
import {bundleProfile} from '../profile-bundler.mjs';
import {selectedManifestsForEngine} from '../module-selection.mjs';

const here=dirname(fileURLToPath(import.meta.url)),repository=resolve(here,'../../..');
const hash=data=>createHash('sha256').update(data).digest('hex');
assert.equal(process.version,'v22.14.0');assert.deepEqual(process.execArgv,[]);assert(!process.env.NODE_OPTIONS);
assert(process.env.NODE_COMPAT_ENGINE,'Select the actual production engine explicitly');
const pins=JSON.parse(await readFile(join(here,'production-codec-pins.json')));
const engine=resolve(process.env.NODE_COMPAT_ENGINE),metadataBytes=await readFile(engine+'.build.json'),metadata=JSON.parse(metadataBytes);
const engineBytes=await readFile(engine);assert.equal(hash(engineBytes),metadata.engineSha256);
assert.equal(engineBytes.length,metadata.engineBytes);
for(const[field,value]of Object.entries({profileEnabled:true,gcStress:false,oomTesting:false,strictInitialization:true,debuggerEnabled:false,wptSupportEnabled:false,sourceInputsCapturedBeforeBuild:true,componentizeSourcesCapturedBeforeBuild:true,buildRecipeCheckedBeforeAndAfterBuild:true}))assert.equal(metadata[field],value,field);
assert(!metadata.utf8DirectExperiment,'Private experiment engines are outside this production gate');
for(const[field,value]of Object.entries({CMAKE_BUILD_TYPE:'Release',WEVAL:'OFF',USE_WASM_OPT:'ON',ENABLE_BUILTIN_NODE_COMPAT:'ON',ENABLE_JS_DEBUGGER:'OFF',ENABLE_BUILTIN_WPT_SUPPORT:'OFF',NODE_COMPAT_GC_STRESS:'OFF',NODE_COMPAT_OOM_TESTING:'OFF'}))assert.equal(metadata.observedCMakeOptions?.[field],value,field);
assert.equal(metadata.archivePins.spiderMonkeySha256,pins.spiderMonkeyReleaseArchiveSha256);
assert(Array.isArray(metadata.sourceManifest));assert.equal(metadata.sourceManifest.length,pins.nativeSourceCount);
const manifest=new Map(metadata.sourceManifest.map(entry=>[entry.path,entry.sha256]));assert.equal(manifest.size,metadata.sourceManifest.length);
assert.equal(manifest.get(pins.productionEncoderPath),pins.productionEncoderSha256,'Reject earlier encoder before any zero/detached/OOB case');
assert(!metadata.sourceManifest.some(entry=>entry.path.includes('direct-testing')),'No private codec test helper');
const sourceRoot=resolve(process.env.NODE_COMPAT_ENGINE_SOURCE_ROOT??'/tmp/starling-node-compat/foundations-v5/native-freeze/source');
async function verifyNativeSources(){
  for(const entry of metadata.sourceManifest){
    const path=resolve(sourceRoot,entry.path);assert(!relative(sourceRoot,path).startsWith('..'),'Source path escapes freeze');
    assert.equal(hash(await readFile(path)),entry.sha256,entry.path);
  }
}
await verifyNativeSources();
// Verify actual captured build inputs, rather than trusting requested flags.
const cache=await readFile(metadata.cmakeCachePath),commandsBytes=await readFile(metadata.compileCommandsPath);
assert.equal(hash(cache),metadata.cmakeCacheSha256);assert.equal(hash(commandsBytes),metadata.compileCommandsSha256);
const commands=JSON.parse(commandsBytes),encoderCommands=commands.filter(entry=>entry.file.endsWith('/'+pins.productionEncoderPath));
assert.equal(encoderCommands.length,1);const encoderCommand=encoderCommands[0];
assert(!/(?:STARLING_UTF8_DIRECT_|(?:^|\s)-DDEBUG(?:=|\s|$))/.test(encoderCommand.command),'No private codec/DEBUG instrumentation');
assert(encoderCommand.command.includes('-DNDEBUG'));assert(encoderCommand.command.includes('-O3'));
assert.equal(hash(await readFile(encoderCommand.file)),pins.productionEncoderSha256,'Actual compiler input must still match captured production source');

const baselineOracleBytes=await readFile(join(here,'node-oracle-results.json')),baselineOracle=JSON.parse(baselineOracleBytes);
assert.equal(hash(baselineOracleBytes),pins.originalNodeOracleReceiptSha256);
assert.equal(hash(await readFile(join(here,'codec-cases.mjs'))),pins.originalCodecCasesSha256);
assert.equal(baselineOracle.sharedCasesSha256,pins.originalCodecCasesSha256);
const extrasOracleBytes=await readFile(join(here,'production-extra-node-oracle-results.json')),extrasOracle=JSON.parse(extrasOracleBytes);
assert.equal(hash(extrasOracleBytes),pins.extraNodeOracleReceiptSha256);
assert.equal(hash(await readFile(join(here,'production-extra-cases.mjs'))),pins.extraCasesSha256);
assert.equal(extrasOracle.sharedCasesSha256,pins.extraCasesSha256);
assert.equal(extrasOracle.node,'v22.14.0');assert.equal(extrasOracle.sourcePolicy.expectedPolicy,'node-strict-string');
assert.equal(hash(await readFile(process.execPath)),extrasOracle.executableSha256);

const output=resolve(process.env.NODE_COMPAT_PRODUCTION_CODEC_OUTPUT??'/tmp/starling-node-compat/foundations-v5/codec');
await mkdir(output,{recursive:true});await writeFile(join(output,'started.json'),JSON.stringify({atUtc:new Date().toISOString(),engine,engineSha256:metadata.engineSha256})+'\n',{flag:'wx'});
const sourcePaths=['codec-cases.mjs','node-oracle-results.json','production-extra-cases.mjs','production-extra-node-oracle.mjs','production-extra-node-oracle-results.json','production-codec-component.mjs','run-production-codec.mjs','production-codec-pins.json','profile.wit','../componentizer.mjs','../toolchain.mjs','../profile-bundler.mjs','../module-selection.mjs','../capability-policy.mjs'];
const sources=[];
for(const path of sourcePaths){const absolute=resolve(here,path),bytes=await readFile(absolute),saved=join(output,'source',relative(repository,absolute));await mkdir(dirname(saved),{recursive:true});await writeFile(saved,bytes);sources.push({path:relative(repository,absolute),sha256:hash(bytes),saved});}
await writeFile(join(output,'engine.build.json'),metadataBytes);
await writeFile(join(output,'CMakeCache.txt'),cache);await writeFile(join(output,'compile_commands.json'),commandsBytes);
await writeFile(join(output,'package.json'),'{"type":"module"}\n');
const tc=await loadToolchain(),selected=await loadComponentizer(tc),manifests=selectedManifestsForEngine(metadata,{sourceRoot});
assert.equal(selected.provenance.selection,'patched-import-i32-clock-v2');
const bundle=await bundleProfile({rolldown:tc.rolldown,parseAst:tc.parseAst,input:join(here,'production-codec-component.mjs'),builtinManifests:manifests});
assert.deepEqual(bundle.imports,['node:buffer']);await writeFile(join(output,'bundle.mjs'),bundle.code);
const world=await readFile(join(here,'profile.wit'),'utf8');
const{component,interfaceAudit}=await selected.componentize(bundle.code,{engine,witWorld:world,worldName:'profile',disableFeatures:['stdio','random','clocks','http','fetch-event'],selectedInterfaces:[],preview2Adapter:join(sourceRoot,'host-apis/wasi-0.2.0/preview1-adapter-release/wasi_snapshot_preview1.wasm')});
const componentPath=join(output,'production-codec.component.wasm');await writeFile(componentPath,component);
const{componentWit,transpile}=await import(pathToFileURL(tc.require.resolve('@bytecodealliance/jco'))),wit=await componentWit(component);
assert.deepEqual(wit.split('\n').filter(line=>/^\s*import /.test(line)),[]);await writeFile(join(output,'component.wit'),wit);
const{files}=await transpile(component,{name:'production-codec'});
for(const[name,data]of Object.entries(files)){const path=join(output,name);await mkdir(dirname(path),{recursive:true});await writeFile(path,data);}
function validate(report,call){
  assert.equal(report.calls,call);assert(!report.failure,report.failure??'guest failure');
  assert.equal(report.baseline.caseCount,8);assert.equal(report.baseline.assertionCount,77769);assert.equal(report.baseline.observationCount,78);
  assert.deepEqual(report.baseline.cases,baselineOracle.cases);assert.equal(report.baseline.gcBoundaryCalls,0);
  for(const field of ['caseCount','assertionCount','observationCount','capabilities','skipped','cases'])assert.deepEqual(report.extras[field],extrasOracle[field],field);
  assert.equal(report.sourcePolicy.expectedPolicy,'starling-coerce');assert.equal(report.sourcePolicy.caseCount,7);assert.equal(report.sourcePolicy.assertionCount,13);
  assert(report.sourcePolicy.cases.every(item=>item.passed));
  assert.deepEqual(report.snapshot,{bytes:11,backingIdentityPreserved:true,offset:0,independentOutput:true});
}
const guest=await import(pathToFileURL(join(output,'production-codec.js'))),reports=[];
for(let call=1;call<=3;call++){const report=JSON.parse(guest.run());reports.push(report);await writeFile(join(output,'progress.json'),JSON.stringify(reports,null,2)+'\n');validate(report,call);}
const wasmtime=resolve(process.env.NODE_COMPAT_WASMTIME??'/tmp/starling-node-compat/bin/wasmtime-v42.0.1-aarch64-macos/wasmtime');
const version=spawnSync(wasmtime,['--version'],{encoding:'utf8'});assert.equal(version.status,0);assert(version.stdout.startsWith('wasmtime 42.0.1'));
const host=spawnSync(wasmtime,['run','--invoke','run()',componentPath],{encoding:'utf8',timeout:120000,maxBuffer:2*1024*1024});
await writeFile(join(output,'wasmtime.stdout'),host.stdout??'');await writeFile(join(output,'wasmtime.stderr'),host.stderr??'');
assert.equal(host.status,0,host.error?.message??host.stderr);
const wave=host.stdout.trim().replace(/\\u\{([0-9a-fA-F]+)\}/g,(_,number)=>String.fromCodePoint(parseInt(number,16))),hostReport=JSON.parse(JSON.parse(wave));validate(hostReport,1);
await verifyNativeSources();
for(const entry of sources)assert.equal(hash(await readFile(join(repository,entry.path))),entry.sha256,'Validation source changed during run: '+entry.path);
assert.equal(hash(await readFile(engine)),metadata.engineSha256);assert.equal(hash(await readFile(engine+'.build.json')),hash(metadataBytes));
const report={schemaVersion:1,atUtc:new Date().toISOString(),engine,engineSha256:metadata.engineSha256,engineBytes:engineBytes.length,engineMetadataSha256:hash(metadataBytes),sourceRoot,nativeSourcesVerifiedBeforeAndAfter:metadata.sourceManifest.length,productionEncoder:{path:pins.productionEncoderPath,sha256:pins.productionEncoderSha256,actualCompileCommand:encoderCommand.command},buildConfiguration:{observedCMakeOptions:metadata.observedCMakeOptions,cmakeCacheSha256:hash(cache),compileCommandsSha256:hash(commandsBytes)},packaging:selected.provenance,bundleSha256:hash(bundle.code),worldSha256:hash(world),componentPath,componentBytes:component.length,componentSha256:hash(component),emittedImports:[],emittedWit:wit,interfaceAudit,originalNodeOracleReceiptSha256:hash(baselineOracleBytes),extraNodeOracleReceiptSha256:hash(extrasOracleBytes),sourceFiles:sources,sourcesCapturedBeforeAndVerifiedAfter:true,reports,wasmtime:{executable:wasmtime,executableSha256:hash(await readFile(wasmtime)),version:version.stdout.trim(),arguments:['run','--invoke','run()',componentPath],report:hostReport},knownDeviation:{api:'TextEncoder.encodeInto source conversion',nodePolicy:extrasOracle.sourcePolicy,starlingPolicy:reports[0].sourcePolicy,claim:'Policy-specific checks passed separately; this existing source-coercion difference is not claimed compatible.'},passed:true,scope:'Ordinary production Release component calls only. Original immutable 77,769-assertion suite plus new valid public API cases; no DEBUG, fault simulation, raw memory, private telemetry, GC extension or performance measurement. Historical private performance and blocked OOM evidence remain separate.'};
await writeFile(join(output,'results.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({engineSha256:report.engineSha256,componentSha256:report.componentSha256,baseline:[8,77769,78],extras:[extrasOracle.caseCount,extrasOracle.assertionCount,extrasOracle.observationCount],sourcePolicy:'existing deviation preserved and explicitly validated',retainedCalls:3,freshWasmtimeCalls:1,emittedImports:[],passed:true,output},null,2));
