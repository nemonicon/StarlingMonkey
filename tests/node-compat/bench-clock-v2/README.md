# Corrected-clock matched Buffer experiment

This is a new version of the historical `../bench` experiment. Historical
sources/reports remain unchanged. `build.mjs` requires the audited patched
ComponentizeJS loader, explicit Release OFF engine and pinned repository adapter.
The final capability audit requires zero imports in both arms. Both use the same
profile-enabled engine; the JS arm additionally bundles Jco1.40's actual Buffer
adapter and unenv2.0.0-rc.24. This measures duplicate-adapter overhead, not the
smallest profile-disabled deployment.

All five operations at 64/4096/65536/524288 bytes have Node22 setup/full-checksum
and result-fingerprint correctness gates in actual components. Three independent
componentization replicates retain each component SHA, byte/gzip sizes and
packaging receipts. Snapshot byte layouts may vary; identical bytes are not
assumed. The guest ABI stays historical `s32` checksum transport; current
high-u32 and signed-BigInt ABI fixes have separate passing gates.

`run.mjs` reuses the exact previously hash-verified stock Wasmtime42 Rust
benchmark host and unchanged three Rust source/lock files. It compiles/deserializes
outside throughput timing, alternates arm order across scenarios, measures
seven batches in each of three fresh instances, and separates initialization,
setup, first batch and warmed throughput. It reports ResourceLimiter observations,
linear memory and process RSS with their existing limits. No guest clocks or
host services are added. Retained batches are correlated; RSS includes the host
and allocator retention. No whole-application or statistical significance claim.

[The completed measurement report](RESULTS.md) records all40 observations for20 scenarios, all six component artifacts from three componentization replicates, exact hashes and background-workload limits. The [raw results](results.json) retain startup, throughput, memory and per-instance data. These observations belong to the exact foundations-v2 non-Weval engine; later source changes need their own applicable gates.
