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
assert.equal(process.version,'v22.14.0');assert(process.env.NODE_COMPAT_ENGINE&&process.env.NODE_COMPAT_WASMTIME);
const here=dirname(fileURLToPath(import.meta.url)),sourceRoot=resolve(process.env.NODE_COMPAT_ENGINE_SOURCE_ROOT);
const engine=resolve(process.env.NODE_COMPAT_ENGINE),wasmtime=resolve(process.env.NODE_COMPAT_WASMTIME);
const output=resolve(process.env.NODE_COMPAT_STREAM_CONSTRUCTOR_OUTPUT??'/tmp/starling-node-compat/foundations-v6/stream-web-constructors');
const hash=bytes=>createHash('sha256').update(bytes).digest('hex'),metadata=JSON.parse(await readFile(engine+'.build.json'));
assert.equal(hash(await readFile(engine)),metadata.engineSha256);assert.equal(metadata.observedCMakeOptions.CMAKE_BUILD_TYPE,'Release');
assert.equal(metadata.oomTesting,false);
for(const entry of metadata.sourceManifest)assert.equal(hash(await readFile(join(sourceRoot,entry.path))),entry.sha256,entry.path);
const toolchain=await loadToolchain(),{componentize,provenance}=await loadComponentizer(toolchain);
const{componentWit,transpile}=await import(pathToFileURL(toolchain.require.resolve('@bytecodealliance/jco')));
const version=spawnSync(wasmtime,['--version'],{encoding:'utf8'});assert.equal(version.status,0);assert.match(version.stdout,/^wasmtime 42\.0\.1\b/);
await mkdir(output,{recursive:true});await writeFile(join(output,'package.json'),'{"type":"module"}\n');
try{await symlink(join(toolchain.directory,'node_modules'),join(output,'node_modules'),'dir');}catch(error){if(error.code!=='EEXIST')throw error;}
const bundled=await bundleProfile({...toolchain,input:join(here,'constructors.mjs'),builtinManifests:selectedManifestsForEngine(metadata,{sourceRoot})});
assert.deepEqual(bundled.imports,[]);await writeFile(join(output,'application.bundle.mjs'),bundled.code);
const{component,interfaceAudit}=await componentize(bundled.code,{engine,witWorld:await readFile(join(here,'profile.wit'),'utf8'),worldName:'profile',
  disableFeatures:['stdio','random','clocks','http','fetch-event'],selectedInterfaces:[]});
const path=join(output,'constructors.component.wasm');await writeFile(path,component);
const wit=await componentWit(component);assert.deepEqual(wit.split('\n').filter(line=>/^\s*import /.test(line)),[]);
await writeFile(join(output,'constructors.wit'),wit);
const{files}=await transpile(component,{name:'constructors'});
for(const[file,bytes]of Object.entries(files)){const target=join(output,file);await mkdir(dirname(target),{recursive:true});await writeFile(target,bytes);}
const instance=await import(pathToFileURL(join(output,'constructors.js'))),calls=[];
function check(report){
  assert(!report.failure,JSON.stringify(report.failure));assert.equal(report.passed,true);
  const writer=report.observations.writer;
  for(const name of ['function','prototypeIdentity','instanceIdentity','locked','unlocked'])assert.equal(writer[name],true,name);
  assert.deepEqual(writer.trace,['x','closed']);
  for(const name of ['plainCall','invalidInput','lockedInput'])assert.equal(writer[name].name,'TypeError');
  for(const value of Object.values(report.observations.controllers)){
    assert(value.function&&value.prototypeIdentity&&value.instanceIdentity);
    assert.equal(value.call.name,'TypeError');assert.equal(value.construct.name,'TypeError');
  }
}
for(let index=0;index<2;index++){
  const report=JSON.parse(await instance.run());calls.push(report);await writeFile(join(output,'calls.json'),JSON.stringify(calls,null,2)+'\n');check(report);
}
const host=spawnSync(wasmtime,['run','--invoke','run()',path],{encoding:'utf8',timeout:120000,maxBuffer:1024*1024});
await writeFile(join(output,'wasmtime.log'),JSON.stringify(host,null,2)+'\n');assert.equal(host.status,0,host.error?.message||host.stderr);
const wasmtimeReport=JSON.parse(JSON.parse(host.stdout.trim().replace(/\\u\{([0-9a-fA-F]+)\}/g,(_,hex)=>String.fromCodePoint(parseInt(hex,16)))));
check(wasmtimeReport);assert.deepEqual(wasmtimeReport,calls[0]);
const node=JSON.parse(await readFile(join(here,'constructors-node-results.json')));
const result={schema:1,atUtc:new Date().toISOString(),scope:'Separate bounded ordinary retained native constructor proof. No JS_GetClassObject call or compression/lifetime/fault probe.',
  engine,engineSha256:metadata.engineSha256,sourceRoot,metadata,componentizer:provenance,
  component:{path,bytes:component.length,sha256:hash(component),emittedImports:[],emittedWit:wit,interfaceAudit},
  calls,wasmtime:version.stdout.trim(),wasmtimeReport,node,
  sourceManifest:await Promise.all(['constructors.mjs','constructors-cases.mjs','constructors-node.mjs','constructors-node-results.json','run-constructors.mjs','profile.wit'].map(async path=>({path,sha256:hash(await readFile(join(here,path)))}))),
  limitations:['Only tested retained constructor operations; not full class parity or registered Node module support.',
    'Node error codes and TransformStreamDefaultController arity may differ; raw observations retained.',
    'Actual JS_GetClassObject result remains a separate native integration gate.']};
await writeFile(join(output,'results.json'),JSON.stringify(result,null,2)+'\n');
await writeFile(join(here,'constructors-component-results.json'),JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify({output,zeroImports:true,writerConstructed:true,illegalControllers:2,wasmtimePassed:true}));
