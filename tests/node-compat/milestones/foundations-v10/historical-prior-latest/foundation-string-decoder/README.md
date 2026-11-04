# Bounded StringDecoder investigation and integration

This directory preserves a **host-tested prototype and a separately built private
native candidate**, followed by the optional bounded production module's
ordinary integration gate. The module implements UTF-8/hex only and requires
explicit feature selection; it is not complete `node:string_decoder` support.
The compatibility oracle is exact Node **v22.14.0**. Source hashes are in
[`source-pins.json`](source-pins.json).

The ordinary private candidate has now passed a real component gate on
Jco-hosted Wasm and stock Wasmtime42.0.1. A cleaned production variant has since
been applied and passed its coordinated v6 installed-module gate.
The private gate uses no fault injection, raw-memory
inspection or unsafe old-native detached/shared-input probes.

## Verified inventory and existing implementations

The pinned module has exactly two ESM names: `StringDecoder` and `default`.
The default is an ordinary object whose `StringDecoder` initially equals the
named function. The function has name `StringDecoder`, arity 1, and an ordinary
prototype with `write`, `end`, `text`, `lastChar`, `lastNeed`, and `lastTotal`.
All six members are enumerable/configurable; methods are writable. The three
state properties are getters. Plain invocation fails, while
`StringDecoder.call(receiver)` initializes an ordinary object receiver.

Instances have a writable/enumerable/configurable `encoding` property and an
enumerable `Symbol(kNativeDecoder)` property containing a seven-byte Buffer.
Its first four bytes back the fresh, live four-byte Buffer view returned by
each `lastChar` read. Missing-byte and buffered-byte counters occupy offsets 4
and 5; offset 6 is the native encoding enum. `lastTotal` is their sum. Changing
the public `encoding` property does not change the private decoder encoding.
See [`inventory-results.json`](inventory-results.json).

Node accepts case aliases for UTF-8, UTF-16LE/UCS-2, hex, ascii, latin1/binary,
base64 and base64url. Undefined, null and an empty encoding select UTF-8.
Normalization first reads the original `length`; recognized lengths then permit
captured String lowercasing/coercion. Boxed strings and matching custom objects
can therefore normalize successfully. Other values produce TypeError
`ERR_UNKNOWN_ENCODING`. This differs from WHATWG label normalization.

`write` accepts strings unchanged, even before checking its receiver. Strings
do not consume pending bytes. Byte input must be an ArrayBufferView: all typed
array element types and DataView are interpreted as raw bytes with byte offsets
and lengths. Bare ArrayBuffer is rejected. Invalid input is checked before the
ordinary receiver check. Null/undefined receivers can produce plain TypeError;
an ordinary uninitialized object produces `ERR_INVALID_THIS` for byte writes.

`end(input)` calls the receiver's observable `write` method, then flushes
pending bytes and resets the counts. Storage bytes remain observable. `text`
is legacy behavior: it clears counts **before** calling `input.slice(offset)`
and then `write`. Consequently DataView has no supported `slice`, typed-array
offsets count elements, and a failed slice still leaves the counts cleared.

Inspected sources/tests:

