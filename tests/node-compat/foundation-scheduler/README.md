# Private guest tick scheduler: source-only integration packet

This is a proposal for a bounded private `nextTick` dependency of classic
streams. It does not install `process`, `node:process`, a global scheduler, or
AsyncLocalStorage. No production file, engine, component, host executable, or
existing ALS/stream receipt was changed. The C++ and CMake files are
**uncompiled and unapplied**; their execution behavior has not been verified.

[phase-packet.json](phase-packet.json) defines the proposed contract, limits,
failure/lifecycle rules, and remaining gates. [source-audit.json](source-audit.json)
pins the actual current m0.10 **304 native inputs**, the compiled external
ComponentizeJS source, relevant SM147 headers, and prior evidence. Its baseline
is Starling revision `54b3329b3ce818fd1f244e871e9c259b63667cda` plus the exact
recorded working-tree manifest, rather than a claim that HEAD contains the
profile. The matched m0.10 OFF engine is
`1098e7531004a4ca1b47f2ca80527a01e64cd3392d28d760da37326c08a85154`;
this packet does not execute it.

## Verified sources and boundaries

| Actual integration point | Current behavior and proposed use |
| --- | --- |
| `runtime/engine.cpp::init_js` | Calls `js::UseInternalJobQueues`. Keep this queue for the initial private tick implementation; do not install a replacement Promise queue merely to implement ticks. |
| `runtime/engine.cpp::Engine` / `core::EventLoop::init` | Sets context private/enters content realm, initializes EventLoop, then calls `install_builtins`. Initialize the proposed traced FIFO here before application registration. |
| `runtime/event_loop.cpp::EventLoop::run_event_loop` | The first of exactly two current `js::RunJobs` sites. It drains jobs, checks strict pending-event errors, runs the queued FinalizationRegistry batch, checks interest, selects a task, removes it, and calls `task->run(engine)`. Replace this checkpoint with the bounded phase helper and select the initial origin explicitly. |
| `runtime/event_loop.cpp::EventLoop::drain_finalization_registry_cleanups` | The second `js::RunJobs` site, after each nonempty finalizer batch. Use the same helper here. The existing 16-round finalizer policy is separate and permits remaining finalizers after its limit. |
| `runtime/engine.cpp::Engine::eval_toplevel` | Calls `ScriptLoader::eval_top_level_script`, then the event loop, and during preinit performs GC/finalizer draining and strict rejection checks. Choose the configured module/classic origin for the first checkpoint; keep the current strict checks after the new full drain. |
| `runtime/script_loader.cpp::eval_top_level_script` | Classic scripts use `JS_ExecuteScript`; modules use `LoadRequestedModules`, `ModuleLink`, and `ModuleEvaluate`. Do not invoke `js::RunJobs` inside module evaluation; SM's implementation asserts it is outside an active evaluation. |
| `runtime/engine.cpp::run_initialization_script` | Runs the separate initializer realm synchronously with `JS_ExecuteScript`; it has no standalone checkpoint today. The proposed private callable is content-only. If initializer code reaches it through a captured content function, add/test an explicit classic initializer checkpoint after successful script execution and before content evaluation; do not silently classify it as ESM. |
| `runtime/js.cpp::wizen` / `Engine::finish_pre_initialization` | `finish_pre_initialization` occurs before ComponentizeJS export binding. Its `Initialized` state does not prove the final snapshot boundary. Add an empty/inactive-FIFO invariant here, without treating it as the final guard. |
| Actual patched `embedding/embedding.cpp::componentize_initialize` | Calls `__wizer_initialize`, then `bindExports` and export-object getters. The current strict patch already calls `run_event_loop` and checks unhandled rejections **after** binding. This actual post-binding checkpoint must also drain ticks and require an empty inactive FIFO before snapshot. |
| Actual patched `embedding/embedding.cpp::call` | Enters deployed execution, checks `Runtime.cur_fn_idx`, invokes the lowering function with `JS_CallFunctionValue`, attaches `JS::AddPromiseReactions`, and calls `Engine::run_event_loop`. Treat this as task/export origin, with an empty-FIFO entry invariant; retain strict post-loop rejection handling. |
| `builtins/web/fetch/fetch_event.cpp::handle_incoming_request` | Dispatches the event synchronously, then calls the same event loop. Its initial tick checkpoint belongs after dispatch and before the Promise drain. No new HTTP capability is implied. |
| `Engine::reset` / `EventLoop::reset` | Current reset cancels tasks, clears interest/event errors, resets timers and collects. Add tick-root disposal only outside callbacks/checkpoints. Current reset does not clear the separate SpiderMonkey Promise queue; do not claim it does. |

