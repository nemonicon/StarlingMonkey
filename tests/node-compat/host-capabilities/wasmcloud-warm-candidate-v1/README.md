# Stock wasmCloud normal deployment: P2 warm reuse unavailable

**Source finding only — no host/NATS/registry/guest was launched.** The unchanged
93,929-byte probe `32830d393ceccc7aaf7f399bd6816ab54928cc240db9b228352b3f16d2f1d720`
uses WASI HTTP 0.2.10 (P2). Pinned wasmCloud 2.11.0 Source
`bc5acfb8e15f7d6d199ca940354d82e590c2d5ff` explicitly creates a new store and
instance for every P2 HTTP request. Normal deployment therefore cannot establish
the required warm counters 1, 2, 3 under the unchanged component/host constraints.
Deployment preparation stopped at this finding. No NATS/zot binaries were downloaded.

The [actual routing branch](https://github.com/wasmCloud/wasmCloud/blob/bc5acfb8e15f7d6d199ca940354d82e590c2d5ff/crates/wash-runtime/src/host/http.rs#L3658-L3764)
uses the pool only when `targets_p3` is true. Its
[P2-specific warning](https://github.com/wasmCloud/wasmCloud/blob/bc5acfb8e15f7d6d199ca940354d82e590c2d5ff/crates/wash-runtime/src/host/http.rs#L2614-L2635)
also states that `poolSize` does not pool P2 HTTP. The subsequent P2 detached task
instantiates the component per call (lines 3798–3815). This is a source-derived
limit; no normal-deployment counter observation is claimed. C independently
checked this branch; the author read the same branch directly.

## Genuine control and artifact path

[plan.json](plan.json) retains the bounded, **unexecuted** normal-deployment
rights proposal. All Root/action/result/port/artifact-path slots remain null.
[workload-start.template.json](workload-start.template.json) uses the generated
Protobuf JSON field names and explicitly marks unresolved substitutions with `$ROOT_`.
It is a template, not an issued request or deployment authority.

The pinned [washlet transport](https://github.com/wasmCloud/wasmCloud/blob/bc5acfb8e15f7d6d199ca940354d82e590c2d5ff/crates/wash-runtime/src/washlet/mod.rs#L1479-L1537)
accepts UTF-8 JSON, **not binary Protobuf or a gRPC request**, on
`runtime.host.<hostId>.workload.start`; status and stop use `workload.status` and
`workload.stop`. Discover the sole private host through
`runtime.operator.heartbeat.*` and check its payload ID against the subject.
The existing stock `wash host` takes explicit scheduler/data NATS URLs and HTTP
listen address; there is no need for an invented `workload` CLI subcommand.

The [normal receiving path](https://github.com/wasmCloud/wasmCloud/blob/bc5acfb8e15f7d6d199ca940354d82e590c2d5ff/crates/wash-runtime/src/washlet/mod.rs#L1733-L1748)
constructs `ComponentSource::Oci` unconditionally. Its generic loader also has a
File variant, but that variant is not selected by WorkloadStart. A `file://`
image is not a legitimate shortcut here. The proposed genuine route was a fresh
loopback stock zot registry, stock `wash oci push ... --insecure`, then an actual
OCI digest reference in WorkloadStart and a fresh host OCI cache. The manifest
digest is distinct from the component SHA256. No cache entry would be fabricated.

Official release metadata/checksum files are retained only to pin proposed
downloads: NATS 2.15.2 darwin-arm64 tarball, 6,785,830 bytes,
`cbd2219d01502c38733485ac684269da585ee479fa3b1377264beecdefdf9e9d`;
zot 2.1.22 minimal darwin-arm64, 76,420,498 bytes,
`c81a26040ae79c7e8a90c306a2377c69982a86ff35c259427bd9accea0eca14c`.
Neither binary was downloaded, installed, executed, or authorized by this packet.

## Rights proposal and remaining limits

The real [volume implementation](https://github.com/wasmCloud/wasmCloud/blob/bc5acfb8e15f7d6d199ca940354d82e590c2d5ff/crates/wash-runtime/src/engine/volumes.rs#L28-L76)
maps `readOnly: true` to read-only filesystem permission plus read open mode;
false adds write mode. Normal deployment can therefore express narrower rights
than the prior `wash dev` mount. Actual enforcement is still untested here.
A future rights-only control should leave the app directory writable by its
host owner and demonstrate that host-side creation succeeds, then require
guest `/app` descriptor flags 1, read success and create refusal. This avoids
confusing Unix mode denial with restricted WASI capability rights. Direct cache
descriptor flags 33 and create/write/read/link/EEXIST/rename/unlink need actual
observations before any acceptance.

The unchanged probe performs those operations only through exact `/app` and
`/cache` descriptors. A separate `/app/.next/cache` mount merely appears in its
preopen names/flags. It does **not** prove nested file operations, overlay
resolution, or the Next native-FS longest-preopen selection. This proposal
keeps that distinction explicit.

`poolSize:1`, `maxInvocations:32`, `maxConcurrency:1`, `reclaimWindowSeconds:0`
are genuine normal API fields and produce a bounded warm policy, but they cannot
override the P2 HTTP branch. A separately scoped P3 guest/engine or a different
stock P2-reusing host would be a new decision. No host modification, custom guest
service, or new guest build is proposed as an automatic fallback.

`upstream-index.json` records downloaded primary files and their SHA256 plus
Git blob SHA1, authenticated against the pinned complete GitHub tree. The
fetcher performs network Source reads only. The packet's `index.json` closes all
retained files; no runtime/admission proof or independent approval is issued.
