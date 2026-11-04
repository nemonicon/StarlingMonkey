# Matched installed allocator experiment

This directory prepares a fixed-domain comparison of the actual installed v8
m0.8 `Buffer.allocUnsafe` and the actual locked Jco1.40 Buffer adapter. Performance
execution is **pending the coordinator's measurement window**. Correctness builds
and artifact byte sizes establish no throughput, startup or memory improvement.
No older Buffer/UTF8/Weval/compression measurements enter this experiment.

## Source and semantic audit

Jco's installed `dist/node-builtins/buffer.js::createBufferBuiltin` synthesizes
an adapter plus `unenv-buffer-core`; `unenv.js::unenvModule` resolves the locked
unenv2.0.0-rc.24 `runtime/node/internal/buffer/buffer.mjs`. That file identifies
Feross commit `795bbb5bda1b39f1370ebd784bea6107b087e3a7` and imports only its
base64/IEEE754 guest modules. `Buffer.allocUnsafe` calls `allocUnsafe -> assertSize
-> checked -> createBuffer`; the last function creates `new Uint8Array(length)`
and changes its prototype. It **zeroes fresh storage and has no actual pool**,
although public poolSize is8192. The source comment claiming nonzero-filled
storage does not describe the executed typed-array allocation.

The Jco adapter adds a deprecated-constructor Proxy, species/export/codec wrappers,
and **replaces `globalThis.Buffer`**. The comparison uses that real adapter without
extracting its allocation method or rewriting its semantics. It remains portable
guest JS: this path imports no WASI or custom host service. The build records exact
adapter/generated source/dependency hashes and audits final component imports.
Build-tool `node:*` imports are separate from guest dependencies. Installed npm
packages omit their upstream test trees; the source audit is supplemented by this
ordinary common-domain component corpus and earlier separately recorded adapter
gates, without claiming their full API passes Node22 conformance.

The adapter's broader Node-facing export shape follows a newer release. Its
`assertSize`/`checked` accepts NaN as zero, reports different error fields, and
permits sizes beyond the profile's16MiB limit. The native profile captures its
existing native `Buffer.alloc`, validates finite raw sizes before truncation and
promises exact zeroed no-pool backing. These are deliberately different APIs;
only integer sizes **64B,4KiB,512KiB** are compared. Actual Node22 is a checksum
oracle for written bytes and construction only; no initial unsafe Node byte is
inspected. Node slab/uninitialized behavior is not an experimental arm.

## Bounded workloads and correctness preflight

The one-export world is `batch(operation:u32,size:u32,iterations:u32)->u32`.
Both arms use identical ordinary Release v8 engine, frozen293 inputs, audited
packager, adapter, world, source workload and case inputs. Native module presence
is retained in both engines; the JS arm additionally bundles the actual adapter.
Identity and encoding markers reject implementation contamination at initialization.
The artifact byte delta therefore measures additional bundled-adapter overhead,
not the saving from a separately minimized profile-free engine.

Five operations run independently: captured `allocUnsafe(size)`, ordinary
`new allocUnsafe(size)`, captured `Buffer.alloc(size)`, `new Uint8Array(size)`, and
an allocation-free-per-iteration reuse control. The reuse control allocates one
typed array per batch. Function-construction and underlying typed-array controls
make overhead visible; their medians will not be subtracted from other timings.
Every timed iteration writes first/last positions and consumes their values plus
length into a checksum. It performs no whole-buffer hash or per-iteration brand
inspection. Maximum requested allocation volume is64MiB per batch.

`build-correctness.mjs` validates0/1/3 iterations against Node22 in both fresh Jco
instances and fresh stock Wasmtime42 invocations. A separate operation4, excluded
from timing scenarios, checks complete zeroing, exact offsets/backing and distinct
allocations at the three sizes. No host timers/RSS/memory/grow observations run
in this script. The build retains full source/engine and emitted-WIT receipts,
minimal benchmark artifact bytes, and explicit-instantiation Jco files.

## Prepared measurement protocol, not executed

`measure.mjs` refuses execution unless `NODE_COMPAT_ALLOC_UNSAFE_MEASURE=1`; the
coordinator must first open the measurement window. It spawns fresh Node22 host
processes for every arm/scenario in both arm orders. Each process compiles its own
core modules, creates one fresh instance, reports first batch separately, then
uses three warmups and seven retained batches. The timer is host
`performance.now` around the batch WIT call. No clock import enters the guest.
The fixed batches request8MiB/32MiB/32MiB at the three sizes.

Only public `process.memoryUsage().rss`, `process.resourceUsage().maxRSS`, and
exported `WebAssembly.Memory.buffer.byteLength` are observed. The public Jco
`instantiateCore` callback retains actual exported Memory objects; no view of
their bytes is created or read. Byte lengths are sampled outside timed intervals.
Boundary growth events are a **lower bound**, not a count of in-Wasm `memory.grow`
attempts/failures. No explicit grow or private diagnostic is used. PeakRSS includes
V8 compilation/code/runtime and allocator retention; boundary RSS is whole-process
resident memory, not guest live heap. Startup observations separate
compile-and-binding-load, instantiation, and first batch; none is componentization
time or isolated single-allocation latency. These future measurements concern
V8-hosted Wasm through Jco, not Wasmtime throughput.

Use exact Node22.14 with the usual frozen engine/source root/toolchain/packager/
Wasmtime environment variables and `NODE_COMPAT_ALLOC_UNSAFE_MATCHED_OUTPUT`.
Run the correctness builder first. Do not run the measurement script until the
coordinated window. Artifact files, source hashes and correctness manifest are
reverified before any later timing execution; changed inputs require a new
correctness gate and output directory.