`EventLoop::process_async_tasks` is declared in the header but has no current
implementation/use; the proposal does not depend on it. `total_compute` is an
existing parameter, not an implemented guest CPU budget.

All six current `api::AsyncTask` implementations pass through the same selected
task dispatch: `TimerTask`, `BodyFutureTask`, `ResponseFutureTask`, `StreamTask`,
`BodyWriteAllTask`, and `BodyAppendTask`. Some completion callbacks run inside
their `run` methods, so the checkpoint belongs after the **whole** method
returns. Requeueing a task must not trigger an intervening checkpoint while its
native stack is active. Cancellation/registration outside dispatch need the
explicit owner/resource policy below.

`host-apis/wasi-0.2.0/host_api.cpp::AsyncTask::select` may create a monotonic-clock
pollable for mixed immediate/pollable tasks. Consequently an immediate AsyncTask
is not a suitable implementation of this host-free priority FIFO. Ticks need
neither an interest increment nor polling, provided they drain before the loop's
existing `interest_complete` exit.

## Ordering contract and Node evidence

The exact shipped Node22 source is extracted in
[task_queues.node-v22.14.0.js](node-source/task_queues.node-v22.14.0.js), with its
MIT notice. Its `processTicksAndRejections` drains the entire tick FIFO and then
runs a full V8 microtask checkpoint, repeating when ticks/rejection work remain.
It does not alternate a tick with each Promise reaction. Its public nextTick
captures arguments, async IDs, trigger IDs and the current async-context frame;
the private proposal does not yet implement IDs/hooks/frame propagation.

[node-results.json](node-results.json) records four small, ordinary Node-only
boundary traces, callback validation/arguments/receiver/return checks, and a
separate unhandled tick throw exiting with status1 before the next callback.
No infinite recursion, fault injection, old DEBUG engine, raw memory access, or
guest execution is involved. The existing
[task/Promise-job Node-versus-Jco drift receipt](../foundation-stream/reference-results.json)
is reused unchanged instead of repeating the earlier adapter investigation.

The extended trace contains an already queued Promise, a tick that enqueues
another tick and Promise, a microtask, and a Promise that enqueues a tick and
another Promise:

| Boundary | Exact observed order |
| --- | --- |
| Classic initial evaluation / native task | tick-first, nested-tick, promise-first, microtask, promise-from-tick, nested-promise, tick-from-promise |
| ESM initial evaluation / Promise-job body | promise-first, microtask, nested-promise, tick-first, tick-from-promise, nested-tick, promise-from-tick |

The proposed loop is therefore:

1. On a task/classic/export origin, drain the tick FIFO including ticks appended
   by ticks. On the initial module-evaluation origin, skip this first step once.
2. Run one **complete** existing `js::RunJobs` checkpoint and apply current
   exception/event checks.
3. If ticks were enqueued during that full drain, return to step1. Only after
   this cycle reaches no pending ticks may the loop run finalizers/check interest
   or select the next task.

Do not run this helper recursively from a Promise job. Dynamic ESM evaluation
already inside a job completes within the outer full checkpoint before ticks.
Statically transformed CommonJS inside a bundled ESM initializer uses the
selected ESM boundary contract; it does not gain native CommonJS ordering from
its original filename. Deployed source functions exported from ESM are entered
as normal host/task callbacks, not as a new module evaluation.

The current SM `js::RunJobs` dispatches its configured queue and calls
`JS::ClearKeptObjects`. Its internal queue can report/clear job exceptions via
`PrepareScriptEnvironmentAndInvoke`; checking `JS_IsExceptionPending` alone is
not proof of Node-wide microtask error parity. The tick helper directly calls
the callback, preserving its pending exception rather than inserting it into a
Promise reaction. Existing strict Promise-rejection and pending-event handling
remain distinct. New uncaughtException/unhandledRejection events are deferred.

## Proposed queue, rooting and limits

[tick-queue.UNCOMPILED.cpp](tick-queue.UNCOMPILED.cpp) uses only observed JSAPI:
`PersistentRooted`, `GCVector`, `Heap`, `TraceEdge`, `RootedValueVector`,
`JS::NewArrayObject`, `HandleValueArray::subarray`, `JS_GetElement`, `JS::Call`,
`JSAutoRealm`, `JS::CreateError`, `JS_DefineProperty`, and `js::RunJobs`. These
symbols/signatures are pinned in the source ledger; the new code is uncompiled.

