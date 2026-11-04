import {coreExpectationsForValidation} from "../../../../../../../native-preflight.mjs";
// Ordinary Release moving-GC gate. Uses public Buffer calls and the existing
// rooted NODE_COMPAT_GC_STRESS boundaries; no DEBUG, fault or memory inspection.
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { spawnSync } from 'node:child_process';
import { readFile, writeFile, mkdir, symlink } from 'node:fs/promises';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { loadToolchain } from '../../../../toolchain.mjs';
import { loadComponentizer } from '../../../../componentizer.mjs';

import { decodeCliString } from '../../../../foundations/native-scalar-harness.mjs';
import { verifyProductionTicks } from '../preflight.mjs';

assert.equal(process.version, 'v22.14.0');
const here=resolve(dirname(fileURLToPath(import.meta.url)),'../../../../foundation-alloc-unsafe/installed'), repository=resolve(here,'../../../..');
const engine=resolve(process.env.NODE_COMPAT_ENGINE), sourceRoot=resolve(process.env.NODE_COMPAT_ENGINE_SOURCE_ROOT);
const output=resolve(process.env.NODE_COMPAT_ALLOCATOR_GC_OUTPUT);
const hash=value=>createHash('sha256').update(value).digest('hex');
await mkdir(output,{recursive:true});
const reportPath=join(output,'results.json');
try{await readFile(reportPath);throw new Error('Choose a fresh allocator GC output');}
catch(error){if(error.code!=='ENOENT')throw error;}
const metadata=JSON.parse(await readFile(engine+'.build.json'));
assert.equal(hash(await readFile(engine)),metadata.engineSha256);
assert.equal(metadata.observedCMakeOptions.CMAKE_BUILD_TYPE,'Release');
assert.equal(metadata.observedCMakeOptions.NODE_COMPAT_GC_STRESS,'ON');
assert.equal(metadata.gcStress,true);assert.equal(metadata.oomTesting,false);
assert.equal(metadata.strictEventExceptionPolicy.version,'sm-uncaught-event-v3-protected-abort-v2-private-ticks-v1-classic-streams-source-v1');
assert.equal(metadata.strictEventExceptionPolicy.embeddingBoundaryPatchSha256,
  '84a91c1f74dbdcf653ef7ced5fa2876abffc32d5da591a1ca2df4a4908406ad2');
for(const item of metadata.sourceManifest)assert.equal(hash(await readFile(join(sourceRoot,item.path))),item.sha256,item.path);
const core=coreExpectationsForValidation(metadata,{sourceRoot});
assert.equal(core.coreVersion,'sm-node-22.14.0-m0.11');
assert.equal(core.allocUnsafePolicy,'zeroed-no-pool-direct-u8-v1');
const admitted=await verifyProductionTicks({gcStress:true});
assert.equal(admitted.report.engineSha256,metadata.engineSha256);
assert.equal(admitted.sourceRoot,sourceRoot);
const pins=admitted.pin;
assert.equal(pins.state,'reviewed-consumers355-native-build-for-validation');
assert.equal(hash(await readFile(pins.freezeReceiptPath)),pins.freezeReceiptSha256);
assert.equal(metadata.engineSha256,pins.engineSha256);
assert.equal(hash(await readFile(engine+'.build.json')),pins.receiptSha256);
assert.equal(metadata.engineBytes,pins.engineBytes);
assert.equal(metadata.buildRecipeSha256,pins.recipeSha256);
assert.deepEqual(core.sourceHashes,pins.coreSources);
assert.equal(metadata.cmakeCacheSha256,pins.cmakeCacheSha256);
assert.equal(metadata.compileCommandsSha256,pins.compileCommandsSha256);
const commandsPath=pins.commandsPath;
if(process.env.NODE_COMPAT_GC_COMPILE_COMMANDS)assert.equal(resolve(process.env.NODE_COMPAT_GC_COMPILE_COMMANDS),commandsPath,'Use frozen GC compile commands');
const commandBytes=await readFile(commandsPath);assert.equal(hash(commandBytes),metadata.compileCommandsSha256);
const command=JSON.parse(commandBytes).find(item=>item.file.endsWith('/builtins/node-compat/buffer.cpp'));
assert(command.command.split(' ').includes('-DNODE_COMPAT_GC_STRESS=1'));
const toolchain=await loadToolchain(), selected=await loadComponentizer(toolchain);
try{await symlink(join(toolchain.directory,'node_modules'),join(output,'node_modules'));}
catch(error){if(error.code!=='EEXIST')throw error;}
await writeFile(join(output,'package.json'),' {"type":"module"}\n');
const source=`import buffer,{Buffer}from'node:buffer';
const snapshot=Buffer.allocUnsafe(32.9),snapshotBacking=snapshot.buffer,snapshotView=snapshot.subarray(4,12);
for(let i=0;i<snapshot.length;i++)snapshot[i]=i;
let calls=0;
function check(value,message){if(!value)throw new Error(message);}
export function run(){
  const a=Buffer.allocUnsafe(127.9),backing=a.buffer,view=a.subarray(3,8),empty=new Buffer.allocUnsafe(0);
  check([...a].every(byte=>byte===0),'zero initialization');a[3]=91;
  let roundtrips=0;for(let i=0;i<8;i++){
    check(Buffer.from('00017fff80','hex').toString('hex')==='00017fff80','native hex');roundtrips++;
  }
  check(buffer.Buffer===Buffer&&Buffer===globalThis.Buffer,'canonical constructor');
  check(Buffer.isBuffer(a)&&Buffer.isBuffer(view)&&Buffer.isBuffer(snapshot)&&Buffer.isBuffer(snapshotView)&&Buffer.isBuffer(empty),'private brands');
  check(a.length===127&&a.byteOffset===0&&backing.byteLength===127&&a.buffer===backing,'owned backing');
  check(view.buffer===backing&&view.byteOffset===3&&view.length===5&&view[0]===91,'shared view');
  check(empty.length===0&&empty.byteOffset===0&&empty.buffer.byteLength===0&&empty.buffer!==backing,'empty backing');
  check(snapshot.buffer===snapshotBacking&&snapshotView.buffer===snapshotBacking&&snapshotView.byteOffset===4,'snapshot backing');
  view[0]++;snapshotView[0]++;
  check(a[3]===92&&snapshot[4]===5+calls,'view writes');
  return JSON.stringify({calls:++calls,roundtrips,brands:5,ownedLength:a.length,viewOffset:view.byteOffset,snapshotByte:snapshot[4]});
}`;
const adapter=join(repository,'host-apis/wasi-0.2.0/preview1-adapter-release/wasi_snapshot_preview1.wasm');
assert.equal(hash(await readFile(adapter)),'988224282d03fe0bd3c25b62344aef265b1a8e1f5804bdbc34d6442507fabcc0');
const {component,interfaceAudit}=await selected.componentize(source,{engine,preview2Adapter:adapter,
  witWorld:'package test:allocator-gc; world test { export run: func() -> string; }',worldName:'test',
  disableFeatures:['stdio','random','clocks','http','fetch-event'],selectedInterfaces:[]});
