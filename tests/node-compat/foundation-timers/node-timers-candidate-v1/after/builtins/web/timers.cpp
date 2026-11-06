#include "timers.h"

#include "event_loop.h"
#include "node-compat-entropy.h"
#include "js/Array.h"
#include "js/PropertyAndElement.h"
#include "js/HashTable.h"
#include "js/Vector.h"

#include <algorithm>
#include <ctime>
#include <host_api.h>
#include <iostream>
#include <list>
#include <limits>
#include <utility>

#define S_TO_NS(s) ((s) * 1000000000)
#define NS_TO_MS(ns) ((ns) / 1000000)

namespace {

class TimersMap {
public:
  // Native ownership and JS-edge tracing last until explicit retirement.
  js::HashMap<int32_t, RefPtr<api::AsyncTask>, js::DefaultHasher<int32_t>,
              js::SystemAllocPolicy> timers_;
  uint64_t next_timer_id = 1;
  size_t node_active = 0, node_arguments = 0;
  void trace(JSTracer *trc) {
    for (auto iter = timers_.iter(); !iter.done(); iter.next()) {
      iter.get().value()->trace(trc);
    }
  }
};

} // namespace

static PersistentRooted<js::UniquePtr<TimersMap>> TIMERS_MAP;
static api::Engine *ENGINE;

class TimerTask final : public api::AsyncTask {
public:
  using TimerArgumentsVector = js::Vector<JS::Heap<JS::Value>, 0, js::SystemAllocPolicy>;

private:
  int32_t timer_id_;
  uint64_t delay_;
  uint64_t deadline_ = 0;
  bool repeat_;
  bool retired_ = false;
  bool node_ = false, immediate_ = false, referenced_ = true, owns_interest_ = false;
  uint64_t refresh_generation_ = 0;
  bool running_ = false;
  Heap<JSObject *> callback_;
  TimerArgumentsVector arguments_;

  void drop_pollable() {
    // Invalidate ownership before the host drop; all terminal paths share this.
    const auto owned = std::exchange(handle_, INVALID_POLLABLE_HANDLE);
    if (owned != INVALID_POLLABLE_HANDLE && owned != IMMEDIATE_TASK_HANDLE) {
      host_api::MonotonicClock::unsubscribe(owned);
    }
  }

  void retire() {
    if (retired_) return;
    const RefPtr<TimerTask> keep_alive(this);
    retired_ = true;
    if(owns_interest_){owns_interest_=false;api::Engine::decr_event_loop_interest();}
    if(node_){MOZ_RELEASE_ASSERT(TIMERS_MAP->node_active && TIMERS_MAP->node_arguments>=arguments_.length());--TIMERS_MAP->node_active;TIMERS_MAP->node_arguments-=arguments_.length();}
    drop_pollable();
    auto entry = TIMERS_MAP->timers_.lookup(timer_id_);
    if (entry && entry->value() == this) TIMERS_MAP->timers_.remove(entry);
    callback_ = nullptr;
    arguments_.clear();
  }

public:
  TimerTask(int32_t id, uint64_t delay, bool repeat, HandleObject callback,
            TimerArgumentsVector&& args, HandleObject resource, bool node=false, bool immediate=false)
      : api::AsyncTask(resource), timer_id_(id), delay_(delay), repeat_(repeat), node_(node), immediate_(immediate), callback_(callback),
        arguments_(std::move(args)) {}

  ~TimerTask() override { drop_pollable(); }

  bool is_node()const{return node_;}
  bool is_immediate()const{return immediate_;}
  bool active()const{return !retired_;}
  bool ref_state()const{return !retired_&&referenced_;}
  [[nodiscard]] bool keeps_event_loop_alive()const override{return !node_||(!retired_&&referenced_);}
  void activate_node(){if(node_){++TIMERS_MAP->node_active;TIMERS_MAP->node_arguments+=arguments_.length();owns_interest_=referenced_;if(owns_interest_)api::Engine::incr_event_loop_interest();}}
  void set_ref(bool value){if(!node_||retired_||value==referenced_)return;referenced_=value;owns_interest_=value;if(value)api::Engine::incr_event_loop_interest();else api::Engine::decr_event_loop_interest();}
  bool refresh(){if(!node_||immediate_||retired_)return false;drop_pollable();if(!running_)subscribe();++refresh_generation_;return true;}

  void subscribe() {
    if(immediate_){handle_=IMMEDIATE_TASK_HANDLE;deadline_=0;return;}
    const uint64_t now = host_api::MonotonicClock::now();
    const uint64_t maximum = std::numeric_limits<uint64_t>::max();
    deadline_ = now > maximum - delay_ ? maximum : now + delay_;
    handle_ = host_api::MonotonicClock::subscribe(deadline_, true);
  }

