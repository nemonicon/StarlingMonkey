# Portable Next cache proposal

Status: **engineering proposal with a model-tested Source prototype; no deployed cache handler accepted**. The original
cache-generation gate remains failed. The deployed affinity diagnostic observed
four different JS-global state epochs for its three cache reads and invalidation
admission. It did not trace the callback or tag-map updates and cannot establish
the sole cause. An arbitrary lexical counter cannot be made process-global by
sharing cache files. Stock P2 host reuse settings provide no affinity promise.

The optional handler now has a separately sealed Source prototype and forty
passing in-memory model checks. Cache filesystem, entropy and Next calls in
that model are explicit fakes; it has not loaded in a real Next application or
Wasm component. Its declared new-route tag set needs a successor before the
existing legacy cache routes can remain operational alongside the new scenario.

Use Next16.4.5's actual `cacheHandler` extension for a separately configured
application scenario. Do not patch Next internals, global Maps, app modules or
host scheduling. `next-server.js:getIncrementalCache` returns a new incremental
cache for its request headers; that constructor creates the selected handler
with the real `get`, `set`, `revalidateTag` and `resetRequestCache` contract.
Actual invocation/lifetime still requires tests. The distinct
`cacheHandlers`/`"use cache"` protocol is outside this
initial proposal. Exact source descriptors and line ranges are recorded in
[source-evidence.json](../../tests/node-compat/frameworks/nextjs/next-portable-cache-proposal-v1/source-evidence.json).

The first reference implementation should be a small audited guest CommonJS
module exporting a real handler class, with a versioned export/behavior manifest.
Its orchestration can use existing native SHA256 and bounded native filesystem
operations. It needs only the already selected filesystem/entropy interfaces;
no custom host service or new interface import. Installation must be explicit
and optional. No new native cache engine is justified before measurement.

| Surface | Proposed first boundary |
| --- | --- |
| FETCH entries used by `unstable_cache` | Bounded JSON records and explicitly configured tag namespace; fresh shared tag-epoch reads on every lookup, including possible memory hits |
| `revalidateTag` | Immediate expiration for declared tags and `expire:0`; other profiles and undeclared invalidation operations throw identifiable errors |
| APP_PAGE / APP_ROUTE and static prerender reads | Evaluate delegation to pinned Next FileSystemCache; do not imply shared cross-instance route-tag coherence |
| Images, `"use cache"`, distributed compute-once, arbitrary globals | Separate deferred contracts; no support inferred from handler installation |
| Storage and lifetime | One explicitly mounted shared cache directory, bounded files/records, runtime-only entropy, closed descriptors per operation; no INIT files, nonce or live handle |

Candidate persistence algorithm: publish each tag's random epoch token and each
entry through a fresh exclusive temporary file plus rename within the same
directory. Cache records carry the tag tokens observed before their computation.
Every lookup compares the record with fresh token files. A computation spanning
invalidation therefore cannot publish a record matching the new epoch merely by
sampling tokens at write time. Missing files have an explicit initial epoch;
corrupt or inaccessible tag state must not silently become that initial epoch.

The pinned `unstable_cache` passes `fetchIdx` to both handler get/set. Investigate
using key plus this request-local index to associate the pre-computation tokens;
test actual handler lifetime and ambiguous/repeated indices before relying on it.
Skip a cache write if that association cannot be established. Do not invent a
Next API or promise globally serialized computation. Concurrent writers,
invalidation races, partial multi-tag failures, crash recovery, temp-file cleanup,
storage bounds and selected-host rename behavior require explicit tests.
The current native fs facade rejects durable `flush:true`; crash durability is
therefore not part of the initial boundary.

Use the ordinary build configuration and tracing mechanisms. Next's build
normalizes `cacheHandler` relative to distDir in required-server-files and traces
the configured handler into standalone output; its runtime resolves that path
against distDir. Verify the actual emitted path and traced files after a fresh
build. Do not rewrite a protected existing application or assume a host absolute
build path remains usable at `/app`.

Guest loading is a prerequisite, not proven by tracing. The pinned Next loader
uses actual `import(fileURL)` for the handler. The current native CommonJS
compiler and core `module_load_hook` need a separate bounded audit/test for
that path. The generic hook assumes an object script-private referrer and then
loads a normal ESM file; that is not demonstrated CommonJS-file interoperation.
Do not execute a suspected invalid-referrer path as a fault experiment. First
provide a checked, identifiable failure boundary, then implement/test the
selected real CJS/default-binding contract through existing registration and
module-cache mechanisms. Do not invent an embedding API or patch Next's loader.

The checked-referrer boundary has since passed its two-case deployed test:
builtin import works and file-URL import throws the identifiable TypeError.
Pinned Node imports that target successfully, so this remains a compatibility
gap. The first interoperability build failed a SpiderMonkey HandleString
signature check. A separate rooted-string correction passes a one-TU frontend
check and now compiles/links as core2251f11a, with full-build DATA review being
closed. No interoperability component or sixteen-case deployed result exists
yet. See [the corrected generation](../../tests/node-compat/frameworks/nextjs/next-module-fileurl-interop-native-root-results-v2/README.md).

Next's `IncrementalCache.set` catches handler exceptions and logs a warning.
Direct helper/error-observation tests must distinguish an identifiable thrown
error from an application request failure; installation does not guarantee the
latter. Both loading and error handling remain implementation gates.

The new fixture should use a process-independent cache value with a recorded
freshness token: first/repeat must match and post-invalidation must differ.
This would be a new versioned scenario, tested against pinned Node and real
components on selected hosts. It cannot replace or relabel the original lexical
generation1→2 gate. Add overlapping get/set/invalidation tests and stale-write
refusals before support claims. Re-run the existing HTTP, streams, browser,
snapshot/import and resource tests, then measure component size, memory and
throughput. Keep production foundations-v13 unchanged throughout this work.
