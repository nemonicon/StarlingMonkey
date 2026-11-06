# Next.js execution priority

Updated 2026-11-06. The immediate target is the **complete existing Next 16.4.5
App Router application executing in a Wasm component**. The accepted general
profile remains foundations-v13. New loader, filesystem, async-context and
HTTP sources are experimental until built and exercised in that component.

Pins are Node 22.14.0 semantics, React/ReactDOM 19.3.1, ComponentizeJS 0.23.0,
Jco 1.40.0, Rolldown 1.2.16 and Wasmtime 42.0.1. The secondary target is
wasmCloud 2.11.0, source `bc5acfb8e15f7d6d199ca940354d82e590c2d5ff`, embedding
Wasmtime 48.0.7; retain the [existing host setup](../../tests/node-compat/wasmcloud/README-host.md).
The accepted StarlingMonkey generation derives from `54b3329b3ce818fd1f244e871e9c259b63667cda`
with recorded overlays: engine `d54446dc…`, sidecar `bfaec95e…`,342 native inputs.
Current repository HEAD is not the identity of a newly compiled engine.
Select standard WASI 0.2.10 interfaces explicitly. Neither a custom host service
nor host-engine modifications are part of this plan.

## Success contract

Keep the original [fixture contract](../../tests/node-compat/frameworks/nextjs/fixture-contract.json):
23 HTTP cases plus a build-derived actual Server Action POST; cache reuse and
invalidation; request headers/cookies; dynamic SSR; filesystem/SHA route;
public/static assets; hydration/counter click; browser form action; and
incremental Suspense delivery. Retain failures and compare future runs to the
same contracts. Compilation alone and a React-only render do not close this
milestone. Do not turn off Next features to obtain a smaller passing workload.

Use Next's real custom-server `prepare()`/`getRequestHandler()` path behind the
standard `wasi:http/incoming-handler` export. This keeps the real router,
rendering, actions and cache while letting the selected host own HTTP transport.
The untouched standalone tree and computed module/chunk loads remain the
application. `http.createServer().listen()` needs a separate TCP-server
implementation; this hosting path does not require it. HTTPS scheme metadata
does not provide raw TLS sockets; WASI P2 sockets themselves provide no TLS.

## Order of work

Work on rows1–3 in parallel, then combine reviewed implementations into one
fresh guest generation. Do not repeatedly rebuild a full engine for each small
facade edit. Use host differentials and SDK syntax checks to catch local faults
first; they cannot replace native and real-component gates.

| Priority | Work | Completion gate |
| --- | --- | --- |
| 0 | Preserve the full app and establish the bridge control | Complete: actual unmodified Next passes24/24 HTTP,2/2 browser interactions and incremental Suspense through the candidate bridge on Node. This is a host control. The bundler's `.node.js` classification defect is fixed;44 checks pass. |
| 0a | Check the deployment contract early | Before the combined engine build, run a small real standard-WASI component on each stock target to establish filesystem preopens/rights, clocks/random/environment selection and actual instance reuse. Earlier HTTP counters were all1; they do not establish a persistent Next server. Report target limitations before treating either deployment path as viable. |
| 1 | Real CommonJS loader, Buffer demand, formatting and startup APIs | Integrate Module/createRequire/cache/JSON/webpack chunk loading, bounded native Buffer.concat and demanded util.format. Add explicit process, URL, OS, timers and performance surfaces from actual Next call sites. Verify ESM/CJS/default/global identities and coded failures for unsupported operations. |
| 2 | Genuine application IO and computation | Standard read-only app/assets preopens and writable cache. Atomic link/EEXIST/unlink, stat/readdir and actual ReadStream/backpressure/close. RuntimeOnly secure RNG for UUID/cache names. Reuse native SHA256. Implement gzip/deflate streaming demanded by unchanged Next compression; one-shot zlib evidence does not establish streaming. |
| 3 | Correct async/request context and lifecycle | Actual SpiderMonkey Promise queue plus task/tick/timer capture. Validate ALS run/exit/enterWith/bind/snapshot, throw paths, disable/re-enable, awaits and overlapping requests. Fresh native request resources with restoration; no JS global context stack. |
| 4 | Construct and instantiate a complete guest | Fresh source/configuration/metadata and selected WIT through existing native registration/CMake. Audit emitted interfaces and callable imports; refuse custom services, unselected interfaces and Preview1 leakage. Real component controls for loader, FS, HTTP, Buffer, context and snapshot/resumption, then actual Next startup. |
| 5 | Run the full app and make it repeatable | Same24 HTTP contracts, two browser interactions, chunk ordering, cache generation and isolation on the Wasm server. Test retained-instance behavior explicitly. Instantiate on stock Wasmtime and pinned wasmCloud; document host reuse limits. Retain raw artifacts/failures as future regression checks. |
| 6 | Measure and stabilize the working profile | Final component size, startup, memory and throughput against existing JS implementations. Promote only tested exports; publish limits and keep optional capabilities out of unrelated apps. |

