// Actual entry host bundling only. No package/component/guest/host invocation.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {mkdtemp,readFile,writeFile} from 'node:fs/promises';
import {dirname,join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {verifyProductionTicks} from './capability/preflight.mjs';
import {selectedManifestsForEngine} from '../../module-selection.mjs';
import {loadToolchain} from '../../toolchain.mjs';
import {createProfilePlugin} from '../../profile-bundler.mjs';
import {createClassicHTTPPlugin,BASELINE_ENTRY,COMPOSER_ID,COMPOSER_SOURCE} from './capability/composer-plugin.mjs';
import {loadHTTPOracles} from './capability/oracles.mjs';
const here=dirname(fileURLToPath(import.meta.url));
const hash=data=>createHash('sha256').update(data).digest('hex');
const actual=await verifyProductionTicks();
const builtinManifests=selectedManifestsForEngine(actual.metadata,{sourceRoot:actual.sourceRoot});
const admission={...actual,builtinManifests,report:{state:'ACTUAL_READ_ONLY_NATIVE_PREFLIGHT_FOR_HOST_BUNDLE',engineSha256:actual.pin.engineSha256,sourceFiles:342}};
const entry=join(here,'capability/http-component.mjs');
const oracles=await loadHTTPOracles(admission,entry);
const {rolldown,parseAst}=await loadToolchain();
const build=await rolldown({input:entry,platform:'neutral',treeshake:false,plugins:[createClassicHTTPPlugin(),
  {name:'exact-standard-http-host-bundle',resolveId(id){if(id==='wasi:http/types@0.2.10')return{id,external:true};if(id.startsWith('wasi:'))throw new Error('Unselected source WASI import: '+id);}},
  createProfilePlugin(parseAst,{builtinManifests,virtualModules:oracles.virtualModules})]});
let chunk;try{const generated=await build.generate({format:'esm',codeSplitting:false});assert.equal(generated.output.length,1);chunk=generated.output[0];}finally{await build.close();}
const imports=['node:stream','node:stream/promises','node:buffer','node:child_process','wasi:http/types@0.2.10','node:path','node:path/posix','node:path/win32','node:events','node:string_decoder','node:assert','node:assert/strict','node:querystring','node:util','node:util/types','node:sys','node:stream/web'].sort();
assert.deepEqual([...chunk.imports].sort(),imports);
const modules=Object.keys(chunk.modules);assert(modules.includes(BASELINE_ENTRY));assert(modules.includes(COMPOSER_ID));
assert(modules.some(id=>id.endsWith('/production-trace-runtime-activated-v1/harness/checks.mjs')));
assert(modules.every(id=>!/builtins\/node-compat\/|node_modules\/(?:buffer|unenv)|node-builtins|classic-core\.generated/.test(id)));
assert.doesNotMatch(chunk.code,/reference-kernel|createBufferModule|buffer-facade|__require/);
await actual.recheck();
const output=await mkdtemp('/tmp/starling-node-compat/classic-trace-http-bundle-v1-');await writeFile(join(output,'http.bundle.mjs'),chunk.code,{flag:'wx'});
const result={schemaVersion:1,state:'COMBINED_HTTP_ACTUAL_ENTRY_HOST_BUNDLE_PASSED',output,imports:chunk.imports,modules,
  bundleSha256:hash(chunk.code),composerSha256:hash(COMPOSER_SOURCE),baselineEntry:BASELINE_ENTRY,baselineSha256:hash(await readFile(BASELINE_ENTRY)),
  entrySha256:hash(await readFile(entry)),engineSha256:actual.pin.engineSha256,variant:'normal-runtime',ordinaryGroups:19,
  sourceInputClosure:actual.report.inputClosure,sourceInputsRecheckedAfterBundle:true,
  foundationSchema:5,protectedAbortGroups:29,virtualOracleIds:Object.keys(oracles.virtualModules).sort(),noFacadeOrAdapterBundled:true,
  componentizerOperationInvoked:false,bundleExecuted:false,guestExecuted:false,targetHostExecuted:false};
await writeFile(join(output,'results.json'),JSON.stringify(result,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify({state:result.state,output,imports:chunk.imports,bundleSha256:result.bundleSha256}));
