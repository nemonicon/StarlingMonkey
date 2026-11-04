// Isolated bundled-facade gate. This never installs node:stream/consumers.
import assert from 'node:assert/strict';
import * as nodeConsumers from 'node:stream/consumers';
import * as prototype from './prototype.mjs';
import { readFile,writeFile } from 'node:fs/promises';
import { dirname,join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { nativeHarness,hash } from '../foundations/native-scalar-harness.mjs';
import { loadToolchain } from '../toolchain.mjs';
import { bundleProfile } from '../profile-bundler.mjs';
import { guestTextOracle } from './guest-oracle.mjs';
import { profileChecks } from './component-checks.mjs';
const here=dirname(fileURLToPath(import.meta.url));
const sourceIndexBytes=await readFile(join(here,'index.json')),sourceIndex=JSON.parse(sourceIndexBytes);
for(const file of sourceIndex.files)assert.equal(hash(await readFile(join(here,file.path))),file.sha256,'Immutable source/Node record: '+file.path);
const oracle=JSON.parse(await readFile(join(here,'node-results.json'))),policyOracle=JSON.parse(await readFile(join(here,'prototype-node-results.json')));
const selected=guestTextOracle(await readFile(join(here,'node-checks.mjs'),'utf8'),oracle);
// Confirm the exact selected guest body and policy mirror against the pinned
// host oracles before componentization, with the Blob-only exclusion explicit.
const guest=await import('data:text/javascript;base64,'+Buffer.from(selected.source).toString('base64'));
assert.deepEqual(await guest.textChecks(nodeConsumers),selected.cases);
assert.deepEqual(await guest.textChecks(prototype),selected.cases);
const hostPolicies=await profileChecks(prototype);
assert.deepEqual(hostPolicies[2].result.ownKeys,{text:['length','name'],json:['length','name']});
delete hostPolicies[2].result.ownKeys;assert.deepEqual(hostPolicies,policyOracle.profiles);
const h=await nativeHarness({kind:'stream-consumers-prototype',here,enabledField:'profileEnabled',option:'ENABLE_BUILTIN_NODE_COMPAT',outputVariable:'NODE_COMPAT_CONSUMERS_OUTPUT'});
assert.equal(h.metadata.engineSha256,'ee92d5d451c16eb7ce83e0306e8dab6920f4aacd9f2c4bb9d6e5e4af2c20ea09','Use the immutable v7 OFF engine');
assert.equal(h.metadata.sourceManifest.length,293);
const decoderPath='builtins/web/text-codec/text-decoder.cpp',decoderSha='4697d8951a724d92e7550d48bd10cd2652d4d789797dc90ad8401216e9a4512c';
assert.equal(h.metadata.sourceManifest.find(e=>e.path===decoderPath)?.sha256,decoderSha,'Require the exact reviewed fixed decoder');
const sourceAudit=JSON.parse(await readFile(join(here,'source-audit.json')));
assert.equal(sourceAudit.sources.find(e=>e.path===decoderPath)?.sha256,decoderSha);
const toolchain=await loadToolchain(),bundle=await bundleProfile({...toolchain,builtinManifests:h.builtinManifests,input:join(here,'component.mjs'),
  virtualModules:{'node-compat:consumers-text-checks':selected.source}});
assert.deepEqual(bundle.imports,['node:buffer']);
assert(bundle.moduleIds.every(id=>!id.includes('/builtins/node-compat/')&&!id.includes('/node_modules/')),'Only isolated facade/checks plus actual native Buffer');
assert.doesNotMatch(bundle.code,/BlobCtor|new Blob\b|\.Blob\b|blobChecks|readable-stream|jco-std|unenv/,'No Blob/native Stream probe or JS compatibility adapter');
await writeFile(join(h.output,'guest-oracle-selection.json'),JSON.stringify(selected.selection,null,2)+'\n');
await writeFile(join(h.output,'guest-text-checks.mjs'),selected.source);
const fixture=await h.build('isolated_stream_consumers',bundle.code);
function validate(observed,count){
  assert.equal(observed.failure,undefined,JSON.stringify(observed.failure));assert.equal(observed.calls,count);
  assert.deepEqual(observed.cases,selected.cases);
  const policy=structuredClone(observed.profile),expected=structuredClone(policyOracle.profiles);
  assert.equal(policy.length,12);
  // Namespace lowering is a bundler observation, not registered native ESM proof.
  const namespace=policy[1].result.namespace;policy[1].result.namespace=expected[1].result.namespace;
  const ownKeys=policy[2].result.ownKeys;delete policy[2].result.ownKeys;
  for(const name of ['text','json'])assert.deepEqual([...ownKeys[name]].sort(),['length','name']);
  assert.deepEqual(policy,expected);assert(['[object Module]','[object Object]'].includes(namespace));
  assert.deepEqual(observed.snapshot,{text:'ABC!',flushed:'\ufffd',byte:17+count,bufferBrand:true,viewOffset:2,backingBytes:7});
  assert.deepEqual(observed.state,{freshDecoderAfterSnapshot:true,freshJsonAfterError:true});
  assert.equal(observed.nativeBuffer,true);assert.equal(observed.nativeBlobInvoked,false);
  assert.deepEqual(observed.nativeReadableStream,{constructor:'function',asyncIterator:'undefined',values:'undefined',from:'undefined'});
  return observed;
}
const instance=await h.importFixture(fixture);
const calls=[validate(JSON.parse(await instance.run()),1),validate(JSON.parse(await instance.run()),2)];
const wasmtime=h.runHost(fixture);validate(wasmtime.observed,1);
const initialization=[];
async function failure(name,body,expected){
  const input=join(h.output,name+'.mjs');await writeFile(input,`import {arrayBuffer,blob,buffer,text,json} from ${JSON.stringify(join(here,'prototype.mjs'))};\n${body}\nexport function run(){return '';}`);
  const lowered=await bundleProfile({...toolchain,builtinManifests:h.builtinManifests,input});
  assert.deepEqual(lowered.imports,[]);assert.doesNotMatch(lowered.code,/new Blob\b|BlobCtor/);
  initialization.push(await h.expectInitialization(name,lowered.code,expected));
}
for(const name of ['blob','arrayBuffer','buffer']){
  await failure('deferred-'+name+'-call',name+'([]);',/ERR_SM_NODE_UNSUPPORTED/);
  await failure('deferred-'+name+'-new','new '+name+'([]);',/ERR_SM_NODE_UNSUPPORTED/);
}
await failure('awaited-text-invalid','await text([{}]);',/ERR_INVALID_ARG_TYPE/);
await failure('unawaited-text-invalid','text([{}]);',/ERR_INVALID_ARG_TYPE/);
await failure('microtask-text-invalid','Promise.resolve().then(()=>text([{}]));',/ERR_INVALID_ARG_TYPE/);
await failure('awaited-json-invalid',"await json(['{']);",/SyntaxError|JSON|expected property/);
await failure('awaited-input-cap','await text([new Uint8Array(1048577)]);',/ERR_SM_NODE_LIMIT/);
const sources=await Promise.all(['guest-oracle.mjs','component-checks.mjs','component.mjs','run-component.mjs']
  .map(async path=>({path,sha256:hash(await readFile(join(here,path)))})));
const report={schema:1,atUtc:new Date().toISOString(),contractVersion:policyOracle.contractVersion,node:process.version,
  installed:false,nativeBlobInvoked:false,sourceFreezeSha256:hash(sourceIndexBytes),sourceAuditSha256:hash(await readFile(join(here,'source-audit.json'))),
  exactNativeDecoder:{path:decoderPath,sha256:decoderSha},...h.evidence,fixture,
  bundle:{imports:bundle.imports,moduleIds:bundle.moduleIds},oracleSelection:selected.selection,
  differentialGroups:selected.cases.length,profileGroups:policyOracle.profileGroups,calls,wasmtime,initialization,sources,
  limitations:['Isolated bundled facade over actual native TextDecoder; node:stream/consumers is not registered or production-admitted and has no selected production profile version.',
    'One of six invalid-chunk vectors constructs Blob in the immutable Node helper and is explicitly excluded from guest execution. Eighteen groups run with five invalid-kind vectors; Blob remains Node-only.',
    'Native ReadableStream asyncIterator/values/from are absent; plain iterator fixtures do not establish Web or classic Stream acceptance or Node nextTick/ALS ordering.',
    'Namespace reflection after bundling is not proof of a future native Module Namespace Object.',
    'No Blob constructor/read/stream/getter, detached/shared/resizable lifetime, OOM or hazard probe is executed.',
    'Resource errors are explicit profile caps; no genuine allocation-failure, total parser-heap, performance or component-size benefit is claimed.',
    'No HTTP/two-host deployment in this isolated scalar gate.']};
await writeFile(join(h.output,'results.json'),JSON.stringify(report,null,2)+'\n');
await writeFile(join(here,'component-results.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({output:h.output,differentialGroups:report.differentialGroups,profileGroups:report.profileGroups,
  calls:calls.map(c=>c.calls),freshWasmtimeCall:wasmtime.observed.calls,initializationFailures:initialization.length,imports:[],
  excludedBlobInputVectors:selected.selection.excluded.length,installed:false}));
