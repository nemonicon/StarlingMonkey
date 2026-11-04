# Matched allocator measurement: installed allocUnsafe is slower here

Installed m0.8 `allocUnsafe` takes longer than the actual locked Jco adapter at
all three sizes, for both call and construction, in both arm orders. This result
supports keeping the method for its bounded dependency contract; **it provides
no allocUnsafe throughput-acceleration evidence**. No production change follows
from this experiment.

[Full raw results](./raw/results.json), [process-level analysis](./analysis-results.json)
and [the frozen correctness receipt](./correctness-results.json) retain all60
worker reports. Native engine, both component binaries, generated Jco files and
all293 frozen native inputs were reverified after execution. Every raw stdout
matches its corresponding report; every worker stderr is empty. The root and two
peer agents held heavy jobs during the coordinated timing window. Apple M2,
macOS arm64, Node22.14/V8-hosted Wasm through Jco1.40; Wasmtime42 correctness is
separate from these throughput observations.

Each cell lists the **median of seven correlated batches within a process** for
order0/order1. Order0 executes native then JS per scenario; order1 reverses them.
There are **two independent processes per arm/scenario**, not14 independent
samples. Time per iteration includes the guest loop and two written-byte reads;
the host timer surrounds one batch WIT call. Checksum assertions and public
memory/RSS observations occur outside the timed interval. JS/native ratios
below1 mean the installed native-profile arm takes longer.

| Operation | Size | Native µs/iteration, orders0/1 | Jco µs/iteration, orders0/1 | JS/native median time, orders0/1 |
| --- | ---: | ---: | ---: | ---: |
| allocUnsafe call | 64B | 2.099 / 2.095 | 1.108 / 1.084 | 0.528 / 0.518 |
| allocUnsafe call | 4KiB | 2.692 / 2.707 | 1.489 / 1.585 | 0.553 / 0.586 |
| allocUnsafe call | 512KiB | 20.970 / 20.998 | 14.760 / 15.154 | 0.704 / 0.722 |
| new allocUnsafe | 64B | 2.245 / 2.238 | 1.216 / 1.236 | 0.542 / 0.553 |
| new allocUnsafe | 4KiB | 2.777 / 2.776 | 1.632 / 1.673 | 0.588 / 0.603 |
| new allocUnsafe | 512KiB | 21.579 / 21.597 | 14.817 / 15.182 | 0.687 / 0.703 |
| Buffer.alloc | 64B | 1.478 / 1.486 | 1.762 / 1.755 | 1.192 / 1.181 |
| Buffer.alloc | 4KiB | 1.969 / 1.997 | 2.283 / 2.150 | 1.160 / 1.076 |
| Buffer.alloc | 512KiB | 20.138 / 20.371 | 17.145 / 16.277 | 0.851 / 0.799 |
| new Uint8Array | 64B | 0.463 / 0.460 | 0.480 / 0.461 | 1.036 / 1.001 |
| new Uint8Array | 4KiB | 0.838 / 0.832 | 0.863 / 0.859 | 1.030 / 1.032 |
| new Uint8Array | 512KiB | 12.805 / 12.713 | 13.507 / 13.880 | 1.055 / 1.092 |
| Reuse control | 64B | 0.399 / 0.417 | 0.400 / 0.398 | 1.001 / 0.955 |
| Reuse control | 4KiB | 0.591 / 0.596 | 0.593 / 0.591 | 1.003 / 0.992 |
| Reuse control | 512KiB | 2.855 / 2.348 | 2.824 / 2.973 | 0.989 / 1.266 |

Native allocUnsafe call time is about1.89–1.93× Jco at64B,1.71–1.81× at4KiB,
and1.39–1.42× at512KiB. All12 call/construction order comparisons are slower.
The safe-allocation control is faster natively at64B/4KiB and slower at512KiB,
adding two more allocator counterexamples. Underlying Uint8Array controls differ
by about0–9%. Reuse controls reverse direction with order at all sizes; the
512KiB ratio changes about28% while those batches last only0.150–0.190ms. Noisy
control medians are not subtracted from other operations. Seven correlated
samples do not establish statistical significance or confidence intervals.

## Public memory and startup observations

Most final public linear-memory capacities match or are close. At64B they are
9,502,720B in both arms; at512KiB allocation workloads they are68,222,976B in
both arms. Native allocation is not uniformly smaller:

* At4KiB allocUnsafe call, native process peakRSS is334,976/336,864KiB versus
  Jco333,152/334,656KiB in the two orders.
* At4KiB new allocUnsafe, final native linear-memory capacity is69,795,840B
  versus Jco68,812,800B in both orders, a983,040B difference.

These are all four order-specific memory counterexamples in the captured
capacity/peakRSS comparisons. Other scenario process peaks are lower in the
native arm, including controls; this does not isolate an allocation primitive's
memory use. PeakRSS includes verification file reads before baseline, V8
compilation/code/runtime and allocator retention. Point RSS is whole-process
resident memory, and linear-memory capacity is neither live JS heap nor summed
resident memory. No heap byte, raw memory view, private ABI or engine diagnostic
is read.

The observer samples only public exported `WebAssembly.Memory.buffer.byteLength`.
Recorded growth events are a lower bound at sample boundaries, **not counts of
in-Wasm grow calls or failures**. For example, the512KiB reuse control grows at
eight observed boundaries in each process: it allocates one typed array per
batch, though none per iteration. This is not a leak or lifetime verdict.

Across the30 processes per arm, compile-and-binding-load is13.20–16.67ms native
and13.42–15.34ms JS; instantiation is1.24–1.89ms native and1.24–1.49ms JS.
These overlapping observations provide no consistent startup-win claim. First
batches are retained per scenario separately from warm batches; they are batch
latencies, not single-operation startup. Compilation includes generated JS
binding import and V8 compilation. Componentization is excluded.

## Scope and retained evidence

Both arms use identical ordinary Release v8 OFF engine
`e16c19fc567753517d7b61b65372dd7dc86de8f839e7acab959b5cf5eaf294c9`, zero host
imports, the same batch world and fixed64B/4KiB/512KiB integer inputs. The JS arm
bundles the actual portable Jco/unenv adapter and deliberately replaces its own
component's global Buffer. Both selected implementations return fresh zeroed
no-pool storage for this domain; actual Node's uninitialized/slab behavior is
not a timed comparator. Initial unsafe Node bytes are never inspected.

The exact retained minimal artifacts are12,044,770B native and12,248,336B JS,
an artifact-specific203,566B incremental adapter difference with the same full
profile engine. Component snapshot byte determinism is not established; the
prior correctness-only rebuild variation remains documented. No profile-free
engine-size saving, whole-application speedup, Wasmtime throughput result,
cross-platform conclusion or older timing transfer is claimed. Shared desktop
load, frequency/thermal state and n2 independent processes limit these results.

The original correctness-only README/STATUS and preflight-v1 records remain
unchanged. This separate directory records the later authorized measurement.
Raw stdout/stderr/start/partial/results files and exact measurement source copies
are retained; `analyze.mjs` reproduces arithmetic and receipt checks without
executing any workload or collecting new timing/memory samples.
