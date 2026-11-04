# Portability and performance results

This is the original measured baseline, preserved for its exact historical artifacts.
Current portability acceptance is [v10](../../tests/node-compat/milestones/foundations-v10/results.json):
the same HTTP component (63,626,509 bytes) passes both stock hosts with six selected
standard 0.2.10 interfaces, explicit random and type-only monotonic clock.
Counters restart at 1; reuse/isolation is unproved. The bounded Events extension
retains a confirmed callback-return getter counterexample and Symbol registry gap.

The reviewed [m0.11 source adoption](../../tests/node-compat/foundation-alloc-unsafe/production-adoption-m0.11/source-receipt.json)
is applied but lacks fresh production gates. The separate
[private experiment](../../tests/node-compat/foundation-alloc-unsafe/production-candidate-m0.11-v2/README.md)
suggests possible CPU improvement, with higher RSS in 29/30 comparisons, higher
capacity in 4/30 and an 8,513-byte larger minimal snapshot. Seven slower controls,
five reversals and n=2/correlated samples limit interpretation; no memory, size,
Jco-adapter or whole-application win, or performance transfer to the rebased
source, is claimed.

The current [corrected-clock results](../../tests/node-compat/bench-clock-v2/RESULTS.md),
[matched UTF8 allocation experiment](../../tests/node-compat/utf8-direct/README.md)
and [frozen-v5 Weval comparison](../../tests/node-compat/weval-experiment/v5/RESULTS.md)
retain separate engine/source/tool receipts. The Weval pair confirms bounded byte-codec
throughput gains and copying/memory counterexamples; it does not isolate Weval
as a single causal variable. The later
[allocation optimization and scalar export fix](buffer-optimization-and-abi-fix.md)
has separate engine hashes, regression results and matched before/after data.

The bounded native profile runs on the official, unmodified wasmCloud 2.11.0
local host. Its hex and UTF-8 conversion paths substantially outperform Jco's
actual JavaScript Buffer adapter in the measured release mode. Byte copying is
slower, and memory results vary by operation. These results justify selected
native conversion paths; they do not establish complete Buffer compatibility,
universal memory savings or application-level speedups.

## Portability evidence

The same HTTP test component, SHA-256
`d32752b8f240d8edaa2f868469c4b788bd31da8cf0739230b7ed2884f3206f7f`,
passed three requests on Wasmtime 42.0.1 and three on wasmCloud 2.11.0's official
`wash dev` host. Each request ran 381 string cases and 250 byte-array cases
against the Node v22.14.0 oracle, checked aliases/global/CommonJS identities,
and exercised unsupported operations with attributed errors. The host binary's
release digest, effective configuration, commands, responses and graceful shutdown
are preserved in the [wasmCloud execution record](../../tests/node-compat/wasmcloud/historical/d32752b8-host-results.json).

The component exports `wasi:http/incoming-handler@0.2.10`. Its exact imports are
`wasi:http/types`, `wasi:io/error`, `wasi:io/poll`, `wasi:io/streams`, and
`wasi:clocks/monotonic-clock`, all at **0.2.10**. The clock interface supplies only
`duration = u64`: the actual component type graph has no clock functions, and
the core has no clock imports. No outgoing HTTP, filesystem, DNS, sockets,
environment, entropy, custom Node or wasmCloud service is imported. The pure
integration and benchmark worlds retain zero imports.

The host listened on loopback, with empty network/DNS/host-loopback allowlists,
no volumes, custom plugins, sidecars, Docker or NATS. This validates the released
local deployment workflow, not a production cluster. Request counters stayed at
one; neither instance reuse nor general request isolation was established.

ComponentizeJS 0.23.0 needs a version-specific packaging adapter for this narrow
HTTP world. A source-hash-guarded composition of its real `stubWasi` API preserves
manual HTTP types and removes outgoing HTTP, entropy, clocks and stdio functions.
The final core has no Preview1 imports and is wrapped without an adapter. No
installed npm file, native engine, Wasmtime binary or wasmCloud binary was
modified. The proposed upstream patch is explicitly unapplied and uncompiled.
See [reproduction and packaging details](../../tests/node-compat/wasmcloud/README-host.md).

## Matched Buffer experiment

Both arms use the same custom release engine, with `WEVAL=OFF` and
`USE_WASM_OPT=ON`, on an Apple M2 arm64 host with 16 GiB RAM. The comparator is
Jco 1.40.0's actual Buffer adapter and unenv 2.0.0-rc.24/Feross core. Identity
checks exclude accidental use of the native Buffer in the JavaScript arm.
Both worlds have zero host imports; timing uses the host's monotonic clock.

