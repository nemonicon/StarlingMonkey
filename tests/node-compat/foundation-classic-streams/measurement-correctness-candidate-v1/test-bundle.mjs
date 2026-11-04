// Host source graph only: no engine tuple, metadata or actual admission model.
import assert from 'node:assert/strict';
import {readFile,writeFile,mkdir,lstat} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {bundleDiagnostic} from './bundle-diagnostic.mjs';
assert.equal(process.version,'v22.14.0');assert.equal(process.argv.length,4);
const root=resolve(process.argv[2]),output=resolve(process.argv[3]),here=dirname(fileURLToPath(import.meta.url)),hash=bytes=>createHash('sha256').update(bytes).digest('hex');
assert(output.startsWith('/tmp/starling-node-compat/'));try{await lstat(output);assert.fail('Fresh source output required');}catch(error){if(error.code!=='ENOENT')throw error;}await mkdir(output,{recursive:false});
const policy=JSON.parse(await readFile(join(root,'tests/node-compat/foundation-classic-streams/trace-integration-candidate-v1/policy.json'))),sources=new Map(policy.expectedNativeSourceManifest.map(row=>[row.path,row.sha256]));
const names=['export-manifest.node-v22.14.0.json','export-manifest.path.node-v22.14.0.json','export-manifest.events.node-v22.14.0.json','export-manifest.string-decoder.node-v22.14.0.json','export-manifest.assert.node-v22.14.0.json','export-manifest.querystring.node-v22.14.0.json','export-manifest.util.node-v22.14.0.json','export-manifest.stream-web.node-v22.14.0.json','classic-streams/export-manifest.classic-streams.node-v22.14.0.json'];
const builtinManifests=[];for(const name of names){const relative='builtins/node-compat/'+name,bytes=await readFile(join(root,relative));assert.equal(hash(bytes),sources.get(relative));builtinManifests.push(JSON.parse(bytes));}
const {loadToolchain}=await import(pathToFileURL(join(root,'tests/node-compat/toolchain.mjs'))),toolchain=await loadToolchain();
const bundle=await bundleDiagnostic({toolchain,admission:{toolSourceRoot:root,builtinManifests,diagnosticExternalIds:['starling:test-classic-benchmark']},input:join(here,'guest.mjs'),allowedModuleIds:['guest.mjs','native-provider.mjs','workload.mjs','encoding-cases.mjs'].map(name=>join(here,name))});
await writeFile(join(output,'guest.bundle.mjs'),bundle.code,{flag:'wx'});
await writeFile(join(output,'results.json'),JSON.stringify({schemaVersion:1,state:'FINITE_DIAGNOSTIC_CORRECTNESS_HOST_SOURCE_BUNDLE_VERIFIED_NOT_ARTIFACT_ADMISSION',imports:bundle.imports,moduleIds:bundle.moduleIds,bundleSha256:hash(bundle.code),bundleBytes:Buffer.byteLength(bundle.code),engineOrMetadataModelCreated:false,diagnosticModuleBindingUnverifiedUntilActualComponent:true,componentizerOrGuestOrNativeBuildOrTargetHostExecuted:false},null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({imports:bundle.imports,modules:bundle.moduleIds.length,output}));