The proposal uses a lazily allocated fixed4096-slot ring, with a traced callback
and a private packed Array of copied argument **values** per pending tick.
Those arrays are never exposed; referenced objects retain identity. Root the
callback, argument array and extracted argument vector before clearing its ring
slot and calling JavaScript. No queue interior pointer is used after that call.
GC can update every queued or active reference; no raw string/buffer span,
cross-allocator transfer or host handle is stored.

Private packed arrays make ownership easy to audit but cost an allocation and
an invocation-time argument copy. Compare this with a traced native argument
arena only after correctness and measurements; do not assert this representation
is optimal. The pending limits are 4096 callbacks, 1024 arguments per callback,
and 65536 retained argument values. A checkpoint additionally permits at most
65536 executed ticks across all its tick/Promise rounds. The limits count values,
not transitive application object graphs, and do not bound an independent
infinite Promise chain.

Callback validation precedes allocation. A failed enqueue commits no entry;
allocation failure propagates the actual JSAPI failure. Overflow throws a coded
RangeError and leaves already queued work intact if the caller catches it.
Work-budget exhaustion at the native checkpoint fails the boundary, releasing
remaining tick roots instead of silently yielding and changing order. Callback
return values are ignored; returned rejecting Promises retain the existing
tracker policy. A thrown callback preserves its original value, stops draining,
releases remaining entries and returns false to the existing fatal embedding
path. Error codes are defined as own data properties, avoiding an inherited
`Error.prototype.code` setter. No process error listener can resume this profile.

Nested enqueue is supported. Nested checkpoint/event-loop execution or reset
during a callback is a coded failure. The existing EventLoop guard and the new
private checkpoint guard must agree. Cross-realm callback support is excluded
from this first private template; arguments must not be mistaken for safe raw
cross-compartment handles. Node's public nextTick is constructible (confirmed
by the oracle); construction/descriptor parity is outside this private callable
contract.

## Actual integration delta, not new embedding APIs

[integration.UNAPPLIED.cmake](integration.UNAPPLIED.cmake) proposes an optional
`NODE_COMPAT_INTERNAL_TICKS=OFF` flag. Validate it against the existing
`builtin_node_compat` target, publish the selected definition via `extension_api`,
and conditionally add the queue source to the **existing** `starling-raw.wasm`
target after that target is declared. No timer, clock, polling, entropy,
environment, socket or host-service dependency is needed. Emitted imports still
require a new-component audit before claiming zero imports.

The corresponding source edits, still unapplied, are:

- Add queue initialization to `EventLoop::init` and disposal to reset.
- Extend internal `EventLoop::run_event_loop` with an origin argument/default.
  `Engine::run_event_loop()` can retain its existing external signature/default
  task behavior; `Engine::eval_toplevel` passes the configured module/classic
  origin directly to the internal loop. After each task/finalizer batch use its
  own origin. The two RunJobs sites call the shared checkpoint helper.
- Add explicit empty/inactive checks at preinit completion, the actual final
  post-bindExports boundary, and fresh deployed entry. Never use the permanent
  entropy-entry bit as a request/context token. Ensure initializer-realm work has
  its separately reviewed checkpoint instead of being accidentally reprioritized
  by the later content module.
- The existing `register.cpp::evaluate_factory` can receive the proposed
  `create_private_callable(cx)` directly as a factory argument. A future audited
  classic-stream factory consumes that argument in its pinned scheduler slots.
  Any rewriting is confined to that selected dependency graph and hash-pinned;
  no global `process` object or pretend `node:process` namespace is introduced.

Keep public process/env/argv/exit/cwd/signals/spawn/time APIs separately deferred
or explicitly capability-selected. Importing them must not succeed because an
internal stream dependency has a useful tick function. The factory/module
manifest and bundler admission must make that separation reviewable.

Version the private policy as `private-guest-ticks-v1` in a future build receipt,
with explicit requested/observed `NODE_COMPAT_INTERNAL_TICKS` and a boolean
selection field, source hashes, and the actual queue compile command. Optional
OFF must omit the source/callable/initialization rather than merely creating an
unused queue. Old receipts remain historical evidence; no synthetic new receipt
may infer feature selection from a missing field. A future classic-stream
manifest/factory must declare its dependency on this selected private policy.
Standalone CLI evaluation and `init_from_environment` reach the same Engine
constructor/evaluation sites; their CLI/environment imports stay separately
selected. This does not reproduce every Node native `MakeCallback` phase or
infer multiple callback boundaries inside a single existing guest task.

