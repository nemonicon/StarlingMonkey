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

The [bridge cancellation audit](nextjs-bridge-cancellation-audit.md) records an
untested close/drain seam and proposes a focused regression. Neither this Source
finding nor a single positive run proves causation, reliability, host TCP
completion, component reuse or private request/Store identity. Earlier redirect
failures, the portable profile's unavailable arbitrary cross-request JS-global
continuity, lifecycle gates and production acceptance remain unchanged.
