// Focused ordinary reflection check; does not repeat initialization suites.
import assert from 'node:assert/strict';
import {readFile,writeFile} from 'node:fs/promises';
import {dirname,join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {nativeHarness,hash} from '../../foundations/native-scalar-harness.mjs';
import {loadToolchain} from '../../toolchain.mjs';
import {bundleProfile} from '../../profile-bundler.mjs';
import {run as reference} from './reflection-component.mjs';
const here=dirname(fileURLToPath(import.meta.url));
const h=await nativeHarness({kind:'stream-consumers-reflection',here,enabledField:'profileEnabled',option:'ENABLE_BUILTIN_NODE_COMPAT',outputVariable:'NODE_COMPAT_CONSUMERS_REFLECTION_OUTPUT'});
assert.equal(h.metadata.engineSha256,'ee92d5d451c16eb7ce83e0306e8dab6920f4aacd9f2c4bb9d6e5e4af2c20ea09');
const main=JSON.parse(await readFile(join(here,'component-results.json')));
assert.equal(main.engineSha256,h.metadata.engineSha256);
const factorySha256=hash(await readFile(join(here,'create-module.mjs')));
assert.equal(main.sources.find(s=>s.path==='create-module.mjs')?.sha256,factorySha256);
const expected=JSON.parse(reference());
for(const name of ['text','json']){
  assert.deepEqual(expected[name].ownKeys,['length','name']);
  assert.deepEqual(expected[name].length,{value:1,writable:false,enumerable:false,configurable:true});
  assert.deepEqual(expected[name].name,{value:name,writable:false,enumerable:false,configurable:true});
}
const toolchain=await loadToolchain();
const bundle=await bundleProfile({...toolchain,builtinManifests:h.builtinManifests,input:join(here,'reflection-component.mjs')});
assert.deepEqual(bundle.imports,[]);assert(bundle.moduleIds.every(id=>!id.includes('/builtins/node-compat/')&&!id.includes('/node_modules/')));
const fixture=await h.build('consumer_function_descriptors',bundle.code);
const instance=await h.importFixture(fixture),observed=JSON.parse(instance.run());assert.deepEqual(observed,expected);
const wasmtime=h.runHost(fixture);assert.deepEqual(wasmtime.observed,expected);
const report={schema:1,installed:false,implementationRevision:'metadata-v2',factorySha256,expected,observed,wasmtime,
  ...h.evidence,fixture,mainReportSha256:hash(await readFile(join(here,'component-results.json'))),
  sources:await Promise.all(['reflection-component.mjs','run-reflection.mjs'].map(async path=>({path,sha256:hash(await readFile(join(here,path)))}))),
  scope:'Focused Node22/actual native v7 component function reflection. Keys are observed before descriptor reads; no Blob invocation, mutation lifetime or fault probe.'};
await writeFile(join(h.output,'results.json'),JSON.stringify(report,null,2)+'\n');
await writeFile(join(here,'reflection-results.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({keys:observed.text.ownKeys,length:observed.text.length,name:observed.text.name,imports:[],installed:false}));
