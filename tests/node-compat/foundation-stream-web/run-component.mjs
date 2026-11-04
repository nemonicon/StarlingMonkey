import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFile,writeFile,mkdir,symlink} from 'node:fs/promises';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {spawnSync} from 'node:child_process';
import {loadToolchain} from '../toolchain.mjs';
import {loadComponentizer} from '../componentizer.mjs';
import {bundleProfile} from '../profile-bundler.mjs';
import {selectedManifestsForEngine} from '../module-selection.mjs';
assert.equal(process.version,'v22.14.0');
assert(process.env.NODE_COMPAT_ENGINE&&process.env.NODE_COMPAT_WASMTIME);
const here=dirname(fileURLToPath(import.meta.url)),sourceRoot=resolve(process.env.NODE_COMPAT_ENGINE_SOURCE_ROOT??resolve(here,'../../..'));
const engine=resolve(process.env.NODE_COMPAT_ENGINE),wasmtime=resolve(process.env.NODE_COMPAT_WASMTIME);
const output=resolve(process.env.NODE_COMPAT_STREAM_WEB_OUTPUT??'/tmp/starling-node-compat/foundations-v6/stream-web-probe');
const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
const metadata=JSON.parse(await readFile(engine+'.build.json'));
assert.equal(hash(await readFile(engine)),metadata.engineSha256);
assert.equal(metadata.observedCMakeOptions.CMAKE_BUILD_TYPE,'Release');assert.equal(metadata.oomTesting,false);
for(const entry of metadata.sourceManifest)assert.equal(hash(await readFile(join(sourceRoot,entry.path))),entry.sha256,entry.path);
const toolchain=await loadToolchain(),{componentize,provenance}=await loadComponentizer(toolchain);
const{componentWit,transpile}=await import(pathToFileURL(toolchain.require.resolve('@bytecodealliance/jco')));
const version=spawnSync(wasmtime,['--version'],{encoding:'utf8'});assert.equal(version.status,0);assert.match(version.stdout,/^wasmtime 42\.0\.1\b/);
await mkdir(output,{recursive:true});await writeFile(join(output,'package.json'),'{"type":"module"}\n');
try{await symlink(join(toolchain.directory,'node_modules'),join(output,'node_modules'),'dir');}catch(error){if(error.code!=='EEXIST')throw error;}
const bundled=await bundleProfile({...toolchain,input:join(here,'component.mjs'),builtinManifests:selectedManifestsForEngine(metadata,{sourceRoot})});
assert.deepEqual(bundled.imports,[]);
await writeFile(join(output,'application.bundle.mjs'),bundled.code);
const{component,interfaceAudit}=await componentize(bundled.code,{engine,witWorld:await readFile(join(here,'profile.wit'),'utf8'),worldName:'profile',
  disableFeatures:['stdio','random','clocks','http','fetch-event'],selectedInterfaces:[]});
const path=join(output,'streams.component.wasm');await writeFile(path,component);
const wit=await componentWit(component);assert.deepEqual(wit.split('\n').filter(line=>/^\s*import /.test(line)),[]);
await writeFile(join(output,'streams.wit'),wit);
const{files}=await transpile(component,{name:'streams'});
for(const[file,bytes]of Object.entries(files)){const target=join(output,file);await mkdir(dirname(target),{recursive:true});await writeFile(target,bytes);}
const instance=await import(pathToFileURL(join(output,'streams.js'))),calls=[];
for(let index=1;index<=2;index++){
  const report=JSON.parse(await instance.run());calls.push(report);
  await writeFile(join(output,'calls.json'),JSON.stringify(calls,null,2)+'\n');
  assert(!report.failure,JSON.stringify(report.failure));assert.equal(report.calls,index);assert.equal(report.passed,true);assert.equal(report.cases.length,11);
}
const host=spawnSync(wasmtime,['run','--invoke','run()',path],{encoding:'utf8',timeout:120000,maxBuffer:1024*1024});
await writeFile(join(output,'wasmtime.log'),JSON.stringify(host,null,2)+'\n');
assert.equal(host.status,0,host.error?.message||host.stderr);
const wasmtimeReport=JSON.parse(JSON.parse(host.stdout.trim().replace(/\\u\{([0-9a-fA-F]+)\}/g,(_,hex)=>String.fromCodePoint(parseInt(hex,16)))));
assert(!wasmtimeReport.failure,JSON.stringify(wasmtimeReport.failure));assert.equal(wasmtimeReport.passed,true);
assert.deepEqual(wasmtimeReport,calls[0],'Same ordinary API observations on both execution backends');
const node=JSON.parse(await readFile(join(here,'node-results.json'))),differences=[];
assert.deepEqual(calls[0].exports,node.exports);
for(const expected of node.cases){
  const actual=calls[0].cases.find(value=>value.name===expected.name);assert(actual);
  if(JSON.stringify(actual)!==JSON.stringify(expected))differences.push({name:expected.name,node:expected,starlingMonkey:actual});
}
const result={schema:1,atUtc:new Date().toISOString(),scope:'ISOLATED namespace composition and bounded ordinary public API observations; not registered node:stream/web support or broad parity',
  engine,engineSha256:metadata.engineSha256,sourceRoot,metadata,componentizer:provenance,component:{path,bytes:component.length,sha256:hash(component),emittedImports:[],emittedWit:wit,interfaceAudit},
  bundle:{imports:[],moduleIds:bundled.moduleIds},calls,wasmtime:version.stdout.trim(),wasmtimeReport,node,differences,
  sourceManifest:await Promise.all(['prototype.mjs','cases.mjs','component.mjs','inventory.mjs','profile.wit','run-component.mjs','node-results.json'].map(async path=>({path,sha256:hash(await readFile(join(here,path)))}))),
  limitations:['No production manifest, builtin registration or build changes.',
    'Missing exports are finite explicit throwing constructors in this isolated namespace probe; hidden native constructors still require correct admission.',
    'No CompressionStream/DecompressionStream transform invocation; source ownership/constructor gaps remain unverified.',
    'No detached/shared/RAB lifetime probes, forced GC, raw-memory, fault injection or timing claims.',
    'Only eleven bounded ordinary cases are observed; missing native methods, transfer and full conformance remain explicit follow-up gates.']};
await writeFile(join(output,'results.json'),JSON.stringify(result,null,2)+'\n');
await writeFile(join(here,'component-results.json'),JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify({output,zeroImports:true,exports:node.exports.length,cases:node.cases.length,differentCases:differences.map(value=>value.name),wasmtimePassed:true},null,2));
