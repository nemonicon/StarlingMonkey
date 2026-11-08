# Full Next contract on stock wasmCloud

The comprehensive Next application executes on stock wasmCloud 2.11.0. Its HTTP,
persistent-cache, supplemental, streaming and functional browser checks pass.
The original suite remains failed: generation stays 1→1 and the browser's Server
Action POST ends with `ERR_ABORTED`. This is a separate target-host observation;
matching failure shapes across hosts do not establish a shared cause.

The [coordinated DATA review](../../tests/node-compat/frameworks/nextjs/wasmcloud-full-root-results-v1/actual-runtime-review.json)
(`c528ca22`) binds the [ownership/config/browser review](../../tests/node-compat/frameworks/nextjs/wasmcloud-full-root-results-v1/actual-owner-browser-review.json)
(`519e3dd7`). Root independently checks the clean terminal and six published
direct-child log hashes after the original owner's cleanup. Portable retention
and both current/Git-mode standalone checks pass.

| Original check | Result |
| --- | --- |
| HTTP cases and complete retained bodies | 24 pass |
| Five persistent-cache requests | 52 checks pass |
| Six supplemental cases | 80 checks pass |
| Incremental stream | Five chunks; shell in chunk0, ready in chunk2; complete |
| Functional browser interactions | Both pass |
| Legacy generation increase | Fail: 1→1 |
| Strict browser completion | Fail: POST7 body, finished and sizes abort |
| Original process owner | Raw1; clean; no timeout or forced cleanup |

The two browser tests complete their pre-close drains. The failed POST terminal
occurs during action-result assertion, before drain and context close in that
observer's clock. Its decoded body and encoded sizes are unavailable. Neither
NetLog event ordering nor positive UI output supplies HTTP/gzip EOF or a cause.

## Artifact and capability boundary

Actor `f22d805c` reuses component `d990ecc1`, engine `476b1c1d`, metadata
`22f1d456` and the genuine f805 standalone app: 2,186 files, 48,755,844 bytes.
Next is 16.4.5; declared React/ReactDOM are 19.3.1. The captured browser runtime
uses the separately recorded Next-vendored canary. The existing Node22.14.0 client
and default browser worker are unchanged. Server JavaScript runs in embedded
SpiderMonkey/Wasm; this does not claim JavaScript AOT or complete Node/Buffer support.

The selected `next-http` world emits exactly 13 standard WASI0.2.10 interfaces:
`cli/environment`, `cli/stdout`, `cli/stderr`, `clocks/monotonic-clock`,
`clocks/wall-clock`, `filesystem/types`, `filesystem/preopens`, `io/error`,
`io/poll`, `io/streams`, `http/types`, `http/outgoing-handler`, `random/random`
(each in namespace `wasi`). Only `wasi:http/incoming-handler@0.2.10` is exported.
This uses the existing component and stock host without new services or imports.
The pinned wash Source commit `bc5acfb8` depends on Wasmtime48.0.7; the selected
release executable retains its previously authenticated `365d896e` digest.

Preparation derives all 825 source/target pairs and actual 31/39/18 metadata,
build and Source roles. The original full-native and whole-world guards pass
before and after execution. Independent DATA review hashes current metadata,
finite protected Source, the original app, independent app copy and cache;
five large tool/binary payloads are explicitly delegated to accepted build/INIT
records and actual guards, with current physical bookends.

The sole selected origin is `http://127.0.0.1:61785`. Effective configuration
contains exactly `allowedHosts:["http://127.0.0.1:61785/"]`, three guest environment
values, the app/cache mounts, and empty name-lookup/additional-loopback lists.
The actor leases that exact port once through config inspection, then releases
it before one dev launch. Root's earlier selection socket is separate; continuous
reservation through the handoff is not claimed. Config-show, dev and full client
exit0,0,1 respectively under the unchanged 600-second owner.

App files/directories are physically0444/0555; the private cache root is0700.
This host sample observes cache files0600 and child directories0700. The handler
does not explicitly request those child modes. Physical modes do not establish
read-only WASI descriptor rights; stock dev's app descriptor is read/write.
The direct cache preopen works here without adding `.next/cache` to the app copy.

Wash logs use direct file descriptors. Their six final hashes authenticate
stable current bytes after recorded process cleanup. The 8MiB readiness stat
check is not a lifetime sink bound, pipe-EOF or capture-complete schema.
The source policy creates fresh P2 request instances; this run observes no
private Store IDs, request affinity or arbitrary module-global continuity.

## Next work

The [portable corpus](../../tests/node-compat/frameworks/nextjs/wasmcloud-full-root-results-v1/retained-raw-data-v1/README.md)
retains 148 payloads/3,666,674 bytes, including the complete client/owner namespaces,
both reviews, configuration, 24 HTTP bodies, two screenshots and six final logs.
Run `python3 -I -B check.py` inside that directory. The
[actual offline check](../../tests/node-compat/frameworks/nextjs/wasmcloud-full-root-results-v1/retained-data-check.json)
and separate Git-mode check pass while preserving failed overall acceptance.
They open no original paths and revalidate neither omitted binary/app/cache
payloads nor the full 52/80-case semantics.

The reviewed [Source-only correlation proposal](../../tests/node-compat/frameworks/nextjs/nextjs-public-request-correlation-plan-v1/plan.json)
investigates whether a versioned public HTTP field can associate the actual
browser POST with guest completion records without guessing from counters.
It uses a bounded public per-test value, actual sent-header observations and
independent adapter/classic cardinalities; spoofing, duplicates, forwarding and
missing records can leave the association ambiguous. It is not an implemented
fix, new runtime authority,
clock alignment or private identity mechanism. Keep every original assertion.
Persistent-cache overlap/error/storage bounds, broader lifecycle coverage and
performance measurements remain open. Foundations-v13 remains accepted.
