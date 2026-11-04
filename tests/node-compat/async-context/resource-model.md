# Isolated mutable-resource prototype

This is a verified store-propagation experiment, not a shipping `node:async_hooks` implementation. It uses the same exact SM147 release static library and immutable R2 guest sources as the earlier probes, plus [resource-model-v3.cpp](resource-model-v3.cpp) through the existing diagnostic builtin mechanism. Production CMake, runtime and host binaries were not changed.

## Executed evidence

[resource-model-results.json](resource-model-results.json) records native engine SHA `4a71854ad033bfc60e507c299fba7d74d282ca84b368ff237260d97957ccdfc0`, component SHA `57d5fd936d4220cb58520be136f10161305c1ed8a10b73c837e2066b0ab507af`, and **zero imports**. The emitted world exports only `run: func() -> string`. Three calls to one Jco instance and a fresh unmodified Wasmtime 42 instance each pass:

- 19 cases / 63 store observations factored from the exact-release Node oracle.
- 9 cases / 44 species, child-capture and resource-mutation observations, excluding lifecycle/async-ID assertions.
- 23 additional checks for native Promise reactions, moving GC, `exit`, bound receiver/arguments/return, exception identity/restoration and two explicit fresh entries.

The [paired Node runner](resource-model-node-oracle.mjs) executes the same dependency-free case functions on Node v22.14.0 using actual Node timers and filesystem reads. The guest substitutes actual pure guest `api::AsyncTask` dispatch and synthetic bytes for these completions; repeated dispatch runs through an explicitly reused resource cell. This comparison validates the stores and capture boundaries, **not Starling's real timer/filesystem adapters or I/O ownership**. Both the Node and guest receipts name that scope. Filesystem completion order is unordered across independent Node runs; comparison normalizes only those two independent rows and nonportable execution IDs/resource-kind observations. Explicit FIFO assertions inside the shared cases remain intact.

The original edge oracle's custom species rejection callback could swallow a handler assertion. Its original source/results are preserved as `node-promise-edge-oracle-v1.*` / `node-promise-edge-oracle-v1-results.json`. The current [edge oracle](node-promise-edge-oracle.mjs) uses a rejecting completion gate, passes all 9/44 observations, and includes an assertion-propagation negative control. Its receipt records predecessor hashes.

## Model and tracing

Every execution resource is a private JS object with a reserved slot referring to its own linked store list. A store node holds the branded ALS-state object, store value and next node. Those reserved slots are traced automatically by SpiderMonkey. Stores remain ordinary JS values: copying bindings preserves their object identity rather than cloning the application value.

Creating a child copies only bindings whose state is enabled. Mutable list nodes are never shared between resources. Reusing a resource changes its own nodes, so later calls on that resource see `enterWith`, while a previously created child keeps its captured value. This copy-on-resource-creation representation is simpler than the proposed immutable-map/version representation; its allocation and traversal cost has not been accepted for production.

`AsyncLocalStorage.run` records and restores only its own binding. Updating/restoring an existing binding allocates nothing. The other ALS instance's `enterWith` remains on the current resource. `disable` changes lookup/propagation eligibility without deleting old resource bindings; re-enable can reveal an old pending store. A child created while disabled excludes that store permanently, even if the instance is later enabled.

The Promise metadata builder creates a distinct cell at actual Promise creation. Pending await/native reactions use the actual registration-time `getHostDefinedData` capture. Queue execution selects the result Promise's metadata cell where applicable, registration data for await/native paths, and the shared root cell for a validated non-Promise species capability. Nested thenable jobs on the same target Promise therefore share mutations; normal awaiters retain their own captures. This still depends on the pinned private reaction-record discrimination described in [architecture.md](architecture.md).

The queue's `PersistentRooted<Storage>` traces each queued job and cell. A popped job/cell is rooted before its queue entry is cleared. Current/restored cells use persistent/rooted handles, and RAII restores the caller on JS errors. Tasks trace their callback and cell and clear both on cancellation/run. No cell substitutes for a global or determines execution realm. The realm and wrapped-Promise limits of v1/v2 remain; no cross-compartment completeness is claimed.

## Lifetime and failure policy

