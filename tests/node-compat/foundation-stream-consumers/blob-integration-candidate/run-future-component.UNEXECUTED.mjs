// PREPARED ONLY: no engine has been built with this four-file candidate.
// This runner refuses all unpatched/old engines BEFORE componentization.
import assert from 'node:assert/strict';
import {readFile,writeFile} from 'node:fs/promises';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {nativeHarness,hash} from '../../foundations/native-scalar-harness.mjs';
import {ordinaryCases,receiverCases} from './cases.mjs';
const here=dirname(fileURLToPath(import.meta.url));
assert.equal(process.version,'v22.14.0');
assert(process.env.NODE_COMPAT_ENGINE&&process.env.NODE_COMPAT_ENGINE_SOURCE_ROOT,'Require a future corrected engine AND its exact source freeze');
const source=JSON.parse(await readFile(join(here,'source-receipt.json')));
assert.equal(source.baseEngineSha256,'1098e7531004a4ca1b47f2ca80527a01e64cd3392d28d760da37326c08a85154');
assert.equal(source.patch.sha256,'5c33bf8efa60f80e3f796862c42ab40402c9160923e0fbbe6b802b8c122976b3');
const reviewedAfter={
 'builtins/web/blob.cpp':'51c0e7f7eaf8a80a931d3f84f1632d4027600a915e0f5c5d879cdae0a6dccfcb',
 'builtins/web/blob.h':'aaa461831d3edd29373c490e8a76e99d075fc13056e1f349afa79711ce5b356a',
 'builtins/web/file.cpp':'c447b86ac93fbeca42ddb940e6fee9d08481c720013bcbc70feb093d952a880b',
 'builtins/web/file.h':'d162a36c23da23c5a8c1c62500cf6b17fa77876219a135636812f8b21a110305',
};
assert.equal(source.fourFiles.length,4);
for(const item of source.fourFiles)assert.equal(item.afterSha256,reviewedAfter[item.path]);
const engine=resolve(process.env.NODE_COMPAT_ENGINE),metadata=JSON.parse(await readFile(engine+'.build.json'));
assert.equal(hash(await readFile(engine)),metadata.engineSha256);
assert.equal(metadata.oomTesting,false);assert.equal(metadata.gcStress,false);assert.equal(metadata.observedCMakeOptions.CMAKE_BUILD_TYPE,'Release');
assert.equal(metadata.sourceManifest.length,304);assert.equal(new Set(metadata.sourceManifest.map(item=>item.path)).size,304);
const after=new Map(source.fourFiles.map(item=>[item.path,item.afterSha256]));
assert.equal(after.size,4);
const actual=new Map(metadata.sourceManifest.map(item=>[item.path,item.sha256]));
for(const item of source.baseSourceManifest){
  assert.equal(actual.get(item.path),after.get(item.path)??item.sha256,'Future candidate must change ONLY the four reviewed files: '+item.path);
  assert.equal(hash(await readFile(join(process.env.NODE_COMPAT_ENGINE_SOURCE_ROOT,item.path))),actual.get(item.path));
}
assert.deepEqual(metadata.componentizeSourceManifest,source.componentizeSourceManifest,'Preserve the actual m10 embedding/strict boundary');
const manifest=JSON.parse(await readFile(join(process.env.NODE_COMPAT_ENGINE_SOURCE_ROOT,'builtins/node-compat/export-manifest.node-v22.14.0.json')));
for(const name of ['Blob','File'])assert(manifest.modules['node:buffer'].importOnlyExports.includes(name),'Do not promote public node:buffer export');
const oracle=JSON.parse(await readFile(join(here,'node-results.json')));
assert.equal(hash(await readFile(join(here,'cases.mjs'))),oracle.sources['cases.mjs']);
assert.deepEqual(await ordinaryCases({Blob,File}),oracle.ordinary);
assert.deepEqual(await receiverCases({Blob,File}),oracle.receivers);
const h=await nativeHarness({kind:'blob-owned-v2',here,enabledField:'profileEnabled',option:'ENABLE_BUILTIN_NODE_COMPAT',outputVariable:'NODE_COMPAT_BLOB_CANDIDATE_OUTPUT'});
const bundle=await h.bundle(join(here,'future-component.mjs'),['node:buffer']);
assert.doesNotMatch(bundle.code,/nodeOnlyCases|Date\.now|mode:\s*['"]byob|\.getReader\(/,'Exclude all genuine Blob stream/clock/remaining-WebIDL Node-only probes');
const fixture=await h.build('blob_owned_v2',bundle.code),instance=await h.importFixture(fixture),calls=[];
// Node error-code text/own fields differ from native WrongReceiver. Compare
// phase/type while preserving every raw error-code observation in the report.
const timingAndType=rows=>rows.map(({result,...row})=>({...row,result:{phase:result.phase,name:result.name}}));
function check(observed,index){
  assert.equal(observed.calls,index);assert.deepEqual(observed.ordinary,oracle.ordinary);
  assert.deepEqual(timingAndType(observed.receivers),timingAndType(oracle.receivers));
  for(const refusal of observed.deferred){assert.equal(refusal.code,'ERR_SM_NODE_UNSUPPORTED');assert(refusal.distinctFromGlobal);}
  assert.equal(observed.deferred.length,4);assert.equal(observed.nativeBlobStreamInvoked,false);assert.equal(observed.publicNodeBufferBlobFilePromoted,false);
  assert.deepEqual(observed.snapshot,{text:'AB',current:'AB',fileName:'snapshot.txt',lastModified:17,fileText:'C',bufferBrand:true,bufferBytes:[65,66]});
}
for(let i=1;i<=3;i++){const observed=JSON.parse(await instance.run());check(observed,i);calls.push(observed);}
const wasmtime=h.runHost(fixture);check(wasmtime.observed,1);
const initialization=[];
for(const [name,body]of [['null_parts','new Blob(null);'],['file_missing_name','new File([]);'],['unhandled_receiver',"Blob.prototype.text.call({});"]])
  initialization.push(await h.expectInitialization('blob_'+name,body+"export function run(){return '';}",/Blob|File|receiver|TypeError|argument/i));
await h.writeReport({schemaVersion:1,state:'future-candidate-executed-only-if-run',...h.evidence,fixture,calls,wasmtime,initialization,
  sourceReceiptSha256:hash(await readFile(join(here,'source-receipt.json'))),nodeOracleSha256:hash(await readFile(join(here,'node-results.json'))),
  publicNodeBufferBlobFilePromoted:false,genuineNativeBlobStreamInvoked:false,
  limitations:['Only 11 ordinary groups and 23 guarded receiver cases; broader WebIDL/options/scheduling/clock, Blob stream, external-memory accounting and allocation-failure behavior remain unverified/deferred.',
    'No detached/shared/resizable, poisoned Error.code, old native unsafe path, fault, OOM or DEBUG execution.']});
