// SOURCE-ONLY PROPOSAL. Not compiled, linked, installed, or executed.
// Proposed private runtime source; no public process/module/global API.
// Future ALS resource capture is intentionally absent; see README.md.
#include "extension-api.h"
#include "event_loop.h"
#include "js/Array.h"
#include "js/CallAndConstruct.h"
#include "js/ColumnNumber.h"
#include "js/ErrorReport.h"
#include "js/GCVector.h"
#include "js/PropertyAndElement.h"
#include "js/Realm.h"
#include "js/ValueArray.h"
#include "jsfriendapi.h"

namespace proposed::internal_ticks {
using namespace JS;

enum class Origin { TaskOrExport, ClassicEvaluation, ModuleEvaluation, SnapshotBinding, FinalizerBatch };
constexpr size_t MaxPending = 4096;
constexpr size_t MaxArgumentsPerTick = 1024;
constexpr size_t MaxPendingArguments = 65536;
constexpr size_t MaxCallbacksPerCheckpoint = 65536;

struct Tick {
  Heap<JSObject*> callback{nullptr};
  Heap<JSObject*> arguments{nullptr}; // Private packed JS Array; never exposed.
  uint32_t argc = 0;
  void trace(JSTracer* trc) {
    TraceEdge(trc, &callback, "internal tick callback");
    TraceEdge(trc, &arguments, "internal tick arguments");
  }
};
struct Storage {
  GCVector<Tick, 0, js::SystemAllocPolicy> slots;
  size_t head = 0, count = 0, argument_count = 0;
  bool checkpoint_running = false;
  void trace(JSTracer* trc) { slots.trace(trc); }
};
static PersistentRooted<Storage> storage;

// Own code data property: no inherited Error.prototype.code setter invocation.
// Exact CreateError signature verified in SM147 ErrorReport.h; this template
// has NOT been compiled, including this exception-construction path.
static bool fail(JSContext* cx, JSExnType type, const char* code, const char* text) {
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

// Proposed call from EventLoop::init, before any application registration.
// Fixed ring backing is lazy, so selecting but not using it avoids that allocation.
void initialize(JSContext* cx) { storage.init(cx); }

static void discard() {
  auto& state = storage.get();
  for (auto& tick : state.slots) {
    tick.callback = nullptr; tick.arguments = nullptr; tick.argc = 0;
  }
  state.head = state.count = state.argument_count = 0;
}

// Proposed private native function supplied directly to an audited JS factory.
bool enqueue(JSContext* cx, unsigned argc, Value* vp) {
  CallArgs args = CallArgsFromVp(argc, vp);
  if (argc == 0 || !args[0].isObject() || !IsCallable(&args[0].toObject()))
    return fail(cx, JSEXN_TYPEERR, "ERR_INVALID_ARG_TYPE", "callback must be callable");
  RootedObject callback(cx, &args[0].toObject());
  if (GetObjectRealmOrNull(callback) != GetCurrentRealmOrNull(cx))
    return fail(cx, JSEXN_TYPEERR, "ERR_SM_NODE_UNSUPPORTED", "cross-realm tick callback is outside this profile");
  auto& state = storage.get();
  const size_t argument_count = argc - 1;
  if (state.count >= MaxPending || argument_count > MaxArgumentsPerTick ||
      argument_count > MaxPendingArguments - state.argument_count)
    return fail(cx, JSEXN_RANGEERR, "ERR_SM_NODE_SCHEDULER_LIMIT", "internal tick queue budget exceeded");
  if (state.slots.empty() && !state.slots.resize(MaxPending)) {
    JS_ReportOutOfMemory(cx); return false;
  }
  // CallArgs is rooted by SpiderMonkey. Array creation copies values without
  // invoking application getters. No queue entry is committed until it succeeds.
  RootedObject arguments(cx, NewArrayObject(cx, HandleValueArray::subarray(args, 1, argument_count)));
  if (!arguments) return false;
  Tick& tick = state.slots[(state.head + state.count) % MaxPending];
  tick.callback = callback; tick.arguments = arguments; tick.argc = argument_count;
  state.count++; state.argument_count += argument_count;
  args.rval().setUndefined();
  return true;
}

static bool exceptions_ok(JSContext* cx) {
#ifdef NODE_COMPAT_STRICT_INITIALIZATION
  if (!core::EventLoop::take_pending_event_exception(cx)) return false;
#endif
  return !JS_IsExceptionPending(cx);
}

static bool drain_ticks(JSContext* cx, size_t& executed) {
  auto& state = storage.get();
  while (state.count) {
    if (executed == MaxCallbacksPerCheckpoint)
      return fail(cx, JSEXN_RANGEERR, "ERR_SM_NODE_SCHEDULER_LIMIT", "tick checkpoint work budget exceeded");
    Tick& tick = state.slots[state.head];
    RootedObject callback(cx, tick.callback), arguments(cx, tick.arguments);
    RootedValueVector argv(cx);
    if (!argv.resize(tick.argc)) { JS_ReportOutOfMemory(cx); return false; }
    for (uint32_t i = 0; i < tick.argc; ++i)
      if (!JS_GetElement(cx, arguments, i, argv[i])) return false;
    state.argument_count -= tick.argc;
    tick.callback = nullptr; tick.arguments = nullptr; tick.argc = 0;
    state.head = (state.head + 1) % MaxPending; state.count--;
    ++executed;
    // argv/callback remain rooted after removal. No queue interior pointer is
    // used after calling JS, and the fixed ring does not grow during callbacks.
    JSAutoRealm realm(cx, callback);
    RootedValue ignored(cx);
    if (!Call(cx, UndefinedHandleValue, callback, argv, &ignored) || !exceptions_ok(cx)) return false;
  }
  return true;
}

// Replace the TWO existing RunJobs checkpoints with this helper. No callback
// runs between individual Promise jobs. A nested event-loop attempt is failure.
bool checkpoint(api::Engine* engine, Origin origin) {
  auto& state = storage.get();
  JSContext* cx = engine->cx();
  // Never enter another JS callback with an existing direct failure pending.
  if (JS_IsExceptionPending(cx)) return false;
  if (state.checkpoint_running)
    return fail(cx, JSEXN_ERR, "ERR_SM_NODE_SCHEDULER_REENTRY", "internal checkpoint is already running");
  state.checkpoint_running = true;
  struct Exit { Storage& state; ~Exit() { state.checkpoint_running = false; } } exit{state};
  size_t executed = 0;
  bool promise_first = origin == Origin::ModuleEvaluation;
  do {
    if (!promise_first && !drain_ticks(cx, executed)) { discard(); return false; }
    promise_first = false;
    // Existing full SpiderMonkey checkpoint: retains its current queue, kept-
    // objects cleanup, rejection tracking and exception-reporting behavior.
    js::RunJobs(cx);
    if (!exceptions_ok(cx)) { discard(); return false; }
  } while (state.count);
  return true;
}

bool empty() { return storage.get().count == 0; }

// Proposed Engine::reset boundary, only when no checkpoint/callback is active.
// Does not clear or misrepresent the separate SpiderMonkey Promise job queue.
bool reset(JSContext* cx) {
  if (storage.get().checkpoint_running)
    return fail(cx, JSEXN_ERR, "ERR_SM_NODE_SCHEDULER_REENTRY", "cannot reset an active tick checkpoint");
  discard();
  storage.get().slots.clearAndFree();
  return true;
}

JSObject* create_private_callable(JSContext* cx) {
  RootedFunction function(cx, JS_NewFunction(cx, enqueue, 1, 0, "nextTick"));
  return function ? JS_GetFunctionObject(function) : nullptr;
}
} // namespace proposed::internal_ticks