- [Node v22.14.0 lib/string_decoder.js](https://github.com/nodejs/node/blob/v22.14.0/lib/string_decoder.js),
  `StringDecoder`, `write`, `end`, `text` and the state accessors;
  [native DecodeData/FlushData](https://github.com/nodejs/node/blob/v22.14.0/src/string_decoder.cc).
- Node's pinned `test-string-decoder.js` and `test-string-decoder-end.js`,
  including split sequences, malformed UTF-8, receiver errors and end/reuse.
- Jco1.40 `packages/jco/src/node-builtins/string-decoder.ts`, its component
  fixture, and jco-std0.10's Node24 implementation and differential tests.
  The actual current adapter uses jco-std, rather than the unenv fallback.
  Its `inputBytes` copies each view through `Buffer.from`; `utf8Write` can
  concatenate the carried prefix with the whole new input. Its mutable
  `this.encoding` dispatch and DataView `text` behavior differ from this pin.
- unenv's shim selects a global `StringDecoder` or an explicit unimplemented
  class. The installed historical `string_decoder` package was inspected as
  an algorithm reference, not assumed to be the current Jco implementation.
- StarlingMonkey `TextDecoder::decode`, constructor/finalizer,
  `runtime/builtin.cpp::value_to_buffer`, encoding_c0.9.8 and encoding_rs0.8.35,
  and existing `tests/integration/textdecoder`/stream usage.

## Why native TextDecoder is not the whole implementation

Current native TextDecoder **does support** `stream:true`. Nevertheless, the
per-call outputs differ from Node StringDecoder:

| UTF-8 chunks | Node outputs | WHATWG streaming outputs |
| --- | --- | --- |
| `c0`, `80` | `""`, `"��"` | `"�"`, `"�"` |
| `f0 8f`, `80 80` | `""`, `"����"` | `"��"`, `"��"` |
| `ed a0`, `80` | `""`, `"���"` | `"��"`, `"�"` |

Node defers syntactically incomplete tails even when their scalar-value range
is invalid. Its public carry bytes/counts also require explicit state.
UTF-16LE preserves lone surrogate code units and ignores an odd final byte;
WHATWG decoding replaces them. ASCII masks the high bit, while WHATWG ascii
and latin1 labels map to windows-1252. Base64 and hex are byte-to-text encodings,
not TextDecoder character decoders. These are verified safe host observations,
not an inference that native encoding_rs has passed every malformed case.

## Bounded prototype contract

[`prototype.mjs`](prototype.mjs) implements only **UTF-8 aliases and hex**.
Other recognized Node encodings throw `ERR_SM_NODE_UNSUPPORTED` at construction;
unknown encodings retain `ERR_UNKNOWN_ENCODING`. It exposes the exact proposed
two-binding module record, ordinary default object, constructor/prototype shape,
seven-byte owned state, and live four-byte `lastChar` views. It does not register
that record as an ESM builtin yet.

The UTF-8 framing is adapted from pinned Node's native algorithm. At most three
pending bytes are copied into owned state. Completed prefix and bulk regions
are decoded through **captured Buffer.from(ArrayBuffer,offset,length) and
Buffer.prototype.toString** methods. With the profile Buffer these select its
existing native UTF-8/web decoder and hex kernel, without Buffer.concat or a
full-input Buffer copy. The dependency uses only methods already in M0.
The prototype does not allocate a native TextDecoder per StringDecoder or pass
application options to one.

Each byte input is limited to 16 MiB. `write` preserves pending state on limit
failure; legacy `text` clears it first, then rejects large views before slice
can copy them.
Hex output is consequently at most 32 Mi UTF-16 code units. String input is a
zero-copy pass-through. Shared, resizable and detached backing stores are
explicitly excluded. Captured native view getters ignore shadowed `buffer`,
`byteOffset` and `byteLength` properties. Private WeakMap state keeps the
construction-time encoding; public `encoding` mutations and live carry-byte
mutations follow the tested Node behavior. Ordinary `.call(receiver)` works.

Detailed received-value text, `Buffer.isEncoding` extension monkey-patches,
forged receivers, arbitrary private-symbol/counter corruption, exotic
constructors/species and unsupported profile Buffer overloads are excluded.
Corrupt legacy storage is rejected rather than passed to a native decoder.
The profile Buffer's broader deviations still apply; this is not complete
Node Buffer support. Each decoder owns its carry state; `.end()` is an API
flush/reset, not a host-handle close. Component reuse must preserve this
observable per-instance state rather than treating it as implicit request state.
Reading `.buffer` to create a branded view can materialize SpiderMonkey inline
typed-array storage. No full-input Buffer copy is requested, but the actual
small-input allocation cost still needs measurement; a private codec accepting
views directly may avoid that materialization if measurements justify it.

Host-only differential validation passes **137,520 sequences / 283,984 writes**
across two dependencies: real NodeBuffer and the current M0 facade with its
explicit JavaScript reference kernel. This includes every 65,536 two-byte split
pair per dependency, all cuts of curated valid/malformed byte sequences,
deterministic longer fuzz, all typed-array widths/DataView offsets, end/reuse,
constructor/prototype/state inspection, error ordering, mutable encoding/carry,
observable `text` callbacks, and shadowed view accessors. See
[`oracle-results.json`](oracle-results.json). It does **not** validate the
production C++ kernel or a registered StringDecoder component.

```sh
/absolute/path/to/node-v22.14.0 tests/node-compat/foundation-string-decoder/inventory.mjs
/absolute/path/to/node-v22.14.0 tests/node-compat/foundation-string-decoder/oracle.mjs
```

## Native decoder ownership candidate

The existing generic native decoder obtains a borrowed span before accessing
the user-controlled `stream` getter. A getter may change the source before its
raw pointer is consumed. `value_to_buffer` also discards sharedness, and a
zero-length null pointer violates encoding_c's Rust-slice precondition. These
are **source-backed hazards**, not runtime memory-fault demonstrations. No
detached/shared/resizable hazard is executed against the old native decoder.

Safe Node mutation probes confirm that an option getter changing `a` to `b`
must affect that decode call. Copying before the getter would be wrong. Node22's
global TextDecoder additionally reads `stream` before rejecting invalid input
(twice on one UTF-8 streaming path), unlike current native type-first behavior.
The private candidate preserves type-first BufferSource validation and performs
options conversion before acquiring data. WebIDL conversion and the Encoding
algorithm also place input copying after dictionary conversion;
[the Encoding Standard](https://encoding.spec.whatwg.org/#dom-textdecoder-decode)
permits avoiding a copy when future calls cannot observe source changes.

[`text-decoder-ownership.private.patch`](text-decoder-ownership.private.patch)
and the adjacent full candidate use the minimal unshared borrow path:

1. Validate/root the source object without retaining data; read stream options.
2. Re-read native lengths and explicitly reject shared views in this private
   candidate. Shared atomic-copy support remains a decision, not an implicit
   conformance claim.
3. Allocate checked UTF-16 output through fallible `JS_malloc` with matching
   `JS::FreePolicy`, before borrowing any input pointer.
4. Reacquire input length/data under `JS::AutoCheckCannotGC`; hold the pointer
   only through synchronous encoding_c/encoding_rs decoding. Use a nonnull
   sentinel for empty input. Pending decoder bytes are copied into Rust-owned
   state, not retained as references to the source.
5. Leave the borrow scope before JS string allocation/error creation. Preserve
   the actual pending OOM on string-allocation failure.

No clone/full-input copy is needed for ordinary unshared inputs. The pinned
Rust decoding functions consume slices synchronously, have no JavaScript
callback parameters, and the encoding_rs dependency has no host API interface.
The ordinary compiled-engine gate below validates the selected API behavior;
it does not establish exhaustive GC or allocation-failure recovery.

The candidate checks `JS_NewObjectForConstructor` before accessing slots and
initializes a null decoder slot before further allocation; finalization handles
an uninitialized slot. This addresses the missing JS allocation check.
**encoding_c allocates Decoder with Box::new, so true Rust allocator exhaustion
still aborts.** Its defensive null check does not demonstrate recoverable Rust
OOM. Fatal-decoding lifecycle details and other existing native getters are
also outside this ownership patch's tested scope.

The private candidate passed actual SDK30/SpiderMonkey147 syntax checking and a
linked private Release-engine gate. That exact private source is preserved;
[`text-decoder-candidate-pins.json`](text-decoder-candidate-pins.json) records
the base/candidate/patch hashes. The later cleaned production variant is a
separately pinned source below.

## Private ordinary API component gate

[`build-private-engine.mjs`](build-private-engine.mjs) starts from the immutable
foundations-v4 OFF/Path1/Events1 engine and its frozen recipe. It verifies all
271 source hashes before copying them into an isolated checkout, applies only
the decoder CPP patch, builds with the same Release flags, and verifies the
same source path set with exactly that one hash changed. Embedding sources,
archive pins, manifests, requested/observed options and recipe match v4.
[`private-build-pins.json`](private-build-pins.json) records the exact baseline
engine `347025c9…fa5087`, receipt, recipe and helper pins. The private engine is
`cc340877…c6861`. Builds use no diagnostic/fault hook and no new host service.

[`run-private.mjs`](run-private.mjs) admits only this audited private candidate.
It selects the actual registered native Buffer and runs the unintegrated
StringDecoder factory over it. Results in
[`private-results.json`](private-results.json) verify:

- 40 generic TextDecoder cases: empty/offset/all typed-array inputs, view
  accessor shadows, mutation/throwing stream getters, **standard** transfer and
  resize operations, streaming/flush/BOM, and throwing constructor getters.
- 2,982 UTF-8/hex StringDecoder sequences / 8,886 writes with exact Node outputs
  and all public carry-state bytes, plus live-byte mutation, mutable public
  encoding, observable `text` callback, and unsupported/unknown encodings.
- Snapshot-created native TextDecoder and prototype StringDecoder carry,
  three calls on the same component instance, and a fresh stock Wasmtime42.0.1
  instance. Both Jco-hosted Wasm and Wasmtime pass. The component imports zero
  host interfaces; the emitted-interface audit is recorded.

Thirty-eight generic cases match the Node oracle exactly. Two deliberately
preserved existing ordering differences are explicit in the result: native
type validation precedes the stream getter on invalid input, and constructor
options are each read once rather than Node22's two reads. SharedArrayBuffer
was unavailable in this guest, so shared rejection was not exercised there.
The Node host oracle remains separate and never executes old native hazards.

```sh
/absolute/path/to/node-v22.14.0 tests/node-compat/foundation-string-decoder/build-private-engine.mjs --plan
/absolute/path/to/node-v22.14.0 tests/node-compat/foundation-string-decoder/build-private-engine.mjs
/absolute/path/to/node-v22.14.0 tests/node-compat/foundation-string-decoder/decoder-oracle.mjs
/absolute/path/to/node-v22.14.0 tests/node-compat/foundation-string-decoder/make-corpus.mjs
NODE_COMPAT_TOOLCHAIN=/absolute/path/to/pinned-toolchain \
NODE_COMPAT_COMPONENTIZE_MODULE=/absolute/path/to/v2/package/src/componentize.js \
NODE_COMPAT_ENGINE=/absolute/path/to/private-candidate.wasm \
NODE_COMPAT_WASMTIME=/absolute/path/to/wasmtime-42.0.1 \
/absolute/path/to/node-v22.14.0 tests/node-compat/foundation-string-decoder/run-private.mjs
```

The first fixture had a harness-only hex reuse expectation of `a` rather than
the correct `61`. That component is preserved in the external `results-v1`
directory; the accepted corrected fixture/results use `results-v2`. Neither
attempt required a native source change. This gate makes no timing,
allocation-failure recovery, complete WebIDL or production StringDecoder claim.

The separate [`encodeInto source audit`](encode-into-source-audit.md) records
the no-demonstrated-MayGC conclusion and a safe Node-only zero-length oracle.

## Next ordinary production source proposal

The accepted private engine/source/receipt remain unchanged. The separate
[`text-decoder.production-candidate.cpp`](text-decoder.production-candidate.cpp)
and [`production patch`](text-decoder-ownership.production.patch) were
subsequently applied by the coordinating agent for the next ordinary build.
The complete
[`delta from the tested private candidate`](production-from-private.diff)
replaces the integer-derived empty pointer with the address of a local
`const uint8_t empty = 0` and cleans private-only comments/blank lines. It adds
no diagnostic macro, API or host capability. Exact hashes and pending status
are in [`production-candidate-pins.json`](production-candidate-pins.json).
This cleaned variant passed its own compiled-engine gate below; the accepted
private result continues to prove its preserved private source/hash.

The optional canonical UTF-8/hex facade now has independent production source,
finite m0.4 manifest, generator/header and license under
[`builtins/node-compat`](../../../builtins/node-compat/README.string-decoder.md).
It adds captured error constructors and native byte-length getters to the
tested prototype; the prototype history is preserved. Shared registration,
CMake flags and admission/build metadata are a separate coordinated merge.
[`production-contract-tests.mjs`](production-contract-tests.mjs) passes the
common corpus (2,982 sequences / 8,886 writes per dependency) against NodeBuffer
and M0 Buffer with the explicit JS reference kernel. It also passes intrinsic
replacement and five detached-owned-state checks per dependency. The actual
header literal is evaluated with strict script semantics matching native
`CompileOptions::setForceStrictMode()`: a plain constructor call and four
detached methods reject without global pollution. Header and native-helper
hashes are in [`production-contract-results.json`](production-contract-results.json).
This is host verification, not an installed native-module claim.

[`run-native-component.mjs`](run-native-component.mjs) and native fixtures are
prepared for the actual installed module. They admit only an engine with
explicit `stringDecoderEnabled`, observed `NODE_COMPAT_STRING_DECODER=ON`, the
corrected decoder hash and all compiled source hashes. They pin the strict
factory helper. The gate includes the bounded corpus and generic decoder
cases, named/default/CJS identities, mutable defaults, plain calls, detached
owned state, intrinsic replacement, snapshot/reuse, uncached deployed aliases,
top-level componentization failures, final imports and stock Wasmtime. It
passes the coordinated v6 Release engine gate. See
[`native-component-results.json`](native-component-results.json): three
Jco-hosted Wasm calls and a fresh stock Wasmtime42.0.1 instance pass all
2,982 sequences / 8,886 writes and 40 ordinary decoder cases per call. Five
detached-owned-state checks and post-install intrinsic replacements pass;
plain constructor calls reject without global pollution. The separate
uncached-alias component passes two Jco calls and a fresh Wasmtime instance.
Both components emit zero host interfaces. All three top-level unsupported,
unknown-encoding and no-new fixtures fail componentization as required.

The v6 engine is `33b9cb24…cd59516`, with 285 verified native input hashes and
the observed optional flag ON. The common strict-factory helper is pinned as
`a219848a…84c63d1`; the semantic component is `9115869c…018cb`.
The two existing generic decoder ordering differences remain explicit, shared
memory was unavailable in this guest, and broad fatal-error lifecycle,
complete WebIDL and allocator recovery remain unclaimed. Original prototype,
private candidate, private receipts and failed harness control are preserved.

The coordinated HTTP application passed on both target hosts with this bounded
module. The immutable
[foundations-v6 checkpoint](../milestones/foundations-v6/README.md) records the
exact component, six selected standard0.2.10 imports and three requests on each
of stock Wasmtime and official wasmCloud. This is distinct from the pure
zero-import semantic and alias components above.

## Further integration and performance gates

The coordinated integration uses an optional default-OFF feature, separate
versioned two-export manifest, existing native factory/registration generator,
and core Buffer dependency. The native gate above tests named/default/bare
aliases, snapshot-created carry, repeated independent instances and end/reset.
The concrete registration mechanism is
[`register.cpp::evaluate_factory` and `install`](../../../builtins/node-compat/register.cpp),
followed by the existing `Engine::define_builtin_module`; pass the already
rooted Buffer constructor as the factory argument. This avoids assuming that
the public global Buffer has already been installed. The checked-in optional
header is orchestrated alongside the Path/Events branches by
[`generate-factories.mjs`](../../../builtins/node-compat/generate-factories.mjs)
and the existing `builtin_node_compat` target.
The pure component must emit zero host interfaces. Re-run this oracle against
actual native Buffer/encoding_rs after each integration change. The private
ordinary gate already covers transfer/resize and input integrity; shared
memory, broader fatal-error lifecycle and GC behavior remain separate gates.
Allocation-failure recovery is unverified and is not part of this ordinary
test plan. No test-only host service or public kernel hook is needed.

Then compare component size, allocation peak and throughput with the actual
Jco string-decoder **and its own Buffer adapter**, using the same engine/world
and common supported UTF-8/hex domain. Keep JS semantics tests separate from
native ownership and performance evidence. Other encodings require a separate
decision: UTF-16/ASCII/latin1 need Node semantics rather than label aliases;
base64/base64url are suitable pure native byte kernels if measurements justify
them. They do not require host capabilities.
