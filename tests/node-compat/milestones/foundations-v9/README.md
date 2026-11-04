# Accepted bounded foundations v9

The [freeze](results.json) contains **1,750 byte-verified evidence files**, **25
full reports**, all **302 native inputs**, three external embedding inputs,
original build sidecars/configurations, source audits, licenses and the test
harnesses. Earlier checkpoints remain unchanged. Archived historical templates
retain their own labels; copying a file here does not claim it was executed.

This checkpoint installs optional **m0.9 `node:stream/web`**, using real native
classes and guest codec/iteration/DataView facades, alongside core m0.8 and the
six earlier bounded foundations. The baseline revision is
`54b3329b3ce818fd1f244e871e9c259b63667cda`; Node is v22.14.0,
ComponentizeJS0.23/Jco1.40, SDK30/SpiderMonkey147, with recipe
`6ccabace68b5951bba98b1f713accb405d4a3ed18b3668bcd1d952a93e564677`.

| Ordinary Release engine | SHA-256 | Bytes |
| --- | --- | ---: |
| Stream/web OFF, entropy OFF control | `3bb37e5c3a97c8dbf263aec0bbdcaf16fc7e8561b2877c2525d31f032246e43b` | 9,724,375 |
| Stream/web ON, entropy OFF | `94e13fcef1b2a7e198f5b51e370e61bc730412fb3786c20d9ee9f4b554b57a25` | 9,750,233 |
| Stream/web ON, runtime entropy | `9f473312fb0f3f6652e3eb1b6809275b1b328585c906c06a4dec42b39b8edc4a` | 9,757,090 |

All three use identical native sources and the unchanged strict-v3 callback
policy. Actual flags and kernel compilation are recorded. The independent
source/configuration gates pass320 admission cases, eight generators and19
configure/no-clobber cases.

The [installed stream/web report](stream-web.json) proves exactly18 exports,
actual native constructor identities/brands, canonical/bare/default/static-CJS
relationships, uncached deployed aliases and snapshot resumption. Three
retained Jco calls and a fresh Wasmtime call pass41 constructor,250 codec,
four cancellation,24 guard,12 view, six controller,67 iteration and26 DataView
cases, with declared deviations and profile policies. Its correctness component
is `bc4aec0aa399f3f2fb72bdb9c2be81c0fae330d6f444d7ac0bfde2b78c4f90d3`,
13,578,693B, with zero imports. Seven top-level initializations fail as required.

The [native OFF guard](stream-native-guard.json) separately tests six controller
state/prototype cases and16 additional invalid receivers per call without the
Node-facing wrappers, across three retained Jco calls and fresh Wasmtime, zero
imports. [Both OFF import names](stream-off-admission.json) fail actual component
initialization as well as bundler admission. No old hazardous native path runs.

The [release index](release-index.json) records passed core Buffer/stub,
installed allocator/helper, all six prior modules and all four strict-callback
suites. The [optional index](optional-index.json) contains ten zero-import audits;
the strict suites retain24 zero-import components,24 rejected componentizations,
handled-instance reuse and fatal/discard checks. Previous allocation-failure and
moving-GC proofs remain tied to their exact earlier engines.

The same [joint HTTP component](http-audit.json),
`95bcdd80f86a345d2ce493f247fb99e8d347db94c9a773bf7da346a3ff01f796`
(62,006,265B), passes three requests each on unmodified
[Wasmtime42.0.1](wasmtime-http.json) and official
[wasmCloud2.11.0](wasmcloud-http.json). Fourteen computed bare aliases and all
module corpora pass. Both hosts stop with code0. Counters remain `[1,1,1]`, so
same-instance HTTP reuse and request isolation are not established.

The exact standard0.2.10 imports are HTTP types, I/O error/poll/streams,
random/random and monotonic-clock. The last is a nominal duration-type dependency
with **zero callable clock imports**. No outgoing HTTP, filesystem, DNS, socket,
CLI/environment, TLS or custom host service is selected. Pure scalar fixtures
require zero imports.

UTF8/fixed-attached-unshared/local-layout/min1 adapter restrictions remain.
Writable controller signal, Proxy behavior, some error codes and constructor
metadata differ. Compression/decompression exports explicitly reject call/new.
Per-operation caps do not bound total retained queues/output or native allocator
failure. No complete Node, Buffer or Web/classic Stream support is claimed.
Corpus sizes are correctness artifacts, not minimal-size or acceleration claims.
Production ALS/tick scheduling, classic streams, compression/crypto and optional
Node I/O remain in the [active roadmap](../../../../docs/node-compat/roadmap.md).
