// Source-only audit and receipts. Does not compile or invoke a guest engine.
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFile, writeFile } from 'node:fs/promises';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
assert.equal(process.version,'v22.14.0');
const here=dirname(fileURLToPath(import.meta.url)),repository=resolve(here,'../../..');
const toolchain=resolve(process.env.NODE_COMPAT_TOOLCHAIN??'/tmp/starling-node-compat/native-toolchain-lock');
const releaseHeaders='/tmp/starling-node-compat/improved-build/spidermonkey-dist-release/include';
const hash=value=>createHash('sha256').update(value).digest('hex');
const groups={repository:[
  'builtins/web/blob.cpp','builtins/web/blob.h','builtins/web/file.cpp','builtins/web/file.h',
  'runtime/builtin.cpp','include/builtin.h','include/extension-api.h','runtime/event_loop.cpp',
  'builtins/web/streams/buf-reader.cpp','builtins/web/streams/buf-reader.h',
  'builtins/web/streams/native-stream-source.cpp','builtins/web/streams/native-stream-source.h',
  'builtins/web/text-codec/text-decoder.cpp','builtins/web/text-codec/text-decoder.h',
  'crates/rust-encoding/src/lib.rs','deps/include/rust-encoding.h',
  'builtins/node-compat/buffer-facade.mjs','builtins/node-compat/export-manifest.node-v22.14.0.json',
  'tests/integration/blob/blob.js','tests/e2e/blob/blob.js',
  ...['Blob-array-buffer.any.js.json','Blob-bytes.any.js.json','Blob-constructor.any.js.json','Blob-stream.any.js.json','Blob-text.any.js.json']
    .map(name=>'tests/wpt-harness/expectations/FileAPI/blob/'+name)],
  releaseHeaders:['js/ArrayBuffer.h','js/experimental/TypedData.h','js/AllocPolicy.h','mozilla/UniquePtr.h','mozilla/Vector.h'],
  toolchain:['@bytecodealliance/jco-std/dist/wasi/0.2.x/node/24.x.x/stream/consumers.js',
    '@bytecodealliance/jco-std/dist/wasi/0.2.x/node/24.x.x/stream/shared.js',
    '@bytecodealliance/jco/dist/node-builtins/stream.js','unenv/dist/runtime/node/stream/consumers.mjs']};
const roots={repository,releaseHeaders,toolchain:join(toolchain,'node_modules')},files=[],texts=new Map();
for(const [origin,paths]of Object.entries(groups))for(const path of paths){const bytes=await readFile(join(roots[origin],path));
  files.push({origin,path,sha256:hash(bytes),bytes:bytes.length});texts.set(origin+':'+path,bytes.toString());}