The experiment covers five operations and four payload sizes. It uses three
fresh instances per arm/scenario, three warmup batches and seven measured
batches per instance: **120 instances and 840 timed batches**. Compilation is
isolated in separate processes. Setup/full FNV checks and every measured batch's
consumed-result checksum match Node. The seven batches within an instance are
correlated, not seven independent setup trials. Raw timings, quartiles, memory
observations and source hashes are in the [benchmark record](../../tests/node-compat/bench/results.json).

Representative 4 KiB payload results:

| Operation | Native profile payload MiB/s | Jco JavaScript payload MiB/s | Native throughput / JavaScript |
| --- | ---: | ---: | ---: |
| Hex encode | 293.30 | 2.71 | 108.19× |
| Hex decode | 159.38 | 0.35 | 460.72× |
| Byte copy | 302.19 | 350.41 | 0.86× |
| UTF-8 encode, ASCII input | 299.21 | 0.37 | 819.74× |
| UTF-8 decode, ASCII input | 311.89 | 0.64 | 484.29× |

Across the four tested sizes, copying throughput was approximately 4–15% lower
in the native profile. Conversion gains are specific to this non-Weval engine
and bounded workload; a Weval-enabled JavaScript comparison remains a separate
experiment. For hex decode, the ASCII API input is twice the logical payload
size. The raw `inputMiBPerSecond` fields are payload-normalized despite their
legacy name. Result sampling may materialize rope strings, so string timings
include that observable access.

Memory does not improve uniformly. For 512 KiB ASCII payloads, UTF-8 encoding
peaked at about 35.84 MiB process RSS in the native arm and 151.80 MiB in the
JavaScript arm; decoding peaked at 29.88 and 148.61 MiB. Conversely, 64-byte hex
decoding peaked at about **52.62 MiB native versus 24.44 MiB JavaScript**. These
are process high-water marks, including Wasmtime/code/allocator retention, not
isolated JS heap measurements. Largest linear-memory growth requests are
reported separately and are not total resident memory. Allocation profiling is
needed before assigning a cause to the regressions.

| Artifact | Native arm | JavaScript arm |
| --- | ---: | ---: |
| Component bytes | 10,991,198 | 11,273,296 |
| Gzip bytes | 3,694,472 | 3,804,714 |
| Serialized Wasmtime component bytes | 43,122,352 | 43,122,352 |

The controlled component delta is 282,098 bytes, or 110,242 bytes after gzip.
Both arms retain the installed native profile, and Jco supplies a broader API
surface, so this is incremental adapter overhead rather than a minimal
production deployment comparison or a pure kernel-code size delta. No compiled
cache-size saving was observed. Compilation took about 5.1 seconds per arm in
one observation each. Fresh instantiation from precompiled bytes had medians of
27.35 microseconds native and 33.92 microseconds JavaScript across 60 instances
per arm; this excludes process startup, compilation, deserialization and the
first guest call and is not an end-to-end cold-start claim.

## Export binding defect found by the correctness gate

A separate [minimal ABI diagnostic](../../tests/node-compat/bench/abi-diagnostic.mjs)
contains no Buffer code. Both the released and custom ComponentizeJS 0.23.0
engines returned incorrect tested `u32` values above `2^31 - 1`; for example,
`2342402100` returned as `109051904`. In-guest/string values and the signed
`s32` control were correct. The [recorded reproduction](../../tests/node-compat/bench/abi-results.json)
does not claim an exact implementation cause or fix.

Benchmark FNV checksums use `s32` with `|0`, then reinterpret those bits as `u32`
in the host. Sizes and iteration counts stay below `2^31`. This preserves every
checksum bit and passes the independent oracle; it does not repair arbitrary
application `u32` exports.

## Engineering decisions

The baseline justified keeping native conversion paths experimental and
investigating copying overhead and small-buffer memory before wider use.
The [follow-up](buffer-optimization-and-abi-fix.md) isolates backing-buffer
materialization, changes fresh-output tagging and repairs scalar-u32 exports.
The pinned HTTP packaging workaround still needs an upstream correction.
Further work includes OOM injection, shared input construction when available,
production-host lifecycle validation and a separate Weval comparison. No
additional Node module or Buffer API is enabled by these measurements.
