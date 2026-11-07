# Bounded native Fetch resource cleanup

Status: reviewed C++ afterimages; two frontend checks pass and the third fails
on three ignored `[[nodiscard]]` results under `-Werror`. The separate
[minimal correction](../../tests/node-compat/frameworks/nextjs/next-native-fetch-resource-cleanup-candidate-v2/README.md)
is sealed and now passes all three fresh frontend checks, with clean ownership
and unchanged guards; independent frontend DATA review passes. It adds only three
explicit `(void)` casts. A fresh full native build now exits0 and produces a
31,347,353-byte candidate engine; coordinated build DATA review passes.
The fresh interoperability component passes all16 deployed module cases in
one GET (runtime review55a255e7). The separate public Fetch component passes
INIT review4b3b0f43 with the full actual import audit; its first actual Node/Wasm
comparison now passes all eight public groups, raw0/clean/protected, with
coordinated DATA review705270ee. These components emit the same thirteen selected
standard WASI0.2.10 interfaces and only the incoming HTTP handler export.
The accepted production checkpoint remains foundations-v13. The experimental
Next.js profile still fails its legacy cache counter and strict Server Action
response-capture gates. This change has no demonstrated causal relationship
to either failure.

The new real-Next componentd990ecc1 now completes the unchanged full suite:
five persistent-cache requests/52 checks,24 HTTP checks,80 supplemental checks,
five stream chunks and both functional browser interactions pass. Legacy
generation stays1→1, and strict Server Action capture retains three
`ERR_ABORTED` errors. Result2fb8d5fd/client55d29476 are overall failed, with
clean ownership and preserved inputs; DATA reviewc3a8b95b independently verifies
the failed trial. A separate pre-HTTP harness prefix
failure and its bounded configuration correction are also retained. Further
native ownership expansion is deferred behind investigation of these two
remaining application gaps.

Recorded artifact sizes increase from31,341,287 to31,347,353 bytes for the engine
(+6,066), and37,235,395 to37,241,086 for the unchanged-entry Next component
(+5,691). These are actual artifact comparisons, not a startup, memory or
throughput benchmark; those measurements remain outstanding.

The existing deployed profile can render the comprehensive Next.js fixture,
serve its HTTP contracts, stream HTML and perform both browser interactions.
Its persistent-cache scenario passes. The corrected pinned Node control passes
the full suite in one sample. Results, raw failures and reusable readers are
retained in the [cache results](nextjs-portable-cache-2026-11-07.md).

The next native change addresses concrete ownership gaps in the actual compiled
Fetch implementation. It uses the existing task queue, rooting, host wrappers,
CMake and Rust build mechanisms. It adds no host service or interface.

| Path and symbol | Proposed behavior | Explicit limit |
| --- | --- | --- |
| `request-response.cpp`: `BodyFutureTask` | Retire each read subscription; retain the body across ordinary chunks; finish or drop the body at terminal states. | Pure ordering models do not prove C++ execution or resource counts. |
| `host_api.cpp`: `HttpIncomingBody::{subscribe,unsubscribe,retire}` | Track the owned pollable and invalidate handles before releasing children and body. EOF consumes `incoming-body.finish` and drops its trailers future. | Dropping an uninspected trailers future does not attest successful HTTP delivery. |
| `request-response.cpp`: `body_source_cancel_algorithm` | Retire a queued read through `Engine::cancel_async_task`; a running read observes cancellation at its safe boundary. | Post-header abort and tee cancellation propagation remain separate work. |
| `fetch-api.cpp` and `ResponseFutureTask` | Move the pending future into a unique owner and release its subscription before the future. | Upload abort/error before normal transfer remains deferred. |
| `HttpOutgoingBody::append` and native pull admission | Mark native append as excluded before it acquires subscriptions; avoid overlapping read admission. | The existing append lifecycle and cancellation behavior are not repaired here. |

Review caught a real conflict in the first unsealed draft: direct source
cancellation could drop a body while the separate native append task still
held subscriptions. The corrected draft explicitly excludes that path at
admission, cancellation and terminal cleanup. This is a source-review finding,
not an observed guest crash. Ninety-eight pure state checks cover the intended
ordering, including the exclusion. Existing response and header metadata
wrappers remain available; generic wrapper/finalizer ownership is deferred.

The wrapper directory name is significant. `wasi-0.2.0/host_api.cpp` includes
its local generated `bindings.h`, while the selected generated binding
translation unit is from `wasi-0.2.10`. The six new owned-drop/finish declarations
were compared in both exact headers and are identical. That is a narrow API
signature check, not a general ABI-equivalence claim. Existing generated
bindings and selected standard WASI 0.2.10 interfaces remain unchanged.

The [candidate](../../tests/node-compat/frameworks/nextjs/next-native-fetch-resource-cleanup-candidate-v1/README.md)
retains six exact before/after pairs, the deterministic patch, API witnesses,
ownership models and public-test plan. All build and guest result fields in
that source snapshot are null. Subsequent execution evidence belongs in a
separate result directory. The first compiler driver attempt stopped before
launch because it omitted the monitor's required output directory. Its separate
driver correction then ran all three checks with clean process ownership and
unchanged source/tool guards, producing exits 0, 0 and 1. The ten installed
generator checks pass. These results do not accept the cleanup implementation.

The dependency order is now:

1. Seal the reviewed source; compose a fresh 825-file source set, retaining the
   corrected CJS loader and all other selected payloads.
2. Check the three changed translation units using the actual compiler flags,
   then run the existing full native build with fresh outputs.
3. Construct fresh components, validate their actual imports and exports and
   rerun the bounded CJS interop probe on the new engine.
4. Run normal guest Fetch tests for EOF, metadata, body readers, cancellation
   and a surviving clone branch against the existing app routes. Keep public
   behavior evidence distinct from private resource-count claims.
5. Run the full Next.js regression without changing its failed gates. Use the
   results to choose further lifecycle or browser investigation, then repeat
   target-host checks and measure size, startup, memory and throughput.

Native append cleanup, late abort reification, both-branch clone cancellation,
owned error diagnostics, unpublished-response allocation failures, complete
wrapper ownership and clean-machine bootstrap remain outstanding. No forced
GC, fault injection, reset or resnapshot experiment is part of this step.
