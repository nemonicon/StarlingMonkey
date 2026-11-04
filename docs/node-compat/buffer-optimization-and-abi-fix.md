# Fresh Buffer allocation and scalar export follow-up

This follow-up keeps the `sm-node-22.14.0-m0.1` API boundary. It changes the
implementation of admitted fresh Buffer allocations and applies one explicit
ComponentizeJS guest patch. No additional Node operation, WASI import or host
service is enabled. The [original performance experiment](portability-and-performance.md)
remains a historical result for its recorded engine hashes.

## Allocation mechanism and implementation

The original facade validated each result by reading its typed-array `buffer`
getter, then checked length, installed `Buffer.prototype` and entered a private
WeakSet. SpiderMonkey's typed-array `BufferGetterImpl` calls `ensureHasBuffer`.
For arrays using inline storage this allocates an ArrayBuffer and copies bytes;
already malloc-backed storage can be transferred. Reading `.buffer` is therefore
observable allocation work even when application code never requests it.

Factorial controls on the original release engine isolate the stages. For
10,000 64-byte copies per batch, plain Uint8Array copying took a median 23.28 ms
with a largest linear-memory request of 9.50 MB. Adding the backing getter took
27.91 ms and 45.15 MB. Adding WeakSet branding alone took 25.87 ms and 9.50 MB.
Combining the getter and WeakSet took 31.87 ms and 51.45 MB. These measurements
implicate backing materialization and its interaction with allocation/GC;
they do not show a WeakSet leak. The high-water values are aggregate runtime
responses, not per-array allocation counts or isolated heap sizes.

Full checked source/output tagging took 120.62 ms; keeping source checks and
trusting the freshly allocated result took 70.26 ms with 9.50 MB. At 4 KiB the
same contrast was 3.116 versus 2.109 ms per 256 operations, without the small-array
memory contrast. The [probe record and source references](../../tests/node-compat/optimization/README-probes.md)
describe these diagnostic controls. They are not replacement Buffer APIs.

The production facade now has two private paths:

* External input and observable species/subarray results keep backing-kind,
  fixed-storage, attachment, length and typed-array checks.
* Fresh outputs from validated Uint8Array allocation, the private C++ hex
  decoder and the captured native TextEncoder receive prototype/WeakSet tagging
  without rereading their backing buffer and length.

The native encoder/decoder methods, fill, prototype installer and WeakSet
operations are captured at installation. Application replacement of those public
methods cannot forge a trusted producer or detach a result during tagging.
WeakSet branding remains private; an ordinary array with `Buffer.prototype`
does not become a Buffer. Public `.buffer`, `parent`, offsets and shared view
relationships retain their specified behavior. Materialization can still occur
when an admitted operation actually requires backing access.

The C++ byte kernels, rooting, no-GC borrowing, allocator ownership and export
manifest are unchanged. This is an allocation/validation reduction in the small
JavaScript facade, with a regenerated checked-in factory header.

## Matched release measurements

Both arms use the identical scalar-export ABI patch, ComponentizeJS source,
SpiderMonkey archive and compiler tools, built sequentially in the same CMake
directory. The only compiled
repository source differences are `buffer-facade.mjs` and its generated header.
The original facade control engine is `6daf1f03438aad3a14124b2dc09f95f09b91eac285233c2345cbd1a24b302748`;
the candidate is `3f5bf602ad2d1507db5c1bcd5b938984aba9ca65af4c5a840b5bf8fcd09d370f`.
Both components have zero host imports and use identical bundled application
bytes. All 20 setup/full-byte and loop/fingerprint checksums match Node v22.14.0.

The shared CMake cache was inspected after the later stress build: release,
`WEVAL=OFF`, `USE_WASM_OPT=ON`. Historical sidecars did not separately capture
those cache settings for each engine, so identical optimization flags rely on
the recorded shared-directory workflow rather than independent per-artifact
cache snapshots. The build recipe now explicitly sets those flags and captures
the actual option map and build-file hashes for future builds. This addition
does not retroactively strengthen the historical metadata. The
[flag audit](../../tests/node-compat/optimization/build-flags-audit.json)
records the observed cache and the unexecuted new capture path explicitly.

The Wasmtime 42.0.1 experiment covers five operations and four payload sizes,
with three fresh instances and seven timed batches after three warmups:
120 instances and 840 timed batches. Arm order alternates by scenario, which
also confounds order with size: 64 bytes/64 KiB always run control first, and
4 KiB/512 KiB candidate first. Timings
use the host clock with compilation isolated. Within-instance batches are
correlated; these are not independent paired trials across repeated component
builds. There is one snapshot/component build per arm. Full observations,
quartiles, source hashes and build records are
preserved in [results](../../tests/node-compat/optimization/improvement-results.json)
and the [artifact manifest](../../tests/node-compat/optimization/improvement-artifacts.json).

At 4 KiB, logical payload MiB/s:

| Operation | Original facade | Candidate | Candidate / original |
| --- | ---: | ---: | ---: |
| Hex encode | 283.07 | 283.81 | 1.00× |
| Hex decode | 158.35 | 193.46 | 1.22× |
| Byte copy | 292.78 | 450.10 | 1.54× |
| UTF-8 encode, ASCII | 288.12 | 438.59 | 1.52× |
| UTF-8 decode, ASCII | 309.93 | 309.96 | 1.00× |

For 64-byte payloads, copying improves from 4.55 to 7.55 MiB/s (1.66×), and hex
decode from 6.06 to 12.03 MiB/s (1.99×). In both cases process peak RSS falls
from about 52.9 to 24.3 MiB, and the largest linear-memory growth request falls
from 51,445,760 to 9,502,720 bytes. The 64-byte UTF-8 encode path is 1.93× faster,
but its peak RSS remains about 51.5–51.7 MiB and its largest linear-memory request
is unchanged. Memory improvement is therefore specific to some allocation paths.

