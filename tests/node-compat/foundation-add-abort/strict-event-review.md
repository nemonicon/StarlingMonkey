# Strict uncaught-event latch: independent source review

This is a source-only review of the unmodified v7 inputs below, not a compiled
implementation or a runtime test result. No production source was edited and no
component was built or executed for this review. The approved policy is broader
than snapshot initialization: in the selected Node profile an uncaught event
callback error fails the next embedding checkpoint, including deployed exports.
The application must discard a component after such a failed export. The
profile-disabled behavior remains report-only. This is an explicit compatibility
deviation from browser-style reporting, not a claim of complete Node process or
Web error-reporting behavior.

## Source findings

* `builtins/web/event/event-target.cpp:552–570`,
  `EventTarget::inner_invoke`, ignores `JS::Call`'s return value and reports and
  clears a pending callback exception. Capture must precede this reporting:
  `runtime/engine.cpp:404–420`, `DumpPendingException`, steals the pending
  exception and builds its report with `ErrorReportBuilder::WithSideEffects`.
  A reporter can run application JavaScript and produce a later error.
* `runtime/event_loop.cpp:47–67`,
  `run_finalization_registry_cleanups`, has the same report-and-clear behavior.
  Its return value currently means **work ran**, not **work succeeded**. A false
  callback invocation without a pending exception is also not representable by
  an exception-value latch alone. Do not accidentally interpret this existing
  boolean as an error result when adding checkpoints.
* `runtime/engine.cpp:620`, `Engine::eval_toplevel`, ignores the return value of
  `run_event_loop`. It must propagate failure before its TLA check, reporting,
  GC, or cleanup drain can replace or clear the restored exception.
* `runtime/event_loop.cpp:151–162`,
  `EventLoop::drain_finalization_registry_cleanups`, returns success immediately
  when no cleanup ran and after its 16-round bound. Both exits need the strict
  checkpoint. The normal loop's cleanup-work `continue` likewise needs the
  checkpoint before it bypasses the interest-complete path.
* `EventTarget::inner_invoke`'s `handleEvent` property-get failure at
  `event-target.cpp:557–559` currently returns directly instead of using the
  callback reporting path. This is a distinct pre-existing behavior; do not
  silently claim all listener-operation failures have identical reporting
  semantics after changing only the `JS::Call` branch.

## Rooting and first-error contract

Use a `JS::PersistentRootedValue` initialized once with the engine's context in
`EventLoop::init`, plus an independent presence boolean. `undefined`, `null`,
primitives, and arbitrary objects are valid thrown values; the value itself
cannot indicate absence. The persistent root traces and updates an object or
string across moving collections without a new custom trace hook. Do not retain
a raw `JS::Value` in an untraced C++ field.

Capture only when no earlier value has been latched. Check
`JS_IsExceptionPending` before retrieving the pending value; check
`JS_GetPendingException`'s boolean result before marking a successful capture.
The pinned `js/Exception.h` declares retrieval as fallible, and the pinned
`js/src/jsapi.cpp:4046–4053` delegates to `cx->getPendingException`. A separate
capture/invocation-failure flag must keep the operation fatal if retrieval fails
or invocation fails without a retrievable pending exception. Reporting and
clearing must not turn either failure into success.

The final parent-reviewed policy preserves any already pending direct exception
at a checkpoint. The first event error wins among successfully latched event
records; an additional event error cannot overwrite it. A pending direct
exception is not cleared or replaced merely because an event value was latched. No
inspection of an application's `code`, `message`, `then`, or property getters is
needed to capture the value. In particular, an application cannot cancel the
policy by placing `dispatchEvent` inside `try`/`catch`: ordinary listener throws
are reported by dispatch rather than synchronously rethrown to that caller.

Restore from the rooted value before releasing that root's reference. The actual
public API supports
`JS_SetPendingException(cx, value, JS::ExceptionStackBehavior::DoNotCapture)`;
this avoids synthesizing a new stack-capture operation during the checkpoint.
A value-only latch preserves thrown-value identity and an Error object's own
properties, but does not preserve the separate optional saved exception stack.
If that separate stack is required, it needs its own rooted storage and an
explicit `GetPendingExceptionStack`/`SetPendingExceptionStack` design.

Clear the presence/failure flags and assign the rooted slot `UndefinedValue()`
when the saved state is consumed or reset. Do **not** call the persistent root's
`reset()` as an ordinary value clear: pinned `RootingAPI.h:1649–1653` removes it
from the runtime's persistent-root list.

