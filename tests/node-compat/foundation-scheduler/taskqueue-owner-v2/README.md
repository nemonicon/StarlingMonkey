# TaskQueue-owned private ticks — unapplied source proposal

This is a compact sibling to the unchanged [original scheduler packet](../README.md).
It is **unapplied, uncompiled, unlinked and unexecuted in a guest**. It changes no
live native source, build recipe, public Node module, global, host implementation,
or stream/web factory record. Root review precedes SDK syntax checking; a new
Release engine and ordinary component tests precede any integration claim.

The [ancestry receipt](source-receipt.json) checks all 304 current native inputs
against the original exact inventory plus the four approved
[m11 source deltas](../../foundation-alloc-unsafe/production-adoption-m0.11/source-receipt.json).
The pinned native revision is `54b3329b3ce818fd1f244e871e9c259b63667cda`,
ComponentizeJS is `4d812f5a7b524cea5bcfd565cac55f3fab876a57`, SpiderMonkey147
is `9dab3d6f643e926a340c391ea30968e940390dec`, and the compatibility oracle
is Node **v22.14.0**. The receipt hashes the actual full input list, existing
embedding and build recipe; it does not mistake the Git revision for a clean tree.
Latest accepted execution remains the [v10 checkpoint](../../milestones/foundations-v10/README.md);
these source assertions do not upgrade it.

## Concrete deltas

- [Native diff](starling-taskqueue-ticks.UNAPPLIED.patch): five existing files
  plus new `runtime/node_tick_queue.{h,cpp}`. The two new source bodies also exist
  under [proposed/runtime](proposed/runtime/node_tick_queue.cpp). It adds an optional
  **default-OFF** `NODE_COMPAT_INTERNAL_TICKS`, requiring the existing core profile.
  The definition flows through `extension_api`; the new runtime source is selected
  on the existing `starling-raw.wasm` target after that target is declared.
- [Embedding diff](componentize-taskqueue-ticks.UNAPPLIED.patch): the already
  patched exact `embedding.cpp`, preserving its numeric ABI, entropy-entry and
  strict/protected policy changes. It adds final post-bind and fresh-entry checks.
- [Test extension source](test-extension.UNCOMPILED.cpp) and
  [opt-in CMake include](test-extension.UNAPPLIED.cmake): isolated diagnostic
  guest modules using actual `add_builtin` and `Engine::define_builtin_module`.
  Neither is included by the live recipe. No extra persistent root is introduced.
- [Ordering proof](ordering-proof.json): four **previously executed** Node traces
  matched by a small pure-Python phase model. This is not C++ execution proof.

`api::Engine::run_event_loop()` in [extension-api.h](../../../../include/extension-api.h)
and its existing implementation remain byte-unchanged. The two-argument internal
`EventLoop::run_event_loop` remains the default TaskOrExport wrapper. A new
three-argument internal overload carries only initial origin. No existing
embedding API is renamed, and no host or public `node:process` API is invented.

## Ownership and the private callable

The existing `PersistentRooted<TaskQueue> queue` in
[event_loop.cpp](../../../../runtime/event_loop.cpp) remains the sole owner root.
`TaskQueue` receives an `InternalTickQueue` member and its trace hook visits that
member, alongside its existing `AsyncTask` roots. The old proposal's extra
process-static `PersistentRooted<Storage>` is absent. There is no separate
`JSContext*`, current-resource global, timer, pollable, or external handle in ticks.

The class owns a lazy, fixed ring of 4096 slots. Each slot has two traced
`Heap<JSObject*>` fields: a callable and a private dense argument Array. That Array
is never exposed. Enqueue validates the callable object's actual realm, copies
argument **values** using `JS::NewArrayObject`/`HandleValueArray`, and commits the
slot only after allocation succeeds. Values retain object/Symbol identity. A
same-realm proxy can invoke other code; the realm check is not an isolation or
security boundary.

Dispatch roots the callback and private Array, copies every argument into a
`RootedValueVector`, and only then clears/dequeues the slot. The callback enters
its actual realm and receives `undefined` as its pre-conversion receiver. Return
values are ignored; returned rejecting Promises remain subject to the existing
rejection tracker. The fixed ring never grows during callback dispatch. No raw
JS pointer spans an allocating JSAPI call without rooting.

The proposed internal `EventLoop::create_internal_next_tick(cx)` constructs the
native callable in the caller's current realm. A future audited classic-stream
factory should receive that function **directly as its private factory argument**,
using the existing strict `evaluate_factory` route in
[register.cpp](../../../../builtins/node-compat/register.cpp). There is no shipping
classic-stream factory or injection change in this packet. Node's public
`process.nextTick` is constructible; that public constructor behavior is outside
this private callable contract. No public process facts, CLI/environment,
`uncaughtException` events, async IDs or AsyncLocalStorage are supplied.

