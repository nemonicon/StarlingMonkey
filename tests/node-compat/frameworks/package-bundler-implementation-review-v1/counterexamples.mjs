// Actual optional API, host bundle-only negative-boundary checks; no generated
// code, native engine, component or guest is imported or invoked.
import assert from 'node:assert/strict';
import { mkdir, writeFile, readFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createHash } from 'node:crypto';
import { loadToolchain } from '../../toolchain.mjs';
import { selectedManifestsForEngine } from '../../module-selection.mjs';
import { bundlePackages } from '../../framework-package-bundler.mjs';
const HERE=dirname(fileURLToPath(import.meta.url));
const root=join(HERE,'counterexample-evidence');await mkdir(root);
const toolchain=await loadToolchain();
const sourceRoot='/private/tmp/starling-node-compat/production-classic-trace-v1/native-freeze/source';
const metadata=JSON.parse(await readFile('/private/tmp/starling-node-compat/production-classic-trace-v1/native-freeze/normal-off.engine.wasm.build.json'));
const builtinManifests=selectedManifestsForEngine(metadata,{sourceRoot});
const cases=[
 {id:'module-require-alias',expected:'deny-runtime-loader',files:{'entry.mjs':"import value from './p.cjs';export {value};",'p.cjs':"const m=module;module.exports=function(name){return m.require(name)};"}},
 {id:'module-require-computed',expected:'deny-runtime-loader',files:{'entry.mjs':"import value from './p.cjs';export {value};",'p.cjs':"module.exports=function(name){return module['req'+'uire'](name)};"}},
 {id:'global-this-require',expected:'deny-runtime-loader',files:{'entry.mjs':"export function value(name){return globalThis.require(name)};"}},
 {id:'global-this-process',expected:'deny-runtime-environment',files:{'entry.mjs':"export function value(){return globalThis.process.env.OTHER_ENV};"}},
 {id:'global-this-filename',expected:'deny-runtime-filename',files:{'entry.mjs':"export function value(){return globalThis.__dirname};"}},
 {id:'provided-local-process',expected:'ordinary-provided-local',files:{'entry.mjs':"export function value(process){return process.answer};"}},
 {id:'provided-local-global',expected:'ordinary-provided-local',files:{'entry.mjs':"export function value(global){return global.answer};"}},
 {id:'computed-global-require',expected:'deny-runtime-loader',files:{'entry.mjs':"export function value(name){return globalThis['req'+'uire'](name)};"}},
];
const results=[];
for(const test of cases){
 const folder=join(root,test.id);await mkdir(folder);await writeFile(join(folder,'package.json'),'{"type":"commonjs"}\n',{flag:'wx'});
 for(const[name,code]of Object.entries(test.files))await writeFile(join(folder,name),code+'\n',{flag:'wx'});
 const result={id:test.id,expected:test.expected,generatedModuleImported:false};
 try{const built=await bundlePackages({...toolchain,input:join(folder,'entry.mjs'),builtinManifests});
  await writeFile(join(folder,'bundle.mjs'),built.code,{flag:'wx'});await writeFile(join(folder,'bundle.json'),JSON.stringify({...built,code:undefined},null,2)+'\n',{flag:'wx'});
  result.accepted=true;result.policy=built.policy;result.imports=built.imports;
 }catch(error){result.accepted=false;result.error={name:error.name,code:error.code,message:error.message};}
 await writeFile(join(folder,'result.json'),JSON.stringify(result,null,2)+'\n',{flag:'wx'});results.push(result);
}
const source=await readFile(join(HERE,'../../framework-package-bundler.mjs'));
const report={schemaVersion:1,sourceSha256:createHash('sha256').update(source).digest('hex'),sourceBytes:source.length,cases:results,guestExecuted:false,nativeEngineExecuted:false};
await writeFile(join(root,'results.json'),JSON.stringify(report,null,2)+'\n',{flag:'wx'});
process.stdout.write(JSON.stringify(results.map(x=>({id:x.id,expected:x.expected,accepted:x.accepted,error:x.error?.message})),null,2)+'\n');