The first new linked generation should target actual application startup and
dependency controls, followed immediately by the complete contract. Rank new
blockers by startup, required route failures, context/resource correctness and
optional branches. Import-only compatibility is never successful execution.

The [startup/API inventory](../../tests/node-compat/frameworks/nextjs/startup-api-demand-v1/README.md)
now supplies56 exact citations from all406 loaded JS files and nine complete
pinned export-name inventories. It prioritizes mutable process/env/cwd, truthful
OS data, real nextTick/Immediate ordering, patchable timer modules, legacy URL
format/file helpers, HTTP Agents and streaming zlib cleanup. Conditional cache
serialization also requests Buffer base64 support. Static call sites and
conditional expressions are not runtime invocation observations; do not expand
support based solely on an imported or read name.

The existing host evidence selected no filesystem volumes, so it does not prove
the new FS configuration. A guest-owned read-only application image is a possible
portable packaging alternative, but is not implemented or selected here. It
does not resolve a target's inability to retain the logical server/cache lifetime.

## Current implementation state

| Dependency | Verified now | Still outstanding |
| --- | --- | --- |
| Resolved-target bundling |44 host checks; genuine Next `.node.js` files resolve as JS and actual binaries are refused | Closed dynamic application graph and guest loader execution |
| HTTP bridge | Full Next on Node:24HTTP+2browser, five chunks, cache1→2;21 focused bridge checks | Native streams, real WASI execution and registered HTTP surfaces demanded by Next |
| WASI HTTP adapter |13 host ownership/translation checks: EOF, cancellation, write splitting, IO failures and resource transfer | Uncompiled WIT/guest control; real standard host and native exception/resource behavior |
| CommonJS Module |42 focused host cases plus full Next24HTTP+2browser:406 JS files/412 cached modules. V2 fixes generator inventory and passes Source review; actual kernel SDK syntax passes | Registrar/loader implementation frontend, joined native build, guest reads and full app loading |
| Primitive util.format |728 Node/canonical/generated comparisons for the specified subset | Fresh guest generation and unchanged shared Next compatibility route |
| Buffer.concat | Native guest candidate ready;38 Node differential+12 profile/generated-factory cases and actual SDK syntax pass | Independent review, linking, component differentials and full Next callers |
| Filesystem | Native direct-P2 provider/stream handle draft; public facade unwritten | Fix two error paths, add public factory/real ReadStream/callbacks, wiring and genuine FS differentials before build |
| AsyncLocalStorage | Native store/queue/task/tick/fresh-request draft;41 reversible edits and53 synchronous models | Final cross-file audit, owner tests, metadata/producer integration, native build and actual async/request propagation |
| Process/URL/OS/performance/HTTP exports | Actual source demand identified; existing web code is a reuse candidate | Explicit exports, bounded semantics, lifecycle policy, implementation and tests |
| Crypto/compression | Experimental SHA256 Hash/Hmac returns and native one-shot zlib results exist | RuntimeOnly UUID, live-native-state INIT barrier and demanded streaming compression |

The Module provider currently uses guest libc for private reads; the FS candidate
uses direct standard P2 descriptors. Join their cwd, preopen, symlink, rights and
error behavior explicitly. The shared deployed accessor is a proposed private
guest API observing the existing entry bit; it adds no host capability.

## Lifecycle and capabilities

Load the application lazily after deployed entry. Snapshot initialization must
not capture deployed environment values, filesystem contents, entropy or live
request handles. Preserve application top-level failures when it is actually
loaded. Snapshot-safe registration and runtime app preparation are distinct.
Deployed-instance re-snapshot/reset behavior is not accepted.

Run deployed `next(...).prepare()` once under a neutral server resource before
entering any fresh request resource. Module singletons, cache infrastructure and
the shared readiness Promise must not inherit the first request's context.
Each request's continuation after readiness and all its subsequent app work must
run under its own genuine native owner. The current host control prepares Next
before admitting HTTP calls; the guest's lazy preparation needs an equally
explicit native boundary and concurrent-first-request tests.

The future Next world needs explicitly selected standard HTTP types/incoming
handler, filesystem types/preopens, clocks/poll/streams/error and secure random.
Select CLI environment/stdio only when implemented and intended; select outgoing
HTTP only for actual outbound paths. The current bridge-control WIT is a smaller
uncompiled dependency world, not the full app world or an emitted-import report.
Audit final component bytes. Host filesystem rights must enforce mount policy.

Cache/module state requires a declared logical server lifetime. A fresh instance
per request does not prove same-instance cache invalidation or ALS isolation.
Use actual retained-instance tests where supported and report each target host
separately. Do not modify Wasmtime or wasmCloud to force reuse.

Generic clock diagnostics, unrelated crypto algorithms, broader Node inventory,
new optimizations and general adoption/performance paperwork move behind these
dependencies. Existing evidence remains valid within its scope. The full roadmap
and full Next-in-Wasm gate are **not complete**.