## Actual boundaries and phase rules

The source has exactly two existing `js::RunJobs` call sites; both selected
branches delegate to the same proposed full-checkpoint helper. It retains
SpiderMonkey's complete job draining, kept-object cleanup and current job-error
reporting. It never wraps `Promise.prototype.then`, swaps the JobQueue, or
interleaves ticks between individual jobs.

| Actual entry | Origin and proposed order |
| --- | --- |
| `Engine::eval_toplevel` after `ScriptLoader::eval_top_level_script` returns | Read **`config_->module_mode`** at this internal call. Classic: ticks, full jobs, new ticks/full jobs until empty. ESM: first full jobs, then ticks/full jobs until empty. Never call RunJobs inside ModuleEvaluate. |
| Existing `Engine::run_event_loop()` after deployed lowering | TaskOrExport default; ticks before the full jobs checkpoint. |
| Selected `AsyncTask::run` completes in the existing loop | Next loop pass uses TaskOrExport; drain ticks FIFO before full jobs. Do not turn a tick into an AsyncTask. |
| Jobs enqueue ticks | Finish the entire current jobs checkpoint; drain the new ticks afterward. |
| `run_initialization_script` in the actual INIT realm | New explicit classic initializer checkpoint after successful `JS_ExecuteScript`, before content evaluation. This is an embedding policy requiring its own test, not Node ESM equivalence. |
| Existing finalizer batch in the normal loop | Preserve the batch and existing strict-error check, then tick/full-jobs checkpoint. Node finalizer parity is unverified. |
| `drain_finalization_registry_cleanups`, second existing RunJobs site | Preserve its strict cleanup-error check **before** dispatch, then the full helper. Existing 16-round finalizer policy remains. |
| `finish_pre_initialization` | Require an empty, inactive FIFO. This is early; it is not the actual final ComponentizeJS snapshot boundary. |
| `componentize_initialize`, after all `bindExports`/export-getter processing | Existing final run-loop and rejection checks remain; additionally require an empty, inactive FIFO. |
| `call`, after existing `cur_fn_idx` reentry check and before fresh dispatch | Require an empty, inactive FIFO; stale work is an error, never silently discarded. This does not use the permanent entropy-entry bit as request identity. |

The six current task kinds are `TimerTask`, fetch `BodyFutureTask` and
`ResponseFutureTask`, `BufReader`'s `StreamTask`, and host body
`BodyWriteAllTask`/`BodyAppendTask`. They share the existing loop dispatch.
The diagnostic uses `IMMEDIATE_TASK_HANDLE` only to prove a real task boundary;
ticks themselves never call `AsyncTask::select`. That selector can use a clock
pollable if immediate and non-immediate tasks are mixed, so a zero-import test
must use isolated immediate tasks and audit the final component bytes.

## Bounds and errors

| Bound | Selected behavior |
| --- | --- |
| Pending callbacks | 4096 |
| Arguments per callback | 1024 |
| Total pending argument values | 65536 |
| Callbacks executed by one checkpoint, across its tick/jobs rounds | 65536 |

Queue/argument overflow throws a RangeError with own
`ERR_SM_NODE_SCHEDULER_LIMIT`, before insertion. Callback validation throws an own
`ERR_INVALID_ARG_TYPE`; different/unknown callable-object realms throw an own
`ERR_SM_NODE_UNSUPPORTED`. Work-budget exhaustion fails the boundary rather than
yielding into tasks. These profile caps differ from Node. They limit retained
value slots, **not** the object graphs those values reference, Promise job work,
individual callback cost or an independently infinite Promise chain.

The proposed `JS::CreateError` helper defines its own code data property through
`JS_DefineProperty`, avoiding an inherited `Error.prototype.code` setter.
Error construction is fallible and propagates actual allocation failure; there
is no fault injection or claimed OOM recovery proof. Reentry has an own
`ERR_SM_NODE_SCHEDULER_REENTRY`; stale boundary state has an own
`ERR_SM_NODE_SCHEDULER_STATE`. Rooting/API syntax remain uncompiled.

A caught enqueue validation/limit error leaves no partially committed entry.
A directly thrown tick value is retained by SpiderMonkey's pending exception;
dispatch stops and pending tick references are discarded. A false native call
without a pending exception also fails the boundary. Existing task/finalizer
ownership is not secretly cancelled by this discard. Existing fatal embedding
behavior applies; **reuse after an aborted component is not promised**.

The existing strict EventTarget latch is taken after the full jobs checkpoint,
not newly after every tick. Its ordering/error-precedence and the known m10
callback-return then-getter counterexample are not silently changed or repaired.
The existing job runner may report/clear a job error; the new helper does not
claim to make every Promise callback failure observable as a pending exception.

## Reset is OPEN, not lifecycle closure

