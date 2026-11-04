# Isolated DataView BYOB adapter

This uninstalled stage leaves the frozen [codec/guard](../candidate/README.md)
and [iteration](../iteration/README.md) evidence unchanged. It installs a
separate opt-in read wrapper on the real native BYOB prototype and restores the
original descriptor afterward. No production files or engine are changed.

The adapter captures the original native read before installing the earlier
simulation. For an ordinary fixed, attached, unshared local DataView it creates
a captured Uint8Array view over the **same buffer, byteOffset and byteLength**,
then invokes native read with that Uint8Array. The result becomes a captured
DataView over the returned buffer/offset/length. Undefined cancellation results
remain undefined. No explicit byte copy occurs in this adaptation; the native
transfer implementation may allocate or copy, and no end-to-end zero-copy or
performance claim follows.

The known old-native DataView constructor branch is never entered. A guest
observer checks every actual original-read input kind and fails before native
entry if a DataView appears. All observed original inputs are the eleven
typed-array classes; DataView requests use Uint8Array. The original failing
DataView control remains preserved in external `stream-web-candidate-v4`.

The bounded guard retains the preceding receiver/options order and policies:
minimum one only (including undefined/null), local standard view prototypes,
16,777,216-byte per-view limit, fixed unshared backing, no own modified layout
properties or subclass/cross-realm/Proxy support. Unsupported operations throw
`ERR_SM_NODE_UNSUPPORTED`; the limit throws RangeError `ERR_SM_NODE_LIMIT` with
resource `byob-view-bytes`. Empty views and selected invalid options use the
recorded Node errors. Coded errors define their own properties through captured
defineProperty and null-prototype descriptors, avoiding inherited code setters.
The native reader constructor/prototype identity remains unchanged.

After an observable min getter the DataView's intrinsic offset and length are
read again. Standard detachment by that getter therefore rejects before native
entry. No raw pointer is retained by guest JavaScript. Returned DataViews keep
their backing buffers alive through normal GC references.

[Node22 oracle](node-results.json) and [host checks](host-results.json) cover
26 DataView cases: offsets/backing, remaining queued bytes, untouched bytes
outside the view, source BYOB requests, empty EOF, pending close/cancel/error,
reason identity, cancellation rejection, concurrent reads, invalid minima,
throwing or detaching getters and released readers.

[Component results](component-results.json) use the immutable v6 OFF engine and
retain all 285 input hashes, candidate hashes, packager provenance and final
zero-import audit. Component
`dd908870277287c0c2285cb578ed8fefe8754b670fea9885278c6bc43cdd7a57`
is 12,165,393 bytes including fixtures. Two Jco calls and fresh stock
Wasmtime42.0.1 pass:

- 25 of the 26 DataView cases match recorded Node fields. A released native
  reader's TypeError lacks Node's `ERR_INVALID_STATE`; its original buffer
  remains intact. That exact error-code deviation is retained, not relabeled
  by parsing messages or changing arbitrary application TypeErrors.
- All twelve ordinary view classes, now including DataView, match their
  existing Node transfer/offset/type oracle.
- The 24 preceding guard cases retain 21 exact matches and the same three
  explicit differences: minimum two, Proxy receiver and modified layout.
- Six policy tests reject without transfer or queued-byte consumption and
  recover with a subsequent DataView read. Inherited code accessors and
  replaced global constructors/intrinsics receive zero calls.
- Native reader identity, all eight restored descriptors and **zero original
  native DataView calls** are checked after each run.

The first v1 adapter component is preserved with its released-reader code
mismatch. The v2 expectation changes only that declared native difference;
it does not weaken input-integrity or source-reason checks. SharedArrayBuffer
is absent in this guest; no guest shared-memory support is claimed.

The adapter remains a proposal until composed regressions, actual native
class/brand capture, the compiled Transform-controller guard, module admission,
both target hosts and production review pass. WDC.signal, minimum-fill greater
than one and compression remain separate missing features. No old-native
DataView/prototype hazard, compression, allocation fault or raw-memory probe
is executed.

```sh
/path/to/node-v22.14.0 tests/node-compat/foundation-stream-web/dataview/node-oracle.mjs
/path/to/node-v22.14.0 tests/node-compat/foundation-stream-web/dataview/run-host.mjs
# Same locked toolchain, patched packager, immutable engine/source and Wasmtime
# environment as the preceding stages.
NODE_COMPAT_STREAM_DATAVIEW_OUTPUT=/path/to/fresh-output \
/path/to/node-v22.14.0 tests/node-compat/foundation-stream-web/dataview/run-component.mjs
```
