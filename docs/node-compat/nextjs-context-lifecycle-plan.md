# Next native context and lifecycle follow-up

Status: read-only source audit and proposed finite tests after checkpoint
`26122a28`. No component, engine, browser, native build, reset, GC/OOM pressure,
fault or DEBUG action was run for this plan. Existing sealed sources and the
successful native hydration first/repeat results remain unchanged. This document
does not identify a newly observed native failure.

Follow-up execution on2026-11-07: the first five controls below now pass459
actual native assertions (153 per call, three calls) and the original Node
public-expectation projections. Component938e6913 and the strict V2 collector
use the same13 standard WASI interfaces; all constructor/runtime parents finish
0/clean. The separate host run covers918 assertions and is not counted as native
proof. Unref across calls, tagged real HTTP, disconnect and native resource
counts remain open. The original source-audit and proposed deeper tests below
retain their scopes.

The [actual native V5 review](../../tests/node-compat/frameworks/nextjs/next-intl-runtime-root-results-v1/hydration-v5-review/README.md)
proves two executions of this fixed app's 24 HTTP contracts, cache invalidation,
incremental stream and two browser interactions. It does not prove same-instance
request concurrency, owner expiry, cancellation cleanup or native resource counts.

## Source boundaries and concrete remaining questions

The current entry creates the shared readiness Promise and runs preparation
inside `runNeutralServer`, then calls the adapter only after readiness succeeds
([entry:628–657](../../tests/node-compat/frameworks/nextjs/next-component-entry-fixes-v4/guest-entry.mjs#L628)).
`prepareServer` bootstraps, selects `/app`, loads the real Next app and awaits
app.prepare ([entry:692–716](../../tests/node-compat/frameworks/nextjs/next-component-entry-fixes-v4/guest-entry.mjs#L692)).
The adapter enters `runFreshRequest` before reading headers or constructing the
body/Request ([entry:603–612](../../tests/node-compat/frameworks/nextjs/next-component-entry-fixes-v4/guest-entry.mjs#L603)).
Native fresh entry creates an empty resource; neutral entry selects the stable
server resource, and both use `ResourceStore::invoke`
([runtime:149–175](../../tests/node-compat/foundation-vm/node-vm-candidate-v1/after/runtime/async_context_runtime.cpp#L149)).

1. **Overlapping HTTP is not same-Store concurrency proof.** The actual embedding
   rejects another export while `cur_fn_idx != -1`, drives the event loop until
   the returned Promise completes, then clears the call state in post_call
   ([embedding:196–204](../../tests/node-compat/milestones/foundations-v12/native-freeze/componentize-source/embedding/embedding.cpp#L196),
   [318–339](../../tests/node-compat/milestones/foundations-v12/native-freeze/componentize-source/embedding/embedding.cpp#L318),
   [378–391](../../tests/node-compat/milestones/foundations-v12/native-freeze/componentize-source/embedding/embedding.cpp#L378)).
   EventLoop independently refuses reentry
   ([250–256](../../tests/node-compat/foundation-timers/node-timers-candidate-v1/after/runtime/event_loop.cpp#L250)).
   Concurrent network requests may use separate host instances. Do not reenter
   an active component to manufacture a race. Use one ordinary export with two
   logical native fresh branches for shared-Store ALS interleaving, then a
   separate tagged real HTTP test for pool behavior.

2. **Preparation race coverage is currently a host model.** The retained test
   starts two callers behind a preparation gate and proves one attempt plus
   sticky readiness using host Node ALS and fake ownership objects
   ([test-models:1–36](../../tests/node-compat/frameworks/nextjs/next-component-candidate-v2/test-models.mjs#L1)).
   That is useful orchestration evidence, not native Promise-context or real WASI
   resource ownership proof. A native readiness control can exercise the exact
   `readiness ??= Promise.resolve().then(prepareServer)` block with real native
   neutral/fresh functions inside one export. It must be labeled a logical
   preparation control; passing fabricated incoming resources would not test
   the real HTTP adapter. No forced preparation rejection is needed now.

3. **Pending Promise registration/resolution across owners is the highest-value
   untested ALS path.** The job queue reads the exact SM147 reaction record,
   chooses target-Promise allocation metadata before host registration data,
   then invokes the job under a native Scope
   ([queue:83–125](../../tests/node-compat/foundation-vm/node-vm-candidate-v1/after/runtime/async_context_queue.cpp#L83),
   [178–187](../../tests/node-compat/foundation-vm/node-vm-candidate-v1/after/runtime/async_context_queue.cpp#L178)).
   This is not a demonstrated bug. It particularly needs neutral-created
   promises registered in A and resolved in B, settled and pending await,
   Promise.all and ordinary thenable assimilation. The actual dependency probe
   currently tests a serial await/tick/immediate/timer chain and snapshot/bind
   restoration ([dependency:258–268](../../tests/node-compat/frameworks/nextjs/next-component-candidate-v2/dependency-entry.mjs#L258)).
   The richer pending REGISTER/RESOLVE sequence remains future Source
   ([future-probe:16–20](../../tests/node-compat/async-context/native-als-candidate-v2/future-probe.mjs#L16)).

4. **Unref work has a real surviving-task policy, not automatic teardown.** The
   loop returns at zero interest before selecting queued tasks. With later
   interest, unref tasks may run under their original task context
   ([event-loop:303–351](../../tests/node-compat/foundation-timers/node-timers-candidate-v1/after/runtime/event_loop.cpp#L303)).
   post_call frees ABI allocations; it does not cancel/reset the task queue.
   Native resource capture retains the original owner and the Scope restores the
   prior owner ([store:108–165](../../tests/node-compat/async-context/native-als-candidate-v2/after/runtime/async_context_store.cpp#L108)).
   Owner resources have no expired bit in this implementation. For the current
   Node-compatible server profile, first test preserving A's context when its
   unref callback runs while B supplies interest. Automatically canceling all
   request-created tasks would be a separate policy change and could change
   ordinary Node/Next background-work behavior. It is not an assumed fix.

5. **Peer disconnect is not wired to Request.signal.** The adapter builds Request
   without a signal ([entry:540–564](../../tests/node-compat/frameworks/nextjs/next-component-entry-fixes-v4/guest-entry.mjs#L540));
   the classic bridge observes only that Request.signal
   ([bridge:78–109](../../tests/node-compat/foundation-http/next-http-candidate-v1/bridge.mjs#L78)).
   The selected WASI P2 incoming-request API exposes headers/body, not an
   independent peer-disconnect notification
   ([WIT:249–276](../../tests/node-compat/frameworks/nextjs/next-component-entry-fixes-v4/deps/wasi-http-0.2.10/package.wit#L249)).
   Current transport loss can be learned through input-read/output-write errors
   ([I/O WIT:22–41](../../tests/node-compat/frameworks/nextjs/next-component-entry-fixes-v4/deps/wasi-io-0.2.10/package.wit#L22)).
   Do not promise instant abort while an application is idle and performs no I/O.
   The adapter cancels its Web response reader on a write failure and drops
   children before parent bodies in finally
   ([entry:575–599](../../tests/node-compat/frameworks/nextjs/next-component-entry-fixes-v4/guest-entry.mjs#L575)).
   Host abort tests and fake-WASI ownership tests exist; equivalent real guest
   disconnect/cleanup observations are still needed. Adding an AbortController
   that is triggered by an observed I/O error would be a future Source change,
   not a new independent P2 disconnect capability.

## Finite next workload

Use the existing engine and real `starling:node-http` native boundaries in a
small separately reviewed component entry. Keep the current standard WASI world;
no native diagnostics, extra host service, app rewrite or custom capability is
needed for these observable controls. Compare shared public cases with pinned
Node22's default ALS backend, without the experimental async-context-frame flag.
Native private-boundary assertions are additional native-only observations.

| Control | Real operations and must-pass assertions |
| --- | --- |
| One-export A/B interleaving | Start two `runFreshRequest` branches before awaiting either; use two ALS instances and distinct nonsecret object markers. Force both branches to suspend through real nextTick, Promise, immediate and timer operations. Every continuation sees its own expected marker and the unrelated store; a fresh branch begins empty and the outer caller is restored after both return. |
| Cross-owner Promise | Create deferred promises neutrally; register reactions/await under A and B; resolve each from the opposite branch. Include settled await, pending await, Promise.all and one ordinary thenable. Compare marker identity, callback receiver/arguments and partial event order with real Node. No result may silently borrow the resolver's context. |
| Shared readiness | Start two logical callers with distinct ambient markers. Both use the exact readiness statement inside real runNeutralServer; prepare suspends once using a real immediate, attempts is exactly 1, neither caller reaches the prepared result early, and prepare never sees either request marker. Later reuse still reports one attempt. This is not real incoming-resource disposal coverage. |
| Disable/re-enable and capture | While A is pending, disable the shared ALS instance from B; compare the actual default-Node outcome, then re-enable from B and invoke A's retained snapshot/bind/AsyncResource callback. Preserve A versus B restoration and a second unaffected ALS instance. Do not assume disable is per-request: the native enabled flag is per ALS state. |
| Normal cancellation | Register timers/promises with a real AbortSignal, cancel from the other branch and immediately observe the original Promise rejection. Compare AbortError/code, callback count and caller/captured context with Node. Await or clear every referenced task before return. No timeout overflow, invalid handles or injected failures. |
| Unref across ordinary calls | In call A, arm a bounded unref timeout and return without waiting for it. In call B, create real referenced interest. Record whether the old callback runs, its original A marker and B restoration; cancel remaining work and inspect once more in the same identified instance. Separately test B clearing A's unref task. Declare the preserve/cancel policy before interpreting the result. |

Keep the first component finite: two logical branches, at most eight live timers
or immediates, bounded trace rows, no intervals, and explicit cancellation/drain
of normal work. Compare values and required ordering, not host timestamps or
arbitrary interleavings. Existing ticks capture before enqueue and restore Scope
before invocation ([tick:45–68](../../tests/node-compat/async-context/native-als-candidate-v1/after/runtime/node_tick_queue.cpp#L45),
[87–113](../../tests/node-compat/async-context/native-als-candidate-v1/after/runtime/node_tick_queue.cpp#L87)).
Task run/cancel use their registered cell, including cancellation from B
([cancel:176–187](../../tests/node-compat/foundation-timers/node-timers-candidate-v1/after/runtime/event_loop.cpp#L176)).

Then use real tagged HTTP requests: one cold pair, one warm sequential pair, and
one slow A/fast B pair. Use a persistent module tag derived from the first
host-supplied case label plus a per-instance call ordinal. These are diagnostic
labels, **not** AsyncResource IDs. Preserve each tag/ordinal/active-count response.
If the host selects different instances, report that fact and leave same-instance
overlap inconclusive; never interpret parallel client completion as shared-Store
concurrency. The current embedding's nonreentrancy must remain intact.

Finally perform one real partial-upload close and one peer close after receiving
the first streamed response chunk. Preserve complete client bytes/errors,
server stdout/stderr and owned outcomes. On the guest side, record only naturally
executed input-error, response-cancel/finally and later inspection observations.
Require the healthy control response to remain correct. If a failed Store is
discarded or the inspection has a different module tag, no after-return cleanup
claim follows. Do not replace real peer closure with a fake stream error.

Retain whole scalar/HTTP outputs, typed thrown values, per-case event arrays,
component/source/engine descriptors and all raw owned terminals before deciding
acceptance. No JS-visible counter can prove native pollable/registry counts,
post-Store-death drops or GC-root release. Those facts need separately reviewed
native observability and remain open here. No reset/resnapshot invocation or
deferred fault test belongs to this workload.

The cited native donor files match the V7 cohort selected by
[portable-native-inputs.json](../../tests/node-compat/frameworks/nextjs/spidermonkey-intl-build-v1/portable-native-inputs.json).
Actual embedding SHA is `9dcb63be...`/22,252 bytes. Native engine `4623640b` changes
only the Module compiler object relative to its documented baseline; the context,
timer, HTTP and embedding seams above are unchanged. Historical SOURCE-only
comments inside donor files are preserved text, not the current build status.