## Required checkpoint ordering

The following are proposed embedding checkpoints, not new existing APIs:

1. At `run_event_loop` entry, before running jobs. A deployed ComponentizeJS
   export may already have dispatched an event synchronously before the bridge
   calls this method.
2. Immediately after `js::RunJobs`, before cleanup execution or host task
   selection, honoring any pending or latched failure.
3. Immediately after a cleanup batch, whether it ran work or not; do this
   before the cleanup-work `continue` or interest-complete success return.
4. After task invocation, before another iteration can overwrite a direct task
   failure. A false task result remains failure even without a pending value.
5. At cleanup-drain entry, after each cleanup batch and subsequent job drain,
   before the no-work success return, and before the 16-round success return.
6. In `eval_toplevel`, honor the event-loop boolean and add the final strict
   checkpoint after pre-snapshot cleanup drainage, before TLA/policy checks can
   replace a saved first error and before success is returned.
7. At the guaranteed `finish_pre_initialization` boundary before changing state
   to `Initialized`. The constructor runs `run_initialization_script` before
   its optional content-script branches. With no content script, no
   `eval_toplevel` checkpoint runs; the void finish method can use the existing
   engine-abort contract if a strict error remains. An equivalent guaranteed
   constructor/Wizer boundary is also possible.

All failures leaving `run_event_loop` must restore `event_loop_running=false`;
an early added return cannot strand that flag. Keep record/clear operations
inside the synchronous EventTarget reporting path so later listeners still run
and normal event flag cleanup still occurs. The strict failure is delivered at
the embedding checkpoint rather than by changing dispatch into an immediate
listener-error throw.

## Reset and reuse

`EventLoop::reset` currently cancels tasks and clears interest; it does not clear
the finalization-registry cleanup queue. `Engine::reset` calls that reset twice
around the timer reset and then runs GC, which can queue additional cleanups.
Clearing the latch during reset prevents its rooted value leaking into later
work, but does not by itself establish request isolation, drain finalizers, or
make an instance reusable after a failed export. Keep the fatal/discard policy
explicit. Do not clear a latched error merely when a successful export starts:
that would erase an earlier unreported failure.

The normal ComponentizeJS `call()` path in the pinned embedding always obtains
an asynchronous Promise and then calls `Engine::run_event_loop`, aborting when
it returns false (`embedding.cpp:270–313` in the v7 external source). This makes
the event-loop checkpoint relevant to ordinary deployed exports. Independent
embedders that dispatch JavaScript without driving this method need their own
explicit checkpoint contract.

## Validation required after implementation

Retain the existing six initializer vectors. Add first-value identity cases
(`throw undefined`, object sentinel, multiple listeners, nested dispatch), an
earlier event error followed by a later TLA/direct error, and caught controls.
Check event callback failure from a Promise job and from a finalizer, including
a finalizer which successfully returns after its nested dispatch. Check a
throwing diagnostic `message` getter and callback-failure-without-pending paths
if the embedding can exercise those through supported APIs. Exercise a moving
GC while a thrown object is only held by the persistent latch. Deployed tests
must call a real exported function, observe failure, and discard that instance.
Profile-disabled tests must retain the old behavior. Audit final emitted imports;
the proposed root, flags, capture, and checkpoints require no host capability or
WIT interface.

## Reviewed input hashes

| File | SHA-256 |
| --- | --- |
| `runtime/event_loop.h` | `242d6d36cb55a542f46d0403ebadc7872d5eda239f0e6e05d4b6062da78383be` |
| `runtime/event_loop.cpp` | `93b77b3268b0cb8f2f44a5711f33b236a8a11037f19ed96f0fbfbb330b064214` |
| `runtime/engine.cpp` | `6c4a750e1f71b7cf3e0f60eafa6a071481982fa6e6861d4249abda777f081120` |
| `include/extension-api.h` | `d743a7fcc0566eb85f382fec2f82b4c768a1043ca29b26e9fdef6f576e6789b8` |
| `builtins/web/event/event-target.cpp` | `d019ceba883efdd4dbf6be4e3edf3944081175978fb648ad90a43037b360c04c` |
| `cmake/builtins.cmake` | `6b78a1063a38517987f9b71b91a599843ec2f5e38439c38044ab2960279b87c4` |
