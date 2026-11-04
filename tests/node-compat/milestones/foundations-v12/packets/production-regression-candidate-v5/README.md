This is an **reviewed-pin activation source packet; runtime validation pending** at its final path. It derives from [common v4](../production-regression-candidate-v4/README.md). The two production pin tuples are copied byte-exact from [Root’s actual pin review](../production-pin-review-v1/README.md). The predecessor’s null pin document remains historical. Source sealing and the separately authorized read-only preflight are preparation gates; no production runner, toolchain, guest or host has executed as part of this packet’s preparation.

The finite production guards and core/allocator/allocator-GC bodies remain byte-identical to v4. The original transformation record is unchanged. New `dependency-bindings.mjs` accepts only a reviewed exact parent-index digest for descendants; it does not read files or admit artifacts. `history/predecessor/` preserves the old scripts, source reports, runtime seal and index as historical data, including their old null-entry tests. Those historical reports establish no new production runtime pass.

`test-host.mjs` uses OWN scratch null/unreviewed/malformed selector documents and the inherited owned-file seal/tamper cases. It never changes or depends on the current pin file, starts no runner/null-entry children, and executes no original Node oracle. It retains pure metadata rejection and original reverse-edit/GC-template checks. Actual live adapter bytes are included in the complete pre/post runtime source closure; host checks separately exercise owned missing/tampered adapter data. Its fresh JSON report is set by `NODE_COMPAT_REGRESSION_HOST_TEST_OUTPUT`.

Root independently reviewed the actual production freeze tuples and authorized this byte-exact `pins.json` revision with exact schema-1 immutable production freezes (recipe869, source306, external embedding3, native layout61, strict4 and parent embedding1). Unavailable variants remain null. The exporter’s `UNREVIEWED_PRODUCTION_PIN_CANDIDATES_V1` output is rejected and must not be relabeled without review. `freeze-inputs.py` refuses unreviewed pins and writes exclusively; it preserves the live Preview1 adapter and historical controls. Complete the source closure and final common index before binding descendants.

After that review and source freeze Root authorized the separate **read-only** entry, with pinned Node22 and the existing exact engine/source/Wasmtime environment:

```sh
node preflight-only.mjs normal-off /ABS/FRESH/preflight.json
node preflight-only.mjs gc-off /ABS/FRESH/gc-preflight.json
```

The separate external read-only reports record whether these commands completed; they are not guest/runtime passes. They perform fixed-artifact admission and rechecks, not runtime compatibility validation. `check-staging.py FRESH_OUTPUT_JSON` checks all four staged successors, predecessor immutability and syntax without running JavaScript mains. No compatibility acceptance follows from these source or read-only checks. The original historical null-entry tests are not rerun against populated pins.
