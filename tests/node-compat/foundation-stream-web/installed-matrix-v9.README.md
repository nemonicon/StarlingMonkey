# Installed m0.9 matrix supplement

[installed-matrix-v9.json](installed-matrix-v9.json) is separate supplementary
evidence for the installed bounded profile. It does not replace the original
source/probe [matrix.json](matrix.json), its generator, or the immutable accepted
v9 archive. Those original files are hash-checked and remain byte-identical.

The supplement contains exactly 18 module exports, 184 observed Node-own static
and prototype members, and eight explicitly labeled semantic operations. It is
generated with exact Node v22.14.0. Own string members must match the preserved
Node inventory; side-effect-free descriptor reflection adds well-known,
registered and private symbol observations without calling getters or creating
streams. Descriptions of nonregistry symbols are not recoverable property keys
or public API requirements. Ordinary Function/Object ancestors are not expanded.

Each row records a strategy, required interfaces (empty), support status,
deviations, current versus historical evidence and remaining validation.
Statuses mean:

- **supported:** the explicitly selected finite binding/introspection contract
  or recorded fields, not complete Node semantics.
- **partial:** an implemented/reused operation has tested ordinary subsets and
  stated limits; untested overloads are not certified.
- **import-only:** the binding imports and inspects safely; its operation is
  deferred. Both compression bindings use this status.
- **deferred:** the stated call/new operation throws, or future work is planned.
  It does not describe every inherited native operation.
- **unavailable:** an observable property is absent. Writable controller signal
  reads undefined; a real implementation is separately planned. No fake getter
  or AbortSignal is supplied. Missing deferred-stub prototype properties have
  a source-derived absence basis, distinct from fresh runtime inspection.
- **unverified:** target presence and behavior are not established. A Node-own
  symbol/member might be absent or executable. Capturing its constructor does
  not prove a corresponding native implementation, conformance or refusal.

The current evidence chain is pinned by report/file hashes, the exact 302-input
source manifest and selected m0.9 manifest, and the actual component hashes:

- Installed ON engine `94e13fce…57a25`, component
  `bc4aec0a…90d3` (13,578,693 bytes including corpora): three retained Jco calls,
  fresh Wasmtime42, exact namespace/default/alias/literal-CJS/snapshot behavior,
  real constructor/reader-brand checks, and seven componentization failures.
- Corrected OFF engine `3bb37e5c…46e43b`, native-controller component
  `eb132497…ac88d`: six state/prototype cases and sixteen additional invalid
  receivers per call, without the Node-facing JS wrappers, on both backends.

Both components import no host interface. Underlying application sources/sinks
or HTTP/filesystem adapters can need separately selected standard capabilities;
the empty list does not remove those application dependencies.

The installed corpus records 41 constructor/shape cases, 250 codec vectors,
four cancellation cases, 24 BYOB guards, twelve view types, six controller
cases, 67 iteration cases and 26 DataView cases. It also checks fourteen public
policies, six DataView rejection/recovery policies, nine own-error checks and
captured-operation groups. It does not re-execute every original eleven-case
probe operation. Earlier pipeTo/tee, queue-strategy and writable-backpressure
results remain explicitly historical; they do not become fresh v9 parity.

The matrix preserves limits and gaps: UTF8-only decoder, per-chunk/view caps,
fixed attached unshared decoder input, BYOB minimum one and ordinary local
views, Proxy/cross-realm exclusions, unavailable signal, module-only codec
globals, released-reader and other native error-code differences, and explicit
compression call/new refusals. The finite mutable default and initial named
bindings are supported within the selected contract; runtime require and
syncBuiltinESMExports are excluded. Per-input caps do not bound retained queues,
total output, operation count or native allocation failure.

The reused policy helper contains a historical ordinaryNativeBrandProof:false
label. It is not used as the installed proof. The actual chain uses the pinned
compiled public-API kernel, no bundled factory/fixture registry, actual valid/
spoof/Proxy guard cases and native/global/genuine-instance identities. This
still does not prove arbitrary cross-realm brands.

Node descriptors in the inventory describe **Node**, not inferred guest
descriptors. The generator never executes native guest operations or builds an
engine. Component sizes are provenance, not deployment-size or performance
measurements. [The receipt](installed-matrix-v9.receipt.json) pins the generator,
supplement, inputs and preserved original audit files.

```sh
/path/to/node-v22.14.0 tests/node-compat/foundation-stream-web/make-installed-matrix-v9.mjs
```