function cite(path,needle){const text=texts.get('repository:'+path);assert(text?.includes(needle),needle);return{path,line:text.slice(0,text.indexOf(needle)).split('\n').length,symbol:needle};}
const nativeSymbols=[
  cite('builtins/web/blob.h','using ByteBuffer ='),cite('builtins/web/blob.cpp','JSObject *Blob::data_to_owned_array_buffer'),
  cite('builtins/web/blob.cpp','bool Blob::read_blob_slice'),cite('builtins/web/blob.cpp','bool Blob::arrayBuffer(JSContext *cx, HandleObject'),
  cite('builtins/web/blob.cpp','bool Blob::bytes(JSContext *cx, HandleObject'),cite('builtins/web/blob.cpp','bool Blob::text(JSContext *cx, HandleObject'),
  cite('builtins/web/blob.cpp','bool Blob::stream(JSContext *cx, HandleObject'),cite('builtins/web/blob.cpp','bool Blob::slice(JSContext *cx, HandleObject'),
  cite('builtins/web/blob.cpp','bool Blob::append_value'),cite('builtins/web/blob.cpp','bool Blob::init_blob_parts'),
  cite('builtins/web/blob.cpp','bool Blob::init(JSContext'),cite('builtins/web/blob.cpp','void Blob::finalize'),
  cite('runtime/builtin.cpp','std::optional<std::span<uint8_t>> value_to_buffer'),
  cite('builtins/web/streams/buf-reader.cpp','class StreamTask'),cite('builtins/web/streams/buf-reader.cpp','bool cancel(JSContext'),
  cite('builtins/web/streams/buf-reader.cpp','bool pull(JSContext'),cite('builtins/web/streams/buf-reader.cpp','JSObject *BufReader::create'),
  cite('builtins/web/streams/native-stream-source.cpp','JSObject *NativeStreamSource::create'),
  cite('builtins/web/text-codec/text-decoder.cpp','bool TextDecoder::decode'),
];
const engine='/tmp/starling-node-compat/foundations-v7/native-freeze/off-foundations.engine.wasm';
const metadataBytes=await readFile(engine+'.build.json'),metadata=JSON.parse(metadataBytes),frozenRoot=resolve(dirname(engine),'source');
assert.equal(hash(await readFile(engine)),metadata.engineSha256);
const frozenChecks=[];
for(const file of files.filter(f=>f.origin==='repository')){
  const input=metadata.sourceManifest.find(e=>e.path===file.path);if(!input)continue;
  assert.equal(file.sha256,input.sha256,'Audited production input changed since v7: '+file.path);
  assert.equal(hash(await readFile(join(frozenRoot,file.path))),file.sha256);
  frozenChecks.push({path:file.path,sha256:file.sha256});
}
const expectations={};
for(const name of groups.repository.filter(p=>p.includes('/expectations/'))){const entries=JSON.parse(texts.get('repository:'+name)),counts={};
  for(const result of Object.values(entries))counts[result.status]=(counts[result.status]??0)+1;
  expectations[name]={counts,storedExpectationsOnly:true};}
