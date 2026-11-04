# encodeInto source audit (SM147)

This is a source audit plus a **Node-only** ordinary-API oracle. It is not a
native fault test, and no detached/shared destination was passed to the old
StarlingMonkey implementation.

The audited SpiderMonkey revision is
`9dab3d6f643e926a340c391ea30968e940390dec`. The current
`TextEncoder::encodeInto` obtains `JS::ToString`, then the Uint8Array destination
pointer through `JS_GetObjectAsUint8Array`, and calls the partial UTF-8 encoder.
For an ordinary attached, unshared Uint8Array, the inspected call path does
**not** establish a MayGC stale-pointer defect:

- [`JS_EncodeStringToUTF8BufferPartial`](https://github.com/bytecodealliance/firefox/blob/9dab3d6f643e926a340c391ea30968e940390dec/js/src/jsapi.cpp#L3635)
  enters `AutoCheckCannotGC` and calls `JSString::encodeUTF8Partial`.
- [`JSString::encodeUTF8Partial`](https://github.com/bytecodealliance/firefox/blob/9dab3d6f643e926a340c391ea30968e940390dec/js/src/vm/StringType.cpp#L141)
  traverses rope constituents without flattening. Its stack uses
  `SystemAllocPolicy`, whose allocation failure returns Nothing without
  collecting or reporting a JS exception. Conversion reads the leaf spans
  under the no-GC token.
- [`JS_GetObjectAsUint8Array`](https://github.com/bytecodealliance/firefox/blob/9dab3d6f643e926a340c391ea30968e940390dec/js/src/vm/TypedArrayObject.cpp#L7333)
  performs the typed-array check and reads length/data without allocating for
  an ordinary unwrapped Uint8Array. This conclusion does not claim arbitrary
  cross-realm wrapper policies are callbacks-free.

There are separate source-backed hardening issues. The public `js/String.h`
contract explicitly says Nothing means OOM **without reporting an error**;
the caller currently returns false without installing an OOM exception.
Also, a detached or out-of-bounds destination can produce a null pointer with
length zero. The leaf conversion delegates to encoding_c_mem0.2.6 Rust entry
points using `slice::from_raw_parts_mut`, which requires a nonnull pointer even
for an empty slice. A zero-length early result avoids that call. These are
source findings; no unsafe native runtime probe was used. Shared output is a
separate atomic-write policy question and is not resolved here.

The proposed minimal production hardening is: root the coerced source string,
leave the existing source conversion order intact, skip the partial encoder
when destination length is zero, and call `JS_ReportOutOfMemory` on Nothing.
No production edit is made by this audit. Adding an explicit outer no-GC span
scope would document the borrow but is not evidence that the existing callee
can collect.

[`encode-into-oracle.mjs`](encode-into-oracle.mjs) is guarded to exact Node
v22.14.0. Empty/ascii/astral strings with a zero destination, detached views,
and fixed/tracking RAB views made out of bounds all return
`{read:0,written:0}`. Node rejects non-string sources with
`ERR_INVALID_ARG_TYPE` before invoking their coercion hooks. StarlingMonkey's
current ToString behavior is therefore a separate API deviation; the
hardening proposal does not silently change that behavior.

Exact local source hashes and the safe oracle output are recorded beside
this note. No conclusions about allocation-failure recovery or shared-memory
correctness follow from it.
