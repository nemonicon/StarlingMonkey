# ALS hook decision addendum: pinned SpiderMonkey147

This is a read-only source addendum to the existing
[async-context audit](../../async-context/architecture.md),
[mutable-resource experiment](../../async-context/resource-model.md) and
[reset design](../reset-design-v1/README.md). It does not change or rerun them.
No Node oracle, compiler, guest, GC/reset experiment or host operation ran here.
The pin remains Firefox `9dab3d6f643e926a340c391ea30968e940390dec` and release
archive `c57dc83d93dc04198882b44fea49cd3cb01e0b267bf99fae3b058cb158da684b`.

The decision is narrower than saying ALS always requires a fork. **Existing
public JobQueue APIs support registration-context propagation; the previous
public/friend APIs plus pinned private record access supported bounded store
experiments without a SpiderMonkey patch. Full Node22 ALS is not established
by those experiments.** A production contract that requires an explicit,
fallible Promise-creation attachment and avoids private PromiseReactionRecord
layout needs an additional reviewed guest SpiderMonkey hook. That is an
engineering contract/recommendation, not a proof that every possible use of
existing instrumentation is impossible. Neither route requires a host change.

## Existing API and the capture boundary

`JS::JobQueue::getHostDefinedData` in installed `js/Promise.h:39–58` returns a
GC object; `enqueuePromiseJob` at lines70–86 receives the stored object and a
possibly null Promise. It is registration metadata, not merely queue-time
context. `Promise.cpp::NewReactionRecord` captures it at 5648–5653 and stores
it at 5688–5689. `InternalAwait` at 6092–6126 uses that reaction path before
suspension. A Promise resolved later outside the original context therefore
still has its registered continuation context. A `.then` wrapper misses
intrinsic await/native reactions, and enqueue-time capture picks the resolver
context for pending continuations. Those are invalid production substitutes.

`EnqueuePromiseReactionJob` at 1934–1958 retrieves the reaction's captured data
and passes it to the embedding. A fresh native resource has a separate context
cell captured at its own creation. A result Promise can require its creation
cell; thenable assimilation and ordinary await registration are distinct, as
the pinned Node oracle already demonstrates. The current native JS microtask
queue bypasses the legacy `enqueuePromiseJob` path (`EnqueueJob`, 1681–1704).
Any legacy-queue installation must select the actual supported preference
before application Promise creation/registration and preserve normal job,
debugger-save and kept-object/error behavior. It cannot hot-install based only
on an idle queue.

## Newly checked alternatives do not close creation semantics

The installed public Promise header has rejection tracking, Promise creation
functions, reaction registration, user-interaction flags and job-queue APIs;
the bounded scan found no general Promise init/before/after lifecycle callback
or public AsyncContext storage hook. Async stack capture concerns diagnostic
stack chains, not arbitrary mutable ALS resource cells.

Two tempting alternatives now have explicit source boundaries:

1. **Debugger new-Promise notification is not the requested creation hook.**
   `PromiseObject::create` creates the Promise through
   `CreatePromiseObjectInternal` at 3313–3319, invokes the user executor at
   3352–3364, and only afterward calls internal `DebugAPI::onNewPromise` at
   3379–3380. A callback there cannot simply capture the context from before
   an executor that changes it. This is an internal debugger entry, not a new
   public embedding lifecycle API. A proposed vector with executor-side
   `enterWith` is unexecuted; no new Node-observed result is asserted.
2. **Public user-interaction flags do not encode ALS context.**
   `Promise.h:551–595` exposes a three-state activation-behavior policy and
   propagation to child Promises. Its non-default flag can prevent some
   Promise elision, as the JobQueue documentation says. It neither supplies
   arbitrary context cells nor preserves a non-Promise species capability:
   `EnqueuePromiseReactionJob` at 1840–1865 explicitly replaces that capability
   with null. Null also represents optimized/native/await result resources.
   These flags are not an unambiguous public job-kind/capability accessor.

`js::SetAllocationMetadataBuilder` is exported in `jsfriendapi.h:645–669` and
can attach creation data. Its callback is general object-allocation
instrumentation, occupies one realm builder slot, and cannot return failure.
The header explicitly makes errors fatal; `Realm::setNewObjectMetadata` at
410–432 enforces same-realm data and crashes on metadata-table allocation or
insertion failure. The old resource prototype intentionally used that policy.
Using it in production requires an explicit coexistence, realm, failure and
cost decision; it is not a fallible Promise-only hook. Node's own fatal OOM
behavior does not by itself decide whether this embedding policy is suitable.

The previous private probe distinguishes plain-object species by inspecting
the retained native reaction holder and fixed slots. Source pinning and class
checks constrain that experiment; they do not turn private layout into a
public API. Cross-realm wrapping, unknown job kinds, optimized paths and
lifecycle/trigger identity remain additional gates.

## Dependency-ordered production proposal

First specify the finite ALS surface and mutable resource semantics against
the pinned Node release: per-instance `run` restoration, `enterWith`,
disable/re-enable, reusable bound resources, explicit empty context and
native resource versus Promise continuation ownership. Keep public
`async_hooks` IDs/lifecycle coverage separate from store propagation.

Then choose one explicit engine strategy. Either accept and validate the
general allocation-builder/private-layout costs and limitations, or add a
versioned guest hook that attaches a traced creation cell before executor
code, carries an explicit reaction/job kind and resource/capability context,
and exposes fallible registration. These are **proposed requirements, not
existing C++ symbols**. Preserve wrapping/realm rules and optimized-await
semantics; a moving pointer or mutable global slot is not an attachment.

Implement native task/timer/private-tick resource capture and dispatch restore
with rooted/traced ownership and exception-safe scope restoration. Intervals
and intentionally reused AsyncResources retain one mutable cell; children
capture the right state at creation. Promise continuation registration must
retain its own context when completion occurs under another resource.

Request owners/epochs and context cells stay distinct. Snapshot initialization
starts empty; unrelated deployment entries get fresh owners and root cells.
Captured module/application resources have their declared lifetime. Closing
and cancellation settlements need the reset protocol's traced cancellation
batch, reentrancy guard, exactly-once interests and late-completion policy.
Current reset remains unsupported; an idle private FIFO is insufficient.

Only after a reviewed hook/owner implementation should ordinary components
test pending/settled/interleaved awaits resolved outside context, thenables,
real/custom species, intrinsic native reactions, multiple stores, reused
resources, executor-side context mutation, realm transitions, snapshot/fresh
entry, cancellation and errors. Pair any generic fatal ABI result with finite
success controls and discard the failed instance. Measure final component
size, throughput and retained stores against the existing queue and instrumented
alternatives; no performance or memory advantage follows from this audit.
