# Private m0.11 paired timing plan, execution pending

The source-reviewed baseline and direct candidate have passed native receipts,
both installed corpora and both minimal-component correctness gates. **This
timing runner is prepared and syntax-checked, not executed.** Toolchain-agent
CPU-clear was received; the coordinator still must approve this source and open
the timing window. No old v8 performance observations enter its inputs.

The pair uses the same single absolute source/build project sequentially, with
complete baseline freeze before switching only facade and generated header.
Twenty-nine held-constant explicit linked archives,198 SDK/compiler/archive
inputs, actual CMake cache/compile-command hashes, flags and external embedding
sources match. The reviewed profile-code archive differs. Both private manifests
and helper metadata are m0.11; neither the live m0.9 selector nor production
sources are changed. Allocation remains the registered JS facade on a captured
native Uint8Array intrinsic, not a new C++ allocator kernel.

Minimal benchmark guest source, world, options, case inputs and bundle hash are
identical. The fixed preview1 adapter is the real Wasm file with SHA98822428…fabcc0.
The first packaging attempt's incorrect JS-generator path is preserved separately;
corrected components were built in a fresh output directory. Candidate engine is
14B smaller, but its exact retained minimal component is **8,513B larger**:
baseline12,054,311B versus candidate12,062,824B. This counterexample remains in
the frozen receipts; snapshot byte determinism or a size win is not inferred.

## Exact protocol

Fifteen scenarios cover ordinary allocUnsafe call, `new allocUnsafe`, Buffer.alloc,
new Uint8Array, and reuse control at64B/4KiB/512KiB. Reuse allocates one array per
batch and zero per iteration. Fixed iterations are131072/8192/64; checksums use
only two positions written by the iteration. No unsafe initial Node byte is read.
Batch volume stays bounded at8MiB/32MiB/32MiB.

Run order0 baseline→candidate for each scenario, then order1 candidate→baseline.
Each arm/scenario/order gets a fresh Node22 host process and one fresh component
instance:60 workers total, **n2 independent processes per arm/scenario**. Report
first batch separately, three warmups and seven correlated retained samples in
each worker. Host `performance.now` surrounds one batch WIT call only; checksum
assertions follow the interval. Report process medians and both arm-order ratios,
all candidate slowdowns and all control reversals. Do not pool14 samples as14
independent trials, infer significance, subtract noisy controls, or attribute the
whole return-expression result to fill alone.

Only public process RSS/resourceUsage and exported `WebAssembly.Memory` objects'
`buffer.byteLength` are observed, outside timed intervals. The copied public Jco
instantiateCore helper retains exported Memory objects without any byte view or
raw read. Boundary growth events are a lower bound, not internal grow/failure
counts. PeakRSS includes input verification reads, V8 compilation/code/runtime
and allocator retention; it is not guest live heap. Compile/binding-load,
instantiation and first-batch observations remain separate. This is V8-hosted
Wasm through Jco, not Wasmtime throughput or a current-Jco-adapter comparison.

## Frozen inputs and launch controls

`inputs.json` contains both exact engine/component/transpiled hashes, unchanged
bundle/world/workload checksums, scenarios, options and native/installed/minimal
receipt copies. The runner rechecks source, receipts, engines, components and
generated modules before work, including in each worker. All raw worker stdout/
stderr and partial results persist under the private experiment's timing folder.
The output's start marker refuses an overwrite. The1.5GiB disk cutoff is checked
before creating timing output; no compilation/package/native build happens here.

Only after coordinator source review and explicit timing-window authorization:

```sh
NODE_COMPAT_M011_TIMING_APPROVED=1 \
  /tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node measure-pair.mjs
```

No execution has occurred while preparing this checkpoint. Shared desktop load,
frequency/thermal state and n2 process replication limit any later conclusion.
No raw/private memory/ABI, DEBUG/fault work, fabricated growth counts, custom host
service or extra guest clock import is introduced.