The patch adds an idle precondition at the start of `Engine::reset`, before
clearing rejected Promises/tasks/timers, and again at `EventLoop::reset`. It
releases tick storage only while idle. This is a **partial precondition**, not a
complete safe-reset guarantee. There is no public application reset API in the
current components; repeated export success is not evidence for Engine reset.

The [cancellation audit](cancellation-audit.json) records the current six virtual
`cancel` implementations. Timer cancellation unsubscribes; fetch's two cancels
only invalidate handles and retain TODOs; BufReader cancellation invalidates its
handle. `BodyWriteAllTask` and `BodyAppendTask` explicitly mark cancellation
`MOZ_ASSERT_UNREACHABLE`. None of these current cancel bodies calls application
JS, but the existing `q.tasks` range-for is not a future-safe ownership design if
cancel becomes JS-capable or mutates that vector.

Before a reset/reuse guarantee, a reviewed reset-in-progress guard must reject
tick enqueue, nested loop and nested reset while cancellation runs. It must also
address the **void** `queue_async_task` API, task insertion/removal during reset,
a traced owner for tasks removed before JS-capable cancellation, the two currently
uncancellable task contracts, finalizers and the separate Promise queue. Merely
adding a boolean around tick callbacks would leave those issues open. No such
broader reset patch is included or claimed tested here.

## Concrete future test access and acceptance

The proposed test-only include uses the already-used
`CMAKE_PROJECT_ComponentizeJS_INCLUDE`/`add_builtin` mechanism from
[async-context/probe.cmake](../../async-context/probe.cmake). Enable both private
ticks and `ENABLE_BUILTIN_DIAGNOSTICS_INTERNAL_TICKS` in a separate source/engine
build, never the live recipe. It defines real finite guest records:

- `starling:test-internal-ticks`: `nextTick`, `scheduleTask`, `attemptReentry`,
  `checkResetGuard`, and default with those same named function identities.
- `starling:test-initializer-ticks`: initializer-realm `nextTick` and default.
  It uses the existing `Engine::init_script_global()` root without a temporary
  task, extra global or realm bypass; both native functions use the same owner.

The diagnostic `BoundaryTask` implements the actual `bool run(Engine*)`,
`bool cancel(Engine*)`, and `void trace(JSTracer*)` virtuals, `RefPtr` and existing
interest accounting. Its own pending-task cap is 16. `attemptReentry` first
requires an active checkpoint, so it cannot accidentally call RunJobs from a
module body. `checkResetGuard` only checks the idle precondition; it **never**
executes Engine reset or claims cancellation safety.

Use raw ComponentizeJS source imports of those literal test IDs; do not weaken
production bundler admission. [fixture.UNEXECUTED.mjs](fixture.UNEXECUTED.mjs)
proposes actual snapshot ESM ordering, task ordering, identities and safe
reentry checks. The separate [initializer](initializer.UNEXECUTED.js) uses the
existing `defineBuiltinModule` to publish an application observation record;
[its content fixture](initializer-main.UNEXECUTED.mjs) must see its count already
updated **at content evaluation**, not merely after the later snapshot drain.
These are source templates, not a complete or executed harness.

Before integration, add and run ordinary tests for the four limits, caught-error
noncommit, FIFO/ring wrap, callbacks retaining objects/Symbols/arguments across
moving GC, callback throw identity, returned rejection tracking, post-bind getter
jobs/failure, new-task origin after ESM/TLA, and repeated deployed exports.
A 65,536-work failure and an uncaught callback need independent fresh instances;
never imply safe reuse of an aborted one. The actual outside-loop reset harness
and all cancellation policies remain separately blocked decisions above.
Run Release and Release-GC; inspect imports on real Jco/Wasmtime components and
the selected standard-host world. No old DEBUG/fault/private-memory probes are
part of this work. Size, queue retention and throughput remain unmeasured.

## ALS stays separate

No tick context field is included. A future reviewed adaptation of
[resource-model-v3.cpp](../../async-context/resource-model-v3.cpp) could call its
actual fallible `new_resource(cx,current_token,true)` at enqueue, trace a private
resource cell beside each callback/argument Array, root it before dequeue, and
use its rooted RAII `Scope` for dispatch/restoration. Promise creation/registration
selection and native task capture are separate integration work: metadata-builder
fatal OOM, private reaction ABI, void task enqueue, saved debugger queues and
request/resource ownership remain unresolved. No `.then` wrapping or generic
request global can supply that propagation contract.

## Reproduce source checks only

`prepare-packet.py` rechecks all 304 ancestors and regenerates only files in this
new directory; `check-ordering.py` compares a Python model with the preserved
Node evidence. `git apply --check` verifies patch applicability without applying.
None invokes a compiler, guest, host service or live source mutation. The
[index](index.json) records the frozen packet hashes. SDK syntax, new native
engines and components remain **pending root review/authorization**.
