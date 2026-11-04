// Proof addendum only; preserve all reviewed v1 files and receipts verbatim.
import assert from 'node:assert/strict';
import {readFile,writeFile} from 'node:fs/promises';
import {dirname,join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
assert.equal(process.version,'v22.14.0');
const here=dirname(fileURLToPath(import.meta.url)),hash=v=>createHash('sha256').update(v).digest('hex');
const prep=JSON.parse(await readFile(join(here,'preparation-receipt.json'))),sources=new Map();
for(const item of prep.proofSources){const bytes=await readFile(join(here,'proof-source',item.path));assert.equal(hash(bytes),item.sha256);sources.set(item.path,bytes.toString());}
function point(path,needle,meaning){const text=sources.get(path),index=text.indexOf(needle);assert(index>=0,needle);return{path,line:text.slice(0,index).split('\n').length,needle,meaning};}
const decoder=[
  point('rust-encoding.h','constexpr static const uint32_t INPUT_EMPTY = 0;','Status0 is exactly INPUT_EMPTY.'),
  point('rust-encoding.h','UTF-16 code units (`u16`) of space.','Output must have at least two writable UTF16 units; v2 enforces this.'),
  point('rust-encoding.h','size_t decoder_max_utf16_buffer_length','Worst-case UTF16 capacity; SIZE_MAX signals size_t overflow and is rejected before multiplication.'),
  point('rust-encoding.h','the processing of the stream has ended.','With last=true and InputEmpty, the decoder stream is complete.'),
  point('encoding_c-0.9.8/lib.rs','fn coder_result_to_u32','Maps CoderResult::InputEmpty to INPUT_EMPTY and OutputFull to OUTPUT_FULL.'),
  point('encoding_c-0.9.8/lib.rs','pub unsafe extern "C" fn decoder_decode_to_utf16(','The wrapper builds slices using input lengths, then overwrites src_len with bytes read and dst_len with UTF16 units written.'),
];
const allocator=[
  point('js/src/jsapi.cpp','JS_PUBLIC_API void* JS_malloc(JSContext* cx, size_t nbytes)','Calls cx->maybe_pod_malloc<uint8_t>(nbytes).'),
  point('js/src/vm/JSContext.h','public js::MallocProvider<JSContext>','JSContext uses this exact allocator mixin.'),
  point('js/src/vm/MallocProvider.h','T* maybe_pod_malloc(size_t numElems)','Selects js::MallocArena and calls maybe_pod_arena_malloc.'),
  point('js/src/vm/MallocProvider.h','T* maybe_pod_arena_malloc(arena_id_t arena, size_t numElems)','Calls js_pod_arena_malloc<T> in that arena; updates GC allocation counter separately.'),
  point('js/Utility.h','static MOZ_ALWAYS_INLINE T* js_pod_arena_malloc','Uses checked byte-size arithmetic, then js_arena_malloc for that arena.'),
  point('js/AllocPolicy.h','class SystemAllocPolicy : public AllocPolicyBase','Vector policy inherits the same native allocator implementation, without JS exception reporting.'),
  point('js/AllocPolicy.h','T* pod_malloc(size_t numElems)','AllocPolicyBase also selects js::MallocArena.'),
  point('js/AllocPolicy.h','T* pod_realloc(T* p, size_t oldSize, size_t newSize)','Subsequent vector growth uses the same js::MallocArena realloc family.'),
  point('js/AllocPolicy.h','void free_(T* p, size_t numElems = 0)','Vector destruction routes to js_free.'),
  point('mozilla/Vector.h','void replaceRawBuffer(T* aP, size_t aLength);','Requires input allocated according to this Vector AllocPolicy; matching MallocArena allocation satisfies that contract for byte elements.'),
  point('js/Utility.h','struct FreePolicy {','UniqueChars uses js_free until release; transfer leaves exactly one vector owner.'),
  point('js/src/jsapi.cpp','JS_PUBLIC_API void* JS_string_malloc(JSContext* cx, size_t nbytes)','String output deliberately uses StringBufferArena and the declared adopting string API, not the vector adoption path.'),
];
const source=await readFile(join(here,'source/builtins/web/blob.cpp'),'utf8');
assert.match(source,/std::max\(maximum, size_t\{2\}\)/);assert.match(source,/size_t written = capacity;/);assert.match(source,/status != jsencoding::INPUT_EMPTY/);
const report={schema:1,candidateVersion:'native-blob-owned-copy-v2',v1Preserved:true,v1IndexSha256:prep.v1IndexSha256,
  spiderMonkeyRevision:prep.spiderMonkeyRevision,proofSources:prep.proofSources,decoder,allocator,
  conclusion:{decoder:'Nonempty input/output pointers are valid; full checked writable capacity >=2 is passed; success requires INPUT_EMPTY, consumed==source_length and written<=capacity. Empty Blob returns before FFI.',
    allocation:'JS_malloc -> JSContext/MallocProvider -> MallocArena -> js_pod_arena_malloc. SystemAllocPolicy -> AllocPolicyBase -> same MallocArena allocation/reallocation and js_free; replaceRawBuffer adoption is within this explicit family, not merely free-compatible.',
    separateAccounting:'JSContext allocation-counter updates differ from SystemAllocPolicy. This proves allocator-family compatibility, not complete external-memory pressure/accounting; native-vector GC accounting still deserves a separate bounded-memory review.'},
  compiled:false,linked:false,nativeTestsRun:false};
await writeFile(join(here,'contract-proof.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({decoderContracts:decoder.length,allocatorSteps:allocator.length,v1Preserved:true,compiled:false}));