The remaining UTF-8 allocation structure is visible in source:
[`TextEncoder::encode`](../../builtins/web/text-codec/text-encoder.cpp) calls
[`core::encode`](../../runtime/encode.cpp), adopts its owned UTF-8 bytes with
`JS::NewArrayBufferWithContents`, releases ownership only on success, then
creates `JS_NewUint8ArrayWithBuffer`. These outputs already have an ArrayBuffer,
so skipping the getter cannot remove that producer allocation. The bytes are
adopted rather than copied again into the view. The exact RSS/linear-memory peak
still needs allocation telemetry before attribution. The existing `encodeInto`
path is a possible basis for a future direct-fill experiment, but exact backing
length, Unicode replacement, rooting and error behavior must be preserved and
measured before changing the shared web implementation.

The original short-batch run also records 7.7% lower 512 KiB UTF-8 decode
throughput in the candidate. Those batches contain only two operations and take
about 0.55–0.60 ms. A separate
[32 MiB-batch stability check](../../tests/node-compat/optimization/stability-results.json)
reuses the exact compiled components and checks both arm orders. At 512 KiB,
the candidate/control ratios are 0.9957 and 0.9910; the original 7.7% drop does
not reproduce under this longer protocol. At 64 KiB the ratios are 1.0308 and
1.0375. Each pass uses three fresh instances and seven timed batches after three
warmups. Longer batches change GC/allocation pressure as well as relative timer
noise; this does not prove the earlier difference was caused solely by timing
noise. These results compare two native facades and do not justify uniform
improvement. They must not be multiplied by historical JavaScript-adapter ratios
from a separate run.

The candidate engine grows by 1,006 bytes. In this component build, component
size grows from 10,987,179 to 10,992,307 bytes, and gzip size from 3,692,206 to
3,744,508 bytes. Both serialized Wasmtime artifacts are 43,138,736 bytes.
This artifact pair demonstrates no size saving or general cold-start
improvement. Snapshot output is not deterministic, so replicated builds are
needed to isolate any size cost from build variability. Small throughput
differences also need independent runs before attribution.

## Component and host validation

The candidate release and compacting-GC-stress engines both pass the full
381-string/250-byte-vector native suite, alias/static/dynamic/cache checks,
four expected initialization failures, and repeated Jco calls. Added actual
guest checks cover eight boundary sizes, three spoofed input shapes, four public
property shadows, copied/shared buffer relationships, species, resizable and
detached inputs, and replacement of public producer/branding methods. Replacement
methods are never called. Both pure components have zero host imports.
SharedArrayBuffer construction remains unavailable in the guest and is recorded
as skipped; supplemental Node tests cover that rejection path. GC stress is
excluded from performance measurements and is not exhaustive OOM testing.

The same candidate HTTP component,
`6d89f735849d74b0af1ba42f2db814cf539a8199d71f172021cb21a3f1d03897`,
passes three requests on Wasmtime 42.0.1 and three on the official unmodified
wasmCloud 2.11.0 local host. Each request includes the original corpus and new
intrinsic checks. Imports remain `wasi:http/types`, `wasi:io/error`,
`wasi:io/poll`, `wasi:io/streams` and the type-only
`wasi:clocks/monotonic-clock`, all at 0.2.10. There are no clock functions,
outgoing HTTP, filesystem, sockets, DNS, environment, entropy or custom host
imports. The host stops cleanly. Request counters remain one, so this establishes
neither instance reuse nor concurrent request isolation. The
[candidate validation record](../../tests/node-compat/optimization/candidate-validation-results.json)
couples the actual engine/component hashes, reports and additional assertions.

## Scalar export binding

At pinned ComponentizeJS source `4d812f5a7b524cea5bcfd565cac55f3fab876a57`,
`embedding/embedding.cpp:call` reads a core-I32 return using `ret.toInt32()`.
A lowered JavaScript `u32` above `INT32_MAX` is represented as a boxed Double.
Reading the Int32 payload produces incorrect bits. The checked-in
[patch](../../tests/node-compat/abi-fix/componentize-u32-result.patch) reads the
numeric value and applies `JS::ToInt32`, preserving its low 32 bits. That numeric
conversion does not allocate, invoke user coercion or add a host capability.

The ABI-only control engine passed all 339 actual-component Jco checks and 16
Wasmtime direct boundary/constant/computed checks. The released control reproduced
138 scalar-u32 failures; all 65 signed/float/container/string controls passed.
See the [ABI regression record](../../tests/node-compat/abi-fix/README.md).
This patch is applied to the external guest source by `build-engine.sh`; it is
not a fix in the released ComponentizeJS 0.23.0 package or a host modification.

A separate imported-callback argument reader in
`crates/spidermonkey-embedding-splicer/src/splice.rs` still mishandles high-u32
arguments. A composed guest identity helper reproduces three bad values with
zero final host imports, while its constant return and the repaired scalar
export pass. The export patch does not change that path. Arbitrary imported
high-u32 calls remain outside the validated toolchain contract until separately
fixed. The benchmark retains its original signed checksum carrier for matched
comparison; the direct export regression uses real `u32` results.

## Remaining gates

Keep the profile opt-in. Exhaustive OOM injection, explicit GC/allocator counters,
shared inputs when available, a Weval-enabled comparison, concurrent request
state and production cluster lifecycle remain separate work. HTTP packaging
still uses the pinned, hash-guarded workaround described in the portability
report. The scalar export patch does not remove that packaging requirement.
