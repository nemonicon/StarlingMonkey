# Corrected-clock Buffer measurements

Exact engine `b02d17366c905ad46108a4c4ca705213572c5f3a6b8dd9bc52494730a7dfe0ad` (foundations-v2, OFF+Path). All20 scenarios pass Node checksums in both real-component arms; all40 measured arm/scenario records pass. The same stock Wasmtime42.0.1 host uses seven batches in three fresh instances per scenario. This is a non-Weval experiment.

Three componentization replicates add **116,820–116,866 bytes** for the actual Jco1.40 Buffer adapter; gzip delta 35,605–35,758 bytes. Both arms already include the native profile. Snapshot byte layouts vary by tens of bytes; sizes are not assumed deterministic.

|512KiB ASCII/byte operation|Native MiB/s|Jco JS MiB/s|Time ratio JS/native|PeakRSS MiB native/JS|
|---|---:|---:|---:|---:|
|hex-encode|1124.44|2.66|422.39|38.16/60.47|
|hex-decode|265.62|0.34|784.91|37.70/36.64|
|byte-copy|7726.96|7573.35|1.02|36.62/36.66|
|utf8-encode|917.12|0.36|2541.47|36.12/151.84|
|utf8-decode|1790.51|0.64|2794.53|30.17/151.89|

Memory does not improve uniformly. At64-byte UTF8 encode, native peakRSS is51.19MiB versus25.08MiB and the largest requested linear memory is35.06MiB versus9.06MiB. At512KiB hex decode, native peakRSS is37.70MiB versus36.64MiB. This supports a targeted small-UTF8 allocation investigation, not a uniform memory-saving claim. Small64-byte copy is1.37x faster;512KiB copy is1.02x, with essentially unchanged peakRSS.

Startup, setup, first batches, IQRs and every raw per-instance observation are in [results.json](results.json). A [three-build artifact record](artifact-manifest.json) retains component/adapter/package hashes. The host executable and its three source/lock files match the previously verified Wasmtime42 harness exactly.

Measurements ran on a shared M2 desktop with background system/VM work. Explicit native builds and other packaging were held during most timing; two already-running packaging jobs ended near the beginning, and one short caught-import diagnostic ran during the window. These are local exploratory timings, not statistical significance or whole-application claims. Batches within an instance are correlated. RSS includes the host/code/allocator; ResourceLimiter maximum requests are not total guest heap. Sampled string fingerprints may materialize ropes.

The subsequent loader fix changes synthetic-module loading and belongs to foundations-v3. These measurements remain evidence for the exact v2 engine. A separate matched Weval comparison and direct small-UTF8 allocation experiment remain pending.
