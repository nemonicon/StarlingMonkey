import assert from 'node:assert/strict';
import {readFile,writeFile} from 'node:fs/promises';
assert.equal(process.version,'v22.14.0');
const node=JSON.parse(await readFile(new URL('./node-results.json',import.meta.url)));
const proof=JSON.parse(await readFile(new URL('./component-results.json',import.meta.url)));
const constructorProof=JSON.parse(await readFile(new URL('./constructors-component-results.json',import.meta.url)));
const details={
  ReadableStream:['Reuse actual SM global; preserve identity.','from, values and Symbol.asyncIterator absent.','readable-basic, readable-cancel, pipe-to, tee','Implement/test iterable conversion and cancellation; pipeThrough/signal/error/lock and transfer gates.'],
  ReadableStreamDefaultReader:['Reuse actual SM global.','Complete property/error semantics unverified.','readable-basic, readable-cancel','Pending-read release, brands, closed rejection and descriptor tests.'],
  ReadableStreamBYOBReader:['Reuse actual SM global with reviewed captured read guard.','Native read ignores Node22 options.min; explicitly reject unsupported minimum fill before native call.','byob-basic, byob-minimum','Minimum-fill, invalid options, EOF, ownership and cancellation; no silent ignored options.'],
  ReadableStreamBYOBRequest:['Reuse actual SM global.','respondWithNewView and wider boundary semantics unverified.','byob-basic','respondWithNewView, close/error and byte accounting.'],
  ReadableByteStreamController:['Reuse actual SM global.','Complete byte queue/auto-allocation semantics unverified.','byob-basic, byob-minimum','enqueue/autoAllocateChunkSize, cancellation/error, transfer boundaries.'],
  ReadableStreamDefaultController:['Reuse actual SM global.','Complete desiredSize/error/reentrancy semantics unverified.','readable-basic, pipe-to, tee','desiredSize, enqueue/close/error state and reentrancy.'],
  TransformStream:['Reuse actual Starling native class.','Complete strategy/cancel/error semantics unverified.','transform-basic','Writable/readable cancellation, errors, strategies and backpressure.'],
  TransformStreamDefaultController:['Capture real retained native constructor from existing public proto_obj root.','Global intentionally removed; prototype probe presently exports explicit unavailable function for this missing global.','transform-basic','Use real function; constructor/prototype/instance identity and illegal-constructor errors.'],
  WritableStream:['Reuse actual SM global.','Complete direct-close/error/abort-signal interactions unverified.','writable-basic, writable-abort, writable-backpressure, pipe-to','Direct stream.close, locked/error states and pipeline propagation.'],
  WritableStreamDefaultWriter:['Capture real cached/retained native constructor.','Global hidden with ClassSpec::DontDefineConstructor; prototype binding remains unavailable placeholder.','writable-basic, writable-abort, writable-backpressure','Use real function via existing JSAPI or retained prototype; no fabricated class.'],
  WritableStreamDefaultController:['Capture real cached/retained native constructor; native signal work needed.','Global hidden; controller.signal absent. Do not fabricate AbortSignal semantics from sink.abort.','writable-basic','Native controller-abort linkage, signal identity/event/reason lifecycle.'],
  ByteLengthQueuingStrategy:['Reuse actual SM global.','Complete conversions/descriptors/shared size-function behavior unverified.','queuing-strategies','Pinned conversions, invalid HWM, size reentrancy and property descriptors.'],
  CountQueuingStrategy:['Reuse actual SM global.','Complete conversions/descriptors/shared size-function behavior unverified.','queuing-strategies','Pinned conversions, invalid HWM, size reentrancy and property descriptors.'],
  TextEncoderStream:['Audited JS framing facade over native TransformStream and TextEncoder.','No native/global implementation found; prototype callable export throws explicitly.','','Cross-chunk high surrogate, flush/replacement, coercion, getters, cancel and backpressure.'],
  TextDecoderStream:['Audited JS facade over fixed native TextDecoder and TransformStream.','No native/global implementation found; prototype callable export throws explicitly.','','UTF8 split/BOM/fatal/flush, BufferSource ownership/shared policy, coercion and cancellation.'],
  CompressionStream:['Existing native zlib class; reuse deferred until source gates close.','Unchecked constructor result, borrowed input across allocating loop, missing owned-state teardown/finalizer.','','Harden source first; bounded gzip/deflate/raw/error/cleanup/backpressure differentials.'],
  DecompressionStream:['Existing native zlib class; reuse deferred until source gates close.','Same ownership gaps, empty unexpected-inflate-status branch and missing output/expansion budget.','','Harden source first; malformed/truncated/trailing data, bounded expansion, cleanup and backpressure.'],
};
const hidden=new Set(['TransformStreamDefaultController','WritableStreamDefaultWriter','WritableStreamDefaultController']);
const deferred=new Set(['TextEncoderStream','TextDecoderStream','CompressionStream','DecompressionStream']);
const rows=node.exports.map(name=>{
  if(name==='default')return{name,productionStatus:'deferred',candidateStatus:'partial',requiredHostInterfaces:[],
    strategy:'Ordinary mutable seventeen-member record, initial named/default identities; selected literal CommonJS default lowering only.',
    deviations:['Current isolated namespace uses explicit unavailable exports for five missing globals; not a native registered module.'],
    validation:['Exactly18 ESM names; no then export/Proxy/property-read trap; future native alias/cache/CJS/initfail gate.']};
  const[strategy,deviation,cases,validation]=details[name];assert(strategy,name);
  return{name,productionStatus:'deferred',candidateStatus:deferred.has(name)?'deferred':'partial',
    isolatedExportStatus:hidden.has(name)||name==='TextEncoderStream'||name==='TextDecoderStream'?'import-only':'partial',
    requiredHostInterfaces:[],nodeInventory:node.constructors[name],
    globalAvailability:proof.calls[0].globals[name].type,
    retainedNativeConstructorProven:hidden.has(name),strategy,deviations:[deviation],
    verifiedOrdinaryCases:cases?cases.split(', '):[],validation:[validation]};
});
assert.equal(rows.length,18);
await writeFile(new URL('./matrix.json',import.meta.url),JSON.stringify({node:'v22.14.0',module:'node:stream/web',aliases:['stream/web'],
  productionStatus:'deferred; uninstalled',requiredHostInterfaces:[],
  scope:'Source/candidate matrix, not a production export manifest or complete compatibility assertion.',
  ordinaryProof:{engineSha256:proof.engineSha256,componentSha256:proof.component.sha256,zeroImports:true,
    cases:11,exactMatchesForRecordedFields:9,deviations:proof.differences.map(value=>value.name),
    backends:['Jco-hosted Wasm','Wasmtime42.0.1']},
  retainedConstructorProof:{report:'constructors-component-results.json',componentSha256:constructorProof.component.sha256,
    zeroImports:true,writerNewWriteCloseRelease:true,controllerCallAndNewTypeErrors:true,
    deviations:['Node-specific invalid/locked writer and illegal controller construction error codes are absent.',
      'Native TransformStreamDefaultController.length is1; Node22 length is0.'],
    jsGetClassObjectExecuted:false},rows},null,2)+'\n');
console.log('PASS exact18-export source/candidate matrix generated');