The model facade keeps ALS and explicit-resource capsules in captured-intrinsic WeakMaps. A live Promise metadata association, queued job, task, bound callback or user `AsyncResource` retains its cell and application stores; otherwise ordinary GC can collect the cells. Disabled bindings remain on live resources, as required to reveal the old value on re-enable. The current root cell can consequently retain old bindings for its lifetime; pruning/weak-state behavior and memory limits need a deliberate production policy.

Ordinary state/resource creation, child capture and first binding insertion propagate native allocation failure. Existing binding restoration performs no allocation, and a failed first insertion commits no map mutation. **The allocation metadata API is different:** its documented callback/table policy is fatal on error. The prototype explicitly calls `AutoEnterOOMUnsafeRegion::crash` if creation capture fails. Metadata association is exercised; this fatal branch has not been fault-injected. A production profile must decide whether this general heap-OOM policy is acceptable or replace the instrumentation with a reviewed fallible guest SpiderMonkey hook. The previously verified four Buffer allocator failure paths are separate evidence.

`emitDestroy` currently returns its resource without delivering hooks or releasing a store. Async IDs, trigger relationships, destroy notifications, exact `executionAsyncResource()` Promise identity, AsyncResource option validation and full bound-function descriptors are not implemented. The API shape exists only to exercise store semantics. This is not an explicit export manifest or a module compatibility claim.

Two targeted calls enter fresh cells cloned from an initialization-only empty template. An intentional reused user resource still sees its earlier store. This establishes the distinction between fresh entry and deliberate reuse, not a complete request lifecycle. Request IDs, expired host handles, cancellation cleanup, cross-request pending jobs and the entry-root choice for plain species remain separate policy/integration work; no generic request global is synthesized.

## Production decisions and measurements still needed

The native engine is 9,480,794 bytes and this large correctness component is 11,260,092 bytes. Those are recorded artifact sizes, not a controlled incremental-size or throughput comparison. On its first run the diagnostic counts 161 Promise metadata captures, 3,580 metadata callbacks across all object kinds and 173 executed jobs. These counters expose the instrumentation surface; they do not measure elapsed cost.

Before selecting this design, measure identical workloads with the original native JS microtask queue, a legacy queue without creation instrumentation, and the full model with 0/1/8/64 enabled stores. Include pending/settled/optimized awaits, ordinary/native reactions, thenable chains, real timers and selected I/O, repeated/cancelled resources, and long component reuse. Compare final component size, startup/snapshot/resumption, live and peak memory, retained stores after disable/cancel, and host-timed batched throughput. Do not infer the legacy queue is faster merely because it is native.

Install production hooks before any application registration. Resolve metadata-builder coexistence and same-realm requirements, unknown-job handling, cross-compartment Promise unwrapping, debugger saved queues, finalizer callbacks and any off-thread dispatch. Put capture/tracing/entry/exit in actual task creation and dispatch paths, preserving one cell for a repeat timer. Keep normal Promise-await registration separate from completion-resource context. Actual WASI I/O tests must use explicitly selected standard interfaces and audit the final imports.

No SpiderMonkey fork is needed for the bounded experiments. The public/friend APIs plus private reaction data suffice for the tested stores. Complete lifecycle IDs and a recoverable/noninstrumentation Promise-creation hook remain unproven from existing APIs; the architecture audit describes the actual pinned guest build route if a small engine patch is justified.

## Reproduction

Use distinct external roots so the earlier controls remain immutable:

```sh
NODE_COMPAT_NODE=/path/to/node-v22.14.0 \
NODE_COMPAT_ASYNC_PROBE_ROOT=/tmp/async-context-resource-v3 \
NODE_COMPAT_ASYNC_PROBE_CPP="$PWD/tests/node-compat/async-context/resource-model-v3.cpp" \
  tests/node-compat/async-context/build-probe.sh

NODE_COMPAT_TOOLCHAIN=/path/to/pinned-toolchain \
NODE_COMPAT_COMPONENTIZE_MODULE=/path/to/audited-v2-package/src/componentize.js \
NODE_COMPAT_ENGINE=/path/to/resource-v3.engine.wasm \
  /path/to/node-v22.14.0 tests/node-compat/async-context/run-resource-model.mjs
```

The build requires the preserved R2 freeze and pinned external SDK/library cache. Its receipt verifies every copied source input; the runner rechecks the complete native manifest, selected componentizer, source files, world and resulting component before execution.
