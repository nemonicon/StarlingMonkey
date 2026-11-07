# Cache affinity diagnostic

The first native request regression, full-build V9 and native extra-CDP-off
control all retain cache generation1→1 after a successful revalidation POST.
Matched Node advances1→2. These are observed failures of the original contract.
Pinned host/Next source identifies possible per-instance state boundaries; it
does not prove which instance handled these actual requests.

The frozen [entry Source](../../tests/node-compat/frameworks/nextjs/next-cache-affinity-diagnostic-entry-v1/README.md)
is an exact V5 descendant with one private pure helper declaration and one call
immediately after real Request construction, inside the existing owned try and
native fresh-request boundary. The six facades, app files, engine and selected
world remain unchanged. Its [constructor Source](../../tests/node-compat/frameworks/nextjs/next-cache-affinity-diagnostic-construction-v1/README.md)
keeps the three V6 executables byte-identical and changes only explicit plan
roles. Entry index8f1a5b5f and constructor indexe0ec4689 pass independent Source
review;74 helper checks use inert callbacks and do not sample real entropy.

On the first deployed admission, the helper calls existing WebCrypto
`getRandomValues` for16 bytes and installs a nonenumerable immutable own slot
on that JS global. The nonce is immutable and a safe-integer ordinal advances
for every admitted request. Exactly `GET /api/cache` and `POST /api/revalidate`
emit bounded JSON stdout lines with marker `NEXT_CACHE_AFFINITY_V1`, phase
`request-admission`, nonce, ordinal, method and pathname. There are no added
response fields or headers, timers, promises, clocks, file operations or handles.
Failures follow the existing owned request cleanup; no token or successful
diagnostic is fabricated after an error.

There is only a function declaration at INIT. Existing RuntimeOnly native
entropy policy and the same `wasi:random/random@0.2.10`/stdout imports apply.
The first actual constructor must retain INIT logs without diagnostic lines,
validate the component and audit the same thirteen standard imports. A later
deployed run is a separate action. Source review and absent log lines alone do
not inspect private snapshot memory or establish complete lifecycle safety.

| Observation in a future deployed run | Permitted interpretation |
| --- | --- |
| Same nonce, increasing ordinals at cache/revalidation admissions | Observed continuity of one JS-global state epoch, subject to probabilistic nonce uniqueness |
| Different nonces | Observed different JS-global state epochs; request routing/lifetime is a candidate boundary |
| Missing, duplicated, malformed or ambiguously correlated lines | Diagnostic inconclusive |
| Same nonce with cache1→1 | Further cache/revalidation investigation required |

Labels do not identify a private native Store, shared app/cache identity,
handler completion, native resource destruction or the cause of cache failure.
Added entropy/logging may perturb timing. A favorable diagnostic is not a fix,
retry acceptance or reliability result. Do not add affinity host services,
modify Wasmtime/wasmCloud, widen the world, reset state or use DEBUG/GC pressure.

If multiple JS-global epochs explain a deployment constraint, the future
portable design must use explicit application/cache semantics suitable for that
host. Next's real CacheHandler extension and guest filesystem persistence are
candidates. They are not implemented by this diagnostic and cannot make an
arbitrary module-local counter process-global. The original failed fixture gate
must remain visible when evaluating any separately versioned portable scenario.
