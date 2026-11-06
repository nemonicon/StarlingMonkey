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

Rows1–3 are now combined in an experimental guest. Current priority is row0b,
the actual JavaScript language blocker, before expanding unrelated APIs. Keep
small audited profile facades in the entry where appropriate; native changes
still require a genuine coherent build and real-component validation.

| Priority | Work | Completion gate |
| --- | --- | --- |
| 0 | Preserve the full app and establish the bridge control | Complete: actual unmodified Next passes24/24 HTTP,2/2 browser interactions and incremental Suspense through the candidate bridge on Node. This is a host control. The bundler's `.node.js` classification defect is fixed;44 checks pass. |
| 0a | Check the deployment contract early | Real C-component probe passes selected standard WASI on both stock hosts. Wasmtime explicit reuse gives1,2,3; default and wasmCloud dev give1,1,1. Pinned primary Source confirms normal wasmCloud P2 HTTP also creates a fresh instance per request regardless of pool settings. Retained-state Next success is unavailable on that path under the present constraints; mount rights and nested cache operation still require guest checks. |
| 0b | Enable required Unicode regex behavior in the guest engine | Confirmed by actual12-case differential:21 property SyntaxErrors and3 Kelvin-sign ignore-case mismatches across three requests. SM147 lacks Intl; source guards explain the property failures. Next: coherent Intl/ICU-enabled SM147 artifacts and single Rust aggregate, full native relink, then the same differential and app. See [build plan](nextjs-intl-build-plan.md). Current fewGiB free is insufficient;20GiB budget/other volume requested. No host changes or dependency rewriting. |
| 1 | Real CommonJS loader, Buffer demand, formatting and startup APIs | Integrate Module/createRequire/cache/JSON/webpack chunk loading, the demanded native Buffer subset and util.format. Include real VM evaluation of Next client-reference manifests: replacing this with an import stub would break real routes. Add process, URL, OS, timers, performance and explicit HTTP/import surfaces. Verify ESM/CJS/default/global identities and coded failures. |
| 2 | Genuine application IO and computation | Standard read-only app/assets preopens and writable cache. Atomic link/EEXIST/unlink, stat/readdir and actual ReadStream/backpressure/close. RuntimeOnly secure RNG for UUID/cache names. Reuse native SHA256. Implement gzip/deflate streaming demanded by unchanged Next compression; one-shot zlib evidence does not establish streaming. |
| 3 | Correct async/request context and lifecycle | Actual SpiderMonkey Promise queue plus task/tick/timer capture. Validate ALS run/exit/enterWith/bind/snapshot, throw paths, disable/re-enable, awaits and overlapping requests. Fresh native request resources with restoration; no JS global context stack. |
| 4 | Construct and instantiate a complete guest | V6 engine `c2bff940` links,10,255,826 bytes, six phases0/clean and2,631 protected inputs unchanged. Both JS entries construct/validate and emit exactly13 selected0.2.10 imports/incoming-handler. The corrected dependency component now passes all16 controls on three real GET/GET/POST requests,48 records, with clean shutdown and preserved inputs. Complete lifecycle/concurrency/GC/snapshot and broader API checks remain open. |
| 5 | Run the full app and make it repeatable | Missing `global` is fixed by a small audited profile prelude; second actual Next-in-Wasm run is blocked by Unicode property regex parsing.23 base HTTP500; later action/cache/stream/browser phases blocked. Complete0b then rerun the unchanged24 HTTP/action+2 browser/cache/stream contracts. Preserve failed baselines and host lifetime checks. wasmCloud retained P2 state remains unavailable. |
| 6 | Measure and stabilize the working profile | Final component size, startup, memory and throughput against existing JS implementations. Promote only tested exports; publish limits and keep optional capabilities out of unrelated apps. |

The original full success contract remains intact. Stock wasmCloud2.11's P2
HTTP lifetime cannot satisfy its retained-server/cache portion: pool settings
apply to the separate P3 HTTP path. P3 is outside this selected WASI0.2.x profile.
Report wasmCloud cold-request/instantiation results separately; do not count
them as a full-contract pass or modify the host to force reuse. See the
[pinned Source analysis](../../tests/node-compat/host-capabilities/wasmcloud-warm-candidate-v1/README.md).

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

