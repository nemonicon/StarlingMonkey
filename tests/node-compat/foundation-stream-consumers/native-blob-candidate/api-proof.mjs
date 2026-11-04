// Read-only pinned public-API proof. Does not compile or execute native code.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFile,writeFile} from 'node:fs/promises';
import {dirname,join} from 'node:path';
import {fileURLToPath} from 'node:url';
assert.equal(process.version,'v22.14.0');
const here=dirname(fileURLToPath(import.meta.url)),headers='/tmp/starling-node-compat/improved-build/spidermonkey-dist-release/include';
const hash=value=>createHash('sha256').update(value).digest('hex');
const specifications=[
  ['js/ArrayBuffer.h','NewArrayBuffer','extern JS_PUBLIC_API JSObject* NewArrayBuffer(JSContext* cx, size_t nbytes);',
    'Create GC-owned output directly. Null propagates the JSAPI allocation failure; root the object before any later allocation. No source pointer is passed into this allocating call.'],
  ['js/ArrayBuffer.h','GetArrayBufferData','extern JS_PUBLIC_API uint8_t* GetArrayBufferData(',
    'Acquire output data with AutoCheckCannotGC only after output allocation. Skip all raw pointers/copies for length0.'],
  ['js/ArrayBuffer.h','IsDetachedArrayBufferObject','extern JS_PUBLIC_API bool IsDetachedArrayBufferObject(JSObject* obj);',
    'Check a proven ArrayBuffer backing before copying; do not confuse detached length0 with an attached empty buffer.'],
  ['js/ArrayBufferMaybeShared.h','IsResizableArrayBufferMaybeShared','extern JS_PUBLIC_API bool IsResizableArrayBufferMaybeShared(JSObject* obj);',
    'Conservative candidate policy explicitly rejects resizable backing after proving the backing is an unshared ArrayBuffer.'],
  ['js/SharedArrayBuffer.h','IsSharedArrayBufferObject','extern JS_PUBLIC_API bool IsSharedArrayBufferObject(JSObject* obj);',
    'Reject direct shared input without reading shared bytes; the view backing API supplies its shared flag separately.'],
  ['js/experimental/TypedData.h','JS_GetArrayBufferViewBuffer','extern JS_PUBLIC_API JSObject* JS_GetArrayBufferViewBuffer(',
    'This may materialize/return detached backing; root returned backing before taking any raw view pointer.'],
  ['js/experimental/TypedData.h','JS_GetArrayBufferViewData','extern JS_PUBLIC_API void* JS_GetArrayBufferViewData(',
    'Use only for a proven view, under AutoCheckCannotGC, after reserve and backing validation.'],
  ['js/experimental/TypedData.h','JS_NewUint8ArrayWithBuffer','JS_FOR_EACH_TYPED_ARRAY',
    'The macro declarations instantiate JS_NewUint8ArrayWithBuffer; construct the view only after helper output is rooted and native copy has ended.'],
  ['js/Object.h','GetMaybePtrFromReservedSlot','inline T* GetMaybePtrFromReservedSlot(JSObject* obj, size_t slot)',
    'Public helper returns null for UndefinedValue and a private pointer otherwise; use for prototype/partial-constructor slots and finalization. Slot values remain only undefined or a native pointer under this candidate.'],
  ['js/Object.h','SetReservedSlot','inline void SetReservedSlot(JSObject* obj, size_t slot, const Value& value)',
    'Reserved JS::Value slots use the public GC barrier path for GC things. Keep JS owner/promise/callback values there, not in an untraced private native byte vector.'],
  ['js/Class.h','JSFinalizeOp','typedef void (*JSFinalizeOp)(JS::GCContext* gcx, JSObject* obj);',
    'Finalization is a JSClass operation on unreachable objects; it must not resurrect/store obj. File installs exactly one operation forwarding to Blob native-byte cleanup.'],
  ['js/Class.h','JSTraceOp','typedef void (*JSTraceOp)(JSTracer* trc, JSObject* obj);',
    'The public trace-hook contract covers traceable things in private data and requires TraceEdge on each location. ByteBuffer contains uint8_t only; stream task private Heap<JSObject*> already has an explicit trace edge.'],
  ['js/Promise.h','ResolvePromise','extern JS_PUBLIC_API bool ResolvePromise(JSContext* cx,',
    'Propagate the bool. The existing repository rejection helper roots/clears the pending exception only to reject a newly created promise.'],
  ['js/MemoryFunctions.h','JS_malloc','extern JS_PUBLIC_API void* JS_malloc(JSContext* cx, size_t nbytes);',
    'Fallible guest allocation for slice native storage, paired with JS::UniqueChars/FreePolicy and the native vector allocator. Null must return with pending OOM, never silently construct an empty Blob.'],
  ['js/MemoryFunctions.h','JS_string_malloc','extern JS_PUBLIC_API void* JS_string_malloc(JSContext* cx, size_t nbytes);',
    'Header explicitly documents this allocator for BYOB JS string creation such as JS_NewUCString. Pair with JS::UniqueTwoByteChars and its declared adopting API.'],
  ['js/String.h','JS_NewUCString','extern JS_PUBLIC_API JSString* JS_NewUCString(JSContext* cx,',
    'Consumes the exact UniqueTwoByteChars type. Decode to owned UTF16 storage, then hand it to this declared string API; no borrowed JS source data survives.'],
  ['js/AllocPolicy.h','SystemAllocPolicy','class SystemAllocPolicy : public AllocPolicyBase',
    'This policy performs no JS error reporting. Explicit checked lengths plus reserve-failure OOM reporting are required.'],
  ['mozilla/Vector.h','reserve','[[nodiscard]] bool reserve(size_t aRequest);',
    'Reserve checked total capacity before a borrowed input span exists.'],
  ['mozilla/Vector.h','infallibleAppend','void infallibleAppend(const U* aBegin, size_t aLength)',
    'Public contract explicitly guarantees these operations only on pre-reserved memory. Use after successful reserve so no allocator runs while borrowed JS bytes are live.'],
  ['js/ForOfIterator.h','closeThrow','void closeThrow();',
    'On append/conversion failure, close for throw completion after the NoGC borrow ends, preserving error precedence. Do not close again after next itself fails.'],
];
const files=new Map(),apis=[];
for(const[path,symbol,needle,use]of specifications){
  if(!files.has(path))files.set(path,await readFile(join(headers,path),'utf8'));
  const text=files.get(path),at=text.indexOf(needle);assert(at>=0,'Pinned API missing: '+symbol);
  apis.push({path,symbol,line:text.slice(0,at).split('\n').length,matchedDeclaration:needle,use});
}
const typed=files.get('js/experimental/TypedData.h');
assert.match(typed,/JS_New##Name##ArrayWithBuffer/);
const report={schema:1,candidateVersion:'native-blob-owned-copy-v1',compiled:false,nativeTestsRun:false,
  headersRoot:headers,files:[...files].map(([path,text])=>({path,sha256:hash(text),bytes:Buffer.byteLength(text)})),apis,
  existingMechanisms:{classPolicy:'include/builtin.h::BuiltinImpl / FinalizableClassPolicy; existing Blob/File web targets',
    ownership:'Blob reserved Data slot owns a byte-only js::Vector; File must install its own finalizer forwarding to Blob because prototype inheritance does not inherit JSClassOps.',
    noNewHostService:true,newWasiImports:[]},
  limits:'Append total length is checked against PTRDIFF_MAX before reserve to keep pointer ranges representable; the candidate is not a complete arbitrary-size Web Blob implementation.',
  unresolved:['C++ source is uncompiled until coordinator review; declarations alone do not prove final call-site compilation.',
    'Rust decoder allocation failure can abort internally; a null check does not prove fallible Rust allocation or genuine OOM behavior.',
    'Blob.stream byte-stream/default-stream and queued-task cancellation are outside this patch.',
    'Constructor options ordering and full WebIDL/Node Blob semantics remain separate compatibility work.']};
await writeFile(join(here,'api-proof.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({headers:files.size,apis:apis.length,compiled:false,nativeTestsRun:false}));