  [[nodiscard]] bool run(api::Engine *engine) override {
    if (retired_) return true;
    JSContext *cx = engine->cx();
#ifdef NODE_COMPAT_TIMERS
    if(node_&&!core::EventLoop::consume_node_timer_callback(cx)){retire();return false;}
#endif
    const uint64_t generation=refresh_generation_;
    MOZ_ASSERT(!running_);running_=true;
    struct RunExit {bool& flag;~RunExit(){flag=false;}} running{running_};
    const RootedObject callback(cx, callback_);
    JS::RootedValueVector argv(cx);
    if (!argv.initCapacity(arguments_.length())) {
      retire();
      JS_ReportOutOfMemory(cx);
      return false;
    }
    for (auto &arg : arguments_) argv.infallibleAppend(arg);
    // Node22 Immediate destroys/unrefs BEFORE invoking its callback. The
    // callback and argv above are independently rooted; AsyncTask's captured
    // ALS cell stays alive in the running native owner until invocation ends.
    if(immediate_)retire();
    RootedValue rval(cx);
    if (!Call(cx, NullHandleValue, callback, argv, &rval)) {
      // Native retirement does not clear or replace the original JS exception.
      retire();
      return false;
    }
    if (retired_) return true; // clear/dispose during callback
    if(generation!=refresh_generation_){engine->queue_async_task(this);subscribe();return true;}
    drop_pollable();
    if (repeat_) {
      // Existing enqueue is void/fatal-on-allocation, not recoverably fallible.
      // No new pollable is acquired until that native queue commit returns.
      engine->queue_async_task(this);
      subscribe();
    } else {
      retire();
    }
    return true;
  }

  [[nodiscard]] bool cancel(api::Engine *) override {
    retire();
    return true;
  }

  [[nodiscard]] uint64_t deadline() override { return deadline_; }
  [[nodiscard]] int32_t timer_id() const { return timer_id_; }

  void trace(JSTracer *trc) override {
    TraceEdge(trc, &callback_, "Timer callback");
    for (auto &arg : arguments_) TraceEdge(trc, &arg, "Timer callback arguments");
  }

  static bool clear(int32_t timer_id) {
    auto entry = TIMERS_MAP->timers_.lookup(timer_id);
    if (!entry) return false;
    // Retain a native owner before queue or registry removal. A running timer
    // is no longer queued, so retire it even when queue lookup returns false.
    RefPtr<api::AsyncTask> timer = entry->value();
    ENGINE->cancel_async_task(timer);
    return timer->cancel(ENGINE);
  }
};

