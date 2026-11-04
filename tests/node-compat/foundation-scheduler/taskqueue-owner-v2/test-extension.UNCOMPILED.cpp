// UNAPPLIED / UNCOMPILED diagnostic guest builtin. NEVER a production module.
// Rooting is supplied by the existing TaskQueue trace and local Rooted values;
// there is no diagnostic global, custom host service, or extra persistent root.
#include "event_loop.h"
#include "extension-api.h"
#include "js/Array.h"
#include "js/CallAndConstruct.h"
#include "js/PropertyAndElement.h"
#include "js/ValueArray.h"
#include "js/TracingAPI.h"
#include "js/Utility.h"
#include "jsapi.h"

#ifndef NODE_COMPAT_INTERNAL_TICKS
#error "Diagnostic extension requires the reviewed private scheduler candidate"
#endif
namespace diagnostics::internal_ticks {
using namespace JS;
namespace {
// Diagnostic-only pending tasks are independently capped; no task-id map/root.
size_t diagnostic_pending_tasks = 0;
class BoundaryTask final : public api::AsyncTask {
  Heap<JSObject*> callback_;
  Heap<JSObject*> arguments_;
  uint32_t argc_;
  bool active_ = true;
  void finish(api::Engine* engine) {
    active_ = false; handle_ = INVALID_POLLABLE_HANDLE;
    callback_ = nullptr; arguments_ = nullptr;
    --diagnostic_pending_tasks;
    engine->decr_event_loop_interest();
  }
public:
  BoundaryTask(HandleObject callback, HandleObject arguments, uint32_t argc)
      : callback_(callback), arguments_(arguments), argc_(argc) { handle_ = IMMEDIATE_TASK_HANDLE; }
  bool run(api::Engine* engine) override {
    auto* cx = engine->cx();
    // The event loop removed this task before run(). Root first, with no JSAPI
    // allocation/callback between removal and these Rooted initializations.
    RootedObject callback(cx, callback_), arguments(cx, arguments_);
    finish(engine);
    RootedValueVector argv(cx);
    if (!argv.resize(argc_)) { JS_ReportOutOfMemory(cx); return false; }
    for (uint32_t i = 0; i < argc_; ++i)
      if (!JS_GetElement(cx, arguments, i, argv[i])) return false;
    JSAutoRealm realm(cx, callback);
    RootedValue ignored(cx);
    return Call(cx, UndefinedHandleValue, callback, argv, &ignored);
  }
  bool cancel(api::Engine* engine) override {
    if (!active_) return false;
    finish(engine);
    return true;
  }
  void trace(JSTracer* trc) override {
    TraceEdge(trc, &callback_, "diagnostic boundary callback");
    TraceEdge(trc, &arguments_, "diagnostic boundary arguments");
  }
};
static bool schedule_task(JSContext* cx, unsigned argc, Value* vp) {
  CallArgs args = CallArgsFromVp(argc, vp);
  if (argc == 0 || !args[0].isObject() || !IsCallable(&args[0].toObject()))
    return core::InternalTickQueue::fail(cx, JSEXN_TYPEERR, "ERR_INVALID_ARG_TYPE", "callback must be callable");
  if (argc-1 > core::InternalTickQueue::MaxArgumentsPerTick || diagnostic_pending_tasks == 16)
    return core::InternalTickQueue::fail(cx, JSEXN_RANGEERR, "ERR_SM_NODE_SCHEDULER_LIMIT", "diagnostic task budget exceeded");
  RootedObject callback(cx, &args[0].toObject());
  RootedObject arguments(cx, NewArrayObject(cx, HandleValueArray::subarray(args, 1, argc-1)));
  if (!arguments) return false;
  RefPtr<BoundaryTask> task = js_new<BoundaryTask>(callback, arguments, argc-1);
  if (!task) { JS_ReportOutOfMemory(cx); return false; }
  auto* engine = api::Engine::get(cx);
  ++diagnostic_pending_tasks;
  engine->incr_event_loop_interest();
  engine->queue_async_task(task); // Existing void API; no recoverable allocator-failure claim.
  args.rval().setUndefined();
  return true;
}
static bool attempt_reentry(JSContext* cx, unsigned argc, Value* vp) {
  // Only attempt the real Engine entry while already inside its checkpoint.
  // Never run RunJobs from a currently executing module-evaluation body.
  if (!core::EventLoop::internal_tick_checkpoint_active())
    return core::InternalTickQueue::fail(cx, JSEXN_ERR, "ERR_SM_NODE_SCHEDULER_STATE", "diagnostic reentry requires an active checkpoint");
  return api::Engine::get(cx)->run_event_loop(); // Must fail with own REENTRY code.
}
static bool check_reset_guard(JSContext* cx, unsigned argc, Value* vp) {
  CallArgs args = CallArgsFromVp(argc, vp);
  if (!core::EventLoop::require_internal_tick_reset_allowed(cx)) return false;
  args.rval().setUndefined();
  return true;
}
const JSFunctionSpec functions[] = {
  JS_FN("scheduleTask", schedule_task, 1, 0),
  JS_FN("attemptReentry", attempt_reentry, 0, 0),
  JS_FN("checkResetGuard", check_reset_guard, 0, 0), JS_FS_END,
};
} // namespace
bool install(api::Engine* engine) {
  auto* cx = engine->cx();
  JSAutoRealm realm(cx, engine->global());
  RootedObject record(cx, JS_NewPlainObject(cx));
  RootedObject next_tick(cx, core::EventLoop::create_internal_next_tick(cx));
  if (!record || !next_tick || !JS_DefineFunctions(cx, record, functions) ||
      !JS_DefineProperty(cx, record, "nextTick", next_tick, JSPROP_ENUMERATE) ||
      !JS_DefineProperty(cx, record, "default", record, JSPROP_ENUMERATE)) return false;
  RootedValue module(cx, ObjectValue(*record));
  if (!engine->define_builtin_module("starling:test-internal-ticks", module)) return false;
  // Separate finite initializer-realm record: same queue, a distinct callable
  // in the actual INIT realm. No new global and no cross-realm callback bypass.
  JSAutoRealm initializer_realm(cx, engine->init_script_global());
  RootedObject initializer_record(cx, JS_NewPlainObject(cx));
  RootedObject initializer_tick(cx, core::EventLoop::create_internal_next_tick(cx));
  if (!initializer_record || !initializer_tick ||
      !JS_DefineProperty(cx, initializer_record, "nextTick", initializer_tick, JSPROP_ENUMERATE) ||
      !JS_DefineProperty(cx, initializer_record, "default", initializer_record, JSPROP_ENUMERATE)) return false;
  RootedValue initializer_module(cx, ObjectValue(*initializer_record));
  return engine->define_builtin_module("starling:test-initializer-ticks", initializer_module);
}
} // namespace diagnostics::internal_ticks
