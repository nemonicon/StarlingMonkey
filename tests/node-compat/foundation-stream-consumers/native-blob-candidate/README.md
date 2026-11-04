# Unapplied native Blob ownership candidate

This is an **uncompiled source candidate** for later Blob-dependent consumers. It changes no production source, CMake target, module manifest/version or host interface. No native Blob test, invalid-receiver probe, getter/detach/shared/OOM probe or build has run. The v7 source control and all previous consumers diagnostics remain unchanged.

[blob-owned-copy-v1.patch](blob-owned-copy-v1.patch) changes only `builtins/web/blob.{cpp,h}` and `builtins/web/file.{cpp,h}` in `source/`. `base/` preserves the same four files from the actual immutable v7 OFF engine, SHA `ee92d5d451c16eb7ce83e0306e8dab6920f4aacd9f2c4bb9d6e5e4af2c20ea09`, with all four input hashes checked against its 293-input receipt. Existing web targets already compile these files; no new embedding API or build mechanism is introduced.

## Exact public API proof first

[api-proof.json](api-proof.json) records 12 actual pinned Release headers and 20 matched declarations/contracts. `api-proof.mjs` checks those bytes; it does not compile source. Relevant calls are the declared `JS::NewArrayBuffer`, `JS::GetArrayBufferData` with `AutoCheckCannotGC`, view backing/data APIs, `GetMaybePtrFromReservedSlot`, `JS_malloc`, `JS_string_malloc`, `JS_NewUCString`, Promise helpers, Vector reserve/infallible append and `ForOfIterator::closeThrow`.

The pinned ArrayBuffer header requires JS_free-compatible input for `NewArrayBufferWithContents`. The candidate removes that handoff entirely from Blob outputs. `JS::NewArrayBuffer` allocates the output object before any destination data pointer is acquired. Rooted Blob self keeps the native byte vector alive across allocation/GC. The vector stores only native bytes and does not move with the JS object. The destination pointer is reacquired inside a bounded NoGC scope; one explicit native-to-JS payload copy finishes there. Zero length bypasses raw pointers/copy. No allocator pointer is transferred between families.

`bytes()` roots that ArrayBuffer, then creates the declared Uint8Array view after the copy has ended. `arrayBuffer()`/`bytes()` root results before Promise resolution. All `ResolvePromise` bool results propagate; no raw byte span survives potentially observable thenable/prototype resolution. Any representation copying internal to SpiderMonkey is outside the one-explicit-copy statement; no empirical performance claim is made.

## Candidate changes and failure boundaries

| Area | Concrete source change |
| --- | --- |
| Receiver/part identity | Blob's existing `is_instance` signatures now require registered class identity **and initialized native Data**. File additionally requires initialized name/lastModified. Prototypes and failed/partial construction cannot pass to private data reads. Registered native File remains a valid Blob part. |
| Invalid async-method receiver | `arrayBuffer`, `bytes` and `text` use the existing `ReturnPromiseRejectedWithPendingError` helper before data access. Ordinary invalid receivers return rejected promises; failure to create such a Promise can still throw an allocation failure. `slice`/`stream` and accessors retain synchronous TypeError paths. Exact Node error codes/text are not promised. |
| Output storage | Replace `new[]`/JS_free handoff with a fresh rooted JS-owned ArrayBuffer and a scoped copy. Zero-length output is valid fresh storage. |
| Constructor append | Materialize/root backing first, validate fixed/attached/unshared storage, check total length and reserve before borrowing. Use public `infallibleAppend` only after successful reserve and under NoGC for JS bytes. Empty input never performs pointer arithmetic. No early copy before that Blob constructor's processing of each part is introduced. |
| Append failure | SystemAllocPolicy does not report JS errors. Checked range overflow reports allocation overflow; failed reserve installs OOM if no exception is already pending. Body failure invokes `closeThrow` after the borrow scope; `next()` failure is not closed twice. |
| Slice | Reacquire immutable native source after conversions/allocation. Positive allocation failure returns with pending error before creation; it cannot silently create an empty Blob. The owned JS-compatible buffer transfers only into the existing same-family native vector path. |
| Text | Empty Blob resolves to empty string without decoder allocation. Nonempty text checks output arithmetic, uses the public string-specific fallible allocator with its declared adopting string API, validates decoder completion and propagates Promise/error results. No borrowed JS input is involved. |
| Partial construction | Publish Data last, after scalar slots/native allocation. Reject null parts before allocation. Finalization accepts undefined Data and never calls a getter/receiver predicate on a partial object. Root option conversion strings and stop on failed ToString. |
| File ownership | File currently uses DefaultClassPolicy even though Blob::init allocates its native vector. The candidate installs its own FinalizableClassPolicy operation forwarding exactly once to Blob cleanup. JS prototype inheritance does not inherit JSClassOps; no automatic second parent finalizer is assumed. |