const nativeFindings=[
  {id:'owned-native-storage',status:'verified-source',symbols:['Blob::ByteBuffer','Blob::append_value','Blob::finalize'],
    finding:'Blob owns a native js::Vector<uint8_t,0,SystemAllocPolicy> in a private reserved slot and deletes it at finalization. Strings/Blob parts/buffer sources are appended synchronously. There is no raw source byte pointer retained in a JS Promise or across iterator await.'},
  {id:'buffer-part-copy',status:'verified-source-with-gates',symbols:['Blob::append_value','value_to_buffer'],
    finding:'BufferSource data is borrowed and immediately appended through a non-JS SystemAllocPolicy vector operation. The shared out-flag is ignored. There is no explicit NoGC scope/current-backing policy or local JS OOM report for append failure; do not extend acceptance to shared/resizable/detached or reentrant coercion cases without a coordinated fix.'},
  {id:'arraybuffer-allocation',status:'unresolved-portable-allocator-contract',symbols:['Blob::data_to_owned_array_buffer','Blob::arrayBuffer','Blob::bytes'],
    finding:'Copy source is stable native storage with rooted self, but destination uses mozilla::MakeUnique<uint8_t[]> (std::make_unique/new[]) before NewArrayBufferWithContents requires JS_free-compatible memory. Use an explicitly compatible fallible JS allocator/FreePolicy or an engine-owned ArrayBuffer and reacquired NoGC data; null checks do not establish new[] allocation failure semantics. No runtime corruption/OOM result was demonstrated.'},
  {id:'promise-failure-reporting',status:'unresolved-source-gate',symbols:['Blob::arrayBuffer','Blob::bytes','Blob::text','Blob::append_value'],
    finding:'arrayBuffer/bytes reject a created Promise on copy failure, while some text native allocation paths return false after creating one; vector SystemAllocPolicy append failure may lack a pending JS error. Standardize pending exception/promise rejection and preserve genuine allocator failures before support claims.'},
  {id:'empty-text-pointer',status:'verified-source-no-null-finding',symbols:['Blob::text','mozilla::Vector<T,0>::CRAndStorage<0>::storage'],
    finding:'The Rust header requires nonnull slices even at length0. Pinned mozilla::Vector<T,0> supplies an aligned nonnull sentinel for empty storage, so the existing Blob text source is not diagnosed as a null-empty-slice bug. Decoder maximum/output overflow/result and allocation policy still require review.'},
  {id:'blob-stream-owner',status:'verified-source',symbols:['Blob::stream','BufReader::create','StreamTask::trace','NativeStreamSource::create'],
    finding:'BufReader User and NativeStreamSource Owner/Stream slots keep the Blob/reader reachable; queued task Heap reader has an explicit trace edge. Each task allocates an 8192-byte ArrayBuffer and fills it from owned native storage before constructing/enqueuing the visible Uint8Array.'},
  {id:'blob-stream-cancellation',status:'unresolved-source-gate',symbols:['BufReader pull','BufReader cancel','StreamTask::run','NativeStreamSource::create'],
    finding:'pull queues an unchecked js_new StreamTask and returns undefined; cancel is a no-op and does not remove already queued tasks. Creation uses NewReadableDefaultStreamObject, not a byte stream. Node Blob.stream has byte-stream/BYOB and pending pull cancellation behavior. No native cancellation race or fault probe was run.'},
  {id:'other-constructor-slice-gates',status:'verified-source-not-consumer-support',symbols:['Blob::init','Blob::slice','Blob::init_options'],
    finding:'Options are processed after parts, so native endings is selected after string appends; slice positive allocation failure can flow to create with null data and a positive requested length. Failed-constructor/finalizer state and limits need separate review. Consumer Blob with default options avoids options semantics, but does not bypass allocator/error/identity gates.'},
  {id:'decoder-reuse',status:'justified-source-proposal-not-guest-proof',symbols:['TextDecoder::decode'],
    finding:'The current decoder validates kind before options, roots input, reads lengths after option access, rejects shared views, allocates owned output before reacquiring native data under NoGC, synchronously consumes bytes/pending state through encoding_c, and copies output into a JS string. A small captured text/json facade can call it with private frozen options and retain no raw spans across await.'},
];
const report={schema:1,proposalVersion:'stream-consumers-source-v1',node:process.version,installed:false,guestProbesRun:false,
  sources:files,nativeSymbols,nativeFindings,storedWptExpectations:expectations,
  nativeSourcePin:{engineSha256:metadata.engineSha256,engineReceiptSha256:hash(metadataBytes),frozenRoot,sourceInputs:metadata.sourceManifest.length,verifiedRelevantInputs:frozenChecks,
    use:'Source identity only; no consumer or new native Blob probe is inferred from the existing v7 engine'},
  nodeEmbeddedSources:Object.fromEntries(['stream/consumers','internal/blob','internal/encoding'].map(name=>[name,{sha256:hash(process.binding('natives')[name]),bytes:Buffer.byteLength(process.binding('natives')[name])}])),
  proposals:{partial:['text','json'],deferred:['blob','arrayBuffer','buffer'],nativeBlobFixesCompiled:false,
    copies:'Keep Blob part JS values rooted until final constructor time. Never copy each yielded byte chunk early. Text instead eagerly decodes each yielded byte chunk and flushes only after iteration; strings do not flush pending decoder bytes.',
    classicStream:'No classic Stream API, Node nextTick queue, Web reader adapter or scheduling compatibility follows from this independent subpath.',requiredHostInterfaces:[]},
  primaryReferences:['https://github.com/nodejs/node/blob/v22.14.0/lib/stream/consumers.js','https://github.com/nodejs/node/blob/v22.14.0/lib/internal/blob.js',
    'https://github.com/nodejs/node/blob/v22.14.0/test/parallel/test-stream-consumers.js','https://nodejs.org/download/release/v22.14.0/docs/api/webstreams.html#utility-consumers','https://w3c.github.io/FileAPI/'],
  scope:'Source/Node-host audit only. No production edits, native compilation, hazardous getter/detach/shared probes, OOM injection, component run or support/performance claim.'};
await writeFile(join(here,'source-audit.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({files:files.length,nativeSymbols:nativeSymbols.length,sourceFindings:nativeFindings.length,frozenInputsVerified:frozenChecks.length,guestProbesRun:false,installed:false}));