## Snapshot, reuse and future ALS

Every normal export must finish with an empty tick FIFO even if its Promise
settled before the final tick was added; check interest only after the full
cycle. Before a subsequent entry, require an empty/inactive FIFO rather than
discarding uncompleted work to disguise a leak. Module state may be retained,
but pending entries must not cross a completed export/snapshot. Reset outside
execution clears tick roots and releases ring storage; pending Promise jobs,
native tasks, borrowed handles and owner cancellation remain distinct concerns.

Reuse the already tested
[mutable resource model](../async-context/resource-model.md), without claiming
that old diagnostic is production ALS:

- At tick enqueue, the real prototype's `new_resource(cx,current_token,true)`
  copies enabled bindings into a distinct mutable cell. Capturing only a pointer
  to the parent's mutable cell would let later `enterWith` change an already
  queued child. Add a traced `Heap<JSObject*> resource` to the tick and root it
  before removing the entry. `Scope` in `resource-model-v3.cpp` uses a rooted
  previous cell and RAII restoration on every return/error.
- Enter the callback's actual realm; a resource cell never substitutes for a
  global or selects an execution realm. Child ticks capture from the callback's
  current resource. `run` restores only its ALS instance; other `enterWith`
  changes on the resource survive as the existing oracle requires.
- Full Promise/await propagation still needs the separately reviewed
  `JS::JobQueue::getHostDefinedData`, enqueue/creation metadata selection,
  `JS::SetJobQueue` and preference configuration from the existing probes.
  Their same-realm requirement, private reaction-record coupling, fatal
  metadata allocation policy and debugger saved queues remain explicit gates.
  Never wrap `.then` to claim `await` propagation.
- Real tasks capture once at registration, retain that cell on requeue, trace
  pending cells centrally and root an active cell **before** removing its queue
  entry. Current `TaskQueue::trace` calls derived `AsyncTask::trace`; adding an
  untraced base field would be unsafe. A side table needs stable ownership and
  cleanup, not raw pointer reuse. Current `queue_async_task` returns void, so
  newly fallible capture requires an explicit API/caller change or pre-capture
  before enqueue; no recoverable behavior is implied by that void API.
- A fresh deployed entry gets a fresh cell from an initialization-only empty
  template. A request owner tracks cancellation/borrowed handles separately.
  Cancel callbacks run under their registered cell before owner teardown;
  deliberately retained application resources are different from leaked current
  request state. Do not expire all ALS stores by changing one generic generation.

No resource field is silently included in the initial template: selecting and
testing the complete propagation/ownership layer is a prerequisite for any ALS
claim, including a classic-stream async-context claim.

## Dependency-ordered validation before implementation acceptance

1. Review the pinned ancestry, private injection, limits/error policy and exact
   origin edits; choose a new isolated candidate source tree/build flag.
2. Compile/link the actual queue and initializer/embedding deltas against SM147;
   audit generated sources and optional-OFF imports/size. This packet has done
   neither compilation nor guest execution.
3. Use a real pure guest AsyncTask (the already verified probe route), actual
   exported callback entry, classic/ESM evaluation and bindExports getters to
   differential-test all four traces. Include tasks after tasks, nested ticks,
   full nested Promise drains, late rejection handlers and finalizer batches.
4. Check callback/argument identity, strict/sloppy receiver, ignored returns,
   ordinary callback errors, pending-event errors, reentry, each finite limit,
   queue disposal and collection using ordinary supported APIs. No unsafe old
   engine, fault-injection, raw-memory or DEBUG/OOM experiment is authorized by
   this packet.
5. Verify top-level errors still fail componentization, final snapshot queues
   are empty, repeated exports do not inherit ticks, reset handles no active
   callbacks, imports match explicit standard selections, and fresh stock
   Wasmtime/Jco instances execute the same component.
6. Measure component-size/startup/queue memory and retention/throughput, then
   select a storage optimization only if justified. Actual HTTP/timer/stream
   completion and cancellation/ALS gates follow under selected standard worlds.

Reproduce only the completed source/oracle checks with the pinned binary:

```sh
/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node \
  tests/node-compat/foundation-scheduler/run-node-oracles.mjs
python3 tests/node-compat/foundation-scheduler/capture-source.py
```

The second command requires the preserved exact m0.10 OFF receipt/artifact and
fails if any of its304 live native source hashes differs. New C++ templates and
future flags are proposals, not APIs discovered in the existing embedding.
