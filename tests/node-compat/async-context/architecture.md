# Async context audit: SpiderMonkey 147 and Node 22.14.0

This is an architecture investigation and a separate guest-engine experiment. It does **not** install `node:async_hooks`, implement production AsyncLocalStorage, or change any production source or host. The Node oracle and real component results below are verified; the production resource model and optional engine hooks are engineering proposals.

The engine baseline is StarlingMonkey `54b3329b3ce818fd1f244e871e9c259b63667cda` plus the preserved allocation-r2 input manifest. SpiderMonkey's `FIREFOX_147_0_4_RELEASE_STARLING` tag dereferences to `9dab3d6f643e926a340c391ea30968e940390dec`. The probe links the same released static library archive SHA `c57dc83d93dc04198882b44fea49cd3cb01e0b267bf99fae3b058cb158da684b`. Packaging uses the separately audited ComponentizeJS 0.23 v2 splicer and Jco 1.40.0. Its component imports nothing.

## Actual supported hooks and capture timing

The installed 147 header has **no `JobQueue::getIncumbentGlobal`**. Its actual API is `JS::JobQueue::getHostDefinedData`, `getHostDefinedGlobal`, and `enqueuePromiseJob(..., hostDefinedData)`. The first hook returns a GC object from any compartment; the second concerns a real host-defined global. An ALS token belongs in host-defined **data**, not a substituted global or realm. [Pinned public header](https://github.com/bytecodealliance/firefox/blob/9dab3d6f643e926a340c391ea30968e940390dec/js/public/Promise.h)

The source establishes these separate paths:

| Path | Registration capture | Enqueue/execution consequence |
| --- | --- | --- |
| Pending ordinary `.then` | `NewReactionRecord` calls `GetObjectFromHostDefinedData` and stores the object in a fixed slot. | `EnqueuePromiseReactionJob` later retrieves/unpacks that object, regardless of which context resolves the promise. |
| Pending native `JS::AddPromiseReactions` | `OriginalPromiseThenWithoutSettleHandlers` uses the same allocation option and reaction record. | Its nullable result-promise argument cannot be treated as evidence of an empty context. |
| Pending `async`/`await` | `InternalAwait` creates its reaction with the same capture hook before suspension. | It does not call application `Promise.prototype.then`; wrapping `.then` cannot implement this path. |
| Already-settled reaction | `HostDefinedDataObjectOption::OptimizeOut` skips the stored object. | Enqueue happens synchronously during registration. A legacy queue can capture the current context then. |
| Truly skipped fulfilled/primitive await | `CanSkipAwait`/`ExtractAwaitValue` can continue within the last job. | There is no new job boundary. Keeping the current execution context during that continuation is required. |
| Thenable assimilation | The queue receives the promise being resolved; the generic host-data value can be optimized out. | Node's relevant resource context may be the resolved promise's **creation** context, not the resolver's context. |

See `Promise.cpp`: `NewReactionRecord`, `PerformPromiseThen`, `InternalAwait`, `EnqueuePromiseReactionJob`, `EnqueuePromiseResolveThenableJob`, and `CanSkipAwait`. `JSObject.cpp::GetObjectFromHostDefinedData` wraps an arbitrary returned data object into the current compartment; it does not require a global. [Promise implementation](https://github.com/bytecodealliance/firefox/blob/9dab3d6f643e926a340c391ea30968e940390dec/js/src/builtin/Promise.cpp), [object helper](https://github.com/bytecodealliance/firefox/blob/9dab3d6f643e926a340c391ea30968e940390dec/js/src/vm/JSObject.cpp)

**An empty context must still be a non-null captured token.** A pending callback registered outside ALS and resolved inside B must resume empty. Returning null for that registration confuses an explicitly captured empty context with SpiderMonkey's optimized-out sentinel; falling back to enqueue-time B would leak the wrong context.

Captured maps must be immutable snapshots, while an execution resource needs a mutable current-map cell. Returning the mutable cell itself from the capture hook would let later `enterWith` calls retroactively change an already registered child's context.

## Queue configuration matters

The shipped `js/PrefsGenerated.h` initializes `use_js_microtask_queue` to true. In that mode, `Promise.cpp::EnqueueJob` directly pushes native JS microtasks; it can bypass `enqueuePromiseJob`. `JS::MaybeGetHostDefinedDataFromJSMicroTask` provides stored data but does not add an enqueue-time context snapshot for the optimized-out case. Treating `getHostDefinedGlobal` as an ALS carrier would violate its actual global-object contract.

The installed public `JS::Prefs::set_use_js_microtask_queue(false)` setter is a supported non-startup preference. The isolated probe selects the legacy queue while it is empty, before application code, then installs `JS::SetJobQueue`. The component confirms the original flag is 1 and the selected flag is 0. No SpiderMonkey source fork is used. This is a pinned configuration choice with potential allocation/performance cost, not an assumption that the default queue already invokes the desired hook. [Preference API](https://github.com/bytecodealliance/firefox/blob/9dab3d6f643e926a340c391ea30968e940390dec/js/public/Prefs.h)

Production installation should occur in `runtime/engine.cpp::init_js`, before application promise registration and preferably before self-hosted initialization/realm creation. An empty queue alone cannot prove that no earlier pending promise registered a callback. The diagnostic builtin's later installation is bounded to the audited startup sequence, checks the existing queue, and precedes application evaluation; that is not a general hot-install policy.

StarlingMonkey initializes `js::UseInternalJobQueues` in `init_js`. Both the normal checkpoint and finalization-drain loop call `js::RunJobs` in `runtime/event_loop.cpp`. The pinned `js::RunJobs` dispatches through `cx->jobQueue->runJobs` and then clears kept objects, so a replacement queue receives these calls; the probe does not need an invented event-loop API. Off-thread dispatch and debugger saved-queue behavior still require production validation. [JSContext queue implementation](https://github.com/bytecodealliance/firefox/blob/9dab3d6f643e926a340c391ea30968e940390dec/js/src/vm/JSContext.cpp)

## Promise creation is also observable in Node

[The exact-release Node oracle](node-oracle-results.json) passes 19 cases and 63 observations using Node v22.14.0 with default flags. It covers pending/settled/interleaved awaits, empty registrations, `finally`/`all`/`race`, microtasks, timer cancellation, interval reuse, native filesystem callbacks/awaits, multiple stores, static snapshot/bind behavior and synchronous restoration.

These findings prevent several attractive but incorrect implementations:

- A promise created under A and resolved under B with a thenable created under C calls that thenable's `then` under A. A continuation awaiting it under D resumes D.
- An interval or reused `AsyncResource` retains an `enterWith` change across later invocations of that same resource. A fresh resource starts empty.
- `disable()` hides old stores, but re-enabling before an old pending resource resumes can expose its old store again. Permanently expiring a storage generation would differ.
- A continuation created while the instance is disabled remains empty after re-enabling.
- A `run` scope restores only that ALS instance. `a.run('A', () => b.enterWith('B'))` leaves a empty and b B; restoring an entire previous context map would erase b incorrectly.

The compiled Node source `internal/async_local_storage/async_hooks` confirms the per-resource-symbol model: resource initialization copies enabled stores, `enterWith` changes the current resource, `run` restores its own symbol in `finally`, and `exit` disables/re-enables the instance. [Pinned Node implementation](https://github.com/nodejs/node/blob/v22.14.0/lib/internal/async_local_storage/async_hooks.js)

## Separate real-component probe

`probe-public-v1.cpp` installs a native queue and uses existing `js::SetAllocationMetadataBuilder`/`GetAllocationMetadata` to capture **Promise creation** context. It does not wrap `.then`. The builder returns a pre-existing token only for Promise objects and allocates no JS object itself. The engine maintains the metadata association as a GC-traced weak-key relation.

The allocation metadata API has significant constraints: its callback runs for object allocations generally, its returned metadata must be in the **same realm** as the allocated object, only one builder occupies that slot, and metadata-table OOM uses an explicitly fatal policy. Installing it changes allocation/JIT behavior. The probe installs it only in the content realm; a production design must handle every participating realm and coexistence policy. [Metadata API](https://github.com/bytecodealliance/firefox/blob/9dab3d6f643e926a340c391ea30968e940390dec/js/src/jsfriendapi.h), [realm enforcement](https://github.com/bytecodealliance/firefox/blob/9dab3d6f643e926a340c391ea30968e940390dec/js/src/vm/Realm.cpp)

The v1 engine SHA is `85984d63544e09659d3a7692df6de21856da074ae0ef48f913b701e3efce7a5d`; its actual component SHA is `ccf8a26353a6cff68a640fe0e48ffeae6338578e42a4ddd5dd1f6c0ad585e5e9`. [Results](probe-public-v1-results.json) record **43 context checks on each of three calls to one Jco instance**, plus a fresh stock Wasmtime 42 invocation. Imports are empty. Sixteen optimized `await 0` operations add **zero enqueues** (27 to 27), while their store remains correct.

The probe also registers/cancels pure guest `api::AsyncTask` instances using the existing `IMMEDIATE_TASK_HANDLE`. This exercises actual Starling event-loop task dispatch without a new host service or external I/O import. It proves the native capture/restore mechanism, not real HTTP/socket/filesystem completion propagation.

All queued jobs/tokens are held in a traced `PersistentRooted`/`GCVector`; current/restored tokens use persistent/rooted handles. Jobs execute in their actual job realm, never their context token's realm. A moving collection while a continuation is pending preserves its captured store. Snapshot initialization starts with an empty token; repeated exported calls return to that empty token after draining. This is not a request-global abstraction or a production reuse/expiry policy.

## Species boundary and the private ABI experiment

The v1 result deliberately reports a Node mismatch for a custom Promise species returning a plain object. Node observes an empty context; generic registration data yields `PLAIN-REGISTER`. A species returning a real Promise created under SPECIES correctly runs the handler under SPECIES. The public enqueue callback replaces a non-Promise result capability with null, which otherwise also denotes optimized async/native reactions.

A separate v2 diagnostic explores whether the original capability can be recovered safely at this exact pin. The actual friend functions `FunctionHasNativeReserved` and `GetFunctionNativeReserved(job, 0)` expose the legacy job's holder. The source's `PromiseReactionRecord` retains its original capability in slot 0, even when the public callback parameter has been replaced with null.

That is **private ABI coupling**, not a general Promise hook. `probe-private-v2.cpp` validates the native function representation, class name, **11 reserved slots**, and membership in the retained content/initializer realms before reading the pinned slot; it never changes the execution realm from this information. Its separately built engine SHA is `ae92c43076bb1f5fff350c210fb74aab053d738e8e8c70aa7e710de49b6285f4`, and its component SHA is `ac123ba03e15c698a98055fcee62a835282beee954da5d18f2fc5669d5909fb8`. [The v2 results](probe-private-v2-results.json) pass the same 43 checks on three retained Jco calls and one fresh Wasmtime invocation with zero imports; the plain-object species now observes Node's empty context. Both actual-Promise species and the await/native-reaction cases still pass. The runner verifies that the compiled source is this private variant and requires both private-record counters and the species match.

Cross-realm wrappers, unknown job kinds and future SM layouts need explicit rejection/coverage. The class/slot checks constrain this exact audited guest build; they are not a stable public layout contract. No complete AsyncResource or public async_hooks compatibility follows merely from this read. The experiment establishes that this observed species distinction can be recovered at the pin without a SpiderMonkey fork; it does not settle all Promise-resource lifecycle or trigger-ID semantics.

In particular, the public enqueue argument can be a cross-compartment wrapper, while `JS::IsPromiseObject` requires an unwrapped object. The v1/v2 creation-metadata selection does not unwrap that argument, and only the content realm has a metadata builder. These probes therefore establish no cross-realm Promise fidelity. Unknown native holder classes also fall through to generic context selection; the current source/fixture is bounded, rather than an assertion that every arbitrary job class has been covered.

The immutable empty token is also only a context-value probe. The additional Node edge oracle observes that plain-object species callbacks can share the root resource: `enterWith` in one persists into the next, while a child captured before that change retains its earlier value. A full prototype must distinguish an immutable captured map from a mutable root resource cell, rather than treating successful empty lookup in v2 as complete resource behavior.

## Production resource model proposed for the next phase

Use a resource-local mutable execution cell containing an immutable map of ALS-instance IDs to store values. Creating an async resource snapshots the enabled stores from the current cell. Jobs/timers/I/O callback entry install that resource's cell and restore the caller's cell with RAII on every exit. `run` restores only its own entry against the cell's current map; `enterWith` leaves its update on that resource. Repeating timers retain their resource cell. `disable` affects propagation/lookup eligibility without destroying old resource stores. Static `bind`/`snapshot` should hold an explicit reusable resource, following the Node oracle.

For native tasks, capture once at actual registration/creation. Store and trace the resource state centrally or ensure every subclass traces its base context; adding an untraced field to `api::AsyncTask` would be unsafe. `TimerTask` currently traces its callback and arguments, and its repeats requeue the same task. `EventLoop::queue_async_task`, `cancel_async_task`, `TaskQueue::trace`, and `task->run` are concrete integration sites. I/O resource creation/completion must apply the same model; promise awaiters retain their own registration context even when resolution happens under an I/O resource's context.

Request ownership is separate. A fresh component entry/request resource starts with an explicit fresh execution cell. A request owner tracks borrowed/live handles and cancellation, not ALS-instance enablement. Cancel callbacks and rejection cleanups execute under their registered resource context before owner teardown. Deliberately reusing an application `AsyncResource` remains distinct from accidentally carrying a previous request's current cell into the next entry. Do not implement request expiry by permanently invalidating every ALS store generation.

## Remaining decisions and engine-build route

No public AsyncContext storage API was found in the pinned installed headers/preferences. Async stack APIs concern diagnostic stacks and are not context-store propagation hooks. The current experiment supports common context mechanics; production ALS still needs the complete API facade, mutable resource identity, multi-instance restoration, disable/exit, callback arguments/receiver behavior, realm handling, cancellation, entry teardown and performance/size validation.

Public Promise async-hook IDs/parent trigger relationships are a further requirement beyond ALS store lookup. The allocation metadata callback does not receive a parent Promise, and the generic job callback can elide resources. A complete `async_hooks.createHook` contract may need additional pinned private data or a narrow guest SpiderMonkey lifecycle hook. This has not been proven possible or impossible from the existing public API.

If a dedicated hook is justified, build the **guest** library at exact Firefox commit `9dab3d6f...` using the existing `cmake/spidermonkey.cmake` mozconfig and `mach --no-interactive build`: WASI target, disabled shell/JIT/shared memory/tests, portable baseline interpreter, exact SDK/compiler/toolchain and a versioned source patch. The existing CMake file lists the extra objects combined into `libspidermonkey.a`; the CI workflow copies the resulting library and dereferenced headers into a distribution. Select that distribution with the existing `SPIDERMONKEY_BINARIES` environment override. Pin generated configuration headers, source/patch/archive hashes and actual tool versions. Mach dependencies and a complete custom build have not been exercised here, and no host runtime change is needed.

## Reproduction

`build-probe.sh` builds an isolated source tree from the audited git base plus every exact R2 native input, then adds the copied diagnostic through the existing `add_builtin` mechanism using `CMAKE_PROJECT_ComponentizeJS_INCLUDE`. The production checkout and prior engines stay untouched. It requires the preserved R2 freeze and existing pinned SDK/SM cache; the receipt records that dependency rather than claiming a clean-checkout-only build.

```sh
NODE_COMPAT_NODE=/path/to/node-v22.14.0 \
  tests/node-compat/async-context/build-probe.sh

NODE_COMPAT_TOOLCHAIN=/path/to/pinned-toolchain \
NODE_COMPAT_COMPONENTIZE_MODULE=/path/to/audited-v2-package/src/componentize.js \
NODE_COMPAT_ENGINE=/path/to/separate-probe.engine.wasm \
  /path/to/node-v22.14.0 tests/node-compat/async-context/run-probe.mjs
```

To reproduce the separately preserved private-layout experiment, build with `NODE_COMPAT_ASYNC_PROBE_CPP` pointing to `probe-private-v2.cpp` and `NODE_COMPAT_ASYNC_PROBE_ROOT` selecting a new external directory. Set `NODE_COMPAT_ASYNC_PROBE_OUTPUT` and `NODE_COMPAT_ASYNC_PROBE_RESULTS` to distinct destinations when running it. This avoids overwriting the public-hook control or its sources/results. The checked-in `probe.cpp` remains the public-hook control.

This phase's native extension remains separate and experimental. Production built-in/module registration, import selection and the existing compatibility profile have not changed.