assert.deepEqual(interfaceAudit.emittedImports,[]);
const componentPath=join(output,'allocator-gc.component.wasm');await writeFile(componentPath,component);
await writeFile(join(output,'source.mjs'),source);
const {transpile,componentWit}=await import(pathToFileURL(toolchain.require.resolve('@bytecodealliance/jco')));
const {files}=await transpile(component,{name:'allocator_gc'});
for(const[name,bytes]of Object.entries(files)){await mkdir(dirname(join(output,name)),{recursive:true});await writeFile(join(output,name),bytes);}
const instance=await import(pathToFileURL(join(output,'allocator_gc.js'))),calls=[];
const expected=call=>({calls:call,roundtrips:8,brands:5,ownedLength:127,viewOffset:3,snapshotByte:4+call});
for(let call=1;call<=3;call++){const result=JSON.parse(await instance.run());assert.deepEqual(result,expected(call));calls.push(result);}
const host=spawnSync(process.env.NODE_COMPAT_WASMTIME,['run','--invoke','run()',componentPath],{encoding:'utf8',timeout:120000,maxBuffer:2*1024*1024});
assert.equal(host.status,0,host.stderr);const observed=JSON.parse(decodeCliString(host.stdout.trim()));assert.deepEqual(observed,expected(1));
for(const item of metadata.sourceManifest)assert.equal(hash(await readFile(join(sourceRoot,item.path))),item.sha256,item.path);
await admitted.recheck();
const report={schema:1,state:'installed-m0.11-ordinary-release-moving-gc-pass',engineSha256:metadata.engineSha256,
  engineReceiptSha256:hash(await readFile(engine+'.build.json')),sourceFilesVerified:metadata.sourceManifest.length,
  sourceRoot,coreExpectations:core,productionTickAdmission:admitted.report,fixedGCAdmission:{variant:admitted.report.variant,pinState:pins.state,pins,freezeReceiptPath:pins.freezeReceiptPath,freezeReceiptSha256:pins.freezeReceiptSha256,scope:'Actual consumers355 freeze pin; genuine consumersBootstrapPreflight/recheck owns the authority bytes. No old pin-schema projection.'},runnerSha256:hash(await readFile(fileURLToPath(import.meta.url))),
  sourceSha256:hash(source),componentSha256:hash(component),componentBytes:component.length,interfaceAudit,
  emittedWit:await componentWit(component),componentizerProvenance:selected.provenance,compileCommand:command.command,
  calls,wasmtime:{observed,stderr:host.stderr},
  scope:'Three retained calls/fresh Wasmtime with public allocation/view operations around eight native hex roundtrips. Existing rooted Shrink instrumentation only; no fault/DEBUG/raw memory, performance or exhaustive GC claim.'};
await writeFile(reportPath,JSON.stringify(report,null,2)+'\n');
await writeFile(join(output,'allocator-gc-summary.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({state:report.state,engineSha256:metadata.engineSha256,componentSha256:report.componentSha256,imports:[]}));
