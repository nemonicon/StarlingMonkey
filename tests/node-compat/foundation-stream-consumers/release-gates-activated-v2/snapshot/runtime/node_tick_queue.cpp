// UNAPPLIED, UNCOMPILED proposal. No additional PersistentRooted/static queue.
#include "node_tick_queue.h"
#include "event_loop.h"
#include "js/Array.h"
#include "js/CallAndConstruct.h"
#include "js/ColumnNumber.h"
#include "js/ErrorReport.h"
#include "js/PropertyAndElement.h"
#include "js/Realm.h"
#include "js/ValueArray.h"
#include "js/TracingAPI.h"
#include "jsapi.h"
#include "jsfriendapi.h"

namespace core {
using namespace JS;
void InternalTickQueue::Tick::trace(JSTracer* trc) {
  TraceEdge(trc, &callback, "internal tick callback");
  TraceEdge(trc, &arguments, "internal tick private argument array");
}

bool InternalTickQueue::fail(JSContext* cx, JSExnType type, const char* code, const char* text) {
  RootedString message(cx, JS_NewStringCopyZ(cx, text));
  if (!message) return false;
  RootedString file(cx, JS_NewStringCopyZ(cx, "<internal-node-tick>"));
  if (!file) return false;
  Rooted<mozilla::Maybe<Value>> cause(cx, mozilla::Nothing());
  RootedValue error(cx);
  if (!CreateError(cx, type, nullptr, file, 0, ColumnNumberOneOrigin::fromZeroOrigin(0),
                   nullptr, message, cause, &error)) return false;
  RootedObject object(cx, &error.toObject());
  RootedString code_string(cx, JS_NewStringCopyZ(cx, code));
  if (!code_string || !JS_DefineProperty(cx, object, "code", code_string, JSPROP_ENUMERATE)) return false;
  JS_SetPendingException(cx, error, ExceptionStackBehavior::DoNotCapture);
  return false;
}

bool InternalTickQueue::enqueue(JSContext* cx, const CallArgs& args) {
  if (args.length() == 0 || !args[0].isObject() || !IsCallable(&args[0].toObject()))
    return fail(cx, JSEXN_TYPEERR, "ERR_INVALID_ARG_TYPE", "callback must be callable");
  RootedObject callback(cx, &args[0].toObject());
  if (GetObjectRealmOrNull(callback) != GetCurrentRealmOrNull(cx))
    return fail(cx, JSEXN_TYPEERR, "ERR_SM_NODE_UNSUPPORTED", "cross-realm tick callback is outside the private contract");
  const size_t argc = args.length() - 1;
  if (count_ >= MaxPending || argc > MaxArgumentsPerTick ||
      argc > MaxPendingArguments - argument_count_)
    return fail(cx, JSEXN_RANGEERR, "ERR_SM_NODE_SCHEDULER_LIMIT", "internal tick queue budget exceeded");
  if (slots_.empty() && !slots_.resize(MaxPending)) { JS_ReportOutOfMemory(cx); return false; }
  // CallArgs is rooted. Copy plain argument VALUES, without getter/coercion.
  // Allocating the private dense Array commits no entry until it succeeds.
  RootedObject arguments(cx, NewArrayObject(cx, HandleValueArray::subarray(args, 1, argc)));
  if (!arguments) return false;
  Tick& tick = slots_[(head_ + count_) % MaxPending];
  tick.callback = callback; tick.arguments = arguments; tick.argc = argc;
  ++count_; argument_count_ += argc;
  args.rval().setUndefined();
  return true;
}

void InternalTickQueue::discard() {
  for (auto& tick : slots_) { tick.callback = nullptr; tick.arguments = nullptr; tick.argc = 0; }
  head_ = count_ = argument_count_ = 0;
}
void InternalTickQueue::reset_storage() {
  MOZ_RELEASE_ASSERT(!checkpoint_running_);
  discard();
  slots_.clearAndFree();
}

bool InternalTickQueue::drain_ticks(JSContext* cx, size_t& executed) {
  while (count_) {
    if (executed == MaxCallbacksPerCheckpoint)
      return fail(cx, JSEXN_RANGEERR, "ERR_SM_NODE_SCHEDULER_LIMIT", "tick checkpoint work budget exceeded");
    Tick& tick = slots_[head_];
    RootedObject callback(cx, tick.callback), arguments(cx, tick.arguments);
    const uint32_t argc = tick.argc;
    RootedValueVector argv(cx);
    if (!argv.resize(argc)) { JS_ReportOutOfMemory(cx); return false; }
    for (uint32_t i = 0; i < argc; ++i)
      if (!JS_GetElement(cx, arguments, i, argv[i])) return false;
    // Everything needed by JS is rooted BEFORE removing the queue entry.
    argument_count_ -= argc;
    tick.callback = nullptr; tick.arguments = nullptr; tick.argc = 0;
    head_ = (head_ + 1) % MaxPending; --count_; ++executed;
    JSAutoRealm realm(cx, callback);
    RootedValue ignored(cx);
    if (!Call(cx, UndefinedHandleValue, callback, argv, &ignored)) return false;
    // Retained EventTarget errors stay subject to the EXISTING layered policy:
    // its latch is checked after the full Promise checkpoint, not per tick.
  }
  return true;
}

bool InternalTickQueue::checkpoint(JSContext* cx, TickCheckpointOrigin origin) {
  if (checkpoint_running_)
    return fail(cx, JSEXN_ERR, "ERR_SM_NODE_SCHEDULER_REENTRY", "internal checkpoint is already running");
  if (JS_IsExceptionPending(cx)) { discard(); return false; }
  checkpoint_running_ = true;
  struct Exit { bool& running; ~Exit() { running = false; } } exit{checkpoint_running_};
  size_t executed = 0;
  bool promise_first = origin == TickCheckpointOrigin::ModuleEvaluation;
  do {
    if (!promise_first && !drain_ticks(cx, executed)) { discard(); return false; }
    promise_first = false;
    // Preserve the existing COMPLETE job checkpoint, kept-object cleanup,
    // rejection tracking and job-error reporting. No individual-job interleave.
    js::RunJobs(cx);
#ifdef NODE_COMPAT_STRICT_INITIALIZATION
    if (!EventLoop::take_pending_event_exception(cx)) { discard(); return false; }
#endif
    if (JS_IsExceptionPending(cx)) { discard(); return false; }
  } while (count_);
  return true;
}
} // namespace core
