# Production TextEncoder v5 validation

The ordinary production `TextEncoder::encode` implementation now allocates an exact-size, GC-owned Uint8Array and deflates directly into it. String conversion, linearization and destination allocation happen before borrowing output data; after those operations the code reacquires both pointers inside a no-GC scope. It checks conversion failures, preserves undefined-to-empty behavior and returns a rooted output. The production body contains no private experiment helpers or fault controls.

The separate `encodeInto` change roots the coerced string, returns `{read:0,written:0}` for an empty/detached/out-of-bounds destination without passing a null span to the underlying codec, and reports OOM if `JS_EncodeStringToUTF8BufferPartial` returns `Nothing`. Shared-memory policy and the existing Starling source conversion remain unchanged. The OOM-reporting branch is source-reviewed; these ordinary tests do not prove allocator-failure behavior.

Both actual v5 production engines pass [OFF results](production-off-results.json) and [RuntimeOnly results](production-runtime-results.json), copied byte-for-byte with a [receipt](production-codec-receipt.json):

| Engine | Engine SHA-256 | Component SHA-256 | Final imports |
| --- | --- | --- | --- |
| OFF + Path + Events | `165b59a1fac4f3bab14547a28063908193c2b98767bd5fa835ca00b9b6d8adfc` | `a808a1ab45fb16784c97fa1b3ba5b5bc9d72f6c7063b67d8205031688e29e9f3` | none |
| RuntimeOnly + Path + Events | `ff770f47dea834da5077fa10f4c1af1e89165519e9d67b664e9b7abf1bfcdb5b` | `38acb91e35acb98d4dd9817159479b69729e02d3b72313583b97601516a6875b` | `wasi:random/random@0.2.10` |

Each component passed three calls to one Jco instance and one fresh unmodified Wasmtime 42.0.1 instance. RuntimeOnly explicitly retains random, selects only the secure-random interface, and uses the hash-pinned repository Preview1 adapter. OFF disables all five ComponentizeJS features. Final interface names/versions are checked directly; no interface-version rewriting is performed.

The original [shared suite](codec-cases.mjs) and [Node 22.14.0 oracle](node-oracle-results.json) remain byte-identical: **8 groups, 77,769 assertions and 78 observations**. New [shared public API cases](production-extra-cases.mjs), compared with a [separate Node oracle](production-extra-node-oracle-results.json), add **7 groups, 226 assertions and 11 observations**. They cover finite reentrant conversion and exception identity, Unicode and independent outputs, ArrayBuffer transfer after `encode` returns, nested transfer after an inner encode returns, zero-length offset views, detached views, fixed/tracking resizable-buffer out-of-bounds views and recovery after regrowth. Every transfer/resize group ran on both engines; none was skipped. A snapshot-created Uint8Array and its backing identity/content also survive every call independently of fresh outputs.

**An existing Node deviation is explicit:** Node 22 `TextEncoder.encodeInto` rejects non-string sources before invoking conversion hooks, while Starling performs `ToString`. The [pinned Node implementation](https://github.com/nodejs/node/blob/v22.14.0/lib/internal/encoding.js) uses `validateString`. Seven policy-specific cases validate each implementation separately, including conversion that transfers or resizes the destination before data acquisition. Starling passes 13 assertions per call; these observations are not claimed equal to Node. Shared differential cases use primitive strings.

[run-production-codec.mjs](run-production-codec.mjs) verifies the complete 271-input native freeze and exact production encoder SHA `32230064c1ea0bc66ffbc5f9ddd6a97f46a8bc47a7c9e72caaddf5745f8986c7` **before executing any new guard case**. It checks engine bytes/sidecar, actual CMake cache and compile-command digests, Release/WEVAL-OFF/no-debug/no-fault flags, the compiler's encoder source, old/new oracle hashes, captured test sources before/after and final imports. An [admission check](production-admission-negative-results.json) proves the preceding v4 encoder is rejected before componentization or guest execution. OFF executed the earlier zero-import runner; its [exact runner](production-executed-off/run-production-codec.mjs) and [pins](production-executed-off/production-codec-pins.json) are preserved independently of later Runtime support. Both external result directories retain all 14 executed test/packaging sources, metadata and actual build caches/commands.

To reproduce with the recorded toolchain and frozen source:

```sh
NODE_COMPAT_ENGINE=/tmp/starling-node-compat/improved-build/artifacts/starlingmonkey_embedding.abi-i32-i64-v1.entropy-entry-v1.OFF.path-1.events-1.foundations-v5.wasm \
NODE_COMPAT_ENGINE_SOURCE_ROOT=/tmp/starling-node-compat/foundations-v5/native-freeze/source \
NODE_COMPAT_TOOLCHAIN=/tmp/starling-node-compat/native-toolchain-lock \
NODE_COMPAT_COMPONENTIZE_MODULE=/tmp/starling-node-compat/import-abi-clock-v2-build/package/src/componentize.js \
NODE_COMPAT_PRODUCTION_CODEC_OUTPUT=/tmp/starling-node-compat/foundations-v5/codec-reproduction \
/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node tests/node-compat/utf8-direct/run-production-codec.mjs
```

For RuntimeOnly select its engine above and a fresh output directory. The runner derives the explicit random selection from verified engine metadata. Output directories are exclusive, and existing receipts are not overwritten. The oracle receipts are archived inputs; generate another oracle in a copied directory to preserve their pinned hashes. Reproduction requires the recorded engine/source/build-receipt archives; a later reused live build directory must not be mistaken for those historical cache/compile-command bytes.

These are new functional/ownership results for the actual production code. The [private paired performance measurements](README.md#completed-ordinary-release-measurement) belong to different engine/source bytes and are not automatically performance results for v5. The failed private linearization OOM assertion and the separate automatic-review block remain preserved and unverified; no DEBUG/fault execution, raw memory access, malformed carrier, private telemetry or access change was used for this production validation. This bounded suite does not establish complete TextEncoder, Web API, Buffer or Node compatibility.
