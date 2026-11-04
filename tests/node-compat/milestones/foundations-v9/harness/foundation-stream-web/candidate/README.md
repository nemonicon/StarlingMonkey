# Isolated codec and receiver-guard candidate

This factory is **uninstalled**. It changes no builtin, CMake flag or production
global. The accepted eleven-case audit and retained-constructor receipts in the
parent directory remain separate. [contract.json](contract.json) is the finite
candidate contract; [source-pins.json](source-pins.json) pins audited Node22
sources and the corrected native decoder used by the component.

`createStreamWebModule(record)` accepts exactly sixteen own data-function
properties: thirteen existing stream classes, native `TextEncoder` and
`TextDecoder`, and `isReadableStreamBYOBReader(value) -> boolean`. The exact keys
are in the contract. The record contains no compression constructors. The
factory returns seventeen explicit bindings plus an ordinary default record
with matching initial identities. This is a record-composition test, not actual
module registration, alias resolution or CommonJS integration.

The native stream constructor/prototype identities are preserved. The two new
codec classes use captured native TransformStream and bulk codecs with private
WeakMap state. They do not install global codec names. Encoder chunks use
`String(chunk)`, including primitive Symbol, as the pinned Node stream does;
one trailing high surrogate is retained across chunks and replaced on flush.
Decoder supports **UTF8 only**, native label normalization, split UTF8, BOM,
fatal errors and flush. Known other native labels fail explicitly with
`ERR_SM_NODE_UNSUPPORTED`; unknown labels produce RangeError with
`ERR_ENCODING_NOT_SUPPORTED`. Decoder options preserve the pinned observable
`fatal, ignoreBOM, ignoreBOM, fatal` getter sequence and expose the first flags.

Decoder chunks are fixed, attached, unshared BufferSources, including ordinary
offset views and DataView. Shared, resizable and detached inputs fail with
`ERR_SM_NODE_UNSUPPORTED`. The underlying production TextDecoder retains its
own broader contract; this facade does not change it. Input validation reads
the intrinsic `.buffer` getter, which can materialize an inline typed array's
ArrayBuffer in SpiderMonkey. There is no zero-copy or performance claim.

Limits are 1,048,576 UTF16 source units per incoming encoder chunk, 16,777,216
bytes per incoming decoder chunk and 16,777,216 bytes per BYOB view. Rejections
are RangeError with `ERR_SM_NODE_LIMIT` and a resource name. These bound one
operation, not an application's retained chunks, total stream output or queue.
Native allocation exhaustion and Rust fatal-allocation behavior are not tested
or covered by these ordinary public-API tests.

The isolated BYOB wrapper validates receiver, view and options in the recorded
order, accepts the eleven ordinary local typed-array classes and default/null
minimum of one. It rejects `min > 1`, modified own layout properties,
subclass/cross-realm views, shared/resizable backing and DataView explicitly.
Empty/detached views retain the selected Node invalid-state error. A Proxy of a
genuine reader is accepted by Node22 but excluded here. This exclusion and the
profile error code are deliberate deviations, not Node parity.

The fixture brand callback is a private registry of fixture-created genuine
readers. It proves neither arbitrary native brands nor cross-realm behavior.
The proposed [native capture kernel](../native-kernel.template.cpp) uses the
actual public `JS::IsReadableStreamBYOBReader` and existing class roots; it is
**uncompiled and unused** here. Temporary fixture streams recover hidden
constructors only after deployed entry and are cleaned up. Production capture
must use the reviewed roots without temporary live initialization handles.

Eight native static/prototype descriptors are temporarily replaced by this
opt-in simulation and restored after every run: BYOB `read`, readable `from`,
`values`, async iterator, and four Transform controller operations. The
controller guards reject the uninitialized native prototype before delegation.
No old native prototype operation is invoked. A minimal separate
[native patch](native-controller-receiver.UNAPPLIED.patch) passes actual
SDK30/SM147 syntax checking but remains **unapplied, unlinked and untested at
runtime**. Its future integration gate must preserve genuine closed/errored
controller behavior and test invalid receivers on the new engine.

CompressionStream and DecompressionStream always throw identifiable deferred
errors on call or construction. Their native classes are neither retained nor
invoked. Writable controller `signal` remains absent. Readable `from`, `values`
and async iterator are explicit deferred callables in this frozen stage;
`values === prototype[Symbol.asyncIterator]` is preserved. Real serialized
iteration is a subsequent independent implementation stage.

## Ordinary proof

[Host results](host-results.json) compare against exact Node v22.14.0.
[Component results](component-results.json) retain all 285 immutable v6 native
input hashes, candidate source hashes, selected patched packager provenance and
final interface audit. The accepted component is
`14d8650b3e9b973ee4378f2ce7f8cd093dae71dc7d99570bfb4cb3c3d7523f0e`,
12,780,327 bytes, with **zero imports**. Its size includes test vectors and is
not a minimal module deployment or performance measurement. Two calls in
Jco-hosted Wasm and one fresh stock Wasmtime42.0.1 instance pass:

- 41 constructor, 250 codec and four cancellation/abort cases match recorded
  Node fields, including split surrogate/UTF8, malformed UTF8, BOM/fatal,
  coercion/getters, flush and brands.
- 24 receiver/options cases have 21 exact matches and three explicit policy
  differences: minimum two, Proxy receiver and modified layout properties.
- Eleven typed-array BYOB cases match; DataView is rejected before detachment
  or consumption and a subsequent Uint8Array read recovers all queued bytes.
- Six newly guarded controller cases match, including valid closed and errored
  instances. Sixteen policy checks cover accepted/rejected limits, backing
  policy, private record validation and rejection recovery.
- Captured intrinsic tests invoke no replacement functions; native constructor
  identities, uninstalled global codecs and all eight restored descriptors are
  checked after each call. SharedArrayBuffer is unavailable in this guest;
  the explicit shared-input rejections are exercised only in Node.

The earlier ordinary DataView failure is preserved in external output
`stream-web-candidate-v4`: native read rejected with `null is not a constructor`.
Pinned SM `ReadableStreamBYOBReader.cpp` leaves the DataView `ctor` root null
before later construction. The current guard never enters that known path.
A future same-backing Uint8Array adaptation needs separate EOF, cancellation,
error, transfer, offset, promise and constructor tests before adoption.

Prior accepted candidate receipts remain in external v3/v5 output directories.
No unsafe old-native receiver, compression transform, raw-memory operation,
allocator fault or forced-GC experiment is part of this proof.

```sh
/path/to/node-v22.14.0 tests/node-compat/foundation-stream-web/candidate/run-host.mjs
NODE_COMPAT_TOOLCHAIN=/path/to/locked-toolchain \
NODE_COMPAT_COMPONENTIZE_MODULE=/path/to/v2/package/src/componentize.js \
NODE_COMPAT_ENGINE=/path/to/frozen-v6-off.engine.wasm \
NODE_COMPAT_ENGINE_SOURCE_ROOT=/path/to/frozen-v6-source \
NODE_COMPAT_WASMTIME=/path/to/wasmtime-42.0.1 \
NODE_COMPAT_STREAM_CANDIDATE_OUTPUT=/path/to/fresh-output \
/path/to/node-v22.14.0 tests/node-compat/foundation-stream-web/candidate/run-component.mjs
```
