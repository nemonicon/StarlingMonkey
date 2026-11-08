# Explicit persisted callback state

Updated 2026-11-08. This is a separately versioned application contract. The
original module-local counter fixture and its failed Wasm result remain intact.
The new callback stores a bounded integer under the existing writable standard
cache preopen. It does not preserve JavaScript globals, closures or object identity.

| Check | Current evidence |
| --- | --- |
| Real Next `nodeFs.writeFileAtomic`, Node | Three cases/11 assertions pass; owner12192/120, raw0/clean |
| Same real helper in a component | Owner18925/180 raw0/clean; primary runtime review pending |
| Callback-state conformance, Node | Eight groups/nine calls pass; owner13933/120, raw0/clean |
| New app V1 packaging | Build passes; artifact rejected for traced build cache |
| New app V2 packaging | Clean inventory verified; no cache directory or callback seed |
| New app full Wasm/Node pair | Fixed preparation complete; execution pending |

The real-helper probe checks new-destination publication, EEXIST without
replacement, temporary-file cleanup and an original ENOENT rejection. It loads
the actual pinned Next16.4.5 helper through the real module loader. The component
uses the existing237c engine, complete52-field metadata and the selected13
standard WASI0.2.10 interfaces; its construction audit observes131 import
functions rather than using that count as a target. No host is modified.

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
Any positive result will describe this ported fixture; earlier failures and
broader Node/Next compatibility limitations remain separate.

Evidence: [clean app review](../../tests/node-compat/frameworks/nextjs/next-fs-callback-root-results-v2/actual-build-review.json),
[Node helper review](../../tests/node-compat/frameworks/nextjs/next-node-fs-atomic-root-results-v1/actual-node-review.json),
[Node state review](../../tests/node-compat/frameworks/nextjs/next-fs-callback-root-results-v1/actual-state-node-review.json),
[component construction](../../tests/node-compat/frameworks/nextjs/next-node-fs-atomic-root-results-v2/actual-construction-review.json),
[preserved constructor failure](../../tests/node-compat/frameworks/nextjs/next-node-fs-atomic-root-results-v1/actual-construction-failure-review.json).
Cold-host persistence, concurrent lifecycle/resource checks, second-host full-app
behavior, clean-machine reproduction and empirical costs remain outstanding.
