# Classic-stream measurement design addendum

No classic benchmark, build or guest runs here. This read-only addendum closes
a concrete access gap in the frozen [measurement plan](../integration-candidate-v1/measurement-plan.md):
its reference factory takes `nextTick`, but current production exports provide
neither `process` nor public `nextTick`. `install_classic_streams` captures a
function from `core::EventLoop::create_internal_next_tick` in a private argument
record (`builtins/node-compat/register.cpp:163–191`). JavaScript cannot retrieve
that closure binding through the supported module namespace. A same-engine
reference cannot simply call a presumed process/global API.

The installed classic state machines are captured guest JavaScript. They are
not a C++ stream/backpressure kernel. Native Buffer/decoder primitives and
the guest C++ scheduler do not change that distinction.

## Feasible bounded harnesses

| Experiment | Legal access and comparison | Meaning and limits |
| --- | --- | --- |
| Same-engine, same bounded semantics and queue | A **new benchmark-only** guest extension creates a tick callable using the existing native method; a reference bundle imports that finite test module and actual native Buffer/Events/StringDecoder, then injects them into the same bounded factory. Installed and bundled factory arms use one identical benchmark engine. | Isolates registration/packaging/binding-path effects with both installed factory and extension cost common. It does not prove enabling the module is free or a native state-machine advantage. |
| Existing Jco provider on the same production engine | Bundle the actual locked Jco provider and its existing private `stream/scheduler` guest module; native arm keeps the registered module. | No new scheduler export/build is needed, but this includes provider/dependency/scheduler differences. Its microtask queue has measured Node-order counterexamples. Restrict timed cases to a validated common domain and retain mismatches; this is not a same-queue causal comparison. |
| Whole component cost | Compare reviewed classic-ON versus classic-OFF profiles with the respective equivalent application bundles; for matched private scheduling, both need the same benchmark extension, so these are two newly audited benchmark engines. | Reports the combined profile/bundle/snapshot result. A flag/source/bundle difference and all common diagnostic cost must be explicit. Existing production ON/OFF engines can support a separate stock-Jco comparison with different scheduler semantics. |

For the first experiment, reuse the **mechanism**, not an invented embedding
API: `diagnostic-candidate-v1/diagnostic.cmake` uses `add_builtin(...
DISABLED_BY_DEFAULT SRC ...)` through a separate `CMAKE_PROJECT_ComponentizeJS_INCLUDE`.
Its `test-extension.cpp:101–111` enters `engine->global()`, creates a rooted
module record/callable and registers it with `Engine::define_builtin_module`.
The production registrar already calls the same real scheduler method.

A future minimal benchmark extension should sequentially check the plain-object
allocation, then create/check the rooted tick function, define the finite named
binding and publish an unmistakably test-only guest module. Do not blindly copy
the older diagnostic's two-allocation-before-check sequence. Retain no borrowed
payload pointer; the module and closure graph must trace the callable normally.
Keep any optional idle assertion at an actual fresh entry using the existing
`require_internal_ticks_quiescent`, not inside an active async checkpoint.
These are proposed test bindings, not existing public module exports or new
production APIs. No reset path is needed or authorized.

`EventLoop::create_internal_next_tick` (`runtime/event_loop.cpp:189–195`) creates
the same JSNative dispatcher that enqueues into the active TaskQueue's private
FIFO. The two factories may capture distinct function objects, but both must
reach that same queue/owner and limits. Trace/check that behavior in correctness
fixtures before measuring. Do not expose the function through a global, steal
it by mutating production modules, or replace Node ordering with a silent shim.

The extension changes the engine source/build. It needs its own exact source
manifest, compile-target evidence, frozen config, after-build witnesses and
diagnostic-only admission. Do not relabel it as one of the four reviewed342
production engines or weaken their selectors. The same engine bytes must be
used by both throughput arms. The existing diagnostic producer demonstrates
how parent CMake targets may need separate actual Ninja command evidence;
membership in the native61 JSON database must not be assumed.

## Actual reference-provider inventory

