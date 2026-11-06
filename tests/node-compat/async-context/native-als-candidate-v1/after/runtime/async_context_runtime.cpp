// SOURCE-ONLY DRAFT; no installed/compiled/native/async result is claimed.
#include "async_context_runtime.h"
#include "async_context_queue.h"
#include "node_tick_queue.h"
#include "js/Array.h"
#include "js/CallAndConstruct.h"
#include "js/Object.h"
#include "js/Prefs.h"
#include "js/Promise.h"
#include "js/PropertyAndElement.h"
#include "js/Realm.h"
#include "js/UniquePtr.h"
#include "js/Utility.h"
#include "jsapi.h"

namespace core::async_context {
using namespace JS;
namespace {
class Metadata final : public js::AllocationMetadataBuilder {
  ResourceStore& resources_;
public:
  explicit Metadata(ResourceStore& resources) : resources_(resources) {}
  JSObject* build(JSContext* cx, HandleObject object,
                  js::AutoEnterOOMUnsafeRegion& oom) const override {
    return resources_.promise_metadata(cx, object, oom);
  }
};
struct RuntimeState {
  ResourceStore resources;
  ContextJobQueue queue;
  Metadata metadata;
  PersistentRootedObject content, initializer;
  bool initialized = false;
  explicit RuntimeState(JSContext* cx)
      : resources(cx), queue(cx, resources), metadata(resources),
        content(cx), initializer(cx) {}
};
js::UniquePtr<RuntimeState> runtime;
bool invalid(JSContext* cx, const char* message) {
  return InternalTickQueue::fail(cx, JSEXN_TYPEERR, "ERR_INVALID_ARG_TYPE", message);
}
bool state_arg(JSContext* cx, const CallArgs& args, MutableHandleObject object) {
  if (!args.length() || !args[0].isObject()) return invalid(cx, "Invalid ALS state");
  object.set(&args[0].toObject());
  return true; // ResourceStore subsequently verifies the private native class.
}
bool create_state(JSContext* cx, unsigned argc, Value* vp) {
  CallArgs args = CallArgsFromVp(argc, vp);
  RootedObject result(cx);
  if (!store().create_state(cx, &result)) return false;
  args.rval().setObject(*result);
  return true;
}
bool enabled(JSContext* cx, unsigned argc, Value* vp) {
  CallArgs args = CallArgsFromVp(argc, vp);RootedObject state(cx);bool value;
  if (!state_arg(cx, args, &state) || !store().enabled(cx, state, &value)) return false;
  args.rval().setBoolean(value);return true;
}
bool set_enabled(JSContext* cx, unsigned argc, Value* vp) {
  CallArgs args = CallArgsFromVp(argc, vp);RootedObject state(cx);
  if (!state_arg(cx, args, &state)) return false;
  if (argc < 2 || !args[1].isBoolean()) return invalid(cx, "enabled must be boolean");
  if (!store().set_enabled(cx, state, args[1].toBoolean())) return false;
  args.rval().setUndefined();return true;
}
bool get(JSContext* cx, unsigned argc, Value* vp) {
  CallArgs args = CallArgsFromVp(argc, vp);RootedObject state(cx);
  if (!state_arg(cx, args, &state)) return false;
  if (argc < 2 || !args[1].isBoolean()) return invalid(cx, "raw must be boolean");
  return store().get(cx, state, args[1].toBoolean(), args.rval());
}
bool set(JSContext* cx, unsigned argc, Value* vp) {
  CallArgs args = CallArgsFromVp(argc, vp);RootedObject state(cx);
  if (!state_arg(cx, args, &state) || !store().set(cx, state, args.get(1))) return false;
  args.rval().setUndefined();return true;
}
bool capture(JSContext* cx, unsigned argc, Value* vp) {
  CallArgs args = CallArgsFromVp(argc, vp);RootedObject resource(cx);
  if (!store().capture(cx, &resource)) return false;
  args.rval().setObject(*resource);return true;
}
bool invoke(JSContext* cx, unsigned argc, Value* vp) {
  CallArgs args = CallArgsFromVp(argc, vp);
  if (argc != 4 || !args[0].isObject() || !args[3].isObject())
    return invalid(cx, "Invalid private resource invocation");
  RootedObject resource(cx, &args[0].toObject()), array(cx, &args[3].toObject());
  bool is_array;uint32_t count;
  if (!JS::IsArrayObject(cx, array, &is_array)) return false;
  if (!is_array) return invalid(cx, "Arguments must be an Array");
  if (!JS::GetArrayLength(cx, array, &count)) return false;
  if (count > 1024) return InternalTickQueue::fail(cx, JSEXN_RANGEERR,
      "ERR_SM_NODE_ASYNC_CONTEXT_LIMIT", "Bound argument limit exceeded");
  RootedValueVector values(cx);
  if (!values.resize(count)) { JS_ReportOutOfMemory(cx);return false; }
  for (uint32_t i = 0; i < count; ++i)
    if (!JS_GetElement(cx, array, i, values[i])) return false;
  return store().invoke(cx, resource, args[1], args[2], values, args.rval());
}
const JSFunctionSpec methods[] = {
  JS_FN("createState", create_state, 0, 0), JS_FN("enabled", enabled, 1, 0),
  JS_FN("setEnabled", set_enabled, 2, 0), JS_FN("get", get, 2, 0),
  JS_FN("set", set, 2, 0), JS_FN("capture", capture, 0, 0),
  JS_FN("invoke", invoke, 4, 0), JS_FS_END,
};
} // namespace
ResourceStore& store() {
  MOZ_RELEASE_ASSERT(runtime && runtime->initialized);
  return runtime->resources;
}
bool prepare_before_self_hosted(JSContext* cx) {
  MOZ_RELEASE_ASSERT(!runtime);
  runtime = js::MakeUnique<RuntimeState>(cx);
  if (!runtime) { JS_ReportOutOfMemory(cx);return false; }
  JS::Prefs::set_use_js_microtask_queue(false);
  JS::SetJobQueue(cx, &runtime->queue);
  JS::InitDispatchsToEventLoop(cx, ContextJobQueue::reject_dispatch,
      ContextJobQueue::reject_delayed, &runtime->queue);
  return true;
}
bool initialize_realms(JSContext* cx, HandleObject content, HandleObject initializer) {
  MOZ_RELEASE_ASSERT(runtime && !runtime->initialized);
  if (JS::GetCompartment(content) != JS::GetCompartment(initializer))
    return invalid(cx, "ALS requires the audited shared initializer compartment");
  runtime->content = content;runtime->initializer = initializer;
  runtime->queue.realms(JS::GetObjectRealmOrNull(content), JS::GetObjectRealmOrNull(initializer));
  {
    JSAutoRealm realm(cx, content);
    if (!runtime->resources.initialize(cx)) return false;
    js::SetAllocationMetadataBuilder(cx, &runtime->metadata);
  }
  {
    JSAutoRealm realm(cx, initializer);
    js::SetAllocationMetadataBuilder(cx, &runtime->metadata);
  }
  runtime->initialized = true;
  return true;
}
JSObject* create_kernel(JSContext* cx) {
  MOZ_RELEASE_ASSERT(runtime && runtime->initialized);
  RootedObject object(cx, JS_NewPlainObject(cx));
  if (!object || !JS_DefineFunctions(cx, object, methods)) return nullptr;
  return object;
}
bool run_fresh_request(JSContext* cx, HandleValue callback, HandleValue receiver,
                        const HandleValueArray& arguments, MutableHandleValue result) {
  RootedObject fresh(cx);
  if (!store().fresh_root(cx, &fresh)) return false;
  return store().invoke(cx, fresh, callback, receiver, arguments, result);
}
bool run_fresh_request_native(JSContext* cx, unsigned argc, Value* vp) {
  CallArgs args = CallArgsFromVp(argc, vp);
  if (argc < 2) return invalid(cx, "Fresh request entry needs callback and receiver");
  return run_fresh_request(cx, args[0], args[1],
      HandleValueArray::subarray(HandleValueArray(args), 2, argc - 2), args.rval());
}
void shutdown_before_context(JSContext* cx) {
  if (!runtime) return;
  // Integration must dispose queued/timer/I/O resources while cx is alive,
  // before this call; it must not pretend an active request is reset-safe.
  JS::ShutdownAsyncTasks(cx);
  if (runtime->content) { JSAutoRealm realm(cx, runtime->content);js::SetAllocationMetadataBuilder(cx, nullptr); }
  if (runtime->initializer) { JSAutoRealm realm(cx, runtime->initializer);js::SetAllocationMetadataBuilder(cx, nullptr); }
  JS::SetJobQueue(cx, nullptr);
  runtime.reset();
}
} // namespace core::async_context
