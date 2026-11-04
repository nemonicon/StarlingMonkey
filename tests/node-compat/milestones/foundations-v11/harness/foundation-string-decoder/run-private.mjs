// Only the source-audited PRIVATE fixed decoder engine may execute these cases.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFile,writeFile,mkdir,symlink} from 'node:fs/promises';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {spawnSync} from 'node:child_process';
import {loadToolchain} from '../toolchain.mjs';
import {loadComponentizer} from '../componentizer.mjs';
import {selectedManifestsForEngine} from '../module-selection.mjs';
import {bundleProfile} from '../profile-bundler.mjs';
const here=dirname(fileURLToPath(import.meta.url));
const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
assert.equal(process.version,'v22.14.0');
assert(process.env.NODE_COMPAT_ENGINE&&process.env.NODE_COMPAT_WASMTIME,'Explicit private engine and stock Wasmtime42 paths required');
const engine=resolve(process.env.NODE_COMPAT_ENGINE),wasmtime=resolve(process.env.NODE_COMPAT_WASMTIME);
const output=resolve(process.env.NODE_COMPAT_DECODER_OUTPUT??'/tmp/starling-node-compat/text-decoder-private/results-v1');
const metadata=JSON.parse(await readFile(engine+'.build.json'));
const audit=metadata.privateTextDecoderCandidate;
assert(audit,'Only a verified private decoder candidate may run the mutation/detach cases');
assert.equal(hash(await readFile(engine)),metadata.engineSha256);
const pins=JSON.parse(await readFile(join(here,'text-decoder-candidate-pins.json')));
assert.equal(audit.candidateSha256,pins.candidateSha256);
assert.equal(audit.onlyChangedNativeSource,'builtins/web/text-codec/text-decoder.cpp');
assert.equal(metadata.observedCMakeOptions.CMAKE_BUILD_TYPE,'Release');
assert.equal(metadata.gcStress,false);assert.equal(metadata.oomTesting,false);
for(const entry of metadata.sourceManifest)assert.equal(hash(await readFile(join(audit.sourceRoot,entry.path))),entry.sha256,entry.path);
const builtinManifests=selectedManifestsForEngine(metadata,{sourceRoot:audit.sourceRoot});
const toolchain=await loadToolchain();
const {componentize,provenance}=await loadComponentizer(toolchain);
const {transpile,componentWit}=await import(pathToFileURL(toolchain.require.resolve('@bytecodealliance/jco')));
const version=spawnSync(wasmtime,['--version'],{encoding:'utf8'});assert.equal(version.status,0);assert.match(version.stdout,/^wasmtime 42\.0\.1\b/);
const corpus=JSON.parse(await readFile(join(here,'component-corpus.json')));
await mkdir(output,{recursive:true});await writeFile(join(output,'package.json'),'{"type":"module"}\n');
try{await symlink(join(toolchain.directory,'node_modules'),join(output,'node_modules'),'dir');}catch(error){if(error.code!=='EEXIST')throw error;}
const bundled=await bundleProfile({...toolchain,input:join(here,'component.mjs'),builtinManifests,
  virtualModules:{'node-compat:string-decoder-oracles':'export default '+JSON.stringify(corpus)+';'}});
assert.deepEqual(bundled.imports,['node:buffer']);
assert(!bundled.moduleIds.some(id=>/node_modules|buffer-facade|reference-kernel/.test(id)),'Actual registered native Buffer must be selected');
await writeFile(join(output,'application.bundle.mjs'),bundled.code);
const {component,interfaceAudit}=await componentize(bundled.code,{engine,
  witWorld:await readFile(join(here,'profile.wit'),'utf8'),worldName:'profile',
  disableFeatures:['stdio','random','clocks','http','fetch-event'],selectedInterfaces:[]});
const path=join(output,'string-decoder.component.wasm');await writeFile(path,component);
const wit=await componentWit(component);assert.deepEqual(wit.split('\n').filter(line=>/^\s*import /.test(line)),[]);
await writeFile(join(output,'string-decoder.wit'),wit);
const {files}=await transpile(component,{name:'string-decoder'});
for(const[file,bytes]of Object.entries(files)){const target=join(output,file);await mkdir(dirname(target),{recursive:true});await writeFile(target,bytes);}
const instance=await import(pathToFileURL(join(output,'string-decoder.js')));
function check(report,calls){assert(!report.failure,JSON.stringify(report.failure));assert.equal(report.passed,true);assert.equal(report.calls,calls);
  assert.equal(report.genericCases,corpus.decoderCases.length);assert.equal(report.sequences,corpus.sequences.length);
  assert.equal(report.preservedOrderingDeviations,2);
  assert.equal(report.writes,corpus.sequences.reduce((sum,value)=>sum+value.chunks.length,0));
  assert.equal(report.mutationChecks,2);assert(report.snapshotResumption&&report.identities);}
const calls=[];
for(let index=1;index<=3;index++){
  const report=JSON.parse(await instance.run());calls.push(report);
  await writeFile(join(output,'calls.json'),JSON.stringify(calls,null,2)+'\n');
  check(report,index);
}
const host=spawnSync(wasmtime,['run','--invoke','run()',path],{encoding:'utf8',timeout:180000,maxBuffer:1024*1024});
assert.equal(host.status,0,host.error?.message||host.stderr);
const wasmtimeReport=JSON.parse(JSON.parse(host.stdout.trim().replace(/\\u\{([0-9a-fA-F]+)\}/g,(_,hex)=>String.fromCodePoint(parseInt(hex,16)))));
check(wasmtimeReport,1);
const result={schema:1,atUtc:new Date().toISOString(),node:process.version,scope:'PRIVATE ordinary API decoder candidate and unintegrated StringDecoder prototype only; no fault injection or unsafe old-native probes',
  engine,engineSha256:metadata.engineSha256,metadata,componentizer:provenance,
  component:{path,sha256:hash(component),bytes:component.length,emittedWit:wit,emittedImports:[],interfaceAudit},
  bundle:{imports:bundled.imports,moduleIds:bundled.moduleIds},calls,wasmtime:version.stdout.trim(),wasmtimeReport,
  preservedOrderingDeviations:corpus.deviations,
  sourceManifest:await Promise.all(['prototype.mjs','decoder-cases.mjs','component.mjs','profile.wit','run-private.mjs','make-corpus.mjs','component-corpus.json'].map(async path=>({path,sha256:hash(await readFile(join(here,path)))}))),
  limitations:['No production decoder changes or registered node:string_decoder module.',
    'Shared inputs rejected in private candidate; SharedArrayBuffer is normally unavailable in guest.',
    'Existing fatal-decoding error lifecycle, full WebIDL coercion and Rust infallible Box allocation failures remain outside this ownership patch.',
    'No performance or allocation-failure recovery claim.']};
await writeFile(join(output,'results.json'),JSON.stringify(result,null,2)+'\n');
await writeFile(join(here,'private-results.json'),JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify({output,engineSha256:metadata.engineSha256,genericCases:corpus.decoderCases.length,
  sequences:corpus.sequences.length,writes:wasmtimeReport.writes,zeroImports:true,wasmtimePassed:true},null,2));
