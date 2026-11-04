# Public ownership/zeroing proof and its limits

The proposal uses ordinary JavaScript `new U8(integerLength)` with the existing
trusted Uint8Array constructor captured by `createBufferModule`; it introduces
no embedding API. Its existing `tagTrusted` changes the genuine view's prototype
and records it in the closure-owned WeakSet. The object remains JS-managed.

ECMA-2622025's [AllocateTypedArrayBuffer](https://262.ecma-international.org/16.0/#sec-allocatetypedarraybuffer)
allocates an ArrayBuffer and sets typed-array length/offset metadata.
[AllocateArrayBuffer](https://262.ecma-international.org/16.0/#sec-allocatearraybuffer)
uses [CreateByteDataBlock](https://262.ecma-international.org/16.0/#sec-createbytedatablock),
which initializes the block to zero and specifies a failure when allocation is
impossible. These stable16th-edition contracts establish zero initialization;
they do not prove an engine's genuine OOM behavior or memory consumption.

The retained [SM147 public TypedData.h](./proof/TypedData.h) documents zero filling
for length-based JS_New typed-array creation (excluding WithBuffer). Its exact
local path/hash are in source-receipt.json. This corroborates the native engine's
public typed-array contract; **the candidate does not call JS_NewUint8Array** or
assume a new undocumented embedding entry point.

Frozen source `builtins/node-compat/buffer-facade.mjs` already captures U8, uses
`new U8(length)` in Buffer.alloc/FastBuffer, and privately brands trusted results.
Candidate allocation follows the same numeric constructor path after unchanged
primary bounded validation. No external storage, borrowed byte view, allocator
family crossing, raw pointer, live host handle or resource lifetime is introduced.
The ordinary VM manages transient references and the returned object; captured
bound WeakSet methods retain the brand set. The source does not eagerly access
`.buffer`, preserving the existing delayed materialization of inline storage.

This source/API reasoning plus four host semantic forms does not establish linked
native behavior. The future installed component corpus must verify actual engine
branding/views/call/new/initialization and snapshot resumption. Failure injection,
private heap access, DEBUG/OOM tests, shared/detached adversarial probes and
performance attribution are expressly absent.