The earlier Next host controls do not prove guest filesystem configuration. The
new [real deployment probe](../../tests/node-compat/host-capabilities/probe-v1/README.md)
selects `/app` and `/cache` on both hosts, with owned Unix modes for app write
denial. Next's actual nested cache layout and narrower per-preopen rights remain
open. A guest-owned application image is an unimplemented packaging alternative;
it would not establish a retained logical server/cache lifetime.

## Current implementation state

| Dependency | Verified now | Still outstanding |
| --- | --- | --- |
| Resolved-target bundling |44 host checks; genuine Next `.node.js` files resolve as JS and actual binaries are refused | Closed dynamic application graph and guest loader execution |
| HTTP bridge | Full Next on Node:24HTTP+2browser, five chunks, cache1→2;21 focused bridge checks | Native streams, real WASI execution and registered HTTP surfaces demanded by Next |
| WASI HTTP adapter |13 host ownership/translation checks: EOF, cancellation, write splitting, IO failures and resource transfer | Uncompiled WIT/guest control; real standard host and native exception/resource behavior |
| CommonJS Module |42 focused host cases plus full Next24HTTP+2browser:406 JS files/412 cached modules. V2 fixes generator inventory and passes Source review; actual kernel SDK syntax passes | Registrar/loader implementation frontend, joined native build, guest reads and full app loading |
| Primitive util.format |728 Node/canonical/generated comparisons for the specified subset | Fresh guest generation and unchanged shared Next compatibility route |
| Buffer | Next-demanded byte/encoding/copy/write subset:134 host checks; original concat SDK check passes. Full Next host control passes24HTTP+2browser using the candidate global Buffer | Other host modules still produce Node Buffers, so that control does not exhaustively validate guest Buffer demand. Compile/link and actual component tests remain required |
| Filesystem | V3 public sync/callback/promises/ReadStream facade and direct-P2 provider;41 host checks. Three actual SDK frontends pass | Native resource/copy/close semantics and nested mount/realpath/recursive mkdir behavior in a real guest; full Next assets/cache writes |
| AsyncLocalStorage | V3 real SpiderMonkey store/Promise queue/task/tick/fresh/neutral boundaries;53 synchronous models and72 ownership cases. All13 SDK frontends pass after retained V2 failures | Native await/reaction/task ordering, disable/re-enable and concurrent-request propagation; link and component lifecycle tests |
| Startup and timers | Explicit process83/os24/url13 and timers12/promises5 inventories;195 startup and46 timer host cases. Native Performance epoch/precision correction prepared | Combined native frontend/link and deployed environment/clocks/FIFO/Immediate behavior; snapshot/resumption tests |
| HTTP and required import surfaces | Real bridge factory plus HTTP/HTTPS module registration and native context binding pass SDK syntax;62 HTTP host checks. Four finite imported surfaces pass422 binding/failure checks. Matched selected/stock controls both pass24HTTP+2browser with strict streaming | Linking and actual standard-WASI request ownership, cancellation, native context and full application startup; earlier browser abort remains retained/unexplained |
| Readable.toWeb | Actual stronger host control exposed five failed routes. Bounded m0.23 adapter passes30 cases/14 Node differentials; fresh full host contract passes with unchanged gates | Genuine native WebStream scheduling, async-destroy completion and resource cleanup in components; other Web adapters remain deferred |
| VM manifest evaluation | Real SpiderMonkey realm/evaluation plus bounded own-data sandbox copy under preparation; actual Next manifest source fixtures retained | Native compiler/link and actual Next client/action route execution. No complete Contextify or security-sandbox claim |
| Crypto/compression | Experimental SHA256 Hash/Hmac and one-shot zlib guest results exist. RuntimeOnly RNG candidate has46 host checks; native streaming Gzip/Deflate candidate has28 | Joined native compilation, INIT barrier, actual RNG calls and persistent compression-state cleanup in components |

The startup Source now replaces Module's libc private reads with the same direct
standard-P2 provider used by process/FS, including shared logical cwd. This join
is still awaiting guest execution. It uses the actual deployed-entry accessor
without introducing a host service. Original Source drafts and failures remain
retained; the combined Source generation must preserve the corrected V3 ALS
header while adding Timer's virtual methods.

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
