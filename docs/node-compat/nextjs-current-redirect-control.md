# Current-build redirect browser controls

Updated 2026-11-08. This isolates the browser workload from the earlier full
HTTP/cache/supplemental sequence. It does not replace that sequence or accept
the full Next.js profile.

| Profile | Current-build browser result | Execution |
| --- | --- | --- |
| Generated standalone server, ordinary Node HTTP | Both strict tests pass | Original owner891/600, raw0/clean |
| Node with the shared HTTP bridge and module provider | Both strict tests pass | Original owner4007/300, raw0/clean |
| Existing real Wasm component and standard WASI observer envelope | Both strict tests pass | Original owner3802/600, raw0/clean |

All three select the same corrected Next16.4.5/React19.3.1 standalone build:
2,196 files/48,800,578 bytes, build review`80c59d47`. The physical browser/client
family is`7c3a7d87`; the original counter and redirect interaction bodies,
network observers, deadlines, capture drains and strict error predicate are
preserved. Actual generated HTML supplies five client scripts and four actions
scripts, with independent physical hashes. There is no preceding application
HTTP warmup or cache/supplemental suite. Different server adapters and their
resulting compression/header behavior remain real profile differences.

The [pristine DATA review](../../tests/node-compat/frameworks/nextjs/next-pristine-redirect-root-results-v1/actual-control-review.json)
verifies one bare`node app/server.js` run, without the bridge, module provider or
preload. Both functional tests and strict browser completion pass. Redirect
POST7 returns200, with a complete2,963-byte decoded body, fulfilled body/sizes/
response.finished and no observer/page/console/request errors. Node applies gzip;
the reported encoded response body is1,531 bytes. Its body hash is a decoded-body
hash, not a wire hash. Browser-local observations finish before context closure.
The server's requested SIGINT exits130 naturally; that expected server status is
distinct from the successful controller and browser exit0.

The retained [raw packet](../../tests/node-compat/frameworks/nextjs/next-pristine-redirect-root-results-v1/raw/index.json)
contains123 payloads/5,245,828 bytes, including browser bodies, traces, NetLog,
screenshots, original owner records, Source/bindings and the final owned-app
inventory. App copies, temporary directory contents and external binaries are
omitted. Reviewer browser authorship and finite verification scope are disclosed
in the primary review.

The earlier failed full pair used the older2,186-file build and ran24HTTP,
52 cache checks and80 supplemental checks before the browser. A pristine pass
against this new build therefore cannot identify the earlier failure's cause.
The fixed pair keeps the current app and browser-only workload while
selecting the existing bridge Node and Wasm profiles. Both finish raw0/clean
with protected inputs and successful browser clients. The
[paired DATA review](../../tests/node-compat/frameworks/nextjs/next-current-redirect-root-results-v1/actual-runtime-review.json)
(`1a689477`) verifies both strict passes and the
[167-file raw packet](../../tests/node-compat/frameworks/nextjs/next-current-redirect-root-results-v1/runtime-records/index.json)
(9,038,560 bytes). Native stdout is complete at13,459 bytes/48 chunks; the host
shuts down normally at0. Both redirect responses have complete2,963-byte decoded
bodies and fulfilled sizes/finished before context closure. Their decoded hashes
and gzip lengths differ across native, bridge and pristine Node; no byte-for-byte
RSC parity or wire hash is claimed. Its Source changes only
control identities, required client suite and current binding declarations;
transport, backpressure, copying, capture and guest code remain unchanged.
The next comprehensive pair will use this exact current build and strict worker,
restore the original HTTP/cache/supplemental/stream workload, and retain the
legacy generation and every other original predicate. This is a new workload
comparison; previous failed runs are not retried or overwritten.
The [comprehensive successor](../../tests/node-compat/frameworks/nextjs/next-current-full-root-results-v1/README.md)
is prepared with both fixed authorities (`35f5ad50`), fresh2,025-descriptor input
closure and genuine before/final constructor/world guards. Source review and
three Node syntax checks pass. Its full client has a distinct real source family
from the unchanged browser worker. Execution scope starts false and is derived
from published collection, separately from the unchanged success predicate.
The first preparation's external fixture-contract omission was caught before
execution and retained with all13 metadata payloads. Corrected binding explicitly
checks all six client dependencies. No test/actor code or assertion changed,
and zero trials ran under that held preparation.

The comprehensive pair now completes once per arm, with unchanged gates:

| Gate | Wasm | Bridge Node22 |
| --- | --- | --- |
| HTTP | 24/24 pass | 24/24 pass |
| Portable cache | 52 checks pass | 52 checks pass |
| Supplemental | 80 checks pass | 80 checks pass |
| Incremental stream | Five chunks; pass | Five chunks; pass |
| Strict browser | Both tests pass | Both tests pass |
| Legacy generation | 1→1; fail | 1→2; pass |
| Original/full client | Fail | Pass |

Original native7204/600 exits1 cleanly; Node7523/300 exits0 cleanly. Both publish
`fullOriginalContractExecuted:true`. The native actor retains its assertion for
the semantic client exit1 while collection itself completes. The
[independent JSON crosscheck](../../tests/node-compat/frameworks/nextjs/next-current-full-root-results-v1/independent-gate-crosscheck.json)
recomputes the original and final conjunctions and verifies the sole false
native term. The [primary DATA review](../../tests/node-compat/frameworks/nextjs/next-current-full-root-results-v1/actual-runtime-review.json)
(`303ca42f`) verifies all detailed HTTP/cache/supplemental/stream/browser data,
both original owners and complete28,746-byte/111-chunk native stdout. The
[raw packet](../../tests/node-compat/frameworks/nextjs/next-current-full-root-results-v1/runtime-records/index.json)
retains632 payloads/13,614,165 bytes, including19 indexed input Source families,
all six explicit client dependencies, owner/client/body records and the held
preparation. App/cache trees and external binaries are omitted. The emitted
imports remain13 standard WASI0.2.10 interfaces. This new positive
browser sample does not explain or repair the earlier aborts. Arbitrary
cross-request JS globals, general lifecycle guarantees and full Next acceptance
remain outside the verified result.

The [next-step Source audit](../../tests/node-compat/frameworks/nextjs/next-current-full-root-results-v1/next-steps.md)
distinguishes the module-local counter from actual persisted cache operations.
A fresh callback can still return1; the nonce-based cache profile already tests
hits and invalidation separately. Next validate a separately versioned bounded
FS-backed callback state contract under the existing standard cache preopen,
keeping the legacy fixture and assertion intact. No arbitrary closure/object
persistence, concurrent increment, CAS or crash durability is implied.

The [bridge cancellation audit](nextjs-bridge-cancellation-audit.md) records an
untested close/drain seam and proposes a focused regression. Neither this Source
finding nor a single positive run proves causation, reliability, host TCP
completion, component reuse or private request/Store identity. Earlier redirect
failures, the portable profile's unavailable arbitrary cross-request JS-global
continuity, lifecycle gates and production acceptance remain unchanged.
