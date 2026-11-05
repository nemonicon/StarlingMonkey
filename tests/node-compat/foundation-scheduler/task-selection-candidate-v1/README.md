# All-invalid task selection: unapplied source proposal

The real api::AsyncTask::select erases invalid pollables after the event loop's
nonempty test. If every task is invalid, the current code calls poll_handles
with an empty list and assumes a nonempty ready result. This source defect is
already documented in reset-design-v1; no unsafe original guest is run here.

This three-file patch is based on the actual resource normal-OFF frozen source
(frozen-artifact review80b7174e), preserving the strong task roots and timer patch.
The existing select method now returns std::optional<size_t> and returns nullopt
when pruning empties the queue. Its only production caller, EventLoop::run_event_loop,
checks that result before indexing and continues through the normal job/failure/
interest boundary. With interest still outstanding and no work, the existing
no-task failure remains. The implementation introduces no new embedding method,
Node export or host capability. The changed C++ return contract requires a full
rebuild of native dependents; it is not ABI-compatible with existing engines.

Actual checks:

- All three source derivations reverse exactly against the frozen originals.
- Twelve standalone host-model cases execute source-extracted selectors with
  instrumented task/poll types: empty/all-invalid, survivor order, oldest-ready
  selection, immediate-first, mixed readiness and cached-pollable reuse. The
  original algorithm reaches a controlled empty-poll exception in that model;
  the real baseline poll function or guest is never executed.
- Two actual WASI SDK30/LLVM21.1.4 frontend calls finish0 with empty streams,
  using the real normal resource compile rows and an explicit three-file VFS
  overlay.1,031 dependency paths and the real metadata/database/compiler inputs
  are recorded. No object, engine, component or linked artifact is produced.

The standalone model does not establish SpiderMonkey rooting, task destructor
behavior, JS exceptions, interest release or WASI runtime behavior. The frontend
checks establish only compilation. This packet remains unapplied and has no
independent source review or runtime/adoption authority.

Next gates: independent source review; a distinct integration generation with
the complete342-source manifest; fresh normal build/freeze/pins/component; a
reviewed private task fixture that invalidates all handles while releasing its
owned interest and verifies continuation without an empty host poll. Also cover
surviving FIFO tasks, still-unaccounted interest failure and ordinary timer
regressions on real components and stock hosts. Do not use old unsafe reset or
fault hooks. The cached immediate pollable lifetime, fallible enqueue, HTTP/
stream cancellation, bounded jobs, reset/reuse and ALS remain unresolved.
