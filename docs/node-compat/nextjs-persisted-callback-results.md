# Explicit persisted callback state

Updated 2026-11-08. This is a separately versioned application contract. The
original module-local counter fixture and its failed Wasm result remain intact.
The new callback stores a bounded integer under the existing writable standard
cache preopen. It does not preserve JavaScript globals, closures or object identity.

| Check | Current evidence |
| --- | --- |
| Real Next `nodeFs.writeFileAtomic`, Node | Three cases/11 assertions pass; owner12192/120, raw0/clean |
| Same real helper in a component | Three cases/11 assertions pass; owner18925/180, raw0/clean |
| Callback-state conformance, Node | Eight groups/nine calls pass; owner13933/120, raw0/clean |
| New app V1 packaging | Build passes; artifact rejected for traced build cache |
| New app V2 packaging | Clean inventory verified; no cache directory or callback seed |
| New app full Wasm/Node pair | Persisted generation1→2 passes both; Native strict browser fails, Node full suite passes |

The real-helper probe checks new-destination publication, EEXIST without
replacement, temporary-file cleanup and an original ENOENT rejection. It loads
the actual pinned Next16.4.5 helper through the real module loader. The component
uses the existing237c engine, complete52-field metadata and the selected13
standard WASI0.2.10 interfaces; its construction audit observes131 import
functions rather than using that count as a target. No host is modified.
The [runtime review](../../tests/node-compat/frameworks/nextjs/next-node-fs-atomic-root-results-v2/actual-runtime-review.json)
verifies HTTP200, all11 real assertions, complete capture and no temporary files.
The165-payload packet preserves Node and guest errors separately: type/code
match; native paths/messages and adapter operation/module fields differ.

The application helper performs no filesystem work at module evaluation. Its
callback checks a canonical, bounded record; genuine missing state starts at
zero, while pending, corrupt, aliased, unexpected or over-limit state fails.
It writes an exclusive pending file, verifies it, renames it, verifies committed
state and only then returns. Failures do not reset, retry, reclaim or roll back.
This is a sequential cooperative protocol. Concurrent increments, CAS, hostile
path replacement and fsync/crash durability are outside the contract.

Two counterexamples are retained. The first app build traced eight webpack cache
files/74,976,273 bytes into standalone. V2 changes only the route-specific tracing
exclusion for`/api/cache` and`./.next/cache/**`; its actual clean artifact has
2,196 files/48,801,297 bytes. No produced artifact was manually filtered, and
the runtime's empty-cache guard remains unchanged. Separately, the first helper
constructor stopped before Node because its copied working directory named the
old recipe. The new recipe fixes that field and checks it before authorization.
It constructs successfully; construction alone is not helper execution.

The unchanged full client still includes24HTTP,52 portable-cache,80 supplemental,
incremental streaming and both strict browser tests. Fresh assets come from the
actual V2 HTML. A fixed Wasm600→Node300 pair is prepared with2,030 protected
inputs, all six external client dependencies and genuine native/world guards.
The fixed pair now completes once per arm. Both pass the persisted1→2 counter,
24HTTP/52 cache/80 supplemental/five-chunk streaming and functional browser
checks. Native19501/600 exits1 cleanly because strict POST7 body/finished/sizes
capture fails with`net::ERR_ABORTED`; Node19876/300 exits0 cleanly with a strict
browser pass. The [primary pair review](../../tests/node-compat/frameworks/nextjs/next-fs-callback-root-results-v2/actual-runtime-review.json)
(`c6846dbb`) verifies all raw assertions, both clean owners and both physical
35-byte canonical generation2 records, separate from the cache-handler namespace.
The [528-payload packet](../../tests/node-compat/frameworks/nextjs/next-fs-callback-root-results-v2/runtime-records/index.json)
retains10,941,748 bytes, including current Sources, all six client dependencies,
browser/NetLog/body records and exact callback state. Native response status200
does not establish body completion: its POST7 body/sizes are unavailable and
finished fails before context closure. Node captures the full2,963-byte decoded
body and1,534-byte encoded body. These results
describe the ported fixture; earlier failures and broader Node/Next compatibility
limitations remain separate. No response-cancellation cause is established.

The [next response-completion probe](../../tests/node-compat/frameworks/nextjs/next-fs-callback-root-results-v2/next-browser-steps.md)
would reuse the retained391-byte request with captured-header restoration and
an ordinary Node HTTP consumer, checking gzip completion and transport EOF.
Preparation must refuse if the missing normalized headers cannot be restored
unambiguously. This would separate producer completion from React/UI consumption
for that workload; it would not explain or waive the original browser abort.

Evidence: [clean app review](../../tests/node-compat/frameworks/nextjs/next-fs-callback-root-results-v2/actual-build-review.json),
[Node helper review](../../tests/node-compat/frameworks/nextjs/next-node-fs-atomic-root-results-v1/actual-node-review.json),
[Node state review](../../tests/node-compat/frameworks/nextjs/next-fs-callback-root-results-v1/actual-state-node-review.json),
[component construction](../../tests/node-compat/frameworks/nextjs/next-node-fs-atomic-root-results-v2/actual-construction-review.json),
[preserved constructor failure](../../tests/node-compat/frameworks/nextjs/next-node-fs-atomic-root-results-v1/actual-construction-failure-review.json).
Cold-host persistence, concurrent lifecycle/resource checks, second-host full-app
behavior, clean-machine reproduction and empirical costs remain outstanding.
