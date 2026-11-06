#include "event_loop.h"
#ifdef NODE_COMPAT_LIFECYCLE_DIAGNOSTICS
#include "clock-lifecycle-diagnostics.h"
namespace lifecycle_diag = diagnostics::clock_lifecycle;
#endif

#include "host_api.h"
#include "jsapi.h"
#include "jsfriendapi.h"
#include "js/GCVector.h"
#include "js/Utility.h"

#include <iostream>
#include <print>
#include <vector>

// A native RefPtr alone is not a JS root after detaching from TaskQueue.
// Each local root traces the actual task throughout run/cancel, including nesting.
struct TracedAsyncTask {
  RefPtr<api::AsyncTask> task;
  void trace(JSTracer *trc) {
    if (task) task->trace(trc);
  }
};

struct TaskQueue {
  std::vector<RefPtr<api::AsyncTask>> tasks;
  int interest_cnt = 0;
  bool event_loop_running = false;
#ifdef NODE_COMPAT_INTERNAL_TICKS
  core::InternalTickQueue ticks;
#endif

  void trace(JSTracer *trc) {
    for (const auto &task : tasks) {
      task->trace(trc);
    }
#ifdef NODE_COMPAT_INTERNAL_TICKS
    ticks.trace(trc);
#endif
  }
};

static PersistentRooted<TaskQueue> queue;

#ifdef NODE_COMPAT_STRICT_INITIALIZATION
// EventLoop::init runs before builtin installation/application evaluation.
// Keep a separate flag: undefined is a valid thrown value.
static JS::PersistentRootedValue first_uncaught_event_exception;
static bool has_uncaught_event_exception = false;
static bool uncaught_event_exception_capture_failed = false;
static bool uncaught_event_invocation_failed = false;
#endif

// SpiderMonkey hands the embedding one cleanup function per FinalizationRegistry that has
// records of dead targets, and leaves calling it to the embedding (HTML's
// HostEnqueueFinalizationRegistryCleanupJob). The functions are queued here and run by the event
// loop, as a task after the microtask checkpoint.
using CleanupFunctions = JS::GCVector<JSFunction *, 0, js::SystemAllocPolicy>;
static PersistentRooted<CleanupFunctions> finalization_registry_cleanups;

// Called during GC, so this must not trigger another collection: it only appends to the queue.
// An append can only fail on allocation failure, which is fatal, as in SpiderMonkey's shell.
static void queue_finalization_registry_cleanup(JSFunction *do_cleanup,
                                                JSObject * /*incumbent_global*/,
                                                void * /*data*/) {
  js::AutoEnterOOMUnsafeRegion oom_unsafe;
  if (!finalization_registry_cleanups.get().append(do_cleanup)) {
    oom_unsafe.crash("queue_finalization_registry_cleanup");
  }
}

// Calls every queued cleanup function and returns whether any ran. An exception thrown by a
// callback is reported and cleared, and does not fail the event loop, as in a browser.
static bool run_finalization_registry_cleanups(api::Engine *engine) {
  if (finalization_registry_cleanups.get().empty()) {
    return false;
  }
  JSContext *cx = engine->cx();
  JS::Rooted<CleanupFunctions> cleanups(cx);
  std::swap(cleanups.get(), finalization_registry_cleanups.get());
  JS::RootedFunction cleanup(cx);
  JS::RootedValue rval(cx);
  for (JSFunction *fn : cleanups) {
    cleanup = fn;
    JS::RootedObject cleanup_obj(cx, JS_GetFunctionObject(cleanup));
    JS::ExposeObjectToActiveJS(cleanup_obj);
    JSAutoRealm ar(cx, cleanup_obj);
    if (!JS_CallFunction(cx, nullptr, cleanup, JS::HandleValueArray::empty(), &rval)) {
#ifdef NODE_COMPAT_STRICT_INITIALIZATION
      // Treat a directly thrown cleanup error like an uncaught event callback.
      // Do not report-and-clear before retaining the original thrown value.
      if (JS_IsExceptionPending(cx)) {
        if (!core::EventLoop::record_pending_event_exception(cx)) {
          break;
        }
      } else {
        core::EventLoop::record_failed_event_invocation();
        break;
      }
#else
      api::Engine::dump_pending_exception("running a FinalizationRegistry callback");
      JS_ClearPendingException(cx);
#endif
    }
  }
  return true;
}

