# Request state in the portable Next profile

The portable profile cannot promise that successive HTTP requests share one
JavaScript module instance. Keep every failed original generation-counter
sample visible. Use explicit request state or selected persistent storage
for application behavior that must cross requests. This is a compatibility
boundary, not a runtime fix or a claim that the counter's exact failure cause
has been proved.

## Verified source and observations

The unchanged [legacy route](../../tests/node-compat/frameworks/nextjs/portable-cache-app-fixture-v1/app/api/cache/route.js)
declares `let misses = 0` at module scope and returns `++misses` from its
`unstable_cache` callback. The [full regression](../../tests/node-compat/frameworks/nextjs/next-guest-promise-completion-runtime-candidate-v1/run-contracts.mjs)
requires the post-invalidation generation to exceed the earlier value. A new
module instance can recompute the callback and still return1. Consequently,
generation1→1 alone does not distinguish an old cache hit from recomputation in
a different module-state epoch.

The earlier [affinity diagnostic](nextjs-cache-affinity-diagnostic-plan.md)
observes four different JS-global state epochs at the selected admissions.
It does not identify private Stores or prove the complete invalidation path.
The new Promise diagnostic separately retains generation1→1 while its persistent
cache scenario passes52 checks and its strict browser tests pass in one sample.
Its runtime result is2ae87cb0; coordinated DATA review4d47759f verifies that
outcome while retaining failed overall acceptance.

The later [fixed ten-trial comparison](nextjs-completion-comparison-2026-11-08.md)
observes generation1→2 in both Node controls and native B/block1. Seven other
native samples remain1→1, including B/block2. That positive guest sample is
retained as a pass for its original gate; it does not establish request affinity,
make module-global continuity a portable guarantee or waive the seven failures.

The subsequent [full stock wasmCloud profile](nextjs-wasmcloud-full-contract-2026-11-08.md)
passes the persistent-cache52 checks and retains legacy1→1. Coordinated DATA
review `c528ca22` verifies that independent host result. Neither that success nor
the host's source policy identifies the private instance of an observed request
or supplies an exact failure cause.

| Execution context | Available continuity contract |
| --- | --- |
| Pinned Node control | The selected host runs the fixture in one Node process; that control advances1→2. This does not generalize to a multiprocess Node deployment. |
| Stock Wasmtime42.0.1 serve | Instance reuse and availability govern dispatch. Reuse128 is a ceiling, not global request affinity or observed physical identity. |
| Stock wasmCloud2.11.0 P2 HTTP | The selected source creates a new Store/instance for each request. P3 pool controls do not change this P2 contract. |
| Explicit shared cache directory | The bounded HandlerV2 uses the selected standard filesystem interfaces. Its observed persistence/invalidation subset is separate from arbitrary lexical JavaScript state. |

The [export/host source audit](nextjs-export-promise-completion-audit.md) and
[wasmCloud lifetime and capability audit](nextjs-wasmcloud-mount-egress-source-note.md)
pin the host source and dispatch boundaries. Neither proves the private instance
identity of a particular observed Wasmtime request.

## Engineering policy and outstanding work

Treat cross-request module-global continuity as an unavailable guarantee in the
portable profile. Do not synthesize it through a custom host service, change
Wasmtime/wasmCloud, or serialize unrelated application requests to imply one
Node process. Standard WASI filesystem persistence stores explicitly encoded
data; it cannot preserve arbitrary closures, object identity or live handles.

Keep three outcomes separate in future checks: the original full contract
(currently failed), the bounded persistent-cache subset, and strict browser
completion. Every new engine still runs all original checks. A positive subset
does not waive the legacy failure or establish complete Next/Node compatibility.

Before broadening the persistent-cache contract, test overlapping invalidation
and publication, stale-write refusal, storage bounds and error behavior on each
selected host. Before accepting browser stability, use a predeclared comparison
that separates the extra await from diagnostic logging; retain every outcome.
Do not repeat trials until one passes or infer a missing-await bug from this
single positive sample. The original async return already adopted the Promise.
