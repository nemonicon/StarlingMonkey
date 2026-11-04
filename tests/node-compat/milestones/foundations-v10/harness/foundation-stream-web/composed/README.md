# Composed ordinary component regression

This runner exercises the uninstalled [m0.9 source candidate](../production-candidate/README.md)
on the immutable v6 OFF engine, without a new native build. It combines the
previously separate codec, guarded receiver, iteration and DataView oracles.
The component fixture derives its native record only after deployed run entry;
all temporary streams are cleaned up and all eight prototype/static descriptors
are restored after each call. The actual public native capture remains unlinked.

[Host](host-results.json) and [component](component-results.json) receipts retain
the test counts and declared deviations. The component receipt includes all 285
native source hashes, runtime source hashes, packager provenance and final
zero-import audit. Two Jco calls and fresh stock Wasmtime42 pass. Byte size
includes the differential vectors and is not a minimal deployment measurement.

Own-error tests poison inherited metadata accessors only while testing pure
JavaScript-created errors. Native fatal decoding runs after restoration: the
initial host log preserved a known Node22 abort in that combined mutation
scenario, which is never repeated. No allocator fault or raw memory is used.

```sh
/path/to/node-v22.14.0 tests/node-compat/foundation-stream-web/composed/run-host.mjs
# Set the same locked-toolchain, v2 packager, immutable v6 engine/source-root
# and Wasmtime42 environment used by the preceding stages.
NODE_COMPAT_STREAM_COMPOSED_OUTPUT=/path/to/fresh-output \
/path/to/node-v22.14.0 tests/node-compat/foundation-stream-web/composed/run-component.mjs
```