The checked native maximum is `PTRDIFF_MAX` bytes (2,147,483,647 on wasm32) so pointer ranges remain representable. Actual allocation limits can be lower. This is a native guest bound, not a new globally reserved Node profile version. Future consumer limits remain much smaller and separately declared.

Backing validation is an explicit **conservative tightening** of the old implicit acceptance: direct/shared-backed input, resizable backing and detached backing reject with TypeError. No shared bytes are read and no atomic-copy policy is inferred. This is not full WebIDL conformance. The coordinator must review that choice before applying the patch.

## Finalization, tracing and callback lifetimes

The exact existing class mechanism is `include/builtin.h::FinalizableClassPolicy::class_ops`, which supplies the class's own finalize callback and background-finalize flag. `BuiltinImpl::init_class_impl` passes the concrete class and parent **prototype** independently to `JS_InitClass`. File's new callback forwards once to Blob's native cleanup; Blob cleanup reads only the reserved native pointer and destroys the byte vector. It consults no mutable subclass registry, invokes no receiver guard/getter/JS callback, stores no reference to the dead object and allocates nothing. This matters because the public `JSFinalizeOp` contract applies to unreachable objects and background finalization is permitted.

`Blob::Data` contains a private byte-only vector, requiring no private GC edge. Type is a JS string stored through `JS::SetReservedSlot`'s GC barrier; Endings is an integer and Readers is currently unused/undefined. File's name is a reserved JS string and lastModified a number. The public `JSTraceOp` contract requires TraceEdge for traceable things in private native data: adding any JS callback/value to the private vector later would require a separate traced design.

Existing stream lifetimes are recorded but unchanged: `BufReader::User` retains the Blob, `BufReader::Stream` retains its NativeStreamSource, and source Owner/Stream/InternalReader/StartPromise/PipedToTransformStream are reserved JS values. The pull/cancel/read entries are private **native function addresses**, not untraced JS callbacks. The queued `StreamTask` owns a `Heap<JSObject*>` reader and explicitly traces it; `runtime/event_loop.cpp::TaskQueue::trace` reaches task trace methods through its PersistentRooted queue. Thus queued work can retain Blob storage after cancellation. Fixing that cancellation/resource lifetime is separate from this output-copy patch.

## Deliberately unresolved

* **No stream fix:** Blob.stream still constructs a default stream, lacks Node's byte/BYOB behavior, has a no-op cancel path and an unchecked task allocation. Output arrayBuffer/bytes/text correctness must not be advertised as stream correctness. No stream source file is changed.
* **No full fallibility/OOM claim:** the Rust decoder constructor can abort on allocator failure internally; checking a null result does not make that API fallible. Existing C++ string normalization/endings allocation behavior also remains. No genuine OOM/fault injection is run or approved by this source candidate.
* **Options/WebIDL remain partial:** parts are still processed before options; has/get ordering and numeric type normalization differ from pinned Node, invalid endings are still handled by the old policy, and full slice coercions are not corrected. The new rooted endings conversion only avoids using a null conversion result. Consumer construction with default options does not exercise these broader options, but does not erase the deviations.
* **Blob public identity remains open:** Node global Blob equals `node:buffer.Blob`; the current profile's latter export is still a stub. This patch promotes neither it nor any consumer export. File's default lastModified still uses its existing clock path; future pure tests must set an explicit lastModified and audit imports.
* **Related caller issues are not silently fixed:** structured-clone and body/form-data callers still need their own lifetime/error-path review. This patch preserves their existing C++ signatures and native-vector ownership route.

## Review and later Release gates

Before any native probe, review the API/pointer/partial-state/finalizer scopes and compile this isolated candidate against the actual Release headers/WASI target using the repository's existing web build targets. Build a new hash-receipted engine only after coordination; preserve v7 artifacts. `git apply --check` passing is not compilation.

Then use bounded ordinary Node and **patched-engine** tests for empty/nonempty/offset views, source mutation after construction, repeated independent arrayBuffer/bytes results, BOM/malformed UTF8 text, finite slice ranges, nested Blob/File inputs and explicit File lastModified. Invalid receivers/prototypes may be tested only once the guard patch is compiled and its exact source receipt is checked. Check rejected-Promise versus synchronous paths and ordinary iterator-close/error precedence. Keep shared/detach/getter/fault tests excluded unless separately scoped and reviewed; no old unsafe control is needed.

Run actual components with snapshot/resumption, retained Jco calls and fresh Wasmtime, exact zero imports for pure memory cases, and the existing normal Blob integration route. Only after these gates should bounded Blob-dependent `blob`/`arrayBuffer`/`buffer` consumer candidates be enabled and compared with their retained-reference Node corpus; do not copy parts when yielded. Request/resource lifecycle and the existing joint host fixture remain later gates, without new host services or runtime modifications.

[source-receipt.json](source-receipt.json) pins the four-file patch, public header proof, unchanged linkage sources and unchanged consumers source/component freezes. No production edit/build or runtime validation is represented by that receipt.