Locked Jco1.40 `dist/node-builtins/stream.js::createStreamBuiltin` routes
readable-stream's `process/` to `stdModule(options.streamSchedulerModule,
'stream/scheduler')`. `shared.js::stdModule` accepts that path override, and
`types.d.ts` declares it. This is a real importer-scoped provider option, not
a public Node process module. A scheduler override would make a **modified
provider** experiment; preserve its source delta rather than call it stock Jco.
Other shared dependency overrides/aliases must be recorded too.

The default module is Jco-std0.10's
`wasi/0.2.x/node/24.x.x/stream/scheduler.js`: an array FIFO schedules `flush`
with `queueMicrotask`; its default object has only nextTick/undefined stdio.
It is pure guest JS, but has no equivalent declared native queue caps. The
existing [source audit and reference cases](../../foundation-stream/README.md)
already show Promise/tick ordering differences. Merely changing its name to
nextTick does not give Node behavior.

Jco-std's core imports readable-stream4.7.0 `lib/stream.js` (Node18.19-derived,
upstream commit88df210…). Its index adds Node24.20-derived lifecycle/Web
features, changes byte defaults/views and adds API beyond this Node22 profile.
The Jco emitter adapter mutates aliases and uses a constructor Proxy for unenv's
class emitter; the installed EventEmitter is already callable. A fair matched
factory arm must use the actual native emitter directly rather than add that
Proxy. Stock-provider comparison must retain its actual adapter behavior and
identify it as a different dependency graph. Do not substitute Node24 consumer
exports or Web streams for the pinned classic surface.

`source-review.json` records exact package/source/license hashes. Package
metadata: Jco1.40.0 and Jco-std0.10.0 declare Apache-2.0 WITH LLVM-exception;
the installed Jco package has no top-level license-text file, while Jco-std's
LICENSE is present. readable-stream4.7.0, unenv2.0.0-rc.24,
abort-controller3.0.0, event-target-shim5.0.1, buffer6.0.3 and
string_decoder1.3.0 declare MIT and ship license texts. Preserve the actual
reachable graph's notices, Node-derived MIT notices and local transformation
ledger; package metadata alone does not replace the missing Jco notice text.
The same bounded factory's existing Node/readable-stream notices are retained.

## Correctness and measurement protocol

Freeze the actual bundle graph and verify its intended external imports.
Use distinct reference entry IDs/relative sources so the native resolver does
not replace the reference with the installed `node:stream`. The native arm
must keep real native imports; the reference must not accidentally pull another
npm Buffer/emitter/decoder into a claimed shared-dependency comparison. For a
stock Jco comparison, inventory those actual differences. No monkey-patched
global Buffer or public process dependency is implicit.

Before timing, use Node22 checksums **and event-order traces** for public valid
APIs: Readable→PassThrough→Writable with64B/4KiB/512KiB chunks, fragmented UTF8
through StringDecoder, object-mode backpressure/high-water marks, and bounded
handled pipeline errors/abort completion. Check end/error/finish/close counts,
callback receiver/arguments, EOF and pending/settled Promise boundaries. Retain
Jco/native/Node counterexamples. Snapshot initialization must contain no queued
work; test fresh and retained exports and closed/failed instance discard.
Full per-event traces belong to correctness runs. Timed exports should return
only bounded checksums/counters, with the same checksum/control cost in both
arms; unbounded per-operation logging would change the measured allocation load.

Hold per-buffer sizes below16MiB, queued chunks/objects below4096 and pending
callback/argument/work budgets below the actual private limits. Repeated input
views and copying Buffer construction are separate cases. Checksum only public
stream output bytes/values; use deterministic input generation. Include an
equally applied checksum/input/constructor-only control and report its raw cost,
without silently subtracting it. Avoid unsupported encodings/copy methods,
unhandled fatal work, unsafe old compression/Blob paths, detach/shared/fault or
private-memory experiments.

Measure host time around batched WIT exports; add no guest clock import.
Audit final imports/exports for every arm, expecting no host capabilities for
pure batches but proving that from actual final components. Record the same
engine, splicer/adapter, world/options, dependency/library/source hashes,
workload/counts and output checksums. Keep componentization/snapshot time
separate from cold deployed instantiation and warmed operation batches.

Use opposite arm orders, fresh independent processes/instances and at least
seven within-worker samples; label the latter correlated. Select a coordinated
quiet CPU window only after all correctness gates pass. Retain every slowdown,
order reversal, outlier and raw child status/log. Report process-level summaries
and shared-desktop/low-independent-sample limits. No older Buffer or host-only
stream result transfers to these experiments.

Record final component bytes, public process current/peak RSS (with host/tool
units and whole-process scope), startup time and operation/byte throughput.
For Jco, observe only a publicly exported `WebAssembly.Memory.buffer.byteLength`
when available; otherwise mark capacity unavailable. Capacity deltas are not
internal `memory.grow` counts: wrapping JS `Memory.grow` misses guest instructions.
No private ABI, raw memory reads or inferred allocator ownership/retained-store
counts are permitted. Stock Wasmtime CLI RSS includes its own compilation and
runtime. HTTP adds transport/instantiation effects and counters of one do not
prove retained-instance reuse.

No promotion follows from this design, native build/syntax success or a common
checksum alone. Make a cost claim only after actual real-component correctness,
appropriate unmodified-host gates and the specific paired measurements, with
same-engine operation effects and whole-profile tradeoffs reported separately.
