// Ordinary host bundling only: emitted JavaScript is inspected, never executed.
import assert from 'node:assert/strict';
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {loadToolchain} from '../../toolchain.mjs';
const HERE=dirname(fileURLToPath(import.meta.url));
const root=resolve(process.env.NODE_COMPAT_CLASSIC_TEST_ROOT??'/tmp/starling-node-compat/classic-integration-source-tests-v3');
const output=resolve(process.env.NODE_COMPAT_CLASSIC_BUNDLER_OUTPUT??'/tmp/starling-node-compat/classic-bundler-source-tests-v1');
await mkdir(output);const hash=data=>createHash('sha256').update(data).digest('hex');
const {coreManifest}=await import(pathToFileURL(join(root,'tests/node-compat/module-selection.mjs')));
const {bundleProfile}=await import(pathToFileURL(join(root,'tests/node-compat/profile-bundler.mjs')));
const manifest=JSON.parse(await readFile(join(HERE,'source/builtins/node-compat/classic-streams/export-manifest.classic-streams.node-v22.14.0.json')));
const toolchain=await loadToolchain(),observations=[];
for(const id of ['node:stream','stream','node:stream/promises','stream/promises'])for(const cjs of[false,true]){
 const path=join(output,'entry-'+observations.length+(cjs?'.cjs':'.mjs'));
 const source=cjs?'module.exports = require('+JSON.stringify(id)+');\n':'import * as api from '+JSON.stringify(id)+'; export {api};\n';
 await writeFile(path,source,{flag:'wx'});
 const result=await bundleProfile({...toolchain,input:path,builtinManifests:[coreManifest,manifest]});
 const canonical=id.startsWith('node:')?id:'node:'+id;assert.deepEqual(result.imports,[canonical]);
 assert(!result.code.includes('createClassicStreams')&&!result.code.includes('createClassicCore'));
 let error;try{await bundleProfile({...toolchain,input:path,builtinManifests:[coreManifest]});}catch(value){error=value;}
 assert(error&&/not admitted/.test(error.message));
 observations.push({id,cjs,sourceSha256:hash(source),canonical,emittedJavaScriptSha256:hash(result.code),disabledError:error.message,adapterBundled:false});
}
const result={schemaVersion:1,state:'CLASSIC_LITERAL_ESM_AND_CJS_HOST_BUNDLING_PASSED',cases:observations.length,enabledBundles:8,disabledRefusals:8,
 node:process.version,rolldown:'1.2.16',componentizerInvoked:false,compilerInvoked:false,guestInvoked:false,emittedJavaScriptExecuted:false,observations};
await writeFile(join(output,'results.json'),JSON.stringify(result,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify({state:result.state,enabledBundles:8,disabledRefusals:8,output}));