namespace core {

#ifdef NODE_COMPAT_STRICT_INITIALIZATION
bool EventLoop::record_pending_event_exception(JSContext *cx) {
  MOZ_ASSERT(JS_IsExceptionPending(cx));
  if (uncaught_event_exception_capture_failed || uncaught_event_invocation_failed) {
    return false;
  }
  if (!has_uncaught_event_exception) {
    JS::RootedValue exception(cx);
    if (!JS_GetPendingException(cx, &exception)) {
      uncaught_event_exception_capture_failed = true;
      return false;
    }
    first_uncaught_event_exception = exception;
    has_uncaught_event_exception = true;
  }
  JS_ClearPendingException(cx);
  return true;
}

bool EventLoop::take_pending_event_exception(JSContext *cx) {
  // Do not replace an existing direct failure with a previously latched event.
  if (JS_IsExceptionPending(cx)) {
    return false;
  }
  if (uncaught_event_exception_capture_failed) {
    // Application code might have caught the capture failure while unwinding.
    // It cannot make a failed policy capture silently successful.
    JS_ReportErrorASCII(cx, "ERR_SM_NODE_EVENT_EXCEPTION_CAPTURE: unable to retain an uncaught event exception");
    return false;
  }
  if (uncaught_event_invocation_failed) {
    JS_ReportErrorASCII(cx, "ERR_SM_NODE_EVENT_INVOCATION: event callback failed without a pending exception");
    return false;
  }
  if (!has_uncaught_event_exception) {
    return true;
  }
  JS::RootedValue exception(cx, first_uncaught_event_exception);
  first_uncaught_event_exception = JS::UndefinedValue();
  has_uncaught_event_exception = false;
  JS_SetPendingException(cx, exception, JS::ExceptionStackBehavior::DoNotCapture);
  return false;
}

void EventLoop::record_failed_event_invocation() {
  if (!has_uncaught_event_exception && !uncaught_event_exception_capture_failed) {
    uncaught_event_invocation_failed = true;
  }
}

bool EventLoop::event_exception_policy_failed() {
  return uncaught_event_exception_capture_failed || uncaught_event_invocation_failed;
}
#endif

void EventLoop::queue_async_task(const RefPtr<api::AsyncTask>& task) {
  MOZ_ASSERT(task);
  queue.get().tasks.emplace_back(task);
#ifdef NODE_COMPAT_LIFECYCLE_DIAGNOSTICS
  lifecycle_diag::count(lifecycle_diag::Counter::QueueEnqueue);
#endif
}

bool EventLoop::cancel_async_task(api::Engine *engine, const RefPtr<api::AsyncTask>& task) {
  auto *const tasks = &queue.get().tasks;
  for (auto it = tasks->begin(); it != tasks->end(); ++it) {
    if (*it == task) {
      JS::Rooted<TracedAsyncTask> retiring(engine->cx());
      retiring.get().task = task; // copy before erase, including an aliased RefPtr argument
      tasks->erase(it);
#ifdef NODE_COMPAT_LIFECYCLE_DIAGNOSTICS
      lifecycle_diag::count(lifecycle_diag::Counter::QueueDetachCancel);
#endif
      (void)retiring.get().task->cancel(engine);
      return true;
    }
  }
  return false;
}

bool EventLoop::has_pending_async_tasks() { return !queue.get().tasks.empty(); }

void EventLoop::incr_event_loop_interest() {
  queue.get().interest_cnt++;
#ifdef NODE_COMPAT_LIFECYCLE_DIAGNOSTICS
  lifecycle_diag::count(lifecycle_diag::Counter::InterestIncr);
#endif
}

void EventLoop::decr_event_loop_interest() {
  MOZ_ASSERT(queue.get().interest_cnt > 0);
  queue.get().interest_cnt--;
#ifdef NODE_COMPAT_LIFECYCLE_DIAGNOSTICS
  lifecycle_diag::count(lifecycle_diag::Counter::InterestDecr);
#endif
}

inline bool interest_complete() { return queue.get().interest_cnt == 0; }

inline void exit_event_loop(bool success = false) {
#ifdef NODE_COMPAT_INTERNAL_TICKS
  if (!success) queue.get().ticks.discard();
#endif
  queue.get().event_loop_running = false;
}

#ifdef NODE_COMPAT_INTERNAL_TICKS
static bool enqueue_internal_tick(JSContext* cx, unsigned argc, JS::Value* vp) {
  return queue.get().ticks.enqueue(cx, JS::CallArgsFromVp(argc, vp));
}
JSObject* EventLoop::create_internal_next_tick(JSContext* cx) {
  JS::RootedFunction function(cx, JS_NewFunction(cx, enqueue_internal_tick, 1, 0, "nextTick"));
  return function ? JS_GetFunctionObject(function) : nullptr;
}
bool EventLoop::internal_tick_checkpoint_active() { return queue.get().ticks.checkpoint_running(); }
bool EventLoop::require_internal_ticks_quiescent(JSContext* cx) {
  if (queue.get().event_loop_running || !queue.get().ticks.empty_and_inactive())
    return InternalTickQueue::fail(cx, JSEXN_ERR, "ERR_SM_NODE_SCHEDULER_STATE", "tick FIFO must be empty and inactive at this boundary");
  return true;
}
bool EventLoop::require_internal_tick_reset_allowed(JSContext* cx) {
  if (queue.get().event_loop_running || queue.get().ticks.checkpoint_running())
    return InternalTickQueue::fail(cx, JSEXN_ERR, "ERR_SM_NODE_SCHEDULER_REENTRY", "cannot reset an active tick/task checkpoint");
  return true;
}
bool EventLoop::run_internal_tick_checkpoint(JSContext* cx, TickCheckpointOrigin origin) {
  return queue.get().ticks.checkpoint(cx, origin);
}
#endif

bool EventLoop::run_event_loop(api::Engine *engine, double total_compute) {
#ifdef NODE_COMPAT_INTERNAL_TICKS
  return run_event_loop(engine, total_compute, TickCheckpointOrigin::TaskOrExport);
}
bool EventLoop::run_event_loop(api::Engine *engine, double total_compute, TickCheckpointOrigin origin) {
  if (queue.get().event_loop_running || queue.get().ticks.checkpoint_running())
    return InternalTickQueue::fail(engine->cx(), JSEXN_ERR, "ERR_SM_NODE_SCHEDULER_REENTRY", "event loop is already running");
#else
  if (queue.get().event_loop_running) {
    std::print(stderr, "cannot run event loop as it is already running");
    return false;
  }
#endif
  queue.get().event_loop_running = true;
  JSContext *cx = engine->cx();

  while (true) {
    // Complete existing Promise checkpoint, optionally bracketed by guest ticks.
#ifdef NODE_COMPAT_INTERNAL_TICKS
    if (!run_internal_tick_checkpoint(cx, origin)) { exit_event_loop(); return false; }
    origin = TickCheckpointOrigin::TaskOrExport;
#else
    js::RunJobs(cx);
#endif

#ifdef NODE_COMPAT_STRICT_INITIALIZATION
    if (!take_pending_event_exception(cx)) {
      exit_event_loop();
      return false;
    }
#endif
    if (JS_IsExceptionPending(cx)) {
      exit_event_loop();
      return false;
    }

    // Once the microtasks are done, run the FinalizationRegistry cleanups that a collection
    // queued, then go round again for the microtasks they queued.
    bool ran_cleanups = run_finalization_registry_cleanups(engine);
#ifdef NODE_COMPAT_STRICT_INITIALIZATION
    if (!take_pending_event_exception(cx)) {
      exit_event_loop();
      return false;
    }
#endif
    if (ran_cleanups) {
#ifdef NODE_COMPAT_INTERNAL_TICKS
      origin = TickCheckpointOrigin::FinalizerBatch;
#endif
      continue;
    }

    // if there is no interest in the event loop at all, just run one tick
    if (interest_complete()) {
      exit_event_loop(true);
      return true;
    }

    auto *const tasks = &queue.get().tasks;
    size_t tasks_size = tasks->size();
    if (tasks_size == 0) {
      exit_event_loop();
      MOZ_ASSERT(!interest_complete());
      return false;
    }

    // Select the next task to run according to event-loop semantics of oldest-first.
    auto selected = api::AsyncTask::select(*tasks);
    if (!selected) {
      // Pruning invalidated tasks can empty the queue after the earlier test.
      // Recheck jobs, failures and interest through the ordinary loop boundary.
      continue;
    }
    const size_t task_idx = *selected;

    JS::Rooted<TracedAsyncTask> running(cx);
    running.get().task = tasks->at(task_idx);
    tasks->erase(tasks->begin() + task_idx);
#ifdef NODE_COMPAT_LIFECYCLE_DIAGNOSTICS
    lifecycle_diag::count(lifecycle_diag::Counter::QueueDetachRun);
#endif
    bool success = running.get().task->run(engine);
    if (!success) {
      exit_event_loop();
      return false;
    }
  }
}

bool EventLoop::drain_finalization_registry_cleanups(api::Engine *engine) {
  JSContext *cx = engine->cx();
#ifdef NODE_COMPAT_STRICT_INITIALIZATION
  if (!take_pending_event_exception(cx)) {
    return false;
  }
#endif
  for (unsigned round = 0; round < MAX_CLEANUP_DRAIN_ROUNDS; round++) {
    bool ran_cleanups = run_finalization_registry_cleanups(engine);
#ifdef NODE_COMPAT_STRICT_INITIALIZATION
    if (!take_pending_event_exception(cx)) {
      return false;
    }
#endif
    if (!ran_cleanups) {
      return true;
    }
#ifdef NODE_COMPAT_INTERNAL_TICKS
    // Existing strict cleanup-error check ABOVE remains before dispatch.
    if (!run_internal_tick_checkpoint(cx, TickCheckpointOrigin::FinalizerBatch)) return false;
#else
    js::RunJobs(cx);
#endif
#ifdef NODE_COMPAT_STRICT_INITIALIZATION
    if (!take_pending_event_exception(cx)) {
      return false;
    }
#endif
    if (JS_IsExceptionPending(cx)) {
      return false;
    }
  }
#ifdef NODE_COMPAT_STRICT_INITIALIZATION
  return take_pending_event_exception(cx);
#else
  return true;
#endif
}

void EventLoop::init(JSContext *cx) {
  queue.init(cx);
#ifdef NODE_COMPAT_STRICT_INITIALIZATION
  first_uncaught_event_exception.init(cx, JS::UndefinedValue());
  has_uncaught_event_exception = false;
  uncaught_event_exception_capture_failed = false;
  uncaught_event_invocation_failed = false;
#endif
  finalization_registry_cleanups.init(cx);
  JS::SetHostCleanupFinalizationRegistryCallback(cx, queue_finalization_registry_cleanup, nullptr);
}

void EventLoop::reset(api::Engine *engine) {
#ifdef NODE_COMPAT_INTERNAL_TICKS
  if (!require_internal_tick_reset_allowed(engine->cx())) {
    engine->abort("resetting an active internal tick checkpoint");
    return;
  }
#endif
  auto &q = queue.get();
  for (const auto& task : q.tasks) {
    task->cancel(engine);
  }
  q.tasks.clear();
  q.interest_cnt = 0;
#ifdef NODE_COMPAT_INTERNAL_TICKS
  q.ticks.reset_storage();
#endif
#ifdef NODE_COMPAT_STRICT_INITIALIZATION
  // Assignment keeps the PersistentRooted registered for subsequent entries.
  first_uncaught_event_exception = JS::UndefinedValue();
  has_uncaught_event_exception = false;
  uncaught_event_exception_capture_failed = false;
  uncaught_event_invocation_failed = false;
#endif
}

} // namespace core
#ifdef NODE_COMPAT_LIFECYCLE_DIAGNOSTICS
namespace diagnostics::clock_lifecycle {
RuntimeCounts runtime_counts() {
  return {queue.get().tasks.size(), queue.get().interest_cnt,
    queue.get().event_loop_running, timer_registry_size(), immediate_cache_owned()};
}
} // namespace diagnostics::clock_lifecycle
#endif
#ifdef NODE_COMPAT_LIFECYCLE_DIAGNOSTICS
namespace diagnostics::clock_lifecycle {
namespace {
// A private native sentinel task owns NO JS edge or WASI pollable. It is placed
// in the REAL Engine queue, then invalidated before the real selector runs once.
class InvalidSelectorProbeTask final : public api::AsyncTask {
public:
  InvalidSelectorProbeTask() {
    handle_ = IMMEDIATE_TASK_HANDLE;
    add_checked(state.selectorProbe.constructed);
  }
  ~InvalidSelectorProbeTask() override { add_checked(state.selectorProbe.destroyed); }
  void invalidate() {
    if (handle_ != IMMEDIATE_TASK_HANDLE) state.invariantViolation = true;
    handle_ = INVALID_POLLABLE_HANDLE;
    add_checked(state.selectorProbe.invalidated);
  }
  bool run(api::Engine*) override {
    add_checked(state.selectorProbe.unexpectedRun); state.invariantViolation = true; return false;
  }
  bool cancel(api::Engine*) override {
    add_checked(state.selectorProbe.unexpectedCancel); state.invariantViolation = true; return false;
  }
  void trace(JSTracer*) override {} // deliberately contains no JS-managed value
};
bool probe_error(api::Engine* engine, const char* message) {
  JS_ReportErrorASCII(engine->cx(), "%s", message); return false;
}
bool room(std::uint64_t value, std::uint64_t amount) {
  return amount <= std::numeric_limits<std::uint64_t>::max() - value;
}
} // namespace
bool probe_all_invalid_selector(api::Engine* engine, std::uint32_t count,
                                SelectorProbeResult& result) {
  if (engine->state() != api::EngineState::Initialized || count == 0 || count > MaxInvalidSelectorTasks)
    return probe_error(engine, "PRIVATE_SELECTOR_V2: ordinary call and count1..8 required");
  const auto initial = runtime_counts();
  const auto native_clock = native_clock_state();
  if (native_clock.overflow || native_clock.adjustmentOverflow || state.overflow || state.invariantViolation || initial.queued != 0 || initial.interest != 1 ||
      initial.loopRunning || initial.timerRegistry != 0)
    return probe_error(engine, "PRIVATE_SELECTOR_V2: inactive empty queue and sole current-export interest required");
#ifdef NODE_COMPAT_INTERNAL_TICKS
  if (!core::EventLoop::require_internal_ticks_quiescent(engine->cx())) return false;
#endif
  for (const auto which : {Counter::QueueEnqueue, Counter::PrunedInvalid})
    if (!room(state.counts[static_cast<std::size_t>(which)], count))
      return probe_error(engine, "PRIVATE_SELECTOR_V2: cumulative queue counter capacity refused");
  for (const auto which : {Counter::SelectorCall, Counter::SelectorEmpty})
    if (!room(state.counts[static_cast<std::size_t>(which)], 1))
      return probe_error(engine, "PRIVATE_SELECTOR_V2: selector counter capacity refused");
  if (!room(state.selectorProbe.constructed, count) || !room(state.selectorProbe.invalidated, count) ||
      !room(state.selectorProbe.destroyed, count))
    return probe_error(engine, "PRIVATE_SELECTOR_V2: probe counter capacity refused");
  result.requested = count; result.before = capture(); result.probeBefore = state.selectorProbe;
  // Allocate the bounded cut before mutating the real queue. Ordinary allocation
  // failure remains an error; no fault injection or reset/repair path is added.
  std::array<RefPtr<api::AsyncTask>, MaxInvalidSelectorTasks> owners{};
  for (std::uint32_t i = 0; i < count; ++i) {
    owners[i] = js_new<InvalidSelectorProbeTask>();
    if (!owners[i]) {
      state.invariantViolation = true; JS_ReportOutOfMemory(engine->cx()); return false;
    }
  }
  for (std::uint32_t i = 0; i < count; ++i) engine->queue_async_task(owners[i]);
  for (std::uint32_t i = 0; i < count; ++i)
    static_cast<InvalidSelectorProbeTask*>(owners[i].get())->invalidate();
  // The owning queue is sole owner during erase; destructor counts are real.
  for (auto& owner : owners) owner = nullptr;
  result.queued = capture();
  const auto selected = api::AsyncTask::select(queue.get().tasks); // ACTUAL owning queue, not a test vector
  result.selectedNone = !selected.has_value(); result.after = capture();
  result.probeAfter = state.selectorProbe;
  const auto delta = [&](Counter c) {
    const auto i = static_cast<std::size_t>(c);
    return result.after.history.counts[i] - result.before.history.counts[i];
  };
  bool valid = result.selectedNone && result.queued.current.queued == count &&
    result.after.current.queued == 0 && result.after.current.interest == initial.interest &&
    !result.after.current.loopRunning && result.after.current.timerRegistry == 0 &&
    result.after.current.immediateCacheOwned == initial.immediateCacheOwned &&
    delta(Counter::QueueEnqueue) == count && delta(Counter::PrunedInvalid) == count &&
    delta(Counter::SelectorCall) == 1 && delta(Counter::SelectorEmpty) == 1 &&
    delta(Counter::PollCall) == 0 && delta(Counter::EmptyPollAttempt) == 0 &&
    delta(Counter::QueueDetachRun) == 0 && delta(Counter::QueueDetachCancel) == 0 &&
    delta(Counter::InterestIncr) == 0 && delta(Counter::InterestDecr) == 0 &&
    result.probeAfter.constructed - result.probeBefore.constructed == count &&
    result.probeAfter.invalidated - result.probeBefore.invalidated == count &&
    result.probeAfter.destroyed - result.probeBefore.destroyed == count &&
    result.probeAfter.unexpectedRun == result.probeBefore.unexpectedRun &&
    result.probeAfter.unexpectedCancel == result.probeBefore.unexpectedCancel &&
    !state.overflow && !state.invariantViolation;
  if (!valid) {
    state.invariantViolation = true;
    return probe_error(engine, "PRIVATE_SELECTOR_V2: native selector invariant failed; instance unaccepted");
  }
  return true;
}
} // namespace diagnostics::clock_lifecycle
#endif
