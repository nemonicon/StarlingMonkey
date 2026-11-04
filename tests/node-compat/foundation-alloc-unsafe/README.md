# Isolated zeroed `Buffer.allocUnsafe` dependency proposal

This experiment passes **10 Node differential groups**, **5 candidate-policy
groups**, and the actual readable-stream `BufferList.concat/_getBuffer` allocation
paths in a real v6 OFF component. Retained Jco calls `[1,2]` and fresh stock
Wasmtime42 call1 pass with **zero host imports**. The constructor field is patched
only inside the isolated fixture and restored in `finally`. Production Buffer and
manifests remain unchanged; `allocUnsafe` and `allocUnsafeSlow` still refuse use.

[node-results.json](./node-results.json), [component-results.json](./component-results.json)
and [integration-proposal.json](./integration-proposal.json) separate tested
candidate behavior from the unimplemented production change. No global profile
version is allocated here. Classic Streams remain deferred.

## Actual contract and demand

Pinned Node22.14 source `buffer::allocUnsafe` calls `validateNumber(size,'size',0,kMaxLength)`
then `allocate`. It accepts only primitive numbers; negatives, NaN and infinities
reject. Positive fractions truncate through typed-array construction. The ordinary
function has name `allocUnsafe`, arity1, ignores `this` and returns a real Buffer
on call, `new`, bound construction and custom new-target construction. Error types
and codes are observed in the oracle; detailed messages are not claimed equal.
Primary references are [the pinned method documentation](https://nodejs.org/download/release/v22.14.0/docs/api/buffer.html#static-method-bufferallocunsafesize),
[buffer.js](https://github.com/nodejs/node/blob/v22.14.0/lib/buffer.js),
[validators](https://github.com/nodejs/node/blob/v22.14.0/lib/internal/validators.js)
and the inspected [allocation tests](https://github.com/nodejs/node/blob/v22.14.0/test/parallel/test-buffer-alloc.js).

Small reference allocations may share Node's8192-byte slab with nonzero offsets.
Even a positive fraction yielding length0 can retain pooled backing. The candidate
deliberately provides exact fresh backing at offset0, independent of poolSize.
No assertion reads initial Node unsafe bytes: differential byte vectors initialize
the whole visible span before reading it. Pool observations record metadata only.
The candidate guarantees zeroing; reference contents are not a correctness oracle.

Locked readable-stream4.7.0 directly calls `Buffer.allocUnsafe` in
`lib/internal/streams/buffer_list.js::concat` and `_getBuffer`. No
`allocUnsafeSlow` use appears in the audited lib tree. The experiment extracts the
exact constructor/push/two allocation method bodies, hashes each excerpt and its
full original source, and injects only Buffer plus a captured typed-array set
helper. Their [MIT license/notice](./LICENSE.readable-stream) is retained here.
It does not bundle or implement classic Streams. The tested aggregation
paths fill every returned byte and preserve residual slice views. Slab-backed
reference allocations can share an ArrayBuffer while their visible ranges remain
disjoint; backing inequality is a candidate policy, not a Node requirement.

## Precisely bounded candidate

`createAllocUnsafeCandidate` is a test-only injected factory. Trusted code supplies
the existing native Buffer constructor before application mutation. It captures
the existing `Buffer.alloc` function and numeric validation intrinsics;
the returned normal function:

* requires a finite primitive number in `[0,16777216]` before truncation;
* truncates positive fractions and accepts signed zero;
* calls the captured allocator with the integer size;
* returns fresh **zeroed**, branded, fixed owned Uint8Array/ArrayBuffer storage;
* adds no pool, C++ kernel, raw byte borrow, allocator transfer, fallback, host
  service, import or public production installer.

Type errors have `TypeError`/`ERR_INVALID_ARG_TYPE`; numeric range errors have
`RangeError`/`ERR_OUT_OF_RANGE`. The raw-size cap means `16777216.25` rejects even
though reference truncation can yield16777216. `Buffer.alloc`'s existing integer
policy is unchanged. All other Buffer APIs, encodings, backing restrictions and
16MiB limits remain as the bounded core declares. Public poolSize changes do not
turn the candidate into a slab allocator. No Slow or legacy constructor support
is inferred.

Allocation/branding/tracing stay in existing `Buffer.alloc`: closures keep the
allocator and constructor reachable, and returned JS-managed buffers own their
storage. Slice/subarray/backing views retain normal shared relationships. There
is no borrowed pointer to root or pin in this wrapper, and none crosses await.
Capturing `Buffer.alloc` protects against later reassignment of that public slot;
it does not expand the underlying core's guarantees for arbitrary mutation of its
constructors/species/intrinsics.

## Validation and lifecycle

Node differential groups cover type/coercion refusal, nonfinite/negative sizes,
fractional/signed-zero lengths, written bytes, `this`/call/new/bind/derived/new-target
behavior, independent visible allocations and shared slice/backing offsets.
Candidate-only groups cover complete small-buffer zeroing, maximum size/zero
samples, exact no-pool backing including zero length, private allocator capture,
poolSize independence and original producer-error propagation. The producer error
is an ordinary mocked exception identity test, **not genuine OOM evidence**.

The actual guest fixture uses native `node:buffer`, runtime-loaded bare `buffer`,
default/global aliases and selected static CommonJS lowering. It installs the
candidate into the mutable constructor slot only for its dependency checks, then
restores the exact prior function/attributes. Before and after every component
call, all **91 original unsupported prototype methods** and both allocation
static call/new refusals still pass. A locally allocated owned snapshot buffer
retains its brand/content across calls. No public field is patched in the snapshot.

Five initialization checks pass: original static call/new still fail; candidate
wrong type and over-cap requests fail; an unawaited rejected microtask also fails
componentization. Legacy core diagnostics print operation/profile rather than its
runtime `code` field, so those two checks match the actual original message.
No detachment, shared memory, GC failure or allocator-fault injection is performed.

The full report verifies v6 OFF engine
`33b9cb248afbb4a3b3653c7b76bd656e51443e6823fa72d712758c742cd59516`, all285 frozen
inputs, exact Node22/Jco1.40/ComponentizeJS0.23 audited v2 packaging and adapter,
stock Wasmtime42 executable hash, source/bundle/component hashes and final WIT.
Only `run: func() -> string` is exported. The corpus/component size is not a product
size, startup, memory or throughput comparison.

## Integration proposal, not an assigned revision

The proposal checks production core hashes against frozen v6, keeps exports and
all91 prototype refusals intact, and specifies adding only this supported static
method while removing only `allocUnsafe` from the deferred-static list.
`allocUnsafeSlow` stays deferred. The existing facade/generator mechanisms suffice;
there is no additional C++ source, guest-host API or WASI interface to add.

A coordinator must assign a new core profile version, update the selected core
receipt coherently, regenerate the header and build a separate engine. Two
manifests defining `node:buffer` cannot be overlaid. Preserve old m0.1/v6 records and
their refusal gates; use version-selected tests for the changed static operation.
The hardcoded `unsupported.mjs::PROFILE_VERSION` must also follow the assigned
core version so refused Buffer/child_process errors agree with the receipt; retain
the old fixture expectation for old engines and keep all91 method checks.
Only then run production/source/native/joint-host gates and measure performance if
an improvement is claimed. Abort listener semantics, tick/context scheduling and
remaining Buffer/encoding demands still gate classic Streams.

Reproduce `run-node.mjs`, then `run-component.mjs` with the usual frozen engine,
source root, pinned toolchain/v2 packager/Wasmtime variables and optional
`NODE_COMPAT_ALLOC_UNSAFE_OUTPUT`, then `integration-proposal.mjs`. All files are
under this isolated directory; accepted v6 and production core files are untouched.
