# Weval native/Jco Buffer measurements

The exact frozen-v5 Weval pair completed **80 arm/scenario runs, 240 fresh instances and 1,680 timed batches**. Two rounds reverse each scenario's arm order; each arm/scenario/round uses three fresh instances, three warmup batches and seven retained batches. All setup/run checksums match Node 22.14.0; all memory-growth attempts succeeded. Component construction and Wasmtime compilation completed before measurement. [Raw samples](results.json), [compilation](compilation-results.json), [app artifacts](app-artifacts.json) and [copy/source receipt](measurement-receipt.json) retain the evidence.

An [independent read-only audit](independent-audit.json) passed 4,190 checks over digests, raw/aggregate arithmetic, per-round ratios, opposite arm orders and all 20 independently reconstructed ASCII/FNV/fingerprint checksums. It found no substantive issue. This is an integrity/source/data review, not independent runtime reproduction or statistical-significance evidence.

Both arms use engine `22b771cd…`, generic read-only cache `f6fe6200…`, verified Weval 0.5.1, the audited v2 guest splicer, identical selected libraries and feature-OFF/zero-import policy. The native arm uses the actual registered Buffer; the JavaScript arm bundles the actual Jco 1.40 / unenv 2.0.0-rc.24 adapter. Snapshot checks distinguish their implementation/global-Buffer identities. No stock-engine/cache fallback, DEBUG/fault work, raw memory access, private telemetry or host modification was used.

The following ratio is **native throughput / Jco throughput** within this Weval configuration. Values below one mean lower native throughput. Medians aggregate 42 retained batches over six fresh instances per arm/scenario; those batches are correlated, not 42 independent trials.

| Shared operation | 64 B | 4 KiB | 64 KiB | 512 KiB |
| --- | ---: | ---: | ---: | ---: |
| Hex encode | 1.80× | 60.5× | 197× | 216× |
| Hex decode | 36.5× | 414× | 491× | 515× |
| `Buffer.from(existing Buffer)` | **0.786×** | **0.759×** | 0.990× | 1.027× |
| UTF-8 encode, ASCII | 31.1× | 963× | 1,988× | 2,225× |
| UTF-8 decode, ASCII | 3.68× | 151× | 656× | 1,731× |

The copying constructor is the historical raw scenario named `byte-copy`. It **does not call `Buffer.prototype.copy`**, which remains deferred, and it does not test a new C++ copying kernel. Its native-profile route is the JavaScript facade plus captured Uint8Array `set`. Native constructor throughput is about 21% lower at 64 B and 24% lower at 4 KiB. These observations do not justify adding a C++ copy kernel without a separate experiment.

The selected unenv source actually uses JavaScript `utf8ToBytes`, `utf8Slice`, `hexWrite` and `hexSlice`; the UTF-8 comparison is not two wrappers over the same TextEncoder. The native byte-codec route is substantially faster in these cases, including both arm orders. This is whole API-route performance for the pinned Weval pipeline, not an isolated primitive measurement or a claim that Weval itself causes these speedups. No ordinary-v5 timing arm was run here.

Memory results have exceptions:

| Operation / input | Peak process RSS, MiB: native / Jco | Largest requested linear memory, MiB: native / Jco |
| --- | ---: | ---: |
| Hex decode / 4 KiB | **44.44 / 39.61** | **20.31 / 13.50** |
| Hex decode / 64 KiB | **44.30 / 39.75** | **20.75 / 14.44** |
| Hex decode / 512 KiB | **46.39 / 41.52** | **23.38 / 19.69** |
| UTF-8 encode / 4 KiB | **44.36 / 40.72** | **20.31 / 18.06** |
| Copying constructor / 64 B | 33.36 / 61.66 | 10.25 / 52.06 |
| UTF-8 encode / 512 KiB | 44.89 / 163.73 | 22.25 / 147.06 |
| UTF-8 decode / 512 KiB | 38.95 / 173.22 | 15.75 / 153.06 |

Thus a faster byte codec can still have a higher memory high-water. RSS includes Wasmtime, code and allocator retention; later instance peaks are cumulative within a measurement process. The ResourceLimiter value is the largest desired size of one linear memory, not live heap, aggregate committed memory, allocation count or evidence of a leak.

Per-scenario median instantiation spans about 20.8–37.9 microseconds for native and 23.2–43.0 for Jco. It excludes engine creation and precompiled-component deserialization; the raw reports retain those separately along with setup and first-batch timings. Startup ranges overlap, so no uniform startup win is claimed. Native/Jco component sizes are 17,761,277 / 19,223,955 bytes, or 5,302,460 / 5,669,134 gzip: a single observed increment of 1,462,678 raw / 366,674 gzip bytes. Both retain the profile, and their total API coverage differs; this is additional-adapter deployment cost in this configuration, not minimum profile-disabled size or equal complete Buffer implementations.

These measurements support native guest byte-codec work for the bounded workload, while preserving the copying-constructor and memory counterexamples. One local machine run, correlated batches, fixed ASCII sizes, whole-process watermarks, O(1) result fingerprinting and background scheduling limit generalization. The Weval and ordinary-v5 pipelines use different static-library/optimizer variants and separately built libcrypto bytes; **no one-variable ordinary-versus-Weval causal comparison** follows. Complete callback ABI/codec/Buffer corpora, Weval RuntimeOnly entropy/HTTP/wash deployment and the stopped new OOM gate remain separate outstanding gates.
