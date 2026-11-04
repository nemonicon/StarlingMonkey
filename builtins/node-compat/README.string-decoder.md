# Optional bounded StringDecoder

This is the source for the optional **m0.4** UTF-8/hex foundation. Select
`NODE_COMPAT_STRING_DECODER=ON`, default OFF, in an explicitly
selected core Node profile. It requires the existing Buffer constructor and
the corrected ordinary native TextDecoder borrow path. The installed v6
Release component gate passes on Jco-hosted Wasm and stock Wasmtime42.0.1;
the selected support remains deliberately bounded.

The finite [manifest](export-manifest.string-decoder.node-v22.14.0.json) selects
`node:string_decoder` and bare alias `string_decoder`. Both module records must
use the same values. There are exactly two ESM bindings, `StringDecoder` and
`default`; the ordinary mutable default object initially contains only the
same constructor. Named bindings retain their initial identity when the
default object is changed. Selected literal CommonJS lowering returns that
default object; runtime require and ESM mutation synchronization are excluded.

[`string-decoder.mjs`](string-decoder.mjs) exports an implementation factory,
not another public Node binding. It accepts the already-rooted core Buffer
constructor and returns the two-binding record. The independent
[`generate-string-decoder-factory.mjs`](generate-string-decoder-factory.mjs)
packages it as `kStringDecoderFactorySource` in
[`string-decoder-factories.generated.h`](string-decoder-factories.generated.h).
The existing native `evaluate_factory` mechanism can invoke it after Buffer
construction, before public global Buffer installation. A normal CMake build
consumes the checked-in header without Node/npm. OFF builds must neither
include this header nor install its two native module IDs.

UTF-8 aliases and hex are supported. Undefined, null and empty labels select
UTF-8; recognized labels are case-insensitive. Other Node-recognized encodings
throw `ERR_SM_NODE_UNSUPPORTED`, with module/operation/profile metadata, when
constructed. Unknown labels throw `ERR_UNKNOWN_ENCODING`. Top-level calls
retain those failures during componentization. No blank namespace or Proxy
stands in for a module or deferred operation.

`write` returns string inputs unchanged before receiver validation. Byte inputs
must be ordinary fixed, unshared ArrayBufferViews, interpreted as raw bytes at
their native offsets and bounded to 16 MiB. Bare ArrayBuffers and
shared/resizable/detached views are rejected. Bulk UTF-8/hex uses captured core
Buffer methods, selecting the existing native codecs/kernels. The facade
copies at most three carried UTF-8 bytes into owned state; it retains no input
pointer or application view after the synchronous operation.

Every instance owns seven-byte fixed Buffer state. `lastChar` returns a fresh
live four-byte Buffer view into the same storage; `lastNeed`/`lastTotal` expose
the tested counts. Public `encoding` writes do not change the private encoding.
Carry-byte writes remain observable. The facade preserves `end`'s observable
receiver `write` and `text`'s counter clearing before observable `slice(offset)`.
Native view getters, Buffer methods, WeakMap access and error constructors are
captured before application code executes. Intentional `write`/`slice`
callbacks occur outside a native borrowed-pointer scope.

Arbitrary replacement/corruption of the exposed internal-symbol storage,
encoding marker or counter fields is excluded. A detached state buffer or
out-of-range counts produce `ERR_SM_NODE_DECODER_STATE`; this is a profile
safety policy rather than a Node internal-state compatibility promise. The
core Buffer's pool machinery, wider encodings, exotic constructors/species and
cross-realm behavior remain unimplemented or unclaimed. There is no host
capability, live handle, entropy read, clock or async scheduler dependency.

Node attribution and exact source/prototype provenance at source creation are in
[`LICENSE.string-decoder`](LICENSE.string-decoder) and
[`string-decoder-sources.json`](string-decoder-sources.json). The preserved
original prototype and private receipts are preserved as historical evidence.
The [installed native gate](../../tests/node-compat/foundation-string-decoder/native-component-results.json)
now verifies 2,982 UTF-8/hex sequences / 8,886 writes and 40 ordinary generic
decoder cases per run, snapshot/reuse, strict calls, ESM/default/CJS identities,
uncached aliases, detached owned state, intrinsic replacement and top-level
failures. Both components emit zero host imports. Two existing generic decoder
ordering deviations are explicit: invalid-input validation precedes stream
getters and constructor options are read once. SharedArrayBuffer was
unavailable in the tested guest. No complete StringDecoder/WebIDL,
fault-injection, raw-memory, fatal-error recovery or allocator-recovery claim
follows from this work.

The coordinated HTTP fixture also passed on stock Wasmtime and official
wasmCloud. Its exact component, six selected standard WASI0.2.10 imports and
three-request results on each host are archived in the immutable
[foundations-v6 checkpoint](../../tests/node-compat/milestones/foundations-v6/README.md).
That application evidence is separate from the pure zero-import module gates.

After source changes, generation and validation commands are:

```sh
node builtins/node-compat/generate-string-decoder-factory.mjs
node builtins/node-compat/generate-string-decoder-factory.mjs --check
```