namespace builtins::web::timers {

template <bool repeat>
bool set_timeout_or_interval(JSContext *cx, HandleObject handler, JS::HandleValueVector handle_args,
                             int32_t delay_ms, int32_t *timer_id, bool node=false, bool immediate=false) {
  delay_ms = std::max(delay_ms, 0);

  // Convert delay from milliseconds to nanoseconds, as that's what Timers operate on.
  const uint64_t delay = static_cast<uint64_t>(delay_ms) * 1000000;
  if (TIMERS_MAP->next_timer_id > static_cast<uint64_t>(std::numeric_limits<int32_t>::max())) {
    JS_ReportErrorASCII(cx, "Timer identifier space exhausted");
    return false;
  }
#ifdef NODE_COMPAT_TIMERS
  if(node && (TIMERS_MAP->node_active>=4096 || handle_args.length()>1024 ||
              handle_args.length()>65536-TIMERS_MAP->node_arguments))
    return core::InternalTickQueue::fail(cx,JSEXN_RANGEERR,"ERR_SM_NODE_SCHEDULER_LIMIT","Node task/argument budget exceeded");
#endif
  TimerTask::TimerArgumentsVector arguments;
  if (!arguments.reserve(handle_args.length())) {
    JS_ReportOutOfMemory(cx);
    return false;
  }
  for (const auto &arg : handle_args) arguments.infallibleAppend(arg);
  const int32_t id = static_cast<int32_t>(TIMERS_MAP->next_timer_id);
  RootedObject resource(cx);
  if (!api::AsyncTask::capture_context(cx, &resource)) return false;
  RefPtr<TimerTask> timer = js_new<TimerTask>(id, delay, repeat, handler, std::move(arguments), resource, node, immediate);
  if (!timer || !TIMERS_MAP->timers_.putNew(id, RefPtr<api::AsyncTask>(timer))) {
    JS_ReportOutOfMemory(cx);
    return false;
  }
  // All recoverable allocation checks precede publication/host acquisition.
  // The legacy void queue's native allocation failure remains fatal, not false.
  ENGINE->queue_async_task(timer);
  timer->subscribe();
  timer->activate_node();
  ++TIMERS_MAP->next_timer_id;
  *timer_id = id;
  return true;
}

bool set_timeout(JSContext *cx, HandleObject handler, JS::HandleValueVector handle_args,
                 int32_t delay_ms, int32_t *timer_id) {
  return set_timeout_or_interval<false>(cx, handler, handle_args, delay_ms, timer_id);
}

bool set_interval(JSContext *cx, HandleObject handler, JS::HandleValueVector handle_args,
                  int32_t delay_ms, int32_t *timer_id) {
  return set_timeout_or_interval<true>(cx, handler, handle_args, delay_ms, timer_id);
}

/**
 * The `setTimeout` and `setInterval` global functions
 * https://html.spec.whatwg.org/multipage/timers-and-user-prompts.html#dom-settimeout
 * https://html.spec.whatwg.org/multipage/timers-and-user-prompts.html#dom-setinterval
 */
template <bool repeat> bool setTimeout_or_interval(JSContext *cx, const unsigned argc, Value *vp) {
  REQUEST_HANDLER_ONLY(repeat ? "setInterval" : "setTimeout");
  CallArgs args = CallArgsFromVp(argc, vp);
  if (!args.requireAtLeast(cx, repeat ? "setInterval" : "setTimeout", 1)) {
    return false;
  }

  if (!(args[0].isObject() && JS::IsCallable(&args[0].toObject()))) {
    return api::throw_error(cx, api::Errors::TypeError, repeat ? "setInterval" : "setTimeout",
                            "first argument", "be a function");
  }
  const RootedObject handler(cx, &args[0].toObject());

  int32_t delay_ms = 0;
  if (args.length() > 1 && !JS::ToInt32(cx, args.get(1), &delay_ms)) {
    return false;
  }

  JS::RootedValueVector handler_args(cx);
  if (args.length() > 2 && !handler_args.initCapacity(args.length() - 2)) {
    JS_ReportOutOfMemory(cx);
    return false;
  }
  for (size_t i = 2; i < args.length(); i++) {
    handler_args.infallibleAppend(args[i]);
  }

  int32_t timer_id = 0;
  if (!set_timeout_or_interval<repeat>(cx, handler, handler_args, delay_ms, &timer_id)) {
    return false;
  }

  args.rval().setInt32(timer_id);
  return true;
}

/**
 * The `clearTimeout` and `clearInterval` global functions
 * https://html.spec.whatwg.org/multipage/timers-and-user-prompts.html#dom-cleartimeout
 * https://html.spec.whatwg.org/multipage/timers-and-user-prompts.html#dom-clearinterval
 */
template <bool interval> bool clearTimeout_or_interval(JSContext *cx, unsigned argc, Value *vp) {
  const CallArgs args = CallArgsFromVp(argc, vp);
  if (!args.requireAtLeast(cx, interval ? "clearInterval" : "clearTimeout", 1)) {
    return false;
  }

  int32_t id = 0;
  if (!ToInt32(cx, args[0], &id)) {
    return false;
  }

  clear_timeout_or_interval(id);
  args.rval().setUndefined();
  return true;
}

void clear_timeout_or_interval(int32_t timer_id) { TimerTask::clear(timer_id); }

#ifdef NODE_COMPAT_TIMERS
namespace {
bool deployed_node(JSContext* cx){auto* e=api::Engine::get(cx);if(e&&e->state()==api::EngineState::Initialized&&builtins::node_compat::entropy::deployed_execution_started())return true;return core::InternalTickQueue::fail(cx,JSEXN_ERR,"ERR_SM_NODE_TIMERS_INITIALIZATION","Node timers require deployed execution");}
RefPtr<TimerTask> node_task(int32_t id){auto entry=TIMERS_MAP->timers_.lookup(id);if(!entry)return nullptr;auto* t=static_cast<TimerTask*>(entry->value().get());return t->is_node()?RefPtr<TimerTask>(t):nullptr;}
bool node_create(JSContext* cx,unsigned argc,JS::Value* vp){
 auto a=JS::CallArgsFromVp(argc,vp);if(!deployed_node(cx))return false;
 if(a.length()!=4||!a[0].isInt32()||a[0].toInt32()<0||a[0].toInt32()>2||!a[1].isObject()||!JS::IsCallable(&a[1].toObject())||!a[2].isInt32()||!a[3].isObject())return core::InternalTickQueue::fail(cx,JSEXN_TYPEERR,"ERR_INVALID_ARG_TYPE","invalid private timer arguments");
 JS::RootedObject cb(cx,&a[1].toObject()),array(cx,&a[3].toObject());bool isArray=false;uint32_t n=0;if(!JS::IsArrayObject(cx,array,&isArray))return false;if(!isArray)return core::InternalTickQueue::fail(cx,JSEXN_TYPEERR,"ERR_INVALID_ARG_TYPE","timer arguments must be array");if(!JS::GetArrayLength(cx,array,&n))return false;
 if(n>1024)return core::InternalTickQueue::fail(cx,JSEXN_RANGEERR,"ERR_SM_NODE_SCHEDULER_LIMIT","timer argument budget exceeded");
 JS::RootedValueVector values(cx);if(!values.resize(n)){JS_ReportOutOfMemory(cx);return false;}for(uint32_t i=0;i<n;i++)if(!JS_GetElement(cx,array,i,values[i]))return false;
 int32_t id=0;bool ok=a[0].toInt32()==1?set_timeout_or_interval<true>(cx,cb,values,a[2].toInt32(),&id,true,false):set_timeout_or_interval<false>(cx,cb,values,a[2].toInt32(),&id,true,a[0].toInt32()==2);
 if(!ok)return false;a.rval().setInt32(id);return true;
}
bool node_state(JSContext* cx,unsigned argc,JS::Value* vp){auto a=JS::CallArgsFromVp(argc,vp);if(!deployed_node(cx))return false;if(a.length()<1||!a[0].isInt32())return core::InternalTickQueue::fail(cx,JSEXN_TYPEERR,"ERR_INVALID_ARG_TYPE","timer id required");auto t=node_task(a[0].toInt32());a.rval().setInt32(!t?-1:t->ref_state()?1:0);return true;}
bool node_ref(JSContext* cx,unsigned argc,JS::Value* vp){auto a=JS::CallArgsFromVp(argc,vp);if(!deployed_node(cx))return false;if(a.length()!=2||!a[0].isInt32()||!a[1].isBoolean())return core::InternalTickQueue::fail(cx,JSEXN_TYPEERR,"ERR_INVALID_ARG_TYPE","timer reference arguments invalid");auto t=node_task(a[0].toInt32());if(t)t->set_ref(a[1].toBoolean());a.rval().setUndefined();return true;}
bool node_clear(JSContext* cx,unsigned argc,JS::Value* vp){auto a=JS::CallArgsFromVp(argc,vp);if(!deployed_node(cx))return false;if(a.length()<1||!a[0].isInt32())return core::InternalTickQueue::fail(cx,JSEXN_TYPEERR,"ERR_INVALID_ARG_TYPE","timer id required");TimerTask::clear(a[0].toInt32());a.rval().setUndefined();return true;}
bool node_refresh(JSContext* cx,unsigned argc,JS::Value* vp){auto a=JS::CallArgsFromVp(argc,vp);if(!deployed_node(cx))return false;if(a.length()<1||!a[0].isInt32())return core::InternalTickQueue::fail(cx,JSEXN_TYPEERR,"ERR_INVALID_ARG_TYPE","timer id required");auto t=node_task(a[0].toInt32());if(!t||!t->refresh())return core::InternalTickQueue::fail(cx,JSEXN_ERR,"ERR_SM_NODE_TIMER_INACTIVE","only an active Timeout can be refreshed");a.rval().setUndefined();return true;}
}
JSObject* create_node_timer_kernel(JSContext* cx){JS::RootedObject o(cx,JS_NewPlainObject(cx));const JSFunctionSpec f[]={JS_FN("create",node_create,4,0),JS_FN("state",node_state,1,0),JS_FN("setRef",node_ref,2,0),JS_FN("clear",node_clear,1,0),JS_FN("refresh",node_refresh,1,0),JS_FS_END};return o&&JS_DefineFunctions(cx,o,f)?o.get():nullptr;}

#endif

constexpr JSFunctionSpec methods[] = {
    JS_FN("setInterval", setTimeout_or_interval<true>, 1, JSPROP_ENUMERATE),
    JS_FN("setTimeout", setTimeout_or_interval<false>, 1, JSPROP_ENUMERATE),
    JS_FN("clearInterval", clearTimeout_or_interval<true>, 1, JSPROP_ENUMERATE),
    JS_FN("clearTimeout", clearTimeout_or_interval<false>, 1, JSPROP_ENUMERATE), JS_FS_END};

bool install(api::Engine *engine) {
  ENGINE = engine;
  TIMERS_MAP.init(engine->cx(), js::MakeUnique<TimersMap>());
  return JS_DefineFunctions(engine->cx(), engine->global(), methods);
}

void reset() {
  // Each cancel removes its own registry entry; never retain an iterator across it.
  while (!TIMERS_MAP->timers_.empty()) {
    RefPtr<api::AsyncTask> timer = TIMERS_MAP->timers_.iter().get().value();
    (void)timer->cancel(ENGINE);
  }
  // Do not alias old IDs. This does not make Engine::reset safe or supported.
}

} // namespace builtins::web::timers
